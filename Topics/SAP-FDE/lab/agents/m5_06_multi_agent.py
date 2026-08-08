"""M5.6 - Multi-agent (clean reference): supervisor routes to 3 focused specialists.

Design lessons baked in:
  - 3 sensible agents (payment folded into billing; shipping/tracking/returns/
    cancellations folded into orders) -> no redundant "agent soup" (M5.4).
  - Route schema (Literal), the AGENTS registry, and dispatch stay IN SYNC.
    A runtime assert catches drift so you can't add an agent the router can't pick.
  - One DRY specialist() function instead of ten near-identical ones.
  - For speed, set GEMINI_MODEL=gemini-2.5-flash-lite in .env.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_06_multi_agent.py
"""
from typing import Literal

from pydantic import BaseModel

from _llm import get_llm

# The registry: what each specialist handles. Add an agent = add ONE line here...
AGENTS = {
    "billing": "invoices, charges, double-billing, refunds, payments, payment methods",
    "tech": "app crashes, errors, uploads, logins, technical problems",
    "orders": "order status, tracking, shipping, cancellations, returns",
}


class Route(BaseModel):
    specialist: Literal["billing", "tech", "orders"]  # ...and keep THIS in sync
    reason: str


# Guard: schema and registry must agree, or new agents are unreachable.
assert set(Route.model_fields["specialist"].annotation.__args__) == set(AGENTS), (
    "Route Literal and AGENTS registry are out of sync!"
)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def supervisor(query: str) -> Route:
    """One decision: which specialist, and why (explainable routing)."""
    catalog = "\n".join(f"- {name}: {desc}" for name, desc in AGENTS.items())
    return get_llm().with_structured_output(Route).invoke(
        f"Pick the best specialist for the query based on their capabilities.\n"
        f"Specialists:\n{catalog}\n\nQuery: {query}"
    )


def specialist(name: str, query: str) -> str:
    """One DRY specialist: a focused prompt built from the registry."""
    return _text(get_llm().invoke(
        f"You are the {name.upper()} specialist ({AGENTS[name]}). "
        f"Answer in one short sentence.\nQuery: {query}"
    ).content)


def run(query: str) -> str:
    route = supervisor(query)
    print(f"[supervisor] -> {route.specialist}  ({route.reason})")
    return specialist(route.specialist, query)


def main() -> None:
    for q in [
        "Why was I charged twice on my last invoice?",  # billing
        "The app crashes when I upload a PDF.",          # tech
        "Where is my package, it hasn't shipped yet?",   # orders
    ]:
        print("Q:", q)
        print("A:", run(q), "\n")


if __name__ == "__main__":
    main()
