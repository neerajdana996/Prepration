#!/usr/bin/env python3
"""OWASP Top 10 for LLM Applications (2025) — offline self-audit checklist.

REFERENCE topic: this is NOT a vulnerable demo. It is a control checklist you can
run against any LLM/GenAI system under review. Each item is one OWASP risk plus a
single yes/no control question — if you can't answer "yes", that's a gap.

Fully offline: no LLM, no network, no API key. Just:  python3 example.py
Source of the list: OWASP GenAI Security Project — https://genai.owasp.org/
"""

# (code, name, control question, deep-dive KB topic in this repo)
CHECKLIST = [
    ("LLM01", "Prompt Injection",
     "Do you treat ALL user input AND ingested data (RAG docs, tool output) as untrusted?",
     "security/prompt-injection"),
    ("LLM02", "Sensitive Information Disclosure",
     "Do you redact/scan inputs and outputs and scope retrieval per tenant so PII/secrets can't leak?",
     "security/sensitive-info-disclosure, security/pii-redaction"),
    ("LLM03", "Supply Chain",
     "Are your models, datasets, and packages vetted, pinned, and provenance-checked (no unsafe pickle)?",
     "(reference only)"),
    ("LLM04", "Data and Model Poisoning",
     "Is training/fine-tune/embedding data curated and validated, and are models eval'd for backdoors?",
     "(reference only)"),
    ("LLM05", "Improper Output Handling",
     "Do you treat model output as untrusted before it hits code/SQL/HTML (encode, parameterize, sandbox)?",
     "security/insecure-output-handling"),
    ("LLM06", "Excessive Agency",
     "Are tools least-privilege and are high-impact/irreversible actions gated behind a human?",
     "security/excessive-agency"),
    ("LLM07", "System Prompt Leakage",
     "Are secrets and authz logic OUT of the prompt and enforced in code (assume the prompt is public)?",
     "(reference only)"),
    ("LLM08", "Vector and Embedding Weaknesses",
     "Is the vector store tenant-isolated with access controls, and do you re-index on embedder change?",
     "(reference only — see data pillar)"),
    ("LLM09", "Misinformation",
     "Are high-stakes outputs grounded with citations, consistency-checked, and human-reviewed?",
     "(reference only — see quality pillar)"),
    ("LLM10", "Unbounded Consumption",
     "Are there per-user/tenant rate limits, token/cost budgets, timeouts, and input-size caps?",
     "(reference only — see cost/scalability pillars)"),
]


def print_checklist() -> None:
    print("=" * 78)
    print("OWASP Top 10 for LLM Applications (2025) — self-audit checklist")
    print("Source: https://genai.owasp.org/   |   [ ] = review this control")
    print("=" * 78)
    for code, name, question, topic in CHECKLIST:
        print(f"\n[ ] {code}  {name}")
        print(f"      Q: {question}")
        print(f"      KB: {topic}")
    print("\n" + "-" * 78)
    print(f"{len(CHECKLIST)} controls. Any question you can't answer 'yes' to is a gap to fix.")
    print("Reference/overview topic — the fixes live in the linked sibling KB topics.")


if __name__ == "__main__":
    print_checklist()
