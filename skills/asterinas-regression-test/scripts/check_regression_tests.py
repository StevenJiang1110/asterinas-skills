#!/usr/bin/env python3
"""Find mechanically detectable Asterinas regression-test convention issues.

The script intentionally reports uncertain structural matches as "candidate".
Callers must inspect candidates in context before editing code or reporting a
review finding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


C_SUFFIXES = {".c", ".h"}
MACROS = ("TEST_SUCC", "TEST_ERRNO", "TEST_RES", "TEST", "CHECK_WITH", "CHECK")
TEST_MACROS = {"TEST", "TEST_SUCC", "TEST_ERRNO", "TEST_RES"}
CHECK_MACROS = {"CHECK", "CHECK_WITH"}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    message: str


def mask_c(source: str) -> str:
    """Mask comments and literals while preserving positions and newlines."""
    out = list(source)
    i = 0
    state = "code"
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                out[i] = out[i + 1] = " "
                i += 2
                state = "line_comment"
                continue
            if ch == "/" and nxt == "*":
                out[i] = out[i + 1] = " "
                i += 2
                state = "block_comment"
                continue
            if ch == '"':
                out[i] = " "
                state = "string"
            elif ch == "'":
                out[i] = " "
                state = "char"
        elif state == "line_comment":
            if ch == "\n":
                state = "code"
            else:
                out[i] = " "
        elif state == "block_comment":
            if ch == "*" and nxt == "/":
                out[i] = out[i + 1] = " "
                i += 2
                state = "code"
                continue
            if ch != "\n":
                out[i] = " "
        elif state in {"string", "char"}:
            quote = '"' if state == "string" else "'"
            if ch == "\\" and i + 1 < len(source):
                if ch != "\n":
                    out[i] = " "
                if source[i + 1] != "\n":
                    out[i + 1] = " "
                i += 2
                continue
            if ch == quote:
                out[i] = " "
                state = "code"
            elif ch != "\n":
                out[i] = " "
        i += 1
    return "".join(out)


def line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def context_ranges(masked: str) -> list[tuple[int, int, str]]:
    markers = re.compile(r"\b(FN_SETUP|END_SETUP|FN_TEST|END_TEST)\s*\(")
    ranges: list[tuple[int, int, str]] = []
    current: tuple[int, str] | None = None
    for match in markers.finditer(masked):
        kind = match.group(1)
        if kind in {"FN_SETUP", "FN_TEST"}:
            current = (match.start(), "setup" if kind == "FN_SETUP" else "test")
        elif current is not None:
            expected = "END_SETUP" if current[1] == "setup" else "END_TEST"
            if kind == expected:
                ranges.append((current[0], match.end(), current[1]))
                current = None
    return ranges


def context_at(offset: int, ranges: list[tuple[int, int, str]]) -> str:
    for start, end, context in ranges:
        if start <= offset <= end:
            return context
    return "outside"


def find_closing_paren(masked: str, opening: int) -> int | None:
    depth = 0
    for i in range(opening, len(masked)):
        if masked[i] == "(":
            depth += 1
        elif masked[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return None


def first_argument(source: str, masked: str, opening: int, closing: int) -> str:
    depth = 0
    for i in range(opening + 1, closing):
        ch = masked[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            return source[opening + 1 : i].strip()
    return source[opening + 1 : closing].strip()


def lacks_apparent_call(expression: str) -> bool:
    masked = mask_c(expression)
    # Ordinary calls, macro calls, and parenthesized function-pointer calls.
    if re.search(r"\b[A-Za-z_]\w*\s*\(", masked):
        return False
    if re.search(r"\)\s*\(", masked):
        return False
    return True


def line_is_preprocessor(masked: str, offset: int) -> bool:
    start = masked.rfind("\n", 0, offset) + 1
    return masked[start:offset].lstrip().startswith("#")


def scan_c(path: Path, source: str) -> list[Finding]:
    masked = mask_c(source)
    ranges = context_ranges(masked)
    findings: list[Finding] = []
    macro_pattern = re.compile(r"\b(" + "|".join(MACROS) + r")\s*\(")

    for match in macro_pattern.finditer(masked):
        macro = match.group(1)
        if line_is_preprocessor(masked, match.start()):
            continue
        opening = masked.find("(", match.start(), match.end())
        closing = find_closing_paren(masked, opening)
        if closing is None:
            continue
        line = line_number(source, match.start())
        context = context_at(match.start(), ranges)
        arg = first_argument(source, masked, opening, closing)

        if arg and lacks_apparent_call(arg):
            findings.append(
                Finding(
                    "violation",
                    "RT-01",
                    str(path),
                    line,
                    f"{macro} first argument has no apparent call: {arg!r}",
                )
            )

        if context == "setup" and macro in TEST_MACROS:
            findings.append(
                Finding(
                    "violation",
                    "RT-03",
                    str(path),
                    line,
                    f"{macro} is inside FN_SETUP; use CHECK/CHECK_WITH",
                )
            )
        elif context == "test" and macro in CHECK_MACROS:
            findings.append(
                Finding(
                    "candidate",
                    "RT-03",
                    str(path),
                    line,
                    f"{macro} is inside FN_TEST; confirm a child-process or similar exception requires it",
                )
            )
        elif context == "outside" and macro in TEST_MACROS:
            findings.append(
                Finding(
                    "violation",
                    "RT-03",
                    str(path),
                    line,
                    f"{macro} is outside FN_TEST",
                )
            )

    findings.extend(scan_asterinas_guards(path, source, masked))
    return findings


def previous_nonblank_line(lines: list[str], index: int) -> str:
    for line in reversed(lines[:index]):
        if line.strip():
            return line.strip()
    return ""


def scan_asterinas_guards(path: Path, source: str, masked: str) -> list[Finding]:
    lines = source.splitlines()
    masked_lines = masked.splitlines()
    findings: list[Finding] = []
    start_pattern = re.compile(
        r"^\s*#\s*(?:ifdef\s+__asterinas__|if\s+.*\b__asterinas__\b)"
    )
    directive_pattern = re.compile(r"^\s*#\s*(if|ifdef|ifndef|endif)\b")

    for index, line in enumerate(masked_lines):
        if not start_pattern.search(line):
            continue
        previous = previous_nonblank_line(lines, index)
        if not (previous.startswith("//") or previous.startswith("/*") or previous.endswith("*/")):
            findings.append(
                Finding(
                    "candidate",
                    "RT-06",
                    str(path),
                    index + 1,
                    "__asterinas__ guard has no immediately preceding explanatory comment",
                )
            )

        depth = 0
        end = None
        for inner in range(index, len(masked_lines)):
            directive = directive_pattern.search(masked_lines[inner])
            if directive:
                token = directive.group(1)
                if token in {"if", "ifdef", "ifndef"}:
                    depth += 1
                elif token == "endif":
                    depth -= 1
                    if depth == 0:
                        end = inner
                        break
        if end is None:
            continue
        guarded = "\n".join(masked_lines[index + 1 : end])
        if re.search(r"\bFN_TEST\s*\(", guarded) and re.search(
            r"\bEND_TEST\s*\(", guarded
        ):
            findings.append(
                Finding(
                    "candidate",
                    "RT-06",
                    str(path),
                    index + 1,
                    "__asterinas__ guard contains an entire FN_TEST; verify the guard cannot be narrower",
                )
            )
    return findings


def scan_shell_list(path: Path, source: str) -> list[Finding]:
    findings: list[Finding] = []
    block: list[tuple[int, str]] = []

    def finish() -> None:
        nonlocal block
        names = [entry for _, entry in block]
        expected = sorted(names)
        if len(names) > 1 and names != expected:
            first_mismatch = next(
                i for i, pair in enumerate(zip(names, expected)) if pair[0] != pair[1]
            )
            line, name = block[first_mismatch]
            findings.append(
                Finding(
                    "candidate",
                    "RT-07",
                    str(path),
                    line,
                    f"test command block is not alphabetical near {name!r}",
                )
            )
        block = []

    for number, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("./") and not stripped.endswith("&"):
            block.append((number, stripped.split()[0]))
        else:
            finish()
    finish()
    return findings


def scan_makefile_list(path: Path, source: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = source.splitlines()
    assignment = re.compile(
        r"^\s*([A-Za-z0-9_]*(?:TESTS|SUBDIRS|SCRIPTS))\s*[:+?]?=\s*\\\s*$"
    )
    i = 0
    while i < len(lines):
        match = assignment.match(lines[i])
        if not match:
            i += 1
            continue
        entries: list[tuple[int, str]] = []
        i += 1
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue
            continued = stripped.endswith("\\")
            value = stripped[:-1].strip() if continued else stripped
            if value and re.fullmatch(r"[^\s]+", value):
                entries.append((i + 1, value))
            if not continued:
                break
            i += 1
        names = [entry for _, entry in entries]
        expected = sorted(names)
        if len(names) > 1 and names != expected:
            first_mismatch = next(
                j for j, pair in enumerate(zip(names, expected)) if pair[0] != pair[1]
            )
            line, name = entries[first_mismatch]
            findings.append(
                Finding(
                    "candidate",
                    "RT-07",
                    str(path),
                    line,
                    f"{match.group(1)} list is not alphabetical near {name!r}",
                )
            )
        i += 1
    return findings


def files_from_paths(paths: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and (
                    child.suffix in C_SUFFIXES
                    or child.name == "Makefile"
                    or child.suffix == ".sh"
                ):
                    files.add(child)
        elif path.is_file():
            files.add(path)
        else:
            raise FileNotFoundError(path)
    return sorted(files)


def scan(path: Path) -> list[Finding]:
    source = path.read_text(encoding="utf-8")
    if path.suffix in C_SUFFIXES:
        return scan_c(path, source)
    if path.name == "Makefile":
        return scan_makefile_list(path, source)
    if path.suffix == ".sh":
        return scan_shell_list(path, source)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="files or directories to scan")
    parser.add_argument("--json", action="store_true", help="emit a JSON array")
    args = parser.parse_args()

    try:
        files = files_from_paths(args.paths)
    except FileNotFoundError as error:
        parser.error(f"path does not exist: {error}")

    findings = [finding for path in files for finding in scan(path)]
    if args.json:
        json.dump([asdict(finding) for finding in findings], sys.stdout, indent=2)
        print()
    else:
        for finding in findings:
            print(
                f"{finding.path}:{finding.line}: {finding.severity}: "
                f"{finding.rule}: {finding.message}"
            )
        if not findings:
            print("No mechanically detectable issues found.")

    return 1 if any(finding.severity == "violation" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
