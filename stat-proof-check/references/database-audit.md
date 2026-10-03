# Database-backed audit

Use the installed `python "<skill-root>/scripts/paper_audit.py" <command>` for new/current audits.
SQLite is authoritative; JSON and HTML are derived views. Existing v1.5 folders use
[legacy-workflow.md](legacy-workflow.md) until explicitly imported. The current core uses record/storage
format 4, packet/projection 2, and protocol `item-audit/1`. Check `version` once per installation/session:
`bundle.ok` must be true. A mismatched bundle needs repair before writing evidence.

## Command contract

Commands emit one JSON object to stdout; diagnostics go to stderr. Run `--help` directly for plain text. Use
[the UTF-8 helper](../scripts/audit_io.py) for saved JSON and subprocess output on every platform.
Exit 0 means success, 2 invalid input, 3 conflict, 4 incompatible package/schema, 5 missing source,
6 render/publication failure. `status` with `process_complete:false` is a successful incomplete assessment.
Failures include `error.code`, `message`, and affected records. For submissions, also inspect `stored`
and `committed_revision`; retained input need not have produced accepted mathematics.

`get` without `--out` returns the packet (`records` is a list). With `--out`, it writes that
packet and returns a receipt: `out` is its path and `record_count` (also `records`) is a count.
When using `get ... --out work/authoring/author.json`, parse that saved file once for packet
records, for example `json.loads(Path(receipt["out"]).read_text(encoding="utf-8"))["records"]`.

Pass `--run-id RUN` to database commands when collecting command timing. `ids` and `version` have
no database and do not accept it. Use `telemetry summary DB --run-id RUN`; unavailable model/time
measurements stay unknown. Measure at meaningful boundaries, not by polling after every record.

## Choose the work folder

For a new audit, choose `proof-check-<paper-name>/` beside the manuscript, unless the user supplies
another destination. This is the work root: place `audit.db` and `report.html` directly inside it.
Start from the manuscript in a new proof-check database; do not copy, convert, attach to, or expand
a proof-graphify database or use its output folder for the audit.

When resuming the same proof-check audit, reuse its existing folder, database and report paths,
including older folder names, and skip `init`. Do not rename or move saved work merely to adopt
this convention. For a separate audit, if the proposed folder already exists, choose the first
unused suffix such as `proof-check-<paper-name>-2/`, then `-3/`; do not merge into an occupied folder.

```text
proof-check-<paper-name>/
  audit.db
  report.html
  work/
    authoring/                 source lists, batches, templates and query context
    assignments/               one folder per assignment: <role>-<result>-<number>/
    qualification/             one folder per qualification, with grading and responses
    sources/
      extracted-text/
      page-images/
      external-references/
    recovery/                  recovered assignment/submission copies
    finalized/                 frozen report-snapshot.json and finalization.json bundles
    helpers/                   small task-specific scripts
    exports/                   optional mathematical snapshots
    backups/                   optional database backups
  releases/                    optional completed snapshots
    <release-name>/             report.html, export.json, receipt.json
```

Create supporting folders only when needed. Assignment filenames and worker delivery rules are in
[controller-workflow.md](controller-workflow.md). `work/` includes durable responses and evidence;
it is not disposable scratch space. Retain useful query snapshots rather than saving every query.

In the current database command examples, `AUDIT.db` means this folder's `audit.db`. Relative
command-line input/output paths resolve from the working directory: run from this root or supply
absolute paths for the database and files. Create needed parent directories before writing authored
files. Keep installed scripts in the shared installation and use the actual manuscript directory's
absolute path for `PAPER_DIR`; do not relocate the manuscript into the output folder.

## Set up source and graph

```text
paper_audit.py init AUDIT.db --source-root PAPER_DIR --title TITLE
paper_audit.py source capture AUDIT.db --files work/authoring/files.json
paper_audit.py get AUDIT.db --target papers:pap_ID --mode author --out work/authoring/author.json
```

`work/authoring/files.json` is an array of source-root-relative paths. Capture's declaration/citation candidates
are parser output, not evidence. Use [graph-records.md](graph-records.md) while authoring anchors,
exact targets, scopes, meaningful intermediate claims and applications. Generate collection shapes
with `template`; do not rediscover schemas from implementation code. Obtain IDs in batches with `ids`.
Source commands capture actual excerpts and hashes; do not fabricate them. For a runnable authoring
example using the UTF-8 helper, optionally consult [the worked example](probability-example.md).

Coordinators can use `source diagnostics AUDIT.db --degraded` to locate current PDF anchors
with detected replacement characters. Omit `--degraded` to list all current PDF anchors and
their extraction limitations. Rows show the captured source version and file, physical page,
replacement count, limitation, and direct live referrers to that anchor version, without excerpts.
This read-only view does not change evidence or audit status. No detected replacements does
not establish correct extraction; visually inspect consequential formulas. Treat a damaged
passage according to its actual use, without propagating uncertainty to unrelated work.
Keep this coordinator inventory out of independent source-only delivery; supply the necessary
source and its limitations through the existing worker packet and context-extension workflow.

An optional early checkpoint can help compare recorded results and connections with declared scope.
It is a preview, not a required interruption of Stage 1. Missing connections require further dependency
recording or an explicit limitation; isolated nodes do not establish independence.

Reuse the database and report paths; do not delete durable data, authored responses or provenance,
or relocate registered sources merely to tidy the folder.
Accepted `source anchor` and `source review` requests can be retried unchanged with the same request ID.
Their returned receipt and anchor listing describe historical acceptance; use `status` for current
freshness. Changed input needs a new request ID. This does not automatically recapture changed files.

Edits are append-only. A create uses `expected_version:null`; a replacement uses the supplied current
version and complete body. A conflict requires rereading/re-authoring, not replaying stale edits.
Use `get` then `apply`, never direct SQLite mutations. Source fidelity is recorded with `compare`
or a controller response and remains separate from mathematical correctness.

Blank captured text ranges cannot support a matched source comparison or a completed proof
boundary. They may remain as draft anchors; locate the actual passage and compare again, or
record the uncertainty. Older decisions remain readable but receive no completion credit while
their evidence is blank. PDF page evidence can be checked visually when text extraction is empty.

Read [coordinator-protocol.md](coordinator-protocol.md) for inventory, source boundaries and scope.
Build the audit inventory from the manuscript; a saved graph alone establishes neither exhaustive
coverage nor proof credit. Full/focused audits name all three global tasks
`global_consistency`, `adversarial`, and `method_interface`, each required or explicitly not applicable.
Review complete proof continuations before recording accepted proof boundaries.
For PDF pages containing neighboring results, record the actual proof's `proof_spans` in the
immutable boundary source review as described in [graph-records.md](graph-records.md). Coverage
then follows those reviewed character ranges for each argument, while workers and readers retain
the full page evidence. Do not classify unrelated page material as structural coverage. Missing
selectors retain whole-page coverage, and uncertain proof boundaries remain unresolved.

## Check, review and recover

Register the audit through ordinary authoring. Follow [controller-workflow.md](controller-workflow.md)
for the proof-owner sequence, [qualification](database-qualification.md), role delivery and recovery.
It covers separate sessions or reviewers when subagents are unavailable, and an honest handoff when
required independent execution is unavailable.

Use `work list DB --audit aud_ID` for actionable work, `status DB --audit aud_ID` for assessed state,
and the submission receipt for immediate next actions. Status includes a factual summary of exact
scope, current versus unfinished evidence, dependency support and review state. These recorded facts
cannot prove that the source was faithfully interpreted or the mathematics correctly checked.

`stage1 status` reports primary readiness and representation blockers; `stage2 status` reports review,
global-work and finalization readiness. Normal preparation uses `stage1 prepare` and `stage2 prepare`
with mode `independent`, `reconcile` or `global`. Use the same `work submit`, `work inspect`, `work extend`
and `review map` interfaces throughout. Source comparisons marked `needs_attention` need an actual
correction/recomparison even when counted as completed examinations. A completed mathematical gap
has a different meaning and does not itself block progression.

## Report and release

```text
paper_audit.py stage2 finalize AUDIT.db --audit aud_ID --out work/finalized/result-1
paper_audit.py stage3 build work/finalized/result-1 --out report.html
```

Finalization saves one fixed revision, its report snapshot and a receipt. It does not render HTML.
Stage 3 consumes that saved bundle and preserves its exact audit identity, findings, scope and limitations.
If the live database later changes, the old report remains a historical snapshot until deliberately renewed.
Renderer or layout changes do not require scientific reexamination.

Use `stage2 finalize --partial` to save a working snapshot with its actual incomplete work or source
representation blockers. Canonical examination counts remain unchanged; a working report is not a
finalized audit even when those counts are complete. Failed analysis cannot create a new canonical
snapshot. Keep its diagnostics and any older snapshot, clearly identified as historical.

Use optional `checkpoint` previews at meaningful boundaries. Use the generated table for examination counts and `status`'s
`process_complete` for audit completion; never hand-count checks. Retain requested parts/exclusions,
draft/stale state, conditional or unavailable support, source limits and review qualification. Explain
findings; do not override a limitation with an unsupported positive summary. Use source labels.
Checkpoint receipts and the report's collapsed Math display notes summarize literal fallbacks
by cause and saved record field. These are nonblocking presentation notes, not a repair queue;
they require no additional checkpoint, source comparison or rewrite of audited text.
Follow [mathematical text and JSON](mathematical-checking.md#mathematical-text-and-json)
for authored formulas and source transcription. Inspect the result
cards: the exact audited claim and part scope,
saved proof strategy or its absence, recorded inputs and their contributions/restrictions, and
current unresolved issues should be clear before opening detailed evidence. Check that alternate
routes and local conditions remain distinguishable. Inspect actual HTML navigation, formulas,
support qualifications and working/completed status; a useful explanation adds no proof credit.

`checkpoint` preserves the prior HTML if rendering fails. `validate` checks structure and recorded
consistency, never mathematical truth. The compatibility `release` command composes finalization and
publication into immutable HTML/export/receipt output; it requires process completion and settled
source representation. A blocked release creates no public release directory. Completed audits may contain
gaps, refutations or adjudicated inconclusive results. They may not hide undone work or missing review.

```text
paper_audit.py release AUDIT.db --audit aud_ID --out releases/<release-name> --checkpoint-out report.html
```

Pass the established report path to `--checkpoint-out` for recovery advice when release is blocked.
If publication fails after freezing, retain its reported preparation directory and follow the supplied
`release ... --resume PREPARATION_DIR` command. It finishes delivery from the old snapshot rather than
reexamining the paper or silently switching to the live revision. A direct Stage 3 build failure simply
reuses the same frozen bundle. Never describe a retained older HTML file as the new successful build.

`backup AUDIT.db --out work/backups/<backup-name>.db` preserves full recovery state.
`export AUDIT.db --out work/exports/<snapshot-name>.json` is only the mathematical snapshot.
Use a fresh name for each retained backup, export or release. `changes AUDIT.db --since REV` explains
affected evidence. Legacy import and existing-store compatibility are
[on demand](database-compatibility.md). Report software tests, browser inspection and scientific
evaluation separately.

## Stop and hand off

Before stopping with unfinished work:

1. Save substantive partial reasoning and authored responses, then inspect `status` and `work list`
   using the [pagination guidance](controller-workflow.md#prepare-and-dispatch) for the remaining inventory.
   Inspect known assignment/delivery directories for unsubmitted output as well as intake history;
   follow [controller recovery](controller-workflow.md#recover-only-affected-work) without treating files
   as accepted evidence. Preserve response paths, packet/request identities and specific remaining questions.
2. Save an explicitly working snapshot with `stage2 finalize --partial` when assessment can complete,
   then build it with Stage 3 if useful. A `checkpoint` remains an optional preview. If assessment or
   rendering fails, disclose the failure and link the database and saved work; identify retained older HTML as old.
3. Deliver report/database paths and their revisions, exact examined scope and exclusions, findings,
   saved output awaiting integration, unfinished obligations and next action. A short continuation note
   points to these artifacts rather than maintaining another task ledger. Missing independent execution
   requires this limited handoff, never a completed-audit claim.

The checkpoint receipt returns the same factual scope summary as `status` and commands for remaining work.
For a completed release, link its report as the final artifact; keep the working files for continuation.
`status` also exposes bounded coverage diagnostics and their total/truncation information. Keep
excluded supplementary proofs explicit. Full/Focused skill completion requires the prescribed
independent work; disclose a generic audit configuration that disables it rather than claiming a
completed full skill audit. Triage remains limited.

When `release` is blocked by an incomplete audit, it creates no release directory and its recovery
commands reuse `--checkpoint-out` when supplied. If that option was omitted, the guidance returns
a checkpoint template requiring an explicit `--out` choice, alongside the work-list command.
Choose this audit's existing working-report path, or the root `report.html` for a new audit,
before running that checkpoint.
If writing a release fails after some files exist, the error identifies those files, the failed
step and retained frozen preparation. It is not a delivered release. Use its exact resume operation;
do not discard finalized scientific data merely because presentation failed.
