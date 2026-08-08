"""M5.7 - Human-in-the-loop: pause for approval before high-impact actions.

Safe reads (lookup) run automatically. High-impact actions (refund) are gated:
the loop STOPS, shows you the proposed action, and waits for your y/n. On deny,
we feed 'DENIED' back as the observation (errors-as-observations again) so the
agent adapts instead of forcing it through.

Needs GOOGLE_API_KEY + an interactive terminal (it calls input()).
Run:  uv run python agents/m5_07_human_in_loop.py
"""
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from _llm import get_llm


@tool
def lookup_invoice(invoice_id: int) -> str:
    """Look up an invoice's status (safe, read-only)."""
    return {101: "paid", 102: "overdue"}.get(invoice_id, "not found")


@tool
def issue_refund(invoice_id: int, amount: float) -> str:
    """Issue a refund for an invoice (HIGH-IMPACT: moves real money)."""
    return f"refunded ${amount} on invoice {invoice_id}"


TOOLS = {"lookup_invoice": lookup_invoice, "issue_refund": issue_refund}
NEEDS_APPROVAL = {"issue_refund"}  # gate by blast radius
MAX_STEPS = 6


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
            name, args = call["name"], call["args"]
            if name in NEEDS_APPROVAL:
                print(f"\n  [APPROVAL NEEDED] agent wants: {name}({args})")
                if input("  approve? [y/N] ").strip().lower() != "y":
                    result = "DENIED by human — action not performed."
                    print("  -> denied\n")
                    messages.append(ToolMessage(result, tool_call_id=call["id"]))
                    continue
            result = TOOLS[name].invoke(args)
            print(f"[step {step}] {name}({args}) -> {result}")
            messages.append(ToolMessage(str(result), tool_call_id=call["id"]))
    return "Stopped: hit the max-steps seatbelt."


def main() -> None:
    q = "Invoice 102 is overdue and the customer is upset. Look it up, then issue a $50 refund."
    print("Q:", q)
    print("\nANSWER:", run(q))


if __name__ == "__main__":
    main()
