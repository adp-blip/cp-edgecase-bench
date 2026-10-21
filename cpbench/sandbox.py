"""Execute model-written code against a test category in an isolated subprocess.

This is NOT a security sandbox. It runs in a throwaway temp dir with `python -I`
and a hard timeout, which is enough for code from mainstream models. Don't point
this at untrusted models without a container.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS = Path(__file__).with_name("harness.py")


def run_category(code, tests, entry, timeout):
    with tempfile.TemporaryDirectory(prefix="cpbench_") as tmp:
        tmp = Path(tmp)
        (tmp / "candidate.py").write_text(code, encoding="utf-8")
        (tmp / "tests.json").write_text(json.dumps(tests), encoding="utf-8")
        try:
            proc = subprocess.run([sys.executable, "-I", str(HARNESS), "candidate.py", "tests.json", entry],
                                  cwd=tmp, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "timeout": timeout}
        lines = [l for l in proc.stdout.splitlines() if l.startswith("{")]
        if not lines:
            return {"status": "crash", "error": (proc.stderr or proc.stdout)[-300:]}
        return json.loads(lines[-1])
