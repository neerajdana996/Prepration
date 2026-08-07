/**
 * SLIDING WINDOW COUNTER  (weighted approximation)
 * ================================================
 *
 * HOW IT WORKS
 *   A hybrid of fixed-window (cheap) and sliding-log (accurate). Keep just TWO
 *   counters: the number of requests in the CURRENT fixed window and in the
 *   PREVIOUS fixed window. Estimate the count over the trailing windowMs by
 *   weighting the previous window by how much of it still overlaps the sliding
 *   window:
 *
 *     elapsed  = how far we are into the current window (0..windowMs)
 *     overlap  = (windowMs - elapsed) / windowMs   // fraction of prev window still "in view"
 *     estimate = currentCount + previousCount * overlap
 *
 *   Accept iff estimate < limit (then increment currentCount).
 *
 *   Intuition: right at the start of a window (elapsed≈0) the previous window
 *   counts almost fully (overlap≈1). Late in the window (elapsed≈windowMs) it
 *   barely counts (overlap≈0). This linear decay smooths the fixed-window
 *   boundary spike without storing per-request timestamps.
 *
 * PROS
 *   - O(1) memory (two integers + a window id) and O(1) time — as cheap as
 *     fixed window, but no 2x boundary burst.
 *   - Accurate enough that this is the COMMON PRODUCTION CHOICE (used by
 *     Cloudflare, Kong, etc.).
 *
 * CONS
 *   - It is an APPROXIMATION. It assumes the previous window's requests were
 *     spread uniformly. If they were actually clustered, the estimate can be
 *     slightly off (over- or under-counting by a small margin). For almost all
 *     traffic this error is negligible.
 *
 * WHEN TO USE
 *   - Default choice for high-throughput API / gateway rate limiting where you
 *     want smooth limiting at low cost.
 */

class SlidingWindowCounter {
  /**
   * @param {number} limit    max weighted requests per window
   * @param {number} windowMs window size in milliseconds
   */
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.windowId = -1;   // floor(now / windowMs) of the current window
    this.current = 0;     // count in current window
    this.previous = 0;    // count in previous window
  }

  /**
   * @param {number} now epoch millis
   * @returns {boolean}
   */
  allow(now = Date.now()) {
    const windowId = Math.floor(now / this.windowMs);

    // Roll windows forward if time has advanced.
    if (windowId !== this.windowId) {
      // If we advanced exactly one window, current becomes previous.
      // If we jumped 2+ windows, the previous window is fully stale -> 0.
      this.previous = windowId === this.windowId + 1 ? this.current : 0;
      this.current = 0;
      this.windowId = windowId;
    }

    const elapsed = now - windowId * this.windowMs;       // 0..windowMs
    const overlap = (this.windowMs - elapsed) / this.windowMs; // 1..0
    const estimate = this.current + this.previous * overlap;

    if (estimate < this.limit) {
      this.current++;
      return true;
    }
    return false;
  }
}

// --------------------------- runnable demo ---------------------------------
if (require.main === module) {
  const limit = 5;
  const windowMs = 60_000;
  const rl = new SlidingWindowCounter(limit, windowMs);
  console.log('Sliding window counter: limit 5 / 60s\n');

  const base = 60_000 * 1000; // a window boundary

  // Saturate the FIRST window: 5 requests late in window [base-60s, base).
  console.log('--- window 1, near its end (t = base-1s) ---');
  for (let i = 1; i <= 5; i++) {
    console.log(`req ${i}: ${rl.allow(base - 1000) ? 'ALLOW' : 'BLOCK'}`);
  }

  // Now just past the boundary. Fixed-window would allow 5 more immediately.
  // Here previous=5 and overlap is high, so the estimate stays near the limit.
  console.log('\n--- window 2, just after boundary (t = base+1s) ---');
  for (let i = 1; i <= 5; i++) {
    const now = base + 1000; // 1s into new window; overlap = 59/60 ~ 0.983
    const ok = rl.allow(now);
    console.log(`req ${i}: ${ok ? 'ALLOW' : 'BLOCK'}`);
  }
  console.log(
    '\nestimate at t=base+1s starts at current(0) + previous(5)*0.983 ~ 4.9,',
    'so almost nothing gets through -> boundary spike suppressed.'
  );

  // Deep into window 2, previous window has decayed away.
  console.log('\n--- window 2, near its end (t = base+59s) ---');
  for (let i = 1; i <= 6; i++) {
    const now = base + 59_000; // overlap = 1/60 ~ 0.017
    console.log(`req ${i}: ${rl.allow(now) ? 'ALLOW' : 'BLOCK'}`);
  }
}

module.exports = SlidingWindowCounter;
