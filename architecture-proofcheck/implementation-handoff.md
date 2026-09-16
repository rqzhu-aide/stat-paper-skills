# Proofcheck implementation handoff

Date: September 13, 2026; controller interfaces updated September 15. Contract: `proofcheck-records/3`, packet protocol `2`, reader projection `2`.

Status: baseline implementation specification. The database pilot and subsequent bounded controller are implemented in the shared core. The [controller implementation plan](controller-implementation-plan.md) owns the added work commands, coherent assignment policy, response schemas, migration and recovery behavior. The released legacy lane remains v1.5 while release evaluation is separate. Start with the controller plan for the current revision.

## 1. What to build

Build a proof audit around one durable paper database. Register major mathematical statements and meaningful intermediate claims once; record each application separately; check local inferences in prerequisite order; save useful work incrementally. Render the existing adapted Archify viewer from those records. The diagram always contains major nodes only. Selecting a connection exposes its applications, intermediate reasoning, other required premises, checks, and findings below the graph. Selecting a result exposes the complete proof, including final composition and work that belongs to no incoming connection.

The complete behavioral requirements remain in [architecture.md](architecture.md). The delivery sequence remains in [revision-plan.md](revision-plan.md). This handoff supplies their concrete implementation decisions. The following companion files are normative for the new format:

| File | Responsibility |
|---|---|
| [Record contract](handoff/record-contract.md) | Exact record fields, identities, mathematical grouping, version bindings, and invariants |
| [SQLite DDL](handoff/schema.sql) | Record-level persistence and history, packets, bindings, references, and publication records |
| [Checker protocol](handoff/checker-protocol.md) | Primary checking, bounded independent review, reconciliation, and proportionate authoring |
| [Example batch](handoff/example-batch.json) | Concrete joint inference with two major premises, a hidden result, and a final theorem |

[Handoff validation](handoff/validation.md) records the checks actually performed on these specification files and their limits.

The DDL is executable specification material. It does not implement application validation, the command layer, or proof checking. The example is synthetic mathematics for an interface fixture, not an assessment of the DRL paper. Implementation must satisfy both the record contract and SQL constraints.

## 2. Terms and document authority

| Term | Meaning |
|---|---|
| Ref / PinnedRef | A collection-qualified record ID / that ID plus an exact record version. Full shapes are in record-contract section 1 |
| Revision / record version | One committed database state / one version of an individual record identity |
| Facet | A fixed projection of one record's content, such as its statement excluding its printed label; used to identify what a check consumed |
| Read set | Tool-recorded versions read for an edit; checked before accepting that edit |
| Membership guard | A digest of a queried relation's members and versions; detects a newly added or removed premise even when previously read rows are unchanged |
| OCC | Optimistic concurrency control: validate the packet's expectations inside the write transaction before committing |
| Obligation | Required checking work derived from the proof structure, including work for which no check exists yet |

Each rule has one owning document. [Architecture](architecture.md) owns mathematical meaning, user-visible behavior, and connection colors (section 9.3). [Record contract](handoff/record-contract.md) owns record shapes and reference/binding rules; [schema.sql](handoff/schema.sql) owns the physical SQL definition and must implement those rules. This handoff owns command, transaction, packaging, and projection interfaces. [Checker protocol](handoff/checker-protocol.md) owns role instructions, using the contract's response shape. [Revision plan](revision-plan.md) owns phase order; section 10 below maps its phases to staffing packages. README, examples, and validation receipts are explanatory evidence.

When text conflicts, the owning document takes precedence within its area. Correct the conflicting restatement before implementing that interface; a lower-level storage or rendering choice cannot silently change the architecture's mathematical meaning. Connection-color rules are kept in architecture section 9.3 rather than duplicated here. Historical review rationale is in Appendix A.

## 3. Decisions implementers must share

| Area | Required decision |
|---|---|
| Storage | SQLite with immutable per-record versions and current heads; no new full-dataset JSON payload on each record edit |
| Versions | Database storage format `3` (reads `2`, explicit migration for writes); export/record contract `3`; packet and projection contracts each `2`, with explicit version-1 compatibility |
| IDs | Stable string IDs, independent of numbering; generated prefixed UUIDs for new records; preserve valid imported IDs |
| Mutations | One integrating writer, short atomic transactions, packet-generated read sets, expected write versions, and relation membership guards |
| Rebase | Accept non-overlapping batches on the current head after checking their dependencies; reject relevant conflicts without dropping work |
| Mathematical grouping | Uses are applications; groups are joint inferences or case assembly; arguments are complete proof routes; scope is explicit |
| Checking | Local reasoning, freshness, dependency support, statement support, and process completion remain separate |
| Blinding | Independent worker receives only an allowlisted source packet and permitted source supplements; no primary records or database path |
| Viewer | Actual existing Archify shell and lower reader; canonical records and diagram projection have separate validation obligations |
| Packaging | One maintained shared core, identical generated bundles in both user-wide skill installations; no sibling checkout dependency |
| Legacy | Preserve legacy execution and evidence. New-format code does not import the monolith, even indirectly |

Do not introduce a second graph store, graph service, browser editing system, runtime downloader, or project-local Python/Node installation. User-wide shared runtimes remain the execution environment.

### Version identifiers

Compare the named identifier and its value, never a bare digit. Native storage format 3 follows the pilot's format 2; both are unrelated to the overview's `schema_version: 2`. Existing overview formats are import inputs; they do not identify a new-format database.

| Interface | Identifier/value | Where it lives | When it changes |
|---|---|---|---|
| Current overview SQLite format | `format = archify-paper-database-1` | Existing SQLite `metadata` | Historical format; detect explicitly for migration, do not overwrite this label to pretend migration occurred |
| Current overview records/export | `schema_version = 2` | Existing snapshot payload and JSON export | Historical input schema; convert through the overview adapter |
| New SQLite storage | `storage_format = 3` | SQLite metadata value `'3'`; exports report the actual database format | Physical table, constraint, or persistence changes requiring a storage migration |
| New record/export contract | `contract_version = 3`, descriptive name `proofcheck-records/3` | JSON batches/exports; SQLite metadata value `'3'` | Record fields, enums, references, or interpretation changes requiring contract migration |
| Packet and worker-response interface | `packet_version = 2` | Stored/issued packet and `packets.packet_version`; historical packet 1 retains its original rules | Packet, read-set, allowlist, or worker-response shape/meaning changes |
| Reader projection | `projection_version = 2` | Projection JSON and bundle manifest; renderer also reads projection 1 | Core-to-renderer payload or assessment interpretation changes |
| Checker method | `protocol_version = item-audit/1` | Pilot protocol; audit, check, and qualification bodies | Substantive checking, qualification, or review-method changes affecting reuse; editorial corrections alone do not bump it |
| Packaged code | `core_version` and skill `metadata.version` | Generated bundle manifest and each `SKILL.md` | Released code/assets/instructions change; this does not by itself change every data/proof contract |

The compatibility gate checks each applicable identifier separately. A storage-only migration does not grant mathematical reuse, and a prose clarification that leaves these interfaces unchanged does not require inventing another format number.

## 4. Persistence and conflict protocol

### 4.1 Record storage

Use [schema.sql](handoff/schema.sql) as the starting schema. `record_versions` is append-only; `record_heads` points to the latest version of each logical identity, including a tombstone for a retired record. JSON is stored per record body, not per paper. `record_refs` is a generated index of canonical references. It is not another authored dependency graph. `record_facets` and `evidence_bindings` are generated version/freshness metadata. Blobs deduplicate captured sources and original worker responses.

Every accepted semantic batch gets a monotonically increasing commit revision. Render/export reads one revision, selecting the newest version of each record at or before it. A consistent historical report must use historical assessments, source context, and findings from that same revision. Rendering, timing receipts, and packet generation do not change mathematical record versions. Publication records retain their own build history.

Enable foreign keys on every connection. Keep model calls outside transactions. Use SQLite's backup API for live backups. A migration backs up the existing database, upgrades it atomically, and retains imported source bytes and IDs. A prior overview runtime must reject storage format `2` before mutation. The upgraded overview supports audit-bearing databases and must preserve collections it does not edit.

### 4.2 Packet and edit envelope

`get` creates an immutable packet manifest inside the database. The model sees the relevant record bodies, copied IDs/versions, evidence, and a `packet_id`; it does not author integrity hashes. The stored manifest contains:

```json
{
  "packet_version": 2,
  "packet_id": "pkt_<uuid>",
  "base_revision": 41,
  "mode": "primary",
  "targets": [{"collection": "items", "id": "itm_<uuid>"}],
  "read_set": [{"collection": "items", "id": "itm_<uuid>", "version": 3}],
  "membership_guards": [
    {"relation": "incoming_uses", "key": {"collection": "items", "id": "itm_<uuid>"}, "digest": "<generated>"}
  ],
  "source_context_digest": "<generated>",
  "write_scope": [{"collection": "items", "id": "itm_<uuid>"}]
}
```

This is a manifest illustration, not an editable packet. The actual worker packet omits internal guards unless requested for diagnosis. Supported modes are `author`, `primary`, `independent`, and `reconcile`. `author` permits inventory work without a mathematical judgment. The packet identifies any pagination or omitted context explicitly. A truncated source/proof packet cannot silently count as complete-result review.

The mutation envelope is:

```json
{
  "contract_version": 3,
  "request_id": "req_<uuid>",
  "packet_id": "pkt_<uuid>",
  "edits": [
    {"op": "create", "collection": "items", "id": "itm_<uuid>", "expected_version": null, "body": {}},
    {"op": "replace", "collection": "uses", "id": "use_<uuid>", "expected_version": 2, "body": {}},
    {"op": "retire", "collection": "coverage", "id": "cov_<uuid>", "expected_version": 1, "reason": "Replaced by corrected coverage spans."}
  ]
}
```

`body` above is a placeholder for the exact collection schema. `replace` supplies the complete intended body, not a field merge. `retire` has no body and requires a nonempty `reason`, retained in the commit receipt. IDs must be unique within a batch. New records may reference other new records in that batch. Existing writes must be in the packet's write scope; new records must be within its declared target proof/audit scope. Source, anchor, qualification, and independent-response records have dedicated creation commands and cannot be forged through generic `apply`.

The tool adds all write expectations and reverse-reference validation to the stored read set. Workers cannot trim the read set by omitting copied records. A genuinely needed extra passage is obtained with `get --extend PACKET`, which creates a new packet with the union of evidence; old packets remain reproducible.

Generic `apply` may create or update primary checks only. Independent checks can be created only by `review submit` or `review map`, generated from the preserved response's identified judgments. Supplying `role: independent` or a `response_id` through ordinary `apply` is rejected. `compare`, source review, qualification, and reconciliation similarly use their dedicated command validators. They share the transaction engine without bypassing provenance rules.

### 4.3 Exact acceptance algorithm

Within `BEGIN IMMEDIATE`:

1. If `request_id` already committed with the same canonical batch digest, return its original receipt. If the digest differs, reject `REQUEST_ID_REUSED`.
2. Check contract, packet existence, write scope, record read versions, expected write versions/absence, membership guards, and source context against the current database.
3. If relevant inputs differ, reject the whole batch as `CONFLICT`. Return changed references, expected/actual versions, changed membership relations, and a command to obtain a replacement packet. Keep the proposed batch available for the caller. Do not commit a partial result.
4. Validate record shapes and the prospective linked state, including references into and out of changed records. While still holding the same writer lock, read `parent_revision = SELECT MAX(revision) FROM commits` (null for an empty store) and set `revision = COALESCE(parent_revision, 0) + 1`. Reject integer exhaustion. The first commit is revision 1. Never reserve a revision before `BEGIN IMMEDIATE` or rely on implicit row-ID allocation.
5. Compute the complete immutable receipt from that validated prospective state, including `{request_id, revision, rebased_from, changed, warnings}`. `rebased_from` is the packet's older base revision when a harmless intervening commit was accepted; otherwise null. Insert the `commits` row first with the explicit revision, parent, packet base revision (null for initialization), request digest, and final receipt. Its row must exist before inserting `record_versions`, whose revision foreign key is immediate.
6. Insert any new blobs, then the changed `record_versions`; advance their `record_heads`; insert the generated `record_refs`, `record_facets`, and `evidence_bindings`. Validate the resulting state and commit. The declared deferred reference constraints are checked at commit, permitting same-batch cross-references. Any failure rolls back the commit row and all batch writes; an uncommitted revision may be reused, but a committed revision never is.
7. Return success and the saved receipt only after `COMMIT` succeeds. Never update the receipt after inserting its commit row. An idempotent retry returns that same receipt without reserving another revision.

A newer global revision alone is not a conflict. An unrelated theorem's draft can commit while another worker checks a lemma. An update to the same claim, a new incoming use, or a newly added required theorem part must be detected even if no previously read row changed. Required membership guards include `incoming_uses`, `uses_in_group`, `groups_in_argument`, `arguments_for_target`, `parts_of_item`, `coverage_in_argument`, `scopes_in_argument`, and `checks_or_findings_for_target` when that set informed reconciliation or completion. Guards hash sorted logical IDs and relevant versions and are registered by query type, not chosen by the agent. The exact reference-path and relation-query conventions are in record-contract section 1.1.

An outgoing consumer is not a supplier-check guard. It is included only in a packet actually assessing downstream impact. Concurrently adding that consumer must leave the supplier's proof judgment intact. A report build or usage receipt never conflicts with a mathematical edit.

OCC and mathematical freshness solve different problems. A cosmetic label edit may conflict with a packet's record replacement while leaving its mathematical evidence current. A saved check binds semantic facets and reviewed source context as specified in the record contract; do not reuse raw OCC versions as the mathematical staleness rule.

### 4.4 Required race fixtures

Test two packets from one revision: unrelated draft updates both commit; same-record updates conflict; adding an incoming premise conflicts with final-composition submission; adding an outgoing consumer does not stale the supplier; adding a theorem part conflicts with whole-result completion; response submission racing reconciliation cannot silently omit the response. Repeating a successful request returns one commit, not duplicate findings.

## 5. Public command and Python interfaces

New entry point: `python <skill>/scripts/paper_audit.py`. It is a thin wrapper over the shared core. All commands return one JSON object to stdout; diagnostics go to stderr. Exit codes: `0` accepted/read succeeded, `2` invalid request or data, `3` conflict, `4` incompatible schema/package, `5` source unavailable, `6` render/publication failure. An incomplete mathematical assessment is a successful status query with `process_complete: false`, not a command failure.

Paths below are arguments. Commands shown here are the target interface and do not exist merely because this handoff was written.

| Command suffix | Contract |
|---|---|
| `init DB --source-root ROOT --title TEXT` | Create new database, paper record, and root source context; refuse overwrite |
| `attach DB --report HTML` | Register proofcheck report for compatible existing overview DB; no second master |
| `migrate-overview DB --backup BACKUP` | Explicitly upgrade current overview storage/export schema; preserve IDs, observations and history provenance |
| `source capture DB --files LIST.json` | Capture registered files; return source revisions, declaration/citation candidates, and limitations |
| `source anchor DB --request LOCATORS.json` | Create/rebind verified locators; extract bytes/excerpts in code |
| `source review DB --request REVIEW.json` | Record branch/locator/context decisions and their exact source bindings |
| `ids --kind NAME --count N` | Return UUID-based IDs; kind is a record collection name or `request`; packet IDs are generated by `get` |
| `get DB --target COLLECTION:ID --mode MODE --out PACKET.json` | Issue bounded packet and persist its manifest; repeat target flag for a bounded target set |
| `get DB --extend PACKET_ID --request CONTEXT.json --out PACKET.json` | Extend through the same mode's allowlist; preserve source snapshot or report a conflict |
| `apply DB --batch BATCH.json` | Atomic record edits, including drafts/checks/findings; use exact envelope above |
| `compare DB --packet ID --batch COMPARISONS.json` | Source-fidelity observations only; never mathematical proof support |
| `review submit DB --submission SUBMISSION.json --response RESPONSE.json` | Coordinator supplies the metadata envelope; RESPONSE.json contains the worker's unchanged bytes. Validate metadata, preserve those bytes, and register judgments using record-contract section 5.1 |
| `review map DB --response ID --mapping MAPPING.json` | Map source-grounded response judgments to canonical targets; generate their checks from preserved response content, never from replacement reasoning |
| `review reconcile DB --packet ID --batch BATCH.json` | Save explicit comparison/resolution, preserving both original judgments |
| `qualification record DB --receipt RECEIPT.json` | Import checker configuration and balanced calibration evidence; no expected answers in worker packets |
| `changes DB --since REV` | Changed records, source context, and affected checks with reasons; paginated |
| `status DB [--audit ID] [--snapshot REV]` | Separate structural health, source limits, review coverage, mathematical assessments, and published revision |
| `validate DB [--snapshot REV]` | Shapes, references, bindings, coverage intervals, and projection inputs; no mathematical certification |
| `checkpoint DB --out HTML` | Build and validate a current working report; retain prior HTML if build fails |
| `release DB --audit ID --out DIRECTORY` | Require process completion, create immutable report/export/receipt package; may report established defects |
| `export DB --out JSON [--snapshot REV]` | Portable complete contract-3 snapshot, including history option documented separately |
| `backup DB --out BACKUP` | Consistent SQLite backup |
| `import-legacy AUDIT_FOLDER --db NEW_DB --map MAPPING.json` | New database only, preserved original artifacts and ID mapping, qualified historical checks |

Python functions have keyword-only options and return the same JSON-serializable receipt shapes: `get_packet(db, *, targets, mode, extend=None)`, `apply_batch(db, batch)`, `submit_review(db, *, submission, response_bytes)`, `derive_assessment(db, *, revision, audit_id=None)`, `build_projection(db, *, revision, audit_id=None)`, and `publish_report(db, *, projection, output, release=False)`. For `submit_review`, `submission` is the coordinator envelope from record-contract section 5.1, and `response_bytes` is the unmodified worker file read as bytes. Raise structured exceptions carrying `code`, `message`, `records`, and optional `retry`; the CLI maps them to the exit codes above. Commands must not instruct workers to edit SQLite directly.

File-argument conventions are shared rather than reinvented per command. `LIST.json` is an array of paths relative to the registered root (absolute paths require explicit registration). Comparison, source-review, qualification, and reconciliation batches use the same edit envelope with only their command-authorized collections; their record bodies are fixed by the record contract. Anchor requests use `{contract_version, request_id, packet_id, anchors: [{id, expected_version, source_id, locator}]}`; the command adds source versions/excerpts/hashes. Context extensions use `{targets: [Ref], source_anchor_ids: [ID], source_paths: [string], reason: string}`, interpreted through the original packet mode's allowlist. Legacy mapping files use the identity-map body plus the import artifact path/hash generated by the tool. Review submission/mapping have their dedicated shapes in the record contract.

## 6. Freshness, completion, and independent review

Implement the binding table and assessment rules in the record contract before a large import. Cosmetic fields, outgoing consumers, builds, and unrelated drafts are not mathematical inputs. Changed source context outside a quoted passage still requires a source-context review. A changed supplier proof with an unchanged exported statement can preserve the consumer's conditional reasoning while changing its dependency support. A borrowed proof passage has its own binding and does become pending when changed.

Primary checkers use [checker-protocol.md](handoff/checker-protocol.md). The coordinator first fixes the major inventory and draft proof structure, then refines intermediate claims in bounded units. It can discover a missing node while checking; register the discovery and revisit affected dependents rather than pretending extraction established mathematical completeness. Resolve cycles in the actual selected argument or record them as unresolved work; do not use a topological sort across all alternative routes as a truth test.

For independent review, dispatch a fresh worker context containing the generated independent packet, checker instructions, and the authorized output destination. Do not give it a database path, working-report path, primary scratchpad, unblinded export, or parent conversation containing the diagnosis. Its source evidence comes from captured manuscript passages and neutral source inventory. Primary-authored intermediate statements, dependencies, reconstructions, and repairs are excluded. The independent checker constructs its own interpretation. If it needs more context, the coordinator requests a source-only extension using the same allowlist.

This is an information-flow rule for the dispatch interface. Omission of the database path is not an operating-system sandbox. The coordinator supplies reviewer identity, qualification, and its dispatch/exposure assessment in the submission envelope; the worker supplies mathematical judgments and its own exposure report in unchanged response bytes. The tool records the conservative combined exposure result. A worker's claim of no exposure cannot override an unverified or compromised dispatch. Compromised independence does not satisfy the independent-review requirement. Checker qualification evidence is configuration-bound and records balanced valid/invalid calibration outcomes. Expected calibration answers remain outside the checker context.

Save the original response before exposing primary work. Reconciliation names both judgments, the disputed assertion or application, and the evidence for `agree`, `primary_revised`, `independent_revised`, or `unresolved`. The first response is never edited to match the primary checker. An adjudicated inconclusive result can complete the review task while leaving the theorem unestablished. Missing work, invalid scope, stale inputs, or missing independent coverage cannot.

## 7. Reader projection and user interface

### 7.1 Separate the canonical dataset from drawing data

Add `build_projection`; do not pass all audit items through the old seven-kind graph renderer and do not delete intermediate records to satisfy it. The projection top-level keys are:

```text
projection_version: 2
snapshot_revision: integer
audit_id: ID|null
nodes: [{id, item_ref, kind, label, caption, assessment, detail_key}]
connections: [{id, from, to, primary_use_ids, groups, support_refs,
               obligation_ids, context_refs, assessment, detail_key}]
records: [{ref, body}]
obligations: [{id, target, kind, role, check_refs, assessment}]
details: {detail_key: {record_refs, sections}}
record_locations: [{ref, detail_key, section_key}]
summary: {scope, progress, findings, source_limits, limitations, published_revision}
layout: {mode: "dag"|"index", reasons: [text]}
```

`nodes.id` is the major item ID. `connections.id` is generated as `conn_` plus the full SHA-256 of the UTF-8 compact JSON pair `[source_major_id,target_major_id]`; retain one connection per ordered endpoint pair. `groups` partitions that connection's use IDs by argument and inference group, with exactly `argument_id`, `group_id`, `use_ids`, `obligation_ids`, and `assessment`. Ungrouped overview uses have null argument/group IDs. No independent correctness value is authored in projection JSON.

`records` carries pinned references and complete contract-3 bodies for all material needed by the reader, including selected anchor excerpts and checks, but excluding source-file blobs, private qualification answers, and database paths. Display math is generated from those texts by the shared rendering path; the UI does not need SQLite beside the HTML. `item_ref` and `records.ref` are PinnedRefs. Other Ref lists identify records within this fixed snapshot payload. Detail section keys are stable generated record anchors.

Each assessment has exactly `{state, label, explanation, check_refs, finding_refs, missing_obligation_ids, independent_review}`. State is `green|red|gray|amber`; label/explanation are generated display text; check references are pinned; finding references identify this snapshot's findings. `independent_review` is `not_required|pending|complete|disputed|compromised`. The indicator is separate from local mathematical color. Missing obligations are explicit even when no check record exists.

Each obligation has a generated ID hashing the compact JSON tuple `[audit_id,target.collection,target.id,kind,role]`. `kind` is a CheckKind from the record contract, or `source_fidelity` or `reconciliation`; `role` is `primary|independent|coordinator`. Its `check_refs` includes the corresponding checks, observations, or reconciliations, with collection-qualified pinned references. Derive required obligations from canonical scope, uses, groups, cases, parts, and final composition before joining existing judgments. A missing intermediate derivation must not disappear from green-status reduction simply because no check record exists.

Each detail section has exactly `{key, title, kind, record_refs, obligation_ids, note}`. Section kind is `statement|applications|derivations|premises|coverage|findings|sources|review|composition|limitations`; note is generated text or null. The record contract supplies mathematical payloads rather than a second independently authored narrative. `record_locations` supplies at least one valid section for each in-scope canonical proof record and finding; one shared claim may have several destinations referencing the same stored body.

`summary.scope` is `{mode, target_refs, exclusions}`. `summary.progress` is `{process_complete, required_obligations, completed_current_obligations, draft_checks, major_results, source_unbound_items}`; counts refer to that declared scope and are not pooled into an invented proof-correctness percentage. `summary.findings` is `{open, resolved, superseded, refs}`. `summary.source_limits` is a list of source-issue Refs; `summary.limitations` is a list of assessment diagnostics, including uncovered or unchecked proof spans that prevent process completion even when the recorded check obligations are satisfied. `published_revision` is an integer or null. Overview mode has `audit_id: null`, scope mode `overview`, and no implied proof-review obligations.

### 7.2 Deterministic projection algorithm

Define `major_owner(item)` as itself for a major item and its required `owner_id` for an intermediate item. A part inherits its parent item's major owner. For each actual use, project its source and target to those owners. Different owners contribute the use to exactly that connection. Same-owner uses stay in details only. Do not infer transitive arrows: recorded A-to-L and L-to-T uses create those connections, not an invented A-to-T use.

For each boundary use, collect its application check and relevant intermediate derivations along the recorded argument toward the owning result. Follow explicit group membership and uses. Stop at a different major statement or the owning result's final composition. Preserve all required joint inputs and case distinctions in the trace; traverse shared claims by ID with a visited set, not by copying claims. A use of a hidden claim owned by L is labeled as an argument inside L, rather than suggesting L's theorem statement supplied that claim.

Always include the crossing application's own obligation, including a direct major-to-major application at a final group. Downstream support traversal includes groups concluding hidden claims, then stops before the owning major target's final group. Same-owner inputs of that final group, its derivation, and its composition are result obligations shown as context. This boundary makes a valid represented application distinguishable from a failed final combination.

`obligation_ids` lists all required represented applications and intermediate derivations, including missing checks. `support_refs` lists their existing check evidence. Both are derived from the same obligation set. `context_refs` lists additional source/premise/result material shown for explanation. The target's final composition is context and belongs to the result assessment, never to every incoming connection's status. Dependencies of a represented intermediate derivation still affect that derivation's support, even when their own detail is shown as another premise. Group boundaries and support selection must be inspectable in the exported projection.

### 7.3 Status reduction

Use the canonical color and precedence rules in [architecture section 9.3](architecture.md#93-connection-assessment-and-colors). Implement one shared reducer over the explicit obligation set, current checks, dependency support, findings, and reconciliations. Use it for per-use/group assessments and the connection summary; retain the constituent reasons and independent-review indicator in the projection. Missing checks remain obligations and the target's final composition remains outside incoming-connection aggregation, as specified in section 7.2. The renderer displays this result without a second color policy.

### 7.4 Existing implementation seams and acceptance

Reuse `render.mjs`'s `fullItemHtml`, `fullUseHtml`, selection runtime, math rendering, and lower inspector layout. Extend `assets/archify/template.html` through a deliberate shared-core change. Existing `proof_overview.py` artifact acceptance equates canonical item/use identities with SVG nodes/edges; replace that equation with two checks: exact preservation of projected node/connection identities in SVG or index, and complete record-to-reader mapping for the in-scope canonical proof records. A hidden claim search result opens its section in the owning result's reader, without adding a diagram node.

The current cycle fallback is a simpler alternate page. Implement the required complete major-item/connection index inside the same Archify shell. A cycle introduced by ownership projection is a display limitation, not automatically circular mathematics. Never drop a real use or expose intermediate diagram nodes to fix layout.

Browser acceptance covers: long mathematics in the lower reader; separate applications on one connection; shared hidden claims; a theorem with no incoming edge; green incoming connections with red final composition; mixed parts; source-changing historical red; keyboard selection and focus; narrow view; full-dataset search; light/dark mode; and same-shell cycle fallback. Mechanical acceptance must compare embedded IDs, status counts, and findings with the fixed source snapshot. Rendering and regeneration require no model call.

## 8. Packaging and module boundary

Create one maintained source at `shared/paper_core/` in this repository. Extract suitable overview code into it, retaining provenance and licenses. The release builder generates identical `scripts/paper_core/` bundles inside both skill packages, including the renderer and its viewer assets. Those generated bundles are never edited by hand. The existing and new script entry points are thin adjacent-package wrappers.

The bundle manifest records core version, storage formats readable/writable, contract versions, required feature names, projection version, source content identity, and hashes of every bundled file. Both packages must contain byte-identical core bundles for a coordinated release. This is distribution of skill code through user-wide installations, not a private language runtime or per-paper tool installation.

Every DB open checks storage and feature compatibility before writing. An older installed overview with no audit support must reject an audit-bearing DB, rather than discard fields on export/import. There is no runtime sibling-skill lookup, relative repository import, or network update. Release tests copy each package into separate temporary install roots, remove repository access from the test import path, and exercise each independently using the shared Python and Node installations.

The overview development folder is a separate repository. Record both repository revisions and dirty-file content identities in the release input manifest. Put extraction changes and thin wrappers into their respective repositories deliberately. A parent repository commit alone does not capture uncommitted nested-repository changes.

## 9. Legacy code and tests

| Component | Implementation treatment |
|---|---|
| Overview record/source/revision code | Extract suitable validators and source behavior; replace full-snapshot edit/load persistence; preserve overview import and source observations |
| `proofcheck_math.py`, `proofcheck_labels.py` | Reuse compatible independent helpers or their fixtures; choose one new-format math pipeline |
| `proofcheck_sources.py`, `proofcheck_source_check.py` | Extract behavior behind a source interface; current namespace/import coupling prevents direct new-core reuse |
| `proofcheck_authoring.py` | Write new database submission; retain atomicity, drafts, and evidence guarantees, not whole-ledger assembly |
| `proofcheck_reconcile.py` | Write new response/reconciliation persistence; retain original-response and disagreement behavior |
| `proofcheck_report.py`, `proofcheck_release.py` | Port publication and assessment guarantees to new snapshot/projection inputs |
| `proofcheck.py`, `proofcheck_graph.py` | Legacy execution only; no import from the new core |
| `proofcheck_usage.py` | Extract timing/event helpers; replace both the legacy finalization import (`load_proofcheck_module` uses `importlib`) and the subprocess target. New-format telemetry must not import the monolith |

Maintain three test lanes. Do not delete the old test suite to make the new implementation pass.

| Lane | Examples and policy |
|---|---|
| Legacy compatibility | Existing suite remains for old-format execution. Run affected tests when touching old code and the combined relevant suite at release |
| Behavioral ports | New database fixtures for blinding/original responses (`test_challenge_evidence.py`), restricted repairs (`test_statement_support.py`), changed prerequisites (`test_semantic_reuse.py`), and failed publication (`test_transaction_publication.py`) |
| Legacy-only representation | Do not port mandatory one-move rows, eight risk rows, mirrored dependency registries, fresh skeletons, or sibling renewal filenames from `test_proofcheck.py` and `test_primary_renewal.py` |

Create `tests/new_format/` for meaningful behavior tests. Each port records the old test or behavior it replaces; the mapping lives in one `tests/new_format/legacy-map.json` with `{old_test, treatment, new_test, reason}` entries, where treatment is `legacy_only`, `ported`, or `shared`. Exhaustively classify tests affected by a changed shared component, not all 1,059 tests before any useful work can start. Legacy retirement requires a separate declared end of old-format support.

## 10. Work packages, owners, and estimates

Roles below are assignment slots, not named people or claims that work has started. Estimates are planning ranges in focused engineer-days, assume familiarity with Python/SQLite and the existing viewer, and exclude unpredictable fresh mathematical reasoning. Re-estimate after the first vertical slice. Parallel work reduces calendar time; it does not remove integration work.

| Package | Responsible role | Depends on | Estimate | Reviewable exit |
|---|---|---|---|---|
| P0: baseline and contract fixtures | Integration lead + audit-method reviewer | None | 1-2 days, including a bounded two-hour pilot | Source identities, measured/unknown timing table, contract fixtures, no unresolved interface decision |
| P1: shared core and storage | Core engineer | P0 | 4-7 days | DDL migration, IDs, references, packet/OCC races, idempotency, overview preservation |
| P2: source fixes | Source engineer | P0; integrate with P1 | 2-4 days | DRL-shaped custom conditional and no-proof citation workflows work without manuscript surgery |
| P3: checks and protocol | Audit engineer + method reviewer | P1 and usable P2 | 4-7 days | One complete saved/resumed proof route, selective freshness, coverage, pilot instructions |
| P4: review and assessment | Audit engineer + independent reviewer | P3 | 3-5 days | Blinded review, preserved response, reconciliation, accurate completion |
| P5: Archify reader | UI engineer | P0 fixtures; integrate P3/P4 | 3-6 days | Major-only projection, complete details, derived states, browser evidence |
| P6: import, package, publication | Integration engineer | P1, P4, P5 | 3-5 days | Old evidence preserved, standalone pilot packages and installation checks, atomic working/release reports |
| P7: forward acceptance and distribution | Independent evaluator + integration lead | P6 | 2-4 engineering days plus measured audit time | Fresh/scoped evaluation, finalized instructions/examples, release-tree checks, user-wide installation verification, and release identities |

These ranges total 22-40 engineer-days and are provisional, not a delivery commitment. One programmer can fill several roles sequentially. The independent mathematical reviewer must still receive a genuinely fresh checking context. The integration lead owns interface changes, compatibility, the delivery checklist, and the decision to advance beyond a failed gate.

### Revision phases and work packages

These are two views of the same work, not additional phases or additive estimates. The revision plan supplies the gates; packages assign responsibility. P6 prepares the pilot package. Final distribution in P7 follows evaluation and uses P6's builder/install checks.

| Revision-plan phase | Responsible package | Completion boundary |
|---|---|---|
| R0: baseline and contract | P0 | Baseline and agreed contract fixtures |
| R1: source acquisition | P2 | Shared source/citation workflow |
| R2: database records | P1 | Record store, migration, and conflict behavior |
| R3: checking and reuse | P3 | Local checking, coverage, reuse, and pilot primary instructions |
| R4: review and completion | P4 | Independent review, reconciliation, and pilot coordinator/reviewer instructions |
| R5: reader | P5 | Accepted projection and browser behavior |
| R6: publication and import | P6 | Preserved legacy evidence and installable pilot package |
| R7: forward evaluation | P7, evaluation portion | Fresh and realistic evaluations with measured limits |
| R8: final instructions and distribution | P7, release portion, using P6 tooling | Finalize skill instructions/examples, run release-tree checks, verify installed behavior, and record distributed identities |

### Early measurement protocol

Before substantial implementation, freeze one manageable DRL unit and its exact prerequisites, versions, audit scope, checker configuration, and source restrictions in a disposable working copy. Budget the initial pilot at two hours; when time expires, save partial work and report unfinished scope. Do not call it a complete audit merely because the budget expired.

Measure two different tasks separately: converting existing saved reasoning into accepted records/report, and fresh mathematical reading/checking from source. The first measures authoring friction without pretending to measure reasoning. Record command wall time, model reading/reasoning, record authoring, schema/conflict retries, renewal/repeated work, waiting, report building, tokens when available, time to first useful report, and unfinished obligations. When the interface cannot separate phases, label combined time and unknowns; do not infer tokens from ledger bytes or double-count parallel elapsed time.

Then exercise adding one consumer and changing one meaningful prerequisite in the copy. Count surviving checks and repeated authoring. Repeat these same scenarios with the first P3/P4 vertical slice. Add generated large-record fixtures for `get`, `apply`, `status`, and render input construction to detect accidental whole-store scans; compare operation count and bytes read/written as well as wall time. Keep R7/P7 for broader independent evaluation. Database speed is not a substitute for reduced prompt and renewal workload.

### Concrete risks and responses

| Risk | User consequence | Trigger and response |
|---|---|---|
| Too many tiny records/prompts | Another long audit dominated by paperwork | Pilot shows headings or routine algebra taking substantive records; revise granularity before full-paper work |
| Incorrect selective reuse | Old reasoning appears current after a meaningful change | Binding/source-context fixture fails; block reuse, retain evidence pending focused review |
| Overbroad conflicts | Workers repeatedly redo unrelated work | Unrelated-packet race fails; repair read/write/membership scopes before adding concurrency |
| Hidden incomplete inference | Green graph obscures a missing case or final combination | Joint-input/final-composition fixture fails; block green aggregation/release |
| Blinding leak | Apparent independent agreement repeats the first checker | Packet/dispatch contains primary interpretation; record compromised review and repeat in a fresh context |
| Divergent packaged cores | One skill corrupts or cannot resume another's records | Bundle or feature manifest differs; fail writes and correct packaging |
| Legacy coupling spreads | New format inherits the old ledger barriers | New-core import reaches `proofcheck.py`; extract the behavior instead |

## 11. Delivery and acceptance

The first usable milestone is a small vertical slice, not a full DRL rerun: source capture, a joint inference, hidden claim, application check, saved draft, resumed work, independent response, reconciliation, and one honest report. It must also demonstrate one harmless concurrent edit and one real conflict.

All acceptance scenarios in revision-plan section 5 remain required. Add the concrete OCC races, packet allowlist, separate canonical/projection preservation, and installed-package tests above. Report software checks, browser inspection, and mathematical evaluation separately. Process completion may include recorded defects or adjudicated inconclusive findings; it cannot hide undone work or stale independent review.

The release delivery contains source/core/schema/renderer identities; contract fixtures and test receipts; package manifests; one complete small example; one scoped realistic evaluation; timing results with unknowns; legacy migration mappings; and a short list of remaining limitations. Preserve historical sealed artifacts byte-for-byte.

The programmer's commit recommendation is sensible for distribution. The documentation and previous archive move currently exist in the working tree; this handoff does not claim a clean commit. Before sharing a source revision, review and commit only the intended architecture/archive and implementation changes, account for the separate overview repository, and record the resulting identities. The twenty old tracked architecture paths appear deleted because they were moved into the dated archive; their preserved content is recorded in [archive-index.json](archived/archive-index.json). Do not stage unrelated writing-skill edits while packaging this work.

## Appendix A. Design review context

The central criticism is correct: the architecture was a complete description of intended behavior, but left schema design, concurrency, packaging, and checker instructions to the implementer. These are decisions to settle before parallel implementation. The review also correctly identifies coupling in the old runtime. Inspection found 37,803 physical lines in `proofcheck.py` and 1,059 `test_*` definitions across 41 test files. These are source counts, not a fresh test run.

Three qualifications matter:

1. The overview database does store a complete semantic JSON payload per snapshot, and bounded retrieval loads that snapshot before selecting records. This merits replacement for incremental audit work. It does not itself require the model to rewrite all mathematical reasoning. Storage cost and model authoring cost must be measured separately.
2. Current overview record edits advance a global snapshot and invalidate outstanding edit expectations. Comparison and build observations are already separate and do not all advance that snapshot. The problem is broader-than-necessary record-edit conflicts, not literally every database write.
3. One authoritative database removes independently edited report masters. It cannot guarantee that every renderer, cache, or status aggregation is correct. Snapshot identity checks, projection tests, and publication recovery still matter. No speedup or accuracy gain has yet been measured for the proposed workflow.

The suggested early measurement, packaging contract, test disposition, and ownership plan are adopted above. A new two-hour mathematical audit was not run to prepare this handoff. The earlier 22-hour history cannot retrospectively supply a reliable timing decomposition. The proposed measurement is an early implementation gate, not invented evidence.
