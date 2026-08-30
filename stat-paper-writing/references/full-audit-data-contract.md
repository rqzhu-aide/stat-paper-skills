# Full-Audit Data Contract

## Purpose

Use only when editing canonical full-audit JSON. It gives the exact shapes and statuses accepted by the snapshotted harness. Do not load for initialization, orientation, status, or a completed report.

## File ownership

The initializer owns AUDIT_MANIFEST.json, ORIGIN.json, inputs/, and protocol/; do not edit them. The author may update AUDIT_STATE.json and FINDINGS.json and place bound evidence or diffs only under artifacts/. The harness owns DIAGNOSIS_FREEZE.json, FINAL_REPORT.md, and FINALIZATION.json; create them only through freeze or check. Never hand-edit them.

Do not change JSON keys, schema_version, bindings, pass tags, kinds, requirements, or order. Use JSON null, true, and false, not strings.

## AUDIT_STATE.json

### Pass records

Each existing item in passes has exactly this shape:

    {
      "tag": "PASS_TAG",
      "kind": "descriptive or evaluative",
      "requirement": "required, conditional, or not_required",
      "status": "pending, completed, or not_required",
      "binding_sha256": "the initialized binding",
      "loaded_references": ["references/example.md"],
      "checkpoint": "A compact source-bound completion record.",
      "reason": null
    }

Do not reorder, insert, or delete pass records. A completed record needs every actually loaded protocol reference, a nonempty checkpoint, and null reason. A not_required record is allowed only for a conditional or not_required requirement and needs no references, null checkpoint, and a substantive reason. A required pass cannot be skipped, and no selected pass may remain pending at final check.

Completed ORIENTATION must use exactly:

    ["references/revision-audit.md"]

For an audit-only run, the initialized REVISION_CLOSURE record is declared not_required and must remain unchanged. For audit-and-revise, REVISION_CLOSURE remains pending until diagnosis is frozen and the authorized revision is closed.

### Reporting record

The reporting object has exactly:

    {
      "status": "pending or completed",
      "binding_sha256": "the initialized binding",
      "loaded_references": [],
      "checkpoint": null
    }

At completion, keep the binding, set status to completed, use loaded_references in this exact order, and record a nonempty checkpoint:

    ["references/reporting-and-validation.md", "references/full-audit-operations.md", "references/full-audit-data-contract.md"]

### Compile and render closure

The compile and render records each have exactly:

    {
      "phase": "audit, baseline, or post_edit",
      "status": null,
      "evidence": null,
      "artifact": null
    }

Allowed compile statuses are passed, failed, not_run, and unavailable. Allowed render statuses are inspected, failed, not_run, and unavailable. Every resolved status needs substantive evidence; failed prevents finalization.

Use phase audit for an audit-only run. For audit-and-revise, use baseline through the diagnosis freeze. If any manuscript edit is applied, replace both records with post_edit evidence before finalization. If no edit is applied, retain the bound baseline records.

Compile passed and render inspected require a bound artifact. not_run or unavailable requires a substantive reason and null artifact.

A bound artifact has exactly:

    {
      "path": "artifacts/relative-file-name",
      "sha256": "64 lowercase hexadecimal characters"
    }

The path must start with artifacts/ and be a canonical POSIX-style relative path to a real file inside that directory. Inputs, protocol snapshots, canonical JSON, and reports cannot serve as closure evidence. Use forward slashes only. Do not use backslashes, drive-relative or absolute paths, empty or dot components, or traversal. Record the hash of those exact bytes.

### Edit and diff closure

The edits record has exactly:

    {
      "applied": null,
      "diff_status": null,
      "evidence": null,
      "artifact": null,
      "finding_dispositions": null
    }

Allowed diff_status values are changed, clean, not_applicable, and unavailable.

For audit-only, retain the initialized values:

    {
      "applied": false,
      "diff_status": "not_applicable",
      "evidence": "Audit-only run; no manuscript files were changed.",
      "artifact": null,
      "finding_dispositions": []
    }

For audit-and-revise, leave every edits value null until after diagnosis is frozen.

After the freeze:

- applied true requires diff_status changed, substantive evidence, a bound diff artifact, and post_edit compile and render records;
- applied false cannot use diff_status changed, requires substantive evidence, uses null artifact, and retains baseline compile and render records;
- replace finding_dispositions with one canonical record for every frozen finding.

Each disposition has exactly:

    {
      "finding_id": "F-001",
      "outcome": "applied, unapplied, or unresolved",
      "reason": "A substantive post-freeze disposition."
    }

Disposition IDs uniquely cover all findings in numerical order. Material and Local use applied or unapplied; Blocking may also use unresolved. Every outcome needs a substantive reason. Any applied outcome requires applied true; none requires applied false. An unapplied safe finding must say why the repair was not taken.

## FINDINGS.json

Preserve schema_version and semantic_binding_sha256.

### Assessment

The assessment object has exactly:

    {
      "status": "findings_recorded or no_consequential_findings",
      "boundary": "The completed author-side assessment boundary."
    }

findings_recorded requires findings; no_consequential_findings requires none. Null status or boundary is not final.

### Source anchors

Use the source_id and bounds recorded in AUDIT_MANIFEST.json.

For a text source:

    {
      "source_id": "SRC-001",
      "kind": "line",
      "start": 12,
      "end": 14,
      "locator": null
    }

For a PDF source:

    {
      "source_id": "SRC-002",
      "kind": "page",
      "start": 3,
      "end": 3,
      "locator": null
    }

For an image or other artifact:

    {
      "source_id": "SRC-003",
      "kind": "artifact",
      "start": null,
      "end": null,
      "locator": "panel A, upper-left legend"
    }

Line and page bounds are inclusive positive integers with start less than or equal to end. Artifact locators must identify a substantive visible or file-local location.

### Finding records

Each item in findings has exactly:

    {
      "id": "F-001",
      "priority": "Blocking, Material, or Local",
      "title": "Concise finding title",
      "anchors": [],
      "observed_evidence": "Literal supplied manuscript fact or pattern.",
      "inferred_consequence": null,
      "unverified_dependency": null,
      "author_question": null,
      "revision_direction": "Specific editorial direction.",
      "remedy_type": "one allowed remedy",
      "safe_repair_available": true
    }

`Blocking` is the legacy canonical JSON encoding for the user-facing priority **Author input required**. Write `Blocking` in FINDINGS.json and in `blocking_finding_ids`; the harness renders **Author input required** in the final report. `Author input required` is not an allowed JSON enum value.

IDs must be unique and match F- followed by three to nine digits. Every finding needs at least one valid anchor. title, observed_evidence, and revision_direction must be nonempty.

Allowed remedy_type values are safe_prose_edit, safe_presentation_edit, author_decision, and additional_support.

Apply the field relations from [reporting-and-validation.md](reporting-and-validation.md):

- Blocking requires inferred_consequence, unverified_dependency, a self-contained author_question ending in ?, safe_repair_available false, and author_decision or additional_support. The question needs at least eight words, must name the unresolved object or choice, and cannot substitute bare this, that, it, these, those, or them.
- Material requires inferred_consequence, null dependency and question, safe_repair_available true, and a safe edit remedy.
- Local requires null dependency and question, safe_repair_available true, and a safe edit remedy; consequence may be null unless requested for every finding.

### Contribution ledger

contribution_ledger has exactly:

    {
      "status": null,
      "reason": null,
      "blocking_finding_ids": [],
      "rows": []
    }

Resolve status as included, not_needed, or unavailable.

included requires null reason, no blocking IDs, at least one row, and supplied identity anchors for every row.

Each included row has exactly:

    {
      "identity_anchors": [],
      "cells": {
        "Rank": "1, Co-primary, or Unclear as supplied",
        "Contribution": "Exact supplied contribution identity",
        "Method object or construction": "Supplied object or Missing",
        "Formal support": "Supplied support, Missing, Unclear, or Not claimed",
        "Empirical support": "Supplied support, Missing, Unclear, or Not claimed",
        "Boundary": "Supplied boundary, Missing, Unclear, or Not claimed"
      }
    }

Do not change the six cell keys or their order in the rendered ledger.

For not_needed, use a substantive reason, no blocking IDs, and no rows.

For unavailable, use a substantive reason, no rows, and cite at least one existing Blocking finding ID in blocking_finding_ids. Each cited finding must have Blocking priority.

If CONTRIBUTION_LEDGER was unselected or marked not_required, use not_needed.

## Audit-and-revise order

Before editing, complete every selected diagnostic pass, resolve assessment, findings, contribution ledger, reporting, and baseline compile/render records, then run freeze.

After DIAGNOSIS_FREEZE.json exists, do not alter FINDINGS.json, completed diagnostic pass records, or reporting. Record only authorized edits, finding dispositions, post-edit compile or render evidence when edits were applied, edit or diff closure, and REVISION_CLOSURE.

## Final checks

Run status while work is incomplete and check when every selected field is resolved. Use check with publish only after validation succeeds.

The checker rejects extra keys, malformed scalar types, invalid enums, noncanonical or escaping artifact paths, hash drift, out-of-range anchors, unexplained repair dispositions, unresolved required fields, and inconsistent priority or remedy combinations. It rejects U+2013 and U+2014 only in assistant-authored pass or reporting checkpoints and reasons, closure evidence and disposition reasons, assessment boundaries, finding titles, consequences, dependencies, questions, revision directions, and ledger reasons. It permits them in source-derived observed evidence, locators, contribution-ledger cells, source metadata, focus text, source snapshots, and bound artifacts.

Publication deterministically creates FINAL_REPORT.md and writes FINALIZATION.json last. If either existing file has different bytes, publication fails rather than overwriting it.
