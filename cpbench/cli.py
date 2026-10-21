"""cpbench: does the model's code survive tests beyond the ones in the problem statement?

    python -m cpbench.cli run
    python -m cpbench.cli run --models groq:qwen/qwen3.8-27b --problems lis_length to_roman
    python -m cpbench.cli check-refs     # run the reference solutions through the same harness
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from .llm import chat
from .problems import PROBLEMS, build_tests
from .sandbox import run_category

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CATEGORIES = ["base", "edge", "random", "stress"]
DEFAULT_MODELS = ["groq:openai/gpt-oss-20b", "groq:openai/gpt-oss-120b", "groq:qwen/qwen3.8-27b", "groq:allam-2-7b"]

PROMPT = """Complete the following Python function. It will be judged on hidden tests, including edge cases and \
large inputs at the stated limits, so make it correct and efficient.

```python
{prompt}
```

Reply with the full function in one ```python code block. Standard library only."""


def extract_code(text):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    return max(blocks, key=len) if blocks else text


def evaluate(code, p, tests):
    out = {}
    for cat in CATEGORIES:
        timeout = p["stress_timeout"] * len(tests[cat]) if cat == "stress" else 10
        out[cat] = run_category(code, tests[cat], p["entry"], timeout)
        if out[cat]["status"] == "load_error":
            break  # nothing else will work either
    return out


def run(args):
    names = args.problems or list(PROBLEMS)
    RESULTS.mkdir(exist_ok=True)
    tests = {n: build_tests(PROBLEMS[n]) for n in names}
    for model in args.models:
        rows = []
        print(f"\n== {model}")
        for n in names:
            p = PROBLEMS[n]
            for s in range(args.samples):
                try:
                    reply = chat(model, [{"role": "user", "content": PROMPT.format(prompt=p["prompt"])}],
                                 temperature=0.0 if args.samples == 1 else 0.8, max_tokens=4096)
                except Exception as e:
                    reply = f"# generation failed: {e}"
                code = extract_code(reply)
                res = evaluate(code, p, tests[n])
                rows.append({"problem": n, "sample": s, "code": code, "results": res})
                status = " ".join(f"{c}={res[c]['status']}" for c in CATEGORIES if c in res)
                print(f"  {n:26} {status}")
        safe = model.split(":", 1)[-1].replace("/", "_")
        (RESULTS / f"{safe}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    report()


def passed(res, upto):
    """'base' = passes the statement samples. 'plus' = passes everything."""
    cats = CATEGORIES[:CATEGORIES.index(upto) + 1]
    return all(res.get(c, {}).get("status") == "pass" for c in cats)


def report(*_):
    lines = ["# Results", "",
             "**base** = passes the sample tests from the problem statement. "
             "**plus** = also passes edge cases, 40 random tests checked against a reference, and max-size stress tests.",
             "", "| model | base pass@1 | plus pass@1 | base - plus |", "|---|---|---|---|"]
    per_problem, first_fail = {}, {}
    for f in sorted(RESULTS.glob("*.json")):
        rows = json.loads(f.read_text(encoding="utf-8"))
        if not rows:
            continue
        base = sum(passed(r["results"], "base") for r in rows) / len(rows)
        plus = sum(passed(r["results"], "stress") for r in rows) / len(rows)
        lines.append(f"| `{f.stem}` | {base:.0%} | {plus:.0%} | {round((base - plus) * 100)} pts |")
        per_problem[f.stem] = {}
        fails = Counter()
        for r in rows:
            res = r["results"]
            if passed(res, "stress"):
                mark = "✅"
            elif not passed(res, "base"):
                mark = "❌ base"
            else:
                bad = next(c for c in CATEGORIES if res.get(c, {}).get("status") != "pass")
                mark = f"⚠️ {bad} ({res[bad]['status']})"
                fails[f"{bad}: {res[bad]['status']}"] += 1
            per_problem[f.stem][r["problem"]] = mark
        first_fail[f.stem] = fails

    if per_problem:
        models = list(per_problem)
        lines += ["", "## Per problem", "", "| problem | " + " | ".join(f"`{m}`" for m in models) + " |",
                  "|---" * (len(models) + 1) + "|"]
        for n in PROBLEMS:
            if any(n in per_problem[m] for m in models):
                lines.append(f"| {n} | " + " | ".join(per_problem[m].get(n, "-") for m in models) + " |")
        lines += ["", "## Where base-passing solutions broke", ""]
        for m, c in first_fail.items():
            lines.append(f"- `{m}`: " + (", ".join(f"{k} x{v}" for k, v in c.most_common()) or "nothing"))
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'summary.md'}")


def check_refs(args):
    """Sanity check: the reference solutions must pass their own tests, including the timeouts."""
    import inspect
    ok = True
    for n, p in PROBLEMS.items():
        src = inspect.getsource(p["ref"])
        # getsource includes the @problem(...) decorator, whose prompt also contains a 'def'.
        # The real function is the last top-level def.
        src = "import bisect, heapq\n" + src[src.rindex("\ndef ") + 1:]
        res = evaluate(src, p, build_tests(p))
        status = {c: res[c]["status"] for c in res}
        good = all(s == "pass" for s in status.values())
        ok &= good
        print(f"{'ok ' if good else 'BAD'} {n:26} {status}")
    raise SystemExit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(prog="cpbench")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    r.add_argument("--problems", nargs="*")
    r.add_argument("--samples", type=int, default=1)
    sub.add_parser("report")
    sub.add_parser("check-refs")
    args = ap.parse_args()
    {"run": run, "report": report, "check-refs": check_refs}[args.cmd](args)


if __name__ == "__main__":
    main()
