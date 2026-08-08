"""M6.4 - Calibrate the judge: measure judge-vs-human agreement.

You can't just trust an LLM judge. Hand-label a few cases, run the judge on
them, and measure how often it agrees with you. High agreement -> trust it.
Low -> fix the rubric. This is 'evaluating the evaluator'.

Needs GOOGLE_API_KEY. Makes ~5 calls. Run:
    uv run python concepts/m6_03_judge_calibration.py
"""
from typing import Literal

from pydantic import BaseModel, Field

from _llm import get_llm

# Each case has a HUMAN label (the ground truth you assigned by hand).
CASES = [
    {"ctx": "Invoices are due within 30 days.", "q": "How long to pay?",
     "a": "You have 30 days.", "human": "yes"},
    {"ctx": "Invoices are due within 30 days.", "q": "How long to pay?",
     "a": "30 days, and call support for an extension.", "human": "no"},   # unsupported add
    {"ctx": "The late fee is 2 percent.", "q": "What is the late fee?",
     "a": "The late fee is 5 percent.", "human": "no"},                    # contradiction
    {"ctx": "Refunds take 7 business days.", "q": "How long for a refund?",
     "a": "About a week.", "human": "yes"},                               # borderline paraphrase
    {"ctx": "Support is available Monday to Friday.", "q": "Is there weekend support?",
     "a": "No, support is Monday to Friday only.", "human": "yes"},        # borderline inference
]

JUDGE_PROMPT = """You are a strict grader. Is the ANSWER fully supported by the CONTEXT?
Mark "no" if it adds or contradicts any fact not in the context.
Context: {ctx}
Question: {q}
Answer: {a}"""


class Verdict(BaseModel):
    faithful: Literal["yes", "no"] = Field(description="supported by context?")


def judge(case: dict) -> str:
    llm = get_llm().with_structured_output(Verdict)
    v = llm.invoke(JUDGE_PROMPT.format(**case))
    return v.faithful


def main() -> None:
    agree = 0
    for c in CASES:
        verdict = judge(c)
        match = verdict == c["human"]
        agree += match
        flag = "ok " if match else "DIFF"
        print(f"[{flag}] human={c['human']:3} judge={verdict:3} | {c['a']}")
    pct = agree / len(CASES) * 100
    print(f"\nagreement = {agree}/{len(CASES)} = {pct:.0f}%")
    print("Disagreements show where to tighten the rubric (usually the borderline cases).")


if __name__ == "__main__":
    main()
