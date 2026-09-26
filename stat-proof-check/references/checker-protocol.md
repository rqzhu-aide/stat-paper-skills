# Checker protocol (item-audit/1)

This is the routing page for current database audits. Protocol `item-audit/1` preserves
historical response identity; new packet features do not relabel old evidence. The installed
`paper_audit.py version` must report the matching protocol and `bundle.ok: true`.

Read only the assigned role:

| Role | Instructions |
|---|---|
| Coordinator | [Scope/dispatch](coordinator-protocol.md), then [controller operations](controller-workflow.md) as needed |
| Primary checker | [Primary brief](primary-checker.md), [mathematical method](mathematical-checking.md), [evidence/outcomes](evidence-and-verdicts.md) |
| Independent checker | [Independent brief](independent-checker.md) and the same two scientific references |
| Reconciler | [Reconciliation](reconciler.md), [evidence/outcomes](evidence-and-verdicts.md) |

Mathematical workers receive their packet, response scaffold and generated worker guidance.
The coordinator retains its manifest/guidance. Do not load this whole routing page again when
the role files have already been supplied. Add only relevant domain or external-source guidance.
Supplied-route work additionally uses [its exposure rules](supplied-route-review.md).
Coordinator mapping is documented [separately](review-mapping.md).

Existing v1.5 folders retain [their own workflow](legacy-workflow.md). Current database reports
use [database-audit.md](database-audit.md), not the legacy monolith's release commands.
