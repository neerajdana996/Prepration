# SAP FDE — Interview Practice: Agents & Multi-Agent Systems (M5)

Real-style interview questions for the agentic-systems part of the loop. The SAP FDE JD explicitly wants "integrating Agentic AI into complex business processes," so expect the interviewer to push past definitions into **what breaks in production and how you bound it**.

**How to use:** Read the question, answer out loud in ~2 min before reading the model answer, then run the linked lab to make it muscle memory. In the room, always default to the *least autonomy that works* and name the failure mode before the interviewer does.

---

## Tier 1 — fundamentals

### Q: What actually makes something an "agent" vs. a plain LLM call?

**Tests:** Whether you have a crisp mental model or just buzzwords.

**Answer (production-grade):** An agent is **LLM + tools + a loop + a stopping condition**. The LLM sees the goal and current observations, decides the next action (usually a tool call), the tool runs, the result is fed back as a new observation, and the loop repeats until the model emits a final answer or a seatbelt fires (step cap, budget, timeout). The defining property is that **control flow lives in the model at runtime**, not in your code. A single LLM call replies but doesn't act or choose a path; tool use alone isn't enough either if the sequence is hard-coded. The load-bearing pieces people forget: the *stopping condition* (without it you get infinite loops and runaway cost) and *observations fed back* (that's what lets it self-correct). If I can draw the exact sequence of steps in advance, it's a workflow, not an agent.

**Lab:** [`../lab/agents/m5_01_agent_loop.py`](../lab/agents/m5_01_agent_loop.py) — minimal loop from scratch with a step-cap seatbelt.

### Q: Explain ReAct. What's the difference between "native" tool-calling and classic text ReAct?

**Tests:** Do you understand the reasoning loop and modern implementation reality.

**Answer (production-grade):** ReAct = **Reason + Act**: the agent interleaves a Thought (chain-of-thought about what to do), an Action (a tool call), and an Observation (the tool result), looping until done. It mirrors how people solve problems — think, do, see, think again — which is why nearly every agent framework is ReAct under the hood. Two implementations:
- **Classic text ReAct**: you prompt the model to literally *write* `Thought: / Action: / Action Input:` as text, then you parse the string, run the tool, and append `Observation:`. Reasoning is explicit and visible, but you own a fragile string parser.
- **Native tool-calling** (GPT/Claude/Gemini function calling): the model emits a structured tool call directly; the runtime executes it and returns a typed result. More robust, no parser — **but the reasoning is silent** (it happens inside the model, not in the visible transcript). That's the key gotcha: with native tool-calling you don't get a free "Thought" trace, so for debugging you either prompt it to narrate a one-line reason or rely on trajectory logging.

Production almost always uses native tool-calling; text ReAct is the teaching form and still useful with models that lack a tool-calling API.

**Lab:** [`../lab/agents/m5_02_react.py`](../lab/agents/m5_02_react.py) (native, narrated) and [`../lab/agents/m5_02b_react_text.py`](../lab/agents/m5_02b_react_text.py) (classic text, you parse it).

### Q: Workflow vs. agent — how do you decide? Walk me up the "autonomy ladder."

**Tests:** Engineering maturity — do you reach for the simplest thing that works.

**Answer (production-grade):** The axis is **predictability vs. autonomy**, and the rule is *least autonomy that works*. The ladder:
1. **Single LLM call** — one input, one output. Classification, extraction, a rewrite.
2. **Workflow** — LLM calls wired together by *your code* in a fixed path (e.g. retrieve → generate → format). Predictable, cheap, testable. Use when you know the steps in advance.
3. **Router** — an LLM classifies intent and picks one of N predefined branches. A tiny bit of dynamism, still bounded.
4. **Agent** — the model decides the steps at runtime and loops. Use only when the path genuinely can't be mapped ahead of time (open-ended research, diagnostics, coding).

Start at the bottom and climb only when the task forces it. Over-engineering a known task with an agent buys you cost, latency, and non-determinism for nothing; under-engineering an open-ended task into a rigid pipeline breaks the moment reality deviates. In production the winning pattern is **hybrid**: deterministic boundaries where you need reliability/compliance, agent autonomy only inside bounded scopes.

**Lab:** Build: extend [`../lab/agents/m5_06_multi_agent.py`](../lab/agents/m5_06_multi_agent.py) — the supervisor is a router; note it does *not* loop, so it sits at rung 3, not 4.

### Q: What is the anatomy of a good tool definition?

**Tests:** Do you treat the LLM as the *user* of your tool API.

**Answer (production-grade):** Design tools as UX for a literal, non-mind-reading user:
- **Name** — specific and action-oriented: `lookup_invoice`, not `invoice_tool`. It's the first signal for selection.
- **Description** — the single most important field; it drives selection. State what it does, *when to use it* ("use this when the user asks about a specific invoice id"), and any format hints ("dates as YYYY-MM-DD").
- **Typed args** — meaningful parameter names, explicit JSON-schema types, enums for closed sets. This is a contract that stops the model inventing formats.
- **Errors as return values** — return the error *as data* with an actionable message, not a thrown exception that kills the run (see next questions).
- **Granularity** — right-sized. Too fine → the model chains 5 calls for one job and drifts; too coarse → it can't compose. If you see over-chaining, add a composite tool.
- **Idempotency** — assume at-least-once execution; mutating tools take idempotency keys so a retry can't double-charge. Annotate read (safe) vs. write (destructive) so you can gate the destructive ones.

**Lab:** [`../lab/agents/m5_01_agent_loop.py`](../lab/agents/m5_01_agent_loop.py) — typed `@tool` functions with docstring descriptions.

---

## Tier 2 — applied / design

### Q: Categorize tool-call failure modes and give a defense for each.

**Tests:** Production instinct — you've seen agents fail, not just read about them.

**Answer (production-grade):** Four buckets:
1. **Bad or hallucinated calls** — invented tool that doesn't exist, wrong/missing args, malformed JSON, args not grounded in the conversation. *Defense:* strict input schemas + a validation layer *between* the proposed call and execution (reject unknown tools, coerce/validate args before running). Schema fixes ~half; the validator catches most of the rest.
2. **Execution errors** — the tool runs but throws (bad id, timeout, 500). *Defense:* catch and return the error **as an observation** so the agent can read it and retry differently.
3. **Loop failures** — infinite loops, repeating the same call with identical args, objective drift on long tasks. *Defense:* step cap, detect repeated identical calls, cost/token budget, wall-clock timeout — circuit breakers.
4. **Safety failures** — the agent takes a high-blast-radius action (refund, delete, send) that's wrong. *Defense:* human-in-the-loop approval gates on destructive tools, and least-privilege tool scoping.

The one-liner: **schema + validator before, errors-as-observations after, seatbelts around, approval gates on the dangerous ones.**

**Lab:** [`../lab/agents/m5_03_robust_agent.py`](../lab/agents/m5_03_robust_agent.py) — tool raises on a bad id; the loop feeds the error back and the agent recovers.

### Q: How do you make an agent *reliable* despite a non-deterministic core?

**Tests:** Can you bound a stochastic system with deterministic guardrails.

**Answer (production-grade):** You can't make the LLM deterministic, so you wrap it in deterministic control:
- **Errors-as-observations** — never let a tool exception crash the run; feed the message back with a hint ("invoice 999 not found; valid ids are..."). The agent self-corrects instead of dying. This is the single highest-leverage reliability move.
- **Step cap** — hard max iterations; on hit, stop and return partial + reason.
- **Cost/token budget** — track spend per run; abort when exceeded. Agents that loop can call the LLM thousands of times on a minor bug.
- **Timeouts** — per-tool and per-run wall clock.
- **Repeated-call detection** — same tool + same args twice usually means it's stuck; break or escalate.
- **Validation layer** on tool args before execution.
- **Idempotency keys** on mutating tools so retries are safe.

Frame it as backend engineering imported into the loop: budgets, retries, guards, timeouts, circuit breakers.

**Lab:** [`../lab/agents/m5_03_robust_agent.py`](../lab/agents/m5_03_robust_agent.py) — errors-as-observations + seatbelt.

### Q: When do you put a human in the loop, and how do you gate it?

**Tests:** Judgment about autonomy vs. risk in a business process (core to the FDE role).

**Answer (production-grade):** Gate on **blast radius**, not on convenience. Safe, reversible reads run autonomously. High-impact, irreversible, or costly actions (refunds, DB writes, sending emails, deleting data, moving money) pause for approval: the loop stops, surfaces the *proposed* action and its args, and waits for y/n. On approve, execute; on deny, feed "DENIED" back as an observation so the agent adapts rather than being forced through. Two senior nuances:
- **Interrupt fatigue** — if you gate everything, reviewers rubber-stamp and the gate is theater. Reserve gates for genuinely high-stakes/ambiguous actions; let low-stakes run with strong guardrails + after-the-fact monitoring.
- **Idempotency at the gate** — a resumed run must not re-fire the side effect. Checkpoints make *state* recoverable, not side effects exactly-once, so pair the gate with idempotency keys.

**Lab:** [`../lab/agents/m5_07_human_in_loop.py`](../lab/agents/m5_07_human_in_loop.py) — reads auto-run, refund is gated y/n, deny → observation.

### Q: How does an agent handle memory? Distinguish short-term from long-term.

**Tests:** Do you know memory is two different mechanisms, not one.

**Answer (production-grade):** Two layers:
- **Short-term (working) memory** = the **context window**: the running message list for this task/session — recent thoughts, actions, observations. It's what keeps the agent from looping and lets it reason about the next step. It's session-bound and discarded when the run ends. It's also finite, so long runs need compaction/summarization.
- **Long-term memory** = an **external store** that persists across sessions, typically a vector DB. You write facts/experiences as embeddings; on a new turn you **retrieve the relevant ones by meaning and inject them** into context. That is literally **RAG over the conversation history** — same retrieve-then-augment machinery as document RAG, just pointed at past interactions. It's why an agent can recall your preference in a brand-new session with zero chat history.

The trap: don't conflate "the model remembers" (context window, transient) with "the system remembers" (external store, durable).

**Lab:** [`../lab/agents/m5_09_memory.py`](../lab/agents/m5_09_memory.py) — writes facts to a store, retrieves by embedding+cosine in a fresh session (RAG over history).

### Q: Plan-and-execute vs. ReAct — when would you pick each?

**Tests:** Awareness that ReAct isn't the only reasoning loop.

**Answer (production-grade):**
- **ReAct** interleaves think→act→observe and re-decides after every observation. High adaptability; ideal when the environment is unpredictable and tool results should change the next step (troubleshooting, exploration). Weakness: on long tasks it can drift from the objective or loop.
- **Plan-and-execute** splits a **planner** (decompose the goal into an ordered step list up front) from an **executor** (work the list, often with a smaller/cheaper model), then optionally re-plan at the end. Better for long-horizon, mostly-deterministic workflows: fewer expensive planning calls, clearer structure, higher accuracy on complex multi-step tasks. Weakness: brittle if a step returns something the fixed plan didn't anticipate — hence re-planning.

Rule of thumb: unpredictable/short → ReAct; long-horizon/structured → plan-and-execute with a re-plan escape hatch. (Reflexion is the retry-with-a-lesson variant: it writes a critique to episodic memory and reattempts the whole task.)

**Lab:** Build: turn [`../lab/agents/m5_01_agent_loop.py`](../lab/agents/m5_01_agent_loop.py) into plan-and-execute — one LLM call to produce a step list, then execute steps, then a final review call.

### Q: How do you test a non-deterministic agent?

**Tests:** This is the round that fails most candidates — do you test trajectory + outcome, not one lucky run.

**Answer (production-grade):** Move the unit of assertion from the output string to the **execution trace**, and measure a **pass rate over N runs** (one green run proves nothing on a stochastic system). Assert at three levels:
1. **Tool selection** — the right tool was called (and, for negative cases, that *no* tool was called when none was warranted).
2. **Argument validity** — args are well-formed and *grounded* in the input, not hallucinated.
3. **Trajectory + outcome** — the ordered sequence reaches the goal without detours/repeats/loops, and the final answer is correct.

Practical rig: **mock/sandbox the tools** (a test that hits real refund APIs is dangerous or untestable), run temperature 0, use an **LLM-as-judge** for fuzzy free-text answers, and add explicit tests that guardrails/HITL actually *fire*. Cheap bonus: the **"no-tool test"** — remove the tool a known task needs and re-run; a reliable agent refuses with an explanation, a hallucinating one invents a call. Also define **failure boundaries** — the things that must never happen (hallucinated calls, action on the wrong entity, fabrications) — as golden assertions.

**Lab:** [`../lab/agents/m5_08_agent_testing.py`](../lab/agents/m5_08_agent_testing.py) — asserts trajectory + outcome across N runs, reports a pass rate, tools mocked.

---

## Tier 3 — senior trade-offs & debugging

### Q: When does multi-agent actually help, and when does it just add failure surface?

**Tests:** The senior instinct to justify complexity, not chase it.

**Answer (production-grade):** Multi-agent helps when there's **genuine specialization** — distinct toolsets, prompts, or domains that don't fit one coherent agent (a billing specialist with billing tools vs. a tech-support specialist with diagnostics), or when separate context windows keep each agent focused. Default topology is a **supervisor/orchestrator**: one router delegates to specialists and synthesizes results; routing stays predictable, specialists get autonomy only inside their scope.

It hurts when you split work that one agent could do — you pay extra latency/cost and, worse, **errors compound across handoffs**. Two 90%-accurate agents in series don't give 90%; the errors stack, and the downstream agent has no way to know its input is wrong — the writer confidently builds on the researcher's hallucinated stat. So every handoff needs validation. The progression: **supervisor until it's not enough → sequential pipeline where stages are fixed → free-for-all network only with a demonstrated need and the observability to debug it** (any-agent-calls-any-agent is powerful and almost always the wrong first choice). Route on **capability descriptions**, keep the router/registry/dispatch in sync, and set a max-turns cap with a default resolution rule to avoid inter-agent deadlock.

**Lab:** [`../lab/agents/m5_06_multi_agent.py`](../lab/agents/m5_06_multi_agent.py) — supervisor routes to 3 specialists; a runtime assert keeps route schema, registry, and dispatch in sync (no "agent soup").

### Q: Supervisor pattern vs. agents-as-tools vs. handoffs — what's the difference?

**Tests:** Precision about multi-agent wiring, not just "it's multi-agent."

**Answer (production-grade):**
- **Supervisor / orchestrator**: a central agent decomposes the task, dispatches subtasks to specialists, gathers their outputs, and synthesizes the final answer. It enforces step validity, safety, and termination. Control always returns to the supervisor.
- **Agents-as-tools**: each specialist is wrapped as a callable `@tool`; the supervisor is itself a ReAct agent that "calls" a specialist like any other tool. Clean because it reuses the tool-calling machinery — the specialist runs its own loop internally and returns a result. Control returns to the caller.
- **Handoff**: one agent *transfers control and context* to another and steps out; the new agent owns the conversation from there (classic triage → billing). Good for "route once to the right owner," but you must decide explicitly what context passes, and control doesn't automatically come back.

Rule: prefer supervisor/agents-as-tools (control returns, easier to reason about and validate) unless the interaction genuinely is a one-way transfer of ownership.

**Lab:** [`../lab/agents/m5_12_langgraph_agents_as_tools.py`](../lab/agents/m5_12_langgraph_agents_as_tools.py) — specialist ReAct agents exposed as tools to a supervisor ReAct agent.

### Q: An agent works in the demo but fails ~20% of the time in prod. How do you debug it?

**Tests:** Real operational debugging of a stochastic system.

**Answer (production-grade):** First, make failure *observable and reproducible*: log the full **trajectory** (every thought, tool call + args, observation) for each run and bucket the 20% by failure mode. Then attack by category:
- **Wrong tool / bad args** (most common): the description or schema is ambiguous. Tighten "use this when" guidance, add enums/examples, add a pre-execution validator. Run the no-tool test.
- **Over-trust of a bad tool output**: the agent treats a wrong tool result as gospel (measurable ~14% flip from correct→wrong once a bad output enters the trace). Add sanity checks/validation on tool *outputs*, not just inputs.
- **Loops / drift** on longer tasks: add repeated-call detection, tighten the step cap, or switch to plan-and-execute so the objective is pinned in an explicit plan.
- **Handoff corruption** (if multi-agent): a specialist is producing bad output the next stage builds on — add per-handoff validation and check whether you even need the split.

Then close the loop: turn each reproduced failure into a golden test in the trajectory suite, and track pass rate over N runs so you know the fix actually moved the number. Guard against flaky-eval too — a hallucinated tool call can fool a trajectory-only judge, so verify real outcomes.

**Lab:** [`../lab/agents/m5_08_agent_testing.py`](../lab/agents/m5_08_agent_testing.py) — turn reproduced failures into trajectory+outcome assertions with a pass rate.

### Q: Explain LangGraph's core abstractions and what you get "for free."

**Tests:** Can you reason about the runtime, not recite docs — and connect it to the hand-built loop.

**Answer (production-grade):** LangGraph is a **state graph**: **nodes** (functions that read and update state), **edges** (including *conditional* edges that route on state), and a typed **state** object (commonly the message list, merged via reducers). An agent is just an `agent` node and a `tools` node with a conditional edge — "tool calls present? → loop to tools; none? → finish" — i.e. the exact loop you hand-build in m5_01. `create_react_agent` builds that graph for you. What you get for free once it's a graph:
- **Checkpointer** = memory: it snapshots full state after every step, keyed by `thread_id` (within-thread memory). That gives durable resume, crash recovery, and multi-turn memory without resending everything. (Cross-thread long-term memory is a separate **Store** — don't confuse the two.)
- **interrupt / interrupt_before** = HITL: pause execution, surface state to a human, resume from the checkpoint via a `Command`. Requires a checkpointer.
- Streaming, retries, and subgraphs (for multi-agent).

Senior nuances: checkpointing adds an I/O round-trip per step (the price of resumability/audit); `interrupt()` **re-runs the node from its start** on resume, so keep node logic idempotent; and checkpoints recover state but not side effects exactly-once — add idempotency keys. In 2026 framing, **LangGraph is the runtime, LangChain is the layer on top** — it's a layering question, not a rivalry.

**Lab:** [`../lab/agents/m5_10_langgraph.py`](../lab/agents/m5_10_langgraph.py) (graph = your loop), [`../lab/agents/m5_11_langgraph_memory.py`](../lab/agents/m5_11_langgraph_memory.py) (MemorySaver + thread_id).

### Q: How would you design a long-horizon agent (e.g. "research a company's full history and write a 50-page report") so it doesn't get lost?

**Tests:** Handling the hard 2026 scenario — context limits, drift, cost over a long run.

**Answer (production-grade):** Don't run one giant ReAct loop against a growing context — it'll drift and blow the window. Structure it:
- **Plan-and-execute** at the top: a planner decomposes into sections/subtasks (the explicit plan pins the objective so the agent can't lose it), an executor works them, then a review/re-plan pass.
- **Decompose to bounded subtasks** each with its own fresh, focused context — optionally specialist sub-agents (researcher, writer, editor) via a supervisor, with **validation at each handoff** so a hallucinated fact doesn't get polished into the final report.
- **External memory** for accumulated findings (a store / scratchpad) so state doesn't have to live in one context window; retrieve per section (RAG over your own notes). Compact/summarize as you go.
- **Guardrails**: per-subtask step caps and a global cost/token budget; checkpoint after each section so a crash resumes mid-report.
- **HITL** at plan-approval and before publishing.

The theme: convert one unbounded autonomous run into many bounded ones with durable state and validation between them.

**Lab:** Build: compose [`../lab/agents/m5_06_multi_agent.py`](../lab/agents/m5_06_multi_agent.py) (specialists) + [`../lab/agents/m5_09_memory.py`](../lab/agents/m5_09_memory.py) (external store) + a plan-and-execute planner; checkpoint via [`../lab/agents/m5_11_langgraph_memory.py`](../lab/agents/m5_11_langgraph_memory.py).

### Q: An agent that executes user-supplied code or hits arbitrary systems — how do you contain it? (prompt injection, sandboxing)

**Tests:** Security posture for autonomous systems — a live 2026 interview theme (OpenAI asks it).

**Answer (production-grade):** Treat the agent as untrusted and design for blast-radius containment:
- **Least privilege**: give it only the tools/scopes the task needs; separate read (safe) from write (destructive) and gate the writes behind HITL.
- **Sandboxing**: run any code execution in an isolated, ephemeral, network-restricted environment (container/VM/microVM) with CPU/mem/time limits and no access to secrets or prod data. Assume escape attempts; monitor for them.
- **Prompt-injection defense**: never trust content pulled from tools/web/documents as instructions — it's data, not commands. Keep a strong system prompt boundary, don't let retrieved text redirect tool use, and validate/allowlist tool calls regardless of what the content "says." Human-approve any action whose parameters trace back to untrusted content.
- **Idempotency + audit**: idempotency keys on side-effecting tools; full trajectory logging for forensics.
- **Budgets/timeouts**: cap steps, cost, and wall clock so a hijacked loop can't run away.

The framing: it's the intersection of LLM behavior and classic distributed-systems/security engineering — sandboxes, allowlists, least privilege, audit.

**Lab:** Build: wrap a `run_python(code)` tool with a subprocess timeout + restricted globals, add an allowlist validator before execution, and gate it behind [`../lab/agents/m5_07_human_in_loop.py`](../lab/agents/m5_07_human_in_loop.py)'s approval pattern.

### Q: Native tool-calling hides the reasoning. How do you get observability without going back to text ReAct?

**Tests:** Do you understand the silent-reasoning trade-off and how to operate around it.

**Answer (production-grade):** You accept that the Thought is internal and instrument the *behavior* instead. Log the full trajectory — every tool call, its args, and each observation — since that's the ground truth of what the agent did regardless of hidden reasoning. Optionally prompt the model to emit a one-line justification alongside each call (cheap, human-readable, but treat it as a post-hoc rationalization, not proof of the real computation). Add tracing (LangSmith/OpenTelemetry-style spans per step) with latency and token cost per call. For evaluation, assert on the trajectory + outcome, not on the reasoning text. Only drop to explicit text ReAct when you specifically need a verbatim reasoning transcript and are willing to own the fragile parser and the reliability hit — for most prod systems trajectory logging + one-line rationales are the better trade.

**Lab:** [`../lab/agents/m5_02_react.py`](../lab/agents/m5_02_react.py) — native call with a narrated one-line reason (compare the visibility to m5_02b text ReAct).

---

## Code gaps to add

Concepts covered above that don't yet have a runnable lab file:

- **`m5_04_agent_soup.py`** — a deliberately over-decomposed multi-agent system (too many redundant agents) to *feel* the compounding-error / debuggability cost before m5_06 fixes it. (Referenced as "M5.4" in m5_06's comments but no file exists.)
- **`m5_05_agents_as_tools.py`** — the non-LangGraph agents-as-tools pattern (referenced as "M5.5"); m5_12 is the LangGraph version only.
- **`m5_13_plan_and_execute.py`** — planner (decompose → step list) + executor + final review, to contrast with the ReAct loop (Tier 2 planning question has no lab).
- **`m5_14_budgets_and_timeouts.py`** — explicit cost/token budget + per-tool and per-run wall-clock timeout + repeated-call detection (m5_03 only shows the step cap + errors-as-observations, not budgets/timeouts).
- **`m5_15_validation_layer.py`** — a pre-execution validator between the proposed tool call and the tool (reject unknown tools, schema-check/coerce args, ground args) + the "no-tool test" harness.
- **`m5_16_sandbox_code_agent.py`** — a `run_python` tool sandboxed with subprocess timeout + restricted globals + allowlist validator + HITL gate (Tier 3 containment question is build-only).
- **`m5_17_langgraph_interrupt.py`** — LangGraph HITL via `interrupt()` / `interrupt_before` + `Command` resume (m5_07 is the hand-built HITL; m5_11 shows checkpointer memory but not the interrupt gate).
- **`m5_18_reflexion.py`** — retry-with-a-lesson: write a self-critique to episodic memory and reattempt the task (mentioned in the planning question, no lab).

## Sources

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (workflow vs. agent, least-autonomy, hybrid) — via secondary summaries below
- [DataCamp — Top 30 Agentic AI Interview Questions (2026)](https://www.datacamp.com/blog/agentic-ai-interview-questions)
- [Interview Coder — Top 35 Agentic AI Interview Questions (2026)](https://www.interviewcoder.co/blog/agentic-ai-interview-questions)
- [Interview Coder — Top 35 LangGraph Interview Questions (2026)](https://www.interviewcoder.co/blog/langgraph-interview-questions)
- [Dataford — OpenAI Agentic AI Engineer Interview Guide 2026](https://dataford.io/interview-guides/openai/agentic-ai-engineer) (duplicate-tool-call, sandbox agent code execution)
- [Redis — AI Agents vs Workflows: When to Use Each](https://redis.io/blog/agents-vs-workflows/)
- [Machine Learning Mastery — Agentic Workflow vs. Autonomous Agent](https://machinelearningmastery.com/agentic-workflow-vs-autonomous-agent-whats-the-difference/)
- [LeewayHertz — ReAct agents vs function-calling agents](https://www.leewayhertz.com/react-agents-vs-function-calling-agents/)
- [MS Azure Club — ReAct Agents from scratch: native function calling vs custom TAO parsing](https://msazure.club/react-agents-building-from-scratch-native-function-calling-vs-custom-tao-parsing/)
- [Confident AI — AI Agent Testing: Tool Calling, Regressions, Failure Handling](https://www.confident-ai.com/knowledge-base/guides/ai-agent-testing) (trajectory assertions, no-tool test, failure boundaries)
- [PALADIN — Self-Correcting LM Agents to Cure Tool-Failure Cases (arXiv 2509.25238)](https://arxiv.org/html/2509.25238) (failure-mode taxonomy, recovery)
- [Roborhythms — Fix Agent Tool Hallucinations with a 4-Section Prompt](https://www.roborhythms.com/fix-agent-tool-hallucinations-4-section-prompt/) (schema + validator root causes)
- [apxml — LLM Tool Specifications and Designing Tool Interfaces](https://apxml.com/courses/building-advanced-llm-agent-tools/chapter-1-llm-agent-tooling-foundations/tool-specifications-descriptions)
- [AI Expert — Designing MCP tools that LLMs use correctly](https://aiexpert.ee/en/articles/mcp-tools-llms-use-correctly) (idempotency, granularity, errors-as-data)
- [Towards Data Science — How Agent Handoffs Work in Multi-Agent Systems](https://towardsdatascience.com/how-agent-handoffs-work-in-multi-agent-systems/)
- [System Design Handbook — Multi-Agent System Design (2026)](https://www.systemdesignhandbook.com/guides/multi-agent-system-design/)
- [Sapota — Multi-agent handoffs: how orchestration works and when it backfires](https://www.sapotacorp.vn/blog/sapota-multi-agent-handoffs-orchestration) (supervisor→sequential→network progression, compounding error)
- [DeepWiki — LangGraph Human-in-the-Loop and Interrupts](https://deepwiki.com/langchain-ai/langgraph/3.7-human-in-the-loop-and-interrupts)
- [LangChain Reference — interrupt()](https://reference.langchain.com/python/langgraph/types/interrupt)
- [aiagentmemory.org — AI Agent Architecture Patterns: ReAct, Plan-and-Execute, Memory](https://aiagentmemory.org/articles/ai-agent-architecture-patterns/)
- [The AI Engineer — ReAct vs Plan-and-Execute vs ReWOO vs Reflexion](https://theaiengineer.substack.com/p/the-4-single-agent-patterns)
</content>
</invoke>
