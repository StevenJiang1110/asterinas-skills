# Analysis of the 2025–2026 writing corpus

## Coverage and method

Repository: `asterinas/asterinas`. Author: `StevenJiang1110`.
Window: 2025-09-18 00:00:00 UTC through 2026-09-18 02:23:57 UTC.
This is one repository's accessible activity, not all of the author's GitHub activity.

| Material | Retrieved records |
| --- | ---: |
| Issues created in the window | 18 |
| PRs created in the window, with their descriptions | 97 |
| Ordinary discussion comments on PRs, written in the window | 163 |
| Inline review comments written in the window | 1,297 |
| Submitted reviews in the window | 529 |
| Reviews with nonempty bodies | 282 |
| Distinct PRs with a comment or submitted review in the window | 273 |

The 273 includes review-only participation, including approvals without text.
There are 1,742 nonempty comment/review bodies across the three comment categories; an empty review is not a writing sample.
PRs created earlier than the window remain included if the author commented or reviewed during the window.

Collection combined authored-issue and authored-PR searches, commenter/reviewer discovery,
repository-wide ordinary and inline comment endpoints, and paginated reviews for 384 candidate PRs.
The repository comment endpoints returned 3,253 ordinary comments and 11,450 inline comments before filtering by author and creation time.
Search responses reported complete results and remained below the search result cap.
Review submission time was used for reviews; an old comment merely edited this year was excluded.

All retained records were indexed and included in automated structural/length analysis.
Issue bodies and PR descriptions were inspected across the collection; comments were read in month-spanning samples,
with additional examination of longer semantic discussions and all 38 review summaries containing at least 30 approximate prose words.
Some reading views omitted code/log blocks to focus on prose.
This is full-corpus collection and statistical analysis with selective close reading, **not a claim that every comment was individually interpreted in its complete thread**.
The generated `close-reading.jsonl` is a candidate reading set, not a completion log.

The snapshot stores current editable bodies, not historical revisions.
Deleted or inaccessible material is unavailable.
Account authorship does not prove every sentence was written unaided; the corpus itself occasionally credits Codex.
Quoted interlocutors, source excerpts, and code are not evidence of the author's personal phrasing.

Local corpus: `/root/.codex/writing-corpora/jianfeng/2026-09-18/`.
`manifest.json` records scope and PR IDs; `records.jsonl` holds indexed texts and URLs; `statistics.json` records the measurements.
The original API records are retained separately for checking the normalization.
No corpus download is required to use this skill.

## What the larger sample changes

### 1. There is no single preferred document shape

Approximate prose-length medians are 204 words for issues, 82 for PR descriptions,
45 for PR conversation comments, 27 for inline comments, and 5 for nonempty review summaries.
Lengths exclude fenced blocks, blockquote lines, HTML comments, and URLs using a heuristic parser;
indented excerpts and Markdown edge cases may remain.
These figures describe the observed mix, not writing quotas.

Only 8 of 97 PR descriptions have Markdown headings, compared with 11 of 18 issues.
Seven issues use checkboxes, while none of the PR descriptions do.
Of the 1,256 inline comments with extracted prose, 695 have at most 30 approximate words.
A short local correction and a long design proposal should therefore not inherit the same outline.

Examples:

- [#2907](https://github.com/asterinas/asterinas/issues/2907): a compact argument for an unsigned file descriptor type.
- [#2911](https://github.com/asterinas/asterinas/issues/2911): a substantial roadmap organized around a runnable container workflow and dependencies.
- [#3224](https://github.com/asterinas/asterinas/issues/3224): a detailed hotplug plan with a sequence, tasks, and validation.
- [#3313](https://github.com/asterinas/asterinas/issues/3313): a performance investigation using tables and an environment comparison.
- [#3774](https://github.com/asterinas/asterinas/pull/3774): a workflow change described in two short sentences.

The user's rejection of the first bitflags draft remains stronger evidence than any one historical template.
Keep tables and checklists when they do real work; remove them when they merely make a small proposal look exhaustive.

### 2. Personal voice comes from the reasoning, not repeated first-person qualifiers

The literal phrase “I think” appears in only 1 of 18 issue bodies and 2 of 97 PR descriptions,
but in 173 inline comments and 26 ordinary PR comments after excluding explicit quoted lines.
Other first-person expressions exist; these counts do not measure all first-person writing.

Issue and PR openings usually state the situation or the change directly.
Discussion comments more often introduce a judgment, a question, or uncertainty.
Do not manufacture personal voice by inserting “I think” into every opening.

[#2860](https://github.com/asterinas/asterinas/pull/2860) follows the causal chain from a changing build timestamp to changed kernel contents to redundant NixOS rebuilds.
[#3300](https://github.com/asterinas/asterinas/pull/3300) explains a port-allocation issue using the sequence of concrete socket operations.
These mechanisms make the writing distinctive and useful even without a signature phrase.

### 3. Apparently similar cases are separated before a fix is proposed

Several extended discussions turn on a precise semantic distinction:

- [VMO capabilities](https://github.com/asterinas/asterinas/pull/2444#issuecomment-3317872552): permission to modify an object versus permission to map it writable.
- [Credentials](https://github.com/asterinas/asterinas/pull/2516#issuecomment-3420396042): the libc wrapper's behavior versus the raw syscall's behavior.
- [O_PATH](https://github.com/asterinas/asterinas/pull/3572#discussion_r3570102033): a descriptor used as a path reference versus one used directly for an operation.
- [#3600](https://github.com/asterinas/asterinas/pull/3600): differences among socket types and between input flags and returned flags.

Writing lesson: show the two cases and explain the distinction that changes the result.
Do not copy their historical technical conclusions into new work without checking them.

### 4. Upstream behavior is evidence, not a demand to copy implementation

The author frequently requests source references and observable compatibility,
while questioning internal abstractions that add little to the current use case.

[The FileMode discussion](https://github.com/asterinas/asterinas/pull/3086#discussion_r3031293757)
explicitly separates Linux compatibility from matching Linux's internal implementation.
[This documentation review](https://github.com/asterinas/asterinas/pull/3365#pullrequestreview-4752510222)
asks for expected behavior to be documented instead of a list of Linux implementation details.
[The link correction](https://github.com/asterinas/asterinas/pull/3699#discussion_r3985522409)
shows that references should land on the relevant definition or explanatory comment.

Writing lesson: name the behavioral requirement first; use a source path or call chain to substantiate it.
Avoid turning “Linux does this internally” into the entire rationale.

### 5. Review comments have different jobs

A local fix can be an imperative plus one reason, or a suggestion block.
The corpus contains 121 inline comments with suggestion fences, but this is not a requirement to use them.

A design question usually identifies the concrete cost or missing use case:
[one implementor](https://github.com/asterinas/asterinas/pull/3699#discussion_r3966860993),
[an additional wrapper and shared state](https://github.com/asterinas/asterinas/pull/3787#discussion_r3955961795),
or [a derived state flag](https://github.com/asterinas/asterinas/pull/3699#discussion_r4011638240).
The last example explicitly leaves one simplification optional.

An overall review summary serves a different purpose:
[reviewing particular commits](https://github.com/asterinas/asterinas/pull/3702#pullrequestreview-4914407648)
or [narrowing an over-broad PR](https://github.com/asterinas/asterinas/pull/3131#pullrequestreview-4417019475).
Brief thanks, agreement, and LGTM are common in this setting; do not ban them as inherently artificial.
Never fabricate an approval or reviewed scope just to imitate the form.

[The thread-management comment](https://github.com/asterinas/asterinas/pull/3699#pullrequestreview-5174527750)
explicitly says that already-fixed, uncontroversial comments do not each need a reply.
When asked to draft replies, focus on what needs explanation or confirmation; do not silently perform thread actions.

### 6. Revising a judgment is part of the voice

The credentials discussion above acknowledges a mistaken test assumption and gives the corrected conclusion.
[This API discussion](https://github.com/asterinas/asterinas/pull/2564#discussion_r2509275799)
accepts another developer's explanation rather than defending the original preference.
[The DMA naming exchange](https://github.com/asterinas/asterinas/pull/3702#discussion_r3861531981)
adjusts the naming suggestion after learning that the method consumes its input.

Writing lesson: acknowledge the specific new information, update the answer, and retain any remaining concrete question.
Do not imitate confidence that the evidence does not support, or add a lengthy apology ritual.

### 7. Scope decisions are explained through practical dependencies

[#3134](https://github.com/asterinas/asterinas/pull/3134) describes a temporary dependency workaround, its removal condition, and a publishing limitation.
[The sendfile discussion](https://github.com/asterinas/asterinas/pull/3191#issuecomment-4438632084)
weighs a targeted repair against implementing a much larger mechanism.
[#3684](https://github.com/asterinas/asterinas/issues/3684) explains why routing infrastructure and netlink details can be staged.

Writing lesson: explain which behavior works now, which case remains, and why the boundary is reasonable.
Do not automatically split every change or add unrelated future-work lists.

### 8. A final description should reflect the final work

[This review](https://github.com/asterinas/asterinas/pull/3129#pullrequestreview-4250133045)
asks for a description to be updated after its scope and tests changed.
The corpus also contains visibly stale material: for example,
[#2898](https://github.com/asterinas/asterinas/pull/2898) has a zerocopy title with an older bytemuck-oriented body,
and [#2759](https://github.com/asterinas/asterinas/pull/2759) retains struck-through earlier plans.
These are evidence that historical artifacts are imperfect, not habits to reproduce.

## How to apply this evidence

Choose the artifact's job first: report a failure, propose an improvement, explain a diff,
plan a subsystem, request a local change, answer a review point, or summarize a review.
Then select the relevant tone and amount of explanation.

The durable pattern is concrete behavior, a causal explanation, precise distinctions, and an actionable next step.
Do not mistake repeated subsystem topics, one sharp exchange, frequent approval boilerplate,
or mechanically counted phrases for universal writing rules.
