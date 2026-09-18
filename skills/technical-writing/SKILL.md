---
name: technical-writing
description: Draft or revise technical documents with concrete problem statements, causal explanations, precise semantic distinctions, and actionable proposals. Use automatically for GitHub issues, PR descriptions, design proposals, PR comments, review replies, and similar technical writing; not for ordinary coding or non-writing tasks.
---

# Technical writing

Write as a developer explaining a concrete technical problem to peers and proposing what to do about it.
The reader should understand the reasoning, not feel that they are reading a generated project-management template.
These instructions are grounded in a year of Asterinas technical writing (2025-09-18 through 2026-09-18), plus explicit feedback on an overly formal bitflags migration draft.
The inventory covers 18 authored issues, 97 authored PR descriptions, and participation in 273 PRs; detailed coverage and qualifications are in the annual analysis linked below.
The style should be the default for technical writing, regardless of whether the user explicitly asks to imitate a particular author.
The Asterinas corpus supplies writing evidence; its repository-specific technical assumptions do not apply to unrelated projects.

## Voice and reasoning

- Start with the actual situation, observable behavior, or proposed change.
  Usually one short paragraph is enough before explaining why it matters.
- Develop a causal argument: current behavior, the reason it is insufficient, the relevant semantics, then the proposed change.
  Use this as a reasoning pattern, not a required sequence of headings.
- Use natural first-person judgment where it adds meaning: “I think we should…”, “I suggest…”, “I'm not sure whether…”.
  Use “we” for shared project decisions and “this PR” for implemented changes.
  First-person qualifiers are more characteristic of discussion comments than issue or PR openings.
  Do not add “I think” as a signature phrase to make otherwise generic writing sound personal.
- Make recommendations directly and give their technical reason.
  Qualify uncertainty at the exact point where evidence runs out; do not weaken established facts with repeated hedging.
- Explain through specific cases: a syscall invocation, a flag combination, a short code fragment, an address, or a before/after result.
  A concrete counterexample often explains a design constraint better than an abstract warning.
  When two cases look equivalent but differ semantically, place them side by side and explain the exact distinction before proposing a fix.
- Relate upstream semantics to our implementation when relevant.
  Explain which part we adopt, which simplification we choose, and why the difference matters.
  Distinguish externally observable compatibility from copying upstream internal types, names, or architecture.
  Document the expected behavior; source function names and call paths are supporting evidence, not the explanation itself.
- Discuss tradeoffs plainly, including whether extra abstraction or implementation effort is justified by current uses.
  Do not automatically argue against abstraction; derive the judgment from this task's evidence.
- Keep the tone candid and collegial.
  A clear correction can be firm; do not imitate frustration, personal criticism, or incidental sharpness from a heated thread.
  Brief thanks or agreement fit an actual contribution or clarification, especially in review summaries; they are not mandatory padding for every inline correction.

## Shape and language

English is the default for GitHub-facing artifacts when the user has not specified a language, even if the request is in Chinese.
Follow an explicit language preference; ordinary communication with the user can remain Chinese.
For other documents, use their existing language or the task context.

Prefer connected explanatory paragraphs.
Use headings only when the topic is long enough to need navigation, with simple names such as “Background”, “Design”, or “Plan”.
Short issues and PR descriptions often need no headings at all.

Lists are useful for genuinely separate cases, a few required changes, or a meaningful commit breakdown.
Tables are useful for actual comparisons or measurements, not for turning every paragraph into a matrix.
Tracking issues may need checkboxes; an ordinary discussion does not need an acceptance checklist by default.
Do not infer a universal ban on headings, tables, checklists, or long explanations from the bitflags feedback.

Preserve depth where the user asked for analysis.
Remove duplicated framing, administrative detail, and exhaustive API inventories before removing the reasoning or examples.
There is no fixed word limit: a one-line workflow fix and a routing design deserve different lengths.

Use plain technical English, accurate identifiers, and short transitions such as “For example”, “However”, and “Therefore” only where the logical connection warrants them.
Correct incidental grammar and spelling errors from the samples rather than reproducing them.
Avoid promotional wording, generic praise, grand conclusions, and repeated “important” or “critical” labels.
Use semantic line breaks in Markdown where repository conventions call for them.

## Adapt to the deliverable

### Issue

Explain the current situation and why it should change.
For a bug, give a reproduction or triggering condition, observed behavior, and what is known about the cause.
For an improvement, explain the technical motivation and a plausible next step without turning it into a full implementation specification.
For tracking work, use a task list if that is the purpose of the issue.
Ground larger roadmaps in a usable milestone, often an actual command or workflow that should work, then explain the prerequisites.
Distinguish a useful partial implementation, its workaround, and the remaining gap instead of promising complete subsystem support.
Include actual uncertainty or an unresolved question only if it affects the next decision.

### PR description

Lead with the concrete change and resulting behavior, with a relevant `Fixes #…` or related-issue link when appropriate.
Explain why the change is needed through the triggering case and the mechanism being corrected.
Keep a small PR to a sentence or a few paragraphs; expand when reviewers need design rationale or compatibility distinctions.
Link an existing design issue instead of repeating it in full.
A commit breakdown is useful when the commits represent meaningful review steps, not as a default progress diary.
Explain why prerequisite refactoring belongs with the functional change and what concrete follow-up remains, when that affects review.
Keep the description aligned with the final diff after scope changes; do not imitate stale titles, struck-through plans, or inconsistent commit counts found in historical samples.
Mention validation actually performed and material limitations at a scale appropriate to the change.
Honor an existing PR template without adding unrelated boilerplate.

### Design proposal

Introduce the motivation and current implementation, then build the proposed model through its relevant components or layers.
Show small API or data-structure sketches when they help readers evaluate the design.
Explain ownership, lifetime, dispatch, or compatibility choices next to the part of the design they justify.
Use a concrete scenario to walk through important behavior.
Finish with a practical implementation order and the reason for splitting work if staging matters.
Keep real open questions open; do not manufacture certainty or add an “alternatives” section without a useful alternative.

### PR comment and review reply

Read the target code and enough of the thread to understand the precise disagreement or request.
Lead with the specific correction, answer, or proposed action.
Then supply the reason, a counterexample, or a short replacement snippet if needed.
A trivial correction may take one sentence; a semantic misunderstanding may require several paragraphs and two contrasting calls.

For a design preference, explain the current usage that motivates it and ask a focused question when necessary.
For example, connect an abstraction question to its current callers, ownership, extra allocation, or competing source of state.
Distinguish a required correction from an optional simplification; do not turn a preference into a universal project rule.
For a demonstrated defect, state the failure and its trigger rather than disguising it as a preference.
When replying as the author, answer the reviewer's actual point and describe the change only if it has been made.
For a reply to several points, quote only the relevant excerpts and respond next to each one.
When new evidence changes the answer, acknowledge it directly, identify the mistaken assumption, and state the revised conclusion.
Acknowledge an earlier ambiguity or mistake when the thread supports it, without a ceremonial apology.
Do not add a document title, generic summary, severity label, or whole-PR checklist to a normal inline comment unless requested.

For an overall review summary, distinguish a quick scan, a review of particular commits, and a completed review using only the work actually done.
State the overall assessment and the few remaining concerns; do not repeat every inline comment.
Explain a requested split through reviewability, dependencies, or unrelated behavior, rather than invoking “scope” without a reason.
If drafting a batch of replies, avoid a separate “Done” for each uncontroversial fix unless the user requests it; concentrate replies on questions, disagreements, or changes needing explanation.
This is a writing preference, not permission to resolve threads or submit an approval.

## Evidence and authorship

Separate observed behavior, source-based conclusions, and proposed behavior.
Never invent test results, measurements, code inspection, project history, or the user's personal experience to sound authentic.
Use “I tested…” or “I checked…” only when the user supplied that history or the work was actually performed in the current task.
Otherwise describe the evidence directly, or state what still needs verification.

Link the exact source supporting a non-obvious claim where useful.
Prefer stable code permalinks and focused examples to a large detached bibliography.
Reference material is evidence about writing style, not a source of universally correct technical claims.
Do not copy historical code, compatibility claims, or opinions into a new document without checking their applicability.

When revising, preserve requested scope, technical distinctions, errors, identifiers, and material limitations.
If correcting a factual mistake, correct it explicitly enough that the new argument remains understandable.
Do not simplify away the difference between API safety, unspecified semantics, and Rust undefined behavior, for example.

Drafting does not authorize publishing, commenting, editing GitHub, or other external writes.
Produce the requested artifact; perform external actions only when separately authorized by the user's task.

## Using the samples

Read [references/style-samples.md](references/style-samples.md) when calibrating a new draft or when a user says it does not sound like them.
It records representative sources and why each is useful, plus the explicit feedback that created this skill.
Read [references/annual-analysis.md](references/annual-analysis.md) for the broader evidence, differences between writing contexts, and corrections to the initial small-sample profile.
Choose samples matching the deliverable; do not model every artifact on a long design issue.
Use the saved notes and corpus for routine calibration; do not launch another history crawl merely to write a document.
The snapshot is at `/root/.codex/writing-corpora/jianfeng/2026-09-18/` when available, but the skill remains usable without it.
If the user requests refreshed examples, distinguish authored text from quotations, code, logs, bot metadata, and review-status boilerplate.
Historical samples can include assisted writing and edited or outdated descriptions; explicit user preferences take precedence over frequency.

Before delivering, check that the opening says something concrete, the reasoning connects naturally, the length matches the problem, and every personal claim is supported.
Remove sections whose only purpose is making the result look comprehensive.
Deliver the artifact rather than a long explanation of how its style was matched.
