#!/usr/bin/env python3
"""Apply a deterministic vibe-coding threshold to verified findings."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


STRONG_PATTERNS = frozenset({"AP-REF", "AP-WRAP", "AP-CONTEXT", "AP-SCOPE"})
WEAK_PATTERNS = frozenset({"AP-DEFENSIVE", "AP-DOC", "AP-REINVENT", "AP-UPSTREAM"})

# Each mode passes if any alternative satisfies all its minimum counts.
MODES = {
    "lenient": [
        {"strong_occurrences": 1},
        {"weak_occurrences": 2, "weak_patterns": 2},
    ],
    "balanced": [
        {"strong_occurrences": 2, "strong_patterns": 2},
        {"strong_occurrences": 1, "weak_occurrences": 2, "patterns": 3},
    ],
    "conservative": [
        {"strong_occurrences": 3, "strong_patterns": 2},
        {"strong_occurrences": 2, "weak_occurrences": 2, "patterns": 3},
    ],
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Judge verified AI anti-pattern findings using a fixed calibration."
    )
    parser.add_argument("findings", help="JSON file containing a findings array")
    parser.add_argument(
        "--mode",
        choices=sorted(MODES),
        default="conservative",
        help="judgment calibration (default: conservative)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="output format (default: json)",
    )
    parser.add_argument("--output", help="write output to this path instead of stdout")
    return parser.parse_args()


def load_findings(path: Path) -> tuple[str | None, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return None, data
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        raise ValueError("input must be a findings array or an object containing a findings array")
    return data.get("scope"), data["findings"]


def calculate(findings: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    occurrences: dict[str, str] = {}
    ignored = 0
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValueError(f"finding {index} must be an object")
        if finding.get("confidence") != "high":
            ignored += 1
            continue
        pattern = finding.get("pattern_id")
        if not isinstance(pattern, str) or pattern not in STRONG_PATTERNS | WEAK_PATTERNS:
            raise ValueError(f"high-confidence finding {index} has an unknown pattern_id")
        occurrence_id = finding.get("occurrence_id")
        if not isinstance(occurrence_id, str) or not occurrence_id.strip():
            raise ValueError(f"high-confidence finding {index} needs an occurrence_id")
        locations = finding.get("locations", [finding])
        if not isinstance(locations, list) or not locations:
            raise ValueError(f"high-confidence finding {index} needs source locations")
        for location in locations:
            if (
                not isinstance(location, dict)
                or not isinstance(location.get("path"), str)
                or not location["path"].strip()
                or type(location.get("line")) is not int
                or location["line"] < 1
            ):
                raise ValueError(f"high-confidence finding {index} needs concrete path and line")
        if occurrence_id in occurrences and occurrences[occurrence_id] != pattern:
            raise ValueError(f"occurrence {occurrence_id!r} has conflicting primary patterns")
        occurrences[occurrence_id] = pattern

    counts = Counter(occurrences.values())
    repeated = sorted(pattern for pattern, count in counts.items() if count >= 2)
    metrics = {
        "strong_occurrences": sum(count for pattern, count in counts.items() if pattern in STRONG_PATTERNS),
        "weak_occurrences": sum(count for pattern, count in counts.items() if pattern in WEAK_PATTERNS),
        "strong_patterns": len(counts.keys() & STRONG_PATTERNS),
        "weak_patterns": len(counts.keys() & WEAK_PATTERNS),
        "patterns": len(counts),
    }
    threshold = MODES[mode]
    satisfied = any(
        all(metrics[key] >= minimum for key, minimum in alternative.items())
        for alternative in threshold
    )
    return {
        "mode": mode,
        "verdict": "reasonable_suspicion" if satisfied else "insufficient_evidence",
        "high_confidence_patterns": len(counts),
        "high_confidence_occurrences": len(occurrences),
        "signal_counts": metrics,
        "repeated_patterns": repeated,
        "occurrences_by_pattern": dict(sorted(counts.items())),
        "ignored_non_high_findings": ignored,
        "threshold": threshold,
    }


def render_markdown(scope: str | None, result: dict[str, Any]) -> str:
    verdict = (
        "Reasonable suspicion of unchecked vibe coding"
        if result["verdict"] == "reasonable_suspicion"
        else "Insufficient evidence for that conclusion"
    )
    repeated = ", ".join(result["repeated_patterns"]) or "none"
    lines = [
        f"**Verdict:** {verdict}",
        "",
        f"- Scope: {scope or 'not supplied in findings JSON'}",
        f"- Calibration: `{result['mode']}`",
        f"- High-confidence patterns: {result['high_confidence_patterns']}",
        f"- High-confidence occurrences: {result['high_confidence_occurrences']}",
        f"- Strong signals: {result['signal_counts']['strong_occurrences']} occurrences across {result['signal_counts']['strong_patterns']} patterns",
        f"- Weak signals: {result['signal_counts']['weak_occurrences']} occurrences across {result['signal_counts']['weak_patterns']} patterns",
        f"- Repeated patterns: {repeated}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        scope, findings = load_findings(Path(args.findings))
        result = calculate(findings, args.mode)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        rendered = render_markdown(scope, result)
    else:
        rendered = json.dumps({"scope": scope, **result}, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
