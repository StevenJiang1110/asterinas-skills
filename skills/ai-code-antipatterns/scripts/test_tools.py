#!/usr/bin/env python3
"""Self-tests for the deterministic AI anti-pattern helper scripts."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_scanner() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "sample.rs"
        source.write_text(
            """// This PR follows Linux `do_example()` internals.
// See https://example.com/project/latest/source.rs#L10.
/// Returns the current value.
fn current_value(value: usize) -> usize {
    value
}

fn caller(value: usize) -> Option<usize> {
    current_value(value).checked_mul(2)
}
""",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "scan_candidates.py"),
                "--repo-root",
                str(root),
                "--files",
                "sample.rs",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        patterns = {candidate["pattern_id"] for candidate in result["candidates"]}
        expected = {"AP-CONTEXT", "AP-REF", "AP-DEFENSIVE", "AP-DOC", "AP-UPSTREAM", "AP-WRAP"}
        missing = expected - patterns
        assert not missing, f"scanner missed expected candidates: {sorted(missing)}"

        diff = root / "sample.diff"
        diff.write_text(
            """diff --git a/sample.rs b/sample.rs
--- a/sample.rs
+++ b/sample.rs
@@ -1 +1,2 @@
 fn current_value() {}
+
@@ -3 +4 @@
-// Old note.
+// Reworded note.
""",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "scan_candidates.py"),
                "--repo-root",
                str(root),
                "--diff-file",
                str(diff),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        scope_candidates = [
            candidate
            for candidate in result["candidates"]
            if candidate["pattern_id"] == "AP-SCOPE"
        ]
        assert len(scope_candidates) == 2
        assert {candidate["line"] for candidate in scope_candidates} == {2, 4}


def finding(pattern: str, line: int, confidence: str = "high") -> dict[str, object]:
    return {
        "pattern_id": pattern,
        "confidence": confidence,
        "path": "sample.rs",
        "line": line,
    }


def test_judgment() -> None:
    judge = load_module("judge_findings", SCRIPT_DIR / "judge_findings.py")

    assert judge.calculate([finding("AP-REF", 1)], "lenient")["verdict"] == "reasonable_suspicion"
    assert judge.calculate([finding("AP-REF", 1, "medium")], "lenient")["verdict"] == "insufficient_evidence"

    conservative_pass = [
        finding("AP-REF", 1),
        finding("AP-REF", 2),
        finding("AP-DOC", 3),
        finding("AP-DOC", 4),
        finding("AP-WRAP", 5),
    ]
    result = judge.calculate(conservative_pass, "conservative")
    assert result["verdict"] == "reasonable_suspicion"
    assert result["repeated_patterns"] == ["AP-DOC", "AP-REF"]

    conservative_fail = [
        finding("AP-REF", 1),
        finding("AP-DOC", 2),
        finding("AP-WRAP", 3),
    ]
    assert judge.calculate(conservative_fail, "conservative")["verdict"] == "insufficient_evidence"

    balanced_pass = [
        finding("AP-REF", 1),
        finding("AP-REF", 2),
        finding("AP-DOC", 3),
    ]
    assert judge.calculate(balanced_pass, "balanced")["verdict"] == "reasonable_suspicion"


def main() -> int:
    test_scanner()
    test_judgment()
    print("all helper-script tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
