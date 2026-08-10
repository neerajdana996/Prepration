"""Production agent (LangGraph) — every production concern as an explicit STAGE.

Graph:  input_guardrail -> route -> retrieve -> generate -> hitl_gate -> output_guardrail -> respond
Cross-cutting:
  - access control: stage 3 scopes every fetch to the request's customer_id
  - grounding:      stage 4 answers ONLY from fetched context, with citations
  - safety:         stage 1 blocks injection; stage 5 gates money actions on a human; stage 6 redacts PII
  - observability:  every stage appends a span to state['trace'] -> printed at the end

Structured data (orders/invoices) = tool/API (mocked here); policy = RAG (mocked here).
Runnable from the lab venv (LLM stages need GOOGLE_API_KEY):
    cd Topics/SAP-FDE/lab && uv run python ../production-kb/reference-agent/production_agent.py
""" 
import os
import re
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

# --- mocked enterprise data, keyed by customer (access control bites here) ---
INVOICES = {"12345": {"INV-9": "double-charged: $79 on 2026-07-01 AND $79 on 2026-07-02"}}
POLICY_DOCS = ["Refunds are allowed within 30 days for a verified duplicate charge."]

INJECTION = ["ignore all", "ignore previous", "system prompt", "disregard your"]
PII = re.compile(r"[\w.]+@[\w.]+|\b(?:\d[ -]?){13,16}\b")


def _llm(temp: float = 0.0):
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        temperature=temp,
    )


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


class State(TypedDict):
    query: str
    customer_id: str
    intent: Optional[str]
    context: str
    answer: str
    needs_approval: bool
    blocked: Optional[str]
    trace: list


def _span(state: State, stage: str, note: str) -> None:
    state["trace"].append(f"[{stage}] {note}")


# 1 — SECURITY: block injection, attach the customer scope
def input_guardrail(state: State) -> State:
    if any(p in state["query"].lower() for p in INJECTION):
        state["blocked"] = "input guardrail: possible prompt injection"
    _span(state, "1 input-guardrail", f"scope=customer:{state['customer_id']}; injection check")
    return state


# 2 — AGENTS: supervisor routes to a specialist
def route(state: State) -> State:
    if state.get("blocked"):
        return state
    raw = _text(_llm().invoke(
        f"Classify the query as one word: order, invoice, or policy.\nQuery: {state['query']}"
    ).content).lower()
    state["intent"] = next((k for k in ("invoice", "order", "policy") if k in raw), "policy")
    _span(state, "2 route", f"-> {state['intent']} specialist")
    return state


# 3 — RETRIEVAL + ACCESS CONTROL: tool/API for structured, RAG for policy
def retrieve(state: State) -> State:
    if state.get("blocked"):
        return state
    if state["intent"] in ("invoice", "order"):
        state["context"] = str(INVOICES.get(state["customer_id"], {}))  # scoped!
        _span(state, "3 retrieve", f"ERP {state['intent']} API, scoped to {state['customer_id']}")
    else:
        state["context"] = " ".join(POLICY_DOCS)
        _span(state, "3 retrieve", "policy RAG (vector search)")
    return state


# 4 — GROUNDING: answer only from context, with citation
def generate(state: State) -> State:
    if state.get("blocked"):
        return state
    state["answer"] = _text(_llm().invoke(
        "Answer using ONLY the context; cite it; say 'I don't know' if it's not there.\n"
        f"Context: {state['context']}\nQuestion: {state['query']}"
    ).content)
    state["needs_approval"] = "refund" in state["query"].lower()  # high-impact?
    _span(state, "4 generate", "grounded answer produced")
    return state


# 5 — SAFETY: human-in-the-loop for high-impact actions
def hitl_gate(state: State) -> State:
    if state.get("blocked"):
        return state
    if state.get("needs_approval"):
        state["answer"] += "\n[PENDING HUMAN APPROVAL — refund is a high-impact action]"
        _span(state, "5 hitl", "high-impact -> requires human approval")
    else:
        _span(state, "5 hitl", "no high-impact action; auto-proceed")
    return state


# 6 — SECURITY: redact PII / enforce block
def output_guardrail(state: State) -> State:
    if state.get("blocked"):
        state["answer"] = "Request blocked: " + state["blocked"]
    else:
        state["answer"] = PII.sub("[REDACTED]", state["answer"])
    _span(state, "6 output-guardrail", "PII redacted; safety checked")
    return state


# 7 — OBSERVABILITY: respond
def respond(state: State) -> State:
    _span(state, "7 respond", "returned to rep")
    return state


def build():
    g = StateGraph(State)
    nodes = [input_guardrail, route, retrieve, generate, hitl_gate, output_guardrail, respond]
    for fn in nodes:
        g.add_node(fn.__name__, fn)
    g.add_edge(START, "input_guardrail")
    for a, b in zip(nodes, nodes[1:]):
        g.add_edge(a.__name__, b.__name__)
    g.add_edge("respond", END)
    return g.compile()


def main() -> None:
    app = build()
    out = app.invoke({
        "query": "Customer #12345 was double-charged on INV-9 — can they get a refund?",
        "customer_id": "12345", "intent": None, "context": "", "answer": "",
        "needs_approval": False, "blocked": None, "trace": [],
    })
    print("ANSWER:\n", out["answer"], "\n")
    print("OBSERVABILITY TRACE (one span per stage):")
    for s in out["trace"]:
        print("  ", s)


if __name__ == "__main__":
    main()
