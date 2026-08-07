# Arrow Function Behaviours — Predict the Behavior

Predict the behavior/output. Each answer is hidden under a "Show answer" toggle — attempt first!

> Assume each snippet runs as a normal **non-strict browser script** at the top level, so top-level `this === window` (the global object) and reading a missing global property (e.g. `window.count`) gives `undefined`.

## Questions

**1.**
```js
const double = n => n * 2;
console.log(double(5));
```
What logs?

<details>
<summary>Show answer</summary>

`10`.
Single-expression arrow bodies have an **implicit return** — no `return` keyword needed.

</details>

**2.**
```js
const add = (a, b) => a + b;
const greet = () => "hi";
console.log(add(2, 3), greet());
```
What logs?

<details>
<summary>Show answer</summary>

`5 hi`.
Multiple params need parentheses; zero params require empty `()`. Both still implicitly return their expression.

</details>

**3.**
```js
const square = n => { n * n; };
console.log(square(4));
```
What logs?

<details>
<summary>Show answer</summary>

`undefined`.
Curly braces make it a **block body**, so `n * n` is just an unused statement and there is no `return` → the function returns `undefined`.

</details>

**4.**
```js
const makeUser = name => { name: name };
console.log(makeUser("Ann"));
```
What logs?

<details>
<summary>Show answer</summary>

`undefined`.
`{ ... }` is parsed as a block, not an object. `name:` becomes a **label**, `name` an expression statement, and nothing is returned.

</details>

**5.**
```js
const makeUser = name => ({ name });
console.log(makeUser("Ann"));
```
What logs?

<details>
<summary>Show answer</summary>

`{ name: "Ann" }`.
Wrapping the object literal in **parentheses** `({ ... })` forces it to be an expression, so it is implicitly returned.

</details>

**6.**
```js
const sign = n => n > 0 ? "pos" : "neg";
console.log(sign(-3));
```
What logs?

<details>
<summary>Show answer</summary>

`"neg"`.
The whole ternary is a single expression and is implicitly returned; `-3 > 0` is false.

</details>

**7.**
```js
const counter = {
  count: 10,
  getCount: () => this.count
};
console.log(counter.getCount());
```
What logs, and what is `this`?

<details>
<summary>Show answer</summary>

`undefined` (and `this` is `window`).
An arrow has **no own `this`**; an object literal is not a function, so `this` comes from the enclosing (top-level) scope = `window`. `window.count` is `undefined`.

</details>

**8.**
```js
const counter = {
  count: 10,
  getCount() { return this.count; }
};
console.log(counter.getCount());
```
What logs?

<details>
<summary>Show answer</summary>

`10`.
A shorthand method is a real function called as `counter.getCount()`, so `this` is `counter` and `this.count` is `10`.

</details>

**9.**
```js
const obj = {
  vals: [1, 2, 3],
  factor: 10,
  scaled() {
    return this.vals.map(v => v * this.factor);
  }
};
console.log(obj.scaled());
```
What logs?

<details>
<summary>Show answer</summary>

`[10, 20, 30]`.
The arrow inside the method has no own `this`, so it **lexically inherits** the method's `this` (= `obj`); `this.factor` is `10`.

</details>

**10.**
```js
const obj = {
  vals: [1, 2],
  factor: 10,
  scaled() {
    return this.vals.map(function (v) { return v * this.factor; });
  }
};
console.log(obj.scaled());
```
What logs?

<details>
<summary>Show answer</summary>

`[NaN, NaN]`.
A regular `function` callback gets its own `this` (here `window` in non-strict mode), so `this.factor` is `undefined` and `v * undefined` is `NaN`.

</details>

**11.**
```js
const acc = {
  total: 0,
  sum(arr) {
    arr.forEach(n => { this.total += n; });
    return this.total;
  }
};
console.log(acc.sum([1, 2, 3]));
```
What logs?

<details>
<summary>Show answer</summary>

`6`.
The `forEach` arrow inherits `this` from the `sum` method (= `acc`), so `this.total` accumulates correctly.

</details>

**12.**
```js
function Timer() {
  this.seconds = 0;
  setTimeout(() => { this.seconds++; console.log(this.seconds); }, 0);
}
new Timer();
```
What logs?

<details>
<summary>Show answer</summary>

`1`.
The `setTimeout` arrow keeps the `this` of the `Timer` instance, so `this.seconds` (starting at 0) is incremented to `1`.

</details>

**13.**
```js
function Timer() {
  this.seconds = 42;
  setTimeout(function () { console.log(this.seconds); }, 0);
}
new Timer();
```
What logs?

<details>
<summary>Show answer</summary>

`undefined`.
A regular `function` passed to `setTimeout` loses the instance `this`; it is called with `this` = the global object, so `this.seconds` is `undefined`.

</details>

**14.**
```js
class Button {
  constructor() { this.label = "Click me"; }
  attach(el) {
    el.addEventListener("click", () => console.log(this.label));
  }
}
```
When the button is clicked, what logs? What would change if the handler were `function () { console.log(this.label); }`?

<details>
<summary>Show answer</summary>

Logs `"Click me"`; with a regular function it would log `undefined`.
The arrow handler keeps the instance `this`. A regular handler is called with `this` = the DOM element that fired the event, whose `.label` is `undefined`.

</details>

**15.**
```js
const f = () => arguments[0];
console.log(f(1, 2));
```
What happens?

<details>
<summary>Show answer</summary>

Throws `ReferenceError: arguments is not defined`.
Arrows have **no own `arguments`** object, and here there is no enclosing function to inherit one from, so `arguments` is simply undefined at top level.

</details>

**16.**
```js
function outer() {
  const inner = () => arguments[0];
  return inner();
}
console.log(outer("a", "b"));
```
What logs?

<details>
<summary>Show answer</summary>

`"a"`.
The arrow has no own `arguments`, so it uses the **enclosing function's** `arguments`, whose first element is `"a"`.

</details>

**17.**
```js
const Person = (name) => { this.name = name; };
const p = new Person("Ann");
```
What happens?

<details>
<summary>Show answer</summary>

Throws `TypeError: Person is not a constructor`.
Arrow functions **cannot be called with `new`** — they have no `[[Construct]]` internal method.

</details>

**18.**
```js
const f = () => {};
console.log(f.prototype);
```
What logs?

<details>
<summary>Show answer</summary>

`undefined`.
Arrow functions have **no `prototype` property** (consistent with not being usable as constructors).

</details>

**19.**
```js
const obj = { x: 42 };
const getX = () => this.x;
console.log(getX.call(obj));
```
What logs?

<details>
<summary>Show answer</summary>

`undefined`.
`call`/`apply`/`bind` **cannot change an arrow's `this`**. `this` stays `window`, so `this.x` is `undefined`; only the (unused) argument binding would be affected, not `this`.

</details>

**20.**
```js
function outer() {
  const arrow = () => this.val;
  return arrow.bind({ val: 99 })();
}
console.log(outer.call({ val: 7 }));
```
What logs? (Bonus: what about `const gen = *() => { yield 1; };`?)

<details>
<summary>Show answer</summary>

`7`.
`bind` cannot rebind an arrow's `this`; the arrow keeps `outer`'s `this` (= `{ val: 7 }`). Bonus: `*() => {}` is a **SyntaxError** — arrows can't be generators.

</details>
