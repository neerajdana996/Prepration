"""M4.1 - The full RAG pipeline: retrieve → ground → generate (with citations).

Ties together everything from M3 (embeddings + your cosine) plus a grounded
generation step. The grounding PROMPT is the star - study its three rules:
  1) answer ONLY from the context
  2) if it's not there, say so (don't guess)
  3) cite the chunk numbers used

Needs GOOGLE_API_KEY. Run:  uv run python concepts/m4_01_rag.py
"""
import os

from dotenv import load_dotenv
from _llm import get_embeddings, get_llm
from m3_04_semantic_search import cosine

load_dotenv()

# A tiny knowledge base. Each string is one chunk (already split for us).
KB = [
    "Invoices are due within 30 days of the issue date.",
    "A late payment fee of 2 percent applies after the due date.",
    "Refunds are processed within 7 business days of approval.",
    "To reset your password, click 'Forgot password' on the login page.",
    "Support is available Monday to Friday, 9am to 5pm CET.",
]

GROUNDED_PROMPT = """You are a support assistant. Answer the question using ONLY the context below.
If the answer is not in the context, reply exactly: "I don't know from the provided documents."
Cite the chunk numbers you used, like [1].

Context:
{context}

Question: {question}
Answer:"""


def retrieve(query: str, embed, kb_vecs: list[list[float]], k: int = 2) -> list[int]:
    qv = embed.embed_query(query)
    order = sorted(range(len(KB)), key=lambda i: cosine(qv, kb_vecs[i]), reverse=True)
    return order[:k]


def answer(question: str, embed, kb_vecs, llm) -> tuple[str, list[int]]:
    idxs = retrieve(question, embed, kb_vecs)
    context = "\n".join(f"[{i + 1}] {KB[i]}" for i in idxs)
    prompt = GROUNDED_PROMPT.format(context=context, question=question)
    return llm.invoke(prompt).content.strip(), idxs


def main() -> None:
    embed = get_embeddings()
    kb_vecs = [embed.embed_query(chunk) for chunk in KB]
    llm = get_llm()

    questions = [
        "How long do I have to pay an invoice?",   # answerable
        "Do you have a mobile app?",                # NOT in the KB -> should refuse
    ]
    for q in questions:
        ans, idxs = answer(q, embed, kb_vecs, llm)
        print(f"Q: {q}")
        print(f"   retrieved chunks: {[i + 1 for i in idxs]}")
        print(f"   A: {ans}\n")


if __name__ == "__main__":
    main()
