"""M4.3 - Parent-child retrieval: index SMALL children, return the BIG parent.

Small children make sharp embeddings (precise match); the parent gives the LLM
full context. Query matches a child, we hand back its whole parent section.

Needs GOOGLE_API_KEY. Run:  uv run python concepts/m4_03_parent_child.py
"""
from _llm import get_embeddings
from m3_04_semantic_search import cosine

# Parent sections (delivered to the LLM in full).
PARENTS = {
    "p1": "Payment terms: invoices are due in 30 days. After that, a 2 percent "
          "late fee applies monthly on the outstanding balance.",
    "p2": "Shipping: orders ship within 2 business days. Tracking is emailed once dispatched.",
}


def make_children() -> list[tuple[str, str, list[float]]]:
    """Split each parent into sentences (children); embed each child."""
    embed = get_embeddings()
    children = []
    for pid, text in PARENTS.items():
        for sentence in [s.strip() for s in text.split(". ") if s.strip()]:
            children.append((pid, sentence, embed.embed_query(sentence)))
    return children


def main() -> None:
    children = make_children()
    query = "what is the late fee?"
    qv = get_embeddings().embed_query(query)

    # Match on the small child...
    pid, child, _ = max(children, key=lambda c: cosine(qv, c[2]))
    print(f"query: {query!r}\n")
    print(f"best CHILD (precise match): {child!r}")
    print(f"-> return its PARENT (full context): {PARENTS[pid]!r}")
    print("\nMatched on the sharp small chunk, answered from the rich parent section.")


if __name__ == "__main__":
    main()
