"""M3.6 - BM25 from scratch: the better TF-IDF (pure Python, no network).

Two upgrades over TF-IDF:
  1) TF SATURATION - the 10th mention of a word adds far less than the 1st
     (controlled by k1). Stops keyword spam from winning.
  2) SMART LENGTH NORM - fairly compares long vs short docs (controlled by b).

Formula per query term present in the doc:
     idf * ( f*(k1+1) ) / ( f + k1*(1 - b + b*dl/avgdl) )
  f = raw count of the term in the doc, dl = doc length, avgdl = average length.

Run:  python3 concepts/m3_05_bm25.py
"""
import math
from collections import Counter

DOCS = {
    "d1": "please pay the invoice",
    "d2": "the invoice is overdue",
    "d3": "please reset the password",
}
K1 = 1.5   # TF saturation knob (higher = counts matter more)
B = 0.75   # length-normalization knob (0 = ignore length, 1 = full)


def build_stats(docs: dict[str, str]):
    tokenized = {name: text.split() for name, text in docs.items()}
    df: dict[str, int] = {}
    for words in tokenized.values():
        for w in set(words):                 # once per doc
            df[w] = df.get(w, 0) + 1
    avgdl = sum(len(w) for w in tokenized.values()) / len(tokenized)
    return tokenized, df, avgdl


def bm25_idf(term: str, df: dict[str, int], n: int) -> float:
    """Smoothed IDF used by BM25 (never negative in practice for our data).
    
    Example:
    df = {'invoice': 2, 'the': 1, 'overdue': 1}
    n = 3
    term = 'invoice'
    df_t = df.get(term, 0) = 2
    return math.log(1 + (3 - 2 + 0.5) / (2 + 0.5)) = math.log(1.5 / 2.5) = -0.2231435513142097
    term = 'the'
    df_t = df.get(term, 0) = 1
    return math.log(1 + (3 - 1 + 0.5) / (1 + 0.5)) = math.log(2.5 / 1.5) = 0.587786664902119
    term = 'overdue'
    df_t = df.get(term, 0) = 1
    return math.log(1 + (3 - 1 + 0.5) / (1 + 0.5)) = math.log(2.5 / 1.5) = 0.587786664902119
    """
    df_t = df.get(term, 0)
    return math.log(1 + (n - df_t + 0.5) / (df_t + 0.5))


def bm25_score(query: str, doc_words: list[str], df, n, avgdl) -> float:
    freqs = Counter(doc_words)
    dl = len(doc_words)
    score = 0.0
    for term in query.split():
        f = freqs.get(term, 0)
        if f == 0:
            continue
        idf = bm25_idf(term, df, n)
        score += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + B * dl / avgdl))
    return score


def rank(query: str, docs=DOCS):
    tokenized, df, avgdl = build_stats(docs)
    n = len(docs)
    scored = {name: bm25_score(query, tokenized[name], df, n, avgdl) for name in docs}
    return sorted(scored.items(), key=lambda kv: kv[1], reverse=True)


def main() -> None:
    query = "overdue invoice"
    print(f"query: {query!r}\n")
    for name, score in rank(query):
        print(f"  {name}: {score:.3f}   | {DOCS[name]!r}")


if __name__ == "__main__":
    main()
