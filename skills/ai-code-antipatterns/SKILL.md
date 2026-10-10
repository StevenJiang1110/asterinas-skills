---
name: ai-code-antipatterns
description: Review, judge, or fix code for recurring AI-generated anti-patterns and evidence of unchecked vibe coding. Use when the user explicitly requests an AI-code anti-pattern audit, a vibe-coding judgment, or fixes for these patterns; do not replace an ordinary correctness or security review with this skill.
---

# AI Code Anti-patterns

Use one of three modes:

- **review**: find every verified anti-pattern in the requested code scope and write a Markdown report.
- **judge**: evaluate whether the verified anti-patterns justify reasonable suspicion of unchecked vibe coding and write a Markdown judgment.
- **fix**: find and repair verified anti-patterns within the authorized code scope.

If the requested mode is ambiguous, ask which mode to use.

## Scope is mandatory

Identify the exact code scope before inspecting or changing code. A scope may be a Git range, one or more commits, staged or unstaged changes, a PR, a supplied diff, or named files/directories. Never assume that the scope is the current branch or its diff. If the user has not specified the scope, ask one concise question and stop.

Record the resolved scope in review and judge reports. For fix mode, treat it as the write boundary as well as the inspection boundary. If a sound fix requires changing a file outside that boundary, explain why and ask before expanding it.

## Shared evidence rules

Read [references/patterns.md](references/patterns.md) completely before analyzing code.
That file is the skill's fixed, authoritative pattern catalog. Never ask the user to
provide or restate the patterns. Change the catalog only when the user explicitly
asks to evolve the skill itself.

Run `scripts/scan_candidates.py` when the scope can be expressed as a Git diff, diff file, or file list. Its output is a search aid, not a list of findings. Inspect all candidates in context and manually check patterns the script cannot detect.

A reportable finding must:

1. match a defined pattern;
2. identify concrete source locations;
3. explain the relevant caller, type, invariant, stated change goal, existing repository facility, permanent documentation context, or upstream semantics;
4. survive a plausible false-positive check from the pattern reference.

Use `confidence: high` only after that verification. Do not report candidate matches as findings merely because they contain `checked_*`, a short function, a URL, a verbose comment, or an added blank line.

Exclude ordinary correctness bugs, naming preferences, missing tests, generic duplication, and debatable scope preferences unless they concretely instantiate one of the defined AI-skewed patterns. Do not claim that the author used AI. Even in judge mode, state only whether the code provides reasonable grounds for suspicion that it was produced or accepted without serious inspection.

When a finding depends on an external reference, open the target and verify the claimed version, symbol, lines, and semantics. When it depends on repository context, search for callers and existing equivalent facilities rather than reasoning from the changed file alone.

For `AP-SCOPE`, first establish the intended change from the user's request, PR title and description, linked issue, or commit messages. If the goal is unavailable or ambiguous, do not turn apparent diff noise into a high-confidence finding.

## Mode routing

- For **review**, read and follow [references/review-mode.md](references/review-mode.md).
- For **judge**, read and follow [references/judge-mode.md](references/judge-mode.md). Use `scripts/judge_findings.py` for the final threshold calculation.
- For **fix**, read and follow [references/fix-mode.md](references/fix-mode.md).

If no report path is provided, review writes `ai-antipattern-review.md` and judge writes `ai-antipattern-judgment.md` in the current working directory. If that path already exists, do not overwrite it without user direction.
