/**
 * TOKEN BUCKET
 * ============
 *
 * HOW IT WORKS
 *   A bucket holds up to `capacity` tokens and refills at `refillRatePerSec`
 *   tokens/second. Each request costs 1 token (could be N). If a token is
 *   available, spend it and allow; otherwise reject.
 *
 *   LAZY REFILL (no background timer): we do NOT run a setInterval topping up
 *   the bucket. Instead, on each request we compute how much time has elapsed
 *   since the last refill and add `elapsedSec * refillRatePerSec` tokens,
 *   capped at `capacity`. This is O(1), stateless between calls except for
 *   two numbers (tokens, lastRefill), and works perfectly in a distributed
 *   store where a background timer is impractical.
 *
 * BURST BEHAVIOR
 *   *** ALLOWS BURSTS up to `capacity`. *** If the bucket is full, a client
 *   can fire `capacity` requests instantly, then is throttled to the steady
 *   refill rate. This is usually DESIRABLE: it absorbs legitimate spikes while
 *   still bounding the long-run average rate.
 *
 * PROS
 *   - Bursts allowed but average rate bounded. O(1) memory/time. Simple.
 *   - Industry default for API rate limiting (AWS, Stripe, GCP all use it).
 *
 * CONS / GOTCHA
 *   - Because it permits bursts, the INSTANTANEOUS load on downstream can be
 *     up to `capacity` at once — if the downstream cannot tolerate spikes,
 *     you want smoothing (leaky bucket) instead.
 *   - Watch float precision on tokens; and in a distributed setting the
 *     refill+consume must be ATOMIC (Redis Lua) or two nodes double-spend.
 *
 * WHEN TO USE
 *   - Default for user/API rate limiting where short bursts are fine and you
 *     care about the average rate.
 */

class TokenBucket {
  /**
   * @param {number} capacity         max tokens (= max burst size)
   * @param {number} refillRatePerSec tokens added per second
   */
  constructor(capacity, refillRatePerSec) {
    this.capacity = capacity;
    this.refillRatePerSec = refillRatePerSec;
    this.tokens = capacity;      // start full
    this.lastRefill = Date.now();
  }

  /** Lazily add tokens for the time elapsed since lastRefill. */
  _refill(now) {
    const elapsedSec = (now - this.lastRefill) / 1000;
    if (elapsedSec <= 0) return;
    this.tokens = Math.min(
      this.capacity,
      this.tokens + elapsedSec * this.refillRatePerSec
    );
    this.lastRefill = now;
  }

  /**
   * @param {number} now    epoch millis
   * @param {number} cost   tokens this request costs (default 1)
   * @returns {boolean}
   */
  allow(now = Date.now(), cost = 1) {
    this._refill(now);
    if (this.tokens >= cost) {
      this.tokens -= cost;
      return true;
    }
    return false;
  }
}



class TokenBucketNew {
  constructor(capacity,refillRatePerSec) {
    this.capacity = capacity;
    this.refillRatePerSec = refillRatePerSec;
    this.token = this.capacity
    this.last = Date.now()  
  }

  allow(){
    const now = Date.now()
    this.token = Math.min(this.capacity,this.token+((now-this.last)/1000)*this.refillRatePerSec)
    this.last = now;
    if(this.token > 1) {
      this.token--;
     
      return true
    }
    return false
  }
}

// --------------------------- runnable demo ---------------------------------
if (require.main === module) {
  // capacity 5, refill 1 token/sec.
  const rl = new TokenBucket(5, 1);
  console.log('Token bucket: capacity 5, refill 1 token/sec\n');

  // Base on real now so it lines up with the constructor's lastRefill.
  const t = Date.now();

  // Instant burst: bucket starts full with 5 tokens.
  console.log('--- burst of 7 at t=0 (bucket full = 5 tokens) ---');
  for (let i = 1; i <= 7; i++) {
    console.log(`req ${i}: ${rl.allow(t) ? 'ALLOW' : 'BLOCK'}  (tokens=${rl.tokens.toFixed(2)})`);
  }

  // Wait 2s -> refill 2 tokens.
  console.log('\n--- after waiting 2s (t=2000ms), 2 tokens refilled ---');
  for (let i = 1; i <= 3; i++) {
    console.log(`req ${i}: ${rl.allow(t + 2000) ? 'ALLOW' : 'BLOCK'}  (tokens=${rl.tokens.toFixed(2)})`);
  }

  console.log(
    '\nBursts up to capacity (5) allowed instantly, then throttled to the',
    '1/sec steady refill rate.'
  );
}

module.exports = TokenBucket;
