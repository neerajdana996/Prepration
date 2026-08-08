"""M3.2/3.3/3.4 - TF-IDF from scratch (no libraries).

Build order:  document_frequencies (df) -> idf -> term_frequency (tf) -> tfidf
Score = tf (how much of THIS doc is the word)  x  idf (how RARE across all docs).

Pure Python, no network. Run:
    uv run python concepts/m3_02_tfidf.py     (or)     python3 concepts/m3_02_tfidf.py
"""
import math

# ---- One running example (an "invoice" mini-corpus) ----
DOCS = {
    "d1": "please pay the invoice",
    "d2": "the invoice is overdue",
    "d3": "please reset the password",
}
N = len(DOCS)  # total number of documents = 3


def term_frequency(text: str) -> dict[str, float]:
    """TF: how big a fraction of this ONE doc is each word.

    Example: term_frequency("please pay the invoice")
      words = ["please","pay","the","invoice"], length = 4
      -> {"please":0.25, "pay":0.25, "the":0.25, "invoice":0.25}
    """
    words = text.split()
    length = len(words)
    return {w: words.count(w) / length for w in words}


def document_frequencies(docs: dict[str, str]) -> dict[str, int]:
    """DF: in how many docs does each word appear at least once?

    Example over the 3 docs above:
      {"please":2, "pay":1, "the":3, "invoice":2, "is":1,
       "overdue":1, "reset":1, "password":1}
      -> "the" is in all 3, "invoice" is in 2.
    """
    df: dict[str, int] = {}
    for text in docs.values():
        for word in set(text.split()):  # set() so repeats in one doc count once
            df[word] = df.get(word, 0) + 1
    return df


def idf(word: str, df: dict[str, int], n: int) -> float:
    """YOUR TURN.  IDF = log(total docs / docs containing the word).

    Example: idf("the", df, 3)     -> log(3/3) = log(1) = 0.00   (dead)
             idf("invoice", df, 3) -> log(3/2) = log(1.5) = 0.405 (useful)
    Hint: math.log(...) is the natural log; any base works for ranking.
    """
    return math.log(n / df[word])


def tfidf(text: str, df: dict[str, int], n: int) -> dict[str, float]:
    """YOUR TURN.  For each word in the doc: tf(word) * idf(word).

    Example: tfidf("please pay the invoice", df, 3)
      "the"     -> 0.25 * 0.00  = 0.00   (killed by idf)
      "invoice" -> 0.25 * 0.405 = 0.101
    Hint: call term_frequency(text), then multiply each tf by idf(word, df, n).
    """
    tf = term_frequency(text)
    return {w: tf[w] * idf(w, df, n) for w in tf}


def main() -> None:
    df = document_frequencies(DOCS)
    print("document frequencies:", df, "\n")

    print("IDF of a few words:")
    for w in ("the", "please", "invoice", "password"):
        print(f"  idf({w!r}) = {idf(w, df, N):.3f}")

    print("\nTF-IDF vectors per doc:")
    for name, text in DOCS.items():
        vec = {w: round(v, 3) for w, v in tfidf(text, df, N).items()}
        print(f"  {name}: {vec}")

    # Rank docs for a one-word query using that word's tf-idf in each doc.
    query = "invoice"
    print(f"\nRanking docs for query {query!r}:")
    scored = {name: tfidf(text, df, N).get(query, 0.0) for name, text in DOCS.items()}
    for name in sorted(scored, key=scored.get, reverse=True):
        print(f"  {name} score = {scored[name]:.3f}")


if __name__ == "__main__":
    main()
