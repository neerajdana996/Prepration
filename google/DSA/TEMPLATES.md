# Pattern Templates — the reusable skeletons

The point of drilling is to extract these. When you recognize a pattern, you're
really recognizing "which template + how to fill its knobs."

---

## Sliding Window

```python
l = 0
state = ...            # KNOB 1: what you track (set / count-dict / running sum)
best  = ...            # KNOB 4: start value (0 to maximize, inf to minimize)
for r in range(len(arr)):
    add arr[r] to state                 # EXPAND (always the same)
    while <KNOB 2: shrink condition>:
        remove arr[l] from state        # SHRINK
        l += 1
    <KNOB 3: update best>
return best
```

| knob | MAXIMIZE (longest valid) | MINIMIZE (shortest valid) |
|---|---|---|
| 1 · state | set / count map | running sum |
| 2 · shrink while | window is **INVALID** | window is **VALID** |
| 3 · update best | **after** the while → `max(best, r-l+1)` | **inside** the while, before shrink → `min(best, r-l+1)` |
| 4 · start | `0` | `float('inf')` (return 0 if unchanged) |

**Signals:** "longest/shortest/max/min **contiguous** substring/subarray" + a constraint.
**Tips:** variable window shrinks with a `while` (heal/optimize), never `if`.
Each index enters once, leaves once → **O(n)**.

**Seen it power:** longest-substring-no-repeat (set), min-size-subarray-sum (sum),
longest-repeating-char-replacement (count map + "len − maxfreq ≤ k").

---

## Two Pointers (converging)

```python
l, r = 0, len(arr) - 1
while l < r:
    if <found>:      return ...
    elif <too small>: l += 1     # PRECONDITION: array is SORTED
    else:             r -= 1
```

**Signal fork:** pair-that-sums → SORTED? two pointers (O(1) space) : UNSORTED? hash map.
**Variants:** valid palindrome (compare ends), container with most water (move the
**shorter** wall — it's the bottleneck), 3Sum (sort, fix i, two-pointer the rest).

---

## Hashing

- "have I seen this value?" → **set**
- "what value pairs with me?" → **map value → index** (Two Sum)
- "how many of each thing?" → **count map** (anagram, char-replacement, group)
- "group things that share a signature" → **map key → list** (getKey → bucket)
