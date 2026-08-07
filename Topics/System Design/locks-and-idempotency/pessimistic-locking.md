# Pessimistic Locking (`SELECT ... FOR UPDATE`)

**Optimistic** assumes conflicts are rare and checks at write time.
**Pessimistic** assumes conflicts are likely and *prevents* them up front by
taking a lock the moment you read.

## The concept

Inside a transaction, `SELECT ... FOR UPDATE` reads a row **and locks it**. Any
other transaction that tries to `SELECT ... FOR UPDATE` (or `UPDATE`) the same
row **blocks** until you `COMMIT` or `ROLLBACK`. So the read-modify-write is
serialized — no one else can even *see-for-update* the row while you hold it.

```sql
BEGIN;

-- Lock the row. Concurrent writers now WAIT here.
SELECT balance FROM accounts WHERE id = 42 FOR UPDATE;

-- Safe: nobody else can touch row 42 until we commit.
UPDATE accounts SET balance = balance - 30 WHERE id = 42;

COMMIT;  -- lock released
```

Contrast with optimistic locking: there you read freely, compute, and let the
conditional write fail if the version moved. Here you *pay the cost of a lock
before* the conflict, and in exchange the write is guaranteed not to fail from a
concurrent update.

## When to use it

- **High contention** — many writers hit the same row. Optimistic locking would
  turn into a retry storm (everyone reads, everyone loses the CAS, everyone
  retries). A lock makes them queue instead of spin.
- **The operation must not fail / must not be retried** — e.g. a long,
  expensive, or side-effecting computation you don't want to redo, or a
  correctness-critical debit where "just retry" is undesirable.
- **You need to lock multiple related rows** as a consistent set for the
  duration of the transaction.

Rule of thumb: **rare conflicts -> optimistic; frequent conflicts or
must-not-fail -> pessimistic.**

## The costs

- **Blocking / reduced throughput** — waiters sit idle holding a DB connection.
  Long transactions under a hot lock destroy concurrency. Keep the critical
  section short; never do network calls or user interaction while holding a row
  lock.
- **Deadlocks** — two transactions each hold a lock the other needs:
  ```
  T1: locks row A, then wants row B
  T2: locks row B, then wants row A   -> deadlock
  ```
  The DB detects this and kills one transaction (a deadlock victim). You must be
  prepared to catch that error and retry the whole transaction.
- **Lock-ordering discipline** — the standard defense against deadlock: **always
  acquire locks in a consistent global order** (e.g. always lock the
  lower `id` first). If everyone locks A-before-B, the cycle above can't form.
- **Lock timeouts / `NOWAIT` / `SKIP LOCKED`** — bound how long you'll wait.
  `FOR UPDATE NOWAIT` fails fast instead of blocking; `FOR UPDATE SKIP LOCKED`
  is the classic pattern for pulling jobs off a queue table without contending
  on already-claimed rows.

## One-liner
> Pessimistic locking trades throughput for a guarantee: "I hold this row, no
> one else may change it until I'm done." Keep the hold short, lock in a fixed
> order, and be ready to retry deadlock victims.
