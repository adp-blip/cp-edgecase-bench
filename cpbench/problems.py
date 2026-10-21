"""Problem set. Each problem has:

  prompt  - what the model sees (signature + statement + the 2-3 sample tests a judge would show)
  ref     - a reference solution, used to compute expected outputs
  base    - the sample tests from the statement (this is what "looks correct" means)
  edge    - hand-picked corner cases (empty, single element, duplicates, negatives, limits)
  random  - generator for random small/medium inputs, checked against ref
  stress  - a few max-size inputs; a correct but slow solution times out here

Inputs are lists of positional args so they serialize to JSON.
"""
import bisect
import heapq
import random as _r

PROBLEMS = {}


def problem(name, entry, prompt, base, edge, random_gen, stress_gen, stress_timeout=6):
    def deco(ref):
        PROBLEMS[name] = dict(name=name, entry=entry, prompt=prompt.strip(), ref=ref, base=base, edge=edge,
                              random=random_gen, stress=stress_gen, stress_timeout=stress_timeout)
        return ref
    return deco


# 1 ---------------------------------------------------------------------------
@problem(
    "max_subarray", "max_subarray",
    '''
def max_subarray(nums: list[int]) -> int:
    """Return the largest sum of a non-empty contiguous subarray. 1 <= len(nums) <= 2*10^5.
    >>> max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])
    6
    >>> max_subarray([1, 2, 3])
    6
    """
''',
    base=[[[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[1, 2, 3]]],
    edge=[[[-5]], [[-3, -1, -2]], [[0, 0, 0]], [[10**9, -1, 10**9]], [[-1, 0, -2]]],
    random_gen=lambda rng: [[rng.randint(-50, 50) for _ in range(rng.randint(1, 40))]],
    stress_gen=lambda rng: [[rng.randint(-10**4, 10**4) for _ in range(200_000)]],
)
def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


# 2 ---------------------------------------------------------------------------
@problem(
    "count_inversions", "count_inversions",
    '''
def count_inversions(arr: list[int]) -> int:
    """Count pairs (i, j) with i < j and arr[i] > arr[j]. 0 <= len(arr) <= 10^5.
    >>> count_inversions([2, 4, 1, 3, 5])
    3
    >>> count_inversions([1, 2, 3])
    0
    """
''',
    base=[[[2, 4, 1, 3, 5]], [[1, 2, 3]]],
    edge=[[[]], [[7]], [[3, 3, 3]], [[5, 4, 3, 2, 1]], [[2, 1, 2, 1]]],
    random_gen=lambda rng: [[rng.randint(-20, 20) for _ in range(rng.randint(0, 60))]],
    stress_gen=lambda rng: [[rng.randint(-10**9, 10**9) for _ in range(100_000)]],
)
def count_inversions(arr):
    def sort(a):
        if len(a) < 2:
            return a, 0
        m = len(a) // 2
        left, x = sort(a[:m])
        right, y = sort(a[m:])
        out, inv, i, j = [], x + y, 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
                inv += len(left) - i
        return out + left[i:] + right[j:], inv
    return sort(list(arr))[1]


# 3 ---------------------------------------------------------------------------
@problem(
    "merge_intervals", "merge_intervals",
    '''
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Merge overlapping closed intervals [start, end] and return them sorted by start.
    Intervals that touch (end == next start) count as overlapping. Input may be unsorted.
    >>> merge_intervals([[1, 3], [2, 6], [8, 10]])
    [[1, 6], [8, 10]]
    >>> merge_intervals([[1, 4], [5, 6]])
    [[1, 4], [5, 6]]
    """
''',
    base=[[[[1, 3], [2, 6], [8, 10]]], [[[1, 4], [5, 6]]]],
    edge=[[[]], [[[5, 5]]], [[[1, 2], [2, 3]]], [[[8, 10], [1, 3], [2, 6]]], [[[1, 10], [2, 3], [4, 5]]],
          [[[-5, -1], [-3, 0]]]],
    random_gen=lambda rng: [[sorted([rng.randint(-30, 30), rng.randint(-30, 30)]) for _ in range(rng.randint(0, 15))]],
    stress_gen=lambda rng: [[sorted([rng.randint(0, 10**9), rng.randint(0, 10**9)]) for _ in range(100_000)]],
)
def merge_intervals(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


# 4 ---------------------------------------------------------------------------
@problem(
    "longest_unique_substring", "longest_unique_substring",
    '''
def longest_unique_substring(s: str) -> int:
    """Length of the longest substring without repeating characters. 0 <= len(s) <= 10^5.
    >>> longest_unique_substring("abcabcbb")
    3
    >>> longest_unique_substring("pwwkew")
    3
    """
''',
    base=[["abcabcbb"], ["pwwkew"]],
    edge=[[""], ["a"], ["aaaa"], ["abba"], ["dvdf"], [" "], ["tmmzuxt"]],
    random_gen=lambda rng: ["".join(rng.choice("abcde ") for _ in range(rng.randint(0, 40)))],
    stress_gen=lambda rng: ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(100_000))],
)
def longest_unique_substring(s):
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best


# 5 ---------------------------------------------------------------------------
@problem(
    "valid_brackets", "valid_brackets",
    '''
def valid_brackets(s: str) -> bool:
    """True if every bracket in s is closed in the right order. s contains only ()[]{} characters.
    >>> valid_brackets("()[]{}")
    True
    >>> valid_brackets("(]")
    False
    """
''',
    base=[["()[]{}"], ["(]"]],
    edge=[[""], ["("], [")"], ["([)]"], ["{[]}"], ["(("], ["))(("], ["]"]],
    random_gen=lambda rng: ["".join(rng.choice("()[]{}") for _ in range(rng.choice([0, 2, 4, 6, 8, 5])))],
    stress_gen=lambda rng: ["([{" * 50_000 + "}])" * 50_000],
)
def valid_brackets(s):
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


# 6 ---------------------------------------------------------------------------
@problem(
    "min_coins", "min_coins",
    '''
def min_coins(coins: list[int], amount: int) -> int:
    """Fewest coins (unlimited supply of each) that sum to amount, or -1 if impossible.
    1 <= len(coins) <= 12, 1 <= coins[i] <= 10^4, 0 <= amount <= 10^4.
    >>> min_coins([1, 2, 5], 11)
    3
    >>> min_coins([2], 3)
    -1
    """
''',
    base=[[[1, 2, 5], 11], [[2], 3]],
    edge=[[[1], 0], [[7], 0], [[2], 1], [[1, 3, 4], 6], [[5, 10], 3], [[10000], 10000], [[3, 7], 11]],
    random_gen=lambda rng: [sorted(rng.sample(range(1, 30), rng.randint(1, 5))), rng.randint(0, 120)],
    stress_gen=lambda rng: [sorted(rng.sample(range(1, 500), 12)), 10_000],
)
def min_coins(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] <= amount else -1


# 7 ---------------------------------------------------------------------------
@problem(
    "spiral_order", "spiral_order",
    '''
def spiral_order(matrix: list[list[int]]) -> list[int]:
    """Return the elements of an m x n matrix in clockwise spiral order, starting top-left.
    0 <= m, n <= 300.
    >>> spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    [1, 2, 3, 6, 9, 8, 7, 4, 5]
    """
''',
    base=[[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]],
    edge=[[[]], [[[1]]], [[[1, 2, 3, 4]]], [[[1], [2], [3]]], [[[1, 2], [3, 4], [5, 6]]],
          [[[1, 2, 3], [4, 5, 6]]], [[[]]]],
    random_gen=lambda rng: [(lambda m, n: [[rng.randint(0, 99) for _ in range(n)] for _ in range(m)])(
        rng.randint(1, 7), rng.randint(1, 7))],
    stress_gen=lambda rng: [[[rng.randint(0, 9) for _ in range(300)] for _ in range(300)]],
)
def spiral_order(matrix):
    out = []
    if not matrix or not matrix[0]:
        return out
    top, bot, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    while top <= bot and left <= right:
        out += matrix[top][left:right + 1]
        out += [matrix[r][right] for r in range(top + 1, bot + 1)]
        if top < bot:
            out += matrix[bot][left:right][::-1]
        if left < right:
            out += [matrix[r][left] for r in range(bot - 1, top, -1)]
        top, bot, left, right = top + 1, bot - 1, left + 1, right - 1
    return out


# 8 ---------------------------------------------------------------------------
@problem(
    "count_primes", "count_primes",
    '''
def count_primes(n: int) -> int:
    """Number of primes strictly less than n. 0 <= n <= 5*10^6.
    >>> count_primes(10)
    4
    >>> count_primes(20)
    8
    """
''',
    base=[[10], [20]],
    edge=[[0], [1], [2], [3], [4], [100]],
    random_gen=lambda rng: [rng.randint(0, 3000)],
    stress_gen=lambda rng: [5_000_000],
    stress_timeout=8,
)
def count_primes(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n, i)))
    return sum(sieve)


# 9 ---------------------------------------------------------------------------
@problem(
    "count_pairs_with_sum", "count_pairs_with_sum",
    '''
def count_pairs_with_sum(nums: list[int], target: int) -> int:
    """Count index pairs (i, j) with i < j and nums[i] + nums[j] == target. 0 <= len(nums) <= 10^5.
    >>> count_pairs_with_sum([1, 5, 7, -1], 6)
    2
    >>> count_pairs_with_sum([1, 2, 3], 10)
    0
    """
''',
    base=[[[1, 5, 7, -1], 6], [[1, 2, 3], 10]],
    edge=[[[], 0], [[3], 6], [[3, 3, 3], 6], [[0, 0, 0, 0], 0], [[-2, 2, -2, 2], 0], [[1, 1], 3]],
    random_gen=lambda rng: [[rng.randint(-10, 10) for _ in range(rng.randint(0, 40))], rng.randint(-10, 10)],
    stress_gen=lambda rng: [[rng.randint(-1000, 1000) for _ in range(100_000)], 7],
)
def count_pairs_with_sum(nums, target):
    seen, count = {}, 0
    for x in nums:
        count += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


# 10 --------------------------------------------------------------------------
@problem(
    "lis_length", "lis_length",
    '''
def lis_length(nums: list[int]) -> int:
    """Length of the longest strictly increasing subsequence. 0 <= len(nums) <= 10^5.
    >>> lis_length([10, 9, 2, 5, 3, 7, 101, 18])
    4
    >>> lis_length([0, 1, 0, 3, 2, 3])
    4
    """
''',
    base=[[[10, 9, 2, 5, 3, 7, 101, 18]], [[0, 1, 0, 3, 2, 3]]],
    edge=[[[]], [[5]], [[7, 7, 7, 7]], [[5, 4, 3, 2, 1]], [[1, 2, 2, 3]], [[-1, -2, 0]]],
    random_gen=lambda rng: [[rng.randint(-15, 15) for _ in range(rng.randint(0, 50))]],
    stress_gen=lambda rng: [[rng.randint(-10**9, 10**9) for _ in range(100_000)]],
)
def lis_length(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


# 11 --------------------------------------------------------------------------
@problem(
    "to_roman", "to_roman",
    '''
def to_roman(n: int) -> str:
    """Convert 1 <= n <= 3999 to a Roman numeral using subtractive notation (IV, IX, XL, XC, CD, CM).
    >>> to_roman(58)
    'LVIII'
    >>> to_roman(1994)
    'MCMXCIV'
    """
''',
    base=[[58], [1994]],
    edge=[[1], [4], [9], [14], [40], [90], [400], [900], [3999], [3888], [444], [999]],
    random_gen=lambda rng: [rng.randint(1, 3999)],
    stress_gen=lambda rng: [3999],
)
def to_roman(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for v, s in vals:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


# 12 --------------------------------------------------------------------------
@problem(
    "running_median", "running_median",
    '''
def running_median(nums: list[int]) -> list[float]:
    """After each element is added, record the median of all elements so far.
    For an even count the median is the mean of the two middle values. Return floats.
    0 <= len(nums) <= 5*10^4.
    >>> running_median([5, 15, 1, 3])
    [5.0, 10.0, 5.0, 4.0]
    """
''',
    base=[[[5, 15, 1, 3]]],
    edge=[[[]], [[7]], [[2, 2, 2]], [[-1, -3, -2]], [[1, 2]], [[10**9, -10**9]]],
    random_gen=lambda rng: [[rng.randint(-50, 50) for _ in range(rng.randint(0, 30))]],
    stress_gen=lambda rng: [[rng.randint(-10**6, 10**6) for _ in range(50_000)]],
)
def running_median(nums):
    lo, hi, out = [], [], []  # lo is a max-heap (negated), hi is a min-heap
    for x in nums:
        if lo and x > -lo[0]:
            heapq.heappush(hi, x)
        else:
            heapq.heappush(lo, -x)
        if len(lo) > len(hi) + 1:
            heapq.heappush(hi, -heapq.heappop(lo))
        elif len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(float(-lo[0]) if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2)
    return out


def build_tests(p, n_random=40, n_stress=2, seed=1234):
    """Materialize all test inputs + expected outputs for one problem."""
    rng = _r.Random(seed)
    tests = {"base": p["base"], "edge": p["edge"],
             "random": [p["random"](rng) for _ in range(n_random)],
             "stress": [p["stress"](rng) for _ in range(n_stress)]}
    import copy
    return {cat: [{"args": args, "expected": p["ref"](*copy.deepcopy(args))} for args in inputs]
            for cat, inputs in tests.items()}
