"""M1.7 - Roles + statelessness: the model has amnesia.

There is no conversation living on the server. Every turn YOU resend the whole
transcript (system / user / assistant). Prove it: a fresh call with no history
can't remember your name; the same call WITH history can.

Run:  uv run python concepts/m1_05_messages_memory.py
"""
from _llm import get_llm
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def main() -> None:
    llm = get_llm()

    # 1) Amnesia: two INDEPENDENT calls. The model keeps nothing between them.
    llm.invoke("My name is Neeraj.")
    forgetful = llm.invoke("What is my name?")
    print("No history resent -> :", forgetful.content.strip())

    # 2) Give it memory by RESENDING the transcript ourselves.
    transcript = [
        SystemMessage("You are a friendly assistant."),
        HumanMessage("My name is Neeraj."),
        AIMessage("Nice to meet you, Neeraj!"),
        HumanMessage("What is my name?"),
    ]
    remembered = llm.invoke(transcript)
    print("Transcript resent  -> :", remembered.content.strip())

    print("\nLesson: 'memory' is just you re-stapling the history to every request.")
    print("Long chats -> resend grows -> cost grows. Fix: summarize / sliding-window / prompt-caching.")


if __name__ == "__main__":
    main()
