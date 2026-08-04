# Evidence, Status, and Issue Discipline

## Evidence classes

Keep three classes separate:

1. **Observed:** explicitly present in the manuscript or verified external source.
2. **Inferred:** a reviewer reconstruction supported by observed material.
3. **Not established:** missing, ambiguous, externally unchecked, or dependent on unresolved work.

Every strong judgment must cite exact manuscript lines, theorem or equation labels, pages, or verified external theorem locations.

## Assurance boundary

This protocol is non-formal. It can provide high assurance through exact source coverage, independent reconstruction, dependency closure, adversarial search, and a fresh critical-path challenge. It cannot provide the soundness guarantee of a small proof-assistant kernel.

Mechanical validation establishes that source hashes, normalized-field
dispositions, premise origins and active reference anchors, exact
reference-occurrence dispositions, `Dxxx` dependency-use mirrors, atomic move
links and reachability, structured failure and status links, risk dispositions,
joint side-condition discharge, and per-conclusion support closures are present
and internally consistent. Audit-wide validation also
establishes that the reviewed closure registry matches the current source
snapshot, inventory, and scope; every direct dependency has one exact use
record; obligation and external-evidence hashes are current; compatibility and
global-consistency matrices are complete; statuses and issues propagate; and
progress and report claims reconcile. It does not establish that the
mathematics written in those fields is true.

The local active-anchor check is conservative and static. It rejects commented
labels and labels inside disabled or unresolved conditional branches, but it
also masks common command and environment definition bodies, inline `\verb`,
and common verbatim-like environments. It still does not expand macro
invocations or execute TeX. Unrecognized or dynamically generated definitions,
verbatim constructs, and labels can evade static masking. Inspect them during
manual source-resolution review, and do not rely on the local active-label
result alone.

Mechanical validation also rejects unresolved placeholders throughout the
normalized obligation and substantive proof or evidence fields. Exact `unclear`
is allowed in normalized fields only with a matching `unclear` disposition. A
status such as `not_applicable` does not replace paper-specific evidence
explaining why the aspect is absent. Record the mathematical content, the
observed failure, or an appropriate nonverified status.

## Unit verdicts

Use one verdict per proof unit:

- `verified`: all source lines and substantive steps checked; every premise is
  anchored, every declared dependency is verified, every risk is passed or
  specifically not applicable, and every side condition is discharged.
- `conditionally_verified`: each unresolved cause is explicit and maps exactly
  to an open side condition, conditional or unchecked dependency, or open risk.
- `gap`: a necessary claim is not established.
- `incorrect`: a definite invalidity or counterexample is established.
- `unclear`: ambiguity blocks a defensible conclusion.
- `not_checked`: detailed checking is incomplete.

Do not average step statuses. The weakest load-bearing step controls the unit verdict.

A verified step cannot inherit an open, failed, unclear, unchecked, or
conditional load-bearing input. A conditional step cannot hide a failed or
unclear dependency or risk. The structured condition list must be an exact
bijection with its unresolved causes. The unit verdict remains the weakest
substantive step verdict; component judgments can impose additional gates but
cannot upgrade that verdict.
Keep these judgments separate:

- `contract_fidelity`: whether the normalized obligation faithfully matches the stated result;
- `argument_status`: valid, conditional, gap, invalid, unclear, or not checked;
- `statement_status`: established, conditional, refuted, not established, unclear, or not assessed;
- `dependency_closure`: whether every load-bearing dependency resolves with compatible assumptions and conclusions;
- `use_site_sufficiency`: whether the established result is sufficient where later used.

Derive dependency availability from the named conclusion's own contract
fidelity, argument status, statement status, and dependency closure. Do not use
another conclusion or the unit-level weakest summary to cap an independent
conclusion. An established conclusion supplies `verified` only when its
contract, argument, and closure are verified; any conditional component
supplies at most `conditional`. A refuted conclusion supplies `incorrect`. A
`not_established` conclusion supplies `gap`, even when the proof failure is an
invalid argument. An unclear or unassessed conclusion supplies `unclear` or
`unchecked`. This distinction prevents an invalid proof from being propagated
as conclusion falsity.

Each `Cxxx` conclusion has one `review.conclusion_results` row supported by an
exact checked move. Its component judgments, obligation-pointer use,
dependency-use closure, and issues are conclusion-specific. For `established`
or `conditional`, that move must reach the exact conclusion claim. For
`refuted`, `not_established`, or `unclear`, it must preserve the actual failure
or mismatch. Its step status must agree with the conclusion judgment. Use
`review.conclusion_step_id` only as the single-conclusion support-step alias;
leave it empty for a multi-conclusion result. The unit-level `statement_status`
is the weakest conclusion judgment.

An `established` or `refuted` statement requires `contract_fidelity: verified`.
A `conditional` statement requires `contract_fidelity: verified` or
`conditionally_verified`. This prevents a strong statement judgment about an
uncertain normalized target.

An invalid argument establishes a defect in the proof, not the falsity of the
theorem. Use `refuted` only when an exact counterexample or contradiction
establishes that one recorded conclusion itself is false. Its support move must
record the matching `counterexample` or `contradiction` failure kind, issue
link, and evidence, with `failure.target` exactly equal to that conclusion's
claim.

## Method-interface judgments

For a triggered estimated interface, keep the proof-unit judgments above unchanged and record these additional relations in `METHOD_INTERFACE_REGISTRY.json`:

- `interface_specification_status`: `clear`, `ambiguous`, `incomplete`, or `not_checked`;
- `derivation_status`: the status of the mathematical derivation, kept separate from prose clarity;
- `target_relation.verdict`: `match`, `conditional_match`, `mismatch`, `not_assessable`, or `not_checked`;
- `implementation_relation.inspection_status`: `inspected`, `available_not_checked`, `unavailable`, `out_of_scope`, or `not_applicable`;
- separate code comparisons to `documented_estimator` and `required_target`, each with verdict `consistent`, `inconsistent`, `not_assessable`, `not_checked`, or `not_applicable`;
- `implementation_relation.execution_provenance.status`: `matched`, `not_matched`, `not_checked`, or `not_applicable`.

`conditional_match` requires an explicit named condition supported by the source. Do not use it for an unspecified manuscript meaning. If two plausible readings select different targets and the source does not choose between them, use `not_assessable` and record both interpretations.

Ambiguity can be load-bearing and severe. It does not, by itself, establish which target or implementation is wrong. A `mismatch` requires authoritative evidence that fixes both compared objects. Static code inspection can establish only what the inspected snapshot computes. It does not establish that the same code, run configuration, preprocessing, inputs, and output linkage produced reported experiments.

Keep the two code comparisons separate. Code can be consistent with the documented estimator while inconsistent with the theorem-required target because the documented estimator itself is wrong. Classify that as `estimator_target_mismatch`, not a coding defect. Use `implementation_mismatch` when the code is inconsistent with the documented estimator.

When the documented estimator itself remains ambiguous, code may still be compared directly with the required target, but the code-to-documentation verdict is ordinarily `not_assessable`. Do not let code silently choose the manuscript's intended meaning.

Execution provenance affects the proof assessment only when execution linkage is required for the declared claim. A missing link is then inconclusive, while an established required non-match is a defect. Neither state invalidates an abstract theorem that explicitly assumes an oracle nuisance condition and does not claim that the implementation establishes it.

## Severity

- **S0 Fatal:** the main theorem or central claim does not follow in the stated form, with no local repair established.
- **S1 Major:** a load-bearing assumption, dependency, or inference is missing or wrong, but a plausible repair may exist.
- **S2 Moderate:** a local gap, ambiguity, scope mismatch, or incomplete justification affects confidence but may not change the main result.
- **S3 Minor:** a typo, label, notation, or exposition defect does not change the mathematical argument.

Severity measures consequence, not certainty or repair difficulty.

S0 and S1 issues are load-bearing by definition. Any open or deferred S0 or S1 issue, and any lower-severity issue explicitly marked load-bearing, prevents a `no_defect_found` assessment.

## Confidence

- **high:** exact evidence plus reconstructed reasoning or a concrete counterexample.
- **medium:** strong evidence remains dependent on interpretation or an unchecked fact.
- **low:** a plausible concern requiring further analysis.

High severity with low confidence is a priority for checking, not a proven failure.

## Canonical issue records

Define each issue once in `audit/06_reports/ISSUE_LOG.json` with:

- unique ID such as `I-001`;
- severity and confidence;
- lifecycle `status`: `open`, `resolved`, or `deferred`;
- `finding_status`: `defect`, `inconclusive`, or `resolved`;
- exact location and root `affected_result`;
- `affected_results`, equal to the exact dependency-propagated result set;
- concise summary and evidence list;
- downstream consequences;
- possible repair, kept separate from the diagnosis;
- scope set to `unit` or `global`;
- whether the issue is load-bearing.

Use `finding_status: defect` when the evidence establishes a defect. Use
`inconclusive` when an ambiguity, unchecked fact, or conditional finding blocks
a conclusion. Use `resolved` only with lifecycle `status: resolved` and the full
resolution record. An open or deferred issue cannot have `finding_status:
resolved`, and a resolved lifecycle record cannot retain a defect or
inconclusive finding status.

For an open or deferred load-bearing issue, start at `affected_result` and
follow the reverse internal dependency graph. Set `affected_results` to the root
and every in-scope transitive dependent reached by that load-bearing finding.
Do not leave out a downstream result because its ledger predates the issue.
Every reached result must carry a status no stronger than the propagated
finding. For a non-load-bearing issue, do not invent downstream propagation.

A method-interface issue also records:

- `interface_id` linking the canonical interface record;
- `finding_class`: `exposition_ambiguity`, `estimator_target_mismatch`,
  `implementation_mismatch`, `reproducibility_gap`, or `scope_boundary`;
- `affected_layer` and evidence class;
- the estimator-target status, implementation inspection status, both
  code-comparison verdicts, and execution-provenance status copied exactly from
  the interface record;
- the evidence needed to resolve the finding.

The generated issue summary preserves these fields. Every later report,
handoff, or synthesis must preserve the canonical finding status, finding
class, affected layer, affected result set, relation statuses, confidence, and
inspection scope. Strengthen the claim only after new evidence is entered into
the canonical records and revalidated.

A resolved issue must also record the resolution, source revision,
`source_snapshot_sha256`, `recheck_evidence`, and `rechecked_units`.
`source_snapshot_sha256` must equal the current manifest snapshot, and
`rechecked_units` must equal `affected_results`. Changing lifecycle status
without rechecking the root and all affected downstream results is not
resolution.

A resolved method-interface issue additionally needs a semantic contract
containing the protected mathematical meaning, minimal authoritative supporting
spans, dependent claims, conditions that reopen the issue, a regression check,
and the source snapshot identifier. Lock authoritative definitions, algorithms,
or configurations, not merely redundant explanatory prose. A changed
supporting hash marks the contract stale; the validator does not infer that
semantic meaning survived the edit.

Local ledgers reference issue IDs. They do not create competing descriptions.
Dependency and external-use records reference the same canonical IDs. Generate
`ISSUE_SUMMARY.md` with the bundled script so counts, severities, lifecycle
states, finding states, and affected results come from the canonical log.
## Verification burden

"Verified" requires positive support. The following are insufficient:

- the step is familiar;
- a similar theorem is standard;
- the manuscript compiles;
- symbolic software returns the expected expression on examples;
- no counterexample was found;
- the authors cite a relevant-looking paper;
- a downstream theorem would be true if the step held.

When evidence is incomplete, downgrade the status rather than filling the gap from mathematical taste.

## Computational evidence hierarchy

Record the encoded claim, assumptions, domain, tool and version, exact command, deterministic seed or precision when relevant, and output for every computational check.

1. An independently checkable exact certificate may verify only the precisely encoded sub-obligation. Check the translation, supported logic, side conditions, and certificate verifier. An SMT result of `unknown` supplies no support.
2. Exact symbolic algebra may discharge a specific identity only after assumptions, branches, and domains are encoded and checked. Heuristic simplification alone is not proof.
3. Validated interval arithmetic can certify a bounded numerical inclusion or counterexample when both premises and failure are enclosed rigorously.
4. Ordinary numerical tests, simulation, property testing, and random search are falsification tools. A found candidate must be checked exactly or with validated bounds. Finding no counterexample leaves proof status unchanged.

Never promote evidence beyond the claim actually encoded.

## Independent critical-path evidence

For critical results, require a challenger pass that does not see the primary verdict or proposed repair. Record the independence level as fresh-context same model, different model, or independent human. Preserve the primary verdict, challenger verdict, reconciled verdict, disagreements, resolution, and artifacts. Do not describe a same-context reread as independent.
