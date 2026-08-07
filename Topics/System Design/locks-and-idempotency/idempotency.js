/**
 * idempotency.js
 * -----------------------------------------------------------------------------
 * IDEMPOTENCY KEYS: make retries safe by making a repeat a no-op.
 *
 * You cannot prevent duplicates in a distributed system -- a client that gets
 * no response can't tell "it failed" from "it succeeded but the ack was lost,"
 * so it retries, and retries create duplicates. The fix is not to stop the
 * duplicate but to make it HARMLESS:
 *
 *   - The client attaches a unique IDEMPOTENCY KEY to the request.
 *   - The server keeps a store: key -> stored result.
 *   - First time it sees a key: perform the side effect (charge the card),
 *     store the result under the key, return it.
 *   - Any later request with the SAME key: return the STORED result WITHOUT
 *     repeating the side effect.
 *
 * Result: N calls with the same key => the effect happens exactly once, and
 * every caller gets the same answer. That's exactly-once *effect* on top of
 * at-least-once *delivery*.
 *
 * HTTP note: GET/PUT/DELETE are supposed to be idempotent by design; POST is
 * NOT -- which is exactly why payment/order POST endpoints take an
 * "Idempotency-Key" header (Stripe does this) to bolt idempotency onto POST.
 *
 * Outbox pattern (reference): to make "update DB AND publish an event" atomic,
 * write the event into an `outbox` table in the SAME transaction as the state
 * change, then a relay publishes it at-least-once. Consumers dedupe by the
 * event id -- i.e. they, too, rely on idempotency downstream.
 *
 * Run: node idempotency.js
 * -----------------------------------------------------------------------------
 */

'use strict';

// The idempotency store. In production this is Redis / a DB table, and entries
// carry a TTL. We store the in-flight PROMISE (not just the final value) so
// that two CONCURRENT requests with the same key also collapse to one charge --
// the second finds the in-flight promise and awaits the same result.
const idempotencyStore = new Map(); // key -> Promise<result>

// A side-effect ledger so we can PROVE the card was charged only once.
const ledger = { chargeCount: 0, charges: [] };

// The real, non-idempotent side effect: actually move money. Calling this twice
// charges twice -- that's the whole danger we're guarding against.
async function reallyChargeCard(customer, amountCents) {
  await new Promise((r) => setTimeout(r, 10)); // simulate a payment-gateway call
  ledger.chargeCount += 1;
  const charge = {
    id: `ch_${ledger.chargeCount}`,
    customer,
    amountCents,
  };
  ledger.charges.push(charge);
  return charge;
}

/**
 * Idempotent wrapper around reallyChargeCard.
 * Same idempotencyKey => the card is charged at most once; all callers get the
 * same charge object.
 */
function chargePayment(idempotencyKey, customer, amountCents) {
  // Already seen this key (finished OR in flight)? Return the same promise --
  // no new side effect.
  if (idempotencyStore.has(idempotencyKey)) {
    console.log(`[key ${idempotencyKey}] HIT  -> returning stored result, NOT charging again`);
    return idempotencyStore.get(idempotencyKey);
  }

  console.log(`[key ${idempotencyKey}] MISS -> performing charge`);

  // Store the in-flight promise BEFORE awaiting, so a concurrent duplicate sees
  // it and joins in rather than starting a second charge.
  const resultPromise = reallyChargeCard(customer, amountCents).catch((err) => {
    // If the charge FAILS, drop the key so the client can genuinely retry.
    // (Only cache SUCCESSES; a cached failure would make retries pointless.)
    idempotencyStore.delete(idempotencyKey);
    throw err;
  });

  idempotencyStore.set(idempotencyKey, resultPromise);
  return resultPromise;
}

async function main() {
  const KEY = 'idem-abc-123';

  console.log('--- Two SEQUENTIAL requests with the same idempotency key ---');
  const first = await chargePayment(KEY, 'cust_42', 5000);
  console.log('  1st returned:', first);

  // e.g. the client never got the response and retries with the SAME key.
  const retry = await chargePayment(KEY, 'cust_42', 5000);
  console.log('  retry returned:', retry);

  console.log('\n--- Two CONCURRENT requests with the SAME key (double-submit) ---');
  const KEY2 = 'idem-xyz-999';
  const [a, b] = await Promise.all([
    chargePayment(KEY2, 'cust_7', 2500),
    chargePayment(KEY2, 'cust_7', 2500),
  ]);
  console.log('  concurrent A:', a);
  console.log('  concurrent B:', b);

  console.log('\n--- A genuinely different request (new key) charges normally ---');
  const other = await chargePayment('idem-diff-777', 'cust_99', 100);
  console.log('  other returned:', other);

  console.log('\nLedger:');
  console.log('  total charges executed =', ledger.chargeCount);
  console.log('  charges =', ledger.charges);

  // We issued 5 chargePayment() calls but only 3 UNIQUE keys, so exactly 3
  // real charges should have happened. Same-key returns are byte-identical.
  const pass =
    ledger.chargeCount === 3 &&
    first.id === retry.id && // retry returned the SAME charge, no new money moved
    a.id === b.id;           // concurrent duplicate collapsed to one charge
  console.log(
    pass
      ? '\nPASS: same key -> charged once; each caller got the same result.'
      : '\nFAIL: idempotency did not hold.'
  );
}

main();
