"""M6.3 - LLM-as-judge: score faithfulness (does the answer stick to the context?).

Two candidate answers to the same question+context: one grounded, one that invents
a fact. A judge LLM (with a strict rubric + structured output) should PASS the first
and FLAG the second.

Needs GOOGLE_API_KEY. Run:  uv run python concepts/m6_02_llm_judge.py
"""
from typing import Literal

from pydantic import BaseModel, Field

from _llm import get_llm

QUESTION = "How long do I have to pay an invoice?"
CONTEXT = "Invoices are due within 30 days of the issue date."

ANSWERS = {
    "grounded": "You have 30 days from the issue date to pay.",
    "hallucinated": "You have 30 days, and you can call 1-800-555-0199 to request an extension.",
}


class Verdict(BaseModel):
    faithful: Literal["yes", "no"] = Field(
        description="yes only if EVERY claim is supported by the context"
    )
    reason: str = Field(description="one short sentence")


# The rubric is the judge. Note the strict rule: any unsupported fact -> "no".
JUDGE_PROMPT = """You are a strict grader for a support assistant.
Decide whether the ANSWER is fully supported by the CONTEXT.
Rule: if the answer adds ANY fact not present in the context, mark it "no".

Context: {context}
Question: {question}
Answer: {answer}"""


def judge(answer: str) -> Verdict:
    llm = get_llm().with_structured_output(Verdict)
    return llm.invoke(
        JUDGE_PROMPT.format(context=CONTEXT, question=QUESTION, answer=answer)
    )


def main() -> None:
    for label, ans in ANSWERS.items():
        v = judge(ans)
        print(f"[{label:12}] faithful={v.faithful:3} — {v.reason}")


if __name__ == "__main__":
    main()
