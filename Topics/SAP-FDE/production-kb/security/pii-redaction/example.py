"""VULNERABLE: raw PII sent straight into the prompt AND into the logs.

A support-ticket summarizer drops the raw customer record into the prompt and
prints it to the "log". The email, phone, and card-like number leave your
perimeter (into the model provider) and are also written to your logs, where
they are now regulated personal data sitting in plaintext. No attacker needed —
the app leaks by design.

Run (needs GOOGLE_API_KEY; run from the lab so .env + venv are picked up):
    cd Topics/SAP-FDE/lab && uv run python ../production-kb/security/pii-redaction/example.py
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# A retrieved support ticket containing raw customer PII (real values).
CUSTOMER_TICKET = (
    "Customer Jane Doe (email jane.doe@example.com, phone +1-415-555-0142) "
    "reports she was double-charged on card 4111 1111 1111 1111. "
    "She wants a refund to the same card."
)

SYSTEM = "You are a support assistant. Summarize the ticket in ONE sentence and state the next action."


def llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),  # alias!
        temperature=0,
    )


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def main() -> None:
    # NAIVE: raw PII pasted directly into the prompt — it now leaves your perimeter.
    prompt = f"{SYSTEM}\n\nTicket:\n{CUSTOMER_TICKET}"

    # LEAK #1: the raw prompt (with email, phone, card) is written to the log.
    print("LOG >> outbound prompt:\n", prompt)

    out = _text(llm().invoke(prompt).content)

    # LEAK #2: the model may echo the PII back, and we log the response too.
    print("\nLOG >> model response:\n", out)
    print(
        "\n^ Raw email/phone/card were (1) sent to the model provider and (2) written to logs. "
        "Both are now leaks — prompt instructions can't undo that."
    )


if __name__ == "__main__":
    main()
