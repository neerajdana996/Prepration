/**
 * FIXED WINDOW COUNTER
 * ====================
 *
 * HOW IT WORKS
 *   Time is chopped into fixed, non-overlapping windows of size `windowMs`
 *   (e.g. [0s,60s), [60s,120s), ...). Each window has ONE counter. Every
 *   request in the current window increments the counter. If the counter is
 *   already at `limit`, reject. When wall-clock crosses into a new window,
 *   the counter resets to 0.
 *
 *   The window a timestamp belongs to is:  floor(now / windowMs).
 *
 * PROS
 *   - Trivial to implement, O(1) time, O(1) memory per key (a count + a
 *     window id). This is why it is the cheapest option in Redis (INCR + EXPIRE).
 *
 * CONS / THE GOTCHA
 *   - *** 2x BURST AT THE WINDOW BOUNDARY ***
 *     Because each window is scored independently, a client can send `limit`
 *     requests at the very END of one window and another `limit` at the very
 *     START of the next. Those 2*limit requests land inside a span shorter
 *     than one windowMs, yet both windows individually look legal.
 *
 *     Example: limit = 5 per 60s window.
 *       t = 59.9s  -> 5 requests, window [0,60) counter = 5  (allowed)
 *       t = 60.1s  -> 5 requests, window [60,120) counter = 5 (allowed)
 *     => 10 requests in ~0.2s, i.e. 2x the intended rate. Sliding-window
 *        algorithms exist specifically to kill this spike.
 *
 * WHEN TO USE
 *   - When approximate limiting is fine and you want the cheapest possible
 *     implementation (coarse quotas, "X requests per hour" billing tiers).
 *   - Avoid when boundary bursts can hurt you (e.g. protecting a fragile
 *     downstream) — reach for a sliding window instead.
 */

class FixedWindowCounter {
  /**
   * @param {number} limit    max requests allowed per window
   * @param {number} windowMs window size in milliseconds
   */
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.count = 0;
    this.windowId = -1; // floor(now / windowMs) of the current window
  }

  /**
   * @param {number} now epoch millis (injectable so demos/tests are deterministic)
   * @returns {boolean} true if allowed, false if rate-limited
   */
  allow(now = Date.now()) {
    const currentWindow = Math.floor(now / this.windowMs);

    // New window? Reset the counter. (In Redis this reset is implicit: the
    // key expires after windowMs, so a fresh INCR starts at 1.)
    if (currentWindow !== this.windowId) {
      this.windowId = currentWindow;
      this.count = 0;
    }

    if (this.count < this.limit) {
      this.count++;
      return true;
    }
    return false;
  }
}

// --------------------------- runnable demo ---------------------------------
if (require.main === module) {
  const limit = 5;
  const windowMs = 60_000; // 60s
  const rl = new FixedWindowCounter(limit, windowMs);

  console.log('Fixed window: limit 5 / 60s\n');

  // Base time aligned to a window start for clean numbers.
  const base = 60_000 * 1000; // some window boundary

  // Fire 5 near the END of window [base-60s, base).
  console.log('--- End of window 1 (t = base-100ms) ---');
  for (let i = 1; i <= 6; i++) {
    const ok = rl.allow(base - 100);
    console.log(`req ${i}: ${ok ? 'ALLOW' : 'BLOCK'}`);
  }

  // Fire 5 at the START of the next window [base, base+60s).
  console.log('\n--- Start of window 2 (t = base+100ms) ---');
  for (let i = 1; i <= 6; i++) {
    const ok = rl.allow(base + 100);
    console.log(`req ${i}: ${ok ? 'ALLOW' : 'BLOCK'}`);
  }

  console.log(
    '\nGOTCHA: 5 allowed at base-100ms + 5 allowed at base+100ms',
    '=> 10 requests in ~200ms, 2x the intended 5/60s rate.'
  );
}

module.exports = FixedWindowCounter;
