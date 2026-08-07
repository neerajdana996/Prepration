/**
 * debounce(fn, delay) — return a function that runs `fn` only after `delay` ms
 * have passed since the LAST call. Rapid calls RESET the timer.
 *
 *   const search = debounce(q => console.log("search:", q), 300);
 *   search("a"); search("ab"); search("abc");
 *   // only ONE log fires — "search: abc" — 300ms after the last call
 *
 * KEY LESSONS:
 *  - closure holds the pending `timer`
 *  - each call clears the previous timer and starts a fresh one
 *  - the setTimeout callback is an ARROW so it inherits `this` from the wrapper
 *  - contrast with throttle: debounce = "wait until calls STOP"
 */

// --- YOUR ATTEMPT ---


// --- SOLUTION ---
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);                            // cancel previous pending call
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, delay) {
  let last = 0
  return function (...args) {
    const now = Date.now();
    if (now - last >= delay) {
      last = now
      fn.apply(this, args)
    }
  }
}