# Google L5 Coding — Triage Prep Plan

**Situation:** ~2–4 weeks, fixed date. Starting point: "rarely finish a fresh medium cold."
**Goal of this plan:** maximize odds of passing the DS/Algo screening.
**Strategy:** NOT volume. A small set of the highest-frequency patterns, drilled until re-derivable cold, wrapped in one repeatable problem-attack framework. Depth > volume. A problem only "counts" when you can re-derive it from scratch the next day.

Coding language: **Python**. Bar to build toward: medium in 15–20 min, ~0 hints, talk-and-code, plain text editor.

---

## THE MINDSET: the 5-step attack (run this on EVERY problem)

This is the actual skill. The patterns below are just vocabulary; this is how you *use* it.

1. **Restate + tiny example.** Say what it's asking in your own words. Hand-build a 5–8 element example and the expected answer. (If you can't, you don't understand the problem yet.)
2. **Brute force + its cost.** Always have a baseline. State its time/space out loud. You're allowed to be dumb here.
3. **Find the waste.** Look at the brute force and ask: *what work am I repeating?* (re-scanning? re-sorting? recomputing sums?) The waste points at the pattern.
4. **Match signal → tool (CHECK THE PRECONDITION).** Name the pattern from the cheat sheet below — then verify its precondition actually holds before you commit. This is your #1 trap: you grab a recent pattern before checking it fits.
5. **Code small, test on the tiny example, state complexity.** Walk your own example through the code by hand. Then say final time/space.

> The 3-second check before coding: **"What is this actually asking, and does my tool's precondition match?"**

---

## SIGNAL → TOOL cheat sheet

| The problem says / has… | Reach for… | Precondition to verify |
|---|---|---|
| "how many times", "unique", "duplicate", "anagram" | **count map** (dict) | none — safest default |
| "pair/triple that sums to X" | **lookup map** (seen dict) OR **two-pointer** | two-pointer needs a **SORTED** array |
| "sorted array" + find something | **binary search** | array is sorted (or rotated-sorted) |
| "min/max window", "longest/shortest substring", "at most K" | **sliding window** | contiguous subarray/substring |
| "subarray sum", "range sum" | **prefix sum** | none |
| "next greater/smaller", "valid parentheses" | **monotonic stack** | none |
| "tree", "hierarchy", "levels" | **DFS (recursion)** or **BFS (queue)** | — |
| "grid", "islands", "regions", "shortest steps in grid" | **BFS/DFS on grid** | BFS for shortest, DFS for connectivity |
| "all combinations / subsets / permutations" | **backtracking** | — |
| "top K", "K largest/smallest", "merge K" | **heap** | — |
| "overlapping intervals", "merge", "meeting rooms" | **sort + sweep** | sort by start first |
| "min/max ways", "can I reach", overlapping subproblems | **DP** (start 1D) | optimal substructure + overlap |

---

## THE DAILY LOOP (~2–3 focused hours)

1. **Warm-up (15 min):** re-derive ONE problem you solved a previous day, from a blank screen. If you can't → that's today's real lesson.
2. **New pattern (main block):** I teach it socratically with a tiny picture → you drive a first problem with nudges → then you solve 2–3 more, last one **timed**.
3. **Cooldown (15 min):** write 3–5 Anki cards (trigger / insight / pitfall / complexity). Log which problems you owned vs. struggled in the tracker below.

Realistic target: **4–5 problems/day, quality-gated.** ~25–30/week you actually own > 35 skimmed.

---

## WEEK 1 — Linear patterns + the framework (NON-NEGOTIABLE CORE)

| Day | Pattern | Problems (in order) |
|---|---|---|
| 1 | Framework + Hashing (count/lookup maps) | Two Sum, Contains Duplicate, Valid Anagram, Group Anagrams |
| 2 | Two pointers (converging + fast/slow) | Valid Palindrome, Two Sum II (sorted), 3Sum, Container With Most Water |
| 3 | Sliding window (fixed + variable) | Best Time to Buy/Sell Stock, Longest Substring Without Repeat, Longest Repeating Char Replacement, Min Size Subarray Sum |
| 4 | Binary search (plain + on rotated) | Binary Search, Search in Rotated Sorted Array, Find Min in Rotated, Koko Eating Bananas (BS on answer) |
| 5 | Stacks (monotonic + parens) + Intervals | Valid Parentheses, Daily Temperatures, Merge Intervals, Insert Interval |
| 6 | Linked lists | Reverse Linked List, Linked List Cycle, Merge Two Sorted Lists, Reorder List |
| 7 | Mixed timed review | 4 random problems from Days 1–6, each under time |

## WEEK 2 — Trees, graphs, recursion (Google's flagged weak spots — CORE)

| Day | Pattern | Problems (in order) |
|---|---|---|
| 8 | Recursion + tree traversals (DFS/BFS) | Max Depth, Same Tree, Invert Tree, Level Order Traversal |
| 9 | Tree problems | Diameter of Binary Tree, Balanced Binary Tree, Lowest Common Ancestor (BST), Validate BST |
| 10 | Grid BFS/DFS | Number of Islands, Max Area of Island, Flood Fill, Rotting Oranges |
| 11 | Graphs | Clone Graph, Course Schedule (cycle detect / topo), Pacific Atlantic Water Flow |
| 12 | Backtracking | Subsets, Combination Sum, Permutations, Word Search |
| 13 | Heaps / top-K | Kth Largest Element, Top K Frequent Elements, Merge K Sorted Lists |
| 14 | Mixed timed review | 4 random from Days 8–13, timed |

## WEEK 3 — DP intro + consolidation (if you have the runway)

| Day | Pattern | Problems (in order) |
|---|---|---|
| 15 | 1D DP | Climbing Stairs, House Robber, House Robber II, Coin Change |
| 16 | 1D DP cont. | Longest Increasing Subsequence, Word Break, Decode Ways |
| 17 | 2D DP intro | Unique Paths, Longest Common Subsequence |
| 18 | Greedy + intervals | Jump Game, Non-overlapping Intervals, Meeting Rooms II |
| 19 | Full mock #1 | 2 unseen mediums, 45 min total, talk aloud |
| 20 | Weak-spot repair | re-drill whatever you failed in the mock |
| 21 | Full mock #2 | 2 unseen mediums, 45 min |

**If only 2 weeks:** do Weeks 1 + 2. Skip DP depth — instead spend 30 min learning to *recognize* DP and write ONE 1D template (Climbing Stairs), so you're not blank if it appears. Do one mock on the last day.

---

## RULES
- **No looking at solutions during the first attempt.** Struggle 10–15 min first — that's where learning happens. Then hint, then solution, then **re-derive it cold next day**.
- **Talk while you code** — Google scores your reasoning, not just the answer. Practice narrating from Day 1.
- **Plain text, no autocomplete.** Practice in a bare editor sometimes.
- Every solved problem → log below + 3–5 Anki cards.

---

## PROGRESS TRACKER
Legend: ✅ own it cold · 🟡 solved with hints · ❌ struggled/reattempt

### Week 1
- [x] Day 1 — Hashing: ✅ two_sum, contains_duplicate, is_anagram, group_anagrams (all cold) + UNSEEN longest_consecutive (O(n), derived solo). Learned: operation→structure bridge, JS→Python gotchas, run-start trick.
- [~] Day 2 — Two pointers: ✅ is_palindrome, two_sum_sorted, max_area (beat the "move shorter wall" trap solo). Learned: converging-2ptr PRECONDITION = sorted; sorted vs unsorted pair-sum fork. HOMEWORK: three_sum (skeleton designed, dedup left to build) + cooldown re-derive longest_consecutive.
- [ ] Day 3 — Sliding window:
- [ ] Day 4 — Binary search:
- [ ] Day 5 — Stacks + Intervals:
- [ ] Day 6 — Linked lists:
- [ ] Day 7 — Mixed timed:

### Week 2
- [ ] Day 8 — Tree traversals:
- [ ] Day 9 — Tree problems:
- [ ] Day 10 — Grid BFS/DFS:
- [ ] Day 11 — Graphs:
- [ ] Day 12 — Backtracking:
- [ ] Day 13 — Heaps:
- [ ] Day 14 — Mixed timed:

### Week 3
- [ ] Day 15 — 1D DP:
- [ ] Day 16 — 1D DP cont.:
- [ ] Day 17 — 2D DP:
- [ ] Day 18 — Greedy:
- [ ] Day 19 — Mock #1:
- [ ] Day 20 — Repair:
- [ ] Day 21 — Mock #2:
