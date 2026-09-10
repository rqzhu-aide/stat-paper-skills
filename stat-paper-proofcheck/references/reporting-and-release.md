# Reporting and Release

Canonical JSON owns the mathematical judgments. New reader reports are `proofcheck-report.html` beside `AUDIT_MANIFEST.json`, inside the audit folder. Existing audits retain their declared path, including `audit/06_reports/FINAL_REPORT.html`, until explicit migration. The graph, results, findings, repairs, source excerpts, and scope describe the same snapshot. Rendering requires no model call or network service.

## Working reports

For a new HTML audit, generate a working view at any checkpoint:

```bash
python "<skill-root>/scripts/proofcheck.py" report --root "<audit-root>"
```

An unfinished or changed audit produces a NONFINAL view. It counts expected units from the declared scope or identifies unresolved scope. Missing, malformed, or unchecked records remain visible. An empty issue list never establishes a clean audit. On an unchanged current FINAL audit, `report` returns the existing deliverable and `checkpoint` returns current state without rewriting durable files; repeated `finalize` preserves those bytes.

The graph starts with a Paper overview: one group per source-identified manuscript result in the recorded audit scope. It shows the complete overview when readable; bounded pages disclose omitted results and connections and retain access to every recorded dependency. Grouping is a reading view, not a new whole-theorem verdict. Mixed outcomes, unresolved conclusion coverage, and problems in associated assertions remain qualified in group summaries. Full statements come from the current source snapshot; fallback passages are explicitly labeled incomplete. No new authoring record or model call is required.

Open a group for its individual conclusions, or switch to Detailed proof for the existing exact graph. Returning to the overview retains the selected manuscript result. Grouped arrows expose their exact contributing uses, consumed forms, conditions, and source/target links. In the detailed view, premises enter an argument jointly, and written and supplemental arguments remain separate routes. A failed argument does not automatically refute its statement or downstream results; only exact-target evidence has a refutation arrow. Native result groups and technical evidence start collapsed, open when targeted, and remain available without scripting.

Node colors identify mathematical types, with neutral judgment text. Red, green, and yellow belong to connections and matching arrowheads: failed, checked, or unresolved/conditional use. Gray identifies explicit givens. Hover or keyboard focus previews the statement, conditions, judgments, and location; touch can pin the preview and open details. Selection never changes a node's type color. No essential finding belongs only in a preview.

An accepted supplement can establish the unchanged statement while the written argument retains a gap or invalidity. A restricted supplement instead appears as a separate form with its additional conditions; it has no support arrow to the unrestricted statement. A later application uses that form only when the canonical dependency record explicitly selects it and checks its conditions. The original lemma's broader defect remains visible. Pending supplemental review is displayed as pending support. This records reviewer evidence, not a completed manuscript edit.

Essential claims, findings, repairs, source excerpts, scope, and the non-formal boundary remain readable without JavaScript and in print. The script only improves navigation. LaTeX formulas are converted to static MathML during report generation using the shared `latex2mathml` Python package, so the delivered HTML needs no network service, fonts, or math JavaScript.

Write formulas in authored mathematical prose with `$...$` or `\(...\)` for inline math, and `$$...$$` or `\[...\]` for display math. Preserve exact notation and conditions; do not turn formula display into a new mathematical transcription. Unknown commands or malformed expressions retain visibly labeled literal TeX. The converter does not execute TeX or expand manuscript macros. Install the package once in the shared interpreter used for proofcheck, for example `py -3.14 -m pip install --user latex2mathml` on Windows. A missing converter is reported explicitly; it is not silently downloaded.

Historical normalized claims can contain ASCII shorthand rather than delimited LaTeX. For these, the report offers a typeset reading view from that conclusion's locked source spans, keeping the normalized wording in a disclosure. It does not invent backslashes or infer a replacement formula. Exact numbered source remains alongside its typeset reading view. The compact graph remains a navigation overview; complete typeset statements are in the linked result details.

## Canonical report context

Keep judgments, scope, counts, dependencies, and repairs in their canonical records. Optional `report_context` holds authored `title`, `essential_scope`, `limitations`, `confidence`, `confidence_rationale`, and `notes`. Limitations and notes are string lists; other fields are strings. Use `essential_scope` for one concise sentence beside the main judgment when a qualification is decisive, such as a separately assumed Gaussian approximation, fixed grid, or algorithmic target. Retain full limitations below and a reason for authored confidence. Do not infer a stronger judgment or a preferred repair from presentation order.

Additional or legacy context is displayed separately as authored or historical prose, including names resembling canonical scope fields. It cannot overwrite a reviewed fact. The assurance checks apply to authored assertions before either HTML or Markdown publication; formatting a claim as code does not exempt it. Literal locked-source quotations remain attributed evidence.

Result details preserve the selected support reasoning, conclusion-specific initial review and source anchors, and portable response/reconciliation links. Technical records and normalized wording start collapsed, remain available without JavaScript, and expand for print. Historical responses that omitted a judgment dimension say so. Resolved findings show the original failure as historical beside the actual resolution, current mapping, and completed rechecks. Source provenance appears with scope and evidence. These details do not lengthen the four-item overview.

The four summary items are overall finding, key issues, impact, and repair
outlook. Generate them from the existing reviewed records and manuscript
groups; do not author a second summary or repeat mathematical review for
presentation. Feature at most three active findings with existing paper and
evidence links, disclose additional findings, and count resolved history
separately. Preserve a short finding's complete explanation; long explanations
remain linked in full so a shortened excerpt cannot discard qualifications.

Count affected manuscript results separately from their individual conclusions
and associated assertions. Grouping supplies no whole-theorem verdict. Keep
written proof defects, exact statement refutations, conditional or unavailable
support, and accepted supplements distinct. Describe repair directions and
scientific costs from the recorded options, without preferring the first one.
A candidate or locally inspected repair is not verified sufficient; verified
support does not mean the manuscript was edited or the issue resolved. A
failed bounded search does not establish that no local repair exists.

Keep each repair direction attached to its finding and target. A list of
suggestions does not establish that they are interchangeable alternatives.
Use the same recorded finding classification in path headings, source links,
and explanation links; an inconclusive concern must not become a confirmed
failed inference in its detail view.

Distinguish release state from mathematical assessment. NONFINAL means no
overall judgment is released; report known incomplete checks or unavailable
evidence without guessing the remaining cause. Complete local counts alone
cannot establish publication-only readiness. Unknown scope stays unknown,
and an empty issue list cannot establish a clean audit. Keep the opening
compact, with complete reasons, qualifications, and rechecks in linked details.

Reader labels use authenticated literal headings, source titles, or reviewed
PDF numbering through optional `report_context.manuscript_labels`; see
[manuscript label review](manuscript-labels.md) for its small schema and checks.
Never infer numbers from audit IDs, inventory order, or LaTeX counters. Stale
or conflicting PDF labels fall back to independent literal headings or
descriptive source locations, with a display note, not a proof defect. For reviewed PDF
transcriptions, explicit sequential `[PDF page 1; journal page 60]` or
`[PDF page 1]` markers can supply the paper page; exact transcription file
and lines remain in the result details. Missing or ambiguous mappings keep
the original file-and-line locator.

Give distinct conclusions a short, faithful `reader_description` in their
canonical obligation when useful, such as "Lower-tail probability bound"
and "Exponential comparison". This is an authored navigation caption, not
a manuscript title or a replacement for the complete mathematical claim.
Keep it within 120 characters on one line; avoid audit IDs and invented
numbering. Coincident captions without descriptions fall back to exact
claim previews. Audit IDs, JSON pointers, and exact normalized records
remain in technical disclosures. Source links identify their role, such as
the statement, premise, failed inference, citation, or downstream use.

An unnumbered LaTeX environment is presented as an unnumbered result; its
trailing `*` remains source metadata. A separately normalized assertion outside
the formal statement keeps its own descriptive conclusion caption. For original
LaTeX with an actually reviewed PDF, the existing `reader_description` may also
name a verified equation and PDF page, with that review recorded in source or
normalization evidence. This remains an authored navigation caption. Do not
insert transcription markers into the original TeX or infer a page from its
line number; exact file/line coordinates remain available.

Each current finding can expose a short source-located path from its actual
premise through the failed move to the affected result and recorded dependent
use. These connections come from canonical premise and dependency records,
not proximity in the paper. Repair targets link back to the affected result.
Multiple conclusions stay distinct; missing evidence remains unavailable,
and historical failure paths remain labeled historical. Included-source
locations use original physical lines, never internal coverage positions.

## Finalize and deliver

Complete the mathematical work and coordinator checkpoint, then run:

```bash
python "<skill-root>/scripts/proofcheck.py" checkpoint --root "<audit-root>" --clear-active-unit --next-action "Run final issue reconciliation and finalization."
python "<skill-root>/scripts/proofcheck.py" issues --root "<audit-root>" --write-summary --final
python "<skill-root>/scripts/proofcheck.py" finalize --root "<audit-root>"
python "<skill-root>/scripts/proofcheck.py" delivery-check --root "<audit-root>"
```

For HTML audits, `finalize` first checks source, scope, atomic evidence, dependencies, issues, independent review, and completion. It fixes the snapshot time, derives the report, validates the exact visible output, and publishes the report, updated manifest/progress, and finalization record together. Failed publication restores the previous files. An interrupted mixed state cannot pass the read-only delivery check.

Deliver only when `delivery_status` is `FINAL` and `usable_finalization` is true. A completed audit may contain defects or an inconclusive mathematical assessment. A saved HTML file describes the snapshot finalized at its recorded time; current workspace freshness is checked separately.

The manifest's `report_contract` records version 2, the preferred HTML path, optional Markdown export, and renderer identity. `report_release` records the release state, snapshot time, and projection digest. Output hashes belong in `report_deliverables`; the report never embeds a finalization hash that would depend on its own bytes. HTML and its generated Markdown export share report group `R001`, with distinct paths and byte hashes. Adding an export does not add a mathematical reconciliation obligation. Do not modify a sealed report to add a badge.

Report-only changes require rendering and resealing. The renderer identity includes the math adapter and converter version, configuration, and package resources. Installing or changing the converter requires regenerating and resealing the presentation, without repeating unchanged mathematical review. Changes to the mathematical validator or evidence require the existing relevance and revalidation checks. Renderer identity is separate and is not an exemption for mathematical changes.

An older graph needs regeneration to obtain the current compact cards and
mathematical previews. A renderer mismatch alone does not invalidate unchanged
mathematical evidence, but delivery remains NONFINAL until report renewal and
the applicable checks pass. Source and review links resolve from the declared
HTML location; do not move a sealed HTML file manually.

For deliberate repairs or an unfinished alternative report, work in a copy of the delivered audit. Preserve the original as historical evidence, then use the existing archive, repair/recheck, and finalize workflow in the copy. Actual source or evidence changes remain NONFINAL until renewed. Archiving an issue preserves its origin; it does not resolve the defect by itself.

## Existing report locations and legacy Markdown audits

To move an existing HTML report to the audit root, work in a preserved copy and
run `migrate-report --root "<audit-root>" --top-level`, then `finalize` and
`delivery-check`. The old manifest, report, and seal remain in
`audit/06_reports/history/report-location-<identity>/`. The manifest declares one
authoritative reader report; migration creates an honest NONFINAL view first.

Legacy audits without `report_contract` retain their original report checks. Their exact format and generation procedure are in [legacy-markdown-report.md](legacy-markdown-report.md).

To migrate presentation explicitly:

```bash
python "<skill-root>/scripts/proofcheck.py" migrate-report --root "<audit-root>"
python "<skill-root>/scripts/proofcheck.py" finalize --root "<audit-root>"
python "<skill-root>/scripts/proofcheck.py" delivery-check --root "<audit-root>"
```

Migration preserves the original manifest, report, and finalization bytes under `audit/06_reports/history/report-v1-<identity>/`. It retains an existing Markdown report as a generated secondary export and makes HTML primary. New audits default to HTML only. Migration preserves authored scope/confidence/limitation prose as report context. It does not rewrite mathematical judgments, calibration, challenge records, or old finalization history to make stale evidence appear current.

A migration initially creates a NONFINAL working report. History, active declarations, and generated reports are published in one transaction; a failed publication restores the previous files. Stale mathematical records still require the normal revalidation/review process before finalization.

## Scope of assurance

Prefer "no load-bearing defect found under the stated non-formal protocol" to an unqualified claim that the paper is correct. Keep contract fidelity, argument validity, statement status, dependency availability, and use-site sufficiency distinct. Neither deterministic validation nor agreement between reviewers is a formal proof certificate.

Maintainers evaluate release behavior separately using [release-evaluation.md](release-evaluation.md). The supplied corpus and offline harness support blinded comparisons and observed usage, but the provisional keys still require independent expert review. Their software tests do not measure mathematical reliability.
