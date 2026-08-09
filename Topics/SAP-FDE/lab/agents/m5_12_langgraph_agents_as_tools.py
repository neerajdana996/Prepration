"""M5.12 - LangGraph multi-agent: specialist ReAct agents exposed as TOOLS to a supervisor.

Each specialist is its own create_react_agent (own prompt + own tools). We wrap
each as a @tool; the supervisor is itself a ReAct agent that 'calls' a specialist.
This is the agents-as-tools pattern (M5.5) on LangGraph.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_12_langgraph_agents_as_tools.py
"""
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from _llm import get_llm


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


@tool
def lookup_invoice(invoice_id: int) -> str:
    """Look up an invoice's status."""
    return {101: "paid", 102: "overdue"}.get(invoice_id, "not found")


@tool
def run_diagnostic(issue: str) -> str:
    """Run a basic diagnostic for a technical issue."""
    return f"diagnostic for '{issue}': no known outage; suggest reinstalling the app."


# Two specialist agents, each with a focused prompt + its own tools.
billing = create_react_agent(get_llm(), [lookup_invoice], prompt="You are a billing specialist. Be concise.")
tech = create_react_agent(get_llm(), [run_diagnostic], prompt="You are a technical support specialist. Be concise.")


@tool
def ask_billing(question: str) -> str:
    """Delegate billing / invoice / refund / payment questions to the billing specialist."""
    return _text(billing.invoke({"messages": [("user", question)]})["messages"][-1].content)


@tool
def ask_tech(question: str) -> str:
    """Delegate app / crash / error / technical questions to the tech specialist."""
    return _text(tech.invoke({"messages": [("user", question)]})["messages"][-1].content)


def main() -> None:
    supervisor = create_react_agent(
        get_llm(), [ask_billing, ask_tech],
        prompt="You are a supervisor. Route each query to exactly one specialist tool, then relay their answer.",
    )
    for q in ["What's the status of invoice 102?", "The app crashes when I upload a PDF."]:
        r = supervisor.invoke({"messages": [("user", q)]})
        print("Q:", q)
        print("A:", _text(r["messages"][-1].content), "\n")


if __name__ == "__main__":
    main()
