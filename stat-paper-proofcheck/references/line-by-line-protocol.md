# Line-by-Line Verification Protocol

## Contents

- [Lock the unit](#1-lock-the-unit)
- [Normalize the obligation](#2-normalize-the-proof-obligation)
- [First sequential read](#3-perform-the-first-sequential-read)
- [Compact work packets and annotations](#compact-work-packets-and-annotations)
- [Atomic steps](#4-partition-into-atomic-steps)
- [Ledger rows](#5-complete-every-substantive-ledger-row)
- [Inferential checks](#6-check-each-inferential-move)
- [Status](#7-assign-status-conservatively)
- [Use sites](#8-check-the-use-site)
- [Coverage gate](#9-enforce-the-coverage-gate)

## Purpose

Use this protocol for every detailed proof-unit audit. Its two central controls are complete source coverage and atomic mathematical verification records. Neither control substitutes for mathematical judgment, and neither provides formal soundness.
Final verification requires artifact schema `5` and
`evidence_contract_version: 5`. A schema-4, evidence-contract-3, or
evidence-contract-4 ledger may be inspected, but it cannot support a current
final verification claim until it is explicitly migrated and rechecked.

## 1. Lock the unit

Identify the formal statement, full proof, exact source file or files, inclusive line ranges, dependencies, definitions, inherited assumptions, and later use sites. Generate a source-locked ledger with the bundled `proofcheck.py extract` command resolved from the directory containing `SKILL.md`, passing the exact statement file and range so its contract anchor is created automatically. If the proof ledger does not include the statement because it is distant or in another file, record a precise separate-statement reason.

Include proof delimiters and intervening prose. Do not omit setup sentences, displayed-equation lines, "clearly" clauses, or the final conclusion. These locations often carry hidden scope changes.

Treat the analyzer's proof region as canonical. Every automatic or reviewed
proof span must match either a complete proof environment or one uniquely
targeted named-heading region with a recognized boundary. Accept a replacement
only through the existing hash-bound `reviewed_manual` override, with explicit
boundary and target evidence in the override records. Rescan the complete
replacement span and reconcile all references, dependencies, citations, and
warnings. Do not trim or widen a proof span merely to simplify the ledger.

For an explicit `external_restatement` inventory override, there is no local
proof region. Lock exactly the formal statement, set ledger source
`coverage_mode: external_restatement`, and repeat the override's
`external_dependency_use_id`. Cover only that statement span. The one
designated external `Dxxx` use must support every established or conditional
conclusion through the ordinary move and premise links. Never use the
manuscript statement as its own premise.

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

## Compact work packets and annotations

Audit atomicity is not model-call atomicity. Check every substantive move
separately, but normally inspect one complete proof unit and produce all of its
ordered atomic records in one model call. Do not create one call per source
line, risk row, or inference move.

Model tiering may reduce cost without moving judgment. A lighter model may
draft transcription-grade content: reviewing prefilled literals, goals, exact
claim restatements, and source grouping. The judgment-bearing fields, including status,
all risk dispositions, side conditions, failures and computations, premise and
rule choices, conclusion rows, and everything in an issue or challenge,
require the strongest available model, which must review any drafted content
it builds on. The compiler and validators apply identical gates to every
author, and telemetry's `stage` field can record the tier used per call. The
strongest-model requirement is auditable through the calibration record: the
declared `checker_profile_id` names the judgment-bearing checker, and a
changed profile requires a fresh calibration session before further judgment.

When a compact context projection is useful, generate a primary packet:

```bash
python "<skill-root>/scripts/proofcheck.py" packet --root "<audit-root>" --unit-id <unit-id> --mode primary --output "<packet.json>"
```

The packet is noncanonical context and must be written outside the audit root.
It binds exact source text, normalized obligation, current semantic artifact,
unit inventory, exact dependencies, relevant issue triggers, candidate
reconciliation, dependency alignment, risk aspects, and bounded resume state.
The context binding is dependency-closed semantic state. A separate operational
binding records global file hashes, progress, and navigation state for
provenance without forcing mathematical rework. Exact line number and text,
enclosing span hashes, source-member hashes, and the source snapshot retain
traceability; redundant per-line hashes are not model-visible. Require
primary_work_packet_ready: true and a completed normalized obligation.

For a fresh extracted skeleton, generate a deterministic packet-bound draft:

    python "<skill-root>/scripts/proofcheck.py" annotation-scaffold "<unit.skeleton.json>" --packet "<primary-packet.json>" --output "<annotations.json>"

The scaffold pre-fills deterministic hashes, IDs, dependency mirrors, source
line ranges, all eight risk slots, and a literal transcription of each step's
locked line. Every null is an unfinished semantic judgment. Review multiline
source grouping and replace every null with paper-specific analysis; when a
source group merges lines into one step, rewrite that step's prefilled
`literal` to quote the complete merged unit. Do not use placeholder prose.

Run one aggregate preflight before compilation:

    python "<skill-root>/scripts/proofcheck.py" annotation-check "<unit.skeleton.json>" --annotations "<annotations.json>" --packet "<primary-packet.json>" --json

The checker reports detectable schema, binding, and reconciliation problems
together with JSON pointers. It does not publish a ledger. Then compile:

    python "<skill-root>/scripts/proofcheck.py" compile-annotations "<unit.skeleton.json>" --annotations "<annotations.json>" --packet "<primary-packet.json>" --output "<unit.ledger.json>"

The skeleton must be inside the canonical audit and end in .skeleton.json.
The packet and annotation file remain outside the audit root. The compiler
rebuilds current state and requires exact equality of the dependency-closed
semantic projection. Progress, next action, and unrelated metadata may drift
without invalidating sound semantic work; relevant source, obligation,
dependency, external evidence, issue trigger, risk, or protocol drift fails
closed. The compiler never overwrites an existing output. Its receipt records
the exact packet hash, submitted and current operational binding hashes, and an
operational-drift flag, so accepted reuse remains traceable.

The annotation file is not a second evidence standard. It must still contain
one record per substantive move and all judgment-bearing content required by
this protocol: exact local restatement, goal, premise or earlier-move
references, rule and justification, side-condition disposition, all eight risk
dispositions with local evidence, status, issue IDs, and conclusion support.
Stable references may replace copied claims only when the compiler can resolve
them exactly from the normalized obligation, earlier moves, or declared result
uses.

Use annotation schema version `2`. Its top level contains exactly
`annotation_schema_version`, `unit_id`, `source_unit_sha256`,
`obligation_sha256`, `context_binding_sha256`,
`calibration_receipt_sha256`, `source_groups`, `dependencies`, `steps`,
`conclusions`, and `review`. Copy
`source_unit_sha256` from skeleton `source.unit_sha256`. Copy
the other three hashes from the exact primary packet. A changed calibration
receipt requires a fresh scaffold and full judgment review; it cannot be
rebound.
Keep `source_groups` empty unless a genuine multiline sentence or
display requires one. Each step uses a stable local `key`, exact `lines`,
`mode`, `kind`, `goal`, `claim`, literal and atomicity evidence, adversarial
checks, the eight-aspect `risks` object, inputs, side conditions, status, and
issue IDs. A derivation or reuse also supplies its rule and justification; a
failed move supplies the structured failure when required, including the
`computation` record for a counterexample or contradiction. Each conclusion
names its `Cxxx` ID and support-step key.

The review contains exactly `explicit_assumptions`, `inherited_assumptions`,
`source_reference_dispositions`, `candidate_dependency_dispositions`,
`citation_dispositions`, `verification_basis`, and `reviewer_notes`. It does
not author `use_sites`; the compiler derives those exact canonical locations
from packet `inventory.downstream_use_sites`. The compiler rejects unknown
fields so a typo cannot silently become unused evidence.

Make annotation `dependencies` equal the packet's registry-backed direct uses
exactly. Each dependency row has `id`, `use_id`, `kind`, `status`,
`needed_form`, and `compatibility_check`; an internal result also has its exact
`conclusion_id`.

Cover every packet proof reference occurrence once with the same
`occurrence_id`, `target`, and `command`, plus `disposition` and substantive
`evidence`. Use only `internal_result`, `obligation_context`, `local_step`,
`own_result_identification`, `navigation`, `non_load_bearing`, or `unresolved`.
An internal-result disposition also names `dependency_use_id`. An
internal-result, obligation-context, or local-step disposition must be carried
by an exact annotated input with both source-reference IDs.

Cover every packet citation key once with `key`, `disposition`, and substantive
`evidence`. An `external_result` citation also names its exact `dependency_id`
and `dependency_use_id`; other dispositions are `bibliographic_only` or
`unresolved`. Cover every candidate internal dependency and all of its `CPxxx`
path IDs exactly once with `candidate_id`, `path_ids`, `disposition`, and
substantive `evidence`. Map a load-bearing candidate to its internal dependency
use. A candidate with no registry edge may be only `navigation` or
`non_load_bearing`. A verified unit cannot leave a reference or citation
unresolved.

The compiler may generate only deterministic projections, including source
text and hashes, exact referenced claims and origins, mirrored dependency rows,
downstream use sites, non-substantive wrappers, and schema boilerplate. It must
reject or retain as `not_checked` every missing semantic judgment. It cannot invent a premise,
inference, applicability judgment, risk pass, side-condition discharge,
failure, issue, or verdict. Before verified no-overwrite publication, the compiler runs the
same full final local ledger validation used for a manual ledger. A successful
compile receipt with validation passed is therefore the local gate for that
unchanged compiled file; an immediate duplicate ledger-check is unnecessary.
Manual ledgers and any compiled ledger later modified or moved still require
ledger-check --final. Audit-wide dependency, issue, challenge, and finalization
gates remain mandatory.

If compilation reports stale semantic context, regenerate the packet and renew
the annotation binding only after confirming that every affected judgment
remains valid. Use mechanical rebinding only when
`calibration_receipt_sha256` is unchanged:

    python "<skill-root>/scripts/proofcheck.py" rebind-annotations "<annotations.json>" --packet "<primary-packet.json>" --skeleton "<unit.skeleton.json>"

Rebinding copies current hashes only; it never certifies the authored
judgments. If the calibration receipt changed, archive any old ledger under a
name not ending in `.ledger.json`, regenerate the packet, create a fresh
scaffold, and fully re-review. Operational-only drift does not justify
rewriting the binding.

If a proof unit does not fit in one complete packet, process contiguous
source-unit blocks in manuscript order. Carry forward only canonical
established move IDs and explicitly open conditions, then perform a whole-unit
closure pass before assigning any conclusion judgment. Do not use a free-form
summary as a substitute for omitted source or premises.

## 4. Partition into atomic steps

Partition source layout before reconstructing inference. Create
`source_units`, each with:

- a stable `Uxxx` `id`;
- one inclusive `lines: [start, end]` range;
- `kind` equal to `non_substantive`, `one_line`, `continued_sentence`, or
  `continued_display`;
- the exact `source_sha256`;
- `partition_evidence` explaining the classification and, for a multiline
  unit, the paper-specific reason the lines form one source unit.

Every physical proof line must belong to exactly one source unit, with no gap
or overlap. A multiline unit cannot cross a blank or comment-only separator.
Use `continued_display` only for multiple lines lying inside one recognized
display environment, and `continued_sentence` only for a genuine multiline
sentence.
Use `non_substantive` only for blank lines, full-line comments, and
proof-environment delimiters. Do not use it for braces, prose, equation
delimiters surrounding mathematics, labels, or "by standard arguments."

The `extract` command creates a deterministic one-physical-line partition with
current hashes. Keep that partition when it represents the layout adequately;
do not ask a model to rewrite source text or hashes. Merge lines only for one
genuine continued sentence or display, record the required paper-specific
partition evidence, and let validation recompute the joined hash.

Then create mathematical steps. Every schema-5 step references exactly one
`source_unit_id`; final mode forbids `steps[].lines`. One source unit may
support several ordered steps when its sentence or display contains several
transitions, but every source unit must be represented by at least one step. A
`non_substantive` source unit requires exactly one `non_substantive` wrapper
step. Create a separate step whenever any of the following changes:

- the premise or dependency;
- the mathematical operation;
- equality or inequality justification;
- conditioning event or probability measure;
- quantifier or domain;
- asymptotic regime or hidden-constant scope;
- conclusion or proof goal.

Each inferential step contains exactly one move and declares
`support_role: derivation` or `support_role: reuse`. A reuse step exposes an
already established fact and must have exactly one anchored premise whose claim
equals its `restatement`; it cannot support a canonical conclusion. A
derivation step must establish new content and cannot take a premise whose claim
is exactly its own `restatement`.

## 5. Complete every substantive ledger row

Record:

1. `id`: unique step ID such as `S001`.
2. `source_unit_id`: the exact `Uxxx` source unit containing the move.
3. `kind`: statement, setup, definition, algebra, inequality, probability, limit, dependency, conclusion, or other.
4. `goal`: the current local proof obligation.
5. `restatement`: the exact mathematical claim in the row.
6. `premise_uses`: each used fact, assumption, or definition, with a stable ID, exact claim, origin, and source-link evidence.
7. `dependencies`: each dependency's kind, exact needed form, compatibility
   check, and status; every internal or external result use has a `Dxxx`
   `use_id` unique across the whole audit, and every internal use names
   the exact dependency `Cxxx` `conclusion_id`.
8. `support_role`: `derivation` or `reuse` for an inferential step.
9. `inference`: exactly one atomic move for an inferential step, with its
   rule, premise IDs, earlier-move IDs, justification, and conclusion-move link.
10. `checks`: literal evidence, structured atomicity, and adversarial checks.
11. `side_conditions`: every generated condition, its stable ID, status, and a
    discharge with one or more premise or strictly earlier established-move
    sources, each source's contribution, the joint rule, and evidence.
12. `risk_checks`: exactly one disposition for domain, dimension, sign, constant, rate, probability, quantifier, and limit.
13. `conditions`: for a conditional step, an exact mapping to every open side condition, conditional or unchecked dependency, and open risk.
14. `status`: the calibrated outcome.
15. `issue_ids`: canonical IDs for any gap, incorrect, or unclear step.

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
fact" premise. Duplicate exact premise claims do not provide independent
support.

Use `non_inferential` only for statement, setup, or definition rows.
Every `verified` or `conditionally_verified` derivation must consume at least
one premise or strictly earlier move.

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

Every `counterexample` or `contradiction` failure must carry a
`failure.computation` record. Instantiate the failure numerically whenever
feasible: `status: instantiated` with a `script_file` under
`audit/05_adversarial/` (relative to the ledger directory), its exact
`script_sha256`, the exact `command`, and a substantive `output_excerpt`
showing the violation at concrete values, using exact or validated arithmetic
where rounding could matter. Otherwise record `status: not_instantiable` with
a substantive reason. Final validation rejects a refutation-kind failure
without this record, a missing script, or a stale script hash. The computation
falsifies only the exact encoded instance; it never replaces the recorded
mathematical failure analysis, and a counterexample that resists numerical
instantiation deserves heightened scrutiny before `refuted` is assigned.

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

Evidence must identify the actual source claim, mathematical objects, premises,
operation, and failure mode relevant to that record. The current evidence
contract treats repeated stock evidence as nonspecific under the exact gates in
[evidence-and-verdicts.md](evidence-and-verdicts.md). Do not use
generic checklist prose or cosmetic wording changes in place of local evidence.

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

The structural TeX scan is conservative and position preserving. It masks
comments, common command and environment definition bodies, inline `\verb`,
common verbatim-like environments, and branches that are definitely inactive,
such as the body of `\iffalse`. An unknown conditional, such as a project macro
or engine test, remains visible as candidate structure and creates a
review-required parser warning. It is never silently discarded. The stricter
local active-label gate accepts only a label known statically to be active, so
a label inside an unknown conditional cannot by itself certify a locked
anchor. The parser still does not expand macro invocations or execute TeX.
Inspect every unknown-conditional warning against the rendered or compiled
source, and do not rely on static masking alone.

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

Recompute algebra and rates. For a long calculation, preserve the source unit
and record its ordered atomic transitions as separate one-move steps referencing
that unit. Use a separate auxiliary calculation when needed.

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

Use [evidence-and-verdicts.md](evidence-and-verdicts.md) for severity and confidence.

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

Without `--final`, use `ledger-check` as a work-in-progress validator. Draft
mode permits incomplete checking and `not_checked` outcomes, but it does not
waive source-lock integrity, closure of populated links, or the exactly-one-move
rule for inferential steps. Fix those errors as soon as they appear. A clean
draft result says only that the current partial record is coherent.

For a manual ledger, or a compiled ledger later moved or modified, run
`ledger-check --final`. An unchanged compiled file with a passed compile receipt
already has this local gate. Resolve every uncovered or multiply covered source
line, stale or unrepresented source unit, missing or invalid source-unit
reference, non-atomic inferential step, unsupported status, missing issue
reference, and verdict mismatch. The local gate checks the record and declared
dependency statuses only; run `finalize` before any audit-wide verification
claim.

Compilation success does not establish that authored judgments are
mathematically true. It already includes the full final local ledger validator,
but it does not replace dependency closure, issue reconciliation, the
critical-path challenge, or audit-wide finalization.

For PDF-only input, create a UTF-8 numbered transcription for the exact page
range and pass that text file as `--paper` with
`--input-kind pdf_transcription`. Also pass the publisher PDF separately with
`--publisher-pdf`; a raw `.pdf` is rejected as the line-audit source. Record
the transcription hash and the separate publisher-PDF hash, byte size, and
nonauthoritative original location under `input_provenance`. These records
establish identity, not transcription accuracy.

Visually compare every displayed equation and symbol against the rendered
pages, record page and equation anchors in the contract, and manually build
the reviewed inventory. At scaffold, set `--visual-review-status` only to
`not_started` or `partial` and give specific `--visual-review-notes` for work
already performed. Scaffold cannot assert completion because page anchors and
completion time are not supplied through that command. After the actual visual
comparison, update `input_provenance.visual_review.status` to `complete` and
record a nonempty `reviewed_pages` string list, substantive `notes`, and a UTC
`completed_utc` timestamp. An incomplete visual review or manual inventory
keeps the audit nonfinal. State that LaTeX-level cross-reference, macro,
include-closure, and source-authenticity checks were unavailable. Do not claim
that either hash authenticates the transcription-to-PDF correspondence.

For a relocatable PDF audit, use `--portable-sources`. Both the transcription
and publisher PDF are copied into `audit/00_sources/` and hash locked there;
move the complete audit directory and verify it with `status` and
`delivery-check` after relocation.
