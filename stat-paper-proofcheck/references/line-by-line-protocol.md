# Line-by-Line Verification Protocol

## Contents

- [Lock the unit](#1-lock-the-unit)
- [Normalize the obligation](#2-normalize-the-proof-obligation)
- [First sequential read](#3-perform-the-first-sequential-read)
- [Atomic steps](#4-partition-into-atomic-steps)
- [Ledger rows](#5-complete-every-substantive-ledger-row)
- [Inferential checks](#6-check-each-inferential-move)
- [Status](#7-assign-status-conservatively)
- [Use sites](#8-check-the-use-site)
- [Coverage gate](#9-enforce-the-coverage-gate)

## Purpose

Use this protocol for every detailed proof-unit audit. Its two central controls are complete source coverage and atomic mathematical verification records. Neither control substitutes for mathematical judgment, and neither provides formal soundness.
Final verification requires `evidence_contract_version: 3`. A legacy ledger
without conclusion-level support closure, exact occurrence dispositions, and
structured premise and inference evidence may be inspected, but it cannot
support a final verification claim.

## 1. Lock the unit

Identify the formal statement, full proof, exact source file or files, inclusive line ranges, dependencies, definitions, inherited assumptions, and later use sites. Generate a source-locked ledger with `scripts/proofcheck.py extract`, passing the exact statement file and range so its contract anchor is created automatically. If the proof ledger does not include the statement because it is distant or in another file, record a precise separate-statement reason.

Include proof delimiters and intervening prose. Do not omit setup sentences, displayed-equation lines, "clearly" clauses, or the final conclusion. These locations often carry hidden scope changes.

## 2. Normalize the proof obligation

Before judging the argument, rewrite the target without strengthening or weakening it. Record:

- exact statement spans and hashes;
- quantified variables in order, with `forall`, `exists`, or `fixed`, type, and domain;
- quantifier scope and the ambient probability model or `not applicable`;
- every explicit and inherited hypothesis;
- definitions that determine the claim's meaning;
- ordered conclusions, each with a stable `Cxxx` ID, exact claim, locked source
  spans, scalar `applies_under` JSON Pointers, and conclusion-specific
  normalization evidence;
- pointwise, uniform, or mixed scope;
- finite-sample, asymptotic, or mixed regime;
- every permitted dependency of constants.
Complete all eight `normalization_checks` dispositions. Each must have
specific evidence and use `checked`, `not_applicable`, or `unclear`. Use
`not_applicable` only when the corresponding normalized field explicitly
records absence. `quantifiers_and_domains` and `conclusion` cannot be
`not_applicable`. The mandatory `quantifier_scope`, `conclusion`, and each
recorded variable's symbol, type, and domain cannot use a reserved absence
marker. Unresolved placeholders other than exact `unclear` are forbidden
throughout the normalized obligation. Use exact `unclear` when the source
cannot be normalized defensibly, and mirror it with the corresponding
`unclear` normalization disposition. Neither a `verified` nor a
`conditionally_verified` contract can contain an unclear normalization
disposition.

Bare absence or unresolved markers cannot stand in for mathematical content or
evidence. Reserve `none`, `N/A`, `not applicable`, `not-applicable`, and
`not_applicable` for normalized obligation fields whose disposition is
`not_applicable`. Do not use them, or bare `unclear`, `unknown`, `unresolved`,
`TBD`, `TODO`, `pending`, `not checked`, or `not_checked`, as a substantive
step claim, dependency form, premise, inference move, check, or evidence
statement. Record the exact content or use the appropriate nonverified status.
Surrounding punctuation or code formatting does not make a placeholder
substantive.

This contract is the target of the audit. Check contract fidelity separately from the validity of the written argument. A sound derivation of a nearby or weaker claim does not establish the stated theorem.

## 3. Perform the first sequential read

Read from the first source line to the last without jumping ahead. Record, in order:

- objects used before definition;
- assumptions first invoked;
- changes in event, conditioning, domain, norm, or quantifier scope;
- each claimed equality, inequality, implication, approximation, or limit;
- each citation or dependency invocation;
- the exact point where the stated conclusion is reached.

A later definition does not make an earlier use well-formed. A later argument may repair a gap, but the original location remains part of the audit record.

## 4. Partition into atomic steps

Assign every physical line to exactly one contiguous ledger step. A step may span several lines only when they form one continued sentence, display, definition, or inferential move.

Split a row when any of the following changes:

- the premise or dependency;
- the mathematical operation;
- equality or inequality justification;
- conditioning event or probability measure;
- quantifier or domain;
- asymptotic regime or hidden-constant scope;
- conclusion or proof goal.

Do not group several transitions merely because they occur in one display. Split
the source range when possible. If one physical source unit contains an
indivisible chain, use `source_indivisible_chain` and record every transition as
an ordered inference move. Set `source_unit_kind` to `one_line`,
`continued_sentence`, or `continued_display`, and explain in
`partition_evidence` why the unit cannot be split without changing its source
meaning. A multiline unit cannot cross a blank or comment-only separator. For a
multiline indivisible unit, give every move an ordered `source_line_range`;
together the ranges must represent every covered source line. A one-line unit
does not require move-level source ranges.

Use `non_substantive` only for blank lines, full-line comments, and proof-environment delimiters. Do not use it for braces, prose, equation delimiters surrounding mathematics, labels, or "by standard arguments."

## 5. Complete every substantive ledger row

Record:

1. `id`: unique step ID such as `S001`.
2. `lines`: inclusive source range.
3. `kind`: statement, setup, definition, algebra, inequality, probability, limit, dependency, conclusion, or other.
4. `goal`: the current local proof obligation.
5. `restatement`: the exact mathematical claim in the row.
6. `premise_uses`: each used fact, assumption, or definition, with a stable ID, exact claim, origin, and source-link evidence.
7. `dependencies`: each dependency's kind, exact needed form, compatibility
   check, and status; every internal or external result use has a `Dxxx`
   `use_id`, and every internal use names the exact dependency `Cxxx`
   `conclusion_id`.
8. `inference`: ordered atomic moves, their rules, premise IDs, earlier-move IDs, justifications, and the final conclusion move.
9. `checks`: literal evidence, structured atomicity, and adversarial checks.
10. `side_conditions`: every generated condition, its stable ID, status, and a
    discharge with one or more premise or strictly earlier established-move
    sources, each source's contribution, the joint rule, and evidence.
11. `risk_checks`: exactly one disposition for domain, dimension, sign, constant, rate, probability, quantifier, and limit.
12. `conditions`: for a conditional step, an exact mapping to every open side condition, conditional or unchecked dependency, and open risk.
13. `status`: the calibrated outcome.
14. `issue_ids`: canonical IDs for any gap, incorrect, or unclear step.

An obligation-origin premise must use a JSON Pointer that resolves to one
concrete scalar string, such as `/hypotheses/0` or `/quantifier_scope`, and must
name the one-based locked statement or context span that anchors it. Its claim
must exactly match the resolved string. A pointer to a list or object, including
a whole quantified-variable record, cannot supply a load-bearing premise claim.
Select or normalize the exact scalar fact instead.

A prior-step or result premise must have a matching declared dependency, and
its claim must exactly match that dependency's `needed_form`. A result premise
origin names its `Dxxx` use, not merely the dependency result ID. For a prior-step
dependency, `needed_form` must also equal the earlier step's restatement exactly.
When a source occurrence points to a labeled earlier step, record both
`source_reference_occurrence_id` and `source_reference_id`; the target label
must be statically active inside that exact earlier step range.
Every `internal_result` or `external_result` record must exactly mirror the
record with the same `use_id` in `review.direct_dependencies`, including
`kind`, `status`,
`needed_form`, and `compatibility_check`. A dependency cannot have status
`not_applicable`; omit it instead.

The theorem's whole statement span, normalized conclusion, and statement ledger
row are not premise origins because citing any of them would assume the result
under review. Cite a normalized hypothesis, definition, variable, model, scope,
regime, constant, or genuinely established earlier result instead. Every
declared dependency must be used by a premise, and every premise must be
consumed by an inference move. Standard logical or algebraic rules belong in
the move's `rule` and `justification`; do not invent an unanchored "standard
fact" premise.

Use `non_inferential` only for statement, setup, or definition rows.
Use `single_move` for one inference. Use `source_indivisible_chain` only when
one physical source unit cannot be partitioned, and list every atomic move in
order. Every `verified` or `conditionally_verified` inferential move must
consume at least one premise or strictly earlier move.

A move on a `gap`, `incorrect`, or `unclear` step may have no input only when it
has a `failure` object with `kind`, `issue_id`, and paper-specific `evidence`.
The issue must appear in the step's `issue_ids`. Use
`missing_premise` or `unsupported_assertion` with `gap`,
`source_ambiguity` with `unclear`, and `invalid_rule`, `counterexample`,
or `contradiction` with `incorrect`. An `invalid_rule` failure does not excuse
a zero-input move. A `refuted` conclusion requires `counterexample` or
`contradiction` on its designated support move, and its `failure.target` must
exactly equal that `Cxxx` conclusion claim. An invalid proof alone supports only
`not_established`.

Every recorded move must be load-bearing in the backward closure of
`conclusion_move`; an earlier move used to discharge a side condition counts
only when that condition is generated by a reachable move. The final move's
claim must exactly match `restatement`.

Create one ordered `review.conclusion_results` row for each `obligation`
conclusion. Bind its `conclusion_id` to exactly one checked support
`{step_id, move_id}`, its component judgments, exact `dependency_use_ids`, and
issues. For `established` or `conditional`, the support move must exactly equal
that conclusion's claim. For `refuted`, preserve a counterexample or
contradiction whose target equals that claim. Compute each conclusion's support
closure backward through moves, premises, prior-step support, and side-condition
sources. It may use only the obligation pointers in that conclusion's
`applies_under` list, and its dependency-use list must equal the result uses in
that closure. For one conclusion, set `review.conclusion_step_id` to its support
step. For multiple conclusions, leave the alias empty. Set the unit-level
`statement_status` to the weakest conclusion judgment.

An `established` or `refuted` statement requires verified contract fidelity.
A `conditional` statement requires verified or conditionally verified contract
fidelity. Do not use an argument or statement verdict to conceal an uncertain
normalized target.

Every side condition must name its `generated_by` move. A discharged condition
must have a nonempty `discharge.sources` list. Each source records `kind` as
`premise` or `inference_move`, its exact `reference`, and its substantive
`contribution`; the discharge also records the joint `rule` and `evidence`.
Every move source must be established strictly before the generating move. The
same move, a later move, or a failed move is circular or invalid discharge and
cannot support verification. A premise used only in a valid discharge still
counts as consumed.

Each risk disposition must contain paper-specific evidence. Use
`not_applicable` only with a reason tied to the current move. A failed or
unclear risk cannot be hidden inside a verified or conditional status. For a
`conditionally_verified` step, every open risk must be named in `conditions`.
A `gap`, `incorrect`, or `unclear` step may retain an open secondary risk,
but it cannot use that unresolved risk to upgrade its status.

The source text is evidence of what the paper says, not evidence that the step is valid.

For the exact JSON field shape, inspect `assets/templates/AUDIT_RECORD_EXAMPLES.json` when filling the first ledger or issue record. Do not copy its placeholder facts into a paper audit.

Reconcile every parser-discovered reference occurrence found in the reviewed
proof span, including bracket-form `\hyperref`. Give each disposition the exact
parser `occurrence_id`, target, and command. Use `internal_result` for a
load-bearing result use, `obligation_context` for locked statement or context,
`local_step` for an earlier ledger step, `own_result_identification` only for a
genuine header or closing identification, `navigation` only for structural
navigation, `non_load_bearing` when the occurrence supplies no premise, and
`unresolved` otherwise. Premise-bearing roles must list every linked
`{step_id, premise_id}` pair; the premise records the same
`source_reference_occurrence_id` and target. An `internal_result` disposition
also names the matching `dependency_use_id`. An obligation-context premise's
locked anchor must contain the exact statically active
`\label{source_reference_id}` target. The links must be exact in both
directions. A self-reference is not automatically a dependency or harmless
identification. An unresolved occurrence is incompatible with a verified unit.

The local active-label gate is conservative and static. It masks common
command and environment definition bodies, inline `\verb`, and common
verbatim-like environments before checking a locked span. It still does not
expand macro invocations or execute TeX. Unrecognized or dynamically generated
definitions, verbatim constructs, and labels can evade static masking. Inspect
them during global source-resolution review, and do not rely on the local
active-label result alone.

Reconcile every supported citation command found in the proof, including common natbib and biblatex forms such as `\cite`, `\citep`, `\citet`, `\citealp`, `\citealt`, `\parencite`, `\textcite`, `\autocite`, `\footcite`, and `\smartcite`. Mark it `external_result` with a matching external direct dependency and proof step, `bibliographic_only` with evidence that it supplies no premise, or `unresolved`. Inspect every unsupported-citation parser warning manually. An unresolved citation is incompatible with a verified unit.

## 6. Check each inferential move

For every substantive row, ask:

- Does the conclusion follow from the listed facts alone?
- Are objects defined with the required type, dimension, measurability, and domain?
- Is every denominator nonzero and every inverse justified?
- Is the equality exact, almost sure, in distribution, in probability, or asymptotic?
- Is the inequality direction correct, and are signs or monotonicity established?
- Are constants allowed to depend on the quantities they hide?
- Are probability events combined with the correct failure probability?
- Are conditioning and independence used legally?
- Are limits, expectations, derivatives, integrals, suprema, and infima exchanged under valid conditions?
- Is a pointwise statement being used uniformly?
- Does the quantifier order match the theorem statement?
- Does a cited result provide the exact needed conclusion under satisfied assumptions?

Recompute algebra and rates. For a long calculation, preserve the source row,
record its ordered atomic moves in `inference.moves`, and use a separate
auxiliary calculation when needed.

For logical proof rules, also check variable freshness for universal introduction, the legality of existential witnesses, case exhaustiveness, induction base and step, the measure used in almost-sure claims, and that contradiction is reached from the exact negation of the goal. Every generated side condition must be discharged at an identified step or remain open.

## 7. Assign status conservatively

- `verified`: independently justified, with every declared dependency verified,
  every risk check passed or specifically not applicable, and every generated
  side condition discharged.
- `conditionally_verified`: the step is valid under exactly the open side
  conditions, conditional or unchecked dependencies, and open risks enumerated
  in its structured `conditions` records.
- `gap`: a necessary inference or assumption is missing, but falsity is not established.
- `incorrect`: a contradiction, invalid transition, or counterexample establishes failure.
- `unclear`: source ambiguity prevents a defensible judgment.
- `not_checked`: work remains.
- `non_substantive`: only permitted for mechanically non-substantive lines.

Use [evidence-status-and-issues.md](evidence-status-and-issues.md) for severity and confidence.

Record separate component judgments for contract fidelity, argument validity, statement status, dependency closure, and use-site sufficiency. An invalid proof does not by itself show that the theorem statement is false.

## 8. Check the use site

After local verification, inspect where the result is used. Compare:

- theorem statement versus what the proof established;
- lemma conclusion versus the exact form required later;
- local assumptions versus those available at the use site;
- constants, probability level, domain, and uniformity;
- pre-asymptotic versus asymptotic scope.

A lemma can be correct yet insufficient for the main theorem.

Record parser-discovered use sites as a canonical set of exact `file:line`
locations. Multiple occurrences at the same source location collapse to one
set entry. Count occurrences from other units that target either the result
label or a uniquely owned label inside the result, including an equation label.
Exclude occurrences inside the result's own statement, reviewed proof, or
forwarding stub, and exclude structural navigation. Do not replace distinct
locations with a range.

## 9. Enforce the coverage gate

Run `ledger-check --final`. Resolve every uncovered line, overlap, stale hash,
unsupported status, missing issue reference, and verdict mismatch. This command
checks the local record and declared dependency statuses only. Its JSON output
states that audit-wide dependency resolution was not performed. Run `finalize`
on the audit root before making an audit-wide verification claim.

For PDF-only input, create a UTF-8 numbered transcription for the exact page range and use that transcription as the hashed audit source. Visually compare every displayed equation and symbol against the rendered pages, record page and equation anchors in the contract, and manually build the reviewed inventory. State that LaTeX-level cross-reference, macro, include-closure, and source-authenticity checks were unavailable. Do not claim that the transcription hash authenticates the publisher PDF.
