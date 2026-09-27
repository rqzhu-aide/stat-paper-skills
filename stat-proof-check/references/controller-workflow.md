# Bounded controller workflow (v2.2)

The coordinator owns graph construction, dispatch and scientific decisions. The controller records
explicit work; it never calls models or decides that the graph includes every mathematical premise.
Use [database-audit.md](database-audit.md) for setup and [coordinator-protocol.md](coordinator-protocol.md)
for scope. Ordinary operation is prepare, examine, submit, then prepare remaining work from the receipt.
Inspect when recovery or clarification is needed; render at meaningful checkpoints.

## Prepare and dispatch

```text
paper_audit.py work prepare AUDIT.db --audit aud_ID --mode primary --focus items:itm_ID --out assignment
```

An assignment groups coherent context for one argument/result and role, normally five units
(`--max-units 1..10`). Applications, joint derivation, coverage and composition can share a worker
call while retaining distinct records. `--task` keeps necessary joint context; `--exclude-task`
excludes work assigned elsewhere. There is no background queue. `--allow-provisional` permits
explicit conditional local work, never missing-source or independence bypasses.

Preparation writes the files below plus coordinator manifest and guidance. For primary work, read
assigned kinds/targets from the packet. Preserve scaffold IDs programmatically and use generated
worker guidance for shapes. Deliver the listed files for each role:

| Role | Deliver |
|---|---|
| Primary | worker-packet.json, response-scaffold.json, worker-guidance.json, [primary-checker.md](primary-checker.md), [mathematical-checking.md](mathematical-checking.md), [evidence-and-verdicts.md](evidence-and-verdicts.md) |
| Independent | Same three worker files, [independent-checker.md](independent-checker.md), the same two scientific references; fresh source-only context |
| Reconcile | worker-packet.json, response-scaffold.json, worker-guidance.json, coordinator-guidance.json, [reconciler.md](reconciler.md), [evidence-and-verdicts.md](evidence-and-verdicts.md); examine compared judgments |

Add domain/external guidance only when needed. A supplied-route independent assignment additionally
loads [supplied-route-review.md](supplied-route-review.md). Keep mapping, qualification, envelopes,
telemetry, and coordinator manifests out of independent delivery. Do not reload the whole entrypoint
or schema manual when these materials were supplied. Generated shapes have no scientific verdicts.

`prepared:false` with exit 0 is a diagnostic, not a command failure. Finish the named prerequisite,
choose another focus, or refine a meaningful boundary. Packets default to 131,072 bytes, allow
`--max-bytes` up to 1,048,576, and cap records at 2,048. Never truncate a joint argument to fit.

## Save work

The coordinator authors [the separate envelope](controller-example-envelope.json), using fresh
request ID, actual reviewer, original packet, and `rebase_packet_id: null` normally. Independent
work also names the actual qualification/exposure; other modes use null for those fields.
For reconciliation, preserve the response scaffold's `request_id` and use that same ID in the
envelope. A different envelope ID does not identify that response.

```text
paper_audit.py work submit AUDIT.db --submission SUBMISSION.json --response RESPONSE.json
```

Preserve worker bytes unchanged. One request ID identifies those bytes and its envelope; an identical
retry returns the original receipt. Changed input or explicit rebase needs a new ID. Intake precedes
parsing/freshness checks. Included mathematical edits commit atomically; omitted rows remain unfinished.
Read `stored`, `state`, `committed_revision`, diagnostics and next actions separately. Accepted gaps
or inconclusive examinations are not transport errors. Envelope/response limits are 65,536/2,097,152 bytes.

## Recover only affected work

| Situation | Action |
|---|---|
| More reasoning on a saved draft | Select its exact same-reviewer `replaces` pin from coordinator guidance; preserve `supersedes`. |
| Unsaved old reasoning, consumed mathematics unchanged | Keep original packet identity; explicitly rebase authorization in a new envelope. |
| Saved completed judgment, consumed mathematics changed | For primary renewal, pass the needed permissible completed predecessor pin from coordinator guidance in the assignment brief. The worker reexamines, authors `supersedes`, and saves the response for unchanged submission. |
| Missing neutral source in source-only independent work | Capture/anchor it, then `work extend`; examine it and author a new response naming C. |

```text
paper_audit.py work inspect AUDIT.db --request req_ID --out recovered-input
paper_audit.py work inspect AUDIT.db --packet pkt_ID --out recovered-assignment
paper_audit.py work extend AUDIT.db --packet pkt_A --request CONTEXT.json --out assignment-C
```

The extension request is `{source_refs: [{collection, id, version}], reason: nonempty string}`.
Use live captured anchors or source-origin items/parts. A selected item supplies its statement/setup;
an explicit proof anchor supplies a borrowed passage. Group known additions into one request.
The reason stays private. C retains A's tasks, targets and prior context, including after an
inconclusive completed review; it does not add supplier-review obligations. Changed prior mathematics
needs renewed ordinary work. Oversize context creates no packet. Deliver C once, not full A plus C.

A new response must name C. Rebase cannot claim newly supplied independent evidence. Existing
judgments survive until an explicit successor; newest does not win automatically. Disclose actual
same-reviewer continuation. See [mapping/provenance](review-mapping.md) when a source target or
permissible predecessor pin is needed. `get --extend` remains for direct packets only; its request
is `{targets: [Ref], source_anchor_ids: [ID], source_paths: [string], reason: string}`.

Inspect and replay ambiguous `received` intake unchanged before replacing it. Terminal receipts remain
historical. Same-byte artifact output may be reused; different output requires a new directory.
Notes/check-link edits need not stale mathematics. Adding coverage or changing its spans/claims can
reopen composition while local derivations remain current; changed source or scope can also reopen work.
Prefer saving coverage with the checks that examine it. Controller coverage uses `check_task_ids`,
`existing_check_refs`, and `replaces`; direct stored coverage uses `check_ids`, with replacement in
the enclosing edit. Generate the relevant shape rather than copying fields between these interfaces.
Use bounded change diagnostics instead of repeating unaffected checks. When evidence, reasoning and
blocker are unchanged, act on the existing next action or stop that branch; do not create another draft.

## Review and finish

Prepare independent work with `--mode independent`; arrange [qualification](database-qualification.md)
once for the actual configuration and reuse it while that configuration is unchanged. If fresh
independent execution is unavailable, save useful primary work and a reviewer handoff.
Preserve the original response, [map if needed](review-mapping.md), then prepare `--mode reconcile`.
Use generated exact-target eligible pins and [reconciliation rules](reconciler.md).

Preparation selects unfinished work. To correct an already satisfied primary check, use a current
`get --mode primary` packet and `apply` with a full successor-check body, or an authorized reconciliation
batch. `--task` does not reopen completed work. Back up SQLite for recovery; JSON exports omit intake/history.
