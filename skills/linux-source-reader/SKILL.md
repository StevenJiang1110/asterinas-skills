---
name: linux-source-reader
description: Locate, fetch, navigate, and explain Linux kernel source code. Use for questions about Linux kernel implementations, call paths, data structures, subsystems, Kconfig or Makefile wiring, architecture-specific behavior, and source-history context; do not use for ordinary userspace Linux administration unless kernel source inspection is needed.
---

# Linux Source Reader

Resolve the source tree before inspecting code:

```bash
resolver="${CODEX_HOME:-/root/.codex}/skills/linux-source-reader/scripts/resolve-linux-source.sh"
linux_root="$("$resolver")"
```

The `/root/.codex` fallback matches this installation location. The script applies this order:

1. Use the current directory when it is a Linux source root, or its Git worktree root when the current directory is inside one.
2. Otherwise use `/opt/linux` when it is a valid Linux source tree.
3. Otherwise clone Torvalds' Linux repository at tag `v7.1` into `/opt/linux`, then return that path.

Treat the path printed to stdout as the source root. Diagnostics go to stderr. Do not reimplement this discovery or clone flow in ad hoc shell commands.

## Read The Source

- Establish the checked-out version with `git -C "$linux_root" describe --always --dirty` and the top-level `Makefile` version fields. State the version when it affects the answer.
- Prefer `rg` for symbols and text. Use `git -C "$linux_root" grep`, `git log`, and `git blame` when repository history or tracked-file semantics matter.
- Trace behavior from declarations and registrations to implementations and callers. Include relevant Kconfig, Makefile, linker, device-tree, or architecture selection when those gates determine whether code is built or reached.
- Distinguish generic kernel code from architecture-, configuration-, and version-specific behavior. Do not present one implementation as universal without checking those gates.
- Read enough surrounding code to account for locking, lifetime, ownership, error paths, and execution context when they affect the explanation.
- Ground conclusions in the resolved tree. In the final response, cite source paths with line numbers and separate verified behavior from inference.

## Resolver Options

Run `scripts/resolve-linux-source.sh --help` for all options. The defaults implement the required workflow. `--target`, `--ref`, and `--repo` exist for controlled testing or when the user explicitly requests another checkout; `--no-clone` performs discovery without network or filesystem mutation.

Never replace, delete, or overwrite a non-Linux path already present at the target. Report the conflict and ask the user how to proceed.
