# SAP — Forward Deployed Application/ML Engineering Expert

**Req 454031 · "Professional" band (senior IC "Expert") · ~3 weeks out · 3 rounds, all leaders (engineering + behavioral)**

## What this role actually is
Part software engineer, part solutions architect, part customer-facing consultant. You get
embedded in a customer's messy environment, take ambiguous business problems, and ship
**production-grade AI-native applications** (LLM + RAG + agents) end-to-end — discovery →
prototype → deploy → operate → hand over. Then you do it again for the next customer.

The JD's own words, distilled to the 5 things they will test:
1. **Build AI-native apps for real** — LLMs, RAG, vector DBs, agentic workflows, in Python.
2. **Production engineering** — cloud-native, distributed systems, scalability/security/reliability, MLOps, observability.
3. **Forward-deployed judgment** — turn ambiguity into architecture; speed vs. quality vs. maintainability trade-offs; handover.
4. **Evals & trust** — evaluation frameworks, guardrails, responsible/compliant AI.
5. **Customer + leadership communication** — explain trade-offs clearly to non-engineers and execs.

## Likely mapping of the 3 leader-led rounds
| Round | Led by | Probes | Our prep |
|---|---|---|---|
| R1 Engineering depth | Eng leader | LLM app architecture, RAG internals, agents, "how would you build X" | Modules 1–4 |
| R2 Solution / forward-deployed design | Eng/architecture leader | ambiguous customer scenario → architecture, trade-offs, delivery plan, risks | Modules 3–6 |
| R3 Behavioral / values | Senior leader | ambiguity, ownership, customer-centricity, technical leadership, conflict | Module 7 |
(Exact split unknown — leaders often blend engineering + behavioral in every round. Prep all.)

## The ladder (foundation-first, teach-then-quiz)
- **M0 — Role decode & narrative** — position yourself as an FDE; the 60-sec story. *(this file + narrative doc)*
- **M1 — LLM application fundamentals** — tokens, context windows, prompting, structured output, function/tool calling, cost/latency math.
- **M2 — RAG, done properly** — chunking, embeddings, vector search, retrieval quality, reranking, grounding, failure modes. (+ SAP: HANA vector engine, GenAI Hub grounding.)
- **M3 — Agents & agentic workflows** — tool use, planning, multi-agent orchestration, when NOT to use an agent, reliability.
- **M4 — Evals, guardrails & responsible AI** — offline/online evals, LLM-as-judge, regression suites, hallucination/PII/injection guardrails, EU AI Act framing.
- **M5 — Production & MLOps** — serving, latency/cost/throughput, caching, observability/tracing, versioning, rollout, on-call for AI apps.
- **M6 — Forward-deployed delivery** — discovery, scoping under ambiguity, prototype→prod, reference architectures, handover, stakeholder mgmt.
- **M7 — Behavioral bank** — story matrix vs. SAP values (customer-centric, ambiguity, ownership, tech leadership, "challenge with data").
- **M8 — SAP stack literacy** — BTP, AI Core, Generative AI Hub, Joule/Joule Studio, HANA Cloud vector, Business Data Cloud, S/4HANA context, SAP domain models. (Nice-to-have, not required — but earns big signal.)

## SAP stack cheat-sheet (interviewers speak this)
- **BTP** = SAP Business Technology Platform — the substrate everything runs on.
- **AI Foundation** = AI Core + Generative AI Hub (build/run/integrate AI on BTP).
- **Generative AI Hub** = governed multi-model LLM access + orchestration + document grounding.
- **HANA Cloud Vector Engine** = native `REAL_VECTOR` type + `COSINE_SIMILARITY` — vector store inside the business DB, no separate vector DB.
- **Joule** = SAP's copilot; **Joule Studio** = author Skills (deterministic) & Agents (autonomous).
- **Business Data Cloud** = unified data layer; **SAP domain models** = models grounded in SAP business context.
- Pattern for on-prem: S/4HANA exposes OData → BTP app reads via principal propagation → calls orchestration → returns result.

## Progress
- [x] Stage 0 — role research + JD captured (Req 454031)
- [x] Detailed curriculum authored → see [CURRICULUM.md](CURRICULUM.md) (12 modules, ~85 linked concepts)
- [x] Hands-on lab scaffolded → `lab/` (uv + Gemini + LangGraph; one file per concept)
- [x] M1 engine — taught & drilled (tokens → tool calling); backfilled as runnable lab files
- [ ] M1 wrap — 1.10 model selection, 1.11 failure modes
- [ ] M2 prompting → M3 retrieval (hand-coded) → … → M12

## Sources
- SAP JD Req 454031 (jobs.sap.com)
- SAP Business AI release highlights Q2 2026; GenAI Hub + HANA vector RAG (community.sap.com)
