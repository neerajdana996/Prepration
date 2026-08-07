# Immutable class

See [`ImmutableDevice.java`](ImmutableDevice.java).

## The five ingredients
1. **`final` class** — no subclass can add mutable behavior.
2. **all fields `private final`**.
3. **no setters**.
4. **set everything in the constructor**.
5. **defensive-copy mutable fields** (List/Date/arrays) **both in and out** — otherwise a caller's reference can mutate your internals.

## Why it's worth it
- **Thread-safe by construction** (no shared mutable state → no locks needed).
- **Safe as `Map`/`Set` keys** (hashCode never changes).
- Easier to reason about — pass it anywhere without fear of surprise mutation.

## To "change" one → return a new instance (a "wither")
```java
ImmutableDevice renamed = device.withName("core-router-2"); // original untouched
```

## Modern shorthand: `record` (Java 16+)
```java
public record DeviceReading(String id, int cpu, int temp) {}
```
A `record` auto-generates the `final` fields, constructor, `equals`/`hashCode`/`toString`.
⚠️ But records do **not** auto defensive-copy mutable components — if a record holds a `List`, copy it in the compact constructor yourself.

**Soundbite:** *"Final class, final fields, no setters, construct-only, and defensive copies for mutable fields in and out — so state can't change after construction. That makes it thread-safe and a safe map key. `record` is the modern shorthand, but I still defensive-copy mutable components."*
