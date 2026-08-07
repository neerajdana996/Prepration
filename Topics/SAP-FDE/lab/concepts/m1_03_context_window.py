"""M1.3/M1.4 - The context window is a shared desk (input + answer share it).

Diagram idea: system prompt + history + docs + ANSWER all fit on ONE desk.
Cram the desk with input -> no room left for the answer.

This file simulates a chat growing turn by turn and shows the input token
count climbing, plus a sliding-window fix that keeps it bounded.

Run:  uv run python concepts/m1_03_context_window.py
"""
from _llm import get_llm
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

DESK_SIZE = 8000  # pretend our model's window is 8k tokens


def approx_tokens(messages) -> int:
    return round(sum(len(m.content) for m in messages) / 4)


def main() -> None:
    llm = get_llm()

    history = [SystemMessage("You are a terse support bot. One short sentence.")]
    questions = [
        "My invoice didn't arrive.",
        "I checked spam, still nothing.",
        "Can you resend it to a new email?",
        "Also update my billing address.",
    ]

    print(f"Desk size (pretend): {DESK_SIZE} tokens\n")
    for i, q in enumerate(questions, 1):
        history.append(HumanMessage(q))
        answer = llm.invoke(history)
        history.append(AIMessage(answer.content))
        used = approx_tokens(history)
        print(f"Turn {i}: history ~= {used:>4} tokens  | room left for answer ~= {DESK_SIZE - used}")

    print("\n-- Sliding-window fix: keep system prompt + last 2 turns only --")
    trimmed = [history[0]] + history[-4:]
    print(f"Full history ~= {approx_tokens(history)} tokens  ->  trimmed ~= {approx_tokens(trimmed)} tokens")
    print("Lesson: long chats grow the input every turn. Trim (lossy) or summarize (lossy) or cache (lossless).")


if __name__ == "__main__":
    main()
