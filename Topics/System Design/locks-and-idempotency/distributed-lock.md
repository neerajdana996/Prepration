# Distributed Locks (Redis)

An async mutex works within **one process**. When "only one actor may do X at a
time" must hold across **many machines** (e.g. only one worker runs a nightly
job, only one node processes an account), you need a lock that lives *outside*
all of them — a **distributed lock**. Redis is the common choice.

## Acquiring: `SET key value NX PX ttl`

```
# Acquire: set the lock key ONLY IF it does not already exist (NX),
# with an auto-expiry (PX = milliseconds). Store a UNIQUE RANDOM TOKEN
# as the value so we can later prove WE own it.
SET lock:job42 <random-token> NX PX 30000

#   NX      -> only set if absent  => mutual exclusion (only one winner)
#   PX 30000-> expire after 30s     => lock auto-frees if the holder dies
# Reply is OK if you got the lock, nil if someone else holds it.
```

### Why the TTL matters
Without an expiry, a holder that **crashes** (or GC-pauses, or gets network
-partitioned) never releases the lock — it's held **forever** and the whole
system wedges. The TTL is a dead-man's switch: worst case the lock frees itself
after `ttl`. The trade-off: set it too short and it can expire *while you're
still working* (see fencing below).

### Why the TOKEN matters
The value is a unique random token identifying *this* acquisition. It exists to
solve one specific danger on **release**:

> Holder A acquires. A stalls (long GC pause). The TTL expires and the lock
> auto-frees. Holder B acquires the same lock. A wakes up and calls "delete the
> lock" — **deleting B's lock**, not its own.

So release must be: *"delete the key ONLY IF its value is still my token."* That
check-then-delete has to be **atomic**, which plain commands can't guarantee —
hence a Lua script (Redis runs a script atomically).

## Releasing: atomic check-token-then-delete (Lua)

```lua
-- release.lua  --  KEYS[1] = lock key, ARGV[1] = my token
-- Delete the lock ONLY IF I still own it. Never delete someone else's lock.
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

```
# Invoke it:
EVAL "<the script above>" 1 lock:job42 <random-token>
```

## Redlock and its criticism

**Redlock** is Redis's algorithm for locking across N *independent* Redis
masters (typically 5): acquire the lock on a majority (>= 3 of 5) within a time
budget, and you "hold" it. It exists so a single Redis failover can't hand the
same lock to two clients.

The well-known criticism (**Martin Kleppmann vs. antirez**):
- Redlock leans on **wall-clock time and bounded delays**. But a process can
  pause arbitrarily (GC, VM migration, CPU starvation), and clocks can jump
  (NTP steps). During such a pause, your lock can expire and be granted to
  someone else **while you still believe you hold it** — no counting of Redis
  nodes fixes that.
- Therefore: for **efficiency** (avoid duplicate work, usually harmless) a
  simple single-Redis lock is fine. For **correctness** (must *never* have two
  holders mutate shared state) a lock alone is **not safe** — you also need
  **fencing**.

## Fencing tokens (the real safety net)

A **fencing token** is a **monotonically increasing number** handed out with
each lock grant (grant #33, then #34, then #35 — never reused, always larger).

The client passes its token to the **protected resource** (DB, storage,
service) on every write, and **the resource rejects any write whose token is
lower than the highest it has already seen.**

```
Client A gets lock, token = 33.  A pauses (GC).
Lock expires. Client B gets lock, token = 34.
B writes to storage with token 34.  Storage records "last seen = 34".
A wakes up (still thinks it holds the lock) and writes with token 33.
Storage: 33 < 34  -> REJECT.        <-- the stale holder is fenced off
```

This is what makes distributed locking *correct* rather than merely
best-effort: even if two clients simultaneously believe they hold the lock, the
downstream resource lets only the newer token through. The lock provides
mutual-exclusion *most* of the time; the fence guarantees safety when it fails.

## Summary
- `SET key token NX PX ttl` to acquire (NX = exclusivity, PX = dead-man switch).
- Release with a **Lua** script that DELs **only if the token matches** — never
  delete another holder's lock.
- **TTL** prevents a dead holder from wedging the system; **token** prevents
  deleting someone else's lock.
- **Redlock** raises availability but not correctness; for correctness add
  **fencing tokens** so a stale holder's writes are rejected downstream.
- For a bulletproof design, combine a distributed lock (liveness) with fencing
  tokens **or** with an idempotent resource (safety).
