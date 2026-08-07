"""M1.5/M1.6 - Cost and latency: the bill and the speed.

Bill  = input_tokens * in_price + output_tokens * out_price  (output ~5x pricier)
Speed = mostly how LONG the answer is (prefill fast, decode slow -> so we STREAM).

This file measures real tokens, computes the bill, and times a streamed answer
so you can watch decode happen one chunk at a time.

Run:  uv run python concepts/m1_04_cost_latency.py
"""
import time

from _llm import get_llm

IN_PRICE = 3 / 1_000_000    # $3 per million input tokens
OUT_PRICE = 15 / 1_000_000  # $15 per million output tokens
PROMPT = "In 3 sentences, explain what an invoice is."


def main() -> None:
    llm = get_llm()

    # ---- Cost ----
    resp = llm.invoke(PROMPT)
    u = resp.usage_metadata or {}
    in_tok, out_tok = u.get("input_tokens", 0), u.get("output_tokens", 0)
    cost = in_tok * IN_PRICE + out_tok * OUT_PRICE
    print(f"input tokens : {in_tok}")
    print(f"output tokens: {out_tok}")
    print(f"1 call cost  : ${cost:.6f}")
    print(f"at 100k calls/month ~= ${cost * 100_000:,.2f}/month")
    print("(output is fewer tokens but the expensive half -- watch the output)\n")

    # ---- Latency: watch decode stream in ----
    print("Streaming the answer (first chunk = 'time to first token'):")
    start = time.perf_counter()
    first = None
    for chunk in llm.stream(PROMPT):
        if chunk.content:
            if first is None:
                first = time.perf_counter() - start
                print(f"  [first token after {first:.2f}s]")
            print(chunk.content, end="", flush=True)
    total = time.perf_counter() - start
    print(f"\n  [full answer after {total:.2f}s]")
    print("Lesson: shorter answers = faster; stream so users see progress immediately.")


if __name__ == "__main__":
    main()
