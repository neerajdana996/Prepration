/**
 * memoize(fn) — cache results by ARGUMENTS. Repeated calls with the same args
 * return the stored result instead of recomputing.
 *
 *   const fast = memoize(n => n * n);
 *   fast(4);  // computes → 16
 *   fast(4);  // cached   → 16 (no recompute)
 *   fast(5);  // computes → 25
 *
 * KEY LESSONS:
 *  - closure holds a cache (Map or {})
 *  - build a KEY from the args. args.toString() collides for objects
 *    (every object → "[object Object]") → JSON.stringify(args) is more robust
 *  - regular function so `this` forwards
 */

// --- YOUR ATTEMPT ---


// --- SOLUTION ---
function memoize(fn) {
  const cache = new Map();
  return function (...args) {
    const key = JSON.stringify(args);        // robust-ish key (beware: fns/undefined/order)
    if (cache.has(key)) return cache.get(key);
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}
