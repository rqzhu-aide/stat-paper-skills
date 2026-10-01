# Authoring graph records (contract 4)

Use this reference when the coordinator registers or refines the graph. Generate the selected collection's shape from the enforced contract with `template`; no code inspection is needed. All object fields below are required unless marked optional. Unknown fields are rejected.
`?` means JSON null is permitted, not that the field may be omitted. `[]` means an array, which may
be empty unless a stated rule requires members. IDs are stable strings; item labels and theorem
numbers are display text. Generate collection IDs with `ids --kind COLLECTION --count N`;
use the singular `--kind request` for request IDs.

Mint IDs in batches per kind, including request IDs, rather than launching a command per record.
Unused minted IDs need no database entry. Controller responses generate their own check,
observation, coverage and finding IDs; do not pre-mint those IDs for `work submit`.

Follow [mathematical text and JSON](mathematical-checking.md#mathematical-text-and-json)
for formula delimiters, backslash escaping, and unchanged source excerpts.

Run these examples from the [chosen work folder](database-audit.md#choose-the-work-folder);
`AUDIT.db` means its `audit.db`. The manuscript's registered source root is separate from
this working directory.

## Shared values

| Name | Exact shape or allowed values |
|---|---|
| Ref | `{collection, id}`; collection names the referenced record collection |
| Target | Ref restricted to `items` or `parts` |
| PinnedRef | `{collection, id, version}` with a positive integer version |
| Statement | `{form: "verbatim"|"transcription"|"synopsis", text: nonempty string}` |
| Passage | `{role: "statement"|"proof"|"definition"|"evidence", anchor_id: anchors ID}` |
| Origin | `"source"|"reconstruction"|"proposed_repair"` |
| Binder | `{symbol: nonempty string, domain: nonempty string, quantifier: "fixed"|"forall"|"exists"}` |
| Substitution | `{symbol: nonempty string, value: nonempty string}` |
| Locator | `{start_line: positive integer?, end_line: positive integer?, page: positive integer?, label: nonempty string?}` |
| Exclusion | `{target: Ref?, source_anchor_ids: [anchors ID], reason: nonempty string, consequence: nonempty string}` |
| Global task | `{kind: "global_consistency"|"adversarial"|"method_interface", applicability: "required"|"not_applicable", reason: string}` |

A locator supplies both start/end lines together with start no greater than end, or another location
method. Page locators require PDF source. An exclusion supplies a target or at least one source
anchor. Excluding an item removes that result and its parts from required audit work. Keep a missing
proof of a requested result in scope as a source limitation or unresolved examination.
A `not_applicable` global task needs a nonempty reason.

For non-PDF sources, `Locator.label` is a LaTeX source label key, not a descriptive caption.
With line numbers, its uncommented `\label{KEY}` must occur inside that range. Use null for
an unlabeled passage.

Capture source before anchoring. Submit the dedicated anchor request below with
`paper_audit.py source anchor AUDIT.db --request work/authoring/anchors.json`, replacing its example IDs
and line range with captured source and current packet identities:

```json
{
  "contract_version": 4,
  "request_id": "req_anchor_example",
  "packet_id": "pkt_author",
  "anchors": [{
    "id": "anc_statement",
    "expected_version": null,
    "source_id": "src_paper",
    "locator": {"start_line": 10, "end_line": 14, "page": null, "label": null}
  }]
}
```

Keep all four locator keys. This request asks the source command to capture the actual excerpt
and hashes; it is not an ordinary `apply` batch. Rebinding an existing anchor requires its current
`expected_version` rather than null.

One statement can continue across physical PDF pages while remaining one item. For already
captured anchors on pages 18, 19 and standing context on page 4, its existing `passages` can be:

```json
[{"role": "statement", "anchor_id": "anc_p18"},
 {"role": "statement", "anchor_id": "anc_p19"},
 {"role": "evidence", "anchor_id": "anc_p04"}]
```

A use supported by discontiguous passages can have `evidence_refs: ["anc_p08", "anc_p12"]`.
Target specifications likewise use `evidence_refs`; proof boundaries use pinned `anchor_refs`.
Keep separately audited conclusions as parts of that item. Existing report links show captured
files/pages or inclusive text lines; no duplicate nodes, location fields or comparisons are needed.

## Generate one record shape

```text
python "<skill-root>/scripts/paper_audit.py" template AUDIT.db --packet pkt_AUTHOR --collection items --out work/authoring/item-template.json
```

The output contains an uncommitted `template` batch and its contract-derived shape. Author
the scientific fields, then submit only the `template` member with `apply`. Blank placeholders
are not judgments. For a same-ID extension such as `application_details`, pass `--id use_ID`.
Generate only the needed collection. Keep coherent edits in one batch; do not launch one call
per field. Existing schema help remains available through the same command for every collection.

Major item kinds are `assumption`, `definition`, `lemma`, `proposition`, `theorem`, `corollary`,
and `external_result`. Intermediate kinds are `equation`, `claim`, `derivation`, and
`intermediate_result`, each with exactly one major `owner_id`. Other kinds have `owner_id: null`;
parts belong to major items. Preserve the manuscript declaration kind independently of origin.
A locally declared lemma remains a lemma even when attributed elsewhere; `external_result`
represents a result introduced only by citation.

Declaration kind, document provenance and availability are separate. A theorem belonging to
this paper's unavailable supplement remains a theorem with a source limitation. Locate its
bounded description in the supplied manuscript; do not invent its missing statement or proof.
Load-bearing outside results still need exact supplier inspection and application checking.

Supplements can use numbering from an earlier manuscript version. Match corresponding
statements and proof headings by content, hypotheses and cross-references, not a numerical
offset. If main Theorem 3.1 is proved as supplementary Theorem 1, keep one item with the main
label, retain the alternate name in `aliases`, and attach each passage to its actual file/page.
If hypotheses or conclusions differ, preserve the distinct exact targets or routes and explain
the mismatch; a matching heading does not establish coverage of the requested claim.

Use `equation` for a meaningful displayed relation or bound, `claim` for an assertion, and
`derivation` for a multi-step argument whose conclusion is not separately declared. Give
unnumbered content an honest descriptive label. Ownership locates material; it is not an inference
from the owner to the intermediate.

A scope's parent chain is acyclic. Argument/group scopes are global (`argument_id: null`) or local
to that same argument. Conditions are explicit mathematical restrictions, not commentary. Do not
put a needed local result in `assumptions` merely to avoid checking its proof.
List authorized setup premises explicitly, including a definition when its stipulated notation
or defining relation is used as context. This authorizes that definition in the scope, not any
unproved existence, measurability, boundedness, or other property of the defined object. Examine
those properties through their own supplier or inference. A verified external result instead
uses its exact target, source verification, and application; do not turn it into an assumption
to bypass missing support.

A target specification supplies exactly one of `statement_ref` and `statement`. Reference an
already exact shared statement by its version rather than duplicating its text. A synopsis instead
needs an exact, source-grounded statement and applicable scope. Use a separate target for a restricted
repair. `fidelity_ref` explicitly reuses a comparison of the same exact text, setup, and source versions.

`scope_id: null` on a target specification inherits no named scope. A scope with
`argument_id: null` is shared, but its premises apply only through the recorded scope context.
A proof using a premise in `scp_setup` can therefore leave a target outside that context
conditional even with all examinations complete. Choose the intended setup before broad
examination; null is valid when no named premise context is intended. Scope changes can reopen
source comparison and dependent checks; investigate unexpected support using current status.

For a new target, the simplest sequence is to save its final item/part and registered exact
specification with `fidelity_ref: null`, then compare that specification through its prepared
source-fidelity task. This directly checks the statement, setup, and captured source together;
there is no need to add a fidelity reuse reference afterward.

When explicitly reusing an item/part comparison, create the final specification before making
that comparison. For example, compare exact `items:itm_T@1` after its specification is registered,
obtaining `observations:obs_T@1`. In a fresh replacement of that specification, keep
`statement_ref: {collection: "items", id: "itm_T", version: 1}`, `statement: null`, and
set `fidelity_ref: {collection: "observations", id: "obs_T", version: 1}`. Keep the same `scope_id`.
Do not add or change the exact specification between comparison and reuse. Reuse only a current
observation whose source bindings cover
every `evidence_refs` anchor; identical display text is insufficient. Setup absent from that
examination, changed consumed source, or a synopsis needs a new exact-target comparison.
Older comparisons with strict relation bindings may require one fresh comparison even for
this metadata attachment. Preserve their original observations and bindings.

A packet may include `historical_records` containing the immutable statement version named by a
specification. These are read-only provenance outside the live record map and write scope.
To correct the saved representation of the same target:

1. Get a fresh author packet covering the item/part and existing specification.
2. Replace both in one batch, using complete bodies and current `expected_version` values.
   For example, replace `items:itm_T@2` and have the same specification pin `items:itm_T@3`.
   Set `fidelity_ref: null` when the old comparison no longer covers the text or setup; provide
   located `evidence_refs` covering both for direct comparison.
3. Commit, then use `work prepare` focused on that specification for a new source comparison.
   Compare the new statement and setup with source and submit through the comparison path;
   never create observations via `apply`.
4. Follow current work/status to renew affected mathematical and independent examinations.
   An edit or comparison alone does not complete this work.

Every `application_details` record uses the **same ID as its use**, with `use_id` equal to it.
Its optional `scope_id` defaults to the group's scope; use an explicit branch scope for branch
inputs. A registered application needs its group and exact `needed_form`. Draft extensions supply
no mathematical credit. Application checks target `uses`, consuming their extension; summary
connections without application details are not extra checked implications.

A registered argument has a final group belonging to that argument whose conclusion is its exact
target. Other groups conclude that target, an allowed target part, or an intermediate owned by its
major result. Each grouped use has `to` equal to its group's conclusion. Put all jointly required
inputs in the same group through separate use records. `proof_argument` means the consumer borrows
an internal argument; ordinary use of a result's statement is `dependency`. A `joint` group has
empty `case_scope_ids`; a `cases` group has a nonempty distinct list. Case scopes are local to the
argument, and discharged scopes must be permitted local/case scopes. Exhaustive cases require every
branch and checked coverage/discharge. Distinct sufficient proofs use separate arguments; they are
alternatives, not a cases group. Imported provenance-only groups with null argument and scope remain
annotations until refined into actual inferences. Use a retire edit to retire an
argument, rather than writing a live body with `lifecycle: "retired"`.

Focused audits name requested targets; the core derives their recorded prerequisites. Full audits
also reconcile the registered proof inventory. Both modes list exactly the three global task kinds
once each. Use `protocol_version: "item-audit/1"`. Qualification records are created through
`qualification record`, never fabricated in a graph batch.

The selection/refinement rules below apply to the audit's own result view or overview records
already embedded in a resumed proof-check audit, subject to the
[work-folder separation rule](database-audit.md#choose-the-work-folder).
Preserve a selected summary arrow `A -> T` when detail expands it through `A -> C -> T`.
A `connection_refinements` record links that summary use to the relevant detailed uses and argument.
For borrowed proof reasoning, the actual supplier can instead be an intermediate owned by A:
map the summary to `C -> T` without inventing `A -> C`. Ownership alone provides no support.
The refinement must explain the original source-backed contribution, and shared detailed applications
are checked once. Distinct uses, parallel contributions, and mixed outcomes retain their identities.

Such overview selections record their items, connections, main results, and source context independently
of audit scope. Adding audit-only detail does not silently enlarge that selection or its comparison
context. Ordinary overview edits preserve extensions; changing consumed mathematics reopens affected
work. A changed summary needs its own renewed comparison even when an unchanged exact target retains
current mathematics.

Coverage offsets are half-open character intervals into the anchor excerpt. Structural spans have
empty `claim_refs` and `check_ids`; substantive spans need both. Every linked check must be primary,
belong to the same audit and argument, and have its corresponding obligation satisfied. It must be
current and complete, or lead to such an examination through explicit `supersedes` successors.
Together, these examinations must have consumed every claimed item/part statement; citing its
source passage alone is insufficient. An extra unusable linked check prevents coverage credit.

Graph registration can precede complete coverage. Save controller coverage with its checks using
`check_task_ids`, pinned `existing_check_refs`, and `replaces` (null for new rows) from the generated
scaffold/guidance. Direct stored coverage instead uses `check_ids`; its enclosing create/replace
edit supplies identity and version. Generate the `coverage` template for that interface rather
than submitting a controller coverage row through `apply`.
Before asserting completeness, link the target and arguments to a `proof_boundaries`
record pinning all complete source segments and an accepted `source_reviews` record with
`purpose: "proof_boundary"`. Reuse the basis for routes sharing a written proof. Source/segment
changes require renewed review; an unresolved boundary cannot certify full coverage. Registration
never grants source-fidelity or proof credit.

## Reader explanations

While the written proof is already in context, ordinarily save two to four sentences in the
major item's optional `proof_idea`: the central mechanism, how important inputs combine, and
the decisive transition or restriction. A list of lemma labels or a restatement of the conclusion
does not explain the strategy. Reuse inspected sources and useful worker reasoning, checking the
summary against the written argument. Existing proof/source anchors should locate its basis;
add an anchor only when needed. Several written routes can share a summary that distinguishes
their recorded labels. Identify reconstructions and proposed repairs explicitly.

Write each `uses.reason` as the contribution of that supplier to its recorded recipient or step.
Save restrictions in `uses.regime`, uncertainty where applicable, and exact scope/application
records rather than merging branch conditions into theorem-wide assumptions. Keep distinct
applications and routes distinct even when they use the same supplier.

Save these explanations during ordinary authoring, preferably before existing source comparisons.
Later edits retain normal version/freshness rules; do not bypass invalidation to improve the report.
Do not add a separate summary review, mass backfill, or require strategy text for assumptions,
definitions or every intermediate. If the proof is unavailable or unclear, retain that limitation
and leave the summary absent rather than infer it from a verdict or generic composition check.
Strategy text supplies no proof credit and its absence is not an audit-completion gate. Any
suggested simulation or numerical validation remains an unperformed follow-up for the user.

## Authoring commands and envelopes

Capture source using `source capture AUDIT.db --files work/authoring/files.json`, where that file is an array of paths
relative to the source root. Source IDs come from the capture receipt. Obtain an author packet
covering the paper or affected records before writing:

```text
python "<skill-root>/scripts/paper_audit.py" get AUDIT.db --target papers:pap_ID --mode author --out work/authoring/author.json
python "<skill-root>/scripts/paper_audit.py" source anchor AUDIT.db --request work/authoring/anchors.json
python "<skill-root>/scripts/paper_audit.py" get AUDIT.db --target papers:pap_ID --mode author --out work/authoring/graph-context.json
python "<skill-root>/scripts/paper_audit.py" apply AUDIT.db --batch work/authoring/graph.json
```

`work/authoring/anchors.json` is exactly `{contract_version: 4, request_id, packet_id, anchors: [...]}`. Each entry
is `{id, expected_version: positive integer|null, source_id, locator: Locator}`. Use null for a new
anchor, the supplied current version to rebind an existing one. The script extracts the excerpt,
hashes and source version; do not invent those fields or create anchors through `apply`.

`work/authoring/graph.json` is exactly `{contract_version: 4, request_id, packet_id, edits: [...]}`. A create or
replace edit is `{op: "create"|"replace", collection, id, expected_version, body}`. Create uses null;
replace uses the packet's current version and the complete new body. A retire edit is
`{op: "retire", collection, id, expected_version, reason: nonempty string}`, with no body. Records
created in the same batch may reference one another. Reuse an unchanged successful request only
to retrieve its receipt; a new edit gets a new request ID.

## Review complete source boundaries

Read the actual source to identify every segment and continuation of the written proof. Create
a source review using a current author packet:

    python "<skill-root>/scripts/paper_audit.py" source review AUDIT.db --request work/authoring/boundary-review.json

The request is the same `{contract_version: 4, request_id, packet_id, edits}` envelope.
Each create edit targets `source_reviews` with body
`{source_refs: [PinnedRef], anchor_refs: [PinnedRef], purpose: "proof_boundary",
decision: "accepted"|"unresolved", rationale: nonempty string, reviewer: nonempty string}`.
Pin the captured source versions and all complete proof anchors. The rationale identifies the
source boundary, continuations inspected, and any limitation. An accepted decision is the author's
actual source review, not a value to infer from parser output.

Then create or replace `proof_boundaries` through ordinary graph authoring, linking that review
and its complete segment list to the exact target and all applicable arguments. Use
`state: "unresolved"` when the source unit's completeness remains uncertain. Registered argument
excerpts and coverage rows do not substitute for this reviewed basis.


## Worked examples

Use [the probability example](probability-example.md) for meaningful intermediate events,
denominator and ratio bounds, with source coverage and saved reasoning. It is an optional
authoring reference, not a worker assignment. The older
[minimal transitivity example](graph-example-transitivity.md) remains an interface illustration.
