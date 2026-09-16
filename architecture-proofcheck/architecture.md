# Proofcheck architecture

Date: September 12, 2026.

Status: complete target architecture for the next proofcheck implementation. The current runtime remains `stat-paper-proofcheck` v1.5 until the separate [revision plan](revision-plan.md) is implemented and accepted. This document defines the intended system in full; it does not require the previous architecture or a sequence of amendments to interpret it. The September 13 [implementation handoff](implementation-handoff.md) fixes its record, transaction, packaging, and reader interfaces.

## 1. Purpose and user experience

Proofcheck audits the written mathematical argument of a paper and produces a traceable assessment. It maintains a reusable dataset of assumptions, definitions, results, intermediate claims, and their actual uses. The checker works from prerequisites toward dependent conclusions, checking each local derivation and each application of another result.

The reader sees the paper's major mathematical items in the existing adapted Archify viewer. The visible graph contains assumptions, definitions, lemmas, propositions, theorems, corollaries, and relevant external results. Intermediate claims remain in the dataset and appear in the detail reader when a connection or result is selected. They are never added to the main graph merely because an audit records them.

Selecting a connection reveals the actual uses, intermediate steps, additional premises, source passages, and checks that it represents. Connection colors summarize their current assessment: green for checked support, red for a confirmed defect, gray for unchecked work, and amber for unresolved, conditional, mixed, or outdated work. Selecting a theorem exposes its complete derivation and final composition check, including steps that belong to no incoming connection.

The report should answer four questions promptly: what has been checked, what was found, which arguments may be affected, and what evidence or repair remains necessary. Useful draft reasoning and findings appear in working reports before the whole audit is finished.

This is a rigorous non-formal audit. Source hashes, valid records, complete graph traversal, successful rendering, and agreement between models do not constitute a formal proof certificate.

## 2. Scope and mathematical standard

### 2.1 Invocation and audit depth

The skill remains explicitly invoked by name. An overview request alone does not start a full proof audit.

| Mode | Work performed | Meaning of the output |
|---|---|---|
| Triage | Source preparation, major-item inventory, initial dependency map, and identified questions | A scoped map and checking plan; no completed-proof judgment |
| Focused | Selected conclusions and the exact internal prerequisites their arguments consume | A complete audit of that declared scope |
| Full | All proof-required results and written arguments in the declared manuscript scope, dependency applications, global consistency, and independent review | A complete audit of the declared paper scope |

Priority changes work order, not coverage. Exclusions identify the omitted material and the consequence for the assessment. A missing source or unresolved dependency can support an informative incomplete report. It cannot silently reduce the scope or justify a successful proof verdict.

### 2.2 What is checked

For every audited conclusion, distinguish:

1. **Statement fidelity:** the recorded claim preserves the source's hypotheses, quantifiers, domains, constants, probability qualifications, and target.
2. **Local argument validity:** the written reasoning establishes the claim given its recorded premises.
3. **Application validity:** each imported result supplies the form needed at that particular use.
4. **Dependency support:** the imported content is available with the required source and review standing.
5. **Statement assessment:** the claim is supported by the checked argument, remains unestablished, or has been refuted by specific evidence.

A proof gap does not imply that its theorem is false. A correct statement does not repair an invalid written proof. A supplied repair is recorded separately from the manuscript's argument. Assumptions are declared premises whose applicability is checked at their uses; they do not need to be proved within that same argument. Definitions may contain existence or well-posedness assertions that require checking when used.

Domain, dimension, sign, constants, rates, probability, quantifiers, and limits remain mathematical review concerns. The checker explains the relevant risks where they arise. The record format does not require eight repetitive risk rows for each line or heading.

## 3. System responsibilities and authority

| Component | Responsibility |
|---|---|
| Source layer | Capture manuscript versions, locate passages, enumerate declaration candidates, and report source-resolution limitations |
| Shared paper-record core | Maintain stable identities, source anchors, items, uses, history, bounded retrieval, and atomic edits |
| Audit layer | Store scope, arguments, coverage, checks, findings, independent responses, and reconciliation |
| Coordinator and checkers | Read sources, construct the mathematical interpretation, judge derivations and applications, and explain findings |
| Assessment and projection layer | Derive currentness, work queues, qualified summaries, connection traces, colors, and report counts from saved records |
| Archify reader | Present the major-item graph and the selected connection/result's detailed mathematical evidence |
| Publication layer | Render one consistent snapshot, preserve earlier deliverables on failure, and seal completed audit reports |

The paper database is the single authority for a new-format audit. JSON is an import, portable export, or proposed edit batch. HTML and optional Markdown summaries are generated views. There are no independently maintained manifest, issue-log, graph, and progress masters whose contents can drift apart.

The shared record and viewer core grows from `archify-proofs-overview`. Overview-only operation remains supported without audit records. Both skills use the same maintained contract and core behavior; proofcheck does not create another inventory or a separately authored graph for the same paper. Compatible shared runtime code and viewer assets are distributed through the user-wide skill installations, with explicit version/provenance checks. Installed behavior must not depend on the relative position of development repositories. There is no runtime download, project-local environment, database server, or additional graph service.

Code enforces record shape, allowed values, identities, references, snapshots, and declared evidence scope. It computes reachability and presentation. The agent determines whether the recorded dependencies are real, premises suffice, hypotheses apply, and reasoning is valid. The tool can reject an edge to a missing ID; mathematical review must detect an edge to an existing but inappropriate lemma.

## 4. Paper workspace and persistence

For a new audit, use a stable folder beside the manuscript or in the user's chosen output location:

```text
proofcheck-<paper-name>/
  proofcheck-report.html
  data/
    paper-records.sqlite
  work/                         optional edit batches and command receipts
  exports/                      optional portable record snapshots
  releases/                     immutable completed-report packages
```

The manuscript directory is registered independently from this output directory. Source snapshots and selected evidence are captured in the database; content blobs are deduplicated. Exact historical bindings remain reproducible. Source paths are relative to the registered manuscript root where possible.

When an overview database already exists, proofcheck explicitly attaches its audit records to that compatible database. It registers the report destination without creating a second writable paper master or forcing a folder move. A new database is created only for a deliberately separate paper/version lineage or an explicit import. An incompatible schema is diagnosed before any mutation.

Draft reasoning is stored in the database, including its target, examined scope, unresolved questions, and next action. Temporary files are conveniences, not the only surviving evidence. An interruption after saving a draft must permit continuation and an informative working report.

SQLite handles atomic updates and consistent snapshots. Transactions remain short and never span model reasoning. Workers read bounded packets and propose edits; a single integrating writer commits each batch. The store retains immutable versions of changed individual records. A batch can commit after an unrelated intervening edit when its generated read set, write expectations, and relevant relation memberships still match. A relevant conflict returns precise changed inputs without losing the proposal. Unrelated bookkeeping does not change mathematical check identities. No agent should write source hashes, timestamps, adjacency lists, or generated report totals manually. The handoff defines the exact protocol and migration from the overview's current whole-dataset snapshots.

## 5. Dataset contract

### 5.1 Identities and controlled fields

Items, uses, source anchors, arguments, checks, findings, and review responses have stable string IDs. IDs follow a validated format and are unique within their record collection; cross-collection references identify the collection as well as the ID. Printed numbering is a label, not identity. Renaming Lemma 2.3 to Lemma 3.1 preserves its ID. Multiple manuscript labels can be aliases of one item. Splits and merges require an explicit old-to-new mapping.

Item `kind` uses the following closed list:

`assumption`, `definition`, `lemma`, `proposition`, `theorem`, `corollary`, `external_result`, `intermediate_result`.

Use `type` retains the closed list `dependency`, `definition`, and `proof_argument`. The last denotes reuse of an internal argument rather than solely a theorem's stated conclusion. Adding a new kind is a schema change, not an arbitrary label typed by a worker.

Labels, captions, mathematical statements, explanations, and applicability notes are authored text. Statement `form` is `verbatim`, `transcription`, or `synopsis`. A synopsis always retains access to the exact source passage. The record distinguishes `source`, `reconstruction`, and `proposed_repair` origins so a checker-supplied argument cannot silently become the paper's proof.

### 5.2 Logical records

These are logical record groups stored as individually versioned typed JSON bodies in a shared records table. They do not require a separate physical SQL table per mathematical concept. Each edit appends only changed records, rather than another whole-dataset payload. The exact fields and storage constraints are in the [record contract](handoff/record-contract.md) and [DDL](handoff/schema.sql).

| Record | Essential content |
|---|---|
| Source revision and anchor | Registered source identity; captured bytes; exact passage locator and excerpt; locator-check method and source limitation |
| Item | Stable ID, mathematical kind, reader label/caption, statement, statement/proof passages, and any owning result/local scope |
| Use | Stable ID, source and target item/part references, use type, argument membership, contribution, use-site evidence, and necessary instantiated form or substitutions |
| Argument and scope | Target conclusion, inputs required together, local hypotheses, proof route or case, and any hypothesis-discharge or case-completeness obligation |
| Coverage | Source spans, their responsible claims/checks, structural-text classification, and remaining substantive passages |
| Check | Exact target and input versions, draft/completed state, reasoning, examined passages, local outcome, unresolved conditions, and linked findings |
| Finding | Exact item/use/argument target, observed concern, evidence, classification, lifecycle, impact assessment, and separately identified repair proposals |
| Independent response and reconciliation | Blinded target scope, original response, independent judgments/reasons, comparison with primary work, and recorded resolution or disagreement |
| Audit scope and publication | Requested mode and targets, source/external limits, checker qualification, required reviews, derived progress, and released snapshot identity |

Source-fidelity comparisons remain separate from proof checks. Existing overview `matched` observations never become successful mathematical assessments merely by import or renaming.

### 5.3 Major and intermediate items

All in-scope major declarations receive records. Relevant unnumbered assumptions, definitions, and external results are recorded when they materially support the proof system. An external restatement without a local proof is legitimate; it has a source-verification task rather than a missing-local-proof defect.

Create an intermediate item for a significant bound, event, construction, reduction, limit, reusable assertion, disputed inference, or useful checkpoint. Preserve its exact scope. Routine algebra can be explained in a concise derivation spanning several source lines. Further splitting follows mathematical need, not physical layout. Headings have coverage markers and no proof verdict.

An intermediate item's owner groups it under a proof or result. Ownership is not an inference edge. A locally fixed point, conditioned event, or temporary contradiction hypothesis is recorded in its argument scope and inherited through uses until explicitly discharged. Reusing that item in another proof requires a compatible application check; ownership alone grants no exportable conclusion.

Separately used theorem parts are addressable by stable part IDs under the parent item. They retain their own statement bindings and assessments. The visible theorem remains one major node, with mixed part outcomes shown in its detail reader. The system never promotes a check of one part to a check of the entire statement.

### 5.4 Uses and complete local arguments

Store each actual application once, at the claim whose argument makes it. Different applications of the same lemma have different use IDs, even when endpoints coincide. On refinement, an existing use can be retargeted to the appropriate intermediate claim while preserving its identity and evidence when it is the same application. The overview does not receive another manually authored copy of that dependency.

The source item is referenced, not copied into every use. A concise `needed_form` and explicit substitutions are recorded when they clarify the exact application. Its check compares the form available from the supplier with the form required by the consumer, including hypotheses, domains, probability, quantifiers, and parameters.

A local derivation identifies its inputs required together. One ordinary argument is the default. When the source provides complete alternative proof routes, they remain separately identified; when it divides into cases, the cases and the argument establishing their coverage are recorded. A route's applicability is not an uncertainty label. A union of arrows across routes is not a sufficient proof.

For example, from

\[
\Pr(A)\geq 1-\delta,\qquad \Pr(B)\geq 1-\delta,
\]

the generally available joint bound is

\[
\Pr(A\cap B)\geq 1-2\delta.
\]

The combination is a checkable derivation with both inputs, not a consequence of drawing two individually plausible arrows. A target failure probability of \(\delta\) requires an applicable allocation such as \(\delta/2\) to each input or other valid reasoning.

The final composition check belongs to the target result. It examines how the supporting claims establish its exact conclusion. It is required even when all imported uses have successful checks, and even when the proof has no incoming major-item connections.

### 5.5 Checks, findings, and completion

A check records `draft` or `complete` work separately from its local outcome: `supported`, `gap`, `refuted`, or `inconclusive`. A draft can contain a tentative outcome, but it cannot count as a completed successful check. Refutation requires evidence for the exact assertion being refuted, including an instantiated counterexample when that is the basis of the claim.

Freshness is derived as `current`, `needs_review`, or `historical`. Dependency support is derived as `available`, `conditional`, or `unavailable` relative to the declared scope. These are distinct from the local reasoning outcome. A checked derivation given an unverified lemma retains its reasoning while its overall support is qualified.

Findings use a controlled classification separating `presentation`, `proof_gap`, `dependency_mismatch`, `statement_refutation`, and `inconclusive`; source-resolution problems remain separately identified source findings. Lifecycle distinguishes open, resolved, and superseded records. Importance, affected conclusions, and repair costs are justified judgments, not consequences of a graph distance or node degree. Code derives potential downstream reach; the reviewer records which uses are actually affected.

A repair has its own target, proposed change, changed assumptions or scope, and verification state. Distinct remedies are not called alternatives unless they address the same problem as alternatives. A proposed repair neither edits the manuscript automatically nor erases the original finding.

A successfully checked repair also preserves the assessment of the written proof. A supplemental argument for the unchanged statement is a separately identified argument with its own checks. A repair establishing only a restricted statement supports that separate form, including its additional conditions; consumers must explicitly use that form and have its conditions checked. Neither kind silently turns the original defective route green. A revised manuscript receives a new source version and a reviewed reassessment of the changed argument.

## 6. Source preparation and coverage

Capture the main manuscript, relevant appendices, local mathematical macros, bibliographic evidence, and other explicitly used sources. Use source labels and exact passages where available. Printed numbering and PDF pages require their own supported binding; a TeX line number is not a PDF page number.

Source scanners produce declaration and citation candidates. The checker reviews custom environments, conditional branches, aliases, split proofs, and relevant text outside formal theorem blocks. Complete proofs may have multiple passages in several files. Every active citation used by an item is drawn from one consistent statement/context/proof inventory; a no-proof restatement cannot receive conflicting authoring and finalization requirements.

Custom TeX source selection must have a supported resolution path. Literal supported conditions can be resolved by code. Other branches retain a reviewed source-selection record with exact evidence. A conservative parser's inability to confirm a label is reported as a source limitation, with an actionable location, rather than fabricated as a mathematical inference failure. Changed source bytes always create a changed source identity, even when line numbers are preserved.

Coverage maps all substantive passages in the declared written argument to their claims and checks. It also classifies structural text cheaply. A claim may own several consecutive algebraic steps, and a passage may support several claims through explicit references. Missing or unexamined substantive spans remain visible. The system checks interval/reference consistency, while the reviewer remains responsible for the meaningful coverage of the argument.

External results are verified in the exact form used, including authoritative statement, assumptions, applicability, and source location. Missing access is an unresolved dependency, not a license to reconstruct an uncited theorem from memory. Numerical or symbolic experiments can support a specific diagnosis but do not replace a general proof.

## 7. Checking workflow and orchestration

1. **Prepare source and scope.** Resolve environment/source limitations, capture the selected sources, identify exclusions, and build the major-item inventory. Render an initial working overview with explicit inventory limits.
2. **Qualify checkers.** Preserve the balanced calibration protocol and its blinded keys for the declared reviewer profile/configuration. Passing is an entry requirement, not evidence that this paper is correct. Context-only handoffs under the same qualified configuration do not require repeating calibration.
3. **Map actual uses.** Read the relevant statements and arguments. Register dependencies and local context. Prioritize the theorem chain, prerequisite bottlenecks, and important findings without reducing scope.
4. **Check prerequisites before dependent results.** Retrieve a bounded packet containing the target, local proof, needed scope, incoming uses, and consumed prerequisite content. Read additional context when needed. Independent branches may be checked concurrently; database writes remain coordinated.
5. **Develop and save local work.** Register meaningful intermediate claims while checking the written derivation. Check individual applications and combined inferences. Save drafts, completed checks, findings, and next actions directly; there is no separate full-ledger publication barrier.
6. **Close a result.** Verify substantive coverage, local scopes and discharges, all required cases, use applicability, and final composition against every in-scope conclusion. Preserve a conditional assessment when dependency support remains unresolved. Reconcile concrete findings and potentially affected uses.
7. **Perform independent review.** Every in-scope proof-required result receives a fresh-context review of its complete declared argument, applications, and relevant source context. Long proofs can be divided into bounded assignments only when their integration and final conclusion are also covered. Keep primary outcomes, findings, check justifications, inferred proof reconstructions, and proposed repairs out of the initial blinded checking packet. A source-faithful inventory may locate the material, but the challenger independently assesses normalization, applicability, and dependency interpretation. Preserve the original independent response before explicit reconciliation. Unresolved disagreements remain visible and prevent an unqualified supported assessment.
8. **Complete cross-paper checks.** Examine assumption/definition propagation, domains and notation, constants and rates, probability and conditioning, quantifiers and regimes, actual later-use sufficiency, and finding propagation. Include relevant adversarial cases. Method-to-implementation interfaces are examined when the paper's claims or requested scope require them; otherwise record the scope decision once.
9. **Checkpoint and deliver.** Save the next actionable work, regenerate the working report from one committed snapshot, and show coherent progress. Release as complete only after the declared scope, required independent review, global work, and reconciliations are accounted for.

The scheduler uses the detailed item/use graph, not the major-only display graph. Assumptions, definitions, and verified external sources provide starting context. A dependent argument can be examined provisionally before an upstream uncertainty is resolved, but its standing remains conditional. Cycles are inspected for genuine circular use, local hypotheses, induction, mutually proved assertions, or alternative routes. Topological order is used only where the recorded argument actually supports it; induction and simultaneous proof obligations need explicit local justification.

The bounded controller is a synchronous tool used by the coordinator. The coordinator builds and refines the graph, selects a scientific focus and dispatches reviewers. `work list` derives obligations from saved records; `work prepare` groups complete inference context into one assignment; `work submit` validates and atomically records the explicit response; `work inspect` recovers preparations and original input. The controller never calls a model or infers a premise omitted from the graph.

A ready unit seeds an assignment that may include its local successors and final composition. One model call can therefore produce several separately addressable application, derivation and composition checks. Completed negative examinations do not create an endless scheduling wait. Local validity under exact premises remains separate from the support available upstream. A partial response saves its included records, and unchanged reasoning can be resumed against refreshed context. The [controller implementation plan](controller-implementation-plan.md) specifies these interfaces and bounds.

The graph guides work; it never marks mathematics correct because predecessors are green. A complete Full audit accounts for all in-scope written routes and their defects even if a separate valid route supports the same conclusion.

## 8. Preserving checks through changes

Stable identity, recorded content version, and source version are separate. Every check retains the exact material it assessed. History is append-only evidence; a later check does not rewrite an earlier conclusion or its inputs.

A local check's semantic inputs are its claim, written derivation, local/global context actually in force, required uses and argument grouping, and the precise prerequisite content it consumes. A use check binds the particular application and supplied form. A borrowed `proof_argument` additionally binds the internal passage or claim actually reused. Reviewer qualification and protocol identity remain review provenance and compatibility inputs.

Outgoing consumers, report layout, labels used solely for presentation, observation timestamps, and unrelated issue or build records are not mathematical inputs to the supplier's local proof check. Reusing one result in a new place must not require regenerating that result's whole proof record.

| Change | Work made necessary |
|---|---|
| New consumer of a checked lemma | Check the new use and its receiving derivation; preserve the supplier's local check |
| Changed statement or relevant assumption | Review uses consuming that changed content and the conclusions they support |
| Changed supplier proof with the same supplied statement | Recheck the supplier; retain the consumer's conditional derivation while updating dependency support |
| Changed borrowed internal argument | Recheck applications that borrow that argument, even if the supplier's headline theorem is unchanged |
| Relocated passage or changed printed number | Review the binding and reader label; preserve unchanged mathematics after that review |
| Changed global notation, macro, or inherited hypothesis | Inspect the source diff and its actual effect before approving reuse |
| Added finding or a new independent response | Update assessment and impact views; do not change unrelated mathematical input identities |
| Changed checker configuration or audit contract | Requalify as required and explicitly determine which existing reviews meet the new contract; never silently restamp them |

The system computes a candidate impact set and explains why each target needs attention. Reachability means potential impact, not confirmed mathematical failure. An unchanged excerpt alone cannot establish unchanged meaning when global context has changed. Unknown source-context changes keep relevant checks pending until reviewed; a focused reviewed-reuse operation can preserve those shown to be unaffected.

Saved checks can remain valid statements of local reasoning while overall support changes. For example, a consumer may retain “argument checked given Lemma A” after A's proof is questioned, with dependency support now conditional. This prevents both loss of useful work and unwarranted green conclusions.

No user or worker manages `_r2`/`_r3` filenames to renew a check. The integrating writer records a new version and the reason for reassessment, preserving the earlier record and all finding references automatically.

## 9. Major-item graph and connection projection

### 9.1 One detailed dataset, one major-only diagram

The canonical graph contains the mathematical items and their actual uses, including hidden intermediate claims and separately addressable conclusions. The displayed graph contains only major items. There is no expanded intermediate graph or detailed-graph toggle. Intermediate reasoning is read as linked steps in the lower detail panel.

The projection derives a displayed connection from actual uses and supporting intermediate claims connecting major items. It retains the full set of canonical use IDs, claim IDs, and route/case memberships represented by that connection. Connections are never authored separately from the dataset or inferred from citation co-occurrence. Stop a projected dependency trace at another major item: a path through that item does not create an additional direct connection unless a distinct recorded application supports it.

Define a visible owner for each endpoint: a major item owns itself, and each hidden claim or statement part maps to its owning major result. Project each actual use through those owner references. Omit connections whose displayed endpoints have the same owner, and group the remaining uses by displayed endpoints while preserving separate route/case entries. This defines the diagram's connections without computing all-pairs reachability. For each represented use, its detail includes the relevant internal supporting claims and shared inputs. The target result's final composition check may be linked from that detail, but belongs to the result assessment and is not included indiscriminately in every incoming connection's color.

When several uses share displayed endpoints, the overview may combine them with a use count. The detail reader lists the constituent uses and qualifications separately. Internal links within a major result are omitted from the diagram but remain in its complete derivation trace. Source-free local steps also remain accessible from that result. The system checks that every canonical item/use has an explicit reader location, even if it has no drawn element.

A connection trace contains the actual contributing claims in a dependency-compatible reading order, with branches and joint inputs visible. It does not choose a shortest graph path as the proof. An intermediate step shared by several traces retains one ID and one source/check record; each distinct application has its own use check.

### 9.2 Cycles and alternatives

Collapsing intermediate claims into their owning results can create a cycle absent from the detailed argument. For example, an intermediate inside T may support L, and L may then support T. Combining alternative routes can also create an apparent cycle. These are distinguished from a cycle already present in the actual use graph.

The initial implementation keeps the same Archify shell and detail reader, but uses a complete major-item/connection index when a truthful graph projection cannot be laid out. Explain the implicated connections and routes. Never delete a real edge, invent a duplicate major result, expose intermediate graph nodes against the chosen UI, or call a projection cycle a circular proof without examining the argument. A new cycle-aware layout engine is not required for this release.

### 9.3 Connection assessment and colors

Colors are derived from saved current checks, not assigned by the renderer or guessed from captions. Every color has a text label and accessible explanation.

| Display state | Rule |
|---|---|
| Green: checked | Every represented use and required supporting derivation is currently supported, with relevant dependency support available under declared premises |
| Red: defect identified | A current, completed assessment identifies a proof gap, invalid application, or refuted assertion within the represented use/derivation |
| Gray: not checked | No completed or substantive draft assessment exists for the represented work |
| Amber: needs attention | Work is partial, conditional, stale, inconclusive, disputed, or mixes checked and unchecked constituents |

A current confirmed direct defect takes precedence over mixed incomplete work, and its detail lists both. A defect recorded only against an older changed input is historical evidence and yields a recheck qualification rather than a current red assertion. Open independent disagreement yields amber until reconciled. An upstream problem makes a consumer conditional or potentially affected; it does not automatically color that consumer red.

Grouped connections retain per-use states. A red group means a defect exists in a represented use, not that every use is invalid. If an alternative argument succeeds while another contains a defect, the route list makes that distinction explicit. Green does not mean independently reviewed unless that separate review indicator is present. A presentation-only finding can coexist with supported mathematics and should not falsely turn a valid application red.

All green incoming connections do not establish a theorem. Its full assessment also requires its own final composition, source coverage, scope discharge, cases, and the declared review work. Node type colors remain separate from review badges.

## 10. The Archify reader

Reuse the actual adapted Archify viewer: its type palette, compact labels and captions, main-result navigation, selection, zoom, readable/fit views, themes, search, keyboard access, and export conventions. Reuse the static mathematical rendering path and retain explicit source text when a formula cannot be rendered reliably.

### Opening view

Show the paper identity, source/build version, declared scope, and concise assessment. Separate counts for major results, mapped scope, local reviews, drafts, findings, and independent reviews. Do not pool assumptions, intermediate claims, and proof-required results into one misleading completion percentage. The graph stays at major items throughout navigation.

The opening finding summary states the observed problem and its consequence, with linked key findings and individually identified repair directions. It must not transform inconclusive evidence into a defect or infer a clean audit from an empty finding list. A completed audit can report defects or a qualified inconclusive result.

### Selecting a connection

The existing reader below the graph shows:

1. The selected major-item connection and its represented uses, separated by route/case.
2. **Required here:** the form needed by the receiving argument.
3. **Supplied by the result:** the particular statement or proof argument available from the source.
4. **Intermediate reasoning:** linked claims and their derivation checks, with joint inputs and local conditions visible.
5. **Assessment and evidence:** current outcome, precise findings, examined passages, dependency qualifications, and independent-review state.

Show concise reasoning first. Long passages, historical checks, and complete source excerpts can use disclosures. A connection from A to T must expose other inputs its internal steps require; it does not imply that A alone proves T. Shared claims link to the same record wherever they appear.

### Selecting a result

The result reader shows its full statement or labeled synopsis, exact source, assessed parts, overall qualified outcome, and complete written-argument trace. It includes incoming applications, locally established intermediate claims, the final combination, temporary-hypothesis discharge, and unexamined passages. A result with no incoming connection still has a complete reader and checking task.

Assumptions display as declared premises; definitions display their meaning and any separately assessed well-posedness assertions. External results show the exact supplied form and source-verification state. A source-layout limitation has its own explanation rather than pretending to be a mathematical counterexample.

### Search, findings, and navigation

Search indexes the whole dataset, including hidden intermediate claims and finding descriptions. Choosing an intermediate claim opens its owning result's detail and focuses that claim, keeping the major graph unchanged. Stable links can address a result, use, claim, finding, or historical check without relying on printed numbering.

Selecting a finding focuses its precise origin. “Trace potentially affected results” displays recorded downstream candidates and route qualifications; directly defective and potentially affected work remain visually distinct. The full index provides a linear reading option and access to all records, including material hidden by graph filters.

A working HTML file is a snapshot, not a live database client. Its source version and build time are visible. On a successful checkpoint, all counts, traces, colors, finding lists, and summaries are generated from the same committed snapshot. If rendering fails, the previous HTML remains identifiable as the earlier report and current saved work remains available in the database.

## 11. Validation, independent review, and release

### Three kinds of assurance

| Assurance | What it establishes |
|---|---|
| Record validation | Allowed fields/values, stable identities, existing references, valid source bindings, coherent groups/coverage, and recoverable history |
| Mathematical review | Source fidelity, valid reasoning and applications, justified findings, and explicit dependency/scope qualifications |
| Artifact validation | The delivered reader preserves the selected snapshot, accessible items/uses/checks, correct derived states, and supported rendering behavior |

Keep structural validators usable while drafting. A missing future review note should not block reading a source passage, storing a draft finding, or rendering an explicitly incomplete report. Completion checks run against the declared scope; they do not force workers through inconsistent local and final versions of the same rule.

Independent review preserves the primary check and the challenger's original response separately. Reconciliation must cite actual agreement, disagreement, and changed reasoning. The visible summary states which results have independent review. Blinding is not claimed when the review context contained the primary answer. Missing independent capacity is reported as incomplete required review.

### Working and completed reports

Working reports can always be generated from structurally valid records, with incomplete coverage and provisional judgments visible. Completion is a status of the audit process, separate from whether all statements were established. The audit may be complete with defects or explicitly adjudicated inconclusive findings, provided that the required scope and review activities were actually performed. Undone work, unreviewed exclusions, and missing required independent reviews cannot be relabeled as completed inconclusive work.

A completed publication requires coherent source selection and declared scope, accounted substantive arguments and conclusions, completed required primary and independent work, reconciled review records, global checks, and an evidence-backed assessment of outstanding findings. Unresolved mathematical questions retain their qualifications and cannot receive an unqualified supported verdict.

Render a fixed database snapshot and validate the actual graph/index identities and detail accessibility. Every visible connection maps to the exact underlying uses and traces. Check formula rendering and source fallbacks. Inspect the real reader for long mathematics, dense major graphs, selected connections, themes, keyboard navigation, and usable narrow layouts. Automated geometry checks do not claim visual or mathematical review.

Publish a completed report and its manifest into a new immutable release directory. Record source/data snapshot, protocol/core/renderer identity, report bytes/hash, completed review coverage, and actual artifact/browser inspection. Atomically update the current-report pointer or top-level copy after successful publication. A failed publish preserves the preceding release. Rendering the same evidence requires no model call. Historical reports remain available and are never silently restamped as current.

## 12. Compatibility and distribution

New-format audits use the shared database contract with explicit schema/feature versions. An overview-only reader can project major items from a compatible database without treating audit observations as source comparisons. Unsupported audit extensions produce an explicit compatibility result rather than being discarded during an edit.

Existing v1.5 JSON audits retain their original files, hashes, protocols, and finalization seals. A legacy reader remains available during transition. Import into a separate new-format working database records the old identities, classifications, source evidence, and mapping. Old scratchpad notes enter as drafts. Old `verified` strings and FINAL seals do not automatically satisfy a new checking contract.

Compatible reasoning can be reused after its exact target, inputs, evidence, and review scope are compared. Retain imported ledgers as historical attachments rather than turning every old heading or setup step into an intermediate item. Preserve gaps as gaps, conditional judgments as conditional, and independent responses with their original provenance. Ambiguous or incomplete mappings remain visible work.

Use shared installed Python, standard SQLite, the shared mathematical converter, and Node for the viewer. Reuse maintained source and rendering components through a versioned distribution boundary; do not depend on an unrecorded sibling checkout or create per-paper bookkeeping programs. Installation and release testing must exercise the packaged runtime, not only a development tree.

## 13. Evaluation and operating cost

Acceptance covers both mathematical usefulness and software behavior. Small fixtures exercise IDs, aliases, split passages, shared intermediate claims, grouped uses, local scopes, cases, alternatives, mixed outcomes, source changes, interruption/resume, and old-audit import. The two observed DRL blockers, conditional-label resolution and cited no-proof restatements, are required source exercises.

A realistic short audit must reach a useful working report, completed local reasoning, independent review/reconciliation, and final publication. A subsequent large-paper trial tests whether the dataset and reader remain usable. Software tests with fixed synthetic judgments do not establish proof-checking accuracy.

Measure source reading/reasoning, record authoring, command execution, retries, repeated context retrieval, preserved checks, record expansion, time to a useful partial report, and total elapsed time separately. Record actual model usage only when available. Avoid promising a speedup based on file sizes or renderer timing alone.

The design is successful when mathematically meaningful work is easier to trace and reuse, ordinary text does not trigger elaborate proof paperwork, a new consumer does not erase a supplier's check, and the user's report stays faithful to the evidence throughout a long audit.

## 14. Document ownership

This file is the complete target architecture. [implementation-handoff.md](implementation-handoff.md) fixes concrete interfaces and implementation ownership; [revision-plan.md](revision-plan.md) defines the implementation and migration sequence from the current runtime. [README.md](README.md) is the short entry point.

Earlier architectures, plans, experiments, and release receipts are preserved under [archived/pre-item-graph-2026-09-12](archived/pre-item-graph-2026-09-12/README.md). They document their own historical versions and do not override this design. The [DRL case review](archived/pre-item-graph-2026-09-12/drl-case-review-2026-09-12/review.md) records the observed failures motivating this architecture; its mathematical findings were not independently reverified by the workflow review.
