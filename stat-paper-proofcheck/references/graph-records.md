# Authoring graph records (contract 3)

Use this reference when the coordinator registers or refines the graph. The installed core's
`contract.py` defines the enforced shapes; these tables provide the same authoring fields without
requiring code inspection. All object fields below are required. Unknown fields are rejected.
`?` means JSON null is permitted, not that the field may be omitted. `[]` means an array, which may
be empty unless a stated rule requires members. IDs are stable strings; labels and theorem numbers
are display text. Generate fresh IDs with `ids --kind COLLECTION --count N`.

Mint IDs in batches per kind, including request IDs, rather than launching a command per record.
Unused minted IDs need no database entry. Controller responses generate their own check,
observation, coverage and finding IDs; do not pre-mint those IDs for `work submit`.

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
anchor. A `not_applicable` global task needs a nonempty reason.

## Closed record bodies

The collection and ID belong to the edit envelope, not inside these bodies.

| Collection | Complete body fields |
|---|---|
| `items` | `kind`, `label: nonempty string`, `caption: string`, `statement: Statement`, `passages: [Passage]`, `aliases: [nonempty string]`, `uncertainty: string?`, `origin: Origin`, `owner_id: items ID?`, `scope_id: scopes ID?` |
| `parts` | `item_id: items ID`, `label: nonempty string`, `statement: Statement`, `passages: [Passage]`, `scope_id: scopes ID?`, `origin: Origin` |
| `scopes` | `argument_id: arguments ID?`, `parent_id: scopes ID?`, `assumptions: [Target]`, `binders: [Binder]`, `conditions: [nonempty string]`, `evidence_refs: [anchors ID]` |
| `arguments` | `target: Target`, `label: nonempty string`, `origin: Origin`, `scope_id: scopes ID`, `final_group_id: groups ID?`, `evidence_refs: [anchors ID]`, `lifecycle: "draft"|"registered"|"retired"` |
| `groups` | `argument_id: arguments ID`, `conclusion: Target`, `kind: "joint"|"cases"`, `scope_id: scopes ID`, `case_scope_ids: [scopes ID]`, `discharges: [scopes ID]`, `rationale: nonempty string`, `evidence_refs: [anchors ID]` |
| `uses` | `from: Target`, `to: Target`, `type: "dependency"|"definition"|"proof_argument"`, `group_id: groups ID?`, `reason: nonempty string`, `needed_form: Statement?`, `substitutions: [Substitution]`, `evidence_refs: [anchors ID]`, `regime: string?`, `uncertainty: string?` |
| `audits` | `paper_id: papers ID`, `mode: "triage"|"focused"|"full"`, `targets: [Target]`, `exclusions: [Exclusion]`, `protocol_version: string`, `independent_required: boolean`, `qualification_id: qualifications ID?`, `global_tasks: [Global task]`, `report_path: string` |
| `coverage` | `argument_id: arguments ID`, `anchor_id: anchors ID`, `start_offset: nonnegative integer`, `end_offset: nonnegative integer`, `classification: "substantive"|"structural"`, `claim_refs: [Target]`, `check_ids: [checks ID]`, `note: string` |

Item kinds are exactly `assumption`, `definition`, `lemma`, `proposition`, `theorem`, `corollary`,
`external_result`, and `intermediate_result`. An intermediate has exactly one major `owner_id`.
Every other kind has `owner_id: null`; parts belong to major items. Use `external_result` for a cited
result and distinguish checking its exact application from verifying its source statement.

A scope's parent chain is acyclic. Argument/group scopes are global (`argument_id: null`) or local
to that same argument. Conditions are explicit mathematical restrictions, not commentary. Do not
put a needed local result in `assumptions` merely to avoid checking its proof.

A registered argument has a final group belonging to that argument whose conclusion is its exact
target. Other groups conclude that target, an allowed target part, or an intermediate owned by its
major result. Each grouped use has `to` equal to its group's conclusion. Put all jointly required
inputs in the same group through separate use records. `proof_argument` means the consumer borrows
an internal argument; ordinary use of a result's statement is `dependency`. A `joint` group has
empty `case_scope_ids`; a `cases` group has a nonempty distinct list. Case scopes are local to the
argument, and discharged scopes must be permitted local/case scopes. Use a retire edit to retire an
argument, rather than writing a live body with `lifecycle: "retired"`.

Focused audits name requested targets; the core derives their recorded prerequisites. Full audits
also reconcile the registered proof inventory. Both modes list exactly the three global task kinds
once each. Use `protocol_version: "item-audit/1"`. Qualification records are created through
`qualification record`, never fabricated in a graph batch.

Coverage offsets are half-open character intervals into the anchor excerpt. Structural spans have
empty `claim_refs` and `check_ids`; substantive spans link the examined claims and checks. Graph
registration can precede complete coverage. The primary controller response can save coverage with
its checks using task IDs; its response shape in [controller-workflow.md](controller-workflow.md)
differs from the stored coverage body above. Registration never grants source-fidelity or proof credit.

## Authoring commands and envelopes

Capture source using `source capture DB --files FILES.json`, where `FILES.json` is an array of paths
relative to the source root. Source IDs come from the capture receipt. Obtain an author packet
covering the paper or affected records before writing:

```text
python "<skill-root>/scripts/paper_audit.py" get AUDIT.db --target papers:pap_ID --mode author --out author.json
python "<skill-root>/scripts/paper_audit.py" source anchor AUDIT.db --request ANCHORS.json
python "<skill-root>/scripts/paper_audit.py" get AUDIT.db --target papers:pap_ID --mode author --out graph-context.json
python "<skill-root>/scripts/paper_audit.py" apply AUDIT.db --batch GRAPH.json
```

`ANCHORS.json` is exactly `{contract_version: 3, request_id, packet_id, anchors: [...]}`. Each entry
is `{id, expected_version: positive integer|null, source_id, locator: Locator}`. Use null for a new
anchor, the supplied current version to rebind an existing one. The script extracts the excerpt,
hashes and source version; do not invent those fields or create anchors through `apply`.

`GRAPH.json` is exactly `{contract_version: 3, request_id, packet_id, edits: [...]}`. A create or
replace edit is `{op: "create"|"replace", collection, id, expected_version, body}`. Create uses null;
replace uses the packet's current version and the complete new body. A retire edit is
`{op: "retire", collection, id, expected_version, reason: nonempty string}`, with no body. Records
created in the same batch may reference one another. Reuse an unchanged successful request only
to retrieve its receipt; a new edit gets a new request ID.

## Complete small graph example

The linked [graph-example-batch.json](graph-example-batch.json) creates three source-linked items,
one shared scope, one complete registered route, one joint group, its two uses, and a focused audit.
It contains no checks or findings. This example's audit is primary-only to demonstrate authoring;
that setting is not a substitute for the independent review required by a formal audit.

First create a separate example paper directory with `paper.txt` containing these exact five lines:

```text
Let u, v, w be real numbers.
Assumption A: u <= v.
Assumption B: v <= w.
Theorem T: u <= w.
Proof. By transitivity, u <= v and v <= w imply u <= w.
```

Initialize a new example database using that directory as its source root and capture
`["paper.txt"]`. Copy the returned paper/source IDs and obtain an author packet. Create these
anchors in a single request, replacing `req_anchors_example`, `pkt_author_example`, and every
`src_example` with actual fresh IDs/packet identity:

```json
{
  "contract_version": 3,
  "request_id": "req_anchors_example",
  "packet_id": "pkt_author_example",
  "anchors": [
    {"id": "anc_scope", "expected_version": null, "source_id": "src_example", "locator": {"start_line": 1, "end_line": 1, "page": null, "label": null}},
    {"id": "anc_A", "expected_version": null, "source_id": "src_example", "locator": {"start_line": 2, "end_line": 2, "page": null, "label": null}},
    {"id": "anc_B", "expected_version": null, "source_id": "src_example", "locator": {"start_line": 3, "end_line": 3, "page": null, "label": null}},
    {"id": "anc_T_statement", "expected_version": null, "source_id": "src_example", "locator": {"start_line": 4, "end_line": 4, "page": null, "label": null}},
    {"id": "anc_T_proof", "expected_version": null, "source_id": "src_example", "locator": {"start_line": 5, "end_line": 5, "page": null, "label": null}}
  ]
}
```

Then get a fresh author packet, copy the graph example, and replace its top-level `request_id`,
`packet_id`, and audit body's `paper_id`. The other example IDs are valid in this new empty graph;
use fresh generated IDs when adapting to an existing paper. Apply the batch once. Its scope and
two premise uses record the intended joint inference; whether that source-linked reasoning is
actually valid remains work for the checker. Run `work list DB --audit aud_example --focus
items:itm_T`, then prepare the next coherent assignment. Assumption and scope source-fidelity work
is initially unexamined, so do not expect the first assignment to close the whole theorem.
