# Principal Engineer — Distributed Systems / Backend / Infra Roadmap

The "what should I know" map. Each bullet is a topic + why it matters + the key trade-off or gotcha.
Legend: ✅ = covered as a hand-built code folder · ⬜ = to build.

---

## Reliability & Resilience

- ⬜ **Timeouts** — Every remote call needs a deadline; without one a slow dependency exhausts your threads/connections. Gotcha: pick timeouts from real latency percentiles (p99), and propagate deadlines down the call chain so callers don't wait on work the client already abandoned.
- ⬜ **Retries + exponential backoff + jitter** — Retry transient failures, but back off exponentially and add jitter so clients don't synchronize into a retry storm. Gotcha: only retry idempotent ops, and cap total attempts — retries amplify load exactly when the system is already struggling (retry-induced meltdown).
- ⬜ **Circuit breaker** — Stop calling a failing dependency after an error threshold; fail fast (open), probe occasionally (half-open), recover (closed). Trade-off: protects you from cascading failure and wasted latency, but a badly tuned breaker sheds load during a brief blip and turns a hiccup into an outage.
- ⬜ **Bulkhead** — Isolate resources (thread pools, connection pools) per dependency so one slow/failing downstream can't consume all capacity and sink everything. Trade-off: better fault isolation vs. lower utilization (reserved capacity sits idle).
- ✅ **Idempotency** — Make repeated identical requests safe (same result, no double-charge) via idempotency keys / dedup. Essential companion to retries and at-least-once delivery. Gotcha: the key store must be durable and cover the whole side-effecting operation, not just the DB write.
- ✅ **Rate limiting** — Cap request rate to protect capacity and enforce fairness/quotas. Know token bucket vs. leaky bucket vs. fixed/sliding window. Gotcha: distributed rate limiting needs shared state (e.g. Redis) and must handle clock skew and the boundary-burst problem of fixed windows.
- ⬜ **Load shedding & graceful degradation** — Under overload, drop or downgrade low-priority work (shed, serve stale, disable features) instead of collapsing. Trade-off: partial availability beats total failure, but requires you to pre-classify traffic by priority.

## Data & Consistency

- ⬜ **CAP / PACELC** — Under a network partition you choose Consistency or Availability (CAP); and *even without* a partition you trade Latency vs. Consistency (PACELC). It's the lens for every replicated-data decision. Gotcha: "CA" is not a real operating mode for a distributed store — partitions will happen.
- ⬜ **Strong vs. eventual consistency** — Strong: reads always see the latest write (linearizable), simpler to reason about, higher latency/lower availability. Eventual: replicas converge over time, fast and available, but readers can see stale/out-of-order data. Gotcha: know the middle ground (read-your-writes, monotonic reads, causal consistency).
- ⬜ **2PC vs. Saga** — 2PC gives atomic cross-service commits but blocks on the coordinator and hurts availability (locks held through the prepare phase). Saga = a sequence of local transactions with compensating actions; available and scalable but only eventually consistent and you must design rollbacks. Trade-off: atomicity/simplicity vs. availability/scalability.
- ⬜ **Event sourcing & CQRS** — Event sourcing stores the log of state changes as the source of truth (full audit, replay, temporal queries); CQRS splits the write model from read-optimized projections. Trade-off: huge flexibility and auditability vs. real complexity — eventual consistency between write and read side, schema/event versioning, and rebuild cost.
- ⬜ **CDC / transactional outbox** — Reliably get data changes out of your DB to other systems. Outbox: write the event to an outbox table in the *same* transaction as the state change, then relay it — solves the dual-write problem. CDC: tail the DB's replication log to emit changes. Gotcha: consumers must handle at-least-once/duplicate delivery.
- ⬜ **Replication & sharding / partitioning** — Replication = copies for availability & read scaling (sync vs. async; leader-follower vs. multi-leader vs. leaderless). Sharding = split data across nodes for write/storage scaling. Gotchas: async replication risks lost writes on failover; bad shard keys create hot spots and make cross-shard joins/transactions painful.
- ⬜ **Consistent hashing** — Map keys to nodes on a ring so adding/removing a node only remaps ~1/N of keys instead of everything. Use virtual nodes to smooth load. Why it matters: the backbone of sharded caches and stores. Gotcha: without vnodes you get uneven load and cascading hotspots on node loss.
- ⬜ **Quorum (R + W > N)** — In leaderless replication, requiring read replicas (R) + write replicas (W) to overlap (R+W>N) guarantees a read sees the latest write. Tunable: W=N favors read speed, R=N favors write speed. Gotcha: quorum alone doesn't prevent all anomalies — you still need read repair / anti-entropy and handling of concurrent writes (conflicts).
- ✅ **Relational databases** — ACID semantics, isolation levels & anomalies, MVCC, locking, indexing, normalization. The default when you need transactions and strong consistency. (Covered in the separate Relational Databases folder.)

## Communication & APIs

- ⬜ **REST vs. gRPC vs. GraphQL** — REST: simple, cacheable, ubiquitous, but chatty/over- or under-fetching. gRPC: binary/HTTP2, fast, strong contracts, great for internal service-to-service; poor browser/human ergonomics. GraphQL: client picks exactly what it needs, one flexible endpoint; but caching and rate-limiting are hard and naive resolvers cause N+1 queries.
- ⬜ **API versioning** — Evolve APIs without breaking clients (URI vs. header vs. content negotiation). Prefer additive, backward-compatible changes. Gotcha: you own every version until every client migrates — have a deprecation policy or versions live forever.
- ⬜ **Pagination** — Offset/limit is simple but slow on deep pages and unstable when data shifts. Cursor/keyset pagination is stable and scales. Gotcha: offset pagination can skip or duplicate rows during concurrent inserts/deletes.
- ⬜ **WebSockets vs. SSE vs. long-polling** — Long-polling: works everywhere, inefficient. SSE: simple server→client streaming over HTTP, auto-reconnect, one-directional. WebSockets: full-duplex, best for chat/collab/games but stateful connections complicate load balancing and scaling. Choose by directionality and infra tolerance for long-lived connections.
- ⬜ **Backpressure** — When a consumer can't keep up, signal upstream to slow down (bounded buffers, credit-based flow, pull models) instead of buffering unboundedly. Gotcha: unbounded queues just move the failure to OOM/latency-explosion later — always bound and decide the overflow policy (block, drop, or shed).

## Scaling & Distribution

- ⬜ **Load balancing (L4 vs. L7)** — L4 routes on IP/port (fast, protocol-agnostic, no payload inspection); L7 routes on HTTP content (path/host/header-based routing, TLS termination, richer but costlier). Know algorithms (round-robin, least-connections, hashing) and health-check-driven ejection.
- ⬜ **CDN** — Push static (and cacheable dynamic) content to edge POPs near users for latency and origin offload. Trade-off: massive latency/scale win vs. cache invalidation and staleness management. Gotcha: cache-key design and purge strategy make or break hit rate.
- ⬜ **Autoscaling** — Add/remove capacity on demand (horizontal by metric/schedule/predictive). Trade-off: cost efficiency vs. scale-up lag — scaling reacts *after* load arrives, so pair with headroom, warm pools, and slow scale-down to avoid flapping.
- ✅ **Message queues / log (Kafka)** — Decouple producers from consumers for buffering, async processing, and fan-out. Queue (work distribution) vs. log (replayable ordered stream, Kafka). Know partitions/ordering, consumer groups, delivery semantics (at-least/at-most/exactly-once), and offset management. (Covered in the messaging-and-kafka folder.)

## Caching

- ⬜ **Caching strategies (cache-aside / write-through / write-back)** — Cache-aside: app loads on miss and populates (simple, default; risk of stale). Write-through: write cache+DB together (consistent, slower writes). Write-back: write cache now, DB later (fast, risk of data loss on crash). Choose by read/write mix and tolerance for staleness/loss.
- ⬜ **Cache invalidation** — "One of the two hard problems." Keeping cache and source-of-truth in sync: TTL expiry, explicit invalidation, or versioned keys. Gotcha: invalidation races (stale write repopulating after a delete) — consider write-through, short TTLs, or version stamps.
- ⬜ **TTL** — Time-to-live bounds staleness and reclaims memory automatically. Trade-off: short TTL = fresher data but more misses/origin load; long TTL = higher hit rate but staler data. Gotcha: uniform TTLs cause synchronized mass expiry (a thundering-herd trigger) — add TTL jitter.
- ⬜ **Thundering herd / cache stampede** — When a hot key expires, many requests miss simultaneously and hammer the origin. Mitigate with request coalescing (single-flight), lock/lease on recompute, early/probabilistic refresh, and TTL jitter.
- ⬜ **Bloom filters** — Space-efficient probabilistic set membership: "definitely not present" or "maybe present" (no false negatives, tunable false positives). Use to skip expensive lookups for absent keys (avoid cache/DB penetration). Gotcha: can't delete from a standard bloom filter; size for your target false-positive rate.

## Observability & Ops

- ⬜ **Three pillars: logs / metrics / traces** — Logs: discrete events (what happened, detail-rich, costly at volume). Metrics: cheap aggregatable time series (trends/alerting, low cardinality). Traces: request path across services (where latency/errors originate). You need all three; they answer different questions.
- ⬜ **RED & USE methods** — RED (for services): Rate, Errors, Duration — the user-facing view. USE (for resources): Utilization, Saturation, Errors — the "is this box healthy" view. Together they cover request health and resource health. Gotcha: alert on symptoms (RED/SLO) not just causes (USE) to reduce noise.
- ⬜ **SLO / SLI / error budgets** — SLI = a measured signal (e.g. p99 latency, success rate); SLO = target for it; error budget = allowed unreliability (1 − SLO) that governs release velocity. Why it matters: turns "reliability" into a number you can trade against feature speed. Gotcha: SLOs must reflect user experience, not internal vanity metrics.
- ⬜ **Health checks** — Liveness (is the process alive — restart if not) vs. readiness (can it serve traffic now — pull from LB if not). Gotcha: a health check that hits every dependency can cascade-fail a whole fleet when one shared dependency blips; keep liveness shallow.

## Foundations

- ⬜ **Leader election & consensus (Raft / Paxos, concept level)** — How a cluster agrees on one value/leader despite failures. Raft (understandable: leader + log replication + terms) vs. Paxos (foundational, harder). Underpins config stores, coordination, replicated state machines (etcd/ZooKeeper). Gotcha: consensus needs a majority quorum — it trades availability for consistency and can't make progress without one.
- ✅ **Distributed locks** — Mutual exclusion across processes/nodes (e.g. Redis Redlock, ZooKeeper/etcd leases). Used for leader-ish work, single-writer guarantees. Gotcha: locks can expire while the holder still runs (GC pause, network delay) — use fencing tokens so stale holders can't corrupt state. (Covered in the locks-and-idempotency folder.)
- ⬜ **Clocks & ordering (logical / vector clocks)** — Wall-clock time is unreliable across machines (skew, NTP jumps) so you can't order events by timestamp. Lamport clocks give a total order consistent with causality; vector clocks detect concurrency/conflicts. Gotcha: reach for logical clocks whenever "who happened first?" matters across nodes.

---

## Suggested order to build next

Pick these 3–4 first — they're the highest-leverage gaps and they build on the folders you already have (idempotency, rate limiting, locks, Kafka, relational DB):

1. **Retries + backoff + jitter + circuit breaker + timeouts (Reliability bundle)** — Highest ROI: it's the most common interview probe, applies to every service you'll ever build, and directly extends your existing idempotency folder (retries are only safe *because* of idempotency). Build these together as one resilience toolkit.
2. **Caching (cache-aside/write-through/write-back + invalidation + TTL + thundering herd)** — Nearly every scaling question routes through caching, and the stampede/invalidation gotchas are exactly what separates a senior from a principal answer. Reuses your rate-limiting Redis muscle.
3. **Replication & sharding/partitioning + consistent hashing + quorum (Data distribution bundle)** — The core of "how do I scale a stateful system." Consistent hashing and quorum are concrete, codeable, and pair naturally with the relational-DB knowledge you already have to explain the whole read/write-scaling story.
4. **CDC / transactional outbox** — A tight, practical build that closes the loop with your Kafka folder: it's the correct way to get changes *into* the log without dual-write bugs, and it showcases the event-sourcing/consistency thinking principals are expected to lead on.

Rationale: start with the reliability toolkit (broadest applicability + leans on idempotency), then caching (ubiquitous in scaling discussions), then data distribution (the stateful-scaling story), and finally the outbox to connect your data and messaging folders.
