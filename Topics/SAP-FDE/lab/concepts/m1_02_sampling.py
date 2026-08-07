"""M1.2 - Sampling: temperature is the creativity knob.

Diagram idea: low temp SHARPENS the odds (almost always the top guess);
high temp FLATTENS them (lower guesses get a real chance).

You will SEE it: temperature 0 repeats the same answer; temperature 1 varies.

Run:  uv run python concepts/m1_02_sampling.py
"""
from _llm import get_llm

PROMPT = "Give a name for a coffee shop. Reply with just the name, nothing else."


def run_three_times(temperature: float) -> list[str]:
    llm = get_llm(temperature=temperature)
    return [llm.invoke(PROMPT).content.strip() for _ in range(3)]


def main() -> None:
    print("Knob HARD-LEFT (temperature = 0.0)  -> predictable:")
    for name in run_three_times(0.0):
        print(f"   {name}")

    print("\nKnob RIGHT (temperature = 1.0)      -> creative / varied:")
    for name in run_three_times(1.0):
        print(f"   {name}")

    print("\nLesson: extract an invoice number -> temp 0. Brainstorm copy -> temp high.")


if __name__ == "__main__":
    main()
