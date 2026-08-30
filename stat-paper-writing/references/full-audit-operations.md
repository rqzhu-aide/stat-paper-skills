# Full Writing Audit Operations

Use this file only for a Full manuscript presentation audit. The shared finding and delivery rules remain in [reporting-and-validation.md](reporting-and-validation.md); exact JSON fields remain in [full-audit-data-contract.md](full-audit-data-contract.md).

## Workspace

Run `scripts/writer_audit.py` from any directory with explicit quoted paths. Before initialization, inventory the master source, included TeX files, bibliography, supplement, rendered output, figures, and other in-scope artifacts. The harness snapshots only declared sources and does not infer a TeX closure.

For a new audit:

    python "SKILL_DIR/scripts/writer_audit.py" init --audit-root "AUDIT_DIR" --skill-root "SKILL_DIR" --source "MAIN" --source "SUPPLEMENT" --action audit

Use `--action audit-and-revise` only when revision is authorized. Repeated `--focused-pass` values require an explicit `--focus`. Neutral orientation is always retained; omitted diagnostic passes are not silently inserted.

Common text formats are detected by suffix. Use `--source-kind "SOURCE=KIND"`, where KIND is text, pdf, image, or artifact, only when detection is wrong. PDF snapshots bind a verified page count; if automatic inspection is unavailable, supply `--pdf-page-count "SOURCE=N"` from a trusted page count.

The initializer creates the bound manifest, editable state and findings records, nonsemantic origin record, source snapshots under `inputs/`, protocol snapshots under `protocol/`, and an empty `artifacts/` directory. Each logical protocol path is bound to one unique canonical underlying snapshot file at `protocol/<logical_path>`; aliases, including hard links, are invalid. It creates no final report or receipt.

For resume, always run:

    python "AUDIT_DIR/protocol/scripts/writer_audit.py" status --audit-root "AUDIT_DIR" --json

Do not scaffold over an existing audit. Status, freeze, and check use the snapshotted script. Moving the audit or losing an original path does not invalidate snapshots; snapshot, protocol, scope, plan, or binding drift fails closed.

## Pass coverage

The default plan is:

1. ORIENTATION, descriptive;
2. ATOMIC_DOCUMENTARY_CONSISTENCY, evaluative;
3. FORMAL_OBJECT_AND_CLAIM_CONTRACTS, evaluative;
4. LOCAL_PRESENTATION, evaluative;
5. SECTION_JOBS_AND_TRANSITIONS, evaluative;
6. CROSS_SECTION_CONSISTENCY, evaluative;
7. CONTRIBUTION_LEDGER, conditional;
8. EVALUATIVE_READER_WALKTHROUGH, evaluative;
9. WHOLE_PAPER_NARRATIVE, evaluative;
10. REVISION_CLOSURE, required only for audit-and-revise.

Resolve each conditional pass as completed or not required with a reason. ORIENTATION is the only descriptive pass and loads only `revision-audit.md`. Completed contribution-ledger and whole-paper-narrative passes load `argument-architecture.md`.

For a focused audit, record the exact selected evaluative passes and focus. After orientation, do not add unrequested intermediate passes. Add an indispensable dependency only when its use and reason are recorded.

These are logical checkpoints, not mandatory separate model calls. Each completed pass records the semantic binding, references actually loaded, and one compact checkpoint. Reuse the source-anchored orientation map.

## Structured findings

Load [full-audit-data-contract.md](full-audit-data-contract.md) only when editing `AUDIT_STATE.json` or `FINDINGS.json`, binding closure evidence, or preparing canonical state for freeze or publication.

Before finalization, resolve every pending semantic field while retaining contract-required or permitted nulls. Use line anchors for text, page anchors for PDFs, and artifact locators for other supplied files. Do not paste the manuscript into findings; source hashes plus exact anchors provide traceability.

Resolve `contribution_ledger` as included, not_needed, or unavailable. Use not_needed with a reason when it was skipped or would not clarify the narrative. Use unavailable with a reason and a finding requiring author input, encoded with canonical priority `Blocking`, when supplied contribution identities or hierarchy are insufficient. Included rows follow [argument-architecture.md](argument-architecture.md), use a positive integer, `Co-primary`, or `Unclear` rank, and have supplied identity anchors. Editorial candidate ranks remain outside the factual ledger.

## Compile, render, and diff closure

Compilation during the atomic pass records baseline documentary evidence such as unresolved labels, layout warnings, and visible rendering facts. It does not validate the argument. Bind every compile, render, or diff file under `artifacts/`; an input, protocol snapshot, canonical JSON record, or report is not closure evidence.

For audit-and-revise, complete diagnosis, reporting, contribution resolution, and baseline compile or render evidence before editing. Then run:

    python "AUDIT_DIR/protocol/scripts/writer_audit.py" freeze --audit-root "AUDIT_DIR" --json

`DIAGNOSIS_FREEZE.json` binds pre-edit findings, checkpoints, and baseline evidence. After it exists, do not change `FINDINGS.json` or completed diagnostic checkpoints. Record only authorized edits, one disposition for every frozen finding, post-edit compile or render evidence when edits were applied, and REVISION_CLOSURE. Audit-only work neither creates nor accepts this freeze.

After edits:

1. repeat affected atomic and formal-object checks;
2. compare source and revision for protected tokens, claims, and documentary links;
3. recheck affected local through paper-level contracts;
4. compile or render when a suitable toolchain is available and inspect the affected output;
5. record a reviewable diff or explain why no diff applies.

A failed compile or render keeps the audit nonfinal. A not-run or unavailable check needs a substantive reason. Applied edits require post_edit compile and render records plus a hash-bound diff artifact. With no applied edit, retain the frozen baseline records.

Resolve every frozen finding after the freeze. Mark Material and Local findings applied or unapplied with a reason. Findings requiring author input, encoded with canonical priority `Blocking`, may remain unresolved with a reason. Dispositions must cover the frozen findings exactly, and the final report exposes each outcome. A safe finding with an unexplained no-op is nonfinal.

## Check and publish

Validate without publication:

    python "AUDIT_DIR/protocol/scripts/writer_audit.py" check --audit-root "AUDIT_DIR" --json

After all errors are resolved, publish:

    python "AUDIT_DIR/protocol/scripts/writer_audit.py" check --audit-root "AUDIT_DIR" --publish --json

The checker verifies snapshots, protocol bindings, scope, pass coverage, findings, anchors, contribution resolution, freeze status, repair dispositions, phase-specific closure evidence, and forbidden characters. It renders `FINAL_REPORT.md` from canonical state and publishes `FINALIZATION.json` last as the commit marker.

Publication never overwrites different existing bytes. Identical bytes may be accepted idempotently. If interruption leaves an identical report without a receipt, status remains resumable and nonfinal; a conflicting orphan report fails status. Do not hand-edit the report. Change canonical state, recheck, and publish only when no conflicting final artifact exists.
