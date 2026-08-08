"""M3.5/3.6 - Cosine similarity + a tiny TF-IDF search engine (no libraries).

Reuses your TF-IDF functions from m3_02_tfidf.py. The query becomes a vector too,
then we rank docs by the cosine of (query vector, doc vector).

Run:  python3 concepts/m3_03_search.py
"""
import math

from m3_02_tfidf import DOCS, N, document_frequencies, tfidf


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:

    """YOUR TURN.  cosine = (a . b) / (|a| * |b|)

    a, b are {word: weight} dicts (missing word = weight 0).
      dot   = sum of a[w]*b[w] over words in BOTH
      |a|   = sqrt(sum of every a-weight squared)
    Return 0.0 if either vector has zero length (avoid divide-by-zero).

    Example: cosine({"invoice":1.0}, {"invoice":0.5, "the":0.0}) -> 1.0
             (same direction; the extra 0.0 dimension doesn't matter)

    a={"invoice": 1.0, "the": 0.0}
    b={"invoice": 0.5, "the": 0.0}
    dot = 1.0*0.5 + 0.0*0.0 = 0.5
    |a| = sqrt(1.0*1.0 + 0.0*0.0) = 1.0 = sqrt(a[w]*a[w] for w in a)
    |b| = sqrt(0.5*0.5 + 0.0*0.0) = 0.5 = sqrt(b[w]*b[w] for w in b)
    cosine = 0.5 / (1.0 * 0.5) = 1.0
    """
    dot = sum(a[w] * b[w] for w in a if w in b)  # only shared words contribute
    a_len = math.sqrt(sum(v * v for v in a.values()))
    b_len = math.sqrt(sum(v * v for v in b.values()))
    if a_len == 0 or b_len == 0:  # empty / all-zero vector -> no similarity
        return 0.0
    return dot / (a_len * b_len)


def search(query: str, docs: dict[str, str], df: dict[str, int], n: int):
    """Rank every doc by cosine similarity to the query."""
    q_vec = tfidf(query, df, n)
    scored = {
        name: cosine_similarity(q_vec, tfidf(text, df, n)) for name, text in docs.items()
    }
    return sorted(scored.items(), key=lambda kv: kv[1], reverse=True)


def main() -> None:
    df = document_frequencies(DOCS)
    query = "overdue invoice"
    print(f"query: {query!r}\n")
    for name, score in search(query, DOCS, df, N):
        print(f"  {name}: {score:.3f}   | {DOCS[name]!r}")


if __name__ == "__main__":
    main()
