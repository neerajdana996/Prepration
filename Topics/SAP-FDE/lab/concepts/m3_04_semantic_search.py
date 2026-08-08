"""M3.5 (applied) - Real semantic search = a real embedding model + YOUR cosine.

The payoff: TF-IDF scored "unpaid bill" vs "overdue invoice" as 0 (no shared
words). A learned embedding model puts them near each other in meaning space,
so the SAME cosine_similarity you wrote by hand now finds the right doc.

Needs GOOGLE_API_KEY in .env (embeddings hit the network).
Run:  uv run python concepts/m3_04_semantic_search.py
"""
import math
import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

DOCS = {
    "d1": "please pay the invoice",
    "d2": "the invoice is overdue",
    "d3": "please reset the password",
}


def cosine(a: list[float], b: list[float]) -> float:
    """Identical math to the cosine you wrote — just on dense number lists."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def main() -> None:
    embed = GoogleGenerativeAIEmbeddings(
        model=os.getenv("EMBED_MODEL", "models/text-embedding-004")
    )
    doc_vecs = {name: embed.embed_query(text) for name, text in DOCS.items()}

    query = "unpaid bill"  # NONE of these words appear in any doc
    qv = embed.embed_query(query)

    print(f"query: {query!r}  (zero shared words with the docs)\n")
    ranked = sorted(DOCS, key=lambda n: cosine(qv, doc_vecs[n]), reverse=True)
    for name in ranked:
        print(f"  {name}: {cosine(qv, doc_vecs[name]):.3f}   | {DOCS[name]!r}")

    print(f"\neach embedding is {len(qv)} numbers.")
    print("TF-IDF gave d2 a 0.0 here. Meaning-vectors find it. Same cosine, richer vector.")


if __name__ == "__main__":
    main()
