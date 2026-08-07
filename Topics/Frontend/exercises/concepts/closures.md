# JavaScript Closures — Predict the Behavior

Predict the output/behavior of each snippet. Attempt first, then click "Show answer" to reveal!

A **closure** is a function bundled together with references to its surrounding lexical scope. The function "remembers" the variables from where it was *defined*, not where it's called. Watch for: capture-by-reference, `var` vs `let` scoping, and shared vs independent state.

## Questions

### 1

```js
function makeGreeter(name) {
  return function () {
    return "Hi " + name;
  };
}
const greet = makeGreeter("Ada");
console.log(greet());
```

What logs?

<details>
<summary>Show answer</summary>

**`Hi Ada`**
The returned function closes over `name`. Even after `makeGreeter` has returned, the inner function still holds a reference to `name = "Ada"`.

</details>

### 2

```js
function counter() {
  let count = 0;
  return function () {
    count++;
    return count;
  };
}
const c = counter();
console.log(c());
console.log(c());
console.log(c());
```

What are the three logged values?

<details>
<summary>Show answer</summary>

**`1`, `2`, `3`**
`count` lives in `counter`'s scope and is shared by every call to `c`. Each invocation mutates and remembers the same `count`.

</details>

### 3

```js
function makeCounter() {
  let count = 0;
  return () => ++count;
}
const a = makeCounter();
const b = makeCounter();
console.log(a());
console.log(a());
console.log(b());
```

What logs, in order?

<details>
<summary>Show answer</summary>

**`1`, `2`, `1`**
`a` and `b` come from separate `makeCounter()` calls, so each has its own independent `count`. `a` increments to 1 then 2; `b` starts fresh at 1.

</details>

### 4

```js
let x = 10;
function outer() {
  console.log(x);
  let x = 20;
}
outer();
```

What happens when you run this?

<details>
<summary>Show answer</summary>

**`ReferenceError: Cannot access 'x' before initialization`**
The inner `let x` is hoisted to the top of `outer`'s scope but sits in the temporal dead zone. The `console.log` refers to the local `x`, not the outer one, and the local isn't initialized yet.

</details>

### 5

```js
function outer() {
  let value = "first";
  function inner() {
    return value;
  }
  value = "second";
  return inner;
}
console.log(outer()());
```

What logs?

<details>
<summary>Show answer</summary>

**`second`**
`inner` captures the *variable* `value`, not its value at definition time. By the time `inner` runs, `value` has been reassigned to `"second"`.

</details>

### 6

```js
const funcs = [];
for (var i = 0; i < 3; i++) {
  funcs.push(function () {
    return i;
  });
}
console.log(funcs[0](), funcs[1](), funcs[2]());
```

What logs?

<details>
<summary>Show answer</summary>

**`3 3 3`**
`var i` is function-scoped, so all three closures share one `i`. The loop finishes with `i === 3`, and every closure reads that final value.

</details>

### 7

```js
const funcs = [];
for (let i = 0; i < 3; i++) {
  funcs.push(function () {
    return i;
  });
}
console.log(funcs[0](), funcs[1](), funcs[2]());
```

What logs?

<details>
<summary>Show answer</summary>

**`0 1 2`**
`let i` is block-scoped and gets a fresh binding each iteration. Each closure captures its own `i`.

</details>

### 8

```js
for (var i = 0; i < 3; i++) {
  setTimeout(function () {
    console.log(i);
  }, 100);
}
```

What logs, and how many times?

<details>
<summary>Show answer</summary>

**`3`, `3`, `3` (three times)**
`var i` is shared. By the time the timers fire (after the synchronous loop completes), `i` is already 3 for all three callbacks.

</details>

### 9

```js
for (let i = 0; i < 3; i++) {
  setTimeout(function () {
    console.log(i);
  }, 100);
}
```

What logs?

<details>
<summary>Show answer</summary>

**`0`, `1`, `2`**
`let` creates a fresh `i` binding per iteration, so each `setTimeout` callback captures a distinct value.

</details>

### 10

```js
for (var i = 0; i < 3; i++) {
  (function (j) {
    setTimeout(function () {
      console.log(j);
    }, 100);
  })(i);
}
```

What logs?

<details>
<summary>Show answer</summary>

**`0`, `1`, `2`**
The IIFE copies the current `i` into parameter `j` each iteration, giving each timer its own snapshot value — the classic pre-`let` fix.

</details>

### 11

```js
console.log("A");
for (var i = 0; i < 3; i++) {
  setTimeout(function () {
    console.log(i);
  }, 0);
}
console.log("B");
```

What logs, in order?

<details>
<summary>Show answer</summary>

**`A`, `B`, then `3`, `3`, `3`**
Synchronous code runs first (`A`, `B`). The `setTimeout` callbacks are deferred to the task queue and run after; by then shared `var i` is 3.

</details>

### 12

```js
function multiplier(factor) {
  return function (n) {
    return n * factor;
  };
}
const double = multiplier(2);
const triple = multiplier(3);
console.log(double(5), triple(5));
```

What logs?

<details>
<summary>Show answer</summary>

**`10 15`**
Each call to `multiplier` produces a closure with its own `factor`. `double` remembers `factor = 2`, `triple` remembers `factor = 3`.

</details>

### 13

```js
function add(a) {
  return function (b) {
    return function (c) {
      return a + b + c;
    };
  };
}
console.log(add(1)(2)(3));
```

What logs?

<details>
<summary>Show answer</summary>

**`6`**
Curried closures: `add(1)` captures `a=1`, the next captures `b=2`, the innermost captures `c=3`, summing to 6.

</details>

### 14

```js
function makeAccount() {
  let balance = 100;
  return {
    deposit(n) { balance += n; return balance; },
    withdraw(n) { balance -= n; return balance; },
  };
}
const acc = makeAccount();
console.log(acc.deposit(50));
console.log(acc.withdraw(30));
console.log(acc.balance);
```

What are the three logged values?

<details>
<summary>Show answer</summary>

**`150`, `120`, `undefined`**
`deposit` and `withdraw` share the private `balance` via closure: 100+50=150, then 150−30=120. `balance` is not a property on the returned object, so `acc.balance` is `undefined`.

</details>

### 15

```js
function memoize(fn) {
  const cache = {};
  return function (n) {
    if (n in cache) {
      console.log("cache hit", n);
      return cache[n];
    }
    console.log("computing", n);
    cache[n] = fn(n);
    return cache[n];
  };
}
const square = memoize((n) => n * n);
console.log(square(4));
console.log(square(4));
```

What logs, in order?

<details>
<summary>Show answer</summary>

**`computing 4`, then `16`, then `cache hit 4`, then `16`**
First call misses the cache (logs "computing 4"), computes and returns 16. Second call finds `4` in the closed-over `cache` (logs "cache hit 4") and returns the stored 16.

</details>

### 16

```js
const buttons = [];
for (var i = 0; i < 3; i++) {
  buttons.push({
    id: i,
    handleClick: function () {
      return "clicked " + i;
    },
  });
}
console.log(buttons[0].id, buttons[0].handleClick());
```

What logs?

<details>
<summary>Show answer</summary>

**`0 clicked 3`**
`id` was assigned the value `0` at creation time (a copied primitive). But `handleClick` closes over the shared `var i`, which is `3` after the loop finishes — so it returns `"clicked 3"`.

</details>

### 17

```js
function setup() {
  const items = ["a", "b", "c"];
  const handlers = items.map(function (item, index) {
    return function () {
      return index + ":" + item;
    };
  });
  return handlers;
}
const h = setup();
console.log(h[1]());
```

What logs?

<details>
<summary>Show answer</summary>

**`1:b`**
`Array.map`'s callback gets fresh `item` and `index` parameters each iteration, and each returned function closes over its own pair. Index 1 → `"1:b"`.

</details>

### 18

```js
function createTimers() {
  const results = [];
  let i = 0;
  const id = setInterval(function () {
    results.push(i);
    i++;
    if (i === 3) clearInterval(id);
  }, 100);
  return results;
}
const r = createTimers();
console.log(r.length);
```

What is `r.length` at the moment it logs?

<details>
<summary>Show answer</summary>

**`0`**
`setInterval` is asynchronous. `createTimers` returns `results` immediately (still empty) before any interval callback has run, so `r.length` is `0` when logged. The array will fill to `[0,1,2]` later, but that's after the log.

</details>

### 19

```js
let value = 1;
const getValue = () => value;
const getValueSnapshot = ((v) => () => v)(value);
value = 99;
console.log(getValue(), getValueSnapshot());
```

What logs?

<details>
<summary>Show answer</summary>

**`99 1`**
`getValue` closes over the variable `value`, so it sees the updated `99`. `getValueSnapshot` was built by an IIFE that copied `value` (then 1) into parameter `v`, freezing the snapshot at `1`.

</details>

### 20

```js
function makeHandlers() {
  const bigData = new Array(1000000).fill("x");
  return {
    getFirst: () => bigData[0],
    getLength: () => bigData.length,
  };
}
let handlers = makeHandlers();
console.log(handlers.getLength());
handlers = null;
```

What logs, and what happens to `bigData` in memory after the last line?

<details>
<summary>Show answer</summary>

**Logs `1000000`.** After `handlers = null`, nothing references the closures that captured `bigData`, so `bigData` becomes eligible for garbage collection. This is the memory angle: as long as a live closure (e.g., a running `setInterval` callback) holds `bigData`, it stays in memory — dropping the last reference frees it.

</details>
