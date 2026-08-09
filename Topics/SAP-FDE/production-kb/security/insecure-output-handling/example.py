"""VULNERABLE: insecure output handling — eval()ing raw LLM output.

A "calculator" asks the model for an arithmetic expression, then feeds the model's
RAW output straight into eval(). eval() executes arbitrary Python, so the model's
output is really untrusted CODE. Here the expression is benign, but a prompt (or an
indirect injection in retrieved context) that steers the model into emitting
    __import__('os').system('rm -rf ~')
would run it. The sink (eval) sets the blast radius, not the model.

Run (needs GOOGLE_API_KEY; run from the lab so .env + venv are picked up):
    cd Topics/SAP-FDE/lab && uv run python ../production-kb/security/insecure-output-handling/example.py
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# The user's math question. In a real app this is attacker-controllable, and so is any
# retrieved context — either can steer the model's output into something other than a number.
USER_QUESTION = "What is 21 * 2?"

SYSTEM = "You are a calculator. Reply with ONLY a Python arithmetic expression, nothing else."


def llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),  # alias!
        temperature=0,
    )


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def main() -> None:
    prompt = f"{SYSTEM}\n\nQuestion: {USER_QUESTION}"
    raw = _text(llm().invoke(prompt).content).strip().strip("`")
    print("MODEL OUTPUT:", repr(raw))

    # DANGEROUS: eval() runs whatever the model returned. If the output were
    #   __import__('os').system('rm -rf ~')
    # this line would execute it. We treat model output as trusted code — the bug.
    result = eval(raw)  # noqa: S307 - intentional vulnerability for the demo
    print("EVAL RESULT:", result)
    print("\n^ It worked on a benign expression — but eval() would ALSO run arbitrary code.")
    print("  The output is untrusted input; the sink (eval) makes it RCE.")


if __name__ == "__main__":
    main()
