"""M3.1 - Bag of Words: turn text into count vectors (hand-coded, no libraries).

No LLM, no network - pure Python. Run it to see your function work:
    uv run python concepts/m3_01_bag_of_words.py
"""

DOCS = {
    "d1": "cat sat on mat",
    "d2": "dog sat on log",
}


def build_vocab(docs: dict[str, str]) -> list[str]:
    """Collect every unique word across all docs, keeping first-seen order."""
    vocab: list[str] = []
    for text in docs.values():
        for word in text.split():
            if word not in vocab:
                vocab.append(word)
    return vocab


def to_bow(text: str, vocab: list[str]) -> list[int]:
    """YOUR TURN.

    Return a list of counts: for each word in `vocab` (in order), how many
    times does it appear in `text`?

    Example: to_bow("dog log", ["cat","sat","on","mat","dog","log"])
             -> [0, 0, 0, 0, 1, 1]
    """
    return [text.split().count(w) for w in vocab]  # <- your code


def dot(v1: list[int], v2: list[int]) -> int:
    """Multiply matching positions and add them up (your 'overlap' idea).
    
    Example: dot([1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 1, 1]) -> 3
             1*0 + 1*1 + 1*1 + 1*0 + 0*1 + 0*1 = 3
    """
    return sum(a * b for a, b in zip(v1, v2))


def main() -> None:
    vocab = build_vocab(DOCS)
    print("vocab      :", vocab)

    doc_vecs = {name: to_bow(text, vocab) for name, text in DOCS.items()}
    # {d1: [1, 1, 1, 1, 0, 0], d2: [0, 1, 1, 0, 1, 1]}
    for name, vec in doc_vecs.items():
        print(f"{name} vector  :", vec)

    query = "dog log"
    qv = to_bow(query, vocab)
    # qv = [0, 0, 0, 0, 1, 1]
    print("query vector:", qv)

    """
    doc_vecs = {d1: [1, 1, 1, 1, 0, 0], d2: [0, 1, 1, 0, 1, 1]}
    qv = [0, 0, 0, 0, 1, 1]
    d1_score = dot(qv, doc_vecs['d1']) = 2 = 0*0 + 0*1 + 0*1 + 0*1 + 1*0 + 1*1
    d2_score = dot(qv, doc_vecs['d2']) = 3 = 0*0 + 0*1 + 0*1 + 0*0 + 1*1 + 1*1
    """

    ranked = sorted(doc_vecs, key=lambda n: dot(qv, doc_vecs[n]), reverse=True)
    for name in ranked:
        print(f"  {name} score = {dot(qv, doc_vecs[name])}")
    print("best match  :", ranked[0])


if __name__ == "__main__":
    main()
