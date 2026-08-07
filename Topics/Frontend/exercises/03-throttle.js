/**
 * throttle(fn, delay) — run `fn` at most ONCE per `delay` ms, however often it's called.
 *
 *   const onScroll = throttle(() => console.log("tick"), 200);
 *   // fire onScroll() 100x in a second → ~5 "tick"s (one per 200ms), not 100
 *
 * KEY LESSONS:
 *  - track the TIMESTAMP of the last run; only run if enough time has passed
 *  - throttle = "steady cadence DURING calls"  vs  debounce = "wait until calls stop"
 *  - NOT built with setInterval (an interval ticks on its own; throttle reacts to your calls)
 */

// --- YOUR ATTEMPT ---


// --- SOLUTION (timestamp version) ---
function throttle(fn, delay) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= delay) {   // enough time since last run?
      last = now;
      fn.apply(this, args);
    }
  };
}

function throttle(fn, delay) {
  let waiting = false;
  return function (...args) {
    if (waiting) return;        // in cooldown → ignore
    fn.apply(this, args);       // fire now (leading edge)
    waiting = true;
    setTimeout(() => {
      waiting = false;          // cooldown over → allow next
    }, delay);
  };
}