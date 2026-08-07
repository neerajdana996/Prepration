/**
 * optimistic-locking.js
 * -----------------------------------------------------------------------------
 * OPTIMISTIC LOCKING via compare-and-swap (CAS) on a VERSION field.
 *
 * Idea: don't lock anything up front. Assume conflicts are rare ("optimistic").
 *   1. READ the record: you get (value, version).
 *   2. COMPUTE a new value from what you read.
 *   3. WRITE it back ONLY IF the version is still what you read.
 *        - If it matches: your write wins and the version is bumped.
 *        - If it changed: someone else committed in between -> your write is
 *          rejected, and you RETRY from step 1 with the fresh value.
 *
 * No blocking, no held locks. The cost of a conflict is just re-doing the work.
 * >>> Best for LOW CONTENTION: if conflicts are rare, retries are rare, and you
 *     paid nothing to hold a lock. Under high contention this degrades into a
 *     retry storm -- use pessimistic locking there.
 *
 * Run: node optimistic-locking.js
 * -----------------------------------------------------------------------------
 */

'use strict';

// A tiny in-memory "row" with an optimistic version counter, standing in for a
// DB row that has a `version` column (or an ETag in an HTTP world).
const db = {
  row: { value: 100, version: 0 },

  // Simulated async READ. Returns a COPY so callers can't mutate the row
  // directly -- they must go through compareAndSwap.
  async read() {
    await tick();
    return { value: this.row.value, version: this.row.version };
  },

  // Simulated async CONDITIONAL WRITE. This is the atomic heart of optimistic
  // locking. In a real DB this is: UPDATE t SET value=?, version=version+1
  //                                WHERE id=? AND version=?  (0 rows => conflict)
  async compareAndSwap(expectedVersion, newValue) {
    await tick();
    if (this.row.version !== expectedVersion) {
      return false; // conflict: someone bumped the version since we read
    }
    this.row.value = newValue;
    this.row.version += 1;
    return true; // success
  },
};

// Yield to the event loop so our two writers actually interleave, the way two
// real clients hitting the same row would.
function tick() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

/**
 * Apply `delta` to the row using read -> compute -> CAS, retrying on conflict.
 * Returns how many attempts it took (1 = clean, >1 = it lost a race and retried).
 */
async function applyDelta(name, delta) {
  let attempts = 0;
  while (true) {
    attempts += 1;

    // 1. READ
    const { value, version } = await db.read();
    console.log(`${name}: read value=${value} version=${version} (attempt ${attempts})`);

    // 2. COMPUTE
    const newValue = value + delta;

    // 3. CONDITIONAL WRITE
    const ok = await db.compareAndSwap(version, newValue);
    if (ok) {
      console.log(`${name}: CAS OK  -> wrote ${newValue} (bumped version to ${version + 1})`);
      return attempts;
    }

    // Lost the race: fall through and retry with fresh data.
    console.log(`${name}: CAS FAIL -> version moved on, retrying`);
  }
}

async function main() {
  console.log('Start: value =', db.row.value, '\n');

  // Two concurrent writers both start by reading version 0. Only one CAS can
  // succeed at version 0; the other must retry against the new version.
  const [attemptsA, attemptsB] = await Promise.all([
    applyDelta('WriterA(+10)', +10),
    applyDelta('WriterB(-30)', -30),
  ]);

  console.log('\nEnd: value =', db.row.value, `(version ${db.row.version})`);
  console.log(`WriterA attempts=${attemptsA}, WriterB attempts=${attemptsB}`);

  // Correctness check: 100 + 10 - 30 = 80. Neither update was lost.
  const expected = 100 + 10 - 30;
  console.log(
    db.row.value === expected
      ? `PASS: no lost update (got ${db.row.value})`
      : `FAIL: lost update! got ${db.row.value}, expected ${expected}`
  );
}

main();
