# Frontend Mastery — Roadmap (foundation-first)

**Target:** dedicated frontend interview rounds at the Staff/Principal bar (full D3).
**Approach:** bottom-up ladders, taught live & Socratic (one idea → checkpoint → learner drives),
heavy on SVG / interactive `show_widget` visuals and handwritten-notebook summaries.

> NOTE (2026-07-29): the git working tree was reset twice (session start + mid-session), wiping
> uncommitted `Topics/Frontend/` files. **COMMIT this folder to preserve it.** Detailed live progress
> also lives in the persistent memory file `frontend-mastery-track.md`.

## Overall trajectory
1. **Building blocks** — browser + performance spine (F0–F5) ✅, then CSS, then JS.
2. **JavaScript in depth** (current phase) — J0–J8 fundamentals, then an Applied/Advanced/Machine-coding tier.
3. **React in depth** — a later topic once JS is solid.

## Browser + performance spine (F0–F5) — ALL DONE ✅
- **F0** one main thread; "blocking the main thread"; script in `<head>` vs end-of-`<body>`; async/defer.
- **F1** HTML→DOM parse (bytes→chars via charset 1024-byte prescan→tokens→nodes→tree; parser tolerance);
  the entire `<head>`/meta tags (charset, viewport+vw/vh/dvh+100vh trap, title, theme-color,
  stylesheet=render-blocking; description/robots/canonical/OG/Twitter; dns-prefetch/preconnect/preload/prefetch);
  semantic HTML (`<button>` vs `<div onclick>`, landmarks, a/vs/button, headings, section vs div);
  CSS→CSSOM→render tree (display:none out, visibility:hidden stays, opacity:0 stays+clickable).
- **F2** rendering pipeline: layout→paint→composite; the **cost ladder** (geometry=reflow>color=repaint>
  transform/opacity=composite); layers-as-sheets; why transform/opacity are cheap.
- **F3** layout thrashing via the **dirty-flag** model (read forces reflow only if a write dirtied first;
  fix = read-phase then write-phase); `will-change` = GPU layer but costs memory; DevTools Performance.
- **F4** critical rendering path (render-blocking = CSS + sync JS); **Core Web Vitals**: LCP (loading ≤2.5s),
  CLS (stability ≤0.1, fix=img width/height), INP (responsiveness ≤200ms = F0 main-thread blocking; replaced FID).
- **F5** runtime perf: event loop (perf level), ~16ms frame budget, long task >50ms; chunk+yield, Web Worker,
  virtualize, debounce/throttle, requestAnimationFrame.
- Quizzes: F0+F1 → 84%; F4+F5 → 84%. Made a 6-image F0–F3 reference deck + F0–F5 handwritten notes.

## CSS ladder (C0–C8) — PAUSED at C5 (C6–C8 deferred as a later top-up)
- **C0 · How CSS works** ✅ — cascade, specificity `(IDs,classes,elements)`, inheritance, `!important`.
- **C0.5 · Selectors in depth** ✅ — identity; combinators (descendant/`>`/`+`/`~`); attribute (`^`/`$`/`*`);
  pseudo-classes = "virtual class the browser toggles" (state/structural/form/logical); pseudo-elements
  (`::` = a part / generated content). The `:` vs `::` distinction (was the pain point) is now solid.
- **C1 · Box model** ✅ — content/padding/border/margin; content-box vs border-box + width math; margin collapse.
- **C2 · Display & normal flow** ✅ — block vs inline (ignores w/h) vs inline-block; inline-block whitespace gap.
- **C3 · Positioning & stacking** ✅ ★ — static/relative/absolute/fixed/sticky; absolute→nearest positioned
  ancestor; z-index only on positioned; **stacking contexts** trap inner z-index (opacity/transform/will-change
  create them); fix modal-behind-X by portaling to `<body>`.
- **C4 · Flexbox** ✅ — main/cross axis; justify-content(main)/align-items(cross); center 3-liner;
  flex-direction:column swaps axes; `flex:1` grow / `flex:0 0 Npx` fixed; gap; flex-wrap; all props shown live.
- **C5 · Grid** ✅ — display:grid; grid-template-columns+`fr`; `repeat(auto-fit,minmax())` responsive;
  spanning (`grid-column:1/3` or `span 2`); grid-template-areas; flex=1D vs grid=2D, they compose.
- **C6 · Sizing & units** ⬜ (deferred) · **C7 · Responsive** ⬜ · **C8 · Modern CSS** ⬜
- Quiz: C0 + selectors (HARD) → 87% (only miss: `:is()` = most-specific-arg specificity vs `:where()` = 0).

## JavaScript in depth (J0–J8)
- **J0 · How JS runs** ✅ — single-threaded; call stack push/pop LIFO + stack overflow; value vs reference
  (primitives by value, objects shared; mutate = shared vs reassign = breaks link).
- **J1 · Scope, hoisting & closures** ✅ ★ — lexical scope; var=function-scoped/leaks vs let/const=block-scoped;
  hoisting: var→undefined, let/const→TDZ, fn decls fully hoisted; closures = remember defining scope, each call
  fresh; the var-in-loop bug 3,3,3 vs let 0,1,2.
- **J2 · `this` & function binding** ✅ ★ — this = HOW called not where written; 5 rules (new > explicit(call/apply/bind)
  > implicit(obj.dot) > default(undefined)); arrow = lexical this from nearest ENCLOSING FUNCTION (object literal
  is not a function → arrow-as-method looks to global; arrow-inside-method inherits the method's this=obj);
  call=comma / apply=array / bind=new fn later + partial application.
- **J3 · Objects & prototypes** ✅ — every obj has __proto__; lookup walks UP to null; `Constructor.prototype` =
  shared-methods obj, `new` sets instance.__proto__ = Constructor.prototype (methods live ONCE, shared);
  class = sugar (methods→prototype, extends→chain); instanceof = "is Fn.prototype in the chain"; hasOwnProperty vs for...in.
- **J4 · Types, coercion & equality** ⬜ (DEFERRED — user jumped to J5; circle back).
- **J5 · The event loop** ✅ ★★ — sync → drain ENTIRE microtask queue (incl. ones added during the drain) →
  ONE macrotask → repeat; micro = Promise.then / await-continuation / queueMicrotask, macro = setTimeout/events/IO;
  microtasks always before the next macrotask; `await X` runs X SYNC then schedules the rest as a microtask.
  Nailed traces: 1 4 3 2 · A E C D B · 1 2 4 7 3 6 5 · 4 1 3 5 2.  ← last completed
- **J6 · Promises & async/await** ✅ ★ — 3 states (pending→fulfilled/rejected, frozen once settled); .then chaining
  (return value passes on / return promise waits / throw skips to .catch; a .catch that doesn't re-throw HEALS the
  chain so later .then runs); combinators: all (all resolve→results[], fail-fast) / allSettled (waits all, never
  rejects, [{status,value|reason}]) / race (first to settle) / any (first resolve, else AggregateError); losers of
  race/all are NOT cancelled (promises aren't cancellable) → real request keeps running; async fn returns a promise,
  try/catch for errors, sequential await (slow) vs Promise.all (parallel). Built `withTimeout` (Promise.race) +
  AbortController for real cancellation.
- **J7 · Memory & GC** ✅ — auto GC by **reachability**; mark-and-sweep from roots (handles cycles, unlike ref-counting); object survives while ANY reference remains; leak sources = forgotten timers, detached DOM still referenced, listeners not removed, unbounded caches (all = "reachable longer than needed"); `WeakMap`/`WeakSet` hold keys weakly → don't block GC → leak-free object-keyed caches. Nailed the setInterval-closure leak.
- **J8 · Modules & iterators/generators** ⬜ — ESM vs CJS, generators.

**Machine coding built so far:** principal-grade `Function.prototype.bind` polyfill (closures + this + new-handling
via `this instanceof bound` + prototype linking).

## Applied, advanced & machine-coding JS (Principal depth — after J-fundamentals)
- **DOM APIs**, **Events deep** (capture→target→bubble, delegation, custom events, passive), **JS performance**,
  **Concurrency & parallelism** (event loop deep, Web Workers, SharedArrayBuffer/Atomics, AbortController),
  **Modules & tooling** (ESM, bundlers, **tree shaking**, code splitting),
  **Machine coding** (production task/todo app; Redux-by-hand; event emitter; promise polyfill; debounce/throttle;
  once; memoize; deep clone). NOTE: machine coding is now IN scope (user requested; Apple + Principal bar).

## Interview-signal research (Stage 0.25) — regenerate if lost
Three `INTERVIEW-SIGNAL.md` (Browser Internals & Web Performance=15 themes; JavaScript Language & Runtime=14;
CSS, Layout & Accessibility=18) + `APPLE-FRONTEND-SIGNAL.md` (12 themes). Apple signal: team-dependent, no central
bank; strongest = CSS to D3, vanilla-JS + DOM component building, semantic HTML + a11y/focus; style = "explain
exactly what this does and why". (These files were wiped with the working tree — regenerate on request.)

## React in depth
A new topic to create under `Topics/Frontend/React…` once the JS phase is solid.
