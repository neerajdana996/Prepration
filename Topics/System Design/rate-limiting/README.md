# Rate Limiting

Runnable, heavily-commented reference implementations of the five classic
rate-limiting algorithms in plain Node.js (no dependencies). Each file has a
header comment (how it works, pros/cons, when to use, the gotcha) and a
`node <file>.js` demo at the bottom.

```
node fixed-window.js
node sliding-window-log.js
node sliding-window-counter.js
node token-bucket.js
node leaky-bucket.js
```

## What rate limiting is

Rate limiting caps how many operations a caller may perform in a time span. It
protects a system from overload, abuse, and runaway cost, enforces fairness
between tenants, and defends against brute-force and scraping. When the cap is
exceeded you typically reject with HTTP `429 Too Many Requests` (often with a
`Retry-After` header) or, for shaping, queue/delay the request.

## Where it lives (and what you key on)

Rate limiting is applied at multiple layers, each catching what the previous
misses:

- **Client / SDK** — polite self-throttling and backoff. Cheap and reduces
  wasted calls, but untrusted: a malicious or buggy client just ignores it.
  Never your only defense.
- **Edge / CDN / WAF** — coarse per-IP limits to blunt volumetric abuse before
  it reaches your origin (e.g. Cloudflare).
- **API gateway / load balancer** — the primary enforcement point. Centralized,
  sees all traffic for a service, applies per-user / per-API-key / per-route
  limits (Kong, Envoy, NGINX, AWS API Gateway).
- **Service / application** — fine-grained, business-aware limits (per
  endpoint, per plan tier, per expensive operation) that the gateway cannot
  express.

**What you key on** decides fairness and blast radius:

- **Per-IP** — no auth needed; good at the edge. But NAT/proxies share one IP
  (collateral damage) and IPs are cheap to rotate (weak against distributed
  abuse).
- **Per-user / per-API-key / per-tenant** — the fair unit for authenticated
  APIs; ties usage to an identity and to a billing plan.
- **Per-endpoint / per-resource** — protect a specific expensive path
  (search, export) independently.
- **Global** — a safety ceiling protecting a fragile downstream regardless of
  who is calling.

Real systems combine these (e.g. per-IP at the edge + per-key at the gateway).

## The five algorithms

| Algorithm | How it works (1 line) | Memory / key | Burst handling | Accuracy | Typical use |
|---|---|---|---|---|---|
| **Fixed window** | One counter per fixed time window; reset each window | O(1) — a count + window id | Poor: allows up to **2x** at the window boundary | Low (coarse) | Cheapest coarse quotas ("N/hour"), billing tiers |
| **Sliding window log** | Store a timestamp per request; count those in the trailing window | O(limit) — one entry per request | Excellent: no boundary spike | Exact | Small, sensitive limits (login attempts, costly ops) |
| **Sliding window counter** | Weight previous window by its overlap + current count | O(1) — two counters | Good: smooths the boundary spike | Approximate (very close) | **Default** high-throughput API/gateway limiting |
| **Token bucket** | Refill tokens at a rate up to a capacity; spend 1 per request | O(1) — tokens + timestamp | **Allows** bursts up to capacity | Good | **Default** API limiting where short bursts are fine |
| **Leaky bucket** | Queue requests; drain at a constant rate; overflow drops | O(capacity) queue (or O(1) as a counter) | **Smooths** bursts into a steady output | Good | Traffic shaping; protect a fragile, steady-rate downstream |

Quick mental model:
- **Fixed vs sliding**: sliding windows exist to kill the fixed-window
  boundary burst. Log = exact but memory-heavy; counter = cheap approximation.
- **Token vs leaky bucket**: token bucket *allows* bursts (spend saved-up
  allowance now, average rate bounded); leaky bucket *smooths* them (output
  drips at a constant rate regardless of input). See below.

## Distributed rate limiting

A single process can keep counters in memory. Once you run **many gateway
instances behind a load balancer**, per-instance counters are wrong: a limit of
100/min enforced independently on 10 nodes lets through up to ~1000/min if
traffic spreads across them. You need shared state.

### 1. Shared store (Redis)

Move the counter to a store all instances read/write — almost always **Redis**,
because it is fast, in-memory, and has atomic primitives + key TTLs (which
double as automatic window resets). Every instance does `INCR key` /
`ZADD key` against the same key, so the limit is enforced globally.

### 2. Atomicity (the INCR + EXPIRE race)

The naive fixed-window pattern is two commands:

```
INCR  key            # returns new count
EXPIRE key 60        # set/refresh TTL so the window resets
```

This has a **race**: if the process crashes (or the connection drops) between
`INCR` and `EXPIRE`, the key has no TTL and **never expires** — the counter
stays saturated forever and that caller is permanently blocked. There is also a
read-modify-write race in "get, check, set" style logic where two instances
both read `99`, both decide "under 100", and both write `100`, admitting one
request too many.

Fixes:
- **`SET key val NX EX 60` + `INCR`**, or **`INCRBY` + separate first-hit
  `EXPIRE`** — but the clean, standard answer is:
- **A Lua script** run with `EVAL`. Redis executes the whole script
  atomically (single-threaded, no interleaving), so "read counters, compute
  the token-bucket/sliding estimate, decide allow/deny, write back, set TTL"
  happens as one indivisible step. This is how production token-bucket and
  sliding-window limiters are implemented on Redis.

### 3. Clock skew

Sliding-window-log, token bucket, and leaky bucket all reason about elapsed
time. If each gateway node uses its **own wall clock** and those clocks differ
(NTP drift of tens/hundreds of ms, or worse), the same request gets
inconsistent decisions and windows don't line up across nodes.

Mitigations: use a **single clock source** — Redis's own time (`TIME` command)
inside the Lua script — so all decisions use one clock; keep NTP tight; and
prefer relative/elapsed-time math over absolute per-node timestamps.

### 4. Sticky (local) vs central (shared) — the trade-off

- **Central (shared Redis)**: accurate global enforcement, but every request
  pays a network round-trip to Redis (latency) and Redis becomes a hot shared
  dependency and potential bottleneck / single point of failure. You must plan
  for Redis being slow or down (fail-open = allow on error to protect
  availability, vs fail-closed = deny to protect the backend).
- **Sticky (local counters)**: route a given key always to the same node (e.g.
  consistent hashing on user id), so that node owns the counter and no shared
  store is needed. Fast (no round-trip) and scalable, but fragile: rebalancing,
  node loss, or a hot key breaks accuracy, and it can't enforce a truly global
  limit.
- **Common middle ground**: approximate locally, reconcile centrally — each
  node enforces a local share of the budget and periodically syncs with Redis
  (e.g. request tokens in batches). Trades a little accuracy for far less load
  on the shared store. This is what large-scale limiters (e.g. cell-based /
  batched-token designs) actually do.

**Rule of thumb**: start central-with-Redis-and-Lua for correctness; move
toward sticky/local batching only when Redis latency or load forces it.
