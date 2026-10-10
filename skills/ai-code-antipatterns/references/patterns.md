# Pattern catalog

The catalog is intentionally narrow. A finding must show the stated mechanism, not merely resemble a keyword or code shape.

## AP-REF: Unverified references

AI-generated code often supplies a reference that looks precise but was not checked. The URL may point to unrelated code, use an unstable revision, contain a fabricated anchor, or fail to support the accompanying semantic claim.

High-confidence evidence requires opening the target and demonstrating the mismatch. A stale link caused by later upstream movement is not enough unless it was already incorrect or unstable when introduced.

Case: In [Asterinas PR #3365](https://github.com/asterinas/asterinas/pull/3365#discussion_r3636043813), a file-capability reference pointed to unrelated Linux code. A subsequent `latest` URL [again pointed to the wrong location](https://github.com/asterinas/asterinas/pull/3365#discussion_r3680527259).

## AP-WRAP: Trivial one-off wrappers

The code extracts a short expression into a helper used only once, but the helper establishes no stable concept, policy, invariant, ownership boundary, or reusable operation. Understanding the caller now requires an unnecessary jump.

Line count alone is not evidence. A one-line helper may be valuable when it names a domain concept, centralizes unsafe or fallible behavior, enforces an invariant, or is expected to gain real callers immediately.

Case: In [Asterinas PR #3888](https://github.com/asterinas/asterinas/pull/3888#discussion_r4196009561), `get_standard_property` performed two map lookups, had one caller, and added no semantic boundary. The review requested inlining it.

## AP-DEFENSIVE: Defensive code that ignores proven invariants

The code mechanically uses fallible arithmetic, checked conversions, redundant validation, unnecessary cleanup, or propagated errors even though nearby types and established invariants make the failure impossible. This fabricates error semantics and obscures the boundaries that are actually attacker- or user-controlled.

Do not flag a check until the impossibility has been proved for every supported architecture and input path. Checks at trust boundaries, checks preserving API contracts, and cheap assertions documenting real invariants are not findings.

Case: In [Asterinas PR #3925](https://github.com/asterinas/asterinas/pull/3925#discussion_r4110704071), `pitch` and `height` were both `u32` values converted to `usize` on a 64-bit-only OS, so their multiplication could not overflow. The `checked_mul` branch was unreachable.

## AP-DOC: Documentation that restates syntax instead of intent

Comments or docs merely paraphrase a field name, function name, return type, lock type, or ordinary language rule. Other variants are generated mini-tutorials, repeated boilerplate on adjacent items, and prose whose meaning remains unclear despite its length.

Do not flag concise API summaries that are required by public-documentation conventions or that help navigation. The key question is whether the text tells a maintainer anything not already apparent from the declaration.

Case: In [Asterinas PR #3699](https://github.com/asterinas/asterinas/pull/3699#discussion_r4068179795), a method returning `&Mutex<VhostRuntimeState<_>>` was documented as returning runtime state protected by a mutex. The type already conveyed that fact.

## AP-CONTEXT: Patch or conversation context leaked into permanent code

Permanent source text speaks as if it were replying to the current prompt, review, or patch. Typical phrases include “this PR”, “as requested”, “in this change”, or “for this task”. After merge, the comment no longer describes the code without historical context.

References to a specific PR are legitimate when the history itself is materially relevant and linked deliberately. Do not flag issue/PR references that document compatibility history or the origin of a workaround.

Case: In [Asterinas PR #3365](https://github.com/asterinas/asterinas/pull/3365#discussion_r3680498478), a source comment said that generic zero-length `getxattr` behavior was “outside this PR”. It was replaced with a TODO describing the concrete unsupported behavior.

## AP-REINVENT: Locally polished reimplementation of existing facilities

The new code is complete and plausible in isolation but recreates an equivalent helper, abstraction, test double, constant, or validation rule already available in the repository. This pattern reflects local prompt completion without repository-level awareness.

Generic duplication is not enough. Verify that the existing facility has the same semantics and is usable or can be made usable without creating a worse dependency or abstraction boundary.

Case: In [Asterinas PR #3699](https://github.com/asterinas/asterinas/pull/3699#discussion_r4035117307), `validate_owner_range` recreated the `is_userspace_vaddr_range` check already present in `vmar/mod.rs`. In [PR #3686](https://github.com/asterinas/asterinas/pull/3686#discussion_r3726376733), a custom `DummyFile` duplicated the role an existing `EpollFile` could serve in a test.

## AP-UPSTREAM: Copying upstream internals instead of upstream behavior

The implementation mirrors an upstream function split, name, temporary, or call sequence without checking whether that internal structure fits the local architecture. The goal is compatibility with observable semantics, not structural similarity to one upstream revision.

Do not flag intentional structural alignment that is justified by future synchronization, a shared ABI, or a local design that genuinely matches upstream.

Case: In [Asterinas PR #3365](https://github.com/asterinas/asterinas/pull/3365#discussion_r3628791883), the code performed `get_xattr` before `remove_xattr` to mirror Linux's killpriv split. Asterinas's `remove_xattr` already handled absence, so the copied preflight step was redundant.

## AP-SCOPE: Unrelated edits bundled into the change

The patch performs opportunistic cleanup outside its stated goal while changing nearby code. Common forms include altering unrelated comments, adding or removing blank lines, renaming unaffected locals, or reformatting logic that the requested behavior does not touch. These changes create review noise and often indicate that a generated patch was accepted without checking every hunk against the requested task.

High-confidence evidence requires a concrete statement of the intended change and a demonstration that the suspicious edit is not needed to implement, test, document, generate, or format that change. Do not flag prerequisite refactoring, required call-site updates, generated-file changes, repository-mandated formatter output, tests or documentation for the changed behavior, or an explicitly requested cleanup. Mere surprise about a hunk is not enough.

Treat one contiguous edit or one mechanical sweep as one occurrence even if it changes many lines. Separate locations count independently only when each represents a distinct unrelated editing decision.

Case: [Asterinas PR #3780](https://github.com/asterinas/asterinas/pull/3780) added lifecycle-aware host-process support for binding `virtiofsd` to QEMU. An early revision also inserted an extra blank line into existing `Bundle` code; [the review identified that edit as unrelated and requested its removal](https://github.com/asterinas/asterinas/pull/3780#discussion_r4013728678).
