# Graph scope and scheduling audit

Read-only audit of the fixed shared core on 2026-09-14. Production files were not changed. Four small fixtures were created through the public packet, apply, comparison and assessment APIs using the existing shared Python installation. Independent review was disabled in these probes to isolate graph scope and primary checking behavior.

Reproduce with `python -B architecture-proofcheck/goal-alignment-audit-2026-09-14/dataset_probe.py`. Saved results: [dataset_run_f3d3bcb3/results.json](dataset_run_f3d3bcb3/results.json). Each case passes `validate_snapshot`.

## 1. Focused audits do not follow required prerequisites

**Priority: high.** The checker can finish every listed task while a consumed internal lemma has never been checked.

Contract: [architecture.md](../architecture.md), line 28, defines Focused as selected conclusions and the exact internal prerequisites they consume; lines 182 and 189 require work from prerequisites toward dependent conclusions. The current scope builder only adds explicit targets and their parts: `shared/paper_core/assessment.py:431-454`. Incoming uses create application tasks at lines 486-488, but do not add the supplier's establishing work. A supplier without a derived obligation is treated as open at lines 787-791.

Observed case `focused_prerequisite`: the audit targets the theorem; its recorded use consumes the lemma. The packet contains the lemma statement, correctly without recursively copying its argument. After three theorem/application checks and its fidelity observation, status reports **4/4 complete, process_complete=true, no problems, no unsatisfied tasks**, although no lemma check exists. The theorem remains amber/conditional. This is an omitted-work problem, not a false green theorem.

Small correction: derive the required prerequisite closure from actual uses and establishing routes, with explicit exclusions where intended. Keep packets bounded by scheduling the supplier separately. Do not require the user to manually maintain a second copy of the dependency closure in audit targets.

## 2. A consumed intermediate without an establishing inference has no task

**Priority: high.** A newly identified necessary claim can disappear from the remaining-work list precisely when the graph needs refinement.

Contract: `handoff/record-contract.md:114` requires intermediate claims' establishing groups/arguments to be identified through actual uses and the work queue; `architecture.md:184` requires closing the supporting claims and final conclusion. `assessment.py:466-488` creates tasks only for existing arguments, groups and uses. Its missing-route fallback at lines 489-491 applies to the outer proof-required statement, not a consumed intermediate member. Intermediate support merely returns conditional when no establishing group exists, at lines 829-840 and 858-860.

Observed case `unestablished_intermediate`: the theorem consumes source-backed `itm_hidden`, owned by that theorem. The item has no establishing group or argument. Every other task is checked. Status reports **7/7 complete, process_complete=true, no problems, no unsatisfied tasks**. There is no required task or assessment entry for `itm_hidden`; the theorem is conditional.

Small correction: expose a missing-establishment action for every consumed non-assumption claim without a route, then derive its ordinary checking tasks once the group or argument is registered. A valid draft should still save and render. This does not require a new proof verdict or one task per source line.

## 3. Full audits do not notice newly inventoried proof results

**Priority: high.** A complete Full audit stays complete after another unchecked theorem is registered in the same paper.

Contract: `architecture.md:29-31` requires all proof-required results and written arguments in the declared manuscript scope, with explicit exclusions. `assessment.py:431-454` applies the same explicit-target-only rule to Full. Completion at lines 1049-1062 checks only the obligations produced by that rule; it never compares the full inventory against the declared coverage.

Observed case `full_inventory_growth`: a Full audit finishes its two listed results, then a third source-backed theorem is added through a paper-scoped author packet. The result remains **7/7 complete, process_complete=true, no problems**, while the database contains three proof-required major items and progress still counts two. No exclusion accounts for the third.

Small correction: for Full, compare the current in-scope proof inventory with included targets and explicit exclusions. A newly discovered result should either enter required work or reopen scope review. The report can continue displaying completed checks for the original two results.

## 4. The graph does not yet provide a usable checking order

**Priority: medium, but central to the requested workflow.** Resuming work still requires the coordinator to reconstruct readiness and order from the graph.

Contract: `architecture.md:189` says the scheduler uses the detailed item/use graph; `handoff/checker-protocol.md:11` directs ready obligations from prerequisites toward the target. `assessment.py:1029` sorts obligations by their hash IDs. `queries.py:181-182` returns required/unsatisfied IDs without prerequisites or readiness. The only topological queue found in the core is the major-graph layout routine, `projection.py:714-738`.

Observed case `cycle_and_order.acyclic_unchecked`: required work is listed as lemma composition, theorem derivation, lemma fidelity, lemma derivation, theorem composition, theorem fidelity, application. This is deterministic identity order, not a checking sequence. No task specifies which prerequisite is blocking it or which bounded packet to request next.

Small correction: expose a derived work list with target, action, prerequisites and readiness. Order acyclic branches from suppliers toward consumers and local derivations toward composition. Allow explicit provisional work without calling unresolved support established. This can be a query over the existing records, not a separate stored scheduling system.

### Cycle qualification

The cycle probe is secondary to the scope omissions. For a genuine lemma-to-theorem-to-lemma use cycle, `assessment.py:805-806` returns conditional support without recording the implicated cycle. Status reports **8/8 complete, no problems**. The projection does detect the major cycle and selects its same-shell index; [dataset_cycle_projection.json](dataset_cycle_projection.json) preserves the exact diagnostic. Its message explains only the major-owner projection limitation, and both summary limitations and report problems are empty.

This is **not** evidence that process completion must require mathematical support. The local outcomes correctly remain conditional, and genuine induction or simultaneous arguments can be legitimate. The narrower gap is that the work interface cannot identify an actual detailed-graph cycle for inspection or distinguish it from a cycle introduced by display aggregation. Keep that diagnostic separate from automatic mathematical refutation.
