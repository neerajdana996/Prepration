# Pure Functions — Interview Practice

Judge pure vs impure / predict behavior. Attempt each first, then reveal the answer!

## Questions

**1.**
```js
function add(a, b) {
  return a + b;
}
```
Is `add` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

PURE. Same inputs always yield the same sum, and it has no side effects — it only reads its arguments and returns a value.

</details>

**2.**
```js
function square(x) {
  return x * x;
}
```
Is `square` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

PURE. Depends only on `x`, mutates nothing, and always returns the same result for the same input.

</details>

**3.**
```js
function greet(name) {
  console.log("Hello, " + name);
  return "Hello, " + name;
}
```
Is `greet` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

IMPURE. `console.log` is an observable side effect (I/O). The return value is deterministic, but the logging alone makes it impure.

</details>

**4.**
```js
function roll() {
  return Math.floor(Math.random() * 6) + 1;
}
```
Is `roll` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

IMPURE. `Math.random()` returns a different value each call, so the output isn't determined by the (empty) input — it's not referentially transparent.

</details>

**5.**
```js
function timestampedId(prefix) {
  return prefix + "-" + Date.now();
}
```
Is `timestampedId` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

IMPURE. `Date.now()` reads changing external clock state, so the same `prefix` produces different results over time.

</details>

**6.**
```js
let counter = 0;
function nextId() {
  counter += 1;
  return counter;
}
```
Is `nextId` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

IMPURE. It reads and mutates external variable `counter`, so it both has a side effect and returns different values for the same (empty) input.

</details>

**7.**
```js
const TAX_RATE = 0.2;
function withTax(price) {
  return price * (1 + TAX_RATE);
}
```
Is `withTax` PURE or IMPURE? Why? (Assume `TAX_RATE` is a `const` primitive.)

<details>
<summary>Show answer</summary>

PURE. It only reads a constant primitive that never changes, so the output depends solely on `price`. Reading an immutable constant is not impurity.

</details>

**8.**
```js
function addItem(cart, item) {
  cart.push(item);
  return cart;
}
```
Is `addItem` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

IMPURE. `cart.push(item)` mutates the caller's array (a side effect on an argument), so the caller's data changes behind its back.

</details>

**9.**
```js
function addItem(cart, item) {
  return [...cart, item];
}
```
Is this version of `addItem` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

PURE. `[...cart, item]` builds and returns a new array; the original `cart` is untouched, and same inputs give an equivalent result.

</details>

**10.**
```js
const nums = [3, 1, 2];
const doubled = nums.map(n => n * 2);
console.log(doubled);
console.log(nums);
```
Predict both outputs. Is the callback pure? Was `nums` mutated?

<details>
<summary>Show answer</summary>

Outputs: `[6, 2, 4]` then `[3, 1, 2]`. The callback `n => n * 2` is pure, and `map` returns a new array — `nums` is not mutated.

</details>

**11.**
```js
const nums = [3, 1, 2];
const sorted = nums.sort((a, b) => a - b);
console.log(sorted);
console.log(nums);
console.log(sorted === nums);
```
Predict all three outputs. Was `nums` mutated?

<details>
<summary>Show answer</summary>

Outputs: `[1, 2, 3]`, `[1, 2, 3]`, `true`. `sort` sorts in place and returns the same array reference, so `nums` IS mutated and `sorted === nums`.

</details>

**12.**
```js
function toSorted(arr) {
  return [...arr].sort((a, b) => a - b);
}
const original = [3, 1, 2];
const result = toSorted(original);
console.log(result);
console.log(original);
```
Predict both outputs. Is `toSorted` PURE or IMPURE?

<details>
<summary>Show answer</summary>

Outputs: `[1, 2, 3]` then `[3, 1, 2]`. PURE — copying with `[...arr]` first means `sort` mutates only the throwaway copy, leaving `original` intact.

</details>

**13.**
```js
function updateName(user, name) {
  user.name = name;
  return user;
}
const u = { name: "Ada", age: 36 };
const v = updateName(u, "Grace");
console.log(u.name);
console.log(u === v);
```
Predict both outputs. Is `updateName` PURE or IMPURE?

<details>
<summary>Show answer</summary>

Outputs: `Grace` then `true`. IMPURE — it mutates the passed-in object, so `u` changes and `v` is the same reference as `u`.

</details>

**14.**
```js
function updateName(user, name) {
  return { ...user, name };
}
const u = { name: "Ada", age: 36 };
const v = updateName(u, "Grace");
console.log(u.name);
console.log(v.name);
console.log(u === v);
```
Predict all three outputs. Is this version PURE or IMPURE?

<details>
<summary>Show answer</summary>

Outputs: `Ada`, `Grace`, `false`. PURE — the spread creates a new object, so the original `u` is unchanged and `v` is a distinct reference.

</details>

**15.**
```js
let config = { discount: 0.1 };
function priceAfterDiscount(price) {
  return price - price * config.discount;
}
console.log(priceAfterDiscount(100));
config.discount = 0.5;
console.log(priceAfterDiscount(100));
```
Predict both outputs. Is `priceAfterDiscount` PURE or IMPURE? Why?

<details>
<summary>Show answer</summary>

Outputs: `90` then `50`. IMPURE — it reads external mutable state `config.discount`, so the same input `100` gives different results after `config` changes.

</details>

**16.**
```js
function memoize(fn) {
  const cache = new Map();
  return function (n) {
    if (cache.has(n)) return cache.get(n);
    const result = fn(n);
    cache.set(n, result);
    return result;
  };
}
const slowSquare = n => n * n;
const fastSquare = memoize(slowSquare);
console.log(fastSquare(4));
console.log(fastSquare(4));
```
Predict both outputs. Why is it safe to cache `slowSquare` but unsafe to cache `Math.random`?

<details>
<summary>Show answer</summary>

Outputs: `16` then `16`. Caching is safe because `slowSquare` is pure — a given input always maps to one correct result. `Math.random` has no fixed input→output mapping, so a cache would wrongly freeze one random value.

</details>

**17.**
```js
const nums = [1, 2, 3, 4];
const evens = nums.filter(n => n % 2 === 0);
const removed = nums.splice(0, 2);
console.log(evens);
console.log(removed);
console.log(nums);
```
Predict all three outputs. Which method is pure — `filter` or `splice`?

<details>
<summary>Show answer</summary>

Outputs: `[2, 4]`, `[1, 2]`, `[3, 4]`. `filter` is pure (returns a new array, leaves `nums` alone); `splice` is impure (removes elements in place, so `nums` becomes `[3, 4]`).

</details>

**18.**
```js
function pushImpure(arr) {
  arr.push(0);
  return arr.length;
}
const a = [1, 2];
console.log(pushImpure(a));
console.log(pushImpure(a));
console.log(a);
```
Predict all three outputs. Why does calling `pushImpure` twice with the "same" argument give different results?

<details>
<summary>Show answer</summary>

Outputs: `3`, `4`, `[1, 2, 0, 0]`. The "same" argument isn't really the same — the first call mutated `a`, so the second call sees a longer array. Mutation destroys referential transparency across calls.

</details>

**19.**
```js
function tallyPure(scores) {
  return scores.reduce((sum, s) => sum + s, 0);
}
const s = [10, 20, 30];
console.log(tallyPure(s));
console.log(tallyPure(s));
console.log(s);
```
Predict all three outputs. Is `tallyPure` PURE or IMPURE?

<details>
<summary>Show answer</summary>

Outputs: `60`, `60`, `[10, 20, 30]`. PURE — `reduce` only reads the array to compute a sum; it never mutates `scores`, so results are stable.

</details>

**20.**
```js
let log = [];
function processImpure(x) {
  log.push(x);
  return x * 2;
}
function processPure(x, history) {
  return { value: x * 2, history: [...history, x] };
}
console.log(processImpure(5));
console.log(log);
const out = processPure(5, []);
console.log(out.value, out.history);
```
Predict the outputs. Explain how `processPure` achieves the same intent as `processImpure` without a side effect.

<details>
<summary>Show answer</summary>

Outputs: `10`, `[5]`, then `10 [5]`. `processImpure` mutates external `log` (a side effect); `processPure` instead takes prior state as input and returns a new object bundling both the value and an updated history copy — same intent, no external mutation.

</details>
