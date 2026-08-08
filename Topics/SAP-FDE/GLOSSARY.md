# FDE Glossary — what we built (plain words) → the industry term

Speak these names in the interview. You *built* each one, so you can explain the mechanism AND name it.

## M1 — LLM engine
| We said | Industry term |
|---|---|
| word-pieces the model reads | **tokens** / tokenization (BPE) |
| guess the next word, loop | **autoregressive next-token prediction** |
| creativity knob | **temperature** |
| "top guesses adding to X%" | **top-p (nucleus) sampling** |
| the desk / how much it can see | **context window** |
| every token looks at every token | **(self-)attention** (O(n²)) |
| read input fast / write output slow | **prefill vs decode** |
| model has amnesia, resend history | **stateless API** |
| reuse the fixed prefix cheaply | **prompt caching** |
| teach by examples in the prompt | **few-shot / in-context learning** |
| get a JSON form not prose | **structured output** (schema-constrained decoding) |
| model asks, your code runs it | **tool / function calling** |

## M3 — Retrieval
| We said | Industry term |
|---|---|
| count words | **Bag of Words (BoW)** |
| divide by doc length | **Term Frequency (TF)** |
| rare-word weight | **Inverse Document Frequency (IDF)** |
| TF × IDF | **TF-IDF** |
| compare vectors by angle | **cosine similarity** |
| better TF-IDF with saturation + length | **BM25 (Okapi BM25)** |
| meaning vectors | **embeddings** (dense vectors) |
| keyword vs meaning search | **lexical (sparse) vs semantic (dense)** retrieval |
| use both, merge results | **hybrid search** |
| merge two ranked lists | **Reciprocal Rank Fusion (RRF)** |
| split docs into pieces | **chunking** (fixed / recursive / semantic / layout-aware) |

## M4 — RAG
| We said | Industry term |
|---|---|
| retrieve then answer from it | **RAG (Retrieval-Augmented Generation)** |
| answer only from retrieved text | **grounding / grounded generation** |
| generate query variants, fuse | **multi-query / RAG-Fusion** |
| embed a fake answer to search | **HyDE** |
| split a complex question | **query decomposition** |
| cache answers for similar queries | **semantic caching** |
| fetch cheap, then re-score | **two-stage retrieval + reranking** |
| separate encode + compare | **bi-encoder** |
| encode query+doc together → score | **cross-encoder** (the reranker) |
| model ignores a mid-context chunk | **"lost in the middle"** |

## M6 — Evaluation
| We said | Industry term |
|---|---|
| test set with known answers | **golden dataset / eval set** |
| did the right chunk come back | **recall@k / hit@k** (also MRR, nDCG) |
| did we retrieve all needed chunks | **context_recall** (built as hit@k) |
| are retrieved chunks relevant, ranked high | **context_precision** |
| answer supported by context | **faithfulness** (built) |
| answer addresses the question | **answer_relevancy** |
| these 4 together | **RAGAS metrics** (retrieval: recall+precision · generation: faithfulness+relevancy) |
| robot grader | **LLM-as-judge** |
| answer sticks to context | **faithfulness / groundedness** |
| answer addresses the question | **answer relevancy** |
| check judge vs humans | **judge calibration / meta-evaluation** |
| tests that catch quality drops | **regression testing / eval-in-CI** |

## Tools to name (concept first, tool as "e.g.")
- **RAGAS** — standard RAG eval metrics.
- **LangChain / LangGraph** — app + agent orchestration (our lab uses these).
- **Vector DBs** — pgvector, FAISS, and SAP's **HANA Cloud Vector Engine** (M11).
- **Rerankers** — cross-encoder models (e.g. Cohere Rerank, bge-reranker).
