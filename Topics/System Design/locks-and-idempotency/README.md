# Locks, Concurrency & Idempotency

A study/reference pack. Every `.js` file is plain Node.js (no deps) and runnable:

```bash
node optimistic-locking.js
node async-mutex.js
node idempotency.js
```

---

## The core problem

The moment two things touch the same state at the same time — or the same
message gets delivered twice — naive code corrupts data. Three canonical bugs:

### 1. Race condition
Two actors interleave their read/modify/write steps. The classic:

```
Time  Writer A                 Writer B
----  ---------------------    ---------------------
t0    read balance = 100
t1                             read balance = 100
t2    write 100 + 10 = 110
t3                             write 100 - 30 = 70    <-- A's +10 vanished
```

Both read the *same* stale value, both write based on it, and the last write
wins. The intended result was `100 + 10 - 30 = 80`. We got `70`.

### 2. Lost update
The special case above where one committed change is silently overwritten by
another that never saw it. The fix is to make the write *conditional on the
value not having changed since you read it* (optimistic locking) or to *prevent
anyone else from reading it until you're done* (pessimistic locking).

### 3. Double-processing on retries
Networks are unreliable, so almost every real system retries. But a retry can't
tell the difference between "my request was lost" and "my request succeeded but
the *response* was lost." So it resends. Now the payment charges twice, the
order ships twice, the email sends twice.

This is not a bug you can delete — it is a property of distributed systems:

> **At-least-once delivery is the norm.** Exactly-once *delivery* is essentially
> unachievable across an unreliable network. What you can achieve is
> **exactly-once *effect*** by making the receiver **idempotent**.

---

## IDEMPOTENCY (the crisp definition)

> An operation is **idempotent** if performing it **N times has the same
> observable effect as performing it once** (for N >= 1).

`GET`, `PUT`, and `DELETE` are meant to be idempotent; `POST` is not.
`SET x = 5` is idempotent; `x = x + 5` is not.

### Why idempotency is the *real* fix for retries

You cannot reliably prevent duplicates in a distributed system — the sender
cannot know whether a silent failure means "not done" or "done, ack lost," so it
must retry, and retries create duplicates. Locks stop *concurrent* corruption,
but they do nothing about a duplicate that arrives *seconds later* after the
lock is long gone.

So you flip the goal: **stop trying to prevent duplicates and make handling them
safe.** If the operation is idempotent, a duplicate is harmless — the second
attempt is a no-op that returns the same result as the first. That is why
idempotency, not locking, is what makes retries correct.

The usual mechanism is an **idempotency key**: the client attaches a unique key
to the request; the server records `key -> result` the first time and, on any
resend of that key, returns the stored result *without repeating the side
effect*. (See `idempotency.js`.)

---

## Map of the solutions in this folder

| Problem | Tool | File | Reach for it when |
|---|---|---|---|
| Lost update, low contention | Optimistic locking (CAS on a version) | `optimistic-locking.js` | Conflicts are rare; retrying is cheap |
| Lost update, high contention | Pessimistic locking (`SELECT ... FOR UPDATE`) | `pessimistic-locking.md` | Conflicts are common or the op must not fail |
| In-process critical section (JS) | Async mutex | `async-mutex.js` | Serializing async access to shared state in one process |
| Critical section across machines | Distributed lock (Redis + fencing) | `distributed-lock.md` | Only one node may act at a time cluster-wide |
| Safe retries / at-least-once delivery | Idempotency keys | `idempotency.js` | The operation has side effects and *will* be retried |

### How they relate
- **Locking** is about *mutual exclusion in time* — keep concurrent actors from
  stepping on each other *right now*.
- **Idempotency** is about *safety across repetition* — make a repeat of the
  *same* operation harmless, even minutes apart.

They are complementary. A payment endpoint often needs both: an idempotency key
so a client retry doesn't double-charge, **and** a lock (or a CAS) so two
*different* requests don't corrupt the balance concurrently.

---

## One-line takeaways
- Optimistic: *"assume no conflict; verify at write; retry if you lose."*
- Pessimistic: *"assume conflict; block everyone else while I work."*
- Async mutex: *"one at a time, in order, within this process."*
- Distributed lock: *"one holder cluster-wide — with a TTL, a token, and a fence."*
- Idempotency: *"you can't stop duplicates, so make the duplicate a no-op."*
