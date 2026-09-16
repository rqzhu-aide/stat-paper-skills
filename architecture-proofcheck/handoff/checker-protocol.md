# Pilot checker protocol

Protocol version: `item-audit/1`. This is the initial instruction contract for P3/P4. The maintained [installed protocol](../../stat-paper-proofcheck/references/checker-protocol.md) and [controller workflow](../../stat-paper-proofcheck/references/controller-workflow.md) contain the implemented assignment and submission instructions, including subsequent pilot corrections. This document remains the original design reference; it is not a proof certificate.

## Coordinator

Start from the requested audit scope, captured sources, and major-item inventory. Distinguish declarations, assumptions, definitions with well-posedness claims, locally proved results, and external restatements. Review source-selection limitations before assigning mathematical work. Locate complete statement/proof passages, including supplements and relevant macros.

Register a draft argument for each in-scope written route. Expose intermediate nodes for meaningful bounds, events, constructions, reductions, limits, disputed assertions, or reusable checkpoints. Use source coverage for headings and structural text. Several routine algebraic lines can belong to one meaningful derivation. Add a node when it gives a useful assertion, scope boundary, reusable result, or review checkpoint, not merely because a new source line exists.

Schedule ready obligations from prerequisites toward the target. A local derivation can be examined under declared premises before a supplier's full audit finishes; label its support conditional. Do not call the theorem established on that basis. If a checker discovers a missing prerequisite or scope distinction, save the discovery, refine the graph, and revisit affected obligations. Extraction is not assumed perfect or permanently frozen.

Assign one bounded argument or coherent subsection at a time. Supply the primary packet, exact target, allowed operations, and expected saved output. Do not require every role to reread the whole paper. Keep enough surrounding definitions, source context, and full quantifiers to make the bounded assignment valid. Split long proofs only at meaningful claims and retain an explicit final integration task.

After an informative derivation, identified defect, or unresolved obstacle, save it. Before yielding or changing target, save reasoning, examined evidence, remaining questions, and next action as a draft. A valid partial save must not depend on complete proof coverage, all findings being resolved, or final report publication. Regenerate working reports at meaningful checkpoints.

For independent review submission, the coordinator writes `SUBMISSION.json` using the exact envelope in [record-contract section 5.1](record-contract.md#51-worker-response-and-coordinator-submission). Supply reviewer identity, qualification, and exposure assessment from the actual dispatch. Pass the independent worker's `RESPONSE.json` as unchanged bytes with `review submit DB --submission SUBMISSION.json --response RESPONSE.json`. Do not rewrite or wrap judgments inside the worker file; preserve the response before opening reconciliation.

## Primary checker

Read the source and target packet. First verify the recorded statement and the actual proof route against the manuscript. Preserve hypotheses, quantifiers, conditioning, dimensions, constants, rates, and the exact target. Record source fidelity separately from mathematical correctness.

For each local inference, ask the following compact checklist. It is a reading/checking guide, not eight mandatory stored rows.

| Concern | Question to resolve where relevant |
|---|---|
| Objects and scope | Are all quantities defined and well posed? Which variables are fixed, random, universally quantified, or existential? Which assumptions and local conditions are active? |
| Imported result | Does the actual supplier statement provide the form used, for these parameters, hypotheses, and domain? Is the proof borrowing a statement or an internal argument? |
| Algebra and bounds | Are signs, dimensions, inequalities, constants, normalizations, and rate comparisons correct? Are denominators/nonempty sets/extrema justified? |
| Probability | Is the event pointwise or uniform? Are conditioning, dependence, union bounds, failure allocations, and probability limits valid? |
| Limits and regularity | Are limit/interchange, convergence mode, measurability, compactness, differentiability, or integrability conditions supplied where needed? |
| Joint reasoning | Do all required inputs hold together? Are cases exhaustive? Is an existence statement being treated as a uniform construction? |
| Scope exit | Does the inference legitimately discharge its local assumption or fixed-point restriction? Has a local conclusion been strengthened without justification? |
| Exact conclusion | Does the whole route establish every claimed part in the stated form? Is the finding about a written argument, a supplier application, or the statement itself? |

Store a concise explanation of the issues actually examined in the relevant check. Do not output a row saying every checklist concern was checked for every source line. Do not replace scrutiny with a blanket claim that all risks were considered. Explain the nontrivial inference, cite its evidence, and identify the scope of the judgment.

Applications have separate checks. A sound lemma used incorrectly creates an application finding; it does not make the supplier false. Joint inputs require a derivation check in addition to individual applications. For example, two events each with failure probability at most \(\delta\) generally combine to failure probability at most \(2\delta\); two green application checks do not establish a target failure probability of \(\delta\).

Use the closed outcomes precisely:

- `supported`: the local obligation follows under its explicitly recorded premises. Overall support may still be conditional.
- `gap`: the supplied argument fails to establish its obligation, with the missing or invalid inference identified.
- `refuted`: evidence contradicts the exact assertion under its claimed hypotheses. A failed proof is insufficient.
- `inconclusive`: a substantive examination cannot resolve the obligation with the available evidence. Explain what remains uncertain and what could resolve it.

A `draft` may have tentative reasoning or an outcome. It does not count as complete. A complete inconclusive check must contain the actual examination and limitation; it cannot be an empty placeholder for unperformed work.

Keep repairs separate. A different argument for the unchanged statement has its own route. A strengthened assumption or restricted conclusion has its own supported form and explicit conditions. Do not erase the original proof defect or mark its route green because a repair looks promising.

At the end of an argument, check final composition against its exact target and required parts. Include internally originating reasoning with no incoming major edge, case assembly, and scope discharge. Review coverage against the full written argument. The graph's arrows are a navigation aid; their existence and color do not supply this integration check.

## Independent checker

Receive a fresh context containing this protocol and the independent source packet. The packet includes source statements, complete relevant proof passages, source definitions/macros and external statements, declared scope, and neutral source limitations. It excludes primary judgments, primary-authored intermediate claims, inferred dependency explanations, scratchpads, findings, reconstructions, repairs, and expected calibration answers. Do not seek the primary database or report.

Independently normalize the target and identify the needed premises and local inferences from source. Challenge the exact applications, scope, cases, and final composition. Use the same compact mathematical checklist. A balanced reviewer should be able to support a valid proof and identify an invalid one; the assignment is not to manufacture disagreement or rubber-stamp the first audit.

If source context is missing, request a source-only packet extension. State any incomplete/truncated material. A selected theorem part is not the complete theorem. If a long proof is divided into review sections, state what was checked and leave an integration obligation visible.

Write one JSON object to `RESPONSE.json` with exactly `packet_id`, `covered_targets`, `coverage_note`, `exposure_report`, and `judgments`, as defined in [record-contract section 5.1](record-contract.md#51-worker-response-and-coordinator-submission). Each judgment supplies the target, kind, state, outcome, reasoning, evidence references, conditions, next action, and any pinned predecessor. Use the packet's ID and actual reviewed scope. New source-grounded claims may use SourceTarget until mapped. Report possible exposure in `exposure_report`; do not supply reviewer identity, qualification ID, or the coordinator's exposure assessment. Return/save this file before receiving reconciliation material; the coordinator submits its original bytes.

## Reconciliation and final assessment

Only after preserving the original independent response, compare the primary and independent evidence. Map source-grounded claims transparently. Identify the precise disagreement; distinguish a different proof route from a contradictory judgment of the same route.

Record whether the evidence agrees, the primary judgment changes, the independent judgment changes, or disagreement remains unresolved. A changed view requires an explicit successor check and reasoning. Preserve the original judgments. Review incomplete scope, additional discovered dependencies, and final integration even when both responses use the word supported.

Report four separate facts: saved local outcomes, currentness, available/conditional dependency support, and completion of the audit process. Confirmed defects may appear in a completed audit. Undone work, stale obligations, or compromised/missing independent review may not. Graph colors are derived from this evidence and must retain their qualifications.

## Pilot measurement

Record time and usage at meaningful phase boundaries, using the tool's receipts where available. Separate reading/reasoning, record authoring, retries, repeated work after changes, command time, waiting, and reporting. Mark inseparable phases as combined and unavailable usage as unknown. Checkpoint at the pilot budget rather than forcing a final mathematical judgment to fit it.

The first pilot must test both a correct joint inference and a defective final combination, draft/resume, a later consumer, a changed prerequisite, independent disagreement, and report inspection. Use software fixtures for deterministic record behavior and a fresh source-based task for mathematical evaluation. Evaluate whether the instructions produce proportionate records and useful explanations before expanding to a full paper.
