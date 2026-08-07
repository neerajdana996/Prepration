# Round 2 — Tech Coding practice

**Aug 6, 2026 · 2 PM IST · Jerin Ittoop + Lakshmi Shashanka (Technical Leaders)**
Harder coding + "why" / tradeoffs. Run any file with: `node round2/<file>.js`

## How we work
You code step by step in each file → run it → I review like an interviewer:
correctness · edge cases · time/space complexity · "how would you test/scale it."

## The plan (in order)
1. **LRU cache** — `lru-cache.js` — Map version, then HashMap + Doubly Linked List (O(1) get/put)
2. **EventEmitter** — `event-emitter.js` — subscribe/emit/release, then `once`, then bidirectional (subscriber↔events)
3. **Dual-list build** — in the React playground `/machine-coding` — rebuild for speed
4. **JS advanced concepts** — `js-concepts/` (one file each):
   - `debounce-throttle.js`
   - `curry-memoize.js`
   - `deep-clone.js`
   - `promise-utils.js` (Promise.all/allSettled/race polyfill, promisify, retry, concurrency limiter)
   - `bind-call-apply.js` (polyfills)
   - `flatten.js`, `event-loop.js` (output prediction)
   - `this-new-prototype.js`

## Room habits (say these out loud)
clarify inputs/edges → think aloud → **runnable** code → state complexity → edge cases → "how I'd test/scale it"
