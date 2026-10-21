"""Runs inside a child process: load candidate code, run one category of tests, print JSON.

Kept separate from the parent so a crash, infinite loop or os.exit in model code
can't take the bench down with it. The parent kills us on timeout.
"""
import json
import math
import sys


def same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(float(a), float(b), rel_tol=1e-6, abs_tol=1e-6)
        except (TypeError, ValueError):
            return False
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def main():
    code_path, tests_path, entry = sys.argv[1:4]
    sys.setrecursionlimit(10_000)
    ns = {"__name__": "candidate"}
    try:
        exec(compile(open(code_path, encoding="utf-8").read(), "candidate.py", "exec"), ns)
        fn = ns[entry]
    except Exception as e:
        print(json.dumps({"status": "load_error", "error": f"{type(e).__name__}: {e}"[:300]}))
        return
    tests = json.load(open(tests_path, encoding="utf-8"))
    for i, t in enumerate(tests):
        try:
            got = fn(*t["args"])
            got = json.loads(json.dumps(got))  # tuples -> lists, same as expected
        except Exception as e:
            print(json.dumps({"status": "runtime_error", "index": i, "error": f"{type(e).__name__}: {e}"[:300]}))
            return
        if not same(got, t["expected"]):
            shown = json.dumps(t["args"])[:200]
            print(json.dumps({"status": "wrong_answer", "index": i, "input": shown,
                              "expected": str(t["expected"])[:100], "got": str(got)[:100]}))
            return
    print(json.dumps({"status": "pass", "count": len(tests)}))


if __name__ == "__main__":
    main()
