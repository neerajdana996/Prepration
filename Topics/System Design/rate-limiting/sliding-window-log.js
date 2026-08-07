/**
 * SLIDING WINDOW LOG
 * ==================
 *
 * HOW IT WORKS
 *   Keep the exact timestamp of every accepted request in a log (a queue).
 *   On each request at time `now`:
 *     1. Evict every timestamp older than (now - windowMs). These have slid
 *        out of the trailing window.
 *     2. If the number of remaining timestamps < limit, accept and append
 *        `now`. Otherwise reject.
 *
 *   The window is a TRUE sliding window: it always covers exactly the last
 *   `windowMs`, so it has NO boundary spike. At any instant the count is the
 *   real number of requests in the trailing windowMs.
 *
 * PROS
 *   - Perfectly accurate. No boundary burst (fixes the fixed-window gotcha).
 *   - Naturally answers "how long until I can retry" (oldest timestamp +
 *     windowMs).
 *
 * CONS
 *   - Memory-heavy: O(limit) timestamps stored PER KEY. A limit of 10,000/min
 *     over millions of users is a lot of RAM. In Redis this is a sorted set
 *     (ZADD / ZREMRANGEBYSCORE / ZCARD) whose size scales with the limit.
 *   - More CPU per request than a counter.
 *
 * WHEN TO USE
 *   - When exactness matters and limits are small (e.g. 5 login attempts /
 *     15 min, expensive API calls). Do NOT use for very high limits or huge
 *     key cardinality — the memory blows up; use sliding-window-counter.
 */

class SlidingWindowLog {
  /**
   * @param {number} limit    max requests per trailing window
   * @param {number} windowMs window length in milliseconds
   */
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.log = []; // ascending timestamps of accepted requests
  }

  /**
   * @param {number} now epoch millis
   * @returns {boolean}
   */
  allow(now = Date.now()) {
    const cutoff = now - this.windowMs;

    // 1. Evict timestamps that have slid out of the window.
    //    Log is ascending, so drop from the front until the head is fresh.
    while (this.log.length > 0 && this.log[0] <= cutoff) {
      this.log.shift();
    }

    // 2. Room left in the trailing window?
    if (this.log.length < this.limit) {
      this.log.push(now);
      return true;
    }
    return false;
  }
}

// --------------------------- runnable demo ---------------------------------
if (require.main === module) {
  const rl = new SlidingWindowLog(3, 1000); // 3 requests / 1000ms
  console.log('Sliding window log: limit 3 / 1000ms\n');

  const t = 100_000; // arbitrary base
  const events = [
    [t + 0, '3 will fit'],
    [t + 200, ''],
    [t + 400, ''],
    [t + 600, 'log now holds t+0,+200,+400 -> should BLOCK'],
    [t + 1050, 't+0 (at 1050-1000=50 cutoff) evicted -> room for 1 -> ALLOW'],
    [t + 1100, 'still 3 in last 1000ms (+200,+400,+1050) -> BLOCK'],
  ];

  for (const [ts, note] of events) {
    const ok = rl.allow(ts);
    console.log(
      `t+${String(ts - t).padStart(4)}ms: ${ok ? 'ALLOW' : 'BLOCK'}` +
        (note ? `   (${note})` : '')
    );
  }
}

module.exports = SlidingWindowLog;
