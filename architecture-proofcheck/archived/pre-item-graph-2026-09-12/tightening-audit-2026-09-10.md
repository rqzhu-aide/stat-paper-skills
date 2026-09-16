# Proofcheck: remaining targeted repairs

Audited on 10 September 2026, after the package cleanup. This document records
the findings before repair. No skill, installed package, or real manuscript
was changed by the audit. The subsequent implementation and verification are
recorded in the [release status](tightening-release-2026-09-10/STATUS.md).

The current installation matches the 191-file runtime package. Its doctor,
status, and delivery checks pass; the bundled reference is FINAL, current,
and usable. The architecture does not need another expansion. Five concrete
repairs are justified by the reproductions below, with the first four more
important than the final drafting convenience.

| Repair | Reader or checker consequence | Smallest useful change |
|---|---|---|
| Preserve uncertainty throughout the report | An unresolved concern can be called a failed inference in its detail view. | Derive every path label from the recorded finding classification. |
| Keep repair directions attached to their findings | Separate remedies can appear interchangeable in the opening summary. | Use neutral directions with their own targets, costs, and verification state. |
| Disambiguate generated theorem identities early | A multi-file paper can pass setup and immediately produce an unusable audit. | Resolve generated filename collisions before constructing inventory lookups. |
| Diagnose inactive TeX source before scope selection | Abandoned or excluded text can create extra proof obligations without a warning. | Recognize literal source-selection controls or raise a precise early diagnostic. |
| Allow source lookup while drafting | A checker cannot inspect a known step until unrelated review fields are finished. | Validate source selection structurally, leaving full checks at submission. |

**1. Uncertainty becomes failure language in the proof path.**

The opening summary correctly calls an inconclusive finding inconclusive.
However, the detail path gives its origin the unconditional role `Failed
inference`, with the link `Why this inference fails and how to repair it`.
A synthetic report-layer probe using the legitimate combination
`finding_status: inconclusive`, `invalidation_kind: scope_inconclusive`, and
an `unclear` step reproduced an `Unclear` badge next to that failure claim.
This is stronger language than the recorded judgment supports.

Relevant code: path roles, explanation links, and source-link labels in the
[report renderer](../stat-paper-proofcheck/scripts/proofcheck_report.py).

Use the recorded classification consistently for the path heading, node role,
source link, and explanation link. Confirmed failure wording may remain for
confirmed defects; unresolved and presentation findings need neutral wording.
Resolved findings must remain historical. Test the actual detail path and its
HTML, including mixed findings, rather than only the opening summary labels.

**2. Separate issues' repairs are joined as alternatives.**

The summary pools all active issues' repairs by their cost and verification
status, then joins them using `or` under `Recorded alternatives`. The probe
supplied two distinct findings, different source locations and result targets,
and a separate repair for each. The opening still described their costs as
alternatives. Neither common cost categories nor appearance in the same
report establishes that one remedy substitutes for another.

Relevant code: summary aggregation and repair wording in the
[report renderer](../stat-paper-proofcheck/scripts/proofcheck_report.py).

Present neutral, linked repair directions. Keep the finding and target attached
to each direction, together with its cost and verification state. Do not infer
mutual exclusivity, interchangeability, or joint sufficiency from a list of
suggestions. This needs no new repair schema or authored report record. Test
two independent issues as well as several suggestions for one issue, and
retain the existing distinction between a candidate, verified support, and an
applied or resolved repair.

**3. Unlabeled theorems in different folders can collide.**

Two complete theorem/proof pairs in `a/result.tex` and `b/result.tex`, each
starting at line 1 without an explicit label, both receive
`theorem:result.tex:1`. The source helper reports `no_layout_flags`; doctor
passes; scaffold succeeds. The first status call then fails with
`Proof-unit inventory needs unique nonempty unit IDs` and reports the audit
as malformed. The later validation refuses it correctly, but the setup has
already created an unusable workspace.

Relevant code: inventory fallback in the
[validator](../stat-paper-proofcheck/scripts/proofcheck.py) and the
[early source-check decision](../stat-paper-proofcheck/scripts/proofcheck_source_check.py).

Disambiguate generated collisions with project-relative source identity before
building ID-indexed lookups. Keep existing unambiguous IDs stable, and retain
errors for duplicate explicit manuscript labels. Report any remaining collision
early with both source locations. Test doctor/source-check/scaffold/status on
the multi-file case and ensure the resulting two units remain distinct after
portable relocation. Do not silently renumber existing reviewed records.

**4. Inactive source is treated as ordinary manuscript content.**

Two generic cases reproduced this: a complete abandoned theorem after literal
`\end{document}`, and an unused chapter excluded by literal
`\includeonly{live}`. In each case the helper inventories both the live and
inactive theorem with ordinary proof associations, zero warnings, and
`no_layout_flags`. This can produce unnecessary review work or findings about
material outside the intended manuscript. The required manual inventory review
remains a safeguard; these probes do not demonstrate a false FINAL judgment.

Relevant code: structural masking and include discovery in the
[validator](../stat-paper-proofcheck/scripts/proofcheck.py).

Recognize these literal controls sufficiently to mask clearly inactive text
while preserving physical line positions, or give a specific early
source-selection diagnostic. For `\includeonly`, establish whether the audit
targets the selected build or the full manuscript instead of silently deciding
its scope. Ignore apparent controls inside comments, verbatim text, definitions,
and inactive conditional branches. Keep original source bytes locked and
supplement selection explicit. A TeX execution engine is unnecessary.

**5. Read-only lookup requires completed review fields.**

`source-lookup --step-key` invokes the full semantic step planner. A fresh
annotation scaffold therefore fails with `steps[1].mode is invalid`. Even a
completed requested step cannot be inspected when an unrelated step has an
unfinished goal. Missing `source_groups` also raises an uncaught `KeyError`.
Direct line lookup remains a workaround, and no mathematical judgment is
accepted incorrectly by this behavior.

Relevant code: [source lookup](../stat-paper-proofcheck/scripts/proofcheck_authoring.py).

For this read-only operation, validate source/obligation bindings, unique keys,
grouping, ranges, and ordering without requiring judgments or explanations to
be complete. Missing structural fields should produce a concise input error.
Keep full validation unchanged in compilation and submission. Test fresh
scaffolds, unrelated unfinished steps, and malformed structure, and verify
that lookup writes no canonical records.

**Verification and boundaries.**

The installed read-only checks took approximately 0.48 seconds for doctor,
1.67 seconds for status, and 1.21 seconds for delivery on the small reference.
They left installed file hashes unchanged. These timings describe small
deterministic commands, not mathematical-review speed.

All 43 targeted submission, reconciliation, transaction-publication, and
workflow-efficiency tests passed in 66.25 seconds. The source findings were
reproduced through ordinary CLI commands on generic LaTeX fixtures. The reader
findings were reproduced through the actual renderer functions using synthetic
projection records with legitimate shapes and statuses; they are not newly
completed or mathematically reviewed audits. No full test suite or new paper
audit was run. This review established no additional stale-evidence acceptance
or transaction-preservation failure in the inspected paths.

Detailed probes and outputs are local-only under
`archived/proofcheck/tightening-audit-2026-09-10/`: `runtime-receipt.json`,
`reader/results.json`, `source/results.json`, `source/workflow.json`, and
`workflow/lookup-repro.json`. They are excluded from Git and installation.

The release-evaluation corpus still explicitly marks its candidate keys as
pending independent expert review. Software regression tests and the above
checks do not establish research-level mathematical reliability. That remains
an evaluation task, not a reason to add more bookkeeping gates to paper audits.

Implement these as focused repairs with the existing generic tests and release
renewal procedure. Preserve the current evidence contracts, independent review,
source freshness, compact HTML report, and separation of runtime/development
material. No architecture redesign or additional model stage is warranted.
