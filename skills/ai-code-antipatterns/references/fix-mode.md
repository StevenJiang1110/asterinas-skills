# Fix mode

Find all verified anti-patterns in the exact authorized scope, then repair them. Candidate scanning is only the first pass; inspect callers, invariants, repository facilities, documentation context, and external references before editing.

Prefer the smallest correction that removes the mechanism:

- verify, replace, or remove incorrect references;
- inline a wrapper only after confirming its callers and semantic role;
- remove defensive branches only after proving failure impossible on all supported targets;
- rewrite or delete comments so they record durable intent rather than syntax or patch history;
- reuse an existing facility only after confirming equivalent semantics and acceptable dependencies;
- translate upstream behavior into the local abstraction instead of preserving upstream internals.

Preserve observable behavior unless the anti-pattern itself introduced incorrect behavior. Do not bundle ordinary cleanup or unrelated defects into the fix. If a correct repair requires design judgment that the evidence does not resolve, leave it unchanged and report the decision instead of guessing.

After editing, rerun the anti-pattern review over the same scope and run the repository's narrowest relevant formatting, build, lint, or tests. Follow repository-local instructions for validation. Report the fixes, validation actually performed, and any verified findings that could not be safely repaired.
