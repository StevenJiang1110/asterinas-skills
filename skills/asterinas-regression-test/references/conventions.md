# Asterinas Regression-Test Conventions

These rules apply to C regression tests under
`test/initramfs/src/regression` and to the scripts or Makefiles that register
them. The examples are evidence from earlier Asterinas reviews, not templates
to copy mechanically.

## RT-01: Put the invocation in the assertion macro

The first argument of `TEST`, `TEST_SUCC`, `TEST_ERRNO`, `TEST_RES`, `CHECK`, or
`CHECK_WITH` must be the syscall, library call, or function call being tested.
Do not call first, store the result, and then pass a bare variable to the macro.

Prefer:

```c
int fd = TEST_SUCC(open(path, O_RDONLY));
TEST_RES(read(fd, buf, sizeof(buf)), _ret == expected_len);
```

Avoid:

```c
ssize_t nread = read(fd, buf, sizeof(buf));
TEST_RES(nread, _ret == expected_len);
```

This keeps the diagnostic attached to the operation it describes. Historical
case: [`TEST_RES(map_size, ...)` and similar pre-stored values in PR
#3925](https://github.com/asterinas/asterinas/pull/3925#discussion_r4118877574).

## RT-02: Do not add defensive failure paths

Tests describe a path that is expected to succeed. Once `TEST_*` has asserted a
required result, continue under that expectation. Do not immediately recheck
the saved result, add `goto out`/`goto destroy`, or build recovery paths solely
to clean up after an assertion failure.

Perform resource cleanup on the normal successful path. The framework records
`TEST_*` failures; a failed test does not need production-style rollback or
best-effort cleanup. This convention does not excuse missing normal-path
cleanup, nor does it forbid control flow that is itself the behavior under
test.

Historical case: [redundant result checks and manual cleanup after
`TEST_RES`](https://github.com/asterinas/asterinas/pull/3925#discussion_r4118852669).

## RT-03: Match macros to their execution context

- Inside `FN_SETUP`, use only `CHECK` or `CHECK_WITH`. Setup failure is fatal;
  later test functions cannot run with invalid fixtures.
- Inside `FN_TEST`, prefer `TEST`, `TEST_SUCC`, `TEST_ERRNO`, or `TEST_RES`.
  They print the exercised call and result and contribute to the test summary.
- Use `CHECK*` inside `FN_TEST` only where `TEST_*` cannot correctly report to
  the parent test context. The standard example is the child branch after
  `fork()`: the child uses `CHECK_WITH`, exits, and the parent validates the
  child through `TEST_RES(waitpid(...), ...)`.
- Do not use `TEST_*` from an ordinary helper or outside `FN_TEST`; its counters
  are local to the generated test function.

Historical case: [`CHECK_WITH` used for ordinary work at the start of an
`FN_TEST`](https://github.com/asterinas/asterinas/pull/3572#discussion_r3557939784).
Canonical exception: `semop_is_interrupted_by_signal` in
`test/initramfs/src/regression/ipc/sem/sem.c`, where the fork child uses
`CHECK_WITH` and the parent uses `TEST_*`.

## RT-04: Keep the test body in FN_TEST

Keep scenario orchestration, operations under test, and assertions in
`FN_TEST`. Do not move a one-use sequence into a helper merely to make the test
function shorter: the helper is then limited to silent/fatal `CHECK_*`, hiding
the useful per-operation `TEST_*` output.

Helpers are appropriate for genuinely reused logic and low-level mechanical
work that is not itself the behavior being asserted. Prefer returning data to
`FN_TEST` so the visible assertion remains there.

Historical cases: [netlink receive helpers that should be inlined so the test
can use `TEST_RES`/`TEST_SUCC`](https://github.com/StevenJiang1110/asterinas/pull/73#discussion_r3911574814)
and [a simplified DRM version test expressed directly with
`TEST_RES`](https://github.com/asterinas/asterinas/pull/3925#discussion_r4091700225).

## RT-05: Run on both host Linux and Asterinas

Regression tests are cross-kernel tests. Build and execute the affected test
with `REGRESSION_TEST_PLATFORM=linux` on the host, then build and execute the
regression suite on Asterinas. Merely using the default initramfs build is not a
Linux validation: its default platform is `asterinas` and defines
`__asterinas__`.

Follow [validation.md](validation.md) for exact commands. Historical case: [a
network regression was accepted only after its actual bind/connect/send/recv
path passed on both host Linux and Asterinas](https://github.com/StevenJiang1110/asterinas/pull/72#discussion_r3748245223).

## RT-06: Isolate real platform differences narrowly

A case may differ between Linux and Asterinas only when the kernels genuinely
have different observable behavior. Use `#ifdef __asterinas__` for the smallest
different expression or statement sequence.

Immediately above the directive, add a comment that explains the semantic
reason for the difference. Do not merely restate which platform executes the
branch. Keep shared setup, operations, and assertions outside the guard. Treat
a guard around an entire `FN_TEST` as suspicious and repeatedly verify that no
smaller scope can express the difference.

Historical cases: [the explanatory comment belongs above
`#ifdef __asterinas__`](https://github.com/asterinas/asterinas/pull/3843#discussion_r4045018327)
and [minor kernel discrepancies should use the harness-provided
`__asterinas__` macro](https://github.com/asterinas/asterinas/pull/3699#discussion_r4060729232).

## RT-07: Keep test lists alphabetical

Every list of regression executables or categories in a script or Makefile must
be alphabetical within its logical group. Preserve deliberate groups, such as
paired client/server setup or subsystem sections; sort entries inside each
group. Check every registration site affected by a new, renamed, moved, or
removed test.

Historical case: [`gem_create_dumb_buffer` had to move before
`get_info`](https://github.com/asterinas/asterinas/pull/3925#discussion_r4110715688)
in `test/initramfs/src/regression/device/run_test.sh`.
