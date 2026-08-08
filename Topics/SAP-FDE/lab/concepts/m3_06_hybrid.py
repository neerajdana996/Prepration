"""M3.7 - Hybrid search: BM25 (keywords) + embeddings (meaning), fused.

Neither ranker is best alone:
  - BM25 nails exact terms ("invoice", an error code, a product SKU)
  - embeddings nail meaning ("unpaid bill" ~ "overdue invoice")
Hybrid runs BOTH, then fuses their RANKED LISTS with Reciprocal Rank Fusion
(RRF): a doc's fused score = sum over rankers of 1 / (k + rank). Rank position
matters, not raw scores - so you never have to normalize two different scales.

Needs GOOGLE_API_KEY (for the embedding half).
Run:  uv run python concepts/m3_06_hybrid.py
"""
import os

from dotenv import load_dotenv
from _llm import get_embeddings
from m3_04_semantic_search import cosine
from m3_05_bm25 import DOCS, rank as bm25_rank

load_dotenv()


def semantic_rank(query: str, docs=DOCS):
    embed = get_embeddings()
    doc_vecs = {name: embed.embed_query(text) for name, text in docs.items()}
    qv = embed.embed_query(query)
    scored = {name: cosine(qv, doc_vecs[name]) for name in docs}
    return sorted(scored.items(), key=lambda kv: kv[1], reverse=True)


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fuse ranked lists of doc names (best-first) by Reciprocal Rank Fusion."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for position, name in enumerate(ranking):
            fused[name] = fused.get(name, 0.0) + 1 / (k + position + 1)
    return sorted(fused.items(), key=lambda kv: kv[1], reverse=True)


def main() -> None:
    query = "unpaid bill"  # meaning-heavy: BM25 alone would miss it
    lexical = [name for name, _ in bm25_rank(query)]
    semantic = [name for name, _ in semantic_rank(query)]

    print(f"query: {query!r}\n")
    print("BM25 (keywords) order  :", lexical)
    print("Embeddings (meaning)   :", semantic)
    print("\nHybrid (RRF fused):")
    for name, score in rrf([lexical, semantic]):
        print(f"  {name}: {score:.4f}   | {DOCS[name]!r}")


if __name__ == "__main__":
    main()
