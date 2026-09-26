# Database-backed audit (v2.2)

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

## Set up source and graph

```text
paper_audit.py init AUDIT.db --source-root PAPER_DIR --title TITLE
paper_audit.py source capture AUDIT.db --files FILES.json
paper_audit.py get AUDIT.db --target papers:pap_ID --mode author --out author.json
```

`FILES.json` is an array of source-root-relative paths. Capture's declaration/citation candidates
are parser output, not evidence. Use [graph-records.md](graph-records.md) while authoring anchors,
exact targets, scopes, meaningful intermediate claims and applications. Generate collection shapes
with `template`; do not rediscover schemas from implementation code. Obtain IDs in batches with `ids`.
Source commands capture actual excerpts and hashes; do not fabricate them. For a runnable authoring
example using the UTF-8 helper, optionally consult [the worked example](probability-example.md).

Edits are append-only. A create uses `expected_version:null`; a replacement uses the supplied current
version and complete body. A conflict requires rereading/re-authoring, not replaying stale edits.
Use `get` then `apply`, never direct SQLite mutations. Source fidelity is recorded with `compare`
or a controller response and remains separate from mathematical correctness.

Read [coordinator-protocol.md](coordinator-protocol.md) for inventory, source boundaries and scope.
Overview selection is a starting graph, not exhaustive proof inventory or proof credit. Preserve its
identities and selection while adding audit detail. Full/focused audits name all three global tasks
`global_consistency`, `adversarial`, and `method_interface`, each required or explicitly not applicable.
Review complete proof continuations before recording accepted proof boundaries.

## Check, review and recover

Register the audit through ordinary authoring. Arrange genuine balanced
[reviewer qualification](database-qualification.md) for the actual independent configuration, then attach
it to the audit. Workers never receive calibration keys. Follow [controller-workflow.md](controller-workflow.md)
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
paper_audit.py release AUDIT.db --audit aud_ID --out release-dir
```

Render at meaningful checkpoints. Use the generated table for examination counts and `status`'s
`process_complete` for audit completion; never hand-count checks. Retain requested parts/exclusions,
draft/stale state, conditional or unavailable support, source limits and review qualification. Explain
findings; do not override a limitation with an unsupported positive summary. Use source labels and
typeset authored mathematics. Inspect the result cards: the exact audited claim and part scope,
saved proof strategy or its absence, recorded inputs and their contributions/restrictions, and
current unresolved issues should be clear before opening detailed evidence. Check that alternate
routes and local conditions remain distinguishable. Inspect actual HTML navigation, formulas,
support qualifications and working/completed status; a useful explanation adds no proof credit.

`checkpoint` preserves the prior HTML if rendering fails. `validate` checks structure and recorded
consistency, never mathematical truth. `release` requires process completion and creates immutable
HTML/export/receipt output; a blocked release creates no directory. Completed audits may contain
gaps, refutations or adjudicated inconclusive results. They may not hide undone work or missing review.

`backup DB --out copy.db` preserves full recovery state. `export DB --out snapshot.json` is only the
mathematical snapshot. `changes DB --since REV` explains affected evidence. Legacy import, storage
migration and shared overview compatibility are [on demand](database-compatibility.md). Report software
tests, browser inspection and scientific evaluation separately.
