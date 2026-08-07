# Cisco Prep — User's Research Questions, Mapped

These are questions the user surfaced from their own research (LinkedIn, Prepfully, AmbitionBox, Glassdoor, GreatFrontend). Mapped to our ladder/tracks with a drill method for each. Several reference Cisco products (Catalyst Centre, IoT, edge devices, L2 switching) — treat networking + real-time dashboard design as HIGHER priority than a generic FE loop.

Legend: 🔴 P1 (drill hard) · 🟣 P2 (know cold) · 🟢 P3 (talk fluently)

---

## Track A — Advanced React & JS internals  🔴
Extends rungs 1 (heap), 4 (closures), 6 (render), 7 (hooks). New mini-rung **7.5: performance & memory**.

| # | Question | Belongs to | How we drill |
|---|----------|-----------|--------------|
| A1 | JS garbage collection under the hood; how persistent closures / uncleaned event listeners leak memory | Rung 1 (heap) + Rung 4 (closures) + Rung 7 (cleanup) | Teach mark-and-sweep + reachability; I quiz you on 3 leak sources and the fix for each (removeEventListener, clear timers, effect cleanup, null detached refs) |
| A2 | Chrome DevTools: Heap Snapshots + Performance tab to find detached DOM nodes in a laggy React app | New: DevTools drill | 5-step walkthrough script you can recite; I quiz the sequence |
| A3 | `useMemo` vs `useCallback` exact difference; protect a heavy data-grid from stream re-renders | Rung 7.5 | Teach memo/useMemo/useCallback + React.memo; build a memoized grid row; quiz the "which one for a function vs a value" |
| A4 | Design a reusable custom hook to fetch massive datasets — error states, no stale deps, cancellation | Rung 7.5 + Rung 8 | LIVE BUILD a `useFetch(url)` with AbortController, loading/error/data states, cleanup. High machine-coding value |

## Track B — Frontend system design & UI components  🟣 (raised from 🟢)
New **Rung 9: FE system design**. Cisco-flavored.

| # | Question | Belongs to | How we drill |
|---|----------|-----------|--------------|
| B1 | Architect a real-time monitoring dashboard (IoT Catalyst Centre) syncing live device state across sessions | Rung 9 | RADIO framework + WebSocket/SSE vs polling, normalized store, optimistic UI, reconnection/backpressure. I play interviewer, you whiteboard aloud |
| B2 | Build an accessible, keyboard-navigable nested tree / network-checkboxes (ARIA compliant) | Rung 8 (build) + a11y | Live build a tree-view: roles (tree/treeitem), arrow-key nav, aria-expanded, focus management |
| B3 | Monorepo vs micro-frontend for a Cisco enterprise suite; build-time vs run-time tradeoffs | Rung 9 (talk) | Memorize a 6-point tradeoff table; 90-sec verbal answer |

## Track C — Java backend & full-stack integration  🟣
Java track. Second interviewer likely owns this.

| # | Question | Belongs to | How we drill |
|---|----------|-----------|--------------|
| C1 | OOP: runtime vs compile-time polymorphism; multi-threaded payload transformation | Java core + concurrency | Flashcards: overriding(runtime) vs overloading(compile); ExecutorService for parallel transforms; quiz |
| C2 | Securely handle JWT session expiration across frontend state + Java interceptors | Java + security (Duo-relevant) | Teach access/refresh token flow, 401→refresh, HttpOnly cookie vs localStorage, Spring interceptor; quiz the refresh race |
| C3 | Design an API rate limiter using sliding-window algorithm | LLD / system design | Teach fixed-window vs sliding-window-log vs sliding-window-counter vs token bucket; you code sliding-window-counter |

## Track D — DSA & networking  🟣
DSA track + Cisco networking wildcard.

| # | Question | Belongs to | How we drill |
|---|----------|-----------|--------------|
| D1 | Verify if an IP address belongs to a subnet/mask | DSA + networking | Teach bitwise (ip & mask == network & mask); you code it. Networking + coding in one |
| D2 | Merge K sorted arrays with a min-heap | DSA | Teach heap approach O(N log K); you code with a priority queue |
| D3 | Reverse linked-list fragments (reverse in k-groups) | DSA | Pointer manipulation drill; you code |
| D4 | TCP vs UDP, NAT, MAC learning in L2 switches | Networking (oral) | One-page fact sheet + rapid oral quiz |

## Track E — Behavioral  🟢
Prep 2 STAR stories; reuse for many prompts.

| # | Question | How we drill |
|---|----------|--------------|
| E1 | Disagreed with a backend architect on payload structure — how you negotiated normalization to keep UI snappy | Build one STAR story (~90s): situation, the conflict, disagree-and-commit, measurable result |
| E2 | Prioritizing structural tech debt (Webpack/Babel upgrade) vs urgent feature deadlines | Build one STAR story on tradeoff/prioritization framework (impact × effort × risk) |

---

## Suggested order for the remaining time (interview Tue Aug 4)

Given ~3 days and the 60-min peer format, priority sequence:
1. **Finish JS/React foundation drills** (rungs 3–7 top-5) — nearly done
2. **Rung 7.5 performance/memory** (A1–A3) — high frequency, fast wins
3. **Rung 8 the dual-list build** (the flagship task) + A4 useFetch + B2 tree-view
4. **Track C Java top-5** (C1–C3) — second interviewer
5. **Track D**: code D1 (subnet, ties coding+networking) + D4 fact sheet; D2/D3 if time
6. **Rung 9 FE system design** B1 + B3 — talk-through, not build
7. **Track E behavioral** — 2 STAR stories, 20 min the night before

Cut list if time runs out: D2/D3 (heavy DSA), B3 (micro-frontends) — keep only if 1–6 are solid.
