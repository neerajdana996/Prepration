"""M4.4 - Multi-hop RAG = a ReAct agent with a 'search_docs' tool.

The question needs two lookups: (1) which customer/plan owns order 5001, then
(2) that plan's late fee. The agent hops: search -> reason -> search again.
Built on LangGraph's create_react_agent (search is just its tool).

Needs GOOGLE_API_KEY. Run:  uv run python concepts/m4_04_multihop_rag.py
"""
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from _llm import get_embeddings, get_llm
from m3_04_semantic_search import cosine

KB = [
    "Order 5001 was placed by Acme Corp, who are on the Enterprise plan.",
    "The Enterprise plan has a 1 percent monthly late fee.",
    "The Standard plan has a 3 percent monthly late fee.",
    "Orders ship within 2 business days.",
]
_EMBED = get_embeddings()
_KB_VECS = [(fact, _EMBED.embed_query(fact)) for fact in KB]


@tool
def search_docs(query: str) -> str:
    """Search the company knowledge base; returns the single most relevant sentence."""
    qv = _EMBED.embed_query(query)
    fact, _ = max(_KB_VECS, key=lambda p: cosine(qv, p[1]))
    return fact


def main() -> None:
    agent = create_react_agent(get_llm(), [search_docs])
    q = "What is the late-fee policy for the customer who placed order 5001?"
    result = agent.invoke({"messages": [("user", q)]})
    print("Q:", q, "\n")
    for m in result["messages"]:
        m.pretty_print()
    print("\nWatch it search twice: order 5001 -> Enterprise plan -> Enterprise late fee = 1%.")


if __name__ == "__main__":
    main()
