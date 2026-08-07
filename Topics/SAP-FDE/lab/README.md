# FDE Lab — hands-on practice for the SAP FDE curriculum

One runnable file per concept. Each mirrors a diagram from the lessons. Model: **Google Gemini** (free tier). Package manager: **uv**.

## Setup (once)

```bash
cd Topics/SAP-FDE/lab
cp .env.example .env          # then paste your free key into .env
uv sync                        # creates .venv and installs deps
```

Get a free key: https://aistudio.google.com/apikey

## Run any concept

```bash
uv run python concepts/m1_01_tokens.py
```

## M1 — the LLM engine (all runnable now)

| File | Concept | The idea in one line |
|---|---|---|
| `m1_01_tokens.py` | Tokens | text → bricks; ~4 chars/token; tokens → money |
| `m1_02_sampling.py` | Temperature | low temp = predictable, high temp = creative |
| `m1_03_context_window.py` | Context window | one shared desk; long chats grow the input |
| `m1_04_cost_latency.py` | Cost & latency | the bill + stream so it feels fast |
| `m1_05_messages_memory.py` | Roles & statelessness | model has amnesia; you resend the transcript |
| `m1_06_few_shot.py` | Few-shot | teach by showing examples, no training |
| `m1_07_structured_output.py` | Structured output | get a JSON form, not an essay |
| `m1_08_tool_calling.py` | Tool calling | model proposes, your code disposes |

> Attention / n² cost (M1.4 in the curriculum) is conceptual — no code file; see the diagram in the lesson.

## What's next
- **M2** prompting discipline, **M3** we hand-code TF-IDF / cosine / BM25 / a mini vector search in plain Python (no libraries) before RAG.
- **M5** is where **LangGraph** earns its place — agent loops and multi-agent graphs.

Curriculum + diagrams live one folder up in [`CURRICULUM.md`](../CURRICULUM.md).
