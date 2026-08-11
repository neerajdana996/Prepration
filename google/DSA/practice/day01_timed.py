"""
DAY 1 — TIMED RE-DERIVE (blank screen)

Rules:
  - No peeking at day01_hashing.py. Rebuild from scratch.
  - Run the 5-step attack out loud (restate -> brute -> waste -> tool+precondition -> code+O).
  - Talk through it as if an interviewer is watching.

TIMING TARGETS (self-time; note your real time next to each):
  #1 two_sum ............... target ~4 min   | mine: ____
  #2 contains_duplicate .... target ~3 min   | mine: ____
  #3 is_anagram ............ target ~4 min   | mine: ____
  #4 group_anagrams ........ target ~6 min   | mine: ____
  #5 longest_consecutive ... target ~15 min  | mine: ____   <- UNSEEN, medium

Run:  python3 day01_timed.py
"""


# --- WARM-UP: re-derive today's four, cold -------------------------------

def two_sum(nums, target):
    s={}
    for i,n in enumerate(nums):
        c=target-n
        if c in s:
            return [s[c],i]
        s[n]=i
    return [-1,-1]


def contains_duplicate(nums):
    s=set()
    for n in nums:
        if n in s:
            return True;
        s.add(n)
    return False


def getKey (s):
    freq=[0]*26
    for c in s:
        freq[ord(c)-ord("a")]+=1
    return tuple(freq)

def is_anagram(s, t):
    return getKey(s)==getKey(t)


def group_anagrams(strs):
    m={}
    for s in strs:
        key = getKey(s)
        if key not in m :
            m[key]=[]
        m[key].append(s)
    return list(m.values())


# --- UNSEEN #5 — Longest Consecutive Sequence ----------------------------
# Given an UNSORTED array of ints, return the length of the longest run of
# CONSECUTIVE integers (e.g. 1,2,3,4). The numbers can be anywhere in the array.
#   [100, 4, 200, 1, 3, 2]      -> 4   (the run 1,2,3,4)
#   [0,3,7,2,5,8,4,6,0,1]       -> 9   (the run 0..8)
#   []                          -> 0
#
# The trap: sorting is O(n log n). Google wants O(n). What structure gives you
# O(1) "is x+1 also present?" lookups... and how do you avoid recounting a run
# you've already walked? (Hint lives in that second question — think about
# where a run STARTS.)
def longest_consecutive(nums):
    s=set(nums)
    b=0
    for n in nums:
        if n-1 not in s:
            l=1
            while n+1 in s:
                l+=1
                n+=1
            b=max(b,l)
    return b

        
def two_sum(nums,target):
    l,r=0,len(nums)-1
    while l<r:
        s = nums[l]+nums[r]
        if target == s:
            return [l,r]
        elif target<s:
            r-=1
        else:
            l+=1
    return [-1,-1]


    


# --- TESTS ---------------------------------------------------------------
def _check(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got!r}", "" if ok else f"(want {want!r})")


if __name__ == "__main__":
    _check("two_sum",         two_sum([2, 7, 11, 4], 9),                  [0, 1])
    _check("two_sum",         two_sum([3, 2, 4], 6),                      [1, 2])
    _check("contains_dup T",  contains_duplicate([1, 2, 3, 1]),           True)
    _check("contains_dup F",  contains_duplicate([1, 2, 3, 4]),           False)
    _check("anagram T",       is_anagram("anagram", "nagaram"),           True)
    _check("anagram F",       is_anagram("rat", "car"),                   False)
    ga = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    ga = sorted(sorted(g) for g in ga) if ga else ga
    _check("group_anagrams",  ga, [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]])
    _check("longest_consec",  longest_consecutive([100, 4, 200, 1, 3, 2]), 4)
    _check("longest_consec",  longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]), 9)
    _check("longest_consec",  longest_consecutive([]),                     0)
