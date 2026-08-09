"""M5.11 - LangGraph memory: a checkpointer remembers across turns.

We give the agent a MemorySaver checkpointer and a thread_id. Turn 2 does NOT
resend the name/preference - the checkpointer persists the state for that thread.
Contrast with concepts/m1_05 (raw stateless API where you must resend everything).

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_11_langgraph_memory.py
"""
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from _llm import get_llm


@tool
def current_offers() -> str:
    """List current promotional offers (just so the agent has a tool; not needed here)."""
    return "10% off annual plans this month."


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def main() -> None:
    agent = create_react_agent(get_llm(), [current_offers], checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "user-1"}}  # same thread = same memory

    r1 = agent.invoke({"messages": [("user", "My name is Neeraj and I prefer email over phone.")]}, config)
    print("turn 1:", _text(r1["messages"][-1].content))

    # Turn 2: we do NOT resend the name/preference — the checkpointer holds it.
    r2 = agent.invoke({"messages": [("user", "What's my name, and how should you contact me?")]}, config)
    print("turn 2:", _text(r2["messages"][-1].content))
    print("\n-> It recalled across turns WITHOUT us resending history (checkpointer = durable memory).")


if __name__ == "__main__":
    main()
