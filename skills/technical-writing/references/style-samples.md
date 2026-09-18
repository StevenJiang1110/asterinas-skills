# Style evidence and calibration

The account is `StevenJiang1110` (Jianfeng Jiang).
These are the initial calibration examples, retained as a compact guide by deliverable.
The broader year-long inventory and revised conclusions are in [annual-analysis.md](annual-analysis.md).
Issue #2294 predates the annual window and remains a supplementary example, not part of its 18-issue count.
The notes describe writing choices, not technical rules to enforce in unrelated work.
Live documents can change; use the links for closer calibration when needed.

## Explicit feedback from the user

The user rejected an initial bitflags migration issue as lacking his personal style.
That draft contained several tables, nested migration sections, an exhaustive API comparison, and a formal acceptance checklist.
He asked for the rewrite to learn from his existing issues.
The subsequent skill request extends this preference to issues, PR descriptions, design proposals, and PR comments.
The rewritten bitflags draft was not explicitly approved; treat it as an attempted application, not a canonical writing sample.

The useful correction is to favor a developer's explanatory argument over an exhaustive migration report.
It is not “always be short”, “never use tables”, or “all issues must have the same headings”.

## Issues

### Dependency migration: issue #3132

[The kernel cannot be built due to core2 is yanked](https://github.com/asterinas/asterinas/issues/3132)

Opens with the immediate dependency problem and its CI consequence.
Distinguishes direct uses from an indirect dependency in a short numbered list.
Explains the straightforward replacement first, then the upstream-dependent case and fallback.
No formal acceptance criteria or validation framework is needed to convey the proposal.
Useful for a library upgrade or narrowly scoped infrastructure issue.

### Small design improvement: issue #2294

[Support the generic syscall table for Asterinas](https://github.com/asterinas/asterinas/issues/2294)

Starts from almost-identical architecture tables, explains why Linux has a shared table,
and makes a personal recommendation grounded in duplication and future reuse.
Ends with the essential API requirement, without prescribing implementation internals.
Useful for improvements that need motivation but not a full design document.

### Substantial design: issue #3684

[Introducing a Unified Routing Table for Asterinas](https://github.com/asterinas/asterinas/issues/3684)

Uses motivation and current-state sections, then explains RouteEntry, RouteTable, and RouteManager from bottom to top.
Uses concrete loopback addresses and route lookups to explain selection behavior.
Discusses lifetime and architecture choices where they affect the design.
Ends with a staged plan and explains why combining all netlink details into the first PR would be unwieldy.
Useful evidence that long, structured writing and code sketches are appropriate when the design needs them.

## PR descriptions

### Small change: PR #3774

[Add udp benchmark to github workflow](https://github.com/asterinas/asterinas/pull/3774)

One short explanation connects adding benchmark workflow entries to making them schedulable.
Do not expand a change of this scale into Background / Implementation / Risks / Test Plan boilerplate.

### Bug fix: PR #3835

[Fix accept() after a queued TCP connection is reset](https://github.com/asterinas/asterinas/pull/3835)

Gives the issue reference, the triggering sequence, the reason an unwrap panics,
and the replacement source of the endpoint.
A separate short paragraph explains a related getpeername correction.
Useful model for a compact, mechanism-based bug-fix description.

### Design follow-through: PR #3701

[Support unified routing table](https://github.com/asterinas/asterinas/pull/3701)

Links the design issue, then concentrates on two clarifications instead of repeating the design.
Expresses uncertainty about the benefit of generics honestly and reasons through loopback versus other subnet behavior with concrete addresses.
Useful for identifying what a PR description should add beyond an existing proposal.

### Semantic distinctions: PR #3600

[Support MSG_TRUNC for all sockets](https://github.com/asterinas/asterinas/pull/3600)

Separates behavior by socket family and distinguishes an input flag from the returned message flag.
Explains a refactoring commit and a known deferred test case because both affect the review scope.
Useful for changes whose apparent single feature has several different semantics.

## PR comments

### Short instruction plus reason

[Remove duplicate constants](https://github.com/asterinas/asterinas/pull/3699#discussion_r3966281747)

Directly asks for removing constants already represented by a flags type, then gives the preferred approach.
One local concern does not need a full review report.

### Design question tied to actual use

[Questioning a trait with one implementor](https://github.com/asterinas/asterinas/pull/3699#discussion_r3966860993)

Identifies the sole implementation, asks whether more implementations are planned,
and suggests using the concrete type if they are not.
The question has a decision consequence; it is not an ornamental invitation for feedback.

### Explaining a semantic disagreement

[Clarifying O_PATH and fchownat](https://github.com/asterinas/asterinas/pull/3572#discussion_r3570102033)

Acknowledges earlier ambiguity, places two calls side by side, and explains why an apparently identical descriptor has different roles.
Then applies that distinction to the disputed fast path and the reviewer's counterexample.
Useful model for a longer reply when one short assertion did not resolve a misunderstanding.
Do not repeat this comment's incidental technical claims without verifying them for the new task.

## Constructed calibration examples

These are illustrative rewrites, not quotations or additional user-authored samples.

Over-formal issue opening:

> This initiative establishes a unified dependency baseline with explicit acceptance criteria and a comprehensive migration framework.

Better direction:

> Currently, most crates use bitflags 1.x, while two components already use 2.x. I think we should use the same workspace dependency. The main reason is that 2.x gives us a safe way to preserve unknown bits.

Overbuilt PR description:

> Summary: eliminate redundant validation. Architecture: centralize validation responsibility. Risk mitigation: preserve compatibility.

Better direction, assuming the implementation was verified:

> This PR removes the empty-path checks at these call sites. The path constructors already handle the same cases, so the additional checks are redundant.

Vague review suggestion:

> Could we perhaps improve the abstraction here to make it more robust and maintainable?

Better direction, assuming the code supports the premise:

> This trait currently has only one implementor. Do we expect another implementation? If not, I think we can use the concrete type directly.
