#!/usr/bin/env python3
"""Find syntactic candidates for the AI code anti-pattern review skill.

The output deliberately contains candidates, not findings. Every candidate must
be verified against repository context and the pattern catalog by the caller.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


MAX_FILE_SIZE = 2 * 1024 * 1024
URL_RE = re.compile(r"https?://[^\s)>\]}]+")
HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@")
COMMENT_RE = re.compile(r"^\s*(?://[/!]?|#|/\*+|\*|<!--)")
DOC_COMMENT_RE = re.compile(r"^\s*(?:///|//!|/\*\*|\*)")
CONTEXT_RE = re.compile(
    r"\b(this\s+(?:pr|pull request|patch|change|task)|as\s+requested|"
    r"requested\s+in\s+(?:the\s+)?review|for\s+this\s+task)\b",
    re.IGNORECASE,
)
DEFENSIVE_RE = re.compile(
    r"(?:\.checked_(?:add|sub|mul|div|rem|neg|shl|shr|next_multiple_of)\s*\(|"
    r"\b(?:TryFrom|try_from|try_into)\b|\.try_reserve(?:_exact)?\s*\()"
)
DOC_RESTATEMENT_RE = re.compile(
    r"^\s*(?:///|//!|/\*\*|\*)\s*(?:returns?|gets?|sets?|creates?)\s+"
    r"(?:the|a|an|this)\b",
    re.IGNORECASE,
)
UPSTREAM_INTERNAL_RE = re.compile(
    r"\blinux\b.*(?:`[A-Za-z_][A-Za-z0-9_]*(?:\(\))?`|"
    r"[A-Za-z_][A-Za-z0-9_]*\(\)|implementation detail|internals?)",
    re.IGNORECASE,
)
RUST_FN_RE = re.compile(
    r"^\s*(?:(?:pub(?:\s*\([^)]*\))?|async|const|unsafe|extern\s+\"[^\"]+\")\s+)*"
    r"fn\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)


@dataclass(frozen=True)
class SourceLine:
    path: str
    line: int
    text: str


@dataclass(frozen=True)
class Candidate:
    pattern_id: str
    path: str
    line: int
    heuristic: str
    evidence: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce review candidates for AI-generated code anti-patterns."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--git-diff",
        metavar="RANGE",
        help="scan added lines from `git diff RANGE`",
    )
    source.add_argument(
        "--staged",
        action="store_true",
        help="scan added lines from the staged diff",
    )
    source.add_argument(
        "--unstaged",
        action="store_true",
        help="scan added lines from the unstaged worktree diff",
    )
    source.add_argument(
        "--diff-file",
        metavar="PATH",
        help="scan a unified diff file; use - for stdin",
    )
    source.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="scan the complete contents of explicit files or directories",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="repository root for Git commands and resolving diff paths (default: cwd)",
    )
    parser.add_argument("--output", help="write JSON output to this file instead of stdout")
    return parser.parse_args()


def run_git_diff(args: argparse.Namespace, root: Path) -> tuple[str, str]:
    command = ["git", "diff", "--unified=0", "--no-ext-diff"]
    if args.staged:
        command.append("--cached")
        description = "staged diff"
    elif args.unstaged:
        description = "unstaged worktree diff"
    else:
        command.append(args.git_diff)
        description = f"git diff {args.git_diff}"
    command.append("--")
    result = subprocess.run(
        command,
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout, description


def normalize_diff_path(raw: str) -> str | None:
    raw = raw.strip()
    if raw == "/dev/null":
        return None
    if raw.startswith("b/"):
        raw = raw[2:]
    return raw


def parse_diff(diff: str) -> list[SourceLine]:
    lines: list[SourceLine] = []
    current_path: str | None = None
    new_line: int | None = None

    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            current_path = normalize_diff_path(raw[4:].split("\t", 1)[0])
            new_line = None
            continue
        hunk = HUNK_RE.match(raw)
        if hunk:
            new_line = int(hunk.group(1))
            continue
        if current_path is None or new_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            lines.append(SourceLine(current_path, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith(" "):
            new_line += 1
        elif raw.startswith("-") or raw.startswith("\\"):
            continue
        else:
            new_line = None
    return lines


def looks_binary(data: bytes) -> bool:
    return b"\0" in data[:8192]


def read_text(path: Path) -> str | None:
    try:
        if not path.is_file() or path.stat().st_size > MAX_FILE_SIZE:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if looks_binary(data):
        return None
    return data.decode("utf-8", errors="replace")


def expand_files(paths: list[str], root: Path) -> tuple[list[SourceLine], dict[str, str]]:
    source_lines: list[SourceLine] = []
    texts: dict[str, str] = {}
    seen: set[Path] = set()

    for item in paths:
        candidate = Path(item)
        if not candidate.is_absolute():
            candidate = root / candidate
        expanded: Iterable[Path]
        if candidate.is_dir():
            expanded = (
                path
                for path in candidate.rglob("*")
                if ".git" not in path.parts
            )
        else:
            expanded = [candidate]

        for path in expanded:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = read_text(path)
            if text is None:
                continue
            try:
                display = str(path.resolve().relative_to(root.resolve()))
            except ValueError:
                display = str(path.resolve())
            texts[display] = text
            source_lines.extend(
                SourceLine(display, index, line)
                for index, line in enumerate(text.splitlines(), start=1)
            )
    return source_lines, texts


def load_touched_texts(lines: list[SourceLine], root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for relative in sorted({line.path for line in lines}):
        text = read_text(root / relative)
        if text is not None:
            texts[relative] = text
    return texts


def short_evidence(text: str) -> str:
    text = text.strip()
    return text if len(text) <= 240 else text[:237] + "..."


def line_candidates(lines: list[SourceLine]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for source in lines:
        text = source.text
        is_comment = COMMENT_RE.match(text) is not None

        if is_comment and CONTEXT_RE.search(text):
            candidates.append(
                Candidate("AP-CONTEXT", source.path, source.line, "patch-context phrase", short_evidence(text))
            )

        if is_comment:
            for url in URL_RE.findall(text):
                unstable = re.search(r"/(?:latest|main|master|HEAD)(?:/|$)", url, re.IGNORECASE)
                candidates.append(
                    Candidate(
                        "AP-REF",
                        source.path,
                        source.line,
                        "unstable reference revision" if unstable else "reference needs semantic verification",
                        short_evidence(url),
                    )
                )

        if not is_comment and DEFENSIVE_RE.search(text):
            candidates.append(
                Candidate("AP-DEFENSIVE", source.path, source.line, "fallible operation needs invariant analysis", short_evidence(text))
            )

        if DOC_COMMENT_RE.match(text) and DOC_RESTATEMENT_RE.search(text):
            candidates.append(
                Candidate("AP-DOC", source.path, source.line, "doc summary may restate declaration", short_evidence(text))
            )

        if is_comment and UPSTREAM_INTERNAL_RE.search(text):
            candidates.append(
                Candidate("AP-UPSTREAM", source.path, source.line, "comment mentions upstream internal shape", short_evidence(text))
            )
    return candidates


def scope_noise_candidates(diff: str) -> list[Candidate]:
    """Find hunks whose changes consist only of comments or whitespace."""

    candidates: list[Candidate] = []
    current_path: str | None = None
    new_line: int | None = None
    hunk_start: int | None = None
    changes: list[tuple[str, int, str]] = []

    def flush_hunk() -> None:
        if current_path is None or hunk_start is None or not changes:
            return
        if not all(not text.strip() or COMMENT_RE.match(text) for _, _, text in changes):
            return

        only_whitespace = all(not text.strip() for _, _, text in changes)
        added = [(line, text) for prefix, line, text in changes if prefix == "+"]
        line, evidence = added[0] if added else (hunk_start, changes[0][2])
        candidates.append(
            Candidate(
                "AP-SCOPE",
                current_path,
                line,
                (
                    "whitespace-only diff hunk needs comparison with the stated change goal"
                    if only_whitespace
                    else "comment/whitespace-only diff hunk needs comparison with the stated change goal"
                ),
                short_evidence(evidence) or "<blank line>",
            )
        )

    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            flush_hunk()
            changes = []
            current_path = normalize_diff_path(raw[4:].split("\t", 1)[0])
            new_line = None
            hunk_start = None
            continue

        hunk = HUNK_RE.match(raw)
        if hunk:
            flush_hunk()
            changes = []
            new_line = int(hunk.group(1))
            hunk_start = new_line
            continue

        if current_path is None or new_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            changes.append(("+", new_line, raw[1:]))
            new_line += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            changes.append(("-", new_line, raw[1:]))
        elif raw.startswith(" "):
            new_line += 1
        elif raw.startswith("\\"):
            continue
        else:
            flush_hunk()
            changes = []
            new_line = None
            hunk_start = None

    flush_hunk()
    return candidates


def rust_wrapper_candidates(
    texts: dict[str, str], scoped_lines: set[tuple[str, int]]
) -> list[Candidate]:
    candidates: list[Candidate] = []
    corpus = "\n".join(texts.values())

    for path, text in texts.items():
        if not path.endswith(".rs"):
            continue
        lines = text.splitlines()
        for index, line in enumerate(lines):
            match = RUST_FN_RE.match(line)
            if not match or (path, index + 1) not in scoped_lines:
                continue
            name = match.group(1)
            header_end = index
            while header_end < len(lines) and "{" not in lines[header_end]:
                if ";" in lines[header_end]:
                    break
                header_end += 1
            if header_end >= len(lines) or "{" not in lines[header_end]:
                continue

            depth = 0
            body_lines: list[str] = []
            end = header_end
            started = False
            while end < len(lines):
                current = lines[end]
                opens = current.count("{")
                closes = current.count("}")
                if opens:
                    started = True
                depth += opens - closes
                if end > header_end:
                    body_lines.append(current)
                if started and depth <= 0:
                    break
                end += 1
            if not started or depth != 0:
                continue

            meaningful = [
                item.strip()
                for item in body_lines
                if item.strip()
                and item.strip() not in {"}", "};"}
                and not COMMENT_RE.match(item)
            ]
            occurrences = len(re.findall(rf"\b{re.escape(name)}\b", corpus))
            if 0 < len(meaningful) <= 3 and occurrences <= 2:
                candidates.append(
                    Candidate(
                        "AP-WRAP",
                        path,
                        index + 1,
                        "short Rust function with at most one apparent caller in scanned text",
                        short_evidence(" ".join(lines[index : min(end + 1, index + 4)])),
                    )
                )
    return candidates


def deduplicate(candidates: list[Candidate]) -> list[Candidate]:
    unique = {
        (item.pattern_id, item.path, item.line, item.heuristic, item.evidence): item
        for item in candidates
    }
    return sorted(
        unique.values(),
        key=lambda item: (item.path, item.line, item.pattern_id, item.heuristic),
    )


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve()

    if args.files:
        lines, texts = expand_files(args.files, root)
        source = {"kind": "files", "value": args.files}
    else:
        if args.diff_file:
            if args.diff_file == "-":
                diff = sys.stdin.read()
            else:
                diff = Path(args.diff_file).read_text(encoding="utf-8")
            description = f"diff file {args.diff_file}"
        else:
            diff, description = run_git_diff(args, root)
        lines = parse_diff(diff)
        texts = load_touched_texts(lines, root)
        source = {"kind": "diff", "value": description}

    scoped = {(line.path, line.line) for line in lines}
    candidates = line_candidates(lines)
    if not args.files:
        candidates.extend(scope_noise_candidates(diff))
    candidates.extend(rust_wrapper_candidates(texts, scoped))
    candidates = deduplicate(candidates)

    result = {
        "schema_version": 1,
        "source": source,
        "candidate_count": len(candidates),
        "candidates": [asdict(item) for item in candidates],
        "notes": [
            "These are heuristic candidates, not verified findings.",
            "AP-REINVENT, most semantic AP-UPSTREAM cases, and AP-SCOPE cases mixed with code changes require manual inspection.",
            "An AP-SCOPE comment/whitespace-only hunk is reportable only after comparison with the stated change goal and formatter requirements.",
            "Absence of candidates does not establish absence of anti-patterns.",
        ],
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
