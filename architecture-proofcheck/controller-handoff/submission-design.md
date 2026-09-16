# Submission storage and recovery proposal

Date: September 15, 2026. Planning only. This document proposes changes to the maintained core; it does not claim that they are implemented.

This is the submission portion of the controller implementation plan. The main plan owns worker/envelope JSON shapes. Reuse record contract 3 and the existing source, check, response, mapping and reconciliation records. Add one operational table, not a job engine. No operation here calls a model, schedules a retry, claims a worker or grants proof support from transport state.

## 1. Identity and outcome semantics

One `request_id` identifies one logical submission of a coordinator envelope and exact worker bytes. Compute its digest before generating edit IDs:

```python
request_digest = digest({
    "command": "work submit",
    "envelope": parsed_trusted_envelope,
    "response_sha256": sha256_bytes(original_response_bytes),
})
```

Store both original files as blobs. The envelope digest uses parsed canonical JSON, so irrelevant envelope formatting does not create a different logical request; the first received envelope bytes remain the retained original. Worker bytes are exact, including whitespace. Generated record IDs, current database values, rewritten drafts and expanded edits are not part of this digest. Existing non-controller commands retain their current digest conventions.

The operational state describes the outcome of this submission, not the current proof or assignment:

| State | Meaning | Mathematical commit |
|---|---|---|
| `received` | Input is durably retained; no terminal outcome was committed | None |
| `accepted` | Included valid edits were committed, including any explicit drafts | Required |
| `needs_revision` | Malformed/unusable output, or a valid independent response awaiting identity mapping | Absent for malformed output; present if an independent response was staged |
| `conflict` | Input was retained but relevant recorded inputs changed | None |

An accepted draft is still unfinished examination. A completed `gap`, `refuted` or `inconclusive` judgment is an accepted result, not a transport failure.

For independent work, an unresolved `SourceTarget` is valid pending identity work. Existing review intake may commit the preserved response and resolvable checks with response state `needs_revision`. No independent completion credit is awarded until existing response, scope, freshness and reconciliation rules permit it. In contrast, a malformed included judgment must not silently disappear while other included judgments are credited. Prevalidate the complete worker shape and applicable local judgment constraints before constructing credited checks; retain malformed input with diagnostics.

Mapping is a separate existing `review map` request. It does not rewrite the original submission receipt. `inspect` returns the original operational outcome and, separately, the current response state and mapping references at a stated revision. Therefore a formerly pending submission may have `state: needs_revision` in its immutable receipt while its response is now accepted. Worklist recovery must consult that current response state instead of repeatedly advertising completed mapping work as unfinished. No `mapped` operational state is needed.

## 2. Proposed storage-format-3 DDL

The index stores references and small results. Large envelope/response data stay in existing `blobs`. `audit_id` and operational `role` are inferred from the stored work assignment, not worker-authored fields. Here `role` means assignment mode (`primary|independent|reconcile`), not the two-valued `checks.role`. `audit_id` is validated against a live audit at intake; SQL cannot reference an audit ID alone through the collection-qualified `record_heads` key without another redundant column.

```sql
CREATE TABLE work_submissions (
    request_id TEXT PRIMARY KEY,
    request_digest TEXT NOT NULL CHECK (length(request_digest) = 64),
    packet_id TEXT NOT NULL REFERENCES packets(packet_id),
    audit_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('primary', 'independent', 'reconcile')),
    envelope_sha256 TEXT NOT NULL REFERENCES blobs(sha256),
    response_sha256 TEXT NOT NULL REFERENCES blobs(sha256),
    received_at TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN ('received', 'accepted', 'needs_revision', 'conflict')
    ),
    committed_revision INTEGER REFERENCES commits(revision),
    result_json TEXT CHECK (result_json IS NULL OR json_valid(result_json)),
    CHECK (
        (state = 'received' AND committed_revision IS NULL AND result_json IS NULL)
        OR
        (state = 'accepted' AND committed_revision IS NOT NULL AND result_json IS NOT NULL)
        OR
        (state = 'needs_revision' AND result_json IS NOT NULL)
        OR
        (state = 'conflict' AND committed_revision IS NULL AND result_json IS NOT NULL)
    )
);

CREATE INDEX work_submissions_by_audit
    ON work_submissions(audit_id, received_at, request_id);
CREATE INDEX work_submissions_by_packet
    ON work_submissions(packet_id, received_at, request_id);

CREATE TRIGGER work_submissions_no_delete
BEFORE DELETE ON work_submissions
BEGIN SELECT RAISE(ABORT, 'submission history is immutable'); END;

CREATE TRIGGER work_submissions_finalize_only
BEFORE UPDATE ON work_submissions
WHEN OLD.state <> 'received'
  OR NEW.state = 'received'
  OR NEW.request_id <> OLD.request_id
  OR NEW.request_digest <> OLD.request_digest
  OR NEW.packet_id <> OLD.packet_id
  OR NEW.audit_id <> OLD.audit_id
  OR NEW.role <> OLD.role
  OR NEW.envelope_sha256 <> OLD.envelope_sha256
  OR NEW.response_sha256 <> OLD.response_sha256
  OR NEW.received_at <> OLD.received_at
BEGIN SELECT RAISE(ABORT, 'only received submissions may be finalized'); END;
```

For any non-null `committed_revision`, the transaction engine must verify that the referenced commit has the same request ID and logical digest. The commit's receipt is the mathematical receipt embedded in `result_json`. This is checked during writes and backup verification, not inferred from matching timestamps.

`result_json` holds the compact original command result: request and packet identity, operational state, `stored` flag, mathematical receipt if any, `record_map`, remaining task IDs, diagnostics or changed-input details, and the next permissible action. It does not duplicate worker reasoning. The main plan fixes exact response fields. Complete response bodies are retrieved only on explicit request.

Do not add assignment status, queued/running states, worker identity claims, leases, retry counters, priority or a duplicate list of proof obligations to this table. Trusted reviewer/provenance fields are already in the retained envelope. Current work remains derived from records.

## 3. Intake algorithm

1. Enforce finite limits on envelope and response bytes before loading them. Read the bounded files once; retain exactly the bytes read. Do not perform a size check followed by an unlimited second read.
2. Parse and validate the coordinator envelope, its supported interface version and request ID. Compute the input digest. Parsing the trusted envelope is allowed here; interpreting the worker judgments is not.
3. Begin a short `BEGIN IMMEDIATE` transaction. Look up `work_submissions` by request ID first.
   - Same ID and different digest: return `REQUEST_ID_REUSED`; preserve the original row. The newly supplied bytes were not saved under that ID.
   - Same digest and terminal state: return the original stored result before checking current mathematical inputs, qualification changes or generating IDs. `inspect` supplies separate current-state information when requested.
   - Same digest and `received`: return/enter explicit resume processing; do not insert another input copy.
4. For a new request, also check the global `commits.request_id` namespace. An ID already used by an unrelated existing command is not a new controller submission. Reject it rather than adopting an old commit without its original input/provenance.
5. Verify the original packet exists and is a supported version-2 work assignment. Infer audit and assignment mode from that stored packet; validate reviewer/qualification/exposure metadata for that mode. Ordinary get packets, including version 2 without work metadata, do not authorize `work submit`. If the envelope names `rebase_packet_id`, verify that packet's identity and compatible mode too, without yet claiming the old reasoning is reusable. Do not reject merely because the original packet is old. Freshness and exact current input-version tests occur after persistence.
6. Store the original envelope and worker bytes with `Database.put_blob`, insert the `received` row, and commit. This transaction does not allocate a mathematical revision.
7. Process immediately in the same tool invocation, unless interrupted. A crash at this point leaves a discoverable `received` input. There is no background processor.

Invalid envelope, unknown/unsupported packet, invalid provenance or oversized data can be rejected before intake. The response must state `stored: false` and leave the caller's files untouched. A genuine stale packet must instead produce a retained `conflict`. Revalidate any mutable audit/provenance requirements in the acceptance transaction before granting credit; pre-intake validation is not a concurrency guarantee.

## 4. Processing and transaction seam

Reuse the existing transaction engine instead of nesting `accept()` transactions or duplicating validation. Refactor its body into an internal transaction-owned helper, for example `_accept_in_transaction(...)`; the public `accept(...)` remains a wrapper that begins, commits and rolls back as today. The helper never commits or rolls back its caller's transaction. It retains idempotency, command permissions, read-set/guard checks, prospective validation, revision allocation, record insertion and binding generation.

The controller then performs:

```text
parse the retained bounded worker bytes and prepare non-database-dependent diagnostics
BEGIN IMMEDIATE
    reload submission; terminal result wins if another caller finished it
    check existing commit by request_id before generating records
    revalidate current envelope/audit/qualification compatibility
    expand primary tasks or plan independent review against recorded packet context
    validate all included edits and consumed-input freshness
    receipt = _accept_in_transaction(...,
        request_id = stored request_id,
        request_digest = stored input digest,
        edits = complete included plan)
    construct compact result from this plan and immutable receipt
    finalize work_submissions with result and committed_revision
COMMIT
```

All graph-sensitive planning and checks are inside this writer transaction or are derived exclusively from the immutable packet and revalidated inside it. Do not query mutable draft versions outside the transaction and silently replace them with newer values. The worker's expected version comes from its prepared context, subject only to an explicitly validated rebase.

This transaction atomically saves mathematical records and finalizes the operational result. There is no legal crash window containing a mathematical commit but an unfinalized index row. `commits.receipt_json` and the receipt nested in `work_submissions.result_json` must match. New generated IDs may differ after an interrupted, uncommitted attempt; they must never change the input digest or survive without their accepted transaction.

On a known structural error or conflict, roll back the mathematical transaction. In a separate short transaction, reload the submission and finalize it as `needs_revision` or `conflict` only if it is still `received` and no matching mathematical commit exists. If another explicit caller completed it, return that caller's terminal result instead. A crash before error finalization leaves `received`, which an identical explicit replay may safely process again.

Unexpected exceptions, process termination and temporary database unavailability must not fabricate a conclusive rejection. Keep the row `received` when no terminal result was saved; return an internal/transient failure plus the inspect/replay reference. No automatic retry occurs.

### Primary adapter

Use the worker shape from the main plan: results by assigned task ID, explicit coverage with task/check references, and explicit findings. `CheckResult` includes both `replaces` and `supersedes` pinned references or null. A `replaces` reference selects the exact packet-listed current draft of the same task and reviewer; retain that record ID and use its expected version. A correction of completed evidence instead creates a new check with explicit `supersedes`. Do not guess a draft or predecessor. `record_map` maps task IDs to the actual written check pins, whether created or replaced, so related coverage/findings use those exact results. Expand only mechanical fields. Keep task identity, target, role, permitted record creation/replacement and expected versions constrained by the packet. Validate the complete prospective state once, including references between newly generated checks, coverage and findings.

Current `apply` forbids observations and current `compare` permits only observations. Calling them sequentially would violate atomicity for a mixed source-fidelity/proof response. Introduce one narrow internal `work_primary` validation profile, using existing body/reference validators:

- Create observations, primary checks, explicit coverage and explicit findings.
- Replace only packet-authorized own drafts and explicitly pinned coverage records.
- Retire nothing; do not mutate the graph, sources, audits, independent evidence or reconciliation.
- Retain command-specific checks for immutable observations/completed judgments, draft ownership, exact task scope and coverage/check associations.

This profile is not a new unrestricted public edit command. A completed check correction uses a newly created check with an explicit predecessor. A primary worker cannot create independent checks or author `response_id` provenance.

### Independent adapter

Extract a reusable planning function from `review.submit_review` so both the existing public command and controller use the same envelope compatibility, scope, exposure, judgment classification and body generation. The controller supplies its already verified input digest to the transaction helper. It must not let the legacy independent function recompute a different digest from a narrowed envelope after intake.

Preserve the actual worker bytes and coordinator/worker provenance separation. Prevalidate malformed included judgments as a whole; treat normal unresolved source identities as pending rather than malformed. When staging a response, save the response and any permitted staged checks together and record `needs_revision` with that mathematical receipt. Mapping and reconciliation continue through their existing command validators.

Move the existing `review map` successful-request lookup ahead of current response-state checks, so replaying a mapping that already accepted a response returns its original receipt instead of incorrectly reporting that the response is closed. A later mapping must never update the original intake row's historical result.

### Reconciliation adapter

For a reconciliation assignment, the operational mode/role is `reconcile`; preserve the coordinator's existing `BATCH` as the original payload. Route its edits through the existing `reconcile` command validation profile in the same transaction-owned acceptance helper. New successor checks created there retain `checks.role: primary`; independent corrections still enter through the independent-response path and are referenced by reconciliation. Never copy the operational mode into `checks.role` or let a coordinator fabricate independent evidence. Do not invent another reconciliation judgment schema, automatically resolve disagreement, or split its successor checks and findings across commits. Batch packet/request identity must agree with the trusted envelope; the logical controller digest still covers the original envelope and exact payload bytes. Direct existing `review reconcile` remains supported.

## 5. Partial saves, rebase and inspect

Atomicity covers the explicit included submission, not every task in the prepared assignment. A valid subset and valid drafts may be saved; omitted tasks remain unfinished. An invalid included entry prevents the included mathematical batch from committing. The controller does not silently salvage a valid subset or edit the worker file.

After a partial save, return the remaining IDs and an explicit preparation option. Reprepare their current context instead of requiring the obsolete original assignment packet. Existing drafts remain attached to their exact task. If already-produced unsaved reasoning is carried forward, retain its original packet reference and compare consumed facets, source context and relevant memberships atomically against the fresh packet.

Use the main plan's optional envelope field `rebase_packet_id` for that fresh acceptance context. The original `packet_id` stays unchanged in the envelope, index and worker bytes. A deliberate rebase is a new request with both packet identities in its digest/provenance; it is not a mutation of an earlier input or a successful retry. Only after the atomic consumed-input comparison passes may acceptance use the fresh packet's current write expectations. Return both original and acceptance packet IDs in the result. Do not overwrite worker packet identity to make a stale response appear newly written. The rebase reference is retained in the envelope blob; no second assignment table is needed.

Only cosmetic/progress changes that did not alter consumed mathematical inputs qualify for mechanical rebase. Judgments actually consumed by composition or reconciliation are mathematical inputs. Changes made by the same coordinator are not automatically harmless. This design requires C2's task-level consumed-input pins; it must not relax raw read-set checks globally before those pins exist. Independent mapping still checks original worker scope and source evidence, even when a fresh coordinator packet supplies canonical identities.

`work inspect DB --request ID` is read-only. It returns the immutable original result or `received`, the exact receipt if committed, and bounded current overlays such as response mapping status, changed input summary and remaining work. `--packet ID` instead retrieves a prepared assignment that may have no submission. The history form `work inspect DB --audit ID --limit N --cursor TOKEN` returns bounded preparation/submission metadata, never all historical payload bodies. Request detail, packet detail and audit history are mutually exclusive. This is discoverability, not an active-worker claim. Detail inspection can offer:

- replay this unchanged `received` input explicitly;
- return the existing terminal receipt;
- retrieve original input to a user-selected path;
- prepare current context for a corrected/new request;
- continue existing independent mapping with the preserved response ID.

Terminal rejection is not rerun under the same ID. A deliberate new attempt uses a new ID even if its response bytes are unchanged. All old diagnostics remain discoverable. If inspect finds a receipt/index inconsistency despite the transaction invariant, show it and block new mathematical writes for that request rather than guessing a new outcome or duplicating the edits.

Operational rows and pending-input bytes are coordinator-only. They never enter independent worker packets, public proof support or reader completion totals. Original source-only responses may be returned to their own worker for correction/resume without exposing primary judgments or coordinator diagnoses.

## 6. Storage 2 to 3 migration and compatibility

Keep `contract_version = 3` and `protocol_version = item-audit/1` unless the main implementation changes their meaning. Storage becomes 3. Both ordinary `get` and controller `work prepare` emit packet version 2, with ordinary get retaining an envelope compatible with its established non-controller callers. Database metadata advertises packet version 2 as the emission default; each historical row and payload retains its own explicit version 1. Preserve old packet-1 blobs and manifests byte for byte.

Add an explicit native-storage migration, proposed command `migrate DB --backup BACKUP`, separate from `migrate-overview`. It accepts storage 2 only; format 3 returns an already-current result without mutation. Newer/unknown formats remain incompatible. The ordinary `Database` constructor must not silently migrate.

1. Open a migration connection, validate storage/record versions and supported features, and create an exclusive-destination SQLite backup using the existing backup approach. Compare `PRAGMA data_version` on that same migration connection before and after backup; abort if a writer changed the source during backup.
2. Disable foreign-key enforcement on this dedicated connection before `BEGIN IMMEDIATE`, because the packet table needs SQLite's table-rebuild procedure. Acquire the write transaction and compare the same connection's `data_version` again with the post-backup value; also record the head revision. If changed, roll back and return a conflict rather than claiming the backup covers the migrated input. Packet/intake commits also matter even when mathematical revision is unchanged. Restore foreign-key enforcement on every exit path.
3. Inside the transaction, create `packets_v3` with the existing columns and foreign keys, changing only the version constraint to `CHECK (packet_version IN (1, 2))`. Copy all packet rows, drop the old `packets` table, and rename the replacement to `packets`. Preserve IDs, payload hashes, manifests, timestamps and base revisions; preserve `evidence_bindings.packet_id` references. Do not use `executescript` in a way that implicitly commits the migration midway.
4. Create `work_submissions`, its indexes and triggers. It begins empty; do not invent historical intake entries for old commits.
5. Set storage metadata to 3, the default new packet version to 2, and required features to the agreed supported names. Keep packet-1 support while declaring packet-2 support. Update code/projection metadata only to actually implemented versions.
6. Run `PRAGMA foreign_key_check` and integrity checks before committing, then enable foreign keys again and reopen through normal compatibility checks. On any failure, roll back the complete migration; retain the untouched backup.

Use `STORAGE_FORMATS_READABLE = (2, 3)` and `STORAGE_FORMATS_WRITABLE = (3,)` while format-2 read compatibility is supported. `Database.check_compatibility` currently checks only readability; add the write-format check when `write=True`. Controller commands require format 3. Normal read/export paths must handle the absent operational table on format 2 explicitly, not by swallowing arbitrary database errors.

Fresh `initialize` uses the format-3 DDL. Existing `migrate_overview` and `import_legacy` continue their current conversion semantics but create the latest storage format through `initialize`; they must not reinterpret legacy evidence as fresh controller submissions. Fix `Database.insert_packet`, which currently writes the global `PACKET_VERSION`, to persist the validated manifest's actual version. Both new get and prepare operations emit packet 2; historical packet 1 remains inspectable and usable by supported generic apply/review commands under its original strict raw-version rules, without silently inventing task pins or assuming its version from current metadata. `work submit` requires packet 2 with work metadata. Generic packet 2 retains the established non-controller permission path; it gains no task-level rebase exemption merely from having the newer version number.

## 7. Backup and export scope

SQLite backup is the only supported recovery transport in this revision. It preserves all packet rows, commits, operational submissions and original blobs without a new export/import framework. Reopening a compatible backup preserves request IDs, receipts, drafts and pending input. A recovered `received` input remains pending for explicit replay; opening the database starts no provider call or background retry.

The current `export_snapshot` is a mathematical snapshot: it exports record-linked blobs and bindings, not packet rows or commit history. `--history` adds record versions only. There is no general native snapshot importer; `import_legacy` and `migrate_overview` remain their existing source-format adapters. Do not claim that mathematical JSON export can restore controller state.

Keep that scope for this revision:

- Existing mathematical exports retain their record provenance and declared mathematical revision. New index-only rejected/pending input is excluded by default; existing record-linked independent-response blobs retain their existing export behavior.
- Operational diagnostic attachments are outside this revision. A later extension would need to embed every newly referenced envelope/response blob and explicitly disclaim controller-state restoration; it must not emit dangling references.
- Report the actual database format from metadata when reading format 2 instead of unconditionally labelling it with the newest compiled `STORAGE_FORMAT` constant.
- Verify the complete backup by reopening it, checking blob references and receipt-to-commit identity, and exercising pending replay on a test copy. Source-root availability is a separately reported local limitation; do not rewrite historical packet/source bytes to hide it.

No native JSON restore command or general recovery archive is required. Correct older plan wording that promises operational export/import round trips: this revision guarantees backup recovery and explicitly scoped mathematical exports.

## 8. Maintained-source seams and focused tests

| File | Surgical change |
|---|---|
| `storage.py`, `schema.sql` | Submission row accessors/finalization; storage compatibility; migration; packet-version preservation |
| `acceptance.py` | Extract transaction-owned core; use original input digest; keep existing public wrapper behavior |
| `validation.py` | Narrow internal `work_primary` permissions plus task/ownership checks; reuse existing record validators |
| `review.py` | Shared independent planning; whole-input malformed handling; early mapping replay; original evidence preserved |
| Controller adapter module | Intake, expansion, explicit processing and compact inspect; no model/queue code |
| `export_import.py`, `cli.py` | Explicit native migration; accurate snapshot-export scope/current-format reporting; four controller verbs wired by main plan |

Minimum behavioral tests:

1. Exact duplicate and envelope-format-only replay return the same terminal receipt; changed response bytes under that ID fail. Generated edit IDs do not change request identity.
2. Crash after intake, before mathematical commit and after commit: no input loss, duplicate check or receipt/index divergence. Temporary processing failure leaves received work inspectable.
3. A stale valid packet is retained before returning conflict. Invalid credentials/oversized input report whether nothing was saved.
4. Mixed source-fidelity/check/coverage/finding output commits atomically; one malformed included entry commits none of that batch. Explicit valid subset and drafts save and resume with fresh remainder context.
5. Independent SourceTarget staging, later mapping, mapping replay and original-submission replay preserve distinct historical and current states; no premature independent completion credit.
6. Caption/progress-only rebase preserves eligible work; changed consumed statement, scope, source or judgment cannot be rebound as harmless. New graph/source facts are not silently authored by adapters.
7. Migration preserves all old records, commit receipts and packet-1 payload hashes; interrupted migration rolls back. Format-2 writes demand migration.
8. SQLite backup recovery preserves accepted, rejected, conflicted and received entries with exact raw blobs and usable receipt references. Mathematical export remains explicitly non-restorable as controller state and unchanged in its read-only purpose. Independent packets contain none of this coordinator-only index.

The main plan owns serialized response shapes and exact command naming. This proposal supplies the transaction/storage requirements needed to implement those interfaces without a second acceptance engine.
