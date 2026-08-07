/**
 * MyPromise — build Promise from scratch. THE capstone machine-coding question.
 * Ties together: closures (J1), `this` (J2), the event loop's microtasks (J5),
 * and promise semantics (J6).
 *
 *   const p = new MyPromise((resolve, reject) => setTimeout(() => resolve(1), 100));
 *   p.then(x => x + 1).then(x => console.log(x));   // 2  (async, chained, transformed)
 *
 * BUILD IT IN STAGES:
 *  1. constructor: state (pending→fulfilled/rejected) + value; resolve/reject settle
 *     ONCE (guard) — set state AND value together (atomic), then ignore repeats silently.
 *  2. then: two cases — already settled → run handler; still pending → STORE the handler
 *     and flush it when settle happens (otherwise a pending .then never fires).
 *  3. async: handlers ALWAYS run as microtasks (queueMicrotask), never synchronously —
 *     so `.then` runs after the current sync code (the J5 guarantee).
 *  4. chaining: then returns a NEW MyPromise; default handlers pass value / re-throw so
 *     values+errors travel down the chain; handler's return resolves the new promise
 *     (throw → rejects it); if a handler returns a promise, ADOPT it (wait for it).
 */

// --- YOUR ATTEMPT (build stage by stage) ---


// --- SOLUTION ---
class MyPromise {
  constructor(executor) {
    this.state = "pending";
    this.value = undefined;
    this.onFulfilledCallbacks = [];
    this.onRejectedCallbacks = [];

    const settle = (newState, val) => {
      if (this.state !== "pending") return;                 // settle once, silently ignore repeats
      this.state = newState;
      this.value = val;                                     // state + value frozen together
      const cbs = newState === "fulfilled" ? this.onFulfilledCallbacks : this.onRejectedCallbacks;
      cbs.forEach(cb => queueMicrotask(cb));                // flush queued handlers as microtasks
    };
    const resolve = (value) => {
      if (value instanceof MyPromise) { value.then(resolve, reject); return; } // adopt a thenable
      settle("fulfilled", value);
    };
    const reject = (reason) => settle("rejected", reason);

    try { executor(resolve, reject); } catch (err) { reject(err); }
  }

  then(onFulfilled, onRejected) {
    // default handlers → pass value through / re-throw error down the chain
    onFulfilled = typeof onFulfilled === "function" ? onFulfilled : (v) => v;
    onRejected  = typeof onRejected  === "function" ? onRejected  : (e) => { throw e; };

    return new MyPromise((resolve, reject) => {             // then returns a NEW promise
      const runFulfilled = () => {                          // closure: reads this.value itself
        try { resolve(onFulfilled(this.value)); }           // return → resolves new promise
        catch (err) { reject(err); }                        // throw  → rejects new promise
      };
      const runRejected = () => {
        try { resolve(onRejected(this.value)); }
        catch (err) { reject(err); }
      };
      if (this.state === "fulfilled") queueMicrotask(runFulfilled);
      else if (this.state === "rejected") queueMicrotask(runRejected);
      else {
        this.onFulfilledCallbacks.push(runFulfilled);
        this.onRejectedCallbacks.push(runRejected);
      }
    });
  }

  catch(onRejected) { return this.then(undefined, onRejected); }
  finally(fn) { return this.then(v => { fn(); return v; }, e => { fn(); throw e; }); }
}
