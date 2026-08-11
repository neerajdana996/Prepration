"""
DAY 1 — HASHING (count maps & lookup maps)

THE 5-STEP ATTACK (run this on every problem, out loud):
  1. Restate + tiny example      -> say it in your words, hand-build a 5-8 element case
  2. Brute force + its cost      -> always have a baseline, state its big-O
  3. Find the waste              -> what work am I repeating?
  4. Match signal -> tool        -> name the pattern, THEN check its precondition holds
  5. Code small, test, state O   -> walk your tiny example through by hand

SIGNAL -> TOOL for today:
  "have I seen this value?"          -> set / lookup map        (O(1) membership)
  "what value pairs with me?"        -> map value -> index      (Two Sum)
  "how many times does X appear?"    -> count map (dict of counts)
  "are these the same multiset?"     -> count map, compare counts (anagram)

RULE: struggle 10-15 min BEFORE any hint. A problem only 'counts' when you can
re-derive it cold tomorrow from a blank screen.

Run this file:  python3 day01_hashing.py
"""
def getKey(s):
        freq=[0]*26
        for c in s:
            freq[ord(c) - ord('a')]+=1
        return tuple(freq)

# ----------------------------------------------------------------------------
# PROBLEM 1 — Two Sum
# Return the two INDICES whose values add up to target. Exactly one answer.
# Example: nums = [2, 7, 11, 4], target = 9  ->  [0, 1]   (2 + 7 = 9)
#
# Your plan (from our session): one pass, dict value -> index.
# Decide: check-first-then-store, or store-first-then-check? Why?
# ----------------------------------------------------------------------------
def two_sum(nums, target):
    seen = {}
    for i,n in enumerate(nums):
        complement = target-n
        if complement in seen:
            return [seen[complement], i]   # partner's index first, then mine
        seen[n]=i
    return [-1,-1]


# ----------------------------------------------------------------------------
# PROBLEM 2 — Contains Duplicate
# Return True if any value appears at least twice, else False.
# Example: [1, 2, 3, 1] -> True     [1, 2, 3, 4] -> False
#
# Signal check: what exactly are you asking at each element?
# ----------------------------------------------------------------------------
def contains_duplicate(nums):
    # TODO: your code here

    s = set()
    for n in nums:
        if n in s:
            return True
        s.add(n)
    return False


# ----------------------------------------------------------------------------
# PROBLEM 3 — Valid Anagram
# Return True if t is an anagram of s (same letters, same counts).
# Example: s = "anagram", t = "nagaram" -> True
#          s = "rat",     t = "car"     -> False
#
# Precondition trap: is a 'seen' set enough here, or do you need COUNTS?
# ----------------------------------------------------------------------------
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    return getKey(s) ==getKey(t)
    


# ----------------------------------------------------------------------------
# PROBLEM 4 — Group Anagrams
# Group words that are anagrams of each other.
# Example: ["eat","tea","tan","ate","nat","bat"]
#       -> [["eat","tea","ate"], ["tan","nat"], ["bat"]]  (order doesn't matter)
#
# The hard part: what KEY makes all anagrams collide into the same bucket?
# ----------------------------------------------------------------------------
def group_anagrams(strs):
    # TODO: your code here
    m= {}
    
    for s in strs:
        k = getKey(s);
        if k not in m:
            m[k]=[]
        m[k].append(s)
    return list(m.values())   # <-- was missing: hand back the buckets




# ----------------------------------------------------------------------------
# TINY TESTS — walk your own example through by hand FIRST, then run these.
# ----------------------------------------------------------------------------
def _check(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got!r}", "" if ok else f"(want {want!r})")


if __name__ == "__main__":
    _check("two_sum",           two_sum([2, 7, 11, 4], 9),                     [0, 1])
    _check("two_sum",           two_sum([3, 2, 4], 6),                         [1, 2])
    _check("contains_dup T",    contains_duplicate([1, 2, 3, 1]),              True)
    _check("contains_dup F",    contains_duplicate([1, 2, 3, 4]),              False)
    _check("anagram T",         is_anagram("anagram", "nagaram"),              True)
    _check("anagram F",         is_anagram("rat", "car"),                      False)
    got = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    norm = sorted(sorted(g) for g in got) if got else got
    _check("group_anagrams",    norm, [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]])
