"""Cross-check every fast reference solution against a dumb brute force on random small inputs.
If a reference is wrong, every score in the bench is wrong, so this matters more than it looks."""
import itertools
import random
import statistics

from cpbench.problems import PROBLEMS
from cpbench.sandbox import run_category

rng = random.Random(0)
ref = {n: p["ref"] for n, p in PROBLEMS.items()}


def test_max_subarray():
    for _ in range(300):
        a = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        brute = max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert ref["max_subarray"](a) == brute


def test_count_inversions():
    for _ in range(300):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 12))]
        brute = sum(a[i] > a[j] for i, j in itertools.combinations(range(len(a)), 2))
        assert ref["count_inversions"](a) == brute


def test_longest_unique_substring():
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        brute = max([j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                     if len(set(s[i:j])) == j - i] or [0])
        assert ref["longest_unique_substring"](s) == brute


def test_lis_length():
    for _ in range(200):
        a = [rng.randint(-4, 4) for _ in range(rng.randint(0, 9))]
        brute = max([len(c) for r in range(len(a) + 1) for c in itertools.combinations(a, r)
                     if all(x < y for x, y in zip(c, c[1:]))] or [0])
        assert ref["lis_length"](a) == brute


def test_running_median():
    for _ in range(200):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 15))]
        assert ref["running_median"](a) == [float(statistics.median(a[:i + 1])) for i in range(len(a))]


def test_count_pairs():
    for _ in range(200):
        a = [rng.randint(-5, 5) for _ in range(rng.randint(0, 12))]
        t = rng.randint(-5, 5)
        assert ref["count_pairs_with_sum"](a, t) == sum(x + y == t for x, y in itertools.combinations(a, 2))


def test_min_coins_against_bfs():
    for _ in range(200):
        coins = rng.sample(range(1, 12), rng.randint(1, 3))
        amount = rng.randint(0, 40)
        best = -1
        for k in range(amount + 1):
            if any(sum(c) == amount for c in itertools.combinations_with_replacement(coins, k)):
                best = k
                break
        assert ref["min_coins"](coins, amount) == best


def test_sandbox_catches_wrong_answers_and_timeouts():
    tests = [{"args": [3], "expected": 6}]
    assert run_category("def f(x): return x * 2", tests, "f", 5)["status"] == "pass"
    assert run_category("def f(x): return x + 2", tests, "f", 5)["status"] == "wrong_answer"
    assert run_category("def f(x):\n    while True: pass", tests, "f", 2)["status"] == "timeout"
    assert run_category("this is not python", tests, "f", 5)["status"] == "load_error"
