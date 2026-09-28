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

Render an early checkpoint after recording the main results and their source-backed uses. Compare
the displayed results and connections with the declared scope. Missing connections require further
dependency recording or an explicit limitation; isolated nodes do not establish independence.

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

## Check, review and recover

Register the audit through ordinary authoring. Arrange genuine balanced
[reviewer qualification](database-qualification.md) for the actual independent configuration, then record
its ID in the audit configuration. Workers never receive calibration keys. Follow [controller-workflow.md](controller-workflow.md)
for exact role delivery and the prepare/examine/submit cycle. Several local examinations can share one
coherent assignment. Save meaningful partial reasoning before yielding.

Use `work list DB --audit aud_ID` for actionable work, `status DB --audit aud_ID` for assessed state,
and the submission receipt for immediate next actions. Status includes a factual summary of exact
scope, current versus unfinished evidence, dependency support and review state. These recorded facts
cannot prove that the source was faithfully interpreted or the mathematics correctly checked.

Independent review starts source-only in a fresh context. Preserve its unchanged response, map
source targets using the private coordinator context, and reconcile exact-target evidence. A
substantive new route requires declared supplied-route review. Missing independent capability
requires a working result/handoff, not manufactured qualifying self-review.

## Report and release

```text
paper_audit.py checkpoint AUDIT.db --audit aud_ID --out report.html
paper_audit.py validate AUDIT.db
paper_audit.py release AUDIT.db --audit aud_ID --out releases/<release-name> --checkpoint-out report.html
```

Pass the chosen working-report path to `--checkpoint-out`; when resuming, use its established path.
This option supplies recovery guidance if release is blocked and does not change the release output.

Render at meaningful checkpoints. Use the generated table for examination counts and `status`'s
`process_complete` for audit completion; never hand-count checks. Retain requested parts/exclusions,
draft/stale state, conditional or unavailable support, source limits and review qualification. Explain
findings; do not override a limitation with an unsupported positive summary. Use source labels.
Follow [mathematical text and JSON](mathematical-checking.md#mathematical-text-and-json)
for authored formulas and source transcription. Inspect the result
cards: the exact audited claim and part scope,
saved proof strategy or its absence, recorded inputs and their contributions/restrictions, and
current unresolved issues should be clear before opening detailed evidence. Check that alternate
routes and local conditions remain distinguishable. Inspect actual HTML navigation, formulas,
support qualifications and working/completed status; a useful explanation adds no proof credit.

`checkpoint` preserves the prior HTML if rendering fails. `validate` checks structure and recorded
consistency, never mathematical truth. `release` requires process completion and creates immutable
HTML/export/receipt output; a blocked release creates no directory. Completed audits may contain
gaps, refutations or adjudicated inconclusive results. They may not hide undone work or missing review.

`backup AUDIT.db --out work/backups/<backup-name>.db` preserves full recovery state.
`export AUDIT.db --out work/exports/<snapshot-name>.json` is only the mathematical snapshot.
Use a fresh name for each retained backup, export or release. `changes AUDIT.db --since REV` explains
affected evidence. Legacy import and existing-store compatibility are
[on demand](database-compatibility.md). Report software tests, browser inspection and scientific
evaluation separately.

## Stop and hand off

Before stopping with unfinished work:

1. Save substantive partial reasoning and authored responses, then inspect `status` and `work list`.
2. Create a `checkpoint` at the chosen working-report path when possible. If rendering fails,
   disclose the failure and link the database and saved work; identify any retained older HTML as old.
3. Deliver the report and database paths, exact examined scope and exclusions, findings, unfinished
   obligations, and next action. Missing independent execution requires this limited handoff,
   never a completed-audit claim.

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
If writing a release fails after some files exist, the error identifies those files and the failed
stage; it is not a delivered release. Keep them for inspection before choosing a new destination.
