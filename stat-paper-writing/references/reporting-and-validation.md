# Audit Reporting and Validation

## Purpose

Use this contract to report any writing audit or close an authorized revision. It owns priorities, remedies, author questions, safe-repair status, provenance, deterministic full-audit publication, and final validation.

It does not assess proof validity, source truth, code behavior, numerical correctness, novelty, or scientific merit.

## Finding contract

Report only consequential findings by default. Inspection order and reporting order are distinct: inspect in the required order, then report by consequence unless the user requests a pass log.

Use only these user-facing priorities:

- **Author input required:** a safe repair requires an author decision, missing context, source support, mathematical or numerical verification, or confirmation of the intended formal object.
- **Material:** the issue substantially affects interpretation, documentary consistency, or paper-level presentation, but the supplied record supports a repair now.
- **Local:** the supplied record supports a bounded presentation repair now.

For Full audit compatibility, encode **Author input required** as the canonical JSON priority value `Blocking`. The harness renders the user-facing label. Do not use `Blocking` as the displayed priority in prose reports.

For each prioritized finding, record:

- stable finding ID for a full audit;
- priority and concise title;
- exact location or source anchor;
- **Observed evidence:** with the literal manuscript fact or recurring pattern;
- **Inferred consequence:** for every Author input required or Material finding, and for a Local finding when the requested contract asks for a consequence for every finding;
- **Unverified dependency:** whenever the issue cannot be resolved from supplied material;
- a direct, self-contained author question when an Unverified dependency concerns an intended author choice;
- revision direction;
- remedy type;
- **Safe repair available now:** yes or no.

Use safe_prose_edit for wording, safe_presentation_edit for supported structural or documentary changes, author_decision for intended-content choices, and additional_support for missing evidence or context.

Apply these relations exactly:

- Every Unverified dependency is Author input required, includes an Inferred consequence and self-contained author question, and has no safe repair now.
- Every Author input required finding contains an Unverified dependency.
- Material and Local findings contain no unresolved dependency and have a supported repair now.
- A safe bounded repair is Local unless its reader-facing effect is genuinely nonlocal.
- Do not present an Inferred consequence as direct manuscript evidence or an Unverified dependency as an established error.

Keep each author question locally self-contained. Repeat the unresolved object or relation rather than using a bare this, that, it, these, or them when more than one dependency could be in scope.

If no consequential findings remain after the required scope is complete, state that result explicitly together with the assessment boundary. An empty report is not evidence of completion.

## Contribution reporting

Use [argument-architecture.md](argument-architecture.md) as the sole owner of contribution identity, hierarchy, and ledger columns. Do not create a contribution row for an unnamed contribution. Include the ledger only when it materially clarifies the narrative or the user requests it.

## Quick and section audits

Do not initialize the full-audit harness. A compact report may use prose rather than a table, but preserve the finding contract above.

State the assessment boundary once. Do not repeat under every finding that proof validity, source verification, code behavior, or numerical correctness was outside scope.

Do not rewrite the manuscript unless revision was requested. For combined audit and revision, record findings before edits. Freeze only a Full audit through its harness.

## Full audits

For a Full audit, also load [full-audit-operations.md](full-audit-operations.md). It owns workspace setup, pass state, freeze, closure, deterministic publication, and interruption recovery. Keep those operations out of quick and section audit context.

## Final response closure

Before returning any writing result:

- keep Unicode U+2013 and U+2014 out of assistant-authored commentary and the canonical prose fields classified as assistant-authored by the full-audit data contract;
- preserve either character in supplied or revised manuscript text, stated venue typography, source-derived observed evidence, locators, contribution-ledger cells, and supplied metadata;
- preserve exact mathematical and documentary tokens;
- state compile or render limitations when relevant;
- distinguish supplied or attributed validation from work actually performed;
- never claim mathematical, source, code, numerical, novelty, or scientific validation that this skill did not perform.
