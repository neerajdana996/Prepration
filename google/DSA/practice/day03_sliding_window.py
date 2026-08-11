"""
DAY 3 — SLIDING WINDOW (coached)

CORE IDEA: a window [l .. r] over a CONTIGUOUS range. Expand r to grow.
When a constraint breaks, shrink l with a WHILE loop until it's healed again.
Each index enters once and leaves once => O(n).

TIPS (bank these):
  - "longest/shortest/max/min contiguous ..." + a constraint  -> sliding window
  - Variable window: shrink with WHILE (heal the constraint), not IF.
  - Track window state cheaply (a set for uniqueness, a dict for counts, a running sum).
  - Answer is usually max(best, r - l + 1) for "longest", or min length for "shortest".

Run:  python3 day03_sliding_window.py
"""


# --- #1 Longest Substring Without Repeating Characters (you derived this) --
# Return the LENGTH of the longest substring with all-unique chars.
#   "abcabcbb" -> 3 ("abc")   "bbbbb" -> 1   "pwwkew" -> 3 ("wke")   "abba" -> 2
from itertools import count


def length_of_longest_substring(st):
    l=0
    best=0
    s=set()
    for r,c in enumerate(st):
        while c in s:
            s.remove(st[l])
            l+=1
        s.add(c)
        best = max(best,r-l+1)
    return best 


# --- #2 Best Time to Buy and Sell Stock ----------------------------------
# One buy, one later sell. Max profit (0 if none). prices[i] = price on day i.
#   [7,1,5,3,6,4] -> 5  (buy at 1, sell at 6)
# Window view: l = cheapest-so-far buy day, r = today's sell day.
def max_profit(prices):
    l=0
    maxProfit = 0
    for r in range(1,len(prices)):
        price = prices[r]
        maxProfit = max(maxProfit,prices[r]-prices[l])
        if price < prices[l]:
            l=r;
    return maxProfit  





# --- #3 Longest Repeating Character Replacement --------------------------
# You may replace at most k chars. Return the longest substring of ONE
# repeated letter you can make.  s="AABABBA", k=1 -> 4
# Window is valid while: (window length - count of the most frequent char) <= k.
def character_replacement(s, k):
    m={s[0]:1}
    l=0
    best=0
    for r in range(1,len(s)):
        ch=s[r]
        m[ch]=m.get(ch,0)+1

        while (r-l+1) - max(m.values()) >k:
            m[s[l]]-=1
            l+=1
        best = max(best,r-l+1)
    return best

        



# --- #4 Minimum Size Subarray Sum ----------------------------------------
# Return the MINIMAL length of a contiguous subarray whose sum >= target,
# or 0 if none.  target=7, nums=[2,3,1,2,4,3] -> 2  (the subarray [4,3])
# This is a SHRINK-to-minimize window: grow r to reach the sum, then shrink l.
def min_subarray_len(target, nums):
    l=0
    currentSum=nums[l]
    best=float('inf')
    for r in range(1,len(nums)):
        currentSum+=nums[r]
        while currentSum >= target:
            best = min(best,r-l+1)
            currentSum-=nums[l]
            l+=1
    return best if best != float('inf') else 0
        
        
        




# --- TESTS ---------------------------------------------------------------
def _check(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got!r}", "" if ok else f"(want {want!r})")


if __name__ == "__main__":
    _check("longest_substr", length_of_longest_substring("abcabcbb"), 3)
    _check("longest_substr", length_of_longest_substring("bbbbb"),    1)
    _check("longest_substr", length_of_longest_substring("pwwkew"),   3)
    _check("longest_substr", length_of_longest_substring("abba"),     2)
    _check("max_profit",     max_profit([7, 1, 5, 3, 6, 4]),          5)
    _check("max_profit",     max_profit([7, 6, 4, 3, 1]),             0)
    _check("char_replace",   character_replacement("AABABBA", 1),     4)
    _check("min_subarray",   min_subarray_len(7, [2, 3, 1, 2, 4, 3]), 2)
    _check("min_subarray",   min_subarray_len(11, [1, 1, 1]),         0)
