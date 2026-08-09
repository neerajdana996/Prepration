"""DEFENDED: the same ticket, but PII is redacted BEFORE the model and BEFORE logs.

Layers applied:
  1. Detect       — regex for email / phone / credit-card-like digit runs.
     (In prod, add an NER model to catch names/addresses regex misses.)
  2. Redact first — mask PII in ONE place, then use that redacted text everywhere:
     the model call AND every print/log read from `safe`, never the raw ticket.
  3. Reversible?  — here we MASK (irreversible, out of GDPR scope). For a reversible
     flow you'd swap masks for stable tokens (<EMAIL_1>...) and keep the token->value
     map inside your network to rehydrate real values in the final answer.
(Redaction is not the whole story — pair it with role-scoped retrieval so a user
only pulls data they're allowed to, and keep EU data in-region.)

Run (needs GOOGLE_API_KEY; run from the lab):
    cd Topics/SAP-FDE/lab && uv run python ../production-kb/security/pii-redaction/prevention.py
"""
import os
import re

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

CUSTOMER_TICKET = (
    "Customer Jane Doe (email jane.doe@example.com, phone +1-415-555-0142) "
    "reports she was double-charged on card 4111 1111 1111 1111. "
    "She wants a refund to the same card."
)

SYSTEM = "You are a support assistant. Summarize the ticket in ONE sentence and state the next action."

# Layer 1: deterministic detectors. Order matters — mask cards/phones (long digit
# runs) before anything else so their digits aren't half-consumed by another rule.
_PII_PATTERNS = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    # 13-16 digit card-like runs allowing spaces/dashes as separators.
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
    # Phone: optional +, then 7+ digits with common separators.
    ("PHONE", re.compile(r"\+?\d[\d\s().-]{6,}\d")),
]


def redact(text: str) -> str:
    """Layer 2: mask every detected entity. Fails safe — masked data can't leak downstream."""
    for label, pattern in _PII_PATTERNS:
        text = pattern.sub(f"[REDACTED_{label}]", text)
    return text


def llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def main() -> None:
    # Redact ONCE, up front. Everything downstream uses `safe`, never the raw ticket.
    safe = redact(CUSTOMER_TICKET)
    prompt = f"{SYSTEM}\n\nTicket:\n{safe}"

    # Safe to log: no raw email/phone/card ever reaches the log.
    print("LOG >> outbound prompt (redacted):\n", prompt)

    # The model still does its job — the ticket is fully understandable without the PII.
    out = redact(_text(llm().invoke(prompt).content))  # belt-and-suspenders on the output too

    print("\nLOG >> model response (redacted):\n", out)

    # Prove no raw PII slipped into anything we logged.
    combined = prompt + out
    leaked = [v for v in ("jane.doe@example.com", "555-0142", "4111") if v in combined]
    print("\nRaw PII found in logged/model text:", leaked or "NONE")
    print("^ Redacted before the model AND before logs; the model works on masked text.")


if __name__ == "__main__":
    main()
