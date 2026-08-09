# Retrieval & RAG — Interview Q&A Bank

**How to use:** Read the question, answer out loud in 60–90s *before* reading the model answer, then run the linked lab so the concept is in your fingers, not just your head.
Tiers go fundamentals → design → senior trade-offs; a real SAP FDE loop will jump between them and chase the "why" — always lead with the trade-off, then the number.

---

## Tier 1 — Fundamentals

### Q: What is an embedding, and what does a single vector actually *represent*?
**Tests:** Do you understand the substrate under all of RAG, or just call an API?
**Answer (production-grade):** An embedding is a fixed-length list of floats (e.g. 768 or 1536 dims) produced by a learned model, positioning a piece of text in a semantic space where *distance ≈ dissimilarity of meaning*. No single dimension is interpretable — meaning is encoded in the *direction* of the vector, learned so that texts used in similar contexts land nearby. That's why "unpaid bill" and "overdue invoice" sit close despite sharing zero words, which lexical methods can't see. Production caveats: (1) embeddings are model-specific — you cannot compare vectors from two different models, and swapping models means a full re-index; (2) most modern models (OpenAI `text-embedding-3`, Cohere, `bge`) are normalized to unit length, so cosine and dot product coincide; (3) query and document should be embedded by the *same* model, and asymmetric models (e.g. E5) want a `query:`/`passage:` prefix.
**Lab:** [`../lab/concepts/m3_04_semantic_search.py`](../lab/concepts/m3_04_semantic_search.py)

### Q: Cosine similarity vs dot product — when does the choice matter?
**Tests:** Precision on the metric, not hand-waving "they measure closeness."
**Answer (production-grade):** Cosine measures the *angle* between two vectors (magnitude-invariant); dot product folds in magnitude too. If all vectors are L2-normalized to unit length, `cosine == dot product` and the choice is moot — which is the common case. The difference bites when vectors are *not* normalized: dot product then rewards longer vectors, so a verbose or "confident" document can outrank a more relevant short one purely on magnitude. Euclidean (L2) distance is monotonically related to cosine *for normalized vectors*, so ANN indexes often let you pick any of the three. Rule of thumb: normalize your embeddings and use cosine/dot interchangeably; only reach for raw dot product when magnitude is a deliberate signal (e.g. some recommendation setups).
**Lab:** [`../lab/concepts/m3_04_semantic_search.py`](../lab/concepts/m3_04_semantic_search.py) (the `cosine` you wrote by hand)

### Q: Explain TF-IDF, then explain why BM25 is strictly better for retrieval.
**Tests:** Sparse-retrieval foundations; can you name the *two* concrete fixes BM25 adds?
**Answer (production-grade):** TF-IDF scores a term as `TF × IDF`: term frequency (how often it appears in this doc) times inverse document frequency (`log(N/df)`, down-weighting words common across the corpus). Two weaknesses: TF grows *linearly* (the 10th mention of "invoice" counts 10×, so keyword spam wins), and it has no principled length normalization (long docs accumulate more matches). BM25 fixes both: (1) **TF saturation** via `k1` (~1.2–1.5) — a term's contribution flattens after a few occurrences, so the 10th mention barely moves the score; (2) **length normalization** via `b` (~0.75) — it divides by document length relative to the average (`dl/avgdl`), so a long doc doesn't win just by being long. That's why BM25 is the default sparse baseline in Elasticsearch/OpenSearch and remains a shockingly strong 2026 baseline, especially for exact terms, IDs, and rare proper nouns.
**Lab:** [`../lab/concepts/m3_02_tfidf.py`](../lab/concepts/m3_02_tfidf.py) → [`../lab/concepts/m3_05_bm25.py`](../lab/concepts/m3_05_bm25.py)

### Q: Lexical vs semantic retrieval (sparse vs dense) — strengths and blind spots of each?
**Tests:** Do you know *why* you'd ever run both instead of picking one?
**Answer (production-grade):** **Sparse/lexical** (BM25) matches actual tokens; its vector is huge and mostly zeros (one dim per vocabulary term). It's exact, cheap, interpretable, and needs no training — unbeatable for error codes, SKUs, statute numbers, and rare names. Its blind spot: zero recall on paraphrase ("unpaid bill" ≠ "overdue invoice"). **Dense/semantic** (embeddings) matches *meaning* in a compact learned space; it nails synonyms and intent, but is fuzzy on exact tokens — it may rank a semantically-adjacent doc above the one containing the literal ticket number the user typed, and it can't match a term the embedding model never learned. The senior insight: their failure modes are *complementary*, which is the entire argument for hybrid search. BM25 also famously beats dense retrieval on code and highly technical corpora.
**Lab:** [`../lab/concepts/m3_03_search.py`](../lab/concepts/m3_03_search.py) (lexical) vs [`../lab/concepts/m3_04_semantic_search.py`](../lab/concepts/m3_04_semantic_search.py) (dense)

### Q: Walk me through chunking strategies and the size/overlap trade-off.
**Tests:** Chunking is the #1 lever on retrieval quality — do you treat it seriously?
**Answer (production-grade):** Chunking decides what a "unit of retrieval" is, so it caps your ceiling. Strategies, roughly increasing in smarts: **fixed-size** (N tokens, dead simple, semantically blind); **recursive character** (split on paragraph→sentence→word boundaries — the pragmatic 2026 default, cheap and robust); **semantic** (embed sentences, cut where similarity drops, i.e. at topic shifts — better recall, more compute); **layout/document-aware** (respect Markdown headers, tables, PDF structure — essential for the messy enterprise docs an FDE actually meets). The trade-off: **small chunks** (~256 tok) give sharp, precise embeddings but can sever the context the LLM needs to answer; **large chunks** (~1024 tok) preserve context but dilute the embedding (one vector averaging many topics) and waste context-window budget. Sensible defaults: ~512 tokens with 10–15% overlap. **Overlap** exists to fight **tail-loss** — a fact split across a boundary lands in neither chunk cleanly; overlapping windows guarantee it appears whole in at least one. Always chunk on a token count, not characters, and align to your embedding model's max sequence length.
**Lab:** [`../lab/concepts/m3_07_chunking.py`](../lab/concepts/m3_07_chunking.py)

### Q: Describe the RAG pipeline end to end. What runs at index time vs query time?
**Tests:** Can you cleanly separate the offline (build) and online (serve) phases?
**Answer (production-grade):** Two phases. **Index (offline, batch):** load → chunk → embed each chunk → store vectors + original text + metadata in a vector DB (build the ANN index). Do this once, refresh on document change. **Query (online, per request):** embed the user query → ANN search for top-N candidates → (optionally hybrid + rerank) → assemble the top-K chunks into a grounded prompt → LLM generates a cited answer. The distinction matters operationally: index-time work is where you spend on quality (good chunking, contextual retrieval, hybrid indexing) because it amortizes across all future queries; query-time is where you fight latency budget (ANN params, rerank depth). Keeping the raw text alongside the vector is non-negotiable — you retrieve *by* vector but feed *text* to the LLM. Freshness is an index-time concern: stale index = stale answers, no matter how good the LLM.
**Lab:** [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py)

### Q: How do you get grounded answers with citations, and make the model say "I don't know"?
**Tests:** This is the whole reason enterprises want RAG — do you know how to actually enforce it?
**Answer (production-grade):** Grounding is enforced in the *prompt contract*, not hoped for. Three rules: (1) "Answer using ONLY the context below"; (2) "If the answer isn't in the context, reply exactly: *I don't know from the provided documents*" — an explicit escape hatch, because without it the model fills gaps with plausible fabrication; (3) "Cite the chunk numbers you used, like [2]." Number each chunk in the prompt so citations are verifiable and post-hoc checkable. Why it works: constraining the model to retrieved evidence collapses its hallucination surface, and the "I don't know" path converts a silent wrong answer (worst outcome in an enterprise) into an honest miss the user can act on. Production hardening: verify every citation actually points at a retrieved chunk, and consider a faithfulness check (does each claim trace to context?) before returning. The "I don't know" rate is itself a monitoring signal — a spike means retrieval is failing.
**Lab:** [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py) (study the `GROUNDED_PROMPT`)

---

## Tier 2 — Applied / Design

### Q: What is hybrid search, and why fuse with Reciprocal Rank Fusion instead of adding scores?
**Tests:** Do you understand *why* score fusion is fragile and RRF is robust?
**Answer (production-grade):** Hybrid search runs BM25 (lexical) *and* dense retrieval in parallel, then merges the two ranked lists — covering each method's blind spot (exact terms + meaning). The naive merge, adding scores, breaks because the two scales are incomparable: BM25 is unbounded (0 to ~30+), cosine is [-1, 1], and normalizing them is brittle and query-dependent. **RRF** sidesteps this entirely by using only *rank position*: a doc's fused score = Σ over rankers of `1/(k + rank)` (k≈60 by convention). No calibration, no tuning per query, robust to outlier scores — a doc ranked #1 by either retriever gets a strong boost regardless of raw magnitude. That's why RRF is the production default for heterogeneous retrievers. Tunable knob: weight the two `1/(k+rank)` terms if you want to lean lexical or semantic. Follow-up they'll ask: RRF loses the *magnitude* of confidence, which is exactly why you still rerank afterward.
**Lab:** [`../lab/concepts/m3_06_hybrid.py`](../lab/concepts/m3_06_hybrid.py)

### Q: Compare HNSW and IVF. Why approximate search at all, and how do they differ from a B-tree?
**Tests:** The single most common vector-DB interview question — recall/latency/memory triangle.
**Answer (production-grade):** Exact nearest-neighbor means comparing the query to *every* vector — O(N) per query, fine at 10K docs, hopeless at 100M. So we use **ANN** (approximate): accept "close enough" neighbors for a massive speedup, trading a little **recall** for latency. A B-tree can't help here because it indexes a 1-D total order; vector similarity is a high-dimensional geometry problem with no meaningful sort order (the "curse of dimensionality"). Two dominant index families:
- **HNSW** (graph): a multi-layer "small-world" graph; queries greedily hop toward the nearest neighbor, coarse at the top layer, fine at the bottom. High recall at low latency, but the graph lives in RAM — **memory-hungry**. Knobs: `M` (edges/node, memory & recall), `efConstruction` (build quality), `efSearch` (recall↔latency at query time).
- **IVF** (clustering): partition vectors into `nlist` Voronoi cells (k-means); at query time probe only the `nprobe` nearest cells. More **memory-efficient** at huge scale, but recall depends on `nprobe` — too few cells and you miss neighbors near a boundary. `nprobe` is a *runtime* knob (no rebuild).

The triangle: **recall ↔ latency ↔ memory** — you pick two. Default advice: HNSW when you need high recall at low latency and can afford RAM (most RAG); IVF (often IVF+PQ **product quantization** to compress vectors) at billion-scale where memory is the bottleneck. Always measure `recall@k` against a brute-force ground-truth set before shipping.
**Lab:** Build: extend [`../lab/concepts/m3_04_semantic_search.py`](../lab/concepts/m3_04_semantic_search.py) from linear scan to an HNSW index (e.g. `faiss`/`hnswlib`) and plot recall vs `efSearch`.

### Q: Explain reranking. Why not just cross-encode all N candidates from the start?
**Tests:** Two-stage retrieval, the bi-encoder/cross-encoder distinction, and the cost math.
**Answer (production-grade):** Two-stage retrieval: **stage 1** a fast **bi-encoder** (embeds query and doc *independently*, so doc vectors are precomputed and reused) fetches N candidates optimizing *recall*; **stage 2** a slow **cross-encoder** (feeds `[query, doc]` *together* through a transformer, modeling their full interaction) reorders them optimizing *precision*. The cross-encoder is far more accurate because it sees query–doc interaction — but it can't precompute anything: every (query, doc) pair is a fresh forward pass. Cross-encoding your whole corpus is `O(corpus)` per query — completely infeasible. So you only rerank the small N the bi-encoder already narrowed to. Sizing: **N ≈ 50–100** candidates in, **K ≈ 3–7** out to the LLM. The **N ≫ K** gap is the point — if N=10 and K=5 you've given the reranker no room to fix ranking errors; you pay latency for nothing. Reality check to mention: off-the-shelf cross-encoders (ms-marco-MiniLM, bge-reranker) are trained on web-search distributions and can *hurt* NDCG on technical/scientific corpora while adding 500–2000ms — domain fit matters, so measure before adopting, and consider a hosted reranker (Cohere Rerank) or fine-tuning.
**Lab:** Build: add a cross-encoder rerank stage on top of [`../lab/concepts/m3_06_hybrid.py`](../lab/concepts/m3_06_hybrid.py) (retrieve N=50 → rerank → K=5); compare hit-rate before/after.

### Q: The user's query retrieves nothing useful. What query-transformation techniques help?
**Tests:** Do you know the modern toolkit and when each applies?
**Answer (production-grade):** The problem is usually a query–document mismatch: queries are short/vague, documents are long/detailed. Techniques:
- **Multi-query expansion:** LLM rewrites the query into several paraphrases, retrieve for each, union the results — raises recall for ambiguous phrasing.
- **RAG-Fusion:** multi-query + fuse the result lists with **RRF** — recall boost plus a sane ranking.
- **HyDE** (Hypothetical Document Embeddings): ask the LLM to *write a fake answer* to the query, embed *that*, and retrieve with it. You're now doing document→document matching instead of question→document, closing the semantic gap. Caveat: the hypothetical can be factually wrong — fine, because you only use its *embedding*, never its content; needs a capable LLM and adds a generation hop of latency.
- **Query decomposition:** break a compound question ("compare the late fee on Standard vs Enterprise") into sub-queries, retrieve each, then synthesize — this is the doorway to multi-hop.

Trade-off to state: every one of these adds LLM calls and latency, so they earn their place only when plain retrieval is measurably missing. Start simple, add transformation when eval shows a recall gap.
**Lab:** Build: wrap [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py) with a multi-query + RRF front-end and compare recall against single-query.

### Q: What is contextual retrieval and why does it help so much?
**Tests:** Awareness of a 2024/2026 best practice and its cost profile.
**Answer (production-grade):** A chunk ripped from a document loses its context — "It reduced churn by 20%" doesn't embed near "loyalty program" because the chunk never names it. **Contextual retrieval** (Anthropic, 2024) fixes this at index time: an LLM reads the full document + the chunk and writes a 1–2 sentence situating summary ("This is from the 2024 loyalty-program section…"), which is *prepended to the chunk before embedding and BM25 indexing*. Now the chunk's vector carries document-level context it structurally lacked. Reported impact: ~**49% fewer retrieval failures**, ~**67% when combined with reranking**. It's composable — layers on top of any chunking strategy — which makes it one of the highest-ROI improvements available. The cost objection (and its answer): it's one LLM call per chunk at index time (50K docs × 50 chunks = a lot of calls), but **prompt caching** on the shared document reduces this up to ~90%, and it's offline/amortized. Cheaper alternative to name: **late chunking** (embed the whole doc at token level, then pool into chunks) achieves similar context-preservation using only the embedding model.
**Lab:** [`../lab/concepts/m4_02_contextual_retrieval.py`](../lab/concepts/m4_02_contextual_retrieval.py)

### Q: Explain parent-child (small-to-big) retrieval and the problem it solves.
**Tests:** Do you see the precision-vs-context tension and how to have both?
**Answer (production-grade):** It resolves the chunk-size dilemma directly: small chunks embed precisely but starve the LLM of context; big chunks give context but blur the embedding. Parent-child **indexes the small children** (sharp, precise matching) but **returns the big parent** (full context) to the LLM. Query matches a child sentence → you hand back its whole parent section. You get precise retrieval *and* complete context without compromising either. Variants: "sentence-window" (return the matched sentence ± a few neighbors) and true hierarchical parent/child. Cost: you store both granularities and manage the child→parent mapping, and parents eat more context-window budget, so cap K accordingly. This is a go-to when answers depend on surrounding context (policy docs, contracts) that a lone matched sentence can't convey.
**Lab:** [`../lab/concepts/m4_03_parent_child.py`](../lab/concepts/m4_03_parent_child.py)

### Q: What is multi-hop RAG, and why do people say it's "just an agent"?
**Tests:** Do you see that iterative retrieval = a reasoning loop, not a bigger top-K?
**Answer (production-grade):** Multi-hop questions need chained lookups: "What's the late fee on the plan that owns order 5001?" requires hop 1 (order 5001 → Enterprise plan), then hop 2 (Enterprise plan → 1% fee). Single-shot retrieval can't do this — the answer to hop 2 depends on hop 1's result, so no single query embeds the right thing. The clean solution is a **ReAct agent**: give the LLM a `search_docs` tool and let it loop *reason → search → observe → reason → search again* until it has enough to answer. That's literally what multi-hop RAG *is* — retrieval promoted from a fixed pipeline stage to a tool the model calls on demand. Trade-offs: far more capable on compositional questions, but each hop is an LLM turn + a retrieval (latency, cost, and the risk of the agent looping or going off-track). Bound it with a max-hops limit and log the trajectory. Simpler pre-agent alternative for known patterns: static query decomposition.
**Lab:** [`../lab/concepts/m4_04_multihop_rag.py`](../lab/concepts/m4_04_multihop_rag.py)

---

## Tier 3 — Senior trade-offs & debugging

### Q: A customer asks: RAG, fine-tuning, or long-context? How do you decide?
**Tests:** The FDE's core consulting judgment — can you match tool to problem, not hype?
**Answer (production-grade):** Frame it as three different questions, not three answers to one:
- **RAG = *knowledge*.** Use when the corpus is large, proprietary, or changes often, and when you need citations/grounding. Freshness (data changes daily) → RAG, because you just update the index. Default starting point for enterprise Q&A.
- **Fine-tuning = *behavior*.** Use to shape *how* the model responds — output schema/format, a specific SQL dialect, tone, a specialized task — not to inject facts. Watch for catastrophic forgetting (a finance-tuned model getting worse at general chat) and the retrain cost when knowledge changes.
- **Long-context = *simplicity*.** If the whole relevant corpus fits in the window and is fairly static, just stuff it — simplest path, great for prototypes. But it's slow and ~20× the per-query cost at volume, and it hits "lost in the middle." If the corpus will outgrow the window, start with RAG now rather than migrating later.

The senior answer: they're complementary — mature systems **fine-tune for behavior + RAG for knowledge**, and long-context is a prototyping shortcut or a within-request tactic (fit more reranked chunks), not a corpus strategy. Anchor the recommendation in the customer's real constraints: data volatility, need for citations, latency/cost budget, and how much domain-specific *behavior* they need.
**Lab:** Build: a decision-matrix doc; cross-links to [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py) and M1 context-window labs.

### Q: What is "lost in the middle" and how do you engineer around it?
**Tests:** Awareness of LLM positional bias and that it changes prompt *ordering*, not just retrieval.
**Answer (production-grade):** From Liu et al. (2023): a model's ability to use information follows a **U-shaped curve** — it uses evidence at the *start* (primacy) and *end* (recency) of the context well, but degrades sharply for evidence in the *middle*, sometimes below a no-context baseline. Bigger context windows don't fix it (suspected cause: positional biases like RoPE decay). Consequences for RAG: (1) don't over-stuff — sending 20 chunks buries the good ones in the dead zone; **reduce** to the ~3–7 that matter; (2) **order strategically** — place the top-reranked chunk *first* (ride the model's bias instead of fighting it), and put the next-best last; (3) this is a direct argument for reranking (get the best chunk to rank 1) and for tight K. Best-practice pipeline: hybrid retrieve N → rerank → keep K≈5 → put rank-1 at the top of the prompt.
**Lab:** Build: an ordering experiment on [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py) — same K chunks, vary position, measure answer accuracy.

### Q: How do you evaluate a RAG system? Why measure retrieval and generation separately?
**Tests:** Do you know the metric taxonomy and why a single blended score is a trap?
**Answer (production-grade):** RAG has two independently-failing components, so a single answer-quality number hides *which* is broken — you must decompose. **Retrieval side** (classic IR + RAGAS): `recall@k` (did the right chunk make the candidate set? — the ceiling on everything downstream), `precision@k`/**context precision** (are retrieved chunks relevant and well-ranked?), MRR, NDCG. **Generation side** (RAGAS/LLM-judge): **faithfulness/groundedness** (is every claim supported by the retrieved context? — decompose answer into statements, verify each), **answer relevancy** (does it actually address the question?). The interview-grade nuance: **faithfulness ≠ correctness** — a model can *faithfully* report bad retrieved context and still be wrong; that failure is upstream in retrieval, which is exactly why you separate the metrics. Build a small golden set (question → ground-truth answer + ground-truth chunks) so you can compute retrieval recall directly. Frameworks: RAGAS, ARES, custom LLM-judge with calibration.
**Lab:** [`../lab/concepts/m6_01_eval_retrieval.py`](../lab/concepts/m6_01_eval_retrieval.py), [`../lab/concepts/m6_04_ragas_from_scratch.py`](../lab/concepts/m6_04_ragas_from_scratch.py), [`../lab/concepts/m6_05_ragas_eval_set.py`](../lab/concepts/m6_05_ragas_eval_set.py)

### Q: Your RAG bot gives a wrong answer. Walk me through debugging it.
**Tests:** Systematic bisection — the single most important senior RAG skill.
**Answer (production-grade):** **Bisect: is it a retrieval failure or a generation failure?** Log and inspect the exact chunks that were retrieved for the failing query.
- **Case A — the right chunk is NOT in the retrieved set → retrieval bug.** Root-cause up the retrieval stack: is the fact even *in* the corpus? Is chunking splitting it across a boundary (fix: overlap, parent-child, contextual retrieval)? Is it a lexical miss on an exact term (fix: add BM25/hybrid)? Is ANN recall too low (raise `efSearch`/`nprobe`, verify against brute-force)? Would reranking or query transformation surface it?
- **Case B — the right chunk IS retrieved but the answer is still wrong → generation bug.** Now it's the LLM: is the evidence buried in the middle (reorder, reduce K)? Is the grounding prompt weak (tighten "answer only from context")? Is it hallucinating despite good context (lower temperature, add the "I don't know" escape, add a faithfulness check)? Is context truncated?

The discipline: **never tune both stages at once** — you can't tell what worked. Measure retrieval recall in isolation first (Case A vs B), fix the failing stage, re-measure. This maps directly to the metric split: low context recall → retrieval; low faithfulness with good context → generation.
**Lab:** [`../lab/concepts/m6_01_eval_retrieval.py`](../lab/concepts/m6_01_eval_retrieval.py) (isolate retrieval) + [`../lab/concepts/m6_02_llm_judge.py`](../lab/concepts/m6_02_llm_judge.py) (isolate generation)

### Q: When would you deliberately NOT add a reranker (or more retrieval sophistication)?
**Tests:** Cost/latency discipline and the "measure first" instinct — anti-over-engineering.
**Answer (production-grade):** Reranking (and multi-query, HyDE, agents) each buy quality with latency and cost, so they must earn it. Skip or defer when: (1) **retrieval recall is already high** and the failure is on the generation side — reranking reorders, it can't add a chunk that recall@k already missed; (2) **latency budget is tight** — a cross-encoder adds 500–2000ms, unacceptable for some interactive UIs; (3) **domain mismatch** — off-the-shelf rerankers trained on web-search can *degrade* NDCG on technical/legal/scientific corpora; without an eval set proving lift, you may be paying to make it worse; (4) **N is already close to K** — no room to help. The FDE principle: instrument first, add complexity only where the eval shows a gap, and always A/B the added stage against a golden set. "We added a reranker because best practice" is not an answer; "recall@50 was 0.9 but precision@5 was 0.4, so a reranker lifted answer accuracy 12% for +300ms — worth it here" is.
**Lab:** Build: an A/B harness reusing [`../lab/concepts/m6_01_eval_retrieval.py`](../lab/concepts/m6_01_eval_retrieval.py) to score with/without rerank on the same golden set.

### Q: How do you keep a production RAG index fresh and scalable for a customer's changing corpus?
**Tests:** Ops reality of RAG — the part demos skip and FDEs live in.
**Answer (production-grade):** Freshness is an index-time problem: an out-of-date index yields confidently stale answers no LLM quality can rescue. Approaches: (1) **incremental upserts** keyed on a stable doc ID + content hash so only changed docs re-embed and re-index (HNSW supports incremental adds; heavy IVF may need periodic rebuilds as centroids drift); (2) **deletes/tombstones** for retracted docs — leaving stale vectors is a correctness *and* compliance risk; (3) **metadata + versioning** so you can filter by effective-date/tenant and answer "as of when"; (4) **change-data-capture / scheduled crawls** to detect source updates. Scaling levers: shard/partition by tenant or namespace (also the isolation boundary in multi-customer deployments), pre-filter by metadata to shrink the ANN search space, quantize (PQ) to fit memory at billion-scale, and monitor `recall@k`, p95 query latency, and index-lag. Also plan the **re-embedding migration** for when you upgrade the embedding model — it's a full re-index, so budget for it. Track the "I don't know" rate as a live retrieval-health signal.
**Lab:** Build: add content-hash upsert + delete to the KB in [`../lab/concepts/m4_01_rag.py`](../lab/concepts/m4_01_rag.py); simulate a doc update and confirm the answer changes.

---

## Code gaps to add
Concepts covered above that have **no runnable lab yet** — worth building to make the answers muscle memory:
- **ANN index lab** (`m3_08_ann_index.py`): linear scan → `hnswlib`/`faiss` HNSW; measure `recall@k` vs brute force and plot recall↔latency as `efSearch` varies. Also demo IVF `nprobe`. *(Referenced by the HNSW/IVF question — currently the only lab there is a "Build:".)*
- **Reranking lab** (`m3_09_rerank.py`): cross-encoder (e.g. `sentence-transformers` ms-marco or Cohere Rerank) reordering hybrid's N=50 → K=5; hit-rate before/after; expose the N≫K trade-off.
- **Query transformation lab** (`m4_05_query_transform.py`): multi-query, RAG-Fusion (multi-query + RRF), and HyDE on one KB, compared on recall.
- **Lost-in-the-middle / ordering lab** (`m4_06_context_ordering.py`): fixed K chunks, vary position, measure answer accuracy — makes the U-curve concrete.
- **Index freshness lab**: content-hash upsert + delete/tombstone over `m4_01_rag.py`'s KB to demonstrate incremental re-indexing.

## Sources
- [DataCamp — Top 30 RAG Interview Questions (2026)](https://www.datacamp.com/blog/rag-interview-questions)
- [Analytics Vidhya — RAG Interview: 40 Questions](https://www.analyticsvidhya.com/blog/2026/02/rag-interview-questions-and-answers/)
- [Milvus — IVF vs HNSW: how it works and when to choose it](https://milvus.io/blog/understanding-ivf-vector-index-how-It-works-and-when-to-choose-it-over-hnsw.md)
- [AppScale — Vector Index Tuning: HNSW, IVF & Product Quantization (recall/latency/memory, 2026)](https://appscale.blog/en/blog/vector-index-tuning-hnsw-ivf-product-quantization-recall-latency-2026)
- [faceprep — Embeddings and Vector Database Interview Questions (2026)](https://faceprep.in/article/embeddings-and-vector-database-interview-questions-2026/)
- [Medium (Hakim) — Inside the RAG Retrieval Pipeline: Bi-Encoders, Cross-Encoders, Re-Rankers, Two-Stage, RRF](https://medium.com/@mudassar.hakim/inside-the-rag-retrieval-pipeline-bi-encoders-cross-encoders-re-rankers-two-stage-retrieval-c391bea7eae4)
- [OpenAI Cookbook — Search reranking with cross-encoders](https://cookbook.openai.com/examples/search_reranking_with_cross-encoders)
- [AWS — Contextual retrieval in Anthropic using Amazon Bedrock Knowledge Bases](https://aws.amazon.com/blogs/machine-learning/contextual-retrieval-in-anthropic-using-amazon-bedrock-knowledge-bases/)
- [KX/Medium — Late Chunking vs Contextual Retrieval: the math behind RAG's context problem](https://medium.com/kx-systems/late-chunking-vs-contextual-retrieval-the-math-behind-rags-context-problem-d5a26b9bbd38)
- [denser.ai — RAG Chunking Strategies 2026](https://denser.ai/blog/rag-chunking-strategies/)
- [Liu et al. 2023 — Lost in the Middle: How Language Models Use Long Contexts (arXiv:2307.03172)](https://arxiv.org/abs/2307.03172)
- [Medium (Dewoolkar) — RAG vs Fine-tuning vs Long Context: When to Use What](https://medium.com/@officialpreksha2166/rag-vs-fine-tuning-vs-long-context-when-to-use-what-and-why-most-teams-get-it-wrong-388cc446ff3c)
- [GeeksforGeeks — Hypothetical Document Embeddings (HyDE)](https://www.geeksforgeeks.org/data-science/hypothetical-document-embeddings-hyde-hyde/)
- [Superlinked — Evaluating Retrieval Augmented Generation using RAGAS](https://superlinked.com/blog/evaluating-retrieval-augmented-generation-ragas)
- [Braintrust — Best RAG Evaluation Tools in 2026](https://www.braintrust.dev/articles/best-rag-evaluation-tools)
