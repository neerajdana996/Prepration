"""M5.2b - Classic (text-based) ReAct: the Thought is EXPLICIT before each Action.

Native tool-calling (m5_02) calls tools silently. Classic ReAct instead asks the
model to WRITE Thought / Action / Action Input as text; we parse it, run the tool,
and feed back an Observation. That's how you literally see the reasoning per step.

Trade-off: explicit + debuggable, but YOU parse strings (more fragile). Production
usually uses native tool-calling; ReAct-text is the classic teaching form.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_02b_react_text.py
"""
import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from _llm import get_llm

TOOLS = {"add": lambda a, b: a + b, "multiply": lambda a, b: a * b}

SYSTEM = SystemMessage(
    "Solve the problem step by step using tools. Reply in EXACTLY this format, nothing else:\n"
    "Thought: <one sentence>\n"
    "Action: <add | multiply | finish>\n"
    'Action Input: <JSON args like {"a": 1, "b": 2}, or the final number if Action is finish>\n'
    "Then STOP. I will reply 'Observation: <result>'. One action per turn."
)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def parse(text: str):
    thought = action = inp = ""
    for line in text.splitlines():
        s = line.strip()
        low = s.lower()
        if low.startswith("thought:"):
            thought = s.split(":", 1)[1].strip()
        elif low.startswith("action input:"):
            inp = s.split(":", 1)[1].strip()
        elif low.startswith("action:"):
            action = s.split(":", 1)[1].strip()
    return thought, action, inp


def run(question: str, max_steps: int = 6) -> str:
    llm = get_llm()
    messages = [SYSTEM, HumanMessage(question)]
    for step in range(1, max_steps + 1):
        text = _text(llm.invoke(messages).content)
        thought, action, inp = parse(text)
        print(f"[step {step}] Thought: {thought}")
        print(f"[step {step}] Action: {action}   Input: {inp}")
        if action == "finish":
            return inp
        result = TOOLS[action](**json.loads(inp))
        print(f"[step {step}] Observation: {result}\n")
        messages.append(AIMessage(text))
        messages.append(HumanMessage(f"Observation: {result}"))
    return "Stopped: hit max-steps seatbelt."


def main() -> None:
    q = "What is (12 + 8) multiplied by 3?"
    print("Q:", q, "\n")
    print("ANSWER:", run(q))


if __name__ == "__main__":
    main()
