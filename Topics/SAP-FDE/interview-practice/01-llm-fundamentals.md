# 01 — LLM Fundamentals & Prompting: Interview Q&A Bank

**How to use:** Cover the question, answer out loud in ~90s, then read the model answer and close the gaps. Rounds grade *how you weigh trade-offs*, not whether you can recite a definition — so lead with the trade-off and back it with a concrete number.

Tiers map to seniority: Tier 1 you must nail cold, Tier 2 is where an applied/FDE loop spends most time, Tier 3 is the senior "debug it live / defend the trade-off" bar.

---

## Tier 1 — Fundamentals

### Q: What is a token, and why does tokenization matter for cost, latency, and correctness?
**Tests:** Whether you understand the unit everything is billed and bounded in.
**Answer (production-grade):** A token is a sub-word chunk the model actually reads — not a character, not a word. Modern tokenizers use Byte-Pair Encoding (BPE): start from bytes, iteratively merge the most frequent adjacent pairs into a vocabulary (~100K–200K entries). Rule of thumb: **1 token ≈ 4 characters ≈ 0.75 words**, so ~1.3 tokens per English word. Three things ride on this: (1) **cost** — you pay per token in and per token out; (2) **context limits** — a "200K context" is 200K tokens, not characters; (3) **multilingual and code cost** — non-Latin scripts and unusual code can be 2–4x more tokens per word, silently inflating bills and truncating context. Practical tell: never estimate prompt size in characters when you're near a limit — count tokens with the model's own tokenizer.
**Lab:** `../lab/concepts/m1_01_tokens.py`

### Q: What is the context window, and how is it different from `max_tokens`?
**Tests:** A very common confusion; separates people who've shipped from people who've read docs.
**Answer (production-grade):** The **context window** is the total token budget for a single request — **input + output combined**. `max_tokens` caps only the *output* (the reply). They interact: input + `max_tokens` must fit inside the window, so a huge prompt shrinks the room left to answer. As of 2026, typical windows are ~128K (GPT-class), ~200K (Claude Sonnet), and up to ~1M (Gemini). Two senior caveats: (1) big window ≠ free — you pay for every token you stuff in, and long contexts raise latency; (2) **"lost in the middle"** — models attend best to the start and end of context, so retrieval quality degrades if key facts sit buried in the middle. Don't treat a large window as a substitute for good retrieval.
**Lab:** `../lab/concepts/m1_03_context_window.py`

### Q: Explain temperature vs. top-p (and top-k). When do you tune which?
**Tests:** Can you reason about the sampling distribution, not just repeat "higher = more creative"?
**Answer (production-grade):** All three shape how the next token is sampled from the probability distribution. **Temperature** rescales the whole distribution: near 0 it sharpens toward the single most likely token (near-deterministic); higher (0.7–1.0) flattens it so lower-probability tokens get a real chance. **Top-p (nucleus)** truncates to the smallest set of tokens whose cumulative probability ≥ p, then samples within it — the set size *adapts* to how confident the model is. **Top-k** truncates to a fixed count of top tokens regardless of confidence. Practical policy: for extraction/classification/JSON/evals use **temperature ~0** (reproducible); for brainstorming raise temperature and/or top-p. Don't crank both to extremes together — at high temperature a top-p of 0.9 can admit genuinely bad 2–3% tokens and produce garbage. Note: even at temperature 0, output isn't 100% guaranteed identical across runs (batching/hardware nondeterminism), so don't build hard equality assertions on it.
**Lab:** `../lab/concepts/m1_02_sampling.py`

### Q: LLM APIs are stateless. What does that mean, and what are the message roles for?
**Tests:** Whether you understand where "memory" actually lives (spoiler: in your app).
**Answer (production-grade):** The model has no memory between calls — each request is independent. "Memory" is an illusion **your app** creates by replaying the prior conversation on every turn. Messages carry roles: **system** (durable instructions/persona/policy — set once, high leverage), **user** (the human turn), **assistant** (the model's prior turns, which you echo back so it "remembers"). Because you resend history each turn, cost and latency grow with conversation length — so at some point you must **truncate or summarize** older turns (sliding window, or a running summary) rather than replay everything. This is also why the *ordering* matters for caching (below): keep the stable stuff (system prompt, tool defs) first and the volatile stuff last.
**Lab:** `../lab/concepts/m1_05_messages_memory.py`

### Q: How do you get reliable structured (JSON) output? Contrast JSON mode vs. schema-constrained decoding.
**Tests:** Do you know the strictness spectrum and pick the right rung?
**Answer (production-grade):** There's a strictness ladder: **(1) prompt-and-pray** ("respond in JSON") — brittle, breaks after model updates; **(2) JSON mode** — guarantees *syntactically valid* JSON but not *your* shape (fields/types can drift); **(3) schema-constrained / structured outputs** — the decoder is masked so only tokens that satisfy your schema (e.g., a Pydantic/JSON-Schema definition) can be emitted, guaranteeing valid *and* conformant output. Default to level 3 when the provider supports it. Regardless of level, **always validate and retry**: parse into your schema, and on failure re-prompt with the validation error. Keep temperature ~0 for these. One gotcha: constrained decoding + chain-of-thought fight each other — if you force JSON you also suppress free-form reasoning, so either give the model a `reasoning` string field or do reasoning in a separate call.
**Lab:** `../lab/concepts/m1_07_structured_output.py`

### Q: What is tool / function calling, and what does the model actually do when it "calls a tool"?
**Tests:** The #1 misconception — that the model executes code.
**Answer (production-grade):** The model **cannot** run anything. Given a set of tool schemas (name, description, JSON-typed args), it emits a *structured request* — "call `get_weather` with `{city: 'Berlin'}`" — and stops. **Your code** decides whether to run it, runs it, and feeds the result back as a tool message; the model then continues. The golden rule: **treat every tool call as untrusted input** — validate args and authorize the action before executing, exactly as you would a request from an external client. Independent calls can be proposed in parallel; dependent ones must be sequenced by your orchestration. This request/response loop is the foundation of agents.
**Lab:** `../lab/concepts/m1_08_tool_calling.py`

---

## Tier 2 — Applied / Design

### Q: Walk me through the cost and latency model of an LLM call. Why are output tokens pricier?
**Tests:** Prefill vs. decode — the mental model behind every cost/latency optimization.
**Answer (production-grade):** A request has two phases. **Prefill:** the whole input prompt is processed in one parallel forward pass — compute-bound, cheap per token, and it sets **TTFT** (time to first token). **Decode:** output tokens are generated one at a time, each its own forward pass — memory-bandwidth-bound, hard to batch across users, and it sets **TPOT** (time per output token). That asymmetry is exactly why **output tokens cost ~3–5x input** (up to ~8x on reasoning models): decode work can't be amortized the way prefill can. Consequences for design: (1) latency is dominated by *how long the answer is*, so cap `max_tokens` and don't ask for essays you'll throw away; (2) **stream** the response — it doesn't reduce total latency but cuts *perceived* latency to ~TTFT; (3) trimming input helps cost but trimming output helps cost *more*. Know your numbers cold: latency budget (p50/p99), cost-per-request, tokens/sec.
**Lab:** `../lab/concepts/m1_04_cost_latency.py`

### Q: What is prompt caching, when does it help, and what's the most common way people break it?
**Tests:** Do you understand it operates on prefill/KV, not output — and the ordering discipline it demands?
**Answer (production-grade):** Prompt caching reuses the computed **KV (key-value) tensors** for an identical prompt **prefix**, so repeat requests skip that prefill work. Payoff: up to ~90% cheaper input tokens and ~80% lower TTFT (often 5–20x faster first token) on cache hits. Critical nuance interviewers push on: **it cuts prefill only — you still pay full price for output tokens**, and it doesn't touch decode/streaming. It shines when the prefill:decode ratio is large — big stable system prompts, tool definitions, RAG context, long multi-turn chats (ratios of 50:1–100:1 are common in agents). The #1 mistake: **putting volatile content at the top** — a timestamp, request ID, or user data in the system prompt busts the cache on every call, since any change invalidates everything after it. Fix: stable content first (system prompt, tool schemas), volatile content last (the user's current message). Real example: relocating dynamic memory out of the system prompt lifted a hit rate from 7% → 84% and cut cost ~59%.
**Lab:** Build: `m1_09_prompt_caching.py` — same 2K-token system prompt sent twice; print cache-read vs. cache-write token counts and TTFT delta.

### Q: What is few-shot / in-context learning, and how many examples should you include?
**Tests:** Trade-off discipline — examples cost tokens and can over-constrain.
**Answer (production-grade):** In-context learning = the model infers the task from **examples in the prompt**, no weight updates. Zero-shot (instructions only) → one-shot → few-shot (a handful of input→output pairs). Reach for few-shot when the **output format is specific** or the task is ambiguous — showing 2–5 examples is usually far more effective than describing the format in prose. Design rules: (1) **fewest examples that establish the pattern** — each one costs tokens on every call and too many can over-fit the style and hurt generality; (2) **cover the edge cases** you actually get wrong (the confusable classes), not the easy ones; (3) keep example format *identical* to what you ask for. When you find yourself needing 20+ examples for consistency, that's the signal to consider fine-tuning instead. Note few-shot examples are great **cache** candidates since they're stable.
**Lab:** `../lab/concepts/m1_06_few_shot.py`

### Q: Design a support-ticket classifier that a downstream system can act on. How do you build the prompt?
**Tests:** Can you assemble the fundamentals (system prompt + few-shot + structured output + temp) into a real component?
**Answer (production-grade):** (1) **System prompt** defines role + the closed set of classes, each with a one-line boundary definition so confusable classes don't blur. (2) **Structured output** — a schema with `category: Literal[...]`, a `confidence`, and a mandatory **`other`** fallback so the model never forces a wrong label. (3) **Few-shot** — 2–3 examples targeting the pairs that get confused. (4) **Temperature ~0** for determinism. (5) **Validate + retry** on parse failure; (6) route **low-confidence** or `other` to a human queue. (7) **Evaluate** on a labeled set (precision/recall per class) before shipping and monitor drift after. Say the numbers: "I'd gate on ≥0.90 macro-F1 on a 200-case set before rollout." The eval + fallback are what make it production-grade, not the prompt wording.
**Lab:** `../lab/concepts/m1_07_structured_output.py` (schema/validation pattern) + `../lab/concepts/m1_06_few_shot.py` (examples)

### Q: How does function calling become an agent, and what guardrails do you require before letting an LLM trigger real actions?
**Tests:** The FDE "customer wants the LLM to run SQL and fire webhooks fast" scenario.
**Answer (production-grade):** An agent is the tool-calling loop run to convergence: model proposes a tool call → your code executes → result goes back → repeat until it produces a final answer. The danger is the model now influences side effects, so **defense in depth**: (1) **least-privilege tools** — narrow, typed, read-only where possible; no raw "execute arbitrary SQL" — expose `get_order(id)`, not a SQL string; (2) **validate + authorize every call** server-side (the model's args are untrusted); (3) **human-in-the-loop** for irreversible/high-blast-radius actions (refunds, deletes, sends); (4) **allowlists, rate limits, and idempotency keys**; (5) **loop caps** to prevent runaway cost; (6) **audit logging** of every proposed and executed call. Rollout: start read-only in shadow mode, add a dry-run/confirm step, then graduate specific tools to auto-execute once evals + logs show they're safe. To the "do it fast" push: I ship *fast on read tools*, and gate *write tools* behind confirmation — that's how we ship this week without a Monday incident.
**Lab:** `../lab/concepts/m1_08_tool_calling.py`

---

## Tier 3 — Senior Trade-offs & Debugging

### Q: How do you choose which model to use for a task?
**Tests:** Whether you reframe "best model" into "cheapest model that clears the quality bar."
**Answer (production-grade):** Wrong question is "which is best"; right question is "which model clears the **quality bar** for *this* task at the lowest cost/latency." Process: (1) define the bar with an **eval set** and a metric (e.g., ≥0.90 pass@1 on 200 cases); (2) start with a strong model to prove the task is *achievable*, then **step down** to the smallest/cheapest model that still passes — often a mid-tier model with good prompting beats a frontier model with lazy prompting; (3) name the constraints: p50/p99 latency, cost-per-request, context needs, data-residency/governance, and tool-calling quality. The mature 2026 answer converges on **routing**: cheap model for easy traffic, frontier only for the hard tail — teams report 40–85% cost cuts because most traffic never needed a frontier model. The router itself is cheap (rule-based <1ms, embedding ~5ms) vs. 500–2000ms inference, so it's never the bottleneck. The risk to name: routing down can quietly degrade answers that surface as tickets days later — mitigate with a **pre-merge eval gate** and production monitoring.
**Lab:** Build: `m1_10_model_router.py` — score a query's complexity, route easy→small / hard→large model, log blended cost vs. all-frontier baseline.

### Q: "Walk me through how you'd diagnose high latency in an LLM pipeline." (live debugging)
**Tests:** Systematic full-stack reasoning under a vague symptom.
**Answer (production-grade):** First **decompose the latency budget**, don't guess. Measure each layer: network/queueing, retrieval (embedding + vector search + rerank), prefill (**TTFT**), and decode (**TPOT × output length**). Then attack the biggest slice: (1) if **TTFT** is high → input is huge → trim/rerank context, enable **prompt caching** on the stable prefix; (2) if total decode is high → the answer is too long → cap `max_tokens`, ask for terser output, or use a faster/smaller model; (3) if it's the **tail (p99)** → look at retries, rate-limit backoff, cold caches, or one slow tool call; (4) **stream** to fix perceived latency regardless. Also check for accidental serial tool calls that could run in parallel. Always **measure before optimizing** and confirm which metric actually hurts — latency, throughput, or cost — because fixing one often worsens another.
**Lab:** `../lab/concepts/m1_04_cost_latency.py` (TTFT/streaming measurement)

### Q: A provider ships a model update and your app's behavior shifts. How do you handle model updates and drift in production?
**Tests:** Reliability engineering around a dependency you don't control.
**Answer (production-grade):** Two failure modes: **provider-side drift** (they update the model behind an alias) and **your-side data drift** (input distribution shifts over time). Defenses: (1) **pin explicit model versions**, don't ride a floating `latest` alias; (2) keep a **regression eval suite** and run it on every candidate version *before* promoting — treat prompts + model like code with CI; (3) **monitor in prod** — output distributions, structured-output parse-failure rate, tool-call error rate, latency, and a sampled **LLM-as-judge** or human review stream; (4) **canary** a new version on a small traffic slice; (5) keep **prompts decoupled** from model so you can re-tune quickly; (6) have a **rollback** path to the pinned prior version. To the non-technical stakeholder: I frame it as "we don't guarantee the model never changes; we guarantee we'll *catch* a regression before customers do" via the eval gate + monitoring.
**Lab:** Build: `m1_11_regression_eval.py` — run a fixed prompt suite across two model versions, diff pass-rates, flag regressions.

### Q: Your app is returning hallucinated / fabricated answers. How do you reduce hallucinations, and how do you debug a specific bad output?
**Tests:** Grounding strategy + a systematic debugging checklist, not hand-waving.
**Answer (production-grade):** Prevention, cheapest first: (1) **ground it** — instruct "use only the provided context; if it's not there, say you don't know" and give it retrieved sources (**RAG**) so it isn't drawing from parametric memory; (2) **reduce open-endedness** — the more constrained the task, the fewer hallucinations; (3) **lower temperature**; (4) require **citations** to the retrieved chunks and validate them; (5) for high stakes, add a **verification pass** (LLM-as-judge or human) and abstention. Debugging a specific bad output — work the layers: (a) is the fact in the retrieved context at all? If not, it's a **retrieval** bug, not a model bug — fix chunking/embeddings/reranking; (b) was context **truncated** by the token limit? (c) simplify and tighten the prompt, add a targeted few-shot for the failure; (d) check whether temperature or a confusing instruction caused it. The senior tell: distinguish a **retrieval failure** from a **generation failure** before touching the prompt — most "hallucinations" in a RAG app are actually retrieval misses.
**Lab:** Build: `m1_12_grounded_answer.py` — answer strictly from provided context, force "I don't know" when the fact is absent, and cite the source chunk. (RAG itself: `../lab/concepts/m4_01_rag.py`)

### Q: When does chain-of-thought *hurt*, and how do you reconcile it with structured output?
**Tests:** Nuance — that "always add reasoning" is wrong.
**Answer (production-grade):** CoT helps on multi-step reasoning/math but **hurts** on: (1) **simple retrieval/lookup** tasks — it adds latency and output cost for zero accuracy gain; (2) **strict structured output** — free-form reasoning pollutes or breaks the JSON, and constrained decoding suppresses the reasoning anyway. Reconciliation options: put reasoning in a dedicated `reasoning` field *inside* the schema (so it's allowed but contained), or **split** into two calls (reason first, then format), or use a reasoning model and only capture its final structured answer. Also relevant in 2026: modern **reasoning models** do this internally and bill hidden "thinking" tokens as output — great for hard tasks, wasteful and slow for easy ones, which loops back to model selection/routing.
**Lab:** Build: `m1_13_cot_vs_direct.py` — same task with/without CoT; compare accuracy, tokens, and latency on an easy vs. a hard task.

### Q: How do you defend an LLM feature against prompt injection?
**Tests:** Security awareness — treating model I/O as an untrusted boundary.
**Answer (production-grade):** Prompt injection = untrusted content (a web page, a document, a tool result, a user message) carrying instructions that hijack the model. There's no single fix — **defense in depth**: (1) **separate trust levels** — keep your instructions in the system prompt and clearly delimit/label untrusted data so the model treats it as data, not commands; (2) **least privilege on tools** and human confirmation for side effects (as above) so a successful injection can't *do* much; (3) **input/output filtering** and validation; (4) **structured tool calls** over free-form action strings; (5) **never auto-follow instructions found inside retrieved/observed content** — surface them instead; (6) don't put secrets/PII where the model can exfiltrate them, and constrain egress. The mindset: the model's output and any content it ingests are **untrusted input** to the rest of your system — validate and authorize at the boundary, don't trust by default.
**Lab:** Build: `m1_14_prompt_injection.py` — feed a poisoned "document" that tries to override the system prompt; show a naive prompt obeying it vs. a delimited/least-privilege setup resisting it.

---

## Code gaps to add

- `m1_09_prompt_caching.py` — send a large stable system prompt twice; print cache-write vs. cache-read tokens and the TTFT/cost delta (proves caching cuts prefill, not output).
- `m1_10_model_router.py` — complexity-score a query, route easy→small / hard→large model, log blended cost vs. an all-frontier baseline.
- `m1_11_regression_eval.py` — run a fixed prompt suite across two pinned model versions and diff pass-rates to catch provider drift.
- `m1_12_grounded_answer.py` — answer strictly from provided context, force abstention when the fact is absent, and cite the source chunk.
- `m1_13_cot_vs_direct.py` — same task with vs. without chain-of-thought; compare accuracy, tokens, and latency on an easy vs. hard task.
- `m1_14_prompt_injection.py` — poisoned-document demo: naive prompt obeys the injected instruction, delimited + least-privilege setup resists it.

## Sources

- [DataCamp — Top 36 LLM Interview Questions and Answers](https://www.datacamp.com/blog/llm-interview-questions)
- [DataCamp — Top 36 Generative AI Interview Questions](https://www.datacamp.com/blog/genai-interview-questions)
- [MyEngineeringPath — LLM Interview Questions (30, Senior, 2026)](https://myengineeringpath.dev/genai-engineer/llm-interview-questions/)
- [rungcode.io — LLM Interview Questions: Tokenization, Sampling & Evals (2026)](https://rungcode.io/guides/llm-interview-questions)
- [Machine Learning Plus — LLM Temperature, Top-P, Top-K Explained](https://machinelearningplus.com/gen-ai/llm-temperature-top-p-top-k-explained/)
- [Towards Data Science — Structured Outputs: JSON Mode, Function Calling, and When to Use Each](https://towardsdatascience.com/structured-outputs-with-llms-json-mode-function-calling-and-when-to-use-each/)
- [Agenta — Guide to Structured Outputs and Function Calling with LLMs](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)
- [skphd (Medium) — Top 50 Prompt Engineering Interview Questions](https://skphd.medium.com/top-50-prompt-engineering-interview-questions-and-answers-7ee3f694ffe8)
- [testRigor — Prompt Engineering Interview Questions](https://testrigor.com/blog/prompt-engineering-interview-questions/)
- [NudgeBee — Anatomy of an LLM Request: Prefill, Decode, Latency & Cost](https://nudgebee.com/resources/blog/anatomy-of-an-llm-request)
- [DigitalOcean — How Prompt Caching Works and When It Cuts Costs](https://www.digitalocean.com/community/tutorials/prompt-caching-cost-break-even)
- [Towards Data Science — Why Care About Prompt Caching in LLMs](https://towardsdatascience.com/why-care-about-promp-caching-in-llms/)
- [digitalapplied — LLM Model Routing in 2026: Cost-Quality Optimization](https://www.digitalapplied.com/blog/llm-model-routing-2026-cost-quality-optimization-engineering-guide)
- [Exponent — Forward Deployed Engineer Interview: Definitive 2026 Guide](https://www.tryexponent.com/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde)
- [Dataford — Cohere Forward-Deployed Engineer Interview Questions 2026](https://dataford.io/interview-guides/cohere/forward-deployed-engineer)
- [gaijineer.co — OpenAI Forward Deployed Engineer Interview Process](https://gaijineer.co/openai-forward-deployed-engineer-interview-process)
