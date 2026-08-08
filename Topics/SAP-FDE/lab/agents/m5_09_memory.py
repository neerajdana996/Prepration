"""M5.9 - Long-term memory: recall facts in a FRESH session (no chat history).

MEMORY is an external store (a list here; a vector DB in real life). We write
facts to it, and each turn we RETRIEVE the relevant ones by meaning (embeddings +
cosine = RAG over history) and inject them. Even with zero conversation history,
the agent recalls the user's preference.

Needs GOOGLE_API_KEY. Run:  uv run python agents/m5_09_memory.py
"""
import math

from _llm import get_embeddings, get_llm

MEMORY: list[tuple[str, list[float]]] = []  # long-term store: (fact, embedding)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def remember(fact: str) -> None:
    MEMORY.append((fact, get_embeddings().embed_query(fact)))


def recall(query: str, k: int = 2) -> list[str]:
    if not MEMORY:
        return []
    qv = get_embeddings().embed_query(query)
    ranked = sorted(MEMORY, key=lambda m: cosine(qv, m[1]), reverse=True)
    return [fact for fact, _ in ranked[:k]]


def answer(query: str) -> str:
    facts = recall(query)
    context = "\n".join(f"- {f}" for f in facts) or "(nothing remembered)"
    return _text(get_llm().invoke(
        f"What you remember about the user:\n{context}\n\nUser: {query}\nReply in one sentence."
    ).content)


def main() -> None:
    # --- Session 1: learn facts about the user ---
    remember("The user prefers to be contacted by email, not phone.")
    remember("The user's company is based in the Netherlands.")

    # --- Session 2: a BRAND NEW conversation (no message history at all) ---
    q = "How should you get in touch with me?"
    print("Q:", q)
    print("A:", answer(q), "  <- recalled from long-term memory, not chat history")


if __name__ == "__main__":
    main()
