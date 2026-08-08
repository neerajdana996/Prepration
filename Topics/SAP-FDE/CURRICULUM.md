# SAP FDE Application/ML — Master Curriculum (the linked spine)

**Purpose:** one ordered path from zero → principal/expert, where **every concept is a prerequisite for the next**. This is the drill map for a real interview (Req 454031), not an overview. We teach top-to-bottom; you never meet a concept whose prerequisite you haven't already drilled.

**How to read this:** each module says *why it sits here* (the link back) and *what it unlocks* (the link forward). Inside a module, lessons are ordered; inside a lesson, concepts are ordered. `⚑ Signal` = what an interviewer is actually listening for.

**Status legend:** ☐ not started · ◐ in progress · ☑ drilled & quizzed

---

## THE SPINE (one sentence per module — memorize this chain)
1. **Engine** — an LLM is a next-token predictor; tokens govern cost, latency, context. →
2. **Prompting** — you control the engine only through the text you put in the window. →
3. **Embeddings & retrieval** — to put the *right* text in the window, you must find it by meaning. →
4. **RAG** — the system that retrieves then generates: the #1 enterprise pattern. →
5. **Agents** — give the engine tools + a loop so it can act, not just answer. →
6. **Evaluation** — nondeterministic systems are worthless unless you can measure them. →
7. **Safety & security** — enterprise data + autonomy = you must contain the blast radius. →
8. **Production & MLOps** — make it fast, cheap, reliable, observable, and shippable. →
9. **AI system design** — combine 1–8 into an architecture for a stated problem. →
10. **Forward-deployed delivery** — wrap the architecture in discovery, delivery, handover under ambiguity. →
11. **SAP stack** — map every generic concept onto SAP's components (BTP/AI Core/GenAI Hub/Joule/HANA). →
12. **Behavioral** — the human layer that runs through all three rounds.

---

## M1 — LLM Foundations: the engine
*Why here:* it's the atom. Every later module manipulates this one loop.
*Unlocks:* prompting (M2), because prompting = controlling this loop's input/output.

- **1.1 Tokens & tokenization** ☑ — what a token is; ~4 chars/¾ word; vocab; BPE at a mental-model level; multilingual/code token cost. *⚑ can you estimate tokens & reason about cost from them.*
- **1.2 Next-token prediction & sampling** ☑ (incl. temperature, top-p, STOP token, max_tokens) — autoregression; logits → probabilities; greedy vs temperature vs top-p/top-k; why output is nondeterministic. *⚑ explain temperature's effect on a real feature.*
- **1.3 Transformer mental model (builder's view)** ☑ (attention = every token looks at every token → n² cost) — attention as "every token looks at every token"; why context is **quadratic**; KV cache; prefill (parallel, fast) vs decode (sequential, slow). *⚑ why long context is expensive & slow.*
- **1.4 Context window** ☑ (the shared desk; input + answer share the budget) — input+output share one budget; truncation/error on overflow; "lost in the middle"; context ≠ memory. *⚑ design around a fixed window.*
- **1.5 The message protocol** ☑ (system/user/assistant; STATELESS → resend transcript; summary vs sliding-window vs prompt-caching to tame cost) — system / user / assistant roles; multi-turn structure; how "chat" is stitched into one sequence; statelessness (you resend history every call). *⚑ know the API is stateless.*
- **1.6 In-context learning** ☑ (zero-shot vs few-shot; teach by showing, no training) — zero-shot vs few-shot; instructions vs examples; when examples beat instructions. *⚑ pick the cheaper technique that works.*
- **1.7 Structured output** ☑ (3 levels: prompt-ask → JSON mode → schema-constrained decoding; match strength to blast radius) — JSON mode / schema-constrained decoding; why it matters for real apps; parsing + validation + repair. *⚑ how you make an LLM's output machine-usable.*
- **1.8 Tool / function calling (mechanism)** ☑ (model proposes JSON call, code disposes; validate as untrusted; dependency graph → parallel independent calls; tool = name+description+param schema; order = workflow vs agent) — model emits a structured call, *you* execute it, feed the result back; the model never runs code. *⚑ the exact request/response loop — this is the seed of agents.*
- **1.9 Cost & latency modeling** ☑ (bill = in×price + out×price; output ~5×; prefill fast / decode slow; stream) — input vs output pricing (output 3–5×); TTFT vs tokens/sec; streaming; prompt caching; batching. *⚑ back-of-envelope a monthly bill & p95 latency.*
- **1.10 Model selection & families** ☐ — capability vs cost vs latency vs context tradeoff; generative vs embedding vs reranker models; hosted API vs open-weights/self-host. *⚑ justify a model choice against constraints.*
- **1.11 Failure modes of the raw engine** ☐ — hallucination, sycophancy, prompt sensitivity, knowledge cutoff, nondeterminism, refusal. *⚑ name the failure before it bites you.*

## M2 — Prompting & context engineering (controlling the engine)
*Why here:* M1 gave the loop; the only knob you have at runtime is the text you feed it.
*Unlocks:* retrieval (M3) — because the hardest part of a prompt is *what context to put in it*, which forces you to go find that context.

- **2.1 Prompt anatomy & instruction hierarchy** ☐ — role, task, constraints, context, examples, output format; ordering effects (primacy/recency). *⚑ a repeatable prompt structure.*
- **2.2 Core techniques** ☐ — chain-of-thought / reasoning, decomposition, self-consistency, self-critique/reflection; cost of each. *⚑ match technique to task difficulty.*
- **2.3 Context construction** ☐ — what goes in the window, in what order, and what to leave out; token budgeting a prompt; compression/summarization. *⚑ treat the window as a scarce resource.*
- **2.4 Output contracts & robustness** ☐ — schemas, delimiters, retries, fallback parsing, guarding against partial/invalid output. *⚑ make prompts production-robust, not demo-robust.*
- **2.5 Prompt injection (intro)** ☐ — user/data can override your instructions; trust boundaries. *⚑ flag the risk early — full treatment in M7.*
- **2.6 Prompt management** ☐ — versioning, templating, parameterization, testing prompts as code. *⚑ prompts are artifacts, not strings — links to evals M6 & MLOps M8.*

## M3 — Embeddings & retrieval (finding the right context)
*Why here:* M2 said "put the right context in the window." When the corpus is huge, you can't; you must retrieve by meaning first.
*Unlocks:* RAG (M4) — retrieval + generation assembled into one system.
*BUILD-FROM-SCRATCH (per user):* we hand-code the classics in plain Python **before** any library — Bag-of-Words, TF, IDF, TF-IDF, cosine similarity, then BM25, then a tiny brute-force vector search. You'll *feel* why embeddings beat keywords, then why ANN indexes beat brute force.

- **3.1 Embeddings** ☑ (meaning-space; learned vectors; real Gemini embeddings feed the hand-built cosine → semantic search beats keyword) — text → vector; semantic space; embedding models; dimensionality; same-model constraint (query & doc). *⚑ what a vector actually represents.*
- **3.2 Similarity metrics** ☑ (cosine hand-coded; angle not magnitude; length-invariant. Lab: BoW→TF→IDF→TF-IDF→cosine→tiny search engine all built from scratch, `lab/concepts/m3_01..m3_03`) — cosine vs dot vs euclidean; normalization; what "close" means. *⚑ pick & justify a metric.*
- **3.3 Vector stores & ANN indexes** ☐ — exact vs approximate; flat / IVF / HNSW; recall–latency–memory tradeoff; when a vector DB vs a column in your existing DB (→ HANA in M11). *⚑ index choice under scale.*
- **3.4 Chunking** ☑ (unit of retrieval; size/overlap trade-off; fixed vs recursive vs semantic vs layout-aware; tail-loss bug; hand-coded splitter) — fixed vs semantic vs structural; size/overlap tradeoffs; metadata attachment; the chunk = the unit of retrieval. *⚑ chunking is where most RAG quality is won or lost.*
- **3.5 Lexical vs semantic retrieval** ☑ — BM25 (saturation+length, hand-coded) vs embeddings; hybrid via RRF; BM25=exact tokens, embeddings=meaning. *⚑ know vector search isn't always best.*

### 🔧 BONUS internals arc (forward-pass only, no training) — slot in as deep-dives, applied-first
1. **BM25** — hand-code the better TF-IDF (still used in real hybrid search).
2. **Word embeddings** — how words become vectors from context (word2vec intuition; tiny co-occurrence build).
3. **Attention** — the actual mechanic: query·key → weights → weighted sum (numpy forward pass).
4. **Transformer block** — attention + FFN + residual + layernorm; encoder vs decoder (decoder = next-token, M1 callback).
5. **Toy embedding model** — mean-pool hidden states → a sentence vector; feed a query, get an embedding → plug into the hand-built `cosine_similarity`. Full circle.
*(Skipped for interview scope: full LLM training/backprop. We build forward passes to understand, not to train.)*

## M4 — RAG, done properly (the flagship pattern)
*Why here:* M3's pieces (embed, index, retrieve) now assemble into the enterprise workhorse.
*Unlocks:* agents (M5) — RAG is a fixed pipeline; agents make retrieval one *tool* among many, chosen dynamically.

- **4.1 The naive RAG pipeline** ☑ — ingest → chunk → embed → store → retrieve top-k → augment → generate → cite; grounded prompt (answer only from context / refuse / cite); built end-to-end in `lab/concepts/m4_01_rag.py`. *⚑ draw it end-to-end from memory.*
- **4.2 Retrieval quality** ☑ (recall vs precision; k too small = miss, too big = dilute + lost-in-the-middle) — recall vs precision; choosing k; context dilution; the "retrieved-but-ignored" problem. *⚑ diagnose bad answers = bad retrieval vs bad generation.*
- **4.3 Reranking** ☑ (bi-encoder=separate encode, precomputable, fast/coarse; cross-encoder=joint encode, per-pair, slow/accurate; 2-stage retrieve-N→rerank-k)
- **4.5 Query transformation** ☑ (multi-query / RAG-Fusion via RRF; HyDE; decomposition — user derived it) · **Bonus:** semantic query cache + feedback loop (answer vs intention, TTL, threshold/negation traps) — bi-encoder recall then cross-encoder precision; latency cost; top-N→top-k. *⚑ the standard quality upgrade.*
- **4.4 Hybrid search & fusion** ☐ — BM25 + vector; Reciprocal Rank Fusion; metadata/filtered search. *⚑ combine lexical + semantic and merge results.*
- **4.5 Query transformation** ☐ — rewriting, multi-query, HyDE, decomposition of complex questions. *⚑ fix the question before blaming the index.*
- **4.6 Grounding, citations & faithfulness** ☐ — force answers from retrieved context; inline citations; "I don't know"; hallucination reduction. *⚑ make it trustworthy for enterprise.*
- **4.7 Advanced RAG** ☐ — parent-child / small-to-big, contextual retrieval, metadata filtering, multi-hop, graph/structured retrieval. *⚑ know upgrades beyond naive.*
- **4.8 RAG vs long-context vs fine-tuning** ☐ — decision framework: freshness, cost, controllability, data volume. *⚑ choose the right tool, not the trendy one.*
- **4.9 RAG failure modes & debugging** ☑ (bisect via printing retrieved chunks → retrieval bug vs generation bug; add regression eval) — bad chunks, wrong k, stale index, embedding mismatch, lost-in-middle, over-retrieval; a debugging playbook. *⚑ systematic triage — links to evals M6.*

## M5 — Agents & agentic workflows (acting, not just answering)
*Why here:* M1.8 gave tool-calling; M4 made retrieval a pipeline. An agent = LLM + tools + a **loop** that decides which tool (incl. retrieval) to call next.
*Unlocks:* evaluation (M6) — agents' open-ended behavior makes measurement mandatory before you can trust one.

- **5.1 Agent definition & the loop** ☐ — perceive → reason → act → observe → repeat; agent = model + tools + control flow + stopping condition. *⚑ define an agent precisely.*
- **5.2 Workflows vs agents** ☐ — deterministic orchestrated steps vs model-directed autonomy; "use the least autonomy that works." *⚑ the single most important agent judgment call.*
- **5.3 ReAct & reasoning-action patterns** ☐ — interleaving thought and tool calls; scratchpad. *⚑ the canonical pattern.*
- **5.4 Tool design** ☐ — tools are an API for the model; naming, descriptions, args, error returns; idempotency; granularity. *⚑ good tools = good agents.*
- **5.5 Planning & decomposition** ☐ — plan-then-execute, task breakdown, reflection/replanning. *⚑ handle multi-step goals.*
- **5.6 Memory** ☐ — short-term (context) vs long-term (external store); what to persist; retrieval of memory (ties to M3). *⚑ state across steps/sessions.*
- **5.7 Multi-agent orchestration** ☐ — supervisor/orchestrator-worker, handoff, parallel specialists; when it helps vs adds failure surface. *⚑ SAP's multi-agent framing (M11).* 
- **5.8 Reliability & control** ☐ — loop/step caps, cost ceilings, timeouts, error recovery, human-in-the-loop approvals, guardrails on tool use. *⚑ keep an autonomous system safe & bounded.*
- **5.9 When NOT to use an agent** ☐ — latency, cost, unpredictability; prefer a workflow or plain RAG. *⚑ principal-level restraint.*

## M6 — Evaluation & quality (the thing that separates toys from products)
*Why here:* M4/M5 produce nondeterministic output; you cannot ship, improve, or defend it without measurement.
*Unlocks:* safety (M7) & MLOps (M8) — guardrail metrics and monitoring are evaluation applied continuously.

- **6.1 Why eval is hard & central** ☑ (non-deterministic + open-ended → no exact-match; measure quality over a set) · golden set + regression-test instinct drilled · judge calibration (vs human labels) built · all 4 RAGAS metrics learned (recall/precision/faithfulness/answer-relevancy) — no single right answer; regression risk on every prompt/model change. *⚑ treat eval as the product, not an afterthought.*
- **6.2 The golden dataset** ☐ — building test cases from real usage; coverage; edge cases; keeping it fresh. *⚑ where ground truth comes from.*
- **6.3 Offline metrics** ☑ (hit@k / recall@k hand-coded on a golden set; retrieval is objective; RAG triad = context-relevance / faithfulness / answer-relevance) — task metrics; RAG triad (context relevance, faithfulness/groundedness, answer relevance); retrieval metrics (recall@k, MRR, nDCG). *⚑ measure each stage separately.*
- **6.4 LLM-as-judge** ☑ (faithfulness judge hand-built w/ Pydantic verdict; strict rubric catches hallucination; biases: verbosity/position/self-preference → calibrate vs human labels) — rubric & pairwise; prompting the judge; biases (position, verbosity, self-preference) and mitigations; when to trust it. *⚑ scalable eval + its traps.*
- **6.5 Human eval & feedback** ☐ — thumbs, annotations, inter-rater agreement; closing the loop. *⚑ humans anchor the automated metrics.*
- **6.6 Eval in CI (regression testing)** ☐ — prompts/models tested like code; gates on merge; canary evals. *⚑ eval as engineering discipline — links to M8.*
- **6.7 Online eval & experimentation** ☐ — A/B, shadow, guardrail metrics, drift/quality decay detection. *⚑ measure in production, not just offline.*

## M7 — Safety, security & responsible AI (containing blast radius)
*Why here:* M5 gives autonomy, M4 gives access to enterprise data — now you must make it safe to point at a customer's systems.
*Unlocks:* production (M8) — you don't deploy to a customer without these controls.

- **7.1 Prompt injection & jailbreaks** ☐ — direct vs **indirect** (poisoned documents/tool outputs); why RAG & agents expand the attack surface. *⚑ the #1 LLM security issue.*
- **7.2 OWASP LLM Top 10 (working knowledge)** ☐ — injection, insecure output handling, data poisoning, excessive agency, sensitive info disclosure, etc. *⚑ speak the enterprise security vocabulary.*
- **7.3 Data protection** ☐ — PII/secret detection & redaction, data residency, retention, training-data boundaries, tenant isolation. *⚑ enterprise data governance.*
- **7.4 Guardrails** ☐ — input & output filters, content moderation, schema/allow-list validation, topical boundaries, refusal design. *⚑ layered defense implementation.*
- **7.5 Least-privilege agency** ☐ — scoping tool permissions, approval gates for high-impact actions, sandboxing, audit logs. *⚑ bound what an agent can *do*.*
- **7.6 Responsible AI & compliance** ☐ — fairness/bias, transparency, human oversight, EU AI Act risk tiers, model/system cards, governance. *⚑ SAP cares deeply — ties to M11.*

## M8 — Production & MLOps / LLMOps (make it real)
*Why here:* now that it works, is measured, and is safe, it must be fast, cheap, reliable, observable, and shippable.
*Unlocks:* system design (M9) — these are the non-functional requirements you design against.

- **8.1 Serving & the LLM gateway** ☐ — API layer, model routing, provider fallback, rate-limit handling, multi-provider abstraction. *⚑ don't hard-wire one model.*
- **8.2 Latency engineering** ☐ — streaming/TTFT, semantic + prompt caching, parallelization, speculative patterns, smaller-model routing. *⚑ hit a p95 budget.*
- **8.3 Cost engineering** ☐ — model tiering, caching, token budgets, batching, context trimming; unit economics per request. *⚑ own the customer's bill.*
- **8.4 Scalability & resilience** ☐ — concurrency, queues/backpressure, retries+backoff, timeouts, circuit breakers, idempotency, graceful degradation/fallbacks. *⚑ distributed-systems rigor applied to LLM apps.*
- **8.5 Observability** ☐ — tracing spans (prompt→retrieval→tools→output), logging, metrics, cost/token dashboards, quality monitoring. *⚑ you can't operate what you can't see.*
- **8.6 Versioning & deployment** ☐ — version prompts/models/indexes/data together; canary, shadow, blue-green; rollback. *⚑ safe change management for nondeterministic systems.*
- **8.7 Data & ingestion pipelines** ☐ — RAG index freshness, incremental updates, reprocessing, schema/embedding-model migrations. *⚑ the index is a living data product.*
- **8.8 Fine-tuning & customization ops (awareness)** ☐ — SFT vs LoRA/PEFT vs distillation vs RAG vs prompt; when fine-tuning earns its keep; eval-gated. *⚑ know the tradeoff, avoid the reflex.*
- **8.9 Infrastructure basics** ☐ — hosted API vs self-hosted, GPU/throughput basics, containers/serverless, where inference runs. *⚑ enough infra to reason about deployment.*

## M9 — AI system design (combine everything into an architecture)
*Why here:* modules 1–8 are components; a design round asks you to assemble them for a stated problem under constraints. This is your R2 core.
*Unlocks:* delivery (M10) — the same design, now wrapped in a customer engagement.

- **9.1 The design method** ☐ — clarify → requirements (functional + NFRs: latency/cost/scale/accuracy/security) → high-level → components → data flow → tradeoffs → risks. *⚑ a repeatable framework, spoken aloud.*
- **9.2 Reference architecture: enterprise RAG assistant** ☐ — ingestion, index, retrieval, generation, guardrails, eval, observability, auth. *⚑ the canonical build.*
- **9.3 Reference architecture: agentic automation** ☐ — tools into enterprise systems, orchestration, HITL approvals, audit. *⚑ acting on enterprise systems safely.*
- **9.4 Reference architecture: document processing / extraction** ☐ — OCR/parse → structure → validate → route; classic enterprise use case. *⚑ non-chatbot AI.*
- **9.5 Enterprise integration** ☐ — SSO/identity, data residency, multi-tenancy & isolation, existing systems (ERP/CRM), event/batch vs realtime. *⚑ the "forward-deployed into a real landscape" reality.*
- **9.6 Tradeoff & sizing drills** ☐ — build vs buy, managed vs custom, model tier, latency vs cost vs quality; capacity/cost estimation. *⚑ defend decisions with numbers.*

## M10 — Forward-deployed delivery craft (the FDE difference)
*Why here:* SAP isn't hiring an architect who draws diagrams — they're hiring someone who ships in a customer's environment. This layer wraps M9.
*Unlocks:* SAP stack (M11) — the concrete environment you deliver into.

- **10.1 Discovery & scoping under ambiguity** ☐ — asking the right questions, finding the real problem behind the request, defining an MVP/thin slice. *⚑ turn vague → scoped.*
- **10.2 Prototyping & demo-driven delivery** ☐ — fastest path to a credible demo, derisking the unknown first, iterating with the customer. *⚑ speed with intent.*
- **10.3 Speed vs quality vs maintainability** ☐ — deliberate tradeoff calls, tech-debt as a decision, "good enough to hand over." *⚑ engineering judgment under time pressure.*
- **10.4 Stakeholder & expectation management** ☐ — managing non-technical customers, saying no, scope creep, communicating uncertainty of AI. *⚑ the consultant muscle.*
- **10.5 Productionization & handover** ☐ — docs, runbooks, ops transfer to platform teams, reusable assets/reference architectures. *⚑ "successful handover" is in the JD verbatim.*
- **10.6 Business impact & ROI** ☐ — tying the solution to a metric the customer's leadership cares about. *⚑ speak outcomes, not features.*

## M11 — SAP stack literacy (map generic → SAP)
*Why here:* everything above is vendor-neutral; now you translate it into SAP's components so you speak the interviewers' language.
*Unlocks:* behavioral (M12) — and lets you land SAP-specific answers in R1/R2.

- **11.1 BTP — the substrate** ☐ — global account/subaccount, Cloud Foundry/Kyma, destinations, IAS/IPS identity, CAP (Cloud Application Programming model). *⚑ where SAP apps live.*
- **11.2 AI Foundation = AI Core + Generative AI Hub** ☐ — model lifecycle, governed multi-model access, orchestration, deployments, resource groups, capacity-unit billing. *⚑ SAP's answer to the LLM gateway (M8.1).* 
- **11.3 HANA Cloud Vector Engine** ☐ — `REAL_VECTOR`, `COSINE_SIMILARITY`, vectors alongside business data (no separate vector DB). *⚑ SAP's answer to M3.3.*
- **11.4 Document Grounding & RAG on SAP** ☐ — managed grounding pipeline; CAP-LLM-Plugin; grounding on SAP data. *⚑ SAP's answer to M4.*
- **11.5 Joule & Joule Studio** ☐ — copilot; Skills (deterministic) vs Agents (autonomous); multi-agent orchestration. *⚑ SAP's answer to M5.*
- **11.6 Business Data Cloud, Knowledge Graph, SAP domain models** ☐ — unified data + SAP-grounded models + context graph. *⚑ SAP's data & grounding story.*
- **11.7 Integration reality** ☐ — S/4HANA OData + principal propagation → BTP orchestration; on-prem/cloud pattern; EU AI Act posture. *⚑ how AI actually reaches SAP business data.*

## M12 — Behavioral & communication (the human layer, all 3 rounds)
*Why here:* leaders test values in every round; this is scored continuously, not just in R3.
*Unlocks:* the offer.

- **12.1 SAP values & this JD's signals** ☐ — customer-centric, ambiguity-comfort, ownership/accountability, technical leadership, "challenge assumptions with data," continuous learning. *⚑ know exactly what they reward.*
- **12.2 STAR story matrix** ☐ — one strong story each for: ambiguity, ownership end-to-end, customer conflict, technical leadership/mentoring, a failure + learning, influencing without authority, speed vs quality call. *⚑ pre-built, reusable, specific.*
- **12.3 Communicating trade-offs to non-engineers/execs** ☐ — structure, analogy, leading with the decision + why. *⚑ the FDE core skill, tested live.*
- **12.4 Handling "I don't know" & ambiguity live** ☐ — reasoning out loud, assumptions, honesty. *⚑ leaders probe depth by pushing past your knowledge edge.*
- **12.5 Your questions for them** ☐ — sharp questions that signal seniority and fit. *⚑ last impression.*

---

## Coverage check (nothing missed — mapped to JD)
- "LLMs, RAG, vector DBs, agentic systems" → M1, M3, M4, M5 ✔
- "AI/ML Python libraries & frameworks" → threaded through M1–M8 (drilled with code) ✔
- "data pipelines & MLOps" → M8.5–8.8 ✔
- "cloud-native, distributed systems, scalability/security/reliability" → M8.4, M9 ✔
- "evaluation frameworks / trustworthy / compliant" → M6, M7 ✔
- "full lifecycle: design → deploy → operate" → M8, M9, M10 ✔
- "ambiguity, customer stakeholders, communicate trade-offs" → M10, M12 ✔
- "SAP AI technologies (advantage)" → M11 ✔

## Drill protocol (per lesson)
1. I teach it foundation-first with tiny concrete numbers. 2. You drive a small problem. 3. Rapid-fire quiz. 4. Mark ☑ and link forward. Weekly: a mock round using drilled modules.
