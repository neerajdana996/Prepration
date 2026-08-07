# JavaScript: Garbage Collection & Memory

Predict GC eligibility / spot the leak. Attempt each first, then click to reveal the answer!

JavaScript GC is based on **reachability**: an object is eligible for collection when it can no longer be reached from a *root* (global object, the current call stack, active closures). Modern engines use **mark-and-sweep**, so unreachable *cycles* are still collected (unlike naive reference-counting).

---

## Questions

**1.**
```js
function f() {
  let obj = { name: "temp" };
  return obj.name;
}
f();
```
After `f()` returns, is the `{ name: "temp" }` object eligible for garbage collection? Why?

<details>
<summary>Show answer</summary>

**Yes, eligible.** Once `f()` returns, its scope is gone and nothing holds a reference to the object — only the primitive string `"temp"` was returned (a copy), not the object. It is unreachable from any root.

</details>

**2.**
```js
let a = { big: new Array(1000000).fill(0) };
a = null;
```
After the reassignment, is the original array object eligible for GC? Why?

<details>
<summary>Show answer</summary>

**Yes, eligible.** `a` was the only reference to the object holding the array. Setting `a = null` makes both the wrapper object and its big array unreachable, so both can be collected.

</details>

**3.**
```js
let x = { id: 1 };
let y = x;
x = null;
```
After `x = null`, is the `{ id: 1 }` object eligible for GC? Why?

<details>
<summary>Show answer</summary>

**No, not eligible.** `y` was assigned the same reference, so after `x = null` the object is still reachable via `y`. An object stays alive while *any* reference remains. Null `y` too, and it becomes collectible.

</details>

**4.**
```js
let user = { name: "Ada" };
globalThis.currentUser = user;
user = null;
```
After `user = null`, is the object eligible for GC? What keeps it alive?

<details>
<summary>Show answer</summary>

**No, not eligible.** `globalThis.currentUser` still points to it, and the global object is a GC root — so the object stays alive regardless of `user` being nulled. Fix: `globalThis.currentUser = null` (or `delete`) when done.

</details>

**5.**
```js
let a = {};
let b = {};
a.partner = b;
b.partner = a;
a = null;
b = null;
```
The two objects reference each other in a cycle. After both `a` and `b` are nulled, are they eligible for GC? Why?

<details>
<summary>Show answer</summary>

**Yes, eligible.** Mark-and-sweep collects by reachability from roots, not reference counts. Since neither object is reachable from any root after both variables are nulled, the whole cycle is unreachable and collected. (Naive reference-counting would leak here; real engines do not.)

</details>

**6.**
```js
const cache = [];
function process(data) {
  const result = data.map(x => x * 2);
  cache.push(result);
  return result;
}
```
If `process` is called repeatedly, does this leak memory? Why, and how would you fix it?

<details>
<summary>Show answer</summary>

**Yes, it leaks.** `cache` is a long-lived array that only ever grows — every `result` is retained forever, so it is reachable from a root. Fix: bound the cache (evict old entries, use an LRU with a size cap), or don't retain results you don't need.

</details>

**7.**
```js
function startPolling() {
  const hugeData = new Array(1000000).fill("x");
  setInterval(() => {
    console.log(hugeData.length);
  }, 1000);
}
startPolling();
```
After `startPolling()` returns, is `hugeData` eligible for GC? Why?

<details>
<summary>Show answer</summary>

**No, not eligible.** The `setInterval` callback is a closure that references `hugeData`, and the running timer keeps the callback alive. So `hugeData` is reachable as long as the interval is active. Fix: `clearInterval(id)` when done, which lets both the callback and `hugeData` be collected.

</details>

**8.**
```js
function attach() {
  const bigBuffer = new Array(1000000).fill(0);
  const timer = setInterval(() => {}, 1000);
  // no reference to bigBuffer inside the callback
}
attach();
```
Does the interval callback keep `bigBuffer` alive? Is `bigBuffer` eligible for GC? Does the timer itself leak?

<details>
<summary>Show answer</summary>

The callback does **not** reference `bigBuffer`, so `bigBuffer` is **eligible for GC** after `attach()` returns (nothing reachable references it). However, the **timer itself leaks**: the interval keeps firing forever because its id was never stored and `clearInterval` is never called. Fix: keep the id and call `clearInterval(timer)` when no longer needed.

</details>

**9.**
```js
const node = document.getElementById("banner");
node.remove(); // removed from the DOM tree
// `node` variable still in scope
```
After `node.remove()`, is the DOM element eligible for GC? Why?

<details>
<summary>Show answer</summary>

**No, not eligible.** Removing a node from the DOM tree does not free it if JS still holds a reference — `node` is a live variable pointing at the element (a "detached DOM node"). Fix: set `node = null` (drop all JS references) after removing it so it becomes unreachable.

</details>

**10.**
```js
let listeners = [];
function addHandler(el) {
  const handler = () => console.log("clicked");
  el.addEventListener("click", handler);
  listeners.push(handler);
}
```
If elements are later removed from the DOM but this runs many times, does it leak? How would you fix it?

<details>
<summary>Show answer</summary>

**Yes, it leaks.** The `listeners` array keeps every `handler` alive, and each handler's closure (plus the listener still attached) can keep the associated element/detached node alive too. Fix: call `el.removeEventListener("click", handler)` before dropping the element, and remove the handler from `listeners` — so nothing is reachable.

</details>

**11.**
```js
const seen = new Map();
function track(obj) {
  seen.set(obj, Date.now());
}
// track() is called with many short-lived objects
```
Does using a `Map` here leak memory? Why? How would you change it so entries are cleaned up automatically?

<details>
<summary>Show answer</summary>

**Yes, it leaks.** A `Map` holds its keys **strongly**, so every tracked object stays reachable via `seen` even after all other references are gone — the map only grows. Fix: use a `WeakMap`, whose keys are held weakly, so an entry is dropped automatically once its key object becomes unreachable elsewhere.

</details>

**12.**
```js
const seen = new WeakMap();
function track(obj) {
  seen.set(obj, Date.now());
}
let temp = {};
track(temp);
temp = null;
```
After `temp = null`, is the object (and its WeakMap entry) eligible for GC? Why?

<details>
<summary>Show answer</summary>

**Yes, eligible.** A `WeakMap` holds keys weakly. After `temp = null`, nothing else references the object, so it (and its associated WeakMap entry) can be collected. Weak references do not, by themselves, keep an object alive.

</details>

**13.**
```js
const registry = new Set();
function register(obj) {
  registry.add(obj);
}
let item = { data: 123 };
register(item);
item = null;
```
After `item = null`, is the object eligible for GC? Why? What would you use instead if you want it collectible?

<details>
<summary>Show answer</summary>

**No, not eligible.** A `Set` holds its members **strongly**, so `registry` keeps the object reachable even after `item = null`. Fix: use a `WeakSet` if you want membership tracking that doesn't prevent collection (note: WeakSet is not iterable and has no size).

</details>

**14.**
```js
const els = new WeakSet();
let div = document.createElement("div");
els.add(div);
div = null;
```
After `div = null`, is the `div` eligible for GC? Why?

<details>
<summary>Show answer</summary>

**Yes, eligible.** `WeakSet` holds its members weakly. After `div = null` there is no strong reference to the element, so it becomes unreachable and collectible; the WeakSet entry drops automatically.

</details>

**15.**
```js
let cached = new WeakRef({ heavy: new Array(1000000) });
// ... later ...
const obj = cached.deref();
```
Does the `WeakRef` prevent the wrapped object from being collected? What can `cached.deref()` return, and when?

<details>
<summary>Show answer</summary>

**No, it does not prevent collection.** A `WeakRef` is a weak (non-owning) reference — because nothing else references the wrapped object, it may be collected at any time. `cached.deref()` returns the object if it is still alive, or `undefined` once it has been collected. Always handle the `undefined` case.

</details>

**16.**
```js
const handlers = {};
function subscribe(id) {
  const bigContext = new Array(500000).fill(id);
  handlers[id] = function () {
    return bigContext.length;
  };
}
// subscribe called for many ids; unsubscribe never called
```
Does this leak? What keeps `bigContext` alive, and how would you fix the growth?

<details>
<summary>Show answer</summary>

**Yes, it leaks.** `handlers` is a long-lived object; each stored function is a closure over `bigContext`, so every `bigContext` stays reachable and the map grows without bound. Fix: delete entries when done (`delete handlers[id]` / an unsubscribe path), and/or avoid capturing large data in the closure.

</details>

**17.**
```js
function makeCounter() {
  let count = 0;
  let unused = new Array(1000000).fill(0);
  return function () {
    return ++count;
  };
}
const counter = makeCounter();
```
Is `unused` eligible for GC after `makeCounter()` returns? Is `count`? Explain what the returned closure keeps alive.

<details>
<summary>Show answer</summary>

**`unused` is eligible for GC** — the returned closure does not reference it, so it's not captured and becomes unreachable when `makeCounter()` returns. **`count` is NOT eligible** — the returned function closes over it and is reachable via `counter`, so `count` is kept alive. Engines only retain the variables a closure actually uses.

</details>

**18.**
```js
const elementData = new Map();
function decorate(el) {
  elementData.set(el, { clicks: 0 });
  el.addEventListener("click", () => {
    elementData.get(el).clicks++;
  });
}
```
A node passed to `decorate` is later detached from the DOM and all other JS references dropped. Is it eligible for GC? What keeps it alive, and how do you fix it?

<details>
<summary>Show answer</summary>

**No, not eligible — it leaks.** The `elementData` `Map` holds the element **strongly** as a key, and the click handler's closure also references `el`; both keep the detached node alive. Fix: use a `WeakMap` keyed by the element, and call `removeEventListener` when detaching so no strong references remain.

</details>

**19.**
```js
let obj = { a: 1 };
const ref = new WeakRef(obj);
const strong = obj;   // second, strong reference
obj = null;
```
After `obj = null`, is the object eligible for GC? Explain the roles of `ref` and `strong`.

<details>
<summary>Show answer</summary>

**No, not eligible.** `strong` is a normal (strong) reference still pointing at the object, so it stays alive after `obj = null`. `ref` is a `WeakRef` and would not, on its own, keep it alive — but the strong reference does. Null `strong` too and it becomes collectible (then `ref.deref()` may return `undefined`).

</details>

**20.**
```js
const arr = [{ big: new Array(100000) }, { big: new Array(100000) }];
let leaked = arr[0];
arr.length = 0; // empties the array
```
After `arr.length = 0`, which objects are eligible for GC and which are not? Why?

<details>
<summary>Show answer</summary>

**`arr[1]`'s object is eligible** for GC — emptying the array dropped the only reference to it. **`arr[0]`'s object is NOT eligible** — `leaked` still holds a strong reference to it, so it (and its `big` array) stay alive. Emptying a container frees only the elements nothing else references.

</details>
