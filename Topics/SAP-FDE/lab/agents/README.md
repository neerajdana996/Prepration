# M5 — Agents (step by step)

Build an agent from scratch, one aspect per file. Each step adds one idea.

Run any step from the lab root:
```bash
cd Topics/SAP-FDE/lab && uv run python agents/m5_01_agent_loop.py
```

## The steps
| # | File | Aspect | One-line idea |
|---|---|---|---|
| 1 | `m5_01_agent_loop.py` | **the loop** | LLM + tools + loop + seatbelts (max steps) |
| 2 | `m5_02_react.py` | **ReAct** | make the reasoning (thought → action → observation) explicit |
| 3 | `m5_03_tool_design.py` | **tool design** | good names/descriptions, arg validation, error returns |
| 4 | `m5_04_planning.py` | **planning** | plan-then-execute for multi-step goals |
| 5 | `m5_05_memory.py` | **memory** | short-term (context) vs long-term (external store) |
| 6 | `m5_06_multi_agent.py` | **multi-agent** | supervisor → worker specialists |
| 7 | `m5_07_reliability.py` | **reliability** | retries, cost caps, human-in-the-loop, guardrails |
| 8 | `m5_08_when_not.py` | **restraint** | workflow vs agent — use the least autonomy that works |

## Two seatbelts every agent needs
- **step cap** — never loop more than N times (in step 1).
- **cost/token budget** — stop if spend exceeds a ceiling (added later).
