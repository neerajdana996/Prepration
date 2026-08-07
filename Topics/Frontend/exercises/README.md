# Frontend Machine-Coding Exercises

Practice reps for **closures, `this`, promises, recursion** — the vanilla-JS utilities that show up
in Staff/Principal & Apple-style machine-coding rounds. Built live on 2026-07-29.

## How to use (spaced repetition)
1. Read the **prompt** comment at the top of each file.
2. **Cover the `--- SOLUTION ---` section and write your own first.**
3. Compare, note what you missed, and re-do the file a few days later.

## The reusable skeleton (most of these share it)
```js
function wrapper(fn /*, config */) {
  // 1. closure state:  flag / timer / lastTime / cache
  return function (...args) {     // REGULAR function → forwards `this`
    // 2. logic (guard / debounce / throttle / cache)
    return fn.apply(this, args);  // 3. call original, forwarding this + args
  };
}
```
**Recurring lesson:** the wrapper must be a *regular* function (not an arrow) so `this` reaches the
caller. `once` / `debounce` / `throttle` / `memoize` are just different **state + logic** in this shell.

## Exercises
| # | File | Skill drilled |
|---|------|---------------|
| 01 | `01-once.js` | closure flag (private state) |
| 02 | `02-debounce.js` | closure + timer (reset each call) |
| 03 | `03-throttle.js` | closure + timestamp (rate limit) |
| 04 | `04-memoize.js` | closure cache (Map) + arg keys |
| 05 | `05-event-emitter.js` | Map of listeners; on/emit/off/once |
| 06 | `06-deep-clone.js` | recursion + WeakMap for cycles |
| 07 | `07-promise-polyfill.js` | **capstone** — closures + this + microtasks + promise semantics |

## Concept behavior quizzes — `concepts/` (100 "predict the output" Qs, click-to-reveal)
`closures.md` · `event-loop.md` · `arrow-functions.md` · `pure-functions.md` · `garbage-collection.md` — 20 each.

## Coming next (to add)
`curry` · array `flatten` · vanilla task app · Redux-by-hand.
</content>
