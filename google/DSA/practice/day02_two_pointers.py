"""
DAY 2 — TWO POINTERS (converging + fast/slow)

CORE IDEA (converging): on a SORTED array, a left and right pointer walk toward
each other. Sum/width too small -> move left up; too big -> move right down.
Each pointer moves one direction only => O(n), O(1) space.

PRECONDITION (your Day 2 lesson): converging two-pointer needs SORTED order
(or a symmetric structure like a palindrome). Unsorted pair-sum -> hash map instead.

SIGNAL -> TOOL:
  "pair in a SORTED array"            -> converging two pointers
  "is it a palindrome / symmetric?"   -> pointers from both ends
  "triplet summing to 0"              -> SORT, fix one, two-pointer the rest
  "max area / widest container"       -> converging pointers, move the smaller wall

Run:  python3 day02_two_pointers.py
"""


# --- #1 Valid Palindrome -------------------------------------------------
# True if s reads the same forwards/backwards, considering only alphanumeric
# chars and ignoring case.  "A man, a plan, a canal: Panama" -> True
# Hint: two pointers from both ends; skip non-alnum; compare lowercased.
def is_palindrome(s):
    s="".join([c.lower() for c in s if c.isalpha()])
    l,r=0,len(s)-1
    while l<=r: # this is a bit confusing teh < and <=
        if s[l]!=s[r]:
            return False
        l+=1
        r-=1
    return True
    


# --- #2 Two Sum II (input is SORTED) -------------------------------------
# Return the 0-based indices [i, j] (i < j) of the pair summing to target.
# nums is sorted ascending, exactly one answer.  [1,3,4,6,8,10], 14 -> [2,5]
def two_sum_sorted(nums, target):
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


# --- #3 Container With Most Water ----------------------------------------
# heights[i] is a vertical wall. Pick two walls; water held = width * min(h).
# Return the MAX water.  [1,8,6,2,5,4,8,3,7] -> 49
# Trap: sum isn't the signal here. Standing on two walls, which pointer do you
# move to have any *hope* of a bigger area, and why?
def max_area(nums):
    l,r=0,len(nums)-1
    maxWater=0
    while l<r:
        maxWater=max(maxWater,(r-l)*min(nums[r],nums[l]))
        if nums[r]<nums[l]:
            r-=1
        else:
            l+=1
    return maxWater


# --- #4 3Sum -------------------------------------------------------------
# Return all UNIQUE triplets [a,b,c] with a+b+c == 0.
#   [-1,0,1,2,-1,-4] -> [[-1,-1,2], [-1,0,1]]
# The move: SORT first. Fix nums[i], then two-pointer the rest for -nums[i].
# The pain: skipping duplicates so triplets don't repeat.
#
# HOMEWORK CHECKLIST (build on the skeleton we designed):
#   [ ] res = [], nums.sort()
#   [ ] loop i; inline two-pointer on l=i+1, r=len-1; on hit append + move BOTH inward
#   [ ] DEDUP the fixed element:  if i > 0 and nums[i] == nums[i-1]: continue
#   [ ] DEDUP after a hit:  while l < r and nums[l] == nums[l-1]: l += 1
#                           while l < r and nums[r] == nums[r+1]: r -= 1
#   [ ] tiny optimization: if nums[i] > 0 you can break (sorted => no negatives left)
# Run the tiny test; then re-derive it COLD tomorrow.
def three_sum(nums):
    nums.sort()
    for i,n in enumerate(nums):
        [l,r]=two_sum_sorted(nums[i:],0-n)
        if n+nums[l]+nums[r]==0:
            return [i,l,r]
    return [-1,-1,-1]


# --- TESTS ---------------------------------------------------------------
def _check(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got!r}", "" if ok else f"(want {want!r})")


if __name__ == "__main__":
    _check("palindrome T", is_palindrome("A man, a plan, a canal: Panama"), True)
    _check("palindrome F", is_palindrome("race a car"),                     False)
    _check("two_sum_sorted", two_sum_sorted([1, 3, 4, 6, 8, 10], 14),       [2, 5])
    _check("two_sum_sorted", two_sum_sorted([2, 7, 11, 15], 9),             [0, 1])
    _check("max_area",     max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]),           49)
    _check("max_area",     max_area([1, 1]),                                1)
    ts = three_sum([-1, 0, 1, 2, -1, -4])
    ts = sorted(sorted(t) for t in ts) if ts else ts
    _check("three_sum",    ts, [[-1, -1, 2], [-1, 0, 1]])
