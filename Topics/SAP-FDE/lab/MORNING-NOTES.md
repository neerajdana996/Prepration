# Overnight build — ready to run

New runnable files filling the code gaps. All **syntax-verified** (py_compile) and
built against your installed LangGraph API. They need your `GOOGLE_API_KEY` to fully
run; free-tier may throttle (429) — just rerun. Recommended `.env`:
`GEMINI_MODEL=gemini-2.5-flash-lite` (fast) · `EMBED_MODEL=models/gemini-embedding-001`.

Run from the lab root: `cd Topics/SAP-FDE/lab`

## RAG (advanced)
| File | Shows |
|---|---|
| `concepts/m4_02_contextual_retrieval.py` | prepend LLM context before embedding → ambiguous chunk becomes findable (naive vs contextual cosine) |
| `concepts/m4_03_parent_child.py` | match the small child, return the big parent section |
| `concepts/m4_04_multihop_rag.py` | multi-hop RAG as a LangGraph ReAct agent with a `search_docs` tool (order 5001 → Enterprise → 1% fee) |

## Evals (RAGAS)
| File | Shows |
|---|---|
| `concepts/m6_05_ragas_eval_set.py` | all 4 RAGAS metrics over an eval SET, with averages (what you gate on). Real lib: `uv add ragas` (import shown in file header) |

## Agents (LangGraph)
| File | Shows |
|---|---|
| `agents/m5_11_langgraph_memory.py` | a `MemorySaver` checkpointer → recalls across turns WITHOUT resending history |
| `agents/m5_12_langgraph_agents_as_tools.py` | supervisor ReAct agent with two specialist ReAct agents exposed as tools |

## Quick smoke test (run these first)
```bash
uv run python concepts/m4_03_parent_child.py        # RAG
uv run python agents/m5_12_langgraph_agents_as_tools.py   # multi-agent
```

## Next session plan
Foundation (M1–M6) is ~95% done. Next = the 0% high-weight modules that ARE your
3 interview rounds: **M9 System Design**, **M10 Delivery**, **M12 Behavioral** (+ M7 Safety, M8 Production).
Say "continue" and we start (recommend M9 or M12).
