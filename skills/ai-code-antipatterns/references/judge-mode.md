# Judge mode

Perform the same complete analysis as review mode, but classify each finding with `confidence: high`, `medium`, or `low`. Only high-confidence occurrences participate in the verdict. Candidates from the scanner never count until they have been inspected semantically.

Use the fixed strong/weak assignments in [patterns.md](patterns.md). Signal strength measures judgment relevance, not impact or confidence. In particular, `AP-WRAP` is strong only after establishing that the helper adds no domain concept, policy, invariant, ownership boundary, or useful operation; shortness and a single caller are insufficient.

## Count independent occurrences

Count independent problematic decisions, not lines or source locations. Give each occurrence a stable `occurrence_id` within the inspected scope:

- One mechanical sweep of unrelated edits is one `AP-SCOPE` occurrence.
- One incorrect reference copied into several places is one `AP-REF` occurrence.
- One construct matching several patterns counts once. Choose one primary `pattern_id`, preferring a verified strong pattern when applicable, and list other labels in `related_pattern_ids` for explanation only.
- Separate locations count independently only when they represent distinct problematic decisions. A grouped `locations` array documents an occurrence's extent; it does not multiply its count.

Create a temporary findings JSON using this shape:

```json
{
  "scope": "the exact inspected scope",
  "findings": [
    {
      "occurrence_id": "unreachable-size-check",
      "pattern_id": "AP-DEFENSIVE",
      "confidence": "high",
      "path": "path/to/file.rs",
      "line": 42,
      "summary": "checked multiplication cannot overflow under the proven type bounds"
    }
  ]
}
```

An entry may provide a `locations` array of `{ "path": ..., "line": ... }` instead of `path` and `line`. Repeated entries with the same occurrence ID and primary pattern count once. Do not assign different IDs to copies or overlapping labels of the same problem. The script requires an ID and concrete locations for each high-confidence entry and rejects conflicting primary patterns for an ID.

## Deterministic thresholds

Run `scripts/judge_findings.py FINDINGS_JSON --mode MODE`. Each row passes if either combination is satisfied. All counts below refer to independent, high-confidence occurrences and their primary pattern categories.

| Calibration | Strong-signal combination | Mixed/supporting combination |
| --- | --- | --- |
| `lenient` | At least 1 strong occurrence | At least 2 weak occurrences covering at least 2 weak patterns |
| `balanced` | At least 2 strong occurrences covering at least 2 strong patterns | At least 1 strong and 2 weak occurrences, covering at least 3 patterns overall |
| `conservative` | At least 3 strong occurrences covering at least 2 strong patterns | At least 2 strong and 2 weak occurrences, covering at least 3 patterns overall |

Use `conservative` when the user does not select a calibration. Weak signals alone never trigger balanced or conservative, regardless of their number or variety. They remain reportable quality findings. These thresholds are policy choices for sensitivity and specificity, not statistical probabilities.

Write the requested Markdown report, or `ai-antipattern-judgment.md` by default. State the exact scope, calibration, strong and weak counts and pattern coverage, deterministic script result, supporting findings, and material limitations. Explain the independent-occurrence grouping when several locations or labels describe one problem. The only verdicts are:

- **Reasonable suspicion of unchecked vibe coding**
- **Insufficient evidence for that conclusion**

The verdict concerns the submitted code and apparent inspection quality. It is not a factual claim about which person or tool authored it. A lenient verdict should explicitly state that the calibration favors sensitivity over specificity and may pass with one strong occurrence or corroborating weak signals alone.
