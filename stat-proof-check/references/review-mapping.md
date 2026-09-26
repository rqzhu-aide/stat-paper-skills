# Coordinator mapping and independent provenance

This is coordinator-only material. Preserve worker response bytes before mapping or reconciliation.
The two packet identities have different jobs:

```text
A = original source-only worker packet, named by the unchanged response
B = current private coordinator packet containing the canonical mapping targets
```

After submitting the response from A, obtain B and generate a mapping scaffold:

```text
paper_audit.py get AUDIT.db --target items:itm_ID --mode primary --out mapping-context.json
paper_audit.py review mapping-template AUDIT.db --response rsp_ID --packet pkt_B --out mapping-help.json
paper_audit.py review map AUDIT.db --response rsp_ID --mapping MAPPING.json
```

Here `itm_ID` owns the argument; use a part target where appropriate. Replace `pkt_B` with
the packet ID returned in `mapping-context.json`. Obtain broader context through `get` if B
lacks a needed canonical record.

Author only the generated `template` member as `MAPPING.json`, filling reviewer, exact canonical
targets and source-grounded rationales. Use zero-based judgment indexes; `--judgment N` selects
particular rows. B's read set must contain each mapped record. Original reviewed scope and source
overlap remain tied to A. Neither mapping nor a corrected envelope can change a judgment's kind,
reasoning, outcome, evidence, or actual coverage. Wrong kinds or malformed content require a
corrected worker response. For a correctly identified inference missing from the graph, refine
from source and map where permissible through a current B. Preserve the original response.
New evidence requires actual examination, not relabeling old bytes.

Equivalent routine reasoning actually examined in an accepted response may be mapped with an
explicit equivalence rationale. Mapping cannot duplicate an exact existing mapping or credit unseen
mathematics. Substantive new reasoning or changed conditions uses
[supplied-route review](supplied-route-review.md). Item/part completion requires all required
exact route examinations and their reconciliations; mapping one composition does not close the rest.

The current response may become accepted while its original submission receipt remains
`needs_revision`. Inspect current record state separately from that historical transport receipt.
Retain pending original opinions and resolve their substantive issues rather than silently dropping
counterexamples when a corrected response arrives.

Record actual reviewer identity and qualification from dispatch, never worker-written fields.
Use `source_only` only for verified isolation; use `route_provided` for its declared supplied packet.
Unverified access or exposure is `compromised`, with a reason. The worker's `none_known` report
cannot improve the coordinator's assessment. For a context extension continuing the same review,
record continuity in the exposure note. Provide a predecessor pin only from that reviewer's own
saved examination; do not disclose other opinions or call continuation a fresh blind launch.

The direct `get` / `review submit` path remains supported. Its envelope contains
`contract_version, request_id, packet_id, reviewer, qualification_id, exposure, exposure_note`.
It omits the controller-only `rebase_packet_id`. Use controller assignments for normal work.
