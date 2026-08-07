"""M1.8 - Few-shot: teach by showing, not retraining.

Zero-shot = just ask (answer can be messy/verbose).
Few-shot  = show 2 labelled examples first -> model copies the clean pattern.

Run:  uv run python concepts/m1_06_few_shot.py
"""
from _llm import get_llm

TICKET = "The app crashed again and I lost my work."


def main() -> None:
    llm = get_llm()

    # Zero-shot: no examples, format is unpredictable.
    zero = llm.invoke(f"What is the sentiment of this message? {TICKET}")
    print("Zero-shot (messy):")
    print("  ", zero.content.strip().replace("\n", " "))

    # Few-shot: two examples teach the exact output we want.
    few_shot_prompt = (
        "Classify the sentiment as exactly one word: happy, neutral, or angry.\n"
        "'Thanks, that fixed it!' -> happy\n"
        "'The invoice is attached.' -> neutral\n"
        "'Late again, this is unacceptable.' -> angry\n"
        f"'{TICKET}' ->"
    )
    few = llm.invoke(few_shot_prompt)
    print("\nFew-shot (clean, one word):")
    print("  ", few.content.strip())

    print("\nLesson: examples in the prompt steer format/behaviour with zero training.")
    print("Cost note: those examples ride along every call -> prompt-caching keeps them cheap.")


if __name__ == "__main__":
    main()
