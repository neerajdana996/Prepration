# Messaging & Kafka — Principal-depth reference

A companion `mini-kafka.js` in this folder is a runnable, in-memory model of
everything below (`node mini-kafka.js`). Read the concept, then read the code —
the code is the concept made mechanical.

---

## 0. The one-sentence mental model

**Kafka is a distributed, append-only, replayable LOG that you partition for
parallelism.** It is *not* a queue that deletes messages on read. Understanding
that single distinction unlocks almost every design decision that follows.

---

## 1. Queue vs Log — the foundational distinction

| | Classic **queue** (RabbitMQ / SQS) | **Log** (Kafka) |
|---|---|---|
| On consume | message is **removed** (delete-on-ack) | message **stays**; consumer advances a cursor (offset) |
| Who tracks progress | the broker (per message) | the **consumer** (per group, an offset) |
| Re-read old data | impossible once acked | trivial — reset the offset and **replay** |
| Multiple independent readers | need multiple queues / fan-out exchange | many consumer groups read the *same* log independently |
| Ordering | weak/none across the queue | **per-partition** total order |
| Natural fit | task distribution, RPC-ish work | event streaming, audit, replay, multiple consumers |

A queue answers "give me the next job and forget it." A log answers "here is the
ordered history of what happened; each reader remembers how far it has read."

Because the log is retained, Kafka gives you things a queue can't: **replay**
(re-process history after a bug fix), **multiple independent consumers** of the
same stream, and a **buffer** that absorbs bursts.

---

## 2. Topic and Partition

- A **topic** is a named stream of records ("orders", "clicks", "payments").
- A topic is split into **partitions**. Each partition is an **independent
  append-only log**: records are appended to the end and each gets a
  monotonically increasing **offset** (0, 1, 2, …) that never changes.

Partitions are the single most important concept. They are simultaneously:

1. **The unit of parallelism.** Different partitions can live on different
   brokers and be read by different consumers at the same time. More partitions
   = more possible concurrency.
2. **The unit of ordering.** Kafka guarantees total order **only within a
   partition**. There is **no global order across partitions.** If two events
   must be processed in order relative to each other, they must land in the
   **same partition** (see the producer's keying below).

> Ordering is guaranteed only WITHIN a partition. Say it out loud in interviews;
> it is the root of most Kafka design trade-offs.

Choosing partition count is a real trade-off: too few caps your consumer
parallelism (see §5); too many adds overhead (open files, leader elections,
rebalance cost, more end-to-end latency) and — crucially — you can **increase**
partitions later but not easily decrease them, and increasing them **breaks
key→partition stickiness** for existing keys.

---

## 3. Producer

The producer decides **which partition** each record goes to. That decision is
the **partitioner**:

- **Keyed record** → `partition = hash(key) % numPartitions`.
  Deterministic, so **the same key always maps to the same partition** → all
  records for that key are in one log → they are **ordered**. (e.g. all events
  for `user-A` go to one partition, so "placed" always precedes "cancelled".)
- **Keyless record** → **round-robin** (or "sticky" batching) across
  partitions. Spreads load evenly but gives **no ordering** guarantee between
  those records.

### acks — the durability knob

`acks` controls how many replicas must confirm a write before the producer
considers it successful:

| `acks` | Waits for | Durability | Latency | Risk |
|---|---|---|---|---|
| `0` | nothing (fire-and-forget) | lowest | lowest | data lost if broker drops it |
| `1` | **leader** only | medium | medium | lost if leader dies before followers copy it |
| `all` (`-1`) | leader **+ all in-sync replicas (ISR)** | highest | highest | no loss while ≥1 ISR survives |

`acks=all` combined with `min.insync.replicas ≥ 2` is the standard durable
config: a write is acknowledged only once it is on multiple replicas.

**Idempotent producer** (`enable.idempotence=true`): the producer tags records
with a producer id + sequence number so a retry after a network blip does **not**
create a duplicate on the log. This turns producer-side retries from
"at-least-once" into "exactly-once *to the log*."

---

## 4. Broker & Replication

A **broker** is a server that stores partitions and serves reads/writes. A
cluster is many brokers.

For each partition there is:

- **1 leader** replica — all reads and writes for that partition go through it.
- **N-1 follower** replicas — they continuously copy the leader's log.

The **ISR (In-Sync Replica set)** is the leader plus every follower that is
caught up "recently enough." Key rules:

- A write with `acks=all` is acknowledged only after **all ISR members** have it.
- If the leader dies, a **new leader is elected from the ISR** — so no
  acknowledged data is lost (as long as an ISR member survives).
- `min.insync.replicas` sets the floor: if the ISR shrinks below it, the
  partition **rejects writes** rather than risk under-replicated (loss-prone)
  data. Durability over availability.

Replication factor 3 + `acks=all` + `min.insync.replicas=2` is the canonical
"don't lose data" setup: tolerate one broker failure and still accept writes.

---

## 5. Consumer & Consumer Group

A **consumer** reads records from partitions. Consumers organize into a
**consumer group** (identified by a `group.id`).

**The core rule:** within a group, **each partition is consumed by exactly ONE
consumer.** A consumer may own several partitions, but a partition is never
split across two consumers of the same group.

Consequences:

- **Partitions cap parallelism.** With 3 partitions you can usefully run at most
  3 consumers in a group. A **4th consumer sits idle** — there is no partition
  left to give it without violating the one-owner rule. To scale consumers, you
  must first add partitions.
- **Different groups are independent.** Group `analytics` and group `billing`
  each read the full topic and keep their own offsets. This is fan-out for free.

### Rebalancing

When a consumer joins, leaves, or crashes, the group **rebalances**: partitions
are re-assigned among the surviving consumers so the one-owner rule still holds.
During a (stop-the-world) rebalance, consumption briefly pauses. Frequent
rebalances (from flapping consumers or long processing pauses that miss
heartbeats) are a common production pain point; cooperative/incremental
rebalancing and tuned `max.poll.interval.ms` mitigate it.

---

## 6. Offsets & delivery semantics

An **offset** is a per-group, per-partition **cursor**: "group G has processed
partition P up to offset N." Committing an offset persists that cursor (Kafka
stores it in an internal `__consumer_offsets` topic).

**The commit strategy decides your delivery guarantee** — this is the part
people get wrong:

- **At-most-once** — **commit the offset BEFORE processing.** If you crash after
  committing but before finishing, the record is skipped. No duplicates, but
  possible **loss**. Fine for lossy metrics.
- **At-least-once** — **commit AFTER processing** (the default, safe choice). If
  you crash after processing but before committing, you re-read the record on
  restart → possible **duplicates**, never loss. Your consumer must therefore be
  **idempotent** (dedupe by key or by offset). This is exactly what
  `mini-kafka.js` demonstrates: a re-poll before `commit()` re-delivers.
- **Exactly-once** — needs more than offsets. Achieved via the **idempotent
  producer** + **transactions**: the consume→process→produce cycle and the
  offset commit are written atomically ("read-process-write" with
  `read_committed` isolation). Everything succeeds or nothing does. Real, but it
  only holds *inside* Kafka — a side effect to an external system (send an email,
  charge a card) is still at-least-once unless that system is idempotent too.

> Rule of thumb: default to **at-least-once + idempotent consumers.** Reach for
> exactly-once only when you truly can't dedupe downstream, and know it costs
> throughput and complexity.

---

## 7. Retention & Log Compaction

Because Kafka keeps records, it needs a policy for *when to drop them*:

- **Time / size retention** (`retention.ms`, `retention.bytes`): delete log
  segments older than X (e.g. 7 days) or once the partition exceeds Y bytes.
  This is the default; the offset of a record never changes, old records just
  age out from the front.
- **Log compaction** (`cleanup.policy=compact`): instead of deleting by age,
  keep **at least the latest value for each key**, garbage-collecting older
  values of the same key. The log becomes a **changelog / snapshot** — replay it
  and you reconstruct the current state of every key. Perfect for "current
  balance per account," "latest config per service," or Kafka's own consumer
  offsets. (Deletes are done with a **tombstone**: a record with the key and a
  `null` value.)

Retention = "a rolling window of recent events." Compaction = "a durable table
of the newest value per key." Some topics use both.

---

## 8. When to use a log / queue (and the caveats)

Reach for messaging when you want:

- **Decoupling** — producers and consumers don't call each other directly; they
  only share the topic contract. Deploy, scale, and fail independently.
- **Buffering / backpressure** — a burst of writes lands in the log; consumers
  drain at their own pace instead of being overwhelmed. The log is a shock
  absorber.
- **Fan-out** — many independent consumer groups react to the same event stream
  (billing, analytics, search-indexing) without the producer knowing about them.
- **Replay** — re-process history after a bug fix or to seed a new service by
  resetting an offset to 0.

**Caveats to say before someone else does:**

- **Ordering is only per-partition.** Need per-entity order? Key by that entity.
  Need strict global order? You're down to one partition = no parallelism.
- **At-least-once is the norm → design idempotent consumers.** Assume every
  message can arrive twice.
- **More partitions ≠ free scaling.** They cost overhead and you can't cleanly
  reduce them; increasing them re-shuffles key→partition mapping.
- **It's async / eventually consistent.** A consumer's view lags the producer by
  the consumer lag. Not a request/response substitute.
- **Poison messages** can stall a partition (one bad record blocks everything
  behind it); you need dead-letter handling.

---

## 9. Kafka vs a task queue (RabbitMQ / SQS)

**Use a log (Kafka)** for high-throughput event streams that multiple consumers
replay and process in per-key order; **use a task queue (RabbitMQ / SQS)** for
distributing discrete jobs to workers where you want per-message ack/retry,
delete-on-consume, and don't need ordering or replay.

---

## 10. 30-second interview recall

- Kafka = distributed **append-only log**, not a delete-on-read queue.
- **Partition** = unit of parallelism **and** ordering; order holds **only
  within** a partition.
- Producer: **same key → same partition → ordered**; `acks=all` = durable.
- Broker: per-partition **leader/followers**, **ISR**, elect new leader from ISR.
- Consumer group: **1 partition → 1 consumer**, so **partitions cap parallelism**.
- **Offset** = per-group cursor; **commit after process = at-least-once →
  idempotent consumers**; exactly-once = idempotent producer + transactions.
- **Retention** ages data out; **compaction** keeps the latest value per key.
