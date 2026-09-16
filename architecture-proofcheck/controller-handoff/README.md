# Controller implementation details and examples

Read [the implementation plan](../controller-implementation-plan.md) first and the [implementation receipt](../controller-implementation-2026-09-15/README.md) for delivered behavior and validation. These examples use illustrative IDs and require an actual prepared packet; they are not existing audit receipts.

| File | Purpose |
|---|---|
| [Task derivation](task-derivation-design.md) | Effective scope, exact establishment, task/unit fields and coherent selection |
| [Packet and reader](packet-reader-design.md) | Local context, task-specific authority/bindings, independent isolation and reader links |
| [Submission and recovery](submission-design.md) | Intake DDL, transaction seam, idempotency, partial saves and migration |
| [Example context](example-context.json) | Small argument and deterministic task IDs used in the response examples |
| [Primary response](example-primary-response.json) | One response containing five observations/checks and one explicit coverage span |
| [Coordinator envelope](example-envelope.json) | Trusted metadata wrapping the unchanged primary response |
| [Partial response](example-partial-response.json) | Source comparison and two applications saved before the remaining derivation/composition |

## Example interpretation

The graph has two assumptions, \(u \leq v\) and \(v \leq w\), for the same real variables, and target \(u \leq w\). The group `grp_T` uses both assumptions through `use_A_T` and `use_B_T`; `arg_T` has this group as its final group. The scope supplies the real-variable binders and both assumption identities. All other prerequisite source/context work is already examined. This is a local primary assignment, not a complete Full audit or independent review.

The source statement is linked through `anc_T_statement`. The proof excerpt in `anc_T_proof` is exactly:

```text
By transitivity, u <= v and v <= w imply u <= w.
```

Its 48 characters are covered by `[0, 48)`. The coverage row links the theorem claim and the joint-derivation check created by this response. It does not manufacture coverage from the presence of the excerpt.

The assignment contains three work units: source fidelity, the joint group including its two applications, and final composition. It produces five observation/check records plus one coverage record. Only source fidelity is initially ready, but selection can include its same-argument successors in order. The supplied assumptions are context, not separately assigned proof derivations.

Task IDs use the current `obligation_id(audit_id, target, kind, role)` formula with audit `aud_example` and role `primary`. Stable example record IDs are deliberately readable; real generated record IDs remain opaque. `example-context.json` is a fixture description, not a complete packet or an authoring batch. The implementer must build the corresponding source-linked database and obtain an actual version-2 packet through `work prepare` in the integration test, replacing the illustrative packet ID.

## Partial-save exercise

Submit either the complete response or the partial response under `req_example`, never both with the same request ID. The partial file preserves three results and leaves the group derivation and composition unfinished. It does not claim written coverage yet.

Then inspect the receipt and prepare the two remaining obligations. If the worker already produced their reasoning under the original packet, submit that explicit subset in a new request, leaving its original `packet_id` unchanged and setting the envelope's `rebase_packet_id` to the fresh packet. The controller validates unchanged consumed inputs and the fresh write scope. If the mathematical inputs changed, reconsider the affected reasoning instead of rewriting packet identity.

For a malformed-output fixture, remove `outcome` from one included check. The expected result is preserved input with a diagnostic pointing to that result field, no mathematical commit, and no credit for the other included entries. A corrected response uses a new request ID. The coordinator may instead deliberately submit a valid subset; the controller never chooses that subset silently.

The plan's implementation gates require these examples to become executable installed-only fixtures. Their presence here does not claim runtime or mathematical evaluation has occurred.
