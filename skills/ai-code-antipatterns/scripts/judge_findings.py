#!/usr/bin/env python3
"""Apply a deterministic vibe-coding threshold to verified findings."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


MODES = {
    "lenient": {
        "min_patterns": 1,
        "min_occurrences": 1,
        "min_repeated_patterns": 0,
    },
    "balanced": {
        "min_patterns": 2,
        "min_occurrences": 3,
        "min_repeated_patterns": 1,
    },
    "conservative": {
        "min_patterns": 3,
        "min_occurrences": 3,
        "min_repeated_patterns": 2,
    },
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


def locations_for(finding: dict[str, Any], index: int) -> list[str]:
    locations = finding.get("locations")
    if isinstance(locations, list) and locations:
        result: list[str] = []
        for location_index, location in enumerate(locations):
            if not isinstance(location, dict):
                continue
            path = location.get("path", "<unknown>")
            line = location.get("line", "?")
            result.append(f"{path}:{line}")
        if result:
            return result
    path = finding.get("path", "<unknown>")
    line = finding.get("line", "?")
    fallback = f"finding-{index}" if path == "<unknown>" and line == "?" else f"{path}:{line}"
    return [fallback]


def calculate(findings: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    occurrences: set[tuple[str, str]] = set()
    ignored = 0
    for index, finding in enumerate(findings):
        if finding.get("confidence") != "high":
            ignored += 1
            continue
        pattern = finding.get("pattern_id")
        if not isinstance(pattern, str) or not pattern:
            raise ValueError(f"high-confidence finding {index} has no pattern_id")
        for location in locations_for(finding, index):
            occurrences.add((pattern, location))

    counts = Counter(pattern for pattern, _ in occurrences)
    repeated = sorted(pattern for pattern, count in counts.items() if count >= 2)
    threshold = MODES[mode]
    satisfied = (
        len(counts) >= threshold["min_patterns"]
        and len(occurrences) >= threshold["min_occurrences"]
        and len(repeated) >= threshold["min_repeated_patterns"]
    )
    return {
        "mode": mode,
        "verdict": "reasonable_suspicion" if satisfied else "insufficient_evidence",
        "high_confidence_patterns": len(counts),
        "high_confidence_occurrences": len(occurrences),
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
