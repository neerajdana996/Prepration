"""M1.9 - Structured output: get a FORM (JSON), not an essay.

Your code can't parse prose. Define a schema (Pydantic) and the model is
constrained to fill it in -> predictable fields you can act on.
This is 'level 3': the shape is enforced, not merely requested.

Run:  uv run python concepts/m1_07_structured_output.py
"""
from typing import Literal

from _llm import get_llm
from pydantic import BaseModel, Field

TICKET = "I was double charged $79 on my last invoice and I'm furious."


class TicketTriage(BaseModel):
    """Structured triage of a support ticket."""

    category: Literal["billing", "bug", "account", "other"] = Field(description="Best category")
    urgency: Literal["low", "medium", "high"] = Field(description="How urgent")
    sentiment: Literal["happy", "neutral", "angry"] = Field(description="Customer mood")
    summary: str = Field(description="One short sentence")


def main() -> None:
    llm = get_llm()
    structured_llm = llm.with_structured_output(TicketTriage)

    result: TicketTriage = structured_llm.invoke(f"Triage this ticket: {TICKET}")

    print("Parsed object your code can use directly:")
    print("  category :", result.category)
    print("  urgency  :", result.urgency)
    print("  sentiment:", result.sentiment)
    print("  summary  :", result.summary)

    # Because it's typed, downstream routing is trivial and safe:
    route = {"billing": "finance-team", "bug": "eng-team"}.get(result.category, "general-team")
    print(f"\nAuto-route -> {route}")
    print("Lesson: enforce the schema so a bad parse can't misroute money (match strength to blast radius).")


if __name__ == "__main__":
    main()
