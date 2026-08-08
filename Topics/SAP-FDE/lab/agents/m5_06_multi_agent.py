"""M5.6 - Multi-agent: a supervisor routes each query to a specialist agent.

Supervisor = 1 LLM call that classifies the query -> which specialist.
Each specialist = its own LLM call with a FOCUSED prompt (and, in real life, its
own small toolset). Total = 2 calls per query. Focused beats do-everything.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_06_multi_agent.py
"""
from typing import Literal

from pydantic import BaseModel

from _llm import get_llm


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


class Route(BaseModel):
    specialist: Literal["billing", "tech"]


def supervisor(query: str) -> str:
    """One focused decision: which specialist should handle this?"""
    r = get_llm().with_structured_output(Route).invoke(
        f"Route this customer query to the right specialist.\nQuery: {query}"
    )
    return r.specialist


def billing_agent(query: str) -> str:
    return _text(get_llm().invoke(
        f"You are a BILLING specialist. Answer in one short sentence.\nQuery: {query}"
    ).content)


def tech_agent(query: str) -> str:
    return _text(get_llm().invoke(
        f"You are a TECHNICAL SUPPORT specialist. Answer in one short sentence.\nQuery: {query}"
    ).content)


SPECIALISTS = {"billing": billing_agent, "tech": tech_agent}


def run(query: str) -> str:
    who = supervisor(query)
    print(f"[supervisor] routed to: {who}")
    return SPECIALISTS[who](query)


def main() -> None:
    for q in [
        "Why was I charged twice on my last invoice?",
        "The app crashes every time I upload a PDF.",
    ]:
        print("Q:", q)
        print("A:", run(q), "\n")


if __name__ == "__main__":
    main()
