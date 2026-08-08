"""M5.8 - Testing a nondeterministic agent: assert the TRAJECTORY + outcome over N runs.

The agent returns (final_answer, trajectory) where trajectory = the tool names it
called. We assert the RIGHT tools were used and the answer is correct - across
several runs, reporting a PASS RATE (one green run proves nothing).

Real CI adds: mock external tools (done here - they're fake), temperature 0 (default),
LLM-as-judge for fuzzy answers, and tests that guardrails/HITL fire.

Needs GOOGLE_API_KEY (~3 runs x a few calls). Run:  uv run python agents/m5_08_agent_testing.py
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
SYSTEM = SystemMessage("You must use the tools for every calculation; never compute yourself.")


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def run_agent(question: str, max_steps: int = 6):
    """Return (final_answer, trajectory=list of tool names called)."""
    llm = get_llm().bind_tools(list(TOOLS.values()))  # temperature 0 by default
    messages, trajectory = [SYSTEM, HumanMessage(question)], []
    for _ in range(max_steps):
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            return _text(ai.content), trajectory
        for call in ai.tool_calls:
            trajectory.append(call["name"])
            out = TOOLS[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(str(out), tool_call_id=call["id"]))
    return "(no answer)", trajectory


def test_case(question: str, expect_tools: list[str], expect_in_answer: str, runs: int = 3) -> None:
    passes = 0
    for i in range(1, runs + 1):
        answer, traj = run_agent(question)
        tools_ok = all(t in traj for t in expect_tools)
        answer_ok = expect_in_answer in answer
        ok = tools_ok and answer_ok
        passes += ok
        print(f"  run {i}: tools={traj} tools_ok={tools_ok} answer_ok={answer_ok} -> {'PASS' if ok else 'FAIL'}")
    print(f"  PASS RATE: {passes}/{runs}\n")


def main() -> None:
    print("Scenario: (12 + 8) x 3  -> expect tools [add, multiply], answer contains '60'\n")
    test_case(
        "What is (12 + 8) multiplied by 3? Use the tools.",
        expect_tools=["add", "multiply"],
        expect_in_answer="60",
        runs=3,
    )


if __name__ == "__main__":
    main()
