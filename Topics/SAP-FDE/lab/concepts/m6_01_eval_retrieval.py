"""M6.2 - Evaluate retrieval with hit@k (objective, offline, no network).

A golden set = questions paired with the chunk that SHOULD be retrieved.
hit@k = fraction of questions whose relevant chunk lands in the top-k.
This is the number you watch when you 'tune on evals'.

Reuses your BM25 from m3_05. Run:  python3 concepts/m6_01_eval_retrieval.py
"""
from m3_05_bm25 import bm25_score, build_stats

KB = {
    "c1": "invoice due within 30 days of issue",
    "c2": "late payment fee 2 percent after due date",
    "c3": "refunds processed within 7 business days",
    "c4": "reset password via forgot password on login page",
    "c5": "support available monday to friday",
}

# Each test case: the question and the chunk id that SHOULD come back.
GOLDEN = [
    {"q": "how many days until the invoice is due", "relevant": "c1"},
    {"q": "what is the late fee", "relevant": "c2"},
    {"q": "how long for refunds", "relevant": "c3"},
    {"q": "how to reset my password", "relevant": "c4"},
    {"q": "unpaid bill", "relevant": "c1"},  # paraphrase - BM25 shares no words -> will MISS
]


def retrieve_topk(query: str, k: int) -> list[str]:
    """Return the ids of the top-k chunks by BM25 (only positive scores)."""
    tokenized, df, avgdl = build_stats(KB)
    n = len(KB)
    scored = [(cid, bm25_score(query, tokenized[cid], df, n, avgdl)) for cid in KB]
    scored = [(cid, s) for cid, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in scored[:k]]


def hit_at_k(golden: list[dict], k: int) -> float:
    """YOUR TURN.

    For each case in `golden`, retrieve the top-k ids with retrieve_topk(case["q"], k).
    Count it a HIT if case["relevant"] is in that list.
    Return  hits / total  (a float between 0 and 1).
    """
    hits = 0
    for case in golden:
        if case["relevant"] in retrieve_topk(case["q"], k):
            hits += 1
    return hits / len(golden)


def main() -> None:
    for k in (1, 2, 3):
        print(f"hit@{k} = {hit_at_k(GOLDEN, k):.2f}")
    print("\n(BM25 caps below 1.0 because of the 'unpaid bill' paraphrase — a meaning miss.)")


if __name__ == "__main__":
    main()
