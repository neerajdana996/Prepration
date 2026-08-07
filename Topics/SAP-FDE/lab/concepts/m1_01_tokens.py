"""M1.1 - Tokens: what the model actually reads.

Diagram idea: a sentence gets snapped into "bricks" (tokens). Rule of thumb:
1 token ~= 4 characters ~= 3/4 of a word.

Run:  uv run python concepts/m1_01_tokens.py
"""
from _llm import get_llm

SENTENCE = "The invoice failed unexpectedly"


def rough_token_estimate(text: str) -> int:
    """The back-of-envelope rule you use in an interview: ~4 chars per token."""
    return max(1, round(len(text) / 4))


def main() -> None:
    llm = get_llm()

    # 1) The estimate you can do in your head (no API needed).
    est = rough_token_estimate(SENTENCE)
    print(f"Sentence      : {SENTENCE!r}")
    print(f"Characters    : {len(SENTENCE)}")
    print(f"Word count    : {len(SENTENCE.split())}")
    print(f"~Est tokens   : {est}  (len/4 rule of thumb)")

    # 2) The REAL count, straight from the model's usage report.
    resp = llm.invoke(SENTENCE)
    usage = resp.usage_metadata or {}
    print(f"\nReal input tokens (from API): {usage.get('input_tokens', '?')}")
    print("Notice: 4 words became MORE tokens, because long/rare words split into pieces.")

    # 3) Turn tokens into money (the FDE reflex).
    in_tok = usage.get("input_tokens", est)
    out_tok = usage.get("output_tokens", 0)
    cost = in_tok / 1_000_000 * 3 + out_tok / 1_000_000 * 15  # $3/M in, $15/M out
    print(f"\nAt $3/M input + $15/M output -> this one call ~= ${cost:.6f}")


if __name__ == "__main__":
    main()
