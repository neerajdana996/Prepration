"""M4.2 - Contextual retrieval: prepend an LLM-written context before embedding.

Compares naive vs contextualized embedding of an ambiguous chunk ("It reduced
churn...") against the query "did the loyalty program cut churn?". The context
line pulls 'loyalty program' into the embedding, so the match jumps.

Needs GOOGLE_API_KEY. Run:  uv run python concepts/m4_02_contextual_retrieval.py
"""
from _llm import get_embeddings, get_llm
from m3_04_semantic_search import cosine

DOC = (
    "Our 2024 loyalty program launched in March. "
    "It reduced churn by 20 percent. "
    "The program is free for all customers."
)
AMBIGUOUS = "It reduced churn by 20 percent."
QUERY = "did the loyalty program cut churn?"


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict)).strip()


def contextualize(chunk: str, doc: str) -> str:
    ctx = _text(get_llm().invoke(
        f"In one short phrase, say what this chunk is about within the document. "
        f"Reply with ONLY the phrase.\nDocument: {doc}\nChunk: {chunk}"
    ).content)
    return f"[{ctx}] {chunk}"


def main() -> None:
    embed = get_embeddings()
    qv = embed.embed_query(QUERY)

    naive_score = cosine(qv, embed.embed_query(AMBIGUOUS))

    contextual_chunk = contextualize(AMBIGUOUS, DOC)
    contextual_score = cosine(qv, embed.embed_query(contextual_chunk))

    print(f"query: {QUERY!r}\n")
    print(f"naive chunk:        {AMBIGUOUS!r}")
    print(f"  cosine = {naive_score:.3f}\n")
    print(f"contextualized:     {contextual_chunk!r}")
    print(f"  cosine = {contextual_score:.3f}\n")
    print("Contextual should score higher -> the prepended context makes the chunk findable.")


if __name__ == "__main__":
    main()
