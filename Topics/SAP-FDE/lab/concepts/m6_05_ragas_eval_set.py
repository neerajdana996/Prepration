"""M6.5 - RAGAS-style eval over a SET of cases (hand-coded), with averages.

Runs the 4 metrics on several RAG examples and averages them - what you'd watch
in CI. Real library equivalent (after `uv add ragas`):
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

Needs GOOGLE_API_KEY (several calls; free tier may throttle -> rerun).
Run:  uv run python concepts/m6_05_ragas_eval_set.py
"""
from typing import Literal

from pydantic import BaseModel

from _llm import get_embeddings, get_llm
from m3_04_semantic_search import cosine

# Eval set: question, retrieved chunks, the gold-relevant chunk, and the answer.
EVAL_SET = [
    {
        "q": "How long do I have to pay an invoice?",
        "retrieved": ["Invoices are due within 30 days.", "The office is closed on holidays."],
        "gold": "Invoices are due within 30 days.",
        "answer": "You have 30 days to pay.",
    },
    {
        "q": "What is the late fee?",
        "retrieved": ["A late fee of 2 percent applies after the due date.", "Refunds take 7 days."],
        "gold": "A late fee of 2 percent applies after the due date.",
        "answer": "The late fee is 2 percent, and you can call support for a waiver.",  # unsupported add
    },
]


class YesNo(BaseModel):
    verdict: Literal["yes", "no"]


def _judge(prompt: str) -> str:
    return get_llm().with_structured_output(YesNo).invoke(prompt).verdict


def context_recall(retrieved, gold) -> float:
    return 1.0 if gold in retrieved else 0.0


def context_precision(q, retrieved) -> float:
    rel = sum(_judge(f"Relevant to the question? yes/no.\nQ: {q}\nChunk: {c}") == "yes" for c in retrieved)
    return rel / len(retrieved)


def faithfulness(retrieved, answer) -> float:
    ctx = " ".join(retrieved)
    return 1.0 if _judge(f"Every claim supported by context? yes/no.\nContext: {ctx}\nAnswer: {answer}") == "yes" else 0.0


def answer_relevancy(q, answer) -> float:
    gen = get_llm(temperature=0.3).invoke(
        f"Write 3 questions this answer would correctly answer, one per line.\nAnswer: {answer}"
    ).content
    if not isinstance(gen, str):
        gen = " ".join(b.get("text", "") for b in gen if isinstance(b, dict))
    qs = [x.strip("-*0123456789. ").strip() for x in gen.splitlines() if x.strip()][:3]
    embed = get_embeddings()
    qv = embed.embed_query(q)
    sims = [cosine(qv, embed.embed_query(g)) for g in qs]
    return sum(sims) / len(sims) if sims else 0.0


def main() -> None:
    totals = {"recall": 0.0, "precision": 0.0, "faithfulness": 0.0, "answer_rel": 0.0}
    for case in EVAL_SET:
        r = context_recall(case["retrieved"], case["gold"])
        p = context_precision(case["q"], case["retrieved"])
        f = faithfulness(case["retrieved"], case["answer"])
        a = answer_relevancy(case["q"], case["answer"])
        totals["recall"] += r; totals["precision"] += p
        totals["faithfulness"] += f; totals["answer_rel"] += a
        print(f"{case['q']!r}\n  recall={r:.2f} precision={p:.2f} faithful={f:.2f} answer_rel={a:.2f}\n")
    n = len(EVAL_SET)
    print("AVERAGES (this is what you gate on in CI):")
    for k, v in totals.items():
        print(f"  {k:12} = {v / n:.2f}")


if __name__ == "__main__":
    main()
