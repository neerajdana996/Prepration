"use strict";
/*
 * mini-kafka.js — a tiny, in-memory model of Kafka's mechanics.
 *
 * This is a TEACHING toy, not production. It runs on plain Node.js (no deps):
 *     node mini-kafka.js
 *
 * It demonstrates the load-bearing ideas:
 *   - a topic is split into PARTITIONS; each partition is an append-only LOG
 *     (an array) where every record gets a monotonically increasing OFFSET.
 *   - a PRODUCER picks a partition by hashing the key (same key -> same
 *     partition -> ordered), or round-robins when there is no key.
 *   - a CONSUMER GROUP assigns each partition to exactly ONE consumer, so the
 *     number of partitions caps the parallelism of the group.
 *   - OFFSETS are per-group, per-partition cursors. "Commit AFTER process"
 *     gives at-least-once: a crash (a re-poll before commit) re-delivers.
 */

// ---------------------------------------------------------------------------
// Broker: owns topics. Each topic is an array of partitions; each partition is
// an array of records. A record is { offset, key, value }.
// ---------------------------------------------------------------------------
class Broker {
  constructor() {
    this.topics = new Map(); // name -> { partitions: [ [record, ...], ... ] }
  }

  createTopic(name, numPartitions) {
    if (this.topics.has(name)) throw new Error(`topic ${name} exists`);
    const partitions = Array.from({ length: numPartitions }, () => []);
    
    this.topics.set(name, { partitions });
    return this.topics.get(name);
  }

  getTopic(name) {
    const t = this.topics.get(name);
    if (!t) throw new Error(`no such topic: ${name}`);
    return t;
  }

  numPartitions(name) {
    return this.getTopic(name).partitions.length;
  }

  // Append a record to a specific partition; the offset is that record's index
  // in the partition log (0-based, gap-free, monotonically increasing).
  append(name, partition, key, value) {
    const log = this.getTopic(name).partitions[partition];
    const offset = log.length;
    const record = { offset, key, value };
    log.push(record);
    return record;
  }

  // Read from `fromOffset` to the end of a partition (a "fetch").
  read(name, partition, fromOffset) {
    return this.getTopic(name).partitions[partition].slice(fromOffset);
  }
}

// ---------------------------------------------------------------------------
// Partitioner: same logic Kafka uses conceptually.
//   - key present   -> hash(key) % numPartitions  (sticky: same key, same partition)
//   - key absent     -> round-robin across partitions
// A tiny deterministic string hash (FNV-1a-ish) keeps the demo reproducible.
// ---------------------------------------------------------------------------
function hashKey(key) {
  let h = 2166136261 >>> 0; // FNV offset basis
  const s = String(key);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0; // FNV prime, keep unsigned 32-bit
  }
  return h >>> 0;
}

// ---------------------------------------------------------------------------
// Producer: sends records to the broker, choosing a partition per the rules.
// ---------------------------------------------------------------------------
class Producer {
  constructor(broker) {
    this.broker = broker;
    this.rrCounter = 0; // round-robin cursor for keyless records
  }

  partitionFor(topic, key) {
    const n = this.broker.numPartitions(topic);
    if (key === undefined || key === null) {
      const p = this.rrCounter % n;
      this.rrCounter++;
      return p;
    }
    return hashKey(key) % n; // keyed: deterministic -> ordering per key
  }

  send({ topic, key, value }) {
    const partition = this.partitionFor(topic, key);
    const record = this.broker.append(topic, partition, key ?? null, value);
    return { topic, partition, offset: record.offset, key: key ?? null, value };
  }
}

// ---------------------------------------------------------------------------
// ConsumerGroup: subscribes to a topic, assigns partitions across N consumers
// (round-robin: partition p -> consumer p % numConsumers), and tracks one
// committed offset per partition FOR THIS GROUP.
//
//   poll(consumerId)  -> returns records from committedOffset..end for each
//                        partition owned by that consumer, WITHOUT committing.
//                        (records a pending "position" so commit can advance.)
//   commit(consumerId)-> advances committedOffset to the position last polled.
//
// Because poll does not auto-commit, re-polling before commit re-delivers the
// same records — that is exactly at-least-once semantics.
// ---------------------------------------------------------------------------
class ConsumerGroup {
  constructor(broker, groupId, topic) {
    this.broker = broker;
    this.groupId = groupId;
    this.topic = topic;
    this.consumers = [];               // consumer ids, in subscribe order
    this.assignment = new Map();       // partition -> consumerId
    this.committed = new Map();        // partition -> committed offset
    this.position = new Map();         // partition -> offset last handed out by poll

    const n = broker.numPartitions(topic);
    for (let p = 0; p < n; p++) {
      this.committed.set(p, 0);
      this.position.set(p, 0);
    }
  }

  // Add consumers and (re)compute the partition assignment. This is the
  // "rebalance": every partition ends up owned by exactly one consumer.
  subscribe(consumerIds) {
    this.consumers = consumerIds.slice();
    this._rebalance();
  }

  _rebalance() {
    this.assignment.clear();
    const n = this.broker.numPartitions(this.topic);
    const c = this.consumers.length;
    for (let p = 0; p < n; p++) {
      this.assignment.set(p, this.consumers[p % c]); // round-robin partitions->consumers
    }
  }

  partitionsFor(consumerId) {
    const owned = [];
    for (const [p, owner] of this.assignment) if (owner === consumerId) owned.push(p);
    return owned.sort((a, b) => a - b);
  }

  // Read new records for the partitions this consumer owns. Does NOT commit.
  poll(consumerId) {
    const out = [];
    for (const p of this.partitionsFor(consumerId)) {
      const from = this.committed.get(p);
      const batch = this.broker.read(this.topic, p, from);
      if (batch.length) {
        this.position.set(p, from + batch.length); // where a commit would move to
        out.push({ partition: p, records: batch });
      }
    }
    return out;
  }

  // Advance committed offsets to the last-polled position for owned partitions.
  commit(consumerId) {
    for (const p of this.partitionsFor(consumerId)) {
      this.committed.set(p, this.position.get(p));
    }
  }

  committedOffsets() {
    return [...this.committed.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([p, o]) => `p${p}=${o}`)
      .join(" ");
  }
}

// ===========================================================================
// DEMO
// ===========================================================================
function line(label) {
  console.log("\n" + "=".repeat(70) + "\n" + label + "\n" + "=".repeat(70));
}

const broker = new Broker();
broker.createTopic("orders", 3); // 3 partitions

// --- 1. Produce keyed messages ------------------------------------------------
line("1. Produce keyed messages -> same key ALWAYS lands in the same partition");
const producer = new Producer(broker);

const events = [
  { key: "user-A", value: "placed order #1" },
  { key: "user-B", value: "placed order #2" },
  { key: "user-A", value: "cancelled order #1" }, // same key as first
  { key: "user-C", value: "placed order #3" },
  { key: "user-A", value: "re-placed order #1" }, // same key again
  { key: "user-B", value: "paid order #2" },
];

const keyToPartition = new Map();
for (const e of events) {
  const md = producer.send({ topic: "orders", key: e.key, value: e.value });
  console.log(
    `  send key=${md.key.padEnd(7)} -> partition ${md.partition} @ offset ${md.offset}  (${md.value})`
  );
  if (keyToPartition.has(md.key) && keyToPartition.get(md.key) !== md.partition) {
    throw new Error("INVARIANT BROKEN: a key mapped to two partitions!");
  }
  keyToPartition.set(md.key, md.partition);
}
console.log("\n  key -> partition map:", Object.fromEntries(keyToPartition));
console.log("  => every user-A event is in ONE partition, so its order is preserved.");

// Show the raw logs (offsets are gap-free and per-partition).
line("Partition logs (each is an append-only log with its own offsets)");
broker.getTopic("orders").partitions.forEach((log, p) => {
  console.log(`  partition ${p}:`);
  log.forEach((r) => console.log(`      @${r.offset} key=${r.key} value="${r.value}"`));
  if (!log.length) console.log("      (empty)");
});

// --- 2. Keyless messages round-robin -----------------------------------------
line("2. Keyless messages round-robin across partitions (no ordering guarantee)");
for (let i = 1; i <= 4; i++) {
  const md = producer.send({ topic: "orders", value: `heartbeat ${i}` });
  console.log(`  send (no key) -> partition ${md.partition} @ offset ${md.offset}`);
}

// --- 3. Consumer group splits partitions --------------------------------------
line("3. Consumer group: 2 consumers split 3 partitions (each partition -> 1 consumer)");
const group = new ConsumerGroup(broker, "billing-service", "orders");
group.subscribe(["consumer-1", "consumer-2"]);
for (const c of ["consumer-1", "consumer-2"]) {
  console.log(`  ${c} owns partitions: [${group.partitionsFor(c).join(", ")}]`);
}
console.log("  => 3 partitions / 2 consumers: one consumer owns 2, the other owns 1.");

// --- 4. At-least-once: re-poll before commit re-delivers ----------------------
line("4. At-least-once: commit AFTER process; a re-poll before commit re-delivers");
console.log("  committed offsets (start):", group.committedOffsets());

console.log("\n  consumer-1 poll #1:");
let batches = group.poll("consumer-1");
for (const b of batches)
  for (const r of b.records) console.log(`      p${b.partition}@${r.offset} "${r.value}"`);

console.log("\n  ...processing... then CRASH before commit (offsets NOT advanced).");
console.log("  committed offsets (still):", group.committedOffsets());

console.log("\n  consumer-1 poll #2 (after restart, still uncommitted) -> SAME records re-delivered:");
batches = group.poll("consumer-1");
for (const b of batches)
  for (const r of b.records) console.log(`      p${b.partition}@${r.offset} "${r.value}"  <-- duplicate`);

console.log("\n  now process succeeds -> commit().");
group.commit("consumer-1");
console.log("  committed offsets (after commit):", group.committedOffsets());

console.log("\n  consumer-1 poll #3 -> nothing new (already committed):");
batches = group.poll("consumer-1");
console.log(batches.length ? batches : "      (no new records)");

console.log(
  "\n  Takeaway: because we commit AFTER processing, a failure re-delivers." +
    "\n  Consumers must therefore be IDEMPOTENT (dedupe by key/offset) to be safe."
);

line("done");
