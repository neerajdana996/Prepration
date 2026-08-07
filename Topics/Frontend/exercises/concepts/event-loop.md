# The Event Loop — Predict the OUTPUT ORDER

Predict the exact output order. Attempt each first, then click to reveal!

**Mental model:** Run all synchronous code (the call stack) to completion → drain the **entire** microtask queue (Promise `.then`/`.catch`/`.finally`, `await` continuations, `queueMicrotask`) — including microtasks queued *during* the drain → then run **one** macrotask (`setTimeout`/`setInterval`) → drain microtasks again → repeat.

---

## Questions

### 1
```js
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
```
Output order?

<details>
<summary>Show answer</summary>

`A, D, C, B`
Sync logs `A` and `D`. Then the microtask (`C`) drains before the `setTimeout` macrotask (`B`).

</details>

### 2
```js
console.log(1);
setTimeout(() => console.log(2), 0);
console.log(3);
```
Output order?

<details>
<summary>Show answer</summary>

`1, 3, 2`
`1` and `3` are synchronous; `setTimeout` callback `2` is a macrotask that runs after the stack clears.

</details>

### 3
```js
console.log('start');
new Promise((resolve) => {
  console.log('executor');
  resolve();
}).then(() => console.log('then'));
console.log('end');
```
Output order?

<details>
<summary>Show answer</summary>

`start, executor, end, then`
The Promise **executor runs synchronously** (so `executor` prints between `start` and `end`); `.then` is a microtask, so `then` runs last.

</details>

### 4
```js
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise1'));
Promise.resolve().then(() => console.log('promise2'));
```
Output order?

<details>
<summary>Show answer</summary>

`promise1, promise2, timeout`
No sync logs. Both microtasks drain (in the order queued) before the single macrotask `timeout`.

</details>

### 5
```js
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
setTimeout(() => console.log('4'), 0);
console.log('5');
```
Output order?

<details>
<summary>Show answer</summary>

`1, 5, 3, 2, 4`
Sync: `1`, `5`. Microtask: `3`. Then macrotasks fire in registration order: `2`, then `4`.

</details>

### 6
```js
async function f() {
  console.log('A');
  await null;
  console.log('B');
}
console.log('start');
f();
console.log('end');
```
Output order?

<details>
<summary>Show answer</summary>

`start, A, end, B`
`f()` runs synchronously up to `await` (prints `A`), then suspends; `end` prints. The code after `await` is a microtask, so `B` runs after sync code finishes.

</details>

### 7
```js
async function f() {
  console.log('1');
  await Promise.resolve();
  console.log('2');
}
console.log('3');
f();
Promise.resolve().then(() => console.log('4'));
console.log('5');
```
Output order?

<details>
<summary>Show answer</summary>

`3, 1, 5, 2, 4`
Sync: `3`, then `f()` prints `1` and suspends at `await` (queues continuation), then `5`. Microtasks in queue order: continuation `2`, then the standalone `.then` `4`.

</details>

### 8
```js
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => {
  console.log('promise1');
  queueMicrotask(() => console.log('micro'));
});
console.log('sync');
```
Output order?

<details>
<summary>Show answer</summary>

`sync, promise1, micro, timeout`
Sync: `sync`. Microtask prints `promise1` and queues `micro` **during** the drain — so `micro` still runs before the `timeout` macrotask.

</details>

### 9
```js
console.log('start');
queueMicrotask(() => console.log('micro'));
Promise.resolve().then(() => console.log('promise'));
console.log('end');
```
Output order?

<details>
<summary>Show answer</summary>

`start, end, micro, promise`
Sync: `start`, `end`. `queueMicrotask` and `.then` share the same microtask queue and run in the order they were queued: `micro`, then `promise`.

</details>

### 10
```js
console.log('A');
setTimeout(() => {
  console.log('B');
  setTimeout(() => console.log('C'), 0);
}, 0);
setTimeout(() => console.log('D'), 0);
console.log('E');
```
Output order?

<details>
<summary>Show answer</summary>

`A, E, B, D, C`
Sync: `A`, `E`. Macrotask 1 prints `B` and schedules `C`. Macrotask 2 (`D`) was already queued, so it runs before `C`. Then `C`.

</details>

### 11
```js
Promise.resolve().then(() => {
  console.log('1');
  Promise.resolve().then(() => console.log('2'));
}).then(() => console.log('3'));
```
Output order?

<details>
<summary>Show answer</summary>

`1, 2, 3`
First `.then` prints `1` and synchronously queues the inner `.then` (`2`). The outer chained `.then` (`3`) is queued only when the first callback *returns*, so `2` is queued before `3`.

</details>

### 12
```js
async function f() {
  console.log('1');
  await g();
  console.log('2');
}
async function g() {
  console.log('3');
}
setTimeout(() => console.log('4'), 0);
f();
console.log('5');
```
Output order?

<details>
<summary>Show answer</summary>

`1, 3, 5, 2, 4`
`f()` prints `1`; `await g()` runs `g` synchronously (`3`) then suspends. Sync `5` prints. Microtask continuation `2` runs before the `setTimeout` macrotask `4`.

</details>

### 13
```js
async function f() {
  console.log('A');
  await null;
  console.log('B');
  await null;
  console.log('C');
}
console.log('start');
f();
Promise.resolve().then(() => console.log('P'));
console.log('end');
```
Output order?

<details>
<summary>Show answer</summary>

`start, A, end, B, P, C`
Sync: `start`, `A`, `end`. First continuation `B` runs, then re-suspends (queues `C`). `P` was queued before that re-suspension, so `P` runs before `C`.

</details>

### 14
```js
console.log('1');
setTimeout(() => {
  console.log('2');
  Promise.resolve().then(() => console.log('3'));
}, 0);
setTimeout(() => console.log('4'), 0);
Promise.resolve().then(() => console.log('5'));
console.log('6');
```
Output order?

<details>
<summary>Show answer</summary>

`1, 6, 5, 2, 3, 4`
Sync: `1`, `6`. Microtask: `5`. Macrotask 1 prints `2`, queues `3`; microtasks drain (`3`) before the next macrotask. Macrotask 2: `4`.

</details>

### 15
```js
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => {
  console.log('3');
  return Promise.resolve();
}).then(() => console.log('4'));
Promise.resolve().then(() => console.log('5'));
console.log('6');
```
Output order?

<details>
<summary>Show answer</summary>

`1, 6, 3, 5, 4, 2`
Sync: `1`, `6`. Microtasks: `3` (which returns a thenable) then `5`. **Returning a Promise adds extra microtask ticks** to adopt it, so `4` is delayed until after `5`. Macrotask `2` last.

</details>

### 16
```js
async function a() {
  console.log('a-start');
  await b();
  console.log('a-end');
}
async function b() {
  console.log('b-start');
  await Promise.resolve();
  console.log('b-end');
}
a();
console.log('main');
```
Output order?

<details>
<summary>Show answer</summary>

`a-start, b-start, main, b-end, a-end`
`a` calls `b`: prints `a-start`, `b-start`, then both suspend; `main` prints. `b`'s continuation prints `b-end` and resolves `b`'s promise, which then resumes `a` → `a-end`.

</details>

### 17
```js
console.log('1');
setTimeout(() => console.log('2'), 0);
queueMicrotask(() => {
  console.log('3');
  queueMicrotask(() => console.log('4'));
});
Promise.resolve().then(() => console.log('5'));
console.log('6');
```
Output order?

<details>
<summary>Show answer</summary>

`1, 6, 3, 5, 4, 2`
Sync: `1`, `6`. Microtasks in queue order: `3` (queues `4` during drain), then `5`, then the newly queued `4`. Macrotask `2` last.

</details>

### 18
```js
async function f() {
  console.log('1');
  setTimeout(() => console.log('2'), 0);
  await Promise.resolve();
  console.log('3');
  await Promise.resolve();
  console.log('4');
}
console.log('5');
f();
setTimeout(() => console.log('6'), 0);
Promise.resolve().then(() => console.log('7'));
console.log('8');
```
Output order?

<details>
<summary>Show answer</summary>

`5, 1, 8, 3, 7, 4, 2, 6`
Sync: `5`, `1`, `8` (the inner `setTimeout` `2` is queued early but is still a macrotask). Microtasks: `3` (re-suspends, queues `4`), `7`, then `4`. Macrotasks in order: `2`, `6`.

</details>

### 19
```js
console.log('script start');

setTimeout(() => console.log('setTimeout'), 0);

Promise.resolve()
  .then(() => console.log('promise1'))
  .then(() => console.log('promise2'));

async function async1() {
  console.log('async1 start');
  await async2();
  console.log('async1 end');
}
async function async2() {
  console.log('async2');
}
async1();

console.log('script end');
```
Output order?

<details>
<summary>Show answer</summary>

`script start, async1 start, async2, script end, promise1, async1 end, promise2, setTimeout`
Classic. Sync prints the first four. Microtasks: `promise1` (queued before `async1`'s continuation), then `async1 end`, then `promise2` (queued when `promise1`'s callback returned). Macrotask `setTimeout` last.

</details>

### 20
```js
console.log('start');

setTimeout(() => console.log('T1'), 0);

Promise.resolve()
  .then(() => {
    console.log('A');
    queueMicrotask(() => console.log('B'));
  })
  .then(() => console.log('C'));

new Promise((resolve) => {
  console.log('E');
  resolve();
  console.log('F');
}).then(() => console.log('G'));

setTimeout(() => {
  console.log('T2');
  Promise.resolve().then(() => console.log('H'));
}, 0);

console.log('end');
```
Output order?

<details>
<summary>Show answer</summary>

`start, E, F, end, A, G, B, C, T1, T2, H`
Sync: `start`, executor `E`/`F`, `end`. Microtasks: `A` (queues `B`, then its return queues `C`), `G` (queued right after `A`), then `B`, then `C`. Macrotask `T1`, then `T2` (which queues `H`, drained immediately after).

</details>
