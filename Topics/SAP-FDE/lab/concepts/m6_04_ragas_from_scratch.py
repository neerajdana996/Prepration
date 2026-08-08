"""M6.5 - The 4 RAGAS metrics, hand-coded (see what the library actually does).

Scores ONE RAG example using your judge + embeddings + cosine:
  context_recall    : did we retrieve the gold-relevant chunk?          (objective)
  context_precision : of retrieved chunks, how many are relevant?       (LLM judges each)
  faithfulness      : is the answer supported by the retrieved context? (LLM judge)
  answer_relevancy  : does the answer address the question?             (generate Qs + cosine)

Needs GOOGLE_API_KEY (~8 calls; free tier may throttle -> just rerun).
Run:  uv run python concepts/m6_04_ragas_from_scratch.py

Real-world: `pip install ragas` gives these out of the box:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
"""
from typing import Literal

from pydantic import BaseModel

from _llm import get_embeddings, get_llm
from m3_04_semantic_search import cosine

QUESTION = "How long do I have to pay an invoice?"
RETRIEVED = [
    "Invoices are due within 30 days of the issue date.",  # relevant
    "Our office is closed on public holidays.",            # junk (hurts precision)
]
ANSWER = "You have 30 days from the issue date to pay."
GOLD_RELEVANT = "Invoices are due within 30 days of the issue date."


class YesNo(BaseModel):
    verdict: Literal["yes", "no"]


def _judge(prompt: str) -> str:
    return get_llm().with_structured_output(YesNo).invoke(prompt).verdict


def context_recall(retrieved: list[str], gold: str) -> float:
    """Did the chunk we NEEDED actually get retrieved?"""
    return 1.0 if gold in retrieved else 0.0


def context_precision(question: str, retrieved: list[str]) -> float:
    """Of the retrieved chunks, what fraction are actually relevant?"""
    relevant = sum(
        _judge(f"Is this chunk relevant to the question? yes/no.\nQ: {question}\nChunk: {c}") == "yes"
        for c in retrieved
    )
    return relevant / len(retrieved)


def faithfulness(retrieved: list[str], answer: str) -> float:
    """Is every claim in the answer supported by the context?"""
    ctx = " ".join(retrieved)
    v = _judge(f"Is EVERY claim in the answer supported by the context? yes/no.\nContext: {ctx}\nAnswer: {answer}")
    return 1.0 if v == "yes" else 0.0


def answer_relevancy(question: str, answer: str) -> float:
    """RAGAS trick: what questions would this answer fit? Compare them to the real Q."""
    gen = get_llm(temperature=0.3).invoke(
        f"Write 3 questions this answer would correctly answer, one per line.\nAnswer: {answer}"
    ).content
    gen_qs = [q.strip("-*0123456789. ").strip() for q in gen.splitlines() if q.strip()][:3]
    embed = get_embeddings()
    qv = embed.embed_query(question)
    sims = [cosine(qv, embed.embed_query(g)) for g in gen_qs]
    return sum(sims) / len(sims) if sims else 0.0


def main() -> None:
    print(f"context_recall    = {context_recall(RETRIEVED, GOLD_RELEVANT):.2f}   (needed chunk retrieved?)")
    print(f"context_precision = {context_precision(QUESTION, RETRIEVED):.2f}   (junk chunk should drag this to ~0.5)")
    print(f"faithfulness      = {faithfulness(RETRIEVED, ANSWER):.2f}   (answer grounded?)")
    print(f"answer_relevancy  = {answer_relevancy(QUESTION, ANSWER):.2f}   (answer on-topic? higher = better)")


if __name__ == "__main__":
    main()
