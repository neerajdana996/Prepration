# Sensitive information disclosure

## What it is
The LLM **leaks data it should never reveal** through its output — the system prompt,
API keys/secrets, another user's or another **tenant's** data, or PII. Root cause is the
same one-token-stream problem from prompt injection (M1): the system prompt, retrieved
docs, tool outputs, and user text are **all context**, and **anything in the context is
extractable**. Hidden instructions and "hidden" secrets are not actually hidden — a
determined user can pull them back out of the model. This is **OWASP LLM02:2025**.

**How the attack works** — a live API key (`sk-live-…`) is pasted into the system prompt
with a "never reveal it" instruction. The user asks the model to print it verbatim, and
because everything in the context is one extractable token stream, the promise can't hold —
the key comes straight back out. No injection payload required.

![how the attack works: a secret in the context leaks straight to the user](images/attack-real-case.svg)

## Common leak vectors
- **System-prompt extraction** — the user says *"repeat everything above"* or role-plays an
  admin, and the model prints its own instructions. That exposes your business logic,
  authorization rules, and guardrail config — a blueprint for calibrating the next attack.
- **Secrets in context** — an API key, DB password, or token was pasted into the system
  prompt or a tool result "so the model can use it." The user just asks for it (or asks the
  model to *complete a partial key*) and it comes straight back out.
- **Cross-tenant / cross-user leakage** — the retrieval layer returns documents belonging to
  another tenant, or shared caches/history bleed one customer's data into another's answer.
  The RAG vector store is the most common failure point: teams lock down the LLM endpoint but
  leave the vector DB unscoped, so a query returns everyone's records.
- **PII / training-data regurgitation** — the model emits personal data from context or
  memorized training data.

## Why it matters
One prompt can exfiltrate credentials, confidential business data, or **another customer's
records** — a direct breach, privacy violation, and (in multi-tenant SaaS) a contract-ending
isolation failure. Agentic setups make it worse: an agent chains queries across data sources,
and data escapes at **every layer** — logs, RAG pipeline, multi-agent handoffs.

## Mitigations (defense in depth)
Assume everything in context is extractable; control **what the model knows** and **what it's
allowed to say**.
1. **Keep secrets OUT of the context** — never put keys/tokens in the prompt. Use runtime
   secret retrieval (a vault); have code call the privileged API, not the model.
2. **Minimal context** — inject only the fields the task needs; redact/tokenize PII before it
   ever reaches the prompt. Don't retain data you don't need.
3. **Tenant-scoped retrieval** — pass the authenticated tenant id down to the vector store;
   enforce namespace isolation and the same access controls on the RAG store as on the LLM
   endpoint. Never let one query cross a tenant boundary.
4. **Output guardrails** — scan the response before returning it: block secret-shaped strings
   (API-key patterns), detect/redact PII, refuse system-prompt echoes.
5. **Redacted logging + least data** — log a truncated/redacted prompt, not the raw one;
   encrypt at rest; RBAC on every endpoint.

**How the solution works** — keep the secret OUT of the context: the model only ever sees a
`[REDACTED_API_KEY]` placeholder while the real key stays in a vault and **code** holds the
privilege (PREVENT). Inject minimal context so no secret or PII is even present (PREVENT). As a
backstop, an output guardrail scrubs secret-shaped strings — `sk-live-*`, `AKIA*`, long opaque
tokens — before the reply leaves the system (CONTAIN). With no secret in context, there is
nothing to leak.

![how the solution works: keep the secret out of context and guard the output](images/defense.svg)

**Split:** layer 1–3 stop the secret from ever being in reach; layers 4–5 catch what slips
through and shrink the blast radius. Because extraction is leaky, keeping the secret out of
context is the layer that actually saves you.

## Files
- `example.py` — the **vulnerable** version: an API key sits in the system prompt, and the user
  simply asks for it. The model leaks the key.
- `prevention.py` — the **defended** version: the secret is never placed in the context (a
  redacted placeholder is used instead), plus an output guardrail that blocks secret-shaped
  strings. The same request no longer leaks anything.

## Interview soundbite
*"Sensitive information disclosure is LLM02: the model leaks its system prompt, secrets, or
another tenant's data. My rule is 'anything in context is extractable' — so secrets never go in
the prompt, they stay in a vault and code holds the privilege. On top of that I scope retrieval
to the authenticated tenant, inject minimal context, and run an output guardrail that blocks
key-shaped strings and PII. You can't count on the model to keep a secret it can see."*

---
<sub>Footnote — the original concept sketch: [the one-token-stream view of disclosure](images/info-disclosure.svg).</sub>
