# Cisco Senior UI / Full Stack (React + Java) — Interview Prep Guide

**Interview:** Aug 4, 2026, 2:00 PM IST · 60 min · Webex · Req 2016546
**Panel:** Vinuta Patankar (SWE), Sharath Bangera (SWE) — *two peer engineers, not a manager*
**Role:** Senior UI / Full Stack Engineer (Frontend) | ReactJS & Java, 8–12 yrs · Bangalore/India

---

## 0. What this round actually is

A **60-min peer technical screen** = intro (~5) + technical (~45) + your questions (~10).
Two SWEs almost always split: **one drives JS/React**, the **other Java/CS fundamentals + one coding task**.
This is the FIRST gate. System design + behavioral/HM come in LATER rounds → deprioritize them for Tuesday.

**Priority for 3 days:** (1) React/JS internals rapid-fire · (2) One live coding task (React component OR JS/DSA) · (3) Java fundamentals · (4) light frontend-architecture talking points. Deep distributed-system design = skip.

---

## 1. JavaScript internals — CONFIRMED asked at Cisco (highest yield)

- **Event loop / call stack / task queue / microtask (Promise) vs macrotask (setTimeout)** — most consistently reported. Be able to predict output ordering.
- **Closures + hoisting + scope** — "tricky" output-prediction questions. TDZ, `var` vs `let` in loops.
- **Promises vs async/await** — *implement*, not just explain. Know `Promise.all/race/allSettled`.
- **OOP in JS** — inheritance, abstraction (theory + code).
- **`this` binding, call/apply/bind** — `.call` vs `.apply` explicitly asked (Splunk).
- Likely (senior fare, prep as hedge): **debounce/throttle**, **polyfill Promise.all / Array.map / bind**, **deep clone**, **currying**, prototype chain.

## 2. React — CONFIRMED + expected

- **Context API + reducers** (asked directly)
- **SSR vs CSR vs SSG** (Next.js framing) + **Critical Rendering Path**
- **React design patterns** (HOC, render props, compound components)
- Expected at senior level: **hooks internals, useEffect cleanup + dependency gotchas, reconciliation/virtual DOM, React.memo/useMemo/useCallback** — prep these even though not name-confirmed.

## 3. Machine-coding — THE flagship Cisco task (drill this most)

**The recurring Cisco React problem:**
> Create **2 mock APIs**, each returning a list of students `{name, marks, registrationId}`. The two lists can contain **duplicate students**. Fetch both (Promises), **merge + de-duplicate**, then render a **dual-list / transfer UI**: checkboxes + move selected students between two boxes (bidirectional).

Bundles: async fetch, Promise handling, dedupe logic, list state, controlled checkboxes. **Build this from scratch, twice.**

Other high-probability build tasks: **pagination in React** (Splunk-confirmed), **autocomplete/typeahead** (debounce + keyboard nav), **todo**, **data table w/ sort**, **star rating**, **modal/accordion**.
⚠️ **Write runnable, debuggable code — NOT pseudocode.** Candidates lost offers for pseudocode they couldn't run.

## 4. CSS / browser — CONFIRMED

Media queries / responsive · **i18n/localization** · **web workers** · HTTP **Content-Types** · **Critical Rendering Path** · **"what happens when you type a URL"** · **a11y / ARIA** · CDN.

## 5. DSA in the FE loop — CONFIRMED (budget real time)

Even "frontend" rounds include **1–2 LeetCode easy→medium**. Reported/named:
- 3rd-largest element in array · **Valid Anagram (242)** · string permutations · reverse words in string
- **Best Time to Buy/Sell Stock (121/122)** · **Coin Change (322)** DP · merge two sorted arrays (asked Sept 2025)
- Sort 0s/1s/2s · Maximum Subarray (53)
Senior candidates can get one **DP/tree/recursion**. Platform: **CoderPad/HackerRank over Webex.**

## 6. Java — CONFIRMED (the 2nd interviewer may own this)

- **HashMap vs Hashtable vs ConcurrentHashMap**; WeakHashMap
- **`int` vs `Integer`** memory; **immutable class** — how to build; deep copy
- **String pool**: `s1 = "ABC"; s1 = s1 + "xyz"` — explain
- **Concurrency (high freq):** object-level vs class-level locking (`synchronized`); Callable vs Runnable; process vs thread; deadlock/starvation/semaphore; **print odd–even with two threads**; producer–consumer
- **Java 8:** Predicate vs Supplier vs Consumer vs Function; streams/lambdas
- **Spring Boot:** `ResponseEntity`; `@ControllerAdvice` global exceptions; bean lifecycle / IoC / DI; `@Transactional`; Filter vs Interceptor; write a REST GET controller w/ query param
- **DB:** PreparedStatement vs Statement; primary vs unique key; indexing; SQL vs NoSQL; **2nd/3rd-highest salary** query

## 7. Frontend system design — LIGHT prep (probably a later round, but be ready to talk)

If it comes up in a 60-min peer round it'll be conceptual, not a full design:
- "Improve eBay's frontend" / "design Uber's frontend + its shortcomings"
- Talking points: **RADIO** framework; debounce + **AbortController** cancellation; **LRU/prefix cache** for autocomplete; **virtualization/windowing**; optimistic updates; normalized client store; CDN/image opt[.
- ⚠️ In an FE design round, keep the server a black box — don't drift into DB sharding.

## 8. Behavioral opener — 2 min prep

Have a crisp **"walk me through your resume / tell me about yourself"** (~90s) and **know your own projects cold** (why this DB, hardest bug, rendering strategy, what you'd do differently). Cisco probes **"disagreed with your manager"** (tests disagree-and-commit). Save deep STAR prep for the HM round.

---

## 3-DAY DRILL SCHEDULE (Sat Aug 1 → Tue Aug 4, 2 PM)

### SAT (Aug 1) — Machine-coding + JS internals (~5–6h)
- **AM:** Build the **student-merge + dual-list transfer** component from scratch (no notes). Then rebuild it faster. This is your #1 asset.
- **PM:** Build **autocomplete w/ debounce** + **pagination in React**. Then JS output-prediction drills: 15 event-loop / closure / hoisting snippets.

### SUN (Aug 2) — JS/React deep-dive + DSA (~5–6h)
- **AM:** Implement debounce, throttle, `Promise.all` polyfill, deep clone, curry. Write React notes: Context+reducer, useEffect cleanup, memo/useMemo/useCallback, reconciliation, SSR/CSR/SSG.
- **PM:** DSA in CoderPad-style env: Valid Anagram, 3rd largest, Best Time Buy/Sell Stock, Coin Change, merge two sorted arrays, reverse words. Time-box 20 min each, **code out loud, runnable**.

### MON (Aug 3) — Java + browser + mock (~4–5h)
- **AM:** Java flashcards (Section 6). Code: immutable class, odd–even two threads, a Spring REST GET controller, 2nd-highest-salary SQL.
- **PM:** Browser/CSS talking points (Section 4). One **timed 45-min mock**: 10 min JS/React Q&A + 30 min build a component + 5 min DSA. Prep 3 questions to ask Vinuta & Sharath.

### TUE (Aug 4) — Interview day
- **Morning (light):** re-skim this guide + re-read your resume projects. Rebuild the dual-list component once for muscle memory. Test Webex + camera + a scratch CoderPad/CodeSandbox. Don't cram new topics.

---

## Golden rules for the room
1. **Think out loud** — repeatedly cited; interviewers help you when stuck and grade reasoning.
2. **Runnable code, not pseudocode.** Actually run it.
3. **Clarify before coding** (inputs, edge cases, expected output).
4. **Know your own projects to the metal** — CV deep-dives sink thin answers.
5. Ask the panel early: *"Should I optimize for a working component or algorithmic depth?"* — tells you which way to steer.

---

## Honesty caveat on the research
Richest question-level data is 2023–2025; no verified Feb–Aug 2026 Cisco FE writeup exists publicly. Treat the *specific questions* as directional patterns (high recurrence across sources), not a guaranteed script. The loop is high-variance by team/interviewer.
