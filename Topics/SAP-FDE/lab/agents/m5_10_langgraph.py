"""M5.10 - LangGraph: the framework version of the agent you hand-built.

create_react_agent builds the SAME graph as your m5_01 loop:
    agent node  <-- (tool calls? loop back)  -->  tools node
    conditional edge: no tool calls -> finish
State = the messages list (formalized). For free, LangGraph adds:
  - checkpointer (durable memory + resume)   -> your M5.9 memory
  - interrupt_before (pause for approval)    -> your M5.7 HITL
  - streaming, retries, subgraphs (multi-agent)

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_10_langgraph.py
"""
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from _llm import get_llm


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


# The entire hand-built loop, in one call:
agent = create_react_agent(get_llm(), [add, multiply])


def main() -> None:
    q = "What is (12 + 8) multiplied by 3? Use the tools."
    result = agent.invoke({"messages": [("user", q)]})
    for m in result["messages"]:
        m.pretty_print()


if __name__ == "__main__":
    main()
