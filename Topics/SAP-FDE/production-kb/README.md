# Production KB — building production-grade, distributed AI systems

A reusable knowledge base. One folder per **pillar**; inside, one folder per **topic**, each with:

```
<pillar>/<topic>/
  explanation.md     # what it is, why it matters, the diagram, the defense/pattern
  example.py         # the naive / vulnerable / broken version (runnable)
  prevention.py      # the fixed / defended / production version (runnable)
  images/*.svg       # standalone diagrams
```

(For non-security pillars, `prevention.py` is named `solution.py` / `pattern.py` — the "here's the right way" file.)

## Pillars
| Pillar | What | AI twist |
|---|---|---|
| **security** | authz, injection defense, data protection | prompt injection (direct + indirect) |
| **data** | storage, vector DB, tenant isolation, freshness | embeddings, re-index on embedder change |
| **latency** | caching, streaming, routing, p95 | decode-bound; semantic cache |
| **reliability** | retry, circuit breaker, fallback, redundancy | 429s + provider outages |
| **scalability** | horizontal scale, queues, load balancing | token throughput, rate limits |
| **observability** | traces, metrics, logs | trace the prompt→retrieval→tools→output chain |
| **cost** | budgets, tiering | per-token; output ~5×; caching |
| **quality** | evals, guardrails, grounding | nondeterministic → eval, not unit tests |

## Built so far — `security/` pillar complete (7 topics)
- `prompt-injection/` ✅ (template exemplar — direct vs indirect)
- `jailbreaks/` ✅ (safety-bypass vs app-instruction subversion)
- `sensitive-info-disclosure/` ✅ (system-prompt / secret / cross-tenant leakage)
- `excessive-agency/` ✅ (too many/too-powerful tools → HITL + least-privilege)
- `insecure-output-handling/` ✅ (LLM output → eval/SQL/HTML sink; AST allow-list)
- `pii-redaction/` ✅ (mask before model + logs; role-scoped retrieval)
- `owasp-llm-top10/` ✅ (reference overview + offline self-audit checklist)

Other pillars (data, latency, reliability, scalability, observability, cost, quality) are queued — see the running app's lab (`../lab/`) for the concept code, and the interview Q&A in `../interview-practice/`.

Runnable code needs `GOOGLE_API_KEY` (run from `../lab` which has the venv + `.env`), e.g.:
```bash
cd Topics/SAP-FDE/lab && uv run python ../production-kb/security/prompt-injection/example.py
```
