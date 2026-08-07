"""M1.10 - Tool calling: the model ASKS, your code ACTS.

The model can't touch anything. It emits a structured request (a tool call);
YOUR code decides whether to run it. Independent tool calls can be proposed
together (parallel); dependent ones must be sequenced.

Golden rule: treat every tool call as UNTRUSTED input -> validate + authorize
before executing. The model proposes; your code disposes.

Run:  uv run python concepts/m1_08_tool_calling.py
"""
from _llm import get_llm
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"{city}: 24C, sunny"  # pretend real API


@tool
def get_time(city: str) -> str:
    """Get the current local time for a city."""
    return f"{city}: 14:30"  # pretend real API


MAX_REFUND = 100  # a business guardrail your code enforces


def main() -> None:
    llm = get_llm().bind_tools([get_weather, get_time])

    # Two INDEPENDENT asks -> the model can propose both at once (parallel).
    resp = llm.invoke("What's the weather AND the time in Berlin?")

    print("The model did NOT run anything. It proposed these tool calls:")
    for call in resp.tool_calls:
        print(f"  -> {call['name']}({call['args']})")

    # YOUR code decides to execute (here: just run them; in prod you'd validate).
    print("\nYour code executes them:")
    registry = {"get_weather": get_weather, "get_time": get_time}
    for call in resp.tool_calls:
        result = registry[call["name"]].invoke(call["args"])
        print(f"  {call['name']} -> {result}")

    # The security reflex, made concrete:
    fake_refund = {"amount": 1_000_000}
    ok = fake_refund["amount"] <= MAX_REFUND
    print(f"\nGuardrail demo: refund ${fake_refund['amount']} allowed? {ok}  (validate BEFORE executing)")


if __name__ == "__main__":
    main()
