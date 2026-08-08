"""M5.2 - ReAct: the same loop as step 1, but the agent narrates its THOUGHT.

We add a system instruction telling the model to state a one-line reason before
each tool call, and we PRINT that reasoning. Now you can see WHY it acts, which
is how you debug an agent that goes off the rails.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_02_react.py
"""
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
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
MAX_STEPS = 5

SYSTEM = SystemMessage(
    "You are an agent that is TERRIBLE at mental math and must NEVER compute yourself. "
    "You MUST use the add and multiply tools for every calculation. Before each tool "
    "call, give a one-sentence Thought explaining the next step. One tool at a time."
)


def _text(content) -> str:
    """Gemini 3.x returns content as a LIST of typed blocks; flatten to plain text."""
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def run_agent(question: str, max_steps: int = MAX_STEPS) -> str:
    llm = get_llm().bind_tools(list(TOOLS.values()))
    messages = [SYSTEM, HumanMessage(question)]

    for step in range(1, max_steps + 1):
        ai = llm.invoke(messages)
        messages.append(ai)

        thought = _text(ai.content)
        if thought:  # the visible reasoning (the "Reason" in ReAct)
            print(f"[step {step}] Thought: {thought}")

        if not ai.tool_calls:
            return thought

        for call in ai.tool_calls:
            result = TOOLS[call["name"]].invoke(call["args"])
            print(f"[step {step}] Action: {call['name']}({call['args']})  ->  Observation: {result}")
            messages.append(ToolMessage(str(result), tool_call_id=call["id"]))

    return "Stopped: hit the max-steps seatbelt."


def main() -> None:
    q = "What is (12 + 8) multiplied by 3? Reason step by step and use the tools."
    print("Q:", q, "\n")
    print("\nANSWER:", run_agent(q))


if __name__ == "__main__":
    main()
