# Judge mode

Perform the same complete analysis as review mode, but classify each verified occurrence with `confidence: high`, `medium`, or `low`. Only high-confidence occurrences participate in the verdict. Candidates from the scanner never count until they have been inspected semantically.

Create a temporary findings JSON using this shape:

```json
{
  "scope": "the exact inspected scope",
  "findings": [
    {
      "pattern_id": "AP-DEFENSIVE",
      "confidence": "high",
      "path": "path/to/file.rs",
      "line": 42,
      "summary": "checked multiplication cannot overflow under the proven type bounds"
    }
  ]
}
```

One finding entry normally represents one independent source occurrence. A grouped entry may instead provide a `locations` array of `{ "path": ..., "line": ... }` objects. The scoring script deduplicates identical locations.

For `AP-SCOPE`, count a contiguous unrelated edit or one mechanical sweep as one occurrence, not one occurrence per changed line. This prevents whitespace churn or a broad automated rewrite from inflating the judgment threshold.

Run `scripts/judge_findings.py FINDINGS_JSON --mode MODE`. Supported calibrations are:

- `lenient`: at least one high-confidence occurrence;
- `balanced`: at least two distinct patterns, at least three high-confidence occurrences in total, and at least one repeated pattern;
- `conservative`: at least three distinct patterns, with at least two patterns repeated at independent source locations.

Use `conservative` when the user does not select a calibration. A repeated pattern means at least two independent source locations, not two comments about the same construct.

Write the requested Markdown report, or `ai-antipattern-judgment.md` by default. State the exact scope, calibration, high-confidence counts, deterministic script result, supporting findings, and material limitations. The only verdicts are:

- **Reasonable suspicion of unchecked vibe coding**
- **Insufficient evidence for that conclusion**

The verdict concerns the submitted code and apparent inspection quality. It is not a factual claim about which person or tool authored it. A lenient verdict should explicitly say that one occurrence is a weak signal and the selected calibration intentionally favors sensitivity over specificity.
