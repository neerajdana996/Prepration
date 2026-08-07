/**
 * once(fn) — return a function that runs `fn` only the FIRST time it's called.
 * Later calls do nothing (or return the first cached result).
 *
 *   const init = once(() => console.log("init!"));
 *   init();  // "init!"
 *   init();  // (nothing)
 *   init();  // (nothing)
 *
 * KEY LESSONS:
 *  - closure holds a boolean flag = private "have I run?" state
 *  - the wrapper must be a REGULAR function so `this` forwards to the caller
 *    (an arrow would make `this` lexical → breaks for object methods)
 */

// --- YOUR ATTEMPT (write it here) ---


// --- SOLUTION ---
function once(fn) {
  let called = false;
  let result;
  return function (...args) {
    if (called) return result;          // repeat calls → cached result
    called = true;
    result = fn.apply(this, args);      // regular fn → forwards `this` + args
    return result;
  };
}
