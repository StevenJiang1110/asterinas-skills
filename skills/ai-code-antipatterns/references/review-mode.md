# Review mode

Review the entire user-specified scope for every pattern in the catalog. Use the candidate scanner first when applicable, then inspect the diff or files manually; several patterns require repository-wide searches or external-reference verification and cannot be recognized reliably by syntax.

Follow changed code far enough to understand its callers, invariants, and existing alternatives. For a Git diff, review added and materially modified code, while using unchanged code as context. Do not report pre-existing anti-patterns unless the user explicitly includes existing code in scope.

Write a Markdown report at the requested path, or `ai-antipattern-review.md` by default. Include:

- the exact scope;
- a short summary with finding counts by pattern;
- findings ordered by impact, each with pattern ID/name, source location, concrete evidence, why the false-positive explanation does not apply, and the appropriate correction;
- a clear “No verified anti-patterns found” result if the review is clean.

List every verified location. Repeated instances with the same mechanism may be grouped under one finding only if all locations are enumerated. Do not add a vibe-coding verdict; that belongs to judge mode.
