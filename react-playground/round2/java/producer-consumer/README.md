# Producer / Consumer (bounded buffer)

The classic concurrency problem — and the literal Feb 2026 Cisco Bengaluru question.
Producers add items to a **shared, bounded** buffer; consumers remove them. It must be
**thread-safe**, and threads must **block** (not busy-wait) when the buffer is full/empty.

## Two versions
1. **[`BlockingQueueDemo.java`](BlockingQueueDemo.java)** — production way. An `ArrayBlockingQueue`
   handles all locking/blocking: `put()` blocks when full, `take()` blocks when empty. Lead with this
   ("in real code I'd use a BlockingQueue"), then show you can build it by hand.
2. **[`BoundedBuffer.java`](BoundedBuffer.java)** — hand-rolled with `synchronized` + `wait()`/`notifyAll()`.
   This is what the interviewer usually wants you to implement. Run it with [`ManualDemo.java`](ManualDemo.java).

## The three things they grill you on
1. **`wait()` in a `while`, never an `if`.** After you wake, the condition may no longer hold —
   another thread could have refilled/drained the buffer, or it may be a **spurious wakeup**. Always
   re-check the predicate in a loop.
2. **`notifyAll()` over `notify()`.** With producers *and* consumers waiting on the same lock,
   `notify()` might wake the *wrong kind* (a producer waking another producer) → stall/deadlock.
   `notifyAll()` wakes everyone; the ones whose condition still fails just `wait()` again.
3. **`wait()` releases the lock.** That's the whole point — it frees the monitor so another thread
   can enter the `synchronized` method and eventually `notifyAll()`. (`sleep()` does NOT release the lock.)

## Related follow-ups
- **`Lock` + `Condition`** (`ReentrantLock`, `notFull`/`notEmpty` conditions) — finer control, can
  signal producers vs consumers separately (avoids `notifyAll` waking everyone).
- **Interrupt handling:** on `InterruptedException`, restore the flag (`Thread.currentThread().interrupt()`).

**Soundbite:** *"In production I'd use a `BlockingQueue` — `put` blocks when full, `take` when empty. Hand-rolled, it's `synchronized` + `wait` in a `while` loop (re-check after spurious wakeups) + `notifyAll` (so a producer doesn't only wake another producer), and `wait` releases the lock so others can proceed."*
