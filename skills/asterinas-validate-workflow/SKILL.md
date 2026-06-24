---
name: asterinas-validate-workflow
description: Asterinas project post-code-change validation and test workflow guide. Use whenever Codex works in /root/asterinas and has edited, implemented, fixed, refactored, or generated code and needs the appropriate after-change validation flow, even if the user did not explicitly ask to run tests. Also use for build, format, lint, verify, test, regression tests, conformance tests, gVisor tests, initramfs changes, pre-commit checks, CI/PR/issue inspection with gh, or Chinese/English prompts such as 改完代码, 修改代码后, 写完代码, 修复后验证, 跑一下验证, 验证, 运行测试, 回归测试, 提交前检查, 编译检查, after editing code, after code changes, post-change validation, run tests, gVisor, conformance, regression, initramfs, make kernel, make check, make run_kernel, or make initramfs.
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
- **Regression test source or kernel behavior change:** build test binaries with `make initramfs ENABLE_REGRESSION_TEST=true`, run the relevant built binary on host Linux from `test/initramfs/build/initramfs/test`, then run `make run_kernel AUTO_TEST=regression`.
- **Before `git commit`:** run `make format`, `make check`, and `make run_kernel AUTO_TEST=regression`.
- **CI/PR/issue investigation:** use `gh` for remote GitHub CI, PR, and issue state when needed.

## Regression Tests

Regression tests live in `test/initramfs/src/regression`.

1. Build them through Nix/Makefile:

   ```bash
   make initramfs ENABLE_REGRESSION_TEST=true
   ```

2. Verify the affected compiled test on host Linux from:

   ```text
   test/initramfs/build/initramfs/test
   ```

   Run the built binary directly from that directory or path. Do not compile it manually.

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

- Full gVisor runs are expensive and usually belong in CI or targeted failure reproduction:

  ```bash
  make run_kernel AUTO_TEST=conformance CONFORMANCE_TEST_SUITE=gvisor
  ```

- To run only a specific gVisor test, edit `test/initramfs/src/conformance/gvisor/Makefile` and comment out unneeded tests, then run the same conformance command.
- Do not try to override gVisor Makefile variables by passing environment variables on the command line; that Makefile is consumed inside the Nix build, so direct environment overrides are not reliable.

## Git Discipline

Before creating a commit, validate with:

```bash
make format
make check
make run_kernel AUTO_TEST=regression
```

Keep commits atomic and complete. If remote CI, PR, or issue information is needed, use `gh` rather than guessing.
