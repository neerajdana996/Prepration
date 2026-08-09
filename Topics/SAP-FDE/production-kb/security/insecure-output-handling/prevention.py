"""DEFENDED: the same calculator, but the model's output is never executed.

Instead of eval(), we treat the output as untrusted data and parse it safely:
  1. ast.literal_eval  — parses ONLY Python literals; it cannot call functions,
     import modules, or run code, so a code-bearing output raises instead of running.
  2. AST allow-list    — we then walk the tree and permit ONLY numbers and a small set
     of arithmetic operators. Anything else (names, calls, attribute access) is rejected.
The unsafe path is closed: a malicious __import__('os').system(...) output is refused,
not run. (In prod you'd also log the rejection and cap the number of retries.)

Run (needs GOOGLE_API_KEY; run from the lab):
    cd Topics/SAP-FDE/lab && uv run python ../production-kb/security/insecure-output-handling/prevention.py
"""
import ast
import operator
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

USER_QUESTION = "What is 21 * 2?"
SYSTEM = "You are a calculator. Reply with ONLY a Python arithmetic expression, nothing else."

# Allow-list: only these AST node types and operators are permitted. No names, no calls.
_ALLOWED_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub,
                   ast.Mult: operator.mul, ast.Div: operator.truediv,
                   ast.Mod: operator.mod, ast.Pow: operator.pow}
_ALLOWED_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def safe_eval(expr: str) -> float:
    """Evaluate ONLY arithmetic over number literals. Rejects anything else."""
    tree = ast.parse(expr, mode="eval")  # raises SyntaxError on non-expressions

    def _ev(node):
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](_ev(node.left), _ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
            return _ALLOWED_UNARYOPS[type(node.op)](_ev(node.operand))
        # Names, Calls, Attributes, imports, etc. all land here -> refused.
        raise ValueError(f"disallowed expression element: {type(node).__name__}")

    return _ev(tree)


def main() -> None:
    prompt = f"{SYSTEM}\n\nQuestion: {USER_QUESTION}"
    raw = _text(llm().invoke(prompt).content).strip().strip("`")
    print("MODEL OUTPUT:", repr(raw))

    try:
        result = safe_eval(raw)
        print("SAFE RESULT:", result)
    except (ValueError, SyntaxError, TypeError) as e:
        print("REJECTED (not a plain arithmetic expression):", e)

    # Prove the unsafe path is closed: a code-bearing "output" is refused, never run.
    malicious = "__import__('os').system('echo pwned')"
    try:
        safe_eval(malicious)
        print("!! malicious output was accepted — should not happen")
    except (ValueError, SyntaxError, TypeError) as e:
        print(f"\nBLOCKED malicious output {malicious!r}: {e}")
        print("^ eval() would have executed it; safe_eval refuses to.")


if __name__ == "__main__":
    main()
