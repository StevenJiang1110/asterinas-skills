# Regression-Test Validation

Run commands from the Asterinas repository root and inside the project's
development environment. Use the repository's Makefile entry points rather
than invoking the category Makefiles directly.

## 1. Run the static convention checker

Pass all changed regression sources and registration files explicitly:

```bash
python3 /root/.codex/skills/asterinas-regression-test/scripts/check_regression_tests.py \
  test/initramfs/src/regression/<category>/<test>.c \
  test/initramfs/src/regression/<category>/run_test.sh
```

Resolve every definite violation. Inspect candidates manually; an allowed fork
child `CHECK_WITH`, an intentionally grouped test list, or an irreducible
platform guard may be valid.

## 2. Format the regression sources

For an editing task, run:

```bash
make format
```

Review the resulting diff and retain only formatting caused by the requested
change.

## 3. Build and run on host Linux

Build the Linux variant explicitly:

```bash
make initramfs ENABLE_REGRESSION_TEST=true REGRESSION_TEST_PLATFORM=linux
```

The explicit platform is mandatory. Without it, `test/initramfs/Makefile`
defaults to `asterinas`, so `__asterinas__` is defined and the resulting binary
does not validate the Linux branch.

Locate the affected executable:

```bash
find test/initramfs/build/initramfs/test -type f -perm -111 -name '<test-name>'
```

Run it from its output directory so relative paths behave as they do in the
suite:

```bash
cd test/initramfs/build/initramfs/test/<category>
./<test-name>
```

If the scenario is coordinated by `run_test.sh` (for example, a client/server
pair), run the smallest applicable script or command sequence rather than an
isolated binary that cannot exercise the scenario. Account for privileges,
devices, and host state before running a test, but do not silently substitute a
build-only check.

## 4. Build and run on Asterinas

Run the regression suite in Asterinas:

```bash
make run_kernel AUTO_TEST=regression
```

This switches the regression build back to its default `asterinas` platform,
includes it in the initramfs, boots Asterinas, and executes
`/test/run_regression_test.sh`. Success requires the command to exit
successfully and the log to report `All regression tests passed.`

## 5. Report exact evidence

State separately:

- static checker result;
- formatting result;
- Linux build and the exact binary or script executed;
- Asterinas regression result.

If either runtime cannot be executed, say which step was not run and why. Do
not describe compilation alone as a passing regression test.
