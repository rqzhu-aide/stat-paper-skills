# Proof-Check Execution Order

## Canonical dependency table

| Unit | Prerequisites | Dependents | Dependency status | Critical path? |
|---|---|---|---|---|

## Execution layers

| Layer | Units | May run independently? | Gate before starting |
|---|---|---|---|
| 0 | Inventory, proof associations, cross-references, source map | Yes | Source fixed; Focused scope is the exact target dependency closure; Full scope includes every proof-required unit |
| 1 | Base definitions and lemmas | If no shared dependency | Layer 0 reviewed |
| 2 | Intermediate results | By dependency table | Required base units checked |
| 3 | Main theorem assembly | Usually after prior layers | Critical chain available |
| 4 | Load-bearing method interfaces | By independent interface | Population derivations and application descriptions available |
| 5 | Dependency-closure registry and issue propagation | Cross-cutting | Local and interface checks complete |
| 6 | Exact global consistency matrix and adversarial pass | Cross-cutting | Registry binding, use records, and cross-reference anomaly reviews complete |
| 7 | Blinded critical-path challenge | By critical unit | Primary artifacts sealed |
| 8 | Progress, report, and finalization reconciliation | No | Challenger artifacts and global matrices complete |

## Unit order

| Priority | Unit | Source range | Reason | Dependencies | Next action |
|---|---|---|---|---|---|

## Closure checkpoint

- Closure contract version: 3
- Registry review binding current:
- Internal and external `Dxxx` use bijections complete:
- Internal uses bind exact `Cxxx` dependency conclusions and contract hashes:
- Per-conclusion support closures complete:
- External source evidence current:
- Dependency statuses and issues propagated:
- Global consistency matrix complete:
- Progress and final report reconciled:

## Blocked work

| Unit | Blocker | Required evidence | Downstream effect |
|---|---|---|---|
