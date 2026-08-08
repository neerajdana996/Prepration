"""M5.3 - Robust tool calls: return errors AS observations so the agent self-corrects.

The tool raises on a bad id. Instead of crashing, we catch it and feed the error
message back as the observation. Watch the agent READ the error and recover
gracefully instead of dying.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_03_robust_agent.py
"""
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from _llm import get_llm

INVOICES = {101: "paid", 102: "overdue"}


@tool
def lookup_invoice(invoice_id: int) -> str:
    """Return the status of an invoice by its numeric id."""
    if invoice_id not in INVOICES:
        raise ValueError(f"invoice {invoice_id} not found. Valid ids: {list(INVOICES)}")
    return INVOICES[invoice_id]


TOOLS = {"lookup_invoice": lookup_invoice}
MAX_STEPS = 5


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def run(question: str, max_steps: int = MAX_STEPS) -> str:
    llm = get_llm().bind_tools(list(TOOLS.values()))
    messages = [HumanMessage(question)]
    for step in range(1, max_steps + 1):
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            return _text(ai.content)
        for call in ai.tool_calls:
            try:
                result = TOOLS[call["name"]].invoke(call["args"])
            except Exception as e:                       # THE STAR PATTERN:
                result = f"ERROR: {e}"                    # feed the error back, don't crash
            print(f"[step {step}] {call['name']}({call['args']}) -> {result}")
            messages.append(ToolMessage(str(result), tool_call_id=call["id"]))
    return "Stopped: hit the max-steps seatbelt."


def main() -> None:
    q = "What is the status of invoice 999?"  # 999 does NOT exist
    print("Q:", q, "\n")
    print("ANSWER:", run(q))


if __name__ == "__main__":
    main()
