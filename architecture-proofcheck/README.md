# Proofcheck architecture

This folder contains the complete target architecture, revision plan, and implementation handoff. The architecture was written on September 12, 2026; the concrete handoff was added on September 13 after reviewing the programmer's feedback. The September 15 [controller implementation receipt](controller-implementation-2026-09-15/README.md) records the delivered revision and remaining acceptance gates. The [controller implementation plan](controller-implementation-plan.md) defines its interfaces, batching, recovery and responsibilities after the [goal-alignment audit](goal-alignment-audit-2026-09-14/review.md).

| Document | Purpose |
|---|---|
| [v2.0 release](release-v2.0.md) | Coordinated release scope, content identities, validation and outstanding evaluation |
| [Controller implementation receipt](controller-implementation-2026-09-15/README.md) | Delivered behavior, test evidence, pilot findings and open acceptance gates |
| [Controller implementation plan](controller-implementation-plan.md) | Implemented task/unit/assignment model, commands, response schemas, transactions, migration and C0-C5 acceptance criteria |
| [Controller details and examples](controller-handoff/README.md) | Supporting task, packet and submission specifications, with complete/partial response examples |
| [Small controller revision plan](controller-revision-plan.md) | September 15 rationale: coordinator-owned scientific work, bounded mechanical scheduling, packet preparation, structured submission and recovery |
| [Implementation handoff](implementation-handoff.md) | Baseline implementation interfaces, concurrency, packaging, UI projection, checker protocol, owners and acceptance; the controller implementation plan specifies the delivered extension |
| [Architecture](architecture.md) | Complete system design: typed items and uses, source evidence, local checking, review, reuse, major-item graph, connection details, and report delivery |
| [Revision plan](revision-plan.md) | Phased implementation and migration from proofcheck v1.5 and the current Archify overview core, with concrete acceptance criteria |
| [Record contract](handoff/record-contract.md) | Closed JSON body shapes, identities, proof structure, checking, and freshness rules |
| [SQLite schema](handoff/schema.sql) | Executable DDL for the target record-level store, with a [synthetic batch](handoff/example-batch.json) |
| [Checker protocol](handoff/checker-protocol.md) | Initial coordinator, primary, independent, and reconciliation instructions for evaluation |
| [Archive](archived/README.md) | Previous architectures, plans, experiments, investigations, and release receipts |

The design uses one paper database and the existing adapted Archify UI. The graph shows major mathematical items only. Selecting a connection exposes intermediate reasoning and checks in the lower reader. Selecting a result exposes its complete derivation and final composition. Connection colors describe recorded current support, defects, unchecked work, or unresolved work.

The September 12-13 documents describe the original implementation target. The database workflow and bounded controller now ship in v2.0. The controller implementation plan owns the added interfaces/defaults; its supporting notes supply details and the implementation receipt records actual acceptance evidence. Existing record meanings remain authoritative except for changes explicitly specified in that plan. New audits use the database workflow; old v1.5 folders retain their legacy workflow. The release record explicitly retains the outstanding browser and large-paper evaluation. The plans preserve the distinction between source comparison, mathematical review, audit completion, and a theorem's actual status.

All 47 entries previously at this folder's top level were moved into the [local historical archive](archived/README.md). Existing historical content was preserved; the source release includes selected previously tracked evidence, not the full local archive. New implementation records should refer to the handoff, architecture, and revision plan here. Historical timing estimates remain provisional; the implementation receipt separates measured software and pilot evidence from release claims.
