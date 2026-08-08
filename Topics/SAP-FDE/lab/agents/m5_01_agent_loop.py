"""M5.1 - A minimal agent loop from scratch: LLM + tools + loop + seatbelt.

Watch the agent take MULTIPLE steps: it calls a tool, sees the result, decides
the next tool, and only stops when it has the final answer (or hits the step cap).

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_01_agent_loop.py
"""
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from _llm import get_llm


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


TOOLS = {"add": add, "multiply": multiply}
MAX_STEPS = 5  # SEATBELT #1: never loop more than this many times


def run_agent(question: str, max_steps: int = MAX_STEPS) -> str:
    llm = get_llm().bind_tools(list(TOOLS.values()))
    messages = [HumanMessage(question)]

    for step in range(1, max_steps + 1):
        ai = llm.invoke(messages)
        messages.append(ai)

        if not ai.tool_calls:  # no more tools requested -> the agent is done
            print(f"[step {step}] done")
            return ai.content

        for call in ai.tool_calls:  # run each requested tool, feed results back
            result = TOOLS[call["name"]].invoke(call["args"])
            print(f"[step {step}] {call['name']}({call['args']}) = {result}")
            messages.append(ToolMessage(str(result), tool_call_id=call["id"]))

    return "Stopped: hit the max-steps seatbelt."


def main() -> None:
    q = "What is (12 + 8) multiplied by 3? Use the tools, one operation at a time."
    print("Q:", q, "\n")
    print("\nANSWER:", run_agent(q))


if __name__ == "__main__":
    main()
