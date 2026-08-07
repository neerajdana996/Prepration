/**
 * LEAKY BUCKET  (as a queue)
 * ==========================
 *
 * HOW IT WORKS
 *   Think of a bucket with a hole in the bottom. Incoming requests are water
 *   poured in; they leak out at a CONSTANT rate `leakRatePerSec`. The bucket
 *   holds at most `capacity` queued requests. On arrival:
 *     1. Leak first: remove floor(elapsedSec * leakRatePerSec) items that have
 *        drained since we last looked (lazy, no background timer).
 *     2. If the queue has room (< capacity), enqueue and accept; else reject
 *        (overflow / "bucket full").
 *   Requests then leave the queue at the fixed leak rate regardless of how
 *   bursty the arrivals were.
 *
 * BURST BEHAVIOR
 *   *** SMOOTHS bursts into a steady OUTPUT stream. *** No matter how spiky the
 *   input, the downstream sees a constant, even flow (at most leakRate). Extra
 *   requests wait in the queue; if the queue overflows they are dropped.
 *
 * TOKEN BUCKET vs LEAKY BUCKET (the key contrast)
 *   - Token bucket ALLOWS bursts: if tokens are saved up, `capacity` requests
 *     can pass at once, so downstream can see a spike. It shapes the AVERAGE
 *     rate but not the instantaneous shape.
 *   - Leaky bucket FORBIDS bursts at the output: requests drain at a fixed
 *     rate, so downstream load is smooth/even. It shapes the OUTPUT rate.
 *   => Token bucket = "spend saved-up allowance in a burst".
 *      Leaky bucket = "no matter the input, drip out at a constant rate".
 *
 * PROS
 *   - Constant, predictable outflow — protects fragile downstreams / enforces
 *     a steady processing rate (classic traffic shaping, e.g. network QoS).
 * CONS / GOTCHA
 *   - Adds latency: a request may WAIT in the queue instead of being served
 *     now. Under sustained overload the queue fills and requests are dropped.
 *   - No credit for idleness: unlike token bucket, being quiet does not let
 *     you burst later; you are always capped at the leak rate.
 *
 * WHEN TO USE
 *   - When the downstream needs a smooth, constant request rate (payment
 *     processors, hardware, strict QoS) rather than bursts.
 *
 * NOTE ON MODELING: this class exposes `tryAdd()` (enqueue a request) and
 * `size(now)` (current queue depth after leaking). We model the queue as a
 * count of pending items since all items are identical here.
 */

class LeakyBucket {
  /**
   * @param {number} capacity        max queued requests
   * @param {number} leakRatePerSec  requests drained per second
   */
  constructor(capacity, leakRatePerSec) {
    this.capacity = capacity;
    this.leakRatePerSec = leakRatePerSec;
    this.queue = 0;              // number of pending (not-yet-leaked) requests
    this.lastLeak = Date.now();
  }

  /** Lazily drain the queue for time elapsed since lastLeak. */
  _leak(now) {
    const elapsedSec = (now - this.lastLeak) / 1000;
    const leaked = elapsedSec * this.leakRatePerSec;
    if (leaked <= 0) return;
    this.queue = Math.max(0, this.queue - leaked);
    this.lastLeak = now;
  }

  /**
   * Try to enqueue one request.
   * @param {number} now epoch millis
   * @returns {boolean} true if accepted into the queue, false if it overflowed
   */
  tryAdd(now = Date.now()) {
    this._leak(now);
    if (this.queue + 1 <= this.capacity) {
      this.queue += 1;
      return true;
    }
    return false; // bucket full -> drop
  }

  /** Current queue depth after leaking (for inspection). */
  size(now = Date.now()) {
    this._leak(now);
    return this.queue;
  }
}

// --------------------------- runnable demo ---------------------------------
if (require.main === module) {
  // capacity 5 queued, leak 1 request/sec.
  const rl = new LeakyBucket(5, 1);
  console.log('Leaky bucket: capacity 5, leak 1 request/sec\n');

  // Base on real now so it lines up with the constructor's lastLeak.
  const t = Date.now();

  // Spike of 8 arrivals at once: only 5 fit in the queue, 3 overflow.
  console.log('--- burst of 8 arrivals at t=0 ---');
  for (let i = 1; i <= 8; i++) {
    const ok = rl.tryAdd(t);
    console.log(`req ${i}: ${ok ? 'QUEUED' : 'DROP '}  (queue=${rl.size(t).toFixed(2)})`);
  }

  // After 3s, 3 requests have leaked out (drained downstream at 1/sec).
  console.log(`\n--- at t=3000ms, 3 leaked out -> queue=${rl.size(t + 3000).toFixed(2)} ---`);
  for (let i = 1; i <= 4; i++) {
    const ok = rl.tryAdd(t + 3000);
    console.log(`req ${i}: ${ok ? 'QUEUED' : 'DROP '}  (queue=${rl.size(t + 3000).toFixed(2)})`);
  }

  console.log(
    '\nDownstream drains at a constant 1/sec no matter how bursty arrivals',
    'are; overflow beyond capacity is dropped. Output is SMOOTH.'
  );
}

module.exports = LeakyBucket;
