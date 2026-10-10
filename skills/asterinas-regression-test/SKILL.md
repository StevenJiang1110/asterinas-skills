---
name: asterinas-regression-test
description: Write, modify, or review Asterinas regression tests using the project's C test-macro conventions and Linux/Asterinas validation workflow. Use whenever work creates, changes, or reviews files under test/initramfs/src/regression, or changes scripts or Makefiles that register those regression tests. Do not use for conformance, benchmark, NixOS, or kernel unit tests unless regression-test files are also in scope.
---

# Asterinas Regression Tests

Apply this skill while writing, changing, or reviewing Asterinas regression
tests. Read [references/conventions.md](references/conventions.md) completely
before acting. Read [references/validation.md](references/validation.md) before
running or assessing validation.

## Workflow

1. Resolve the exact test scope from the request or diff. Inspect the affected
   C source, its local `Makefile`, the category's `run_test.sh`, and nearby tests
   before choosing structure or assertions.
2. Run the checker on every changed regression C/header file and every changed
   registration script or Makefile:

   ```bash
   python3 /root/.codex/skills/asterinas-regression-test/scripts/check_regression_tests.py <paths...>
   ```

   The checker emits both definite violations and review candidates. Inspect
   every result in context. Never turn a candidate into a review finding or a
   code change without confirming it manually.
3. Manually check the semantic rules that cannot be inferred reliably:
   failure-path cleanup, over-defensive branches, whether helpers hide the test
   body, whether a `CHECK_*` in `FN_TEST` is required by a child process, and
   whether an `__asterinas__` guard is as narrow as the actual behavioral
   difference.
4. When writing or modifying code, preserve the local test's scenario and make
   the smallest coherent change. Add the executable to every applicable test
   list in alphabetical order.
5. Format and validate as described in `references/validation.md`. A meaningful
   regression-test change is not complete until the affected behavior has run
   on both host Linux and Asterinas. If the environment prevents either run,
   report that limitation explicitly instead of claiming validation.

## Review behavior

Report concrete findings first, ordered by severity, with file and line. Tie
each finding to a rule ID from `references/conventions.md`; explain the observed
code and the smallest useful correction. Do not report mere checker output,
style preferences, or hypothetical risks.

For a clean review, state that no violations were found and list the Linux and
Asterinas validation actually observed or run. Do not claim that a test covers
a behavior merely because it builds or appears in `run_test.sh`.

## Editing behavior

Use `TEST_*` to make the operation and its observable result visible in the
test log. Keep orchestration and assertions in `FN_TEST`; extract only genuinely
reusable or low-level mechanical operations. Do not add recovery logic for an
assertion failure. Cleanup belongs on the expected successful path.

The regression framework itself is defined in
`test/initramfs/src/regression/common/test.h`. Re-read it if the macro interface
has changed; repository source overrides stale examples in this skill, while
the project conventions in the reference remain authoritative until the user
changes them.
