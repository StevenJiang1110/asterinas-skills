---
name: asterinas-validate-workflow
description: Asterinas post-code-change validation and commit hygiene guide. Use whenever Codex works in /root/asterinas after editing code and needs validation. Also use for build, format, lint, verify, tests, regression, conformance, gVisor/gvisor/GVisor/gVsior, initramfs, pre-commit, amend, fixup, autosquash, commit atomicity, force push, CI/PR/issue investigation, GitHub review replies/resolution, or prompts such as 改完代码, 修改代码后, 写完代码, 写完之后, 修复后验证, 跑一下验证, 验证, 运行测试, 回归测试, 提交前检查, 编译检查, make kernel, make check, make run_kernel, make initramfs, failed CI, after code changes, post-change validation, or run tests.
---

# Asterinas Validate Workflow

Use the repository Makefile as the validation interface. Do not call `cargo` directly for formatting, linting, checks, or building unless the user explicitly asks for low-level investigation and the Makefile path is insufficient.

## Command Rules

- Use `make format`, not `cargo format`.
- Use `make check`, not `cargo check`, for lint and full checks.
- For quick post-edit compile validation, prefer `make format` followed by `make kernel`.
- Treat `make check` as expensive; normally reserve it for pre-commit or when the user explicitly asks for full lint/check validation.
- Anything under `test/initramfs` is built by Nix through the project Makefile. Do not compile those tests directly with `gcc`, `clang`, `make` in a subdirectory, or ad hoc local commands.
- Assume the normal development environment is the project Docker container.

## Validation Decision

Choose the narrowest workflow that proves the change:

- **Formatting only:** run `make format`.
- **Quick compile check after code edits:** run `make format` then `make kernel`.
- **Regression test source or kernel behavior change:** build test binaries with `make initramfs ENABLE_REGRESSION_TEST=true`, locate the relevant built binary under `test/initramfs/build/initramfs/test/**`, run that binary on host Linux when meaningful, then run `make run_kernel AUTO_TEST=regression`.
- **CI gVisor failure reproduction:** do not run the full gVisor suite by default. Identify the failed gVisor binary or binaries from CI logs, temporarily package only those tests, and run the gVisor conformance command.
- **Before `git commit`:** run `make format`, `make check`, and `make run_kernel AUTO_TEST=regression`.
- **CI/PR/issue investigation:** use `gh` for remote GitHub CI, PR, and issue state when needed.

## Regression Tests

Regression tests live in `test/initramfs/src/regression`.

1. Build them through Nix/Makefile:

   ```bash
   make initramfs ENABLE_REGRESSION_TEST=true
   ```

2. Locate and verify the affected compiled test on host Linux from:

   ```text
   test/initramfs/build/initramfs/test/**
   ```

   The output path mirrors the regression source subdirectory. For example,
   `test/initramfs/src/regression/network/msg_peek.c` is built as
   `test/initramfs/build/initramfs/test/network/msg_peek`. A deeper source path
   may produce a deeper output path. If `make initramfs` prints a Nix store path
   or the top-level `test/initramfs/build/initramfs/test` directory does not
   contain the binary directly, search below it before deciding host-side
   execution is unavailable:

   ```bash
   find test/initramfs/build/initramfs/test -type f -perm -111 -name '<test-name>'
   ```

   Run the built binary directly from its actual path when the test is meaningful
   on host Linux. Do not compile it manually.

3. Verify on Asterinas:

   ```bash
   make run_kernel AUTO_TEST=regression
   ```

Regression fixes should normally include or update a regression test that captures the user-visible behavior.

## Conformance Tests

Conformance suites live in `test/initramfs/src/conformance`. They are open-source system-compatibility test suites packaged into the Asterinas initramfs flow.

Run conformance tests through the repository Makefile, not by locally building inside the suite directory. Select suite-specific workflows from the repository Makefiles and CI wiring before editing commands.

## gVisor Tests

gVisor tests live in `test/initramfs/src/conformance/gvisor`.

- Full gVisor runs are expensive. When reproducing a local CI failure, do not run
  the full suite unless the user explicitly asks for it or the failure does not
  identify any test binary. Run only the failed gVisor test binary or binaries
  from the CI log, such as `open_test`, `socket_unix_stream_test`, or
  `xattr_test`.

- A full run uses:

  ```bash
  make run_kernel AUTO_TEST=conformance CONFORMANCE_TEST_SUITE=gvisor
  ```

- To run only specific gVisor tests, temporarily edit
  `test/initramfs/src/conformance/gvisor/Makefile` so the `TESTS ?=` list
  contains only the failed binaries, then run the same conformance command. The
  gVisor runner loops over the `*_test` binaries actually packaged under
  `/opt/gvisor/tests`, so reducing the packaged `TESTS` list is the reliable
  local narrowing mechanism.

- Do not try to select gVisor tests by passing environment variables to
  `make run_kernel`, `make kernel`, or `make initramfs` (for example
  `TESTS=...`, `GVISOR_TESTS=...`, `GTEST_FILTER=...`, or similar). The gVisor
  Makefile is consumed inside the Nix initramfs build, and those top-level
  command-line environment overrides are not a reliable way to change which
  binaries are packaged or run.

## Git Discipline

When the user asks to amend, do not blindly amend the current `HEAD`.
First map each local change to the commit that should have introduced it.
Amend or fix up one or more earliest appropriate commits so every commit remains
atomic and complete. A later commit must not repair, rename, revert, or clean up
something that belongs in an earlier commit. After rewriting, inspect the
per-commit diff/log to ensure the stack has no avoidable "introduce then fix"
history.

Before creating a commit, validate with:

```bash
make format
make check
make run_kernel AUTO_TEST=regression
```

Keep commits atomic and complete. If remote CI, PR, or issue information is needed, use `gh` rather than guessing.
