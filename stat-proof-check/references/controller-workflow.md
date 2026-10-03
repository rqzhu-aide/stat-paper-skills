# Proof workflow and bounded controller

The coordinator owns graph construction, dispatch and scientific decisions. The controller records
explicit work; it never calls models or decides that the graph includes every mathematical premise.
Use [database-audit.md](database-audit.md) for setup and [coordinator-protocol.md](coordinator-protocol.md)
for inventory and scope. This is the canonical operating sequence and recovery procedure.

## Carry one proof forward

A proof unit is one exact conclusion, one written route, its setup and complete source passages.
It uses existing records, not a new storage object. The coordinator is its default primary owner:
keep source comparison, primary examination, coverage and later reconciliation in one continuing
context when useful. Delegate coherent mathematical work when it needs a separate context, rather
than launching a worker for each record type. Reconciliation compares the examinations; it does not
routinely require a third complete examination. Existing role permissions still govern every write.

At startup or resume, inspect database state and known saved outputs before commissioning more work.

| Stage | Work and next operation |
|---|---|
| 1 Prepare and examine | Inventory the source, compare statements/setup and complete proof boundaries, correct known representation problems, build useful graph detail and save primary examination with coverage. Use `stage1 status` and `stage1 prepare`. |
| 2 Review and finalize | Obtain independent examination, integrate unchanged responses, map source targets and reconcile actual reasoning. Finish applicable global checks and the final inventory comparison, then `stage2 finalize`. |
| 3 Produce HTML | Use `stage3 build` on the frozen snapshot. Check presentation and navigation without reexamining unchanged mathematics. |

The normal Stage 2 preparation checks Stage 1 readiness across the declared audit scope. Required local
primary examinations must be current and accounted for, and known source/representation problems settled.
Current required source comparisons must be `matched`: a comparison marked `needs_attention` can be
counted as examined while still needing correction. Use current `get`/`compare` and authorized authoring
to settle it; do not repeatedly request an already satisfied task. Completed mathematical gaps or
refutations can advance. Missing source and unfinished drafts remain incomplete.

If proof B is blocked, explicitly use `stage2 prepare --mode independent --ready-subset --focus items:itm_A` to review a
ready proof A. Its actual primary prerequisite closure must be ready. Ordinary `--focus`, exclusions,
or provisional options do not bypass the boundary; global work cannot use the subset exception. The
declared audit scope and its unfinished work remain unchanged. Do not require independent qualification
to finish Stage 1. Arrange qualification before independent dispatch.

Global consistency, adversarial and method-interface tasks belong to Stage 2 even though their stored
role is primary. Use `stage2 prepare --mode global` after local review and reconciliation settle.
When Stage 2 discovers a substantive correction, revisit the affected records and current change
diagnostics. Preserve unrelated examinations and original responses. Save and integrate useful returns
before expanding the worker pool. A negative result is not a reason to seek repeated favorable reviews.

These stage boundaries govern normal preparation, not the eligibility of previously valid reviews.
Submission, inspection, mapping and recovery remain available throughout. The existing `work prepare`
interface remains for compatibility and specific exceptional investigations, including supplied-route
review; record the purpose and limitations of such work. Three stages do not mean three giant assignments.

## Choose available execution contexts

Plan the actual available reviewer configuration before dispatch. Arrange [qualification](database-qualification.md)
once and reuse it across fresh contexts while provider, model, effort, tools and isolation are unchanged.
A genuine configuration change requires new calibration. Verify actual isolation and exposure for each review.

| Capability or interruption | Action |
|---|---|
| Isolated workers are available | Use source-only independent contexts; parallelize unrelated primary work when useful. |
| No subagents, but a clean session or another reviewer is available | Deliver the same neutral files sequentially and submit the unchanged return with actual provenance. |
| No verifiable independent context | Preserve primary work and a reviewer handoff. Required independence remains unfinished; do not disable it to claim Full or Focused completion. |
| Primary context is lost | A successor identifies itself accurately and continues from saved reasoning, evidence and remaining questions. It cannot replace another reviewer's draft as its own. |
| Original independent author cannot continue | Preserve the response and issue. A new examiner authors its own response and performs the examination needed to support it; it cannot impersonate or silently edit the original author. |

A role prompt, compaction or fork containing primary reasoning does not create isolation. Related neutral
assignments may share the independent examiner's own source context while retaining separate packet responses
and truthful continuity. Use supported equivalent file/command tools; if source inspection or submission is
unavailable, save a precise handoff rather than claiming unseen examination or an unmade database update.

## Prepare and dispatch

Paths follow the [folder rules](database-audit.md#choose-the-work-folder); run from the audit root
or use absolute paths. Keep each assignment under
`work/assignments/<role>-<result>-<number>/`, using a fresh name for new assignments.
`primary-result-1` below is an illustrative assignment name.

```text
paper_audit.py stage1 prepare AUDIT.db --audit aud_ID --focus items:itm_ID --out work/assignments/primary-result-1
```

An assignment groups coherent context for one argument/result and role, normally five units
(`--max-units 1..10`). Applications, joint derivation, coverage and composition can share a worker
call while retaining distinct records. Repeated `--task` selects requested work with necessary joint
context and prerequisites; `task_selection` explains requested versus actually assigned tasks.
`--exclude-task` excludes work assigned elsewhere. There is no background queue. `--allow-provisional` permits
explicit conditional local work, never missing-source or independence bypasses.
`work list --limit` accepts 1..100 tasks per page. Pass a non-null `next_cursor` to `--cursor` with
the same audit and focus to inspect the remaining inventory. After writes, start a fresh listing
without the old cursor, which retains its earlier snapshot. Do not infer completion from the
visible rows; local work need not wait for a scan of every page.

A successful assignment can defer other units:
`different_context` and `unit_limit` mean remaining scheduled work, not a repair. Proceed with
the valid assignment; preserve existing scheduling of other contexts. Size deferrals retain
measured contributors and the applicable limits; do not split a unit or repeatedly guess sizes.

Preparation writes the files below plus coordinator manifest, guidance and an envelope template. Its
`worker_delivery_files` receipt lists files to deliver. Primary `worker-guidance.json` includes a
`task_table` of assigned identities, labels, kinds and result types, plus blank coverage/finding row
templates. Fill only rows justified by the examination; keep explanatory metadata outside the response.
Preserve scaffold IDs and use the generated shapes. Deliver the listed files for each role:

| Role | Deliver |
|---|---|
| Primary | worker-packet.json, response-scaffold.json, worker-guidance.json, [primary-checker.md](primary-checker.md), [mathematical-checking.md](mathematical-checking.md), [evidence-and-verdicts.md](evidence-and-verdicts.md) |
| Independent | Same three worker files, [independent-checker.md](independent-checker.md), the same two scientific references; source-only context with verified isolation/continuity |
| Reconcile | worker-packet.json, response-scaffold.json, worker-guidance.json, coordinator-guidance.json, [reconciler.md](reconciler.md), [evidence-and-verdicts.md](evidence-and-verdicts.md); examine compared judgments |

Add domain/external guidance only when needed. A supplied-route independent assignment additionally
loads [supplied-route-review.md](supplied-route-review.md). Keep mapping, qualification, envelopes,
telemetry, and coordinator manifests out of independent delivery. Do not reload the whole entrypoint
or schema manual when these materials were supplied. Generated shapes have no scientific verdicts.

`prepared:false` with exit 0 is a diagnostic, not completion. Stage readiness and current work facts
explain what remains; they are not proof that every manuscript result was discovered. The CLI's `preparation` summary reports
assessed completion separately from a size, prerequisite or coordinator blocker and supplies next commands.
Finish the named prerequisite, choose another focus, or inspect the meaningful boundary. For size failures,
`preparation.size_action` supplies a bounded retry when supported or identifies context to inspect; a byte
lower bound does not guarantee the retry fits. Packets default to 131,072 bytes, allow
`--max-bytes` up to 1,048,576, and cap records at 2,048. Never truncate a joint argument to fit.

## Save work

Save an informative derivation, defect or unresolved question while its reasoning is in context.
A partial save does not require complete coverage, resolved findings or publication. Retain its examined
evidence and next action before yielding or changing target.

Fill the generated `submission-envelope-template.json`, preserving its initial request and packet IDs
and supplying the actual reviewer. It is coordinator-only first-attempt assistance, not completed
provenance. Independent work also needs the actual qualification/exposure; other modes use null.
For reconciliation, preserve the response scaffold's `request_id` and use that same ID in the
envelope. A different envelope ID does not identify that response.
Save authored envelope and response copies in the assignment directory. A revised response, changed reviewer/provenance,
or explicit rebase needs a fresh request ID; use `ids --kind request` and, for reconciliation, author
that same new ID in the new response before submission. Never change previously submitted bytes.

```text
paper_audit.py work submit AUDIT.db --submission work/assignments/primary-result-1/submission.json --response work/assignments/primary-result-1/response.json
```

Preserve worker bytes unchanged. One request ID identifies those bytes and its envelope; an identical
retry returns the original receipt. Changed input or explicit rebase needs a new ID. Intake precedes
parsing/freshness checks. Included mathematical edits commit atomically; omitted rows remain unfinished.
For a saved terminal rejection, inspect current obligations before reviving the failed submission.
Follow the specific correction below where work is still needed, then use a fresh ID;
unchanged replay only returns that rejection. An unused ID rejected
before intake remains available. Inspect when artifacts or intake state are unclear.
Read `stored`, `state`, `committed_revision`, diagnostics and recovery actions separately. Follow the
specific operation and its required inputs; saving a review awaiting mapping is not a request to redispatch it. Accepted gaps
or inconclusive examinations are not transport errors. Envelope/response limits are 65,536/2,097,152 bytes.

## Recover only affected work

Inspect retained intake and explicitly known assignment/delivery directories. Database history cannot
discover an unsubmitted file. Match packet identities and exact response bytes or hashes to saved attempts,
not descriptive folder names. Files are recovery candidates, not accepted evidence. Preserve old attempts.

| Situation | Action |
|---|---|
| Valid response file has no intake | Check original packet identity, actual provenance and current applicability; submit it or follow its specific recovery diagnostic. A missing task alone does not require another examination. |
| Interrupted intake is still `received` | Inspect by request ID and replay the exact saved envelope/response unchanged. |
| Envelope and worker response name different packets | Inspect both identities and establish the actual assignment before choosing mapping, extension, rebase or authored repair. Correct only an established envelope error; preserve worker bytes. |
| Terminal rejection remains in history | Inspect the original assignment's current obligations and applicable evidence. If all original obligations remain identifiable and satisfied, continue remaining work after comparing unresolved concerns in the saved response. Otherwise recover only work still needed; incomplete or ambiguous current analysis does not establish completion. |
| Administrative envelope error only | Correct the envelope with actual provenance and a fresh request ID when required; preserve worker bytes. No mathematical redispatch is needed. |
| Saved independent response only needs source-target correspondence | [Map the unchanged response](review-mapping.md) using private coordinator context. Do not commission another review solely to supply identities. |
| Wrong worker-authored kind, incompatible target or malformed/scientifically incorrect response | Obtain an authored correction, preserving the original and unresolved concerns. Use genuine author continuity when available; otherwise follow the new-examiner rule above. |
| More reasoning on a saved draft | Select its exact same-reviewer `replaces` pin from coordinator guidance; preserve `supersedes`. |
| Retained reasoning needs current authorization, consumed mathematics unchanged | Keep original packet identity; explicitly rebase authorization in a new envelope. |
| Saved completed judgment, consumed mathematics changed | For primary renewal, pass the needed permissible completed predecessor pin from coordinator guidance in the assignment brief. The worker reexamines, authors `supersedes`, and saves the response for unchanged submission. |
| Missing neutral source in source-only independent work | Capture/anchor it, then `work extend`; examine it and author a new response naming C. |

Several problems can coexist. Mapping cannot remedy absent source, changed inputs, wrong scientific content
or compromised provenance. A new envelope cannot turn unexamined material into evidence. Negative outcomes
and disagreements require their actual reconciliation, not repeated attempts to make the paper pass.

`WRITE_SCOPE` identifies the affected field/reference and its remedy: missing context, a wrong
pin, or an unauthorized edit. Reading a record does not authorize replacing it. `work extend`
supplies independent neutral source context; it is not general primary repair authorization.

For an already saved primary/global response missing context, inspect the named reference and obtain
an appropriate current direct `get --mode primary` packet. Extend that direct packet if needed, then
use generated `template` shapes to author a permitted direct check and `apply` it. This is not a
controller rebase: a direct packet has no controller assignment. Preserve the original response and
receipt. The original examiner can author the direct check from saved reasoning without repeating
unchanged mathematics. A different examiner records its own identity and examines enough evidence to
support its judgment. A coordinator or serializer may prepare the files but does not silently become
the scientific author. Newly supplied source requires examination; rebasing cannot invent that evidence.

Draft and renewal guidance includes the pinned prior outcome, conditions, reasoning and evidence,
plus available changed-input diagnostics. These are previous examinations, not renewed proof credit.
Pass only the allowed predecessor context needed for the assigned primary work. Keep gaps and
restrictions visible unless the examiner explicitly revises them after reexamination.

```text
paper_audit.py work inspect AUDIT.db --request req_ID --out work/recovery/request-1
paper_audit.py work inspect AUDIT.db --packet pkt_ID --out work/recovery/assignment-1
paper_audit.py work inspect AUDIT.db --response rsp_ID
paper_audit.py work extend AUDIT.db --packet pkt_A --request work/authoring/context.json --out work/assignments/independent-result-2
```

The extension request is `{source_refs: [{collection, id, version}], reason: nonempty string}`.
Use live captured anchors or source-origin items/parts. A selected item supplies its statement/setup;
an explicit proof anchor supplies a borrowed passage. Group known additions into one request.
The reason stays private. C retains A's tasks, targets and prior context, including after an
inconclusive completed review; it does not add supplier-review obligations. Changed prior mathematics
needs renewed ordinary work. Oversize context creates no packet. Deliver C once, not full A plus C.

A new response must name C. Rebase cannot claim newly supplied independent evidence. Existing
judgments survive until an explicit successor; newest does not win automatically. Disclose actual
same-reviewer continuation. See [mapping/provenance](review-mapping.md) when a source target or
permissible predecessor pin is needed. `get --extend` remains for direct packets only; its request
is `{targets: [Ref], source_anchor_ids: [ID], source_paths: [string], reason: string}`.

Packet inspection lists saved attempts; choose `--request` to recover exact envelope/response bytes and
original IDs. Initial templates do not replace an authored attempt. `--response` gives current direct or
controller review guidance without `--out`; it does not manufacture a controller intake for direct review.
Request inspection keeps the historical `result` separate from `current` response/recovery guidance.
Accepted intake or a response does not establish current qualifying evidence. Artifact-write errors identify
the saved packet: inspect it instead of preparing duplicate work. Terminal receipts remain historical.
Same-byte artifact output may be reused; different output requires a new directory. Coordinator guidance
reflects current eligibility and may change after another commit; keep the old files and inspect into
a fresh directory rather than freezing obsolete advice or overwriting an authored response.
Notes/check-link edits need not stale mathematics. Adding coverage or changing its spans/claims can
reopen primary composition while local derivations remain current; changed source or scope can also reopen work.
Controller coverage uses `check_task_ids`, `existing_check_refs`, and `replaces`; direct stored coverage uses
`check_ids`, with replacement in
the enclosing edit. Generate the relevant shape rather than copying fields between these interfaces.
Use bounded change diagnostics instead of repeating unaffected checks. Resolve the named blocker or
change the relevant input, evidence or state; otherwise stop that branch and continue other useful work.
A new filename, request ID, worker or identical draft alone does not make progress.

## Review and finish

Use `stage2 prepare --mode independent` for independent work and `stage2 prepare --mode reconcile`
after its saved response is accepted, including any required mapping.
Use generated exact-target eligible pins and [reconciliation rules](reconciler.md).

After local integration, finish required `stage2 prepare --mode global` work and compare the full
inventory with the manuscript. Freeze results before presentation:

```text
paper_audit.py stage2 finalize AUDIT.db --audit aud_ID --out work/finalized/result-1
paper_audit.py stage3 build work/finalized/result-1 --out report.html
```

Use `stage2 finalize --partial` for an explicitly working snapshot when completion or settled source
representation is unavailable. It still requires a successful complete assessment of the recorded
facts. If analysis itself fails, retain diagnostics and the database instead of inventing counts.
An HTML build cannot upgrade working output to a completed release. If rendering fails, keep the
frozen bundle and retry Stage 3 only; do not dispatch another examiner. An optional `checkpoint`
can preview progress, but is not required after every save.

When a gap or disagreement is characterized, record it and continue remaining audit work. Reexamine only a
specific unresolved scientific question; a proposed repaired proof needs its own target/route and review.
At a stopping boundary follow the [handoff checklist](database-audit.md#stop-and-hand-off), including saved
outputs awaiting integration. Report the proof, current operation, meaningful result and next unresolved need.
Distinguish examined/current work, recoverable files, additional examination and unavailable required review.

Preparation selects unfinished work. To correct an already satisfied primary check, use a current
`get --mode primary` packet and `apply` with a full successor-check body, or an authorized reconciliation
batch. `--task` does not reopen completed work. Back up SQLite for recovery; JSON exports omit intake/history.
