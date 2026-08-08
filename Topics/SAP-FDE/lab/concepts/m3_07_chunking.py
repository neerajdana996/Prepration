"""M3.8 - Chunking strategies from scratch (pure Python, no network).

You write the fixed-size + overlap splitter (the core mechanic). A simple
sentence-based splitter is given as a second strategy to compare against.

Run:  python3 concepts/m3_07_chunking.py
"""

SAMPLE = (
    "The invoice was issued on Monday. Payment is due in 30 days. "
    "If payment is late a 2 percent fee applies. Contact billing for help. "
    "Refunds are processed within one week of approval."
)


def fixed_size_chunks(words: list[str], size: int, overlap: int) -> list[str]:
    """YOUR TURN.  Split `words` into chunks of `size` words that OVERLAP by `overlap`.

    Idea: step forward by (size - overlap) each time, take `size` words.
      words = ["a","b","c","d","e"], size=3, overlap=1
      -> ["a b c", "c d e"]        (note "c" repeats = the overlap)

    Return a list of strings (each chunk joined with spaces).
    Hint: use range(0, len(words), size - overlap) and words[start:start+size].
    """
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunks.append(" ".join(words[i:i+size]) if i + size < len(words) else " ".join(words[i:]))
    return chunks


def sentence_chunks(text: str) -> list[str]:
    """Reference strategy: one chunk per sentence (split on '. ')."""
    parts = [s.strip() for s in text.split(". ") if s.strip()]
    return [s if s.endswith(".") else s + "." for s in parts]


def main() -> None:
    words = SAMPLE.split()
    print(f"document has {len(words)} words\n")

    print("Fixed-size (size=8, overlap=2):")
    for i, c in enumerate(fixed_size_chunks(words, size=8, overlap=2), 1):
        print(f"  c{i}: {c}")

    print("\nSentence-based:")
    for i, c in enumerate(sentence_chunks(SAMPLE), 1):
        print(f"  c{i}: {c}")


if __name__ == "__main__":
    main()
