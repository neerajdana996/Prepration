# Cisco Interview — Day-Of Question Bank

**Aug 4, 2026 · 2:00 PM IST · Webex · Vinuta Patankar + Sharath Bangera (2 SWEs) · 60 min**
Loop: **2 coding rounds + 1 AI (code-with-AI-tools) round + manager round.** Tomorrow = coding round 1.
Platform: expect CoderPad/HackerRank shared editor over Webex. **Write runnable code, think aloud, clarify first.**

Legend: ⭐ = highest probability · 🔧 = be ready to code it live

---

## 1. JavaScript internals (⭐ very likely)
- ⭐ Output ordering: `console.log` + `setTimeout` + `Promise.then` — what order & why (event loop, micro vs macro).
- ⭐ Microtask vs macrotask; does the loop drain all microtasks before a macrotask? (yes)
- ⭐ `async/await` output prediction; what does `await` defer? (rest of fn → microtask)
- ⭐ Closures — define one; the `var` vs `let` loop with `setTimeout` (3 3 3 vs 0 1 2).
- ⭐ `this`: implicit/explicit/new/default + arrow (lexical). Predict `this` in nested regular fn vs arrow.
- `call` vs `apply` vs `bind`.
- Promises: 3 states; `Promise.all` vs `allSettled` vs `race` vs `any`.
- Hoisting: `var`/`let`(TDZ)/function declarations; function declaration vs expression.
- Reference vs value (object assign-by-reference; shallow vs deep clone; `structuredClone`).
- GC: mark-and-sweep + reachability; 4 leak sources (timer, listener, detached DOM, unbounded cache) + fixes.
- 🔧 Implement: `debounce`, `throttle`, `Promise.all` polyfill, deep clone, `curry`.

## 2. React (⭐ very likely)
- ⭐ Render vs commit; is `setState` synchronous? (schedules; batched); functional updater `setX(x=>…)`.
- ⭐ Reconciliation: virtual DOM = JS object tree (not a screenshot); diff by `type` + `key`.
- ⭐ Keys: why needed; index-key bug (state binds to slot not item) — explain + fix.
- ⭐ `useEffect`: deps array, cleanup, when NOT to use it (derived data / event logic → don't).
- ⭐ Stale closure bug (setInterval logging old value) + 2 fixes (deps / ref / functional update).
- `useMemo` vs `useCallback` vs `React.memo` — what each memoizes; `useCallback` pointless without memo child.
- `useRef` vs `useState` (silent vs re-render); DOM ref; latest-value ref.
- Context: what it is (transport, not state mgr); re-render trap; `useMemo` value + split contexts; no selectors.
- Derived state anti-pattern (compute in render, don't store).
- Custom hooks; "how do hooks work under the hood" (call-order slots).

## 3. Machine-coding / build-a-component (🔧 — the round is often won here)
- ⭐🔧 **The Cisco flagship:** merge two mock student APIs (name/marks/registrationId, with dupes) → dedupe by id → **dual-list transfer UI** (checkboxes, move both directions). *(You built this.)*
- 🔧 Pagination in React (Splunk-confirmed) / **infinite scroll** with IntersectionObserver.
- 🔧 Autocomplete/typeahead (debounce + keyboard nav + a11y).
- 🔧 Accessible nested tree-view / network-checkboxes (ARIA roles, arrow-key nav).
- 🔧 Todo, data-table with sort, star rating, modal/accordion, carousel.
- ⚠️ Runnable code, not pseudocode. Clarify inputs/edges first. Handle loading + error + empty.

## 4. State management (from your research — ⭐ for this team)
- ⭐ Context vs Redux — when each? (Context = low-freq global; Redux = complex client state + selectors.)
- What does Redux give that Context can't? (selectors / granular re-renders, DevTools, middleware.)
- Client state vs server state — why server data needs RTK Query / React Query (cache, dedup, invalidation).
- RTK: `createSlice`, Immer, memoized selectors (`createSelector`), `createAsyncThunk`.
- RTK Query: `isLoading` vs `isFetching`, cache invalidation via tags, dedup, streaming via `onCacheEntryAdded`.
- Zustand/Jotai as lighter selector-stores (nuance).

## 5. Frontend system design (⭐ — your team is Industrial IoT)
- ⭐ **Design a real-time IoT/Catalyst device dashboard** syncing live state across sessions. *(You designed + built this.)*
  - Requirements→architecture→data/state→real-time→optimize.
  - Transport: **WebSocket vs SSE vs polling** (SSE for one-way telemetry; justify).
  - Scoped subscriptions (don't stream all 10k), delta patching, batching updates.
  - Virtualization / infinite scroll for thousands; server-side filtering; URL for shareable filters.
  - Reconnect + backoff + stale banner + since-cursor resync.
- Improve eBay/Uber frontend; monorepo vs micro-frontend (build-time vs run-time tradeoffs).
- Performance: memoization, code-splitting, CDN, critical rendering path, web workers.

## 6. Browser / CSS / a11y
- ⭐ "What happens when you type a URL and hit enter?" (end-to-end).
- Critical rendering path; CSR vs SSR vs SSG (Next.js).
- Responsive / media queries; i18n/localization; web workers; HTTP content-types; CDN.
- Accessibility: ARIA roles, keyboard nav, labels; a11y for the tree/table.

## 7. DSA (⭐ 1–2 in the coding round, easy→medium)
- ⭐ Valid Anagram (242); 3rd-largest element; reverse words in a string; string permutations.
- ⭐ Best Time to Buy/Sell Stock (121/122); Coin Change (322, DP); Maximum Subarray (53).
- Merge two sorted arrays (asked Sept 2025); Merge K sorted (min-heap); reverse linked-list in k-groups.
- Sort 0s/1s/2s; Number of Islands (AppDynamics).
- Senior may get one DP / tree / recursion.

## 8. Java (⭐ 2nd interviewer may own this)
- HashMap vs Hashtable vs ConcurrentHashMap; WeakHashMap; `int` vs `Integer`.
- Immutable class — how to build; String pool (`s = s + "x"`); deep copy.
- ⭐ Concurrency: object vs class-level locking (`synchronized`); Callable vs Runnable; **print odd–even with 2 threads**; producer–consumer; deadlock/semaphore.
- Java 8: Predicate vs Supplier vs Consumer vs Function; streams/lambdas.
- Spring Boot: `ResponseEntity`; `@ControllerAdvice`; `@Transactional`; bean lifecycle/IoC/DI; Filter vs Interceptor; write a REST GET controller.
- JWT session expiration across frontend + Java interceptors (Duo/security angle).
- API rate limiter — sliding-window algorithm.
- SQL: 2nd/3rd-highest salary; PreparedStatement vs Statement; indexing; SQL vs NoSQL.

## 9. Cisco-domain wildcard (basic only — recruiter said NO routing/switching)
- Be conversant: **platform, controller, site, edge device, real-time device state** (Industrial IoT).
- Light networking: TCP vs UDP; what is DNS/NAT (conceptual); how a device talks to a controller.
- 🔧 Possible: check if an IP belongs to a subnet (bitwise `ip & mask`).

## 10. Behavioral (manager round; opener may appear tomorrow)
- ⭐ "Walk me through your resume / tell me about yourself" (~90s).
- ⭐ **"Why leaving so soon?"** — the stability narrative (post-layoff → seeking stability + IC growth + relocation-ready; ServiceNow→Atlassian was a family/remote reason). Keep positive, brief.
- "Disagreed with your manager / a backend architect on payload structure" — disagree-and-commit; land a result.
- Tech debt (Webpack/Babel upgrade) vs feature deadlines — prioritization framework.
- "Why Cisco?"; hardest bug; an architecture decision you drove.
- Know your own projects cold (CV deep-dive is intense at Cisco).

## 11. The AI round (later, not tomorrow)
- They watch HOW you drive an AI assistant: prompt with context/constraints, **review every line**, catch hallucinations (your JS/React foundation is the bug-detector), test it, iterate with precise feedback, know when to skip AI. Soundbite: *"I use AI to go faster on what I understand, and I catch what it gets wrong — I never ship code I can't explain."*

---

## Golden rules for the room
1. **Clarify before coding** (inputs, edge cases, expected output).
2. **Think out loud** — they grade reasoning; they help when you're stuck.
3. **Runnable, debuggable code** — never pseudocode you can't run.
4. **Know your own projects to the metal.**
5. Ask early: *"Optimize for a working component or algorithmic depth?"*
6. Prepare 3 questions for Vinuta & Sharath.
