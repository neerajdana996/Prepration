/**
 * async-mutex.js
 * -----------------------------------------------------------------------------
 * A working promise-based ASYNC MUTEX for JavaScript critical sections.
 *
 * Why does single-threaded JS need a mutex at all? Because `await` yields the
 * event loop. Between an `await` and the next line, ANOTHER async task can run
 * and mutate your shared state. So a "read -> await -> write" sequence is a
 * classic interleaving hazard even without threads. A mutex serializes those
 * critical sections: one holder at a time, and waiters are served FIFO.
 *
 * Contract:
 *   const release = await mutex.acquire();
 *   try { ...critical section... } finally { release(); }
 *
 * acquire() resolves once you hold the lock, and gives you a release() function.
 * You MUST call release() (use try/finally) or the lock is held forever and
 * every waiter hangs.
 *
 * This is a common machine-coding / interview question, so the implementation
 * below is deliberately small and self-contained.
 *
 * Run: node async-mutex.js
 * -----------------------------------------------------------------------------
 */

'use strict';

class Mutex {
  constructor() {
    this._locked = false;
    this._waiters = []; // queue of resolve fns waiting for the lock (FIFO)
  }

  /**
   * Acquire the lock. Resolves with a release() function once you hold it.
   * If free -> take it immediately. If held -> queue up and resolve later.
   */
  acquire() {
    return new Promise((resolve) => {
      if (!this._locked) {
        this._locked = true;
        resolve(this._makeRelease());
      } else {
        this._waiters.push(resolve);
      }
    });
  }

  /**
   * Build a single-use release fn. Guarding against double-release matters:
   * calling release() twice must not hand the lock to two waiters at once.
   */
  _makeRelease() {
    let released = false;
    return () => {
      if (released) return; // idempotent release: second call is a no-op
      released = true;

      if (this._waiters.length > 0) {
        // Hand the lock DIRECTLY to the next waiter -- stays locked, no gap
        // where a newcomer could jump the queue.
        const nextResolve = this._waiters.shift();
        nextResolve(this._makeRelease());
      } else {
        this._locked = false;
      }
    };
  }

  /** Convenience: run fn() while holding the lock, always releasing after. */
  async runExclusive(fn) {
    const release = await this.acquire();
    try {
      return await fn();
    } finally {
      release();
    }
  }
}

// ---------------------------------------------------------------------------
// DEMO: a shared counter updated with an await in the middle of the critical
// section (the dangerous read -> await -> write pattern).
// ---------------------------------------------------------------------------

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function unsafeIncrement(shared, name) {
  const read = shared.count;          // read
  await delay(10);                    // yield: another task can run HERE
  shared.count = read + 1;            // write based on the STALE read
  console.log(`  ${name}: wrote ${shared.count}`);
}

async function safeIncrement(mutex, shared, name) {
  await mutex.runExclusive(async () => {
    const read = shared.count;        // read
    await delay(10);                  // yield -- but the mutex keeps us alone
    shared.count = read + 1;          // write
    console.log(`  ${name}: wrote ${shared.count}`);
  });
}

async function main() {
  const N = 5;

  // 1) WITHOUT the mutex: all 5 read 0, all await, all write 1. Lost updates.
  console.log('Without mutex (5 concurrent increments):');
  const unsafe = { count: 0 };
  await Promise.all(
    Array.from({ length: N }, (_, i) => unsafeIncrement(unsafe, `task${i}`))
  );
  console.log(`  final count = ${unsafe.count} (expected ${N})  <-- lost updates\n`);

  // 2) WITH the mutex: increments run one at a time, in order. No lost updates.
  console.log('With mutex (5 concurrent increments):');
  const mutex = new Mutex();
  const safe = { count: 0 };
  await Promise.all(
    Array.from({ length: N }, (_, i) => safeIncrement(mutex, safe, `task${i}`))
  );
  console.log(`  final count = ${safe.count} (expected ${N})`);

  console.log(
    safe.count === N
      ? '\nPASS: mutex serialized the critical section.'
      : '\nFAIL: mutex did not serialize correctly.'
  );
}

main();



function debounce(fn,delay){
  let timeout = null;
  return function (...args) {
   clearTimeout(timeout)
   timeout= setTimeout(() => fn.apply(this,args), delay);
  }
}