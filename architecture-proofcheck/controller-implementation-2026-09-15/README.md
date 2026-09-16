# Bounded controller implementation

Implementation date: September 15, 2026. The controller is implemented, including three corrections discovered by the live pilot. Automated validation and the separate recovery continuations are recorded below. This is development evidence, not release approval.

Subsequent distribution: the user requested [v2.0](../release-v2.0.md). That release record owns current metadata/routing and distribution status. This receipt preserves the earlier implementation checkpoint and its remaining evaluation limits.

The coordinator still reads the paper, chooses proof boundaries, builds and refines the graph, dispatches models, and adjudicates scientific findings. The controller provides four synchronous tools: list recorded work, prepare a coherent assignment, submit structured output, and inspect saved work. It performs no model calls or mathematical reasoning.

## Delivered behavior

- Work derives from accepted graph records. It follows exact suppliers, scoped assumptions and establishing routes, with bounded cycle analysis and explicit diagnostics for incomplete structure. Negative examinations remain examined work; they do not cause an endless retry loop.
- Preparation can include an ordered sequence of local applications, joint reasoning and composition in one assignment. Five units are the default, ten the maximum. One model response can create more than ten individually tracked checks. Joint context is never silently truncated.
- Primary responses carry task IDs and scientific content. The controller supplies administrative fields and saves explicit checks, source comparisons, coverage and findings atomically. Independent workers receive source-only context and retain their separate response contract.
- Original response bytes survive malformed output, freshness conflicts and interrupted processing. Exact retries return their historical result. Partial saves and drafts leave a current remainder. Rebase is explicit and compares consumed mathematical inputs, including separately cited evidence.
- Higher results can be checked under the exact statements of lower results. A supplier proof defect remains attached to its own inference; local validity and dependency support remain separate.
- The existing Archify reader keeps major graph nodes. Its paginated worklist links to exact examinations in the lower reader, including intermediate results and joint reasoning. The HTML remains a read-only snapshot.
- Native storage is format 3, with explicit format-2 migration and SQLite backup recovery. Record contract 3 and review protocol `item-audit/1` are unchanged. Packet and projection formats are 2. Historical packet-1 evidence remains supported.

No provider framework, background worker loop, queue, persistent task mirror or automatic graph extraction was added. The maintained additions are `work.py` and `controller.py`, with focused changes to the existing storage, assessment, packet, acceptance, CLI and reader modules.

## Evidence and limits

The executable first-slice test prepares one argument and atomically saves source fidelity, two applications, joint derivation and final composition as five observations/checks plus explicit coverage. Other fixtures cover exact task authority, partial work, drafts, replay, failures around transactions, evidence changes, source-only privacy, migration, backup and bounded local packet size. These are software fixtures, not mathematical reviewer evidence.

| Check | Result |
|---|---|
| New-format integration suite | Final tree passed: 1,124 tests run in 244.927 seconds; one Windows symlink-permission skip |
| Existing overview reader suite | 115 tests passed in 24.141 seconds |
| Installer suite | 13 tests passed |
| Proofcheck skill structure | 7 tests passed; existing instruction-size budgets retained |
| Skill metadata validation | Both proofcheck and overview valid |
| Reader interaction checks | 9 renderer checks and 5 simulated interaction fixtures passed; no real-browser claim |
| Bundle identity | Both generated 40-file cores match maintained source |
| Live mathematical pilot | Final runtime: 19/19 examinations complete at unchanged revision 31; original failures and recovery evidence retained |
| Actual browser visual acceptance | Not performed |

The earlier full new-format run found seven old expectations for command names, format numbers and newly included scope. Those expectations were updated to the specified behavior. Imported legacy argument drafts still retain their old findings but now explicitly need registered establishing routes. No mathematical outcome was changed to make a test pass. The skip is `BundleFileSelectionTests.test_bundle_files_refuses_a_symlink`: this Windows account lacks permission to create the test symlink. Node-backed checks ran.

The final shared-core identity is `b45abd465da23a6c67ce43c40d3a547ebfa88cb9f36c5eab25e9476350ae9b7d`. The first recovery used `dad859214fc02eaee4a4fe9693fafd896aa9f87a542ab7a48d8dd097375a3310`; the initial frozen pilot used `96a8b2bfe1e6df26345479eeeed53c9c7b3652d0db3f0aba1e0d86c3356ab30d`. The historical audited baseline was `6b27574bf1baece6d7c1bbd5c404a9eca4afe14ad75b6db3e42d74e485f1f428`; it comes from the preceding audit, not a fresh start-of-run snapshot. The working tree already contained extensive implementation and writing changes, which were preserved.

Logs: [new format](new-format.log), [initial failures](initial-new-format.log), [overview reader](reader.log), [installer](installer.log), [bundle check](bundle-check.json), and [implementation instruction hashes](instruction-hashes.json). The local-only `input-manifest.json` is an intermediate repository inventory, not a release receipt. Instruction hashes identify the implementation checkpoint before v2.0 metadata/routing changes.

Commands were run from the repository root with the shared Python installation at `C:/Users/zrq/AppData/Local/Python/pythoncore-3.14-64/python.exe`, using `-B`:

```text
python -B -m unittest discover -s tests/new_format
python -B -m unittest discover -s archify-proofs-overview/tests
python -B -m unittest discover -s tools -p test_install_proofcheck.py
python -B -m unittest discover -s stat-paper-proofcheck/tests -p test_skill_structure.py
python -B tools/build_paper_core_bundles.py --check
```

Both skills also passed the shared skill-creator `quick_validate.py` with `-X utf8`. The legacy monolith's full suite was not rerun: its runtime files were unchanged, and the plan calls for the affected new-format, reader, installer and skill-instruction checks. No earlier legacy passing result is represented as evidence from this run.

## Live instruction corrections

The forward coordinator received a frozen skill copy and raw manuscript only. It did not receive tests, prior diagnoses or expected mathematical answers. Its separate reviewer received neutral calibration cases and then source-only proof packets.

The pilot exposed missing qualification-receipt guidance, an undefined `CheckKind` in independent response instructions, and an inaccurate protocol-version lookup instruction. The installed references now define the calibration evidence and receipt shapes, all check kinds and target mappings, and the actual bundle-manifest lookup. The frozen copy remains unchanged; corrections are recorded separately. This pilot therefore cannot be described as an unassisted first-pass success.

The pilot also exposed a real recovery defect: a preserved `needs_revision` response permanently blocked reconciliation even after an accepted corrected review. Reconciliation now uses accepted independent evidence, rejects listed checks from pending responses, and still requires all accepted reviews to be accounted for. The original response remains unchanged and visible. Three regressions and 212 existing affected tests passed after this correction.

A second defect concerned persisted freshness bindings after mapping an independent controller response. Mapping used a generic coordinator packet and lost the original controller assignment's semantic membership policy, so a bookkeeping-only coverage-link update unnecessarily staled the review. The correction preserves controller origin for stored evidence bindings while keeping generic command acceptance strict. Seven new regressions check harmless coverage changes, changed spans/claims/proof excerpts, generic and historical origins, and transaction conflicts. The intermediate suite passed with 1,116 tests and one skip.

The recovery continuation exposed a third defect: five exact-target reconciliation rows were accepted, but completion incorrectly demanded a single row covering every check across each result's whole route. Completion now combines their exact current check references. It still requires nonempty current independent evidence and every required independent examination. Eight new regressions cover successful aggregation, a missing row, unresolved rows and explicit successors, stale rows, a late accepted check, all-stale evidence, missing final composition and an added proof route. Two older expectations were corrected because stale evidence can no longer grant reconciliation credit through an empty set. The 204 affected tests passed before bundle regeneration.

The [frozen pilot report](pilot-frozen-report.md) and [measurements](pilot-frozen-timing.json) preserve the original failure. It produced a working reader, a real calibrated independent review, partial-save recovery and one six-result theorem submission. At that point it remained at 15/19 completed examinations. The [first recovery](pilot-recovery-before-aggregation.md) used a backup and the patched bundle, reached 17/19 and isolated the aggregation defect. Its [coverage bookkeeping test](pilot-bookkeeping-result.json) confirms harmless coverage-link changes preserve current reviews and full proof coverage. Neither continuation changes the frozen run or requests new mathematical reasoning.

The [final runtime check](pilot-final-report.md) reaches **19/19 current required examinations**, with both independent-review indicators complete, zero drafts, no source limits and no proof-coverage problems. It runs against another backup copy and changes none of the 84 scientific records. Two statement-refutation findings remain open, the lemma's route remains a gap, and the theorem's local composition remains supported only under its explicit supplier premise. Process completion does not mean the manuscript is correct.

[Preservation evidence](pilot-scientific-preservation.json) and [byte verification](pilot-unchanged-bytes.json) confirm that all 205 original frozen files, all 74 first-recovery files and the raw independent responses are unchanged. The two pending original responses and four historical stale bindings remain visible without receiving current credit. The final check used eight successful controller calls and 4.569 seconds of subprocess execution, with no preparations, submissions, mappings, scientific edits or new reviewer calls. Its [timing receipt](pilot-final-timing.json) separates the roughly 72-second artifact checkpoint from 154 seconds through the written report.

The [working reader](pilot-reader.html) is a self-contained snapshot of that completed process. The local-only `pilot-evidence.zip`, identified by its [manifest](pilot-archive-manifest.json), preserves the frozen runtime/source/work, both continuation runtimes, databases, unchanged responses, rejected attempts and command receipts. It is excluded from the Git release. Copied pilot reports describe paths relative to their original directories inside that archive. Historical database source paths remain recorded; the archive is evidence, not an installed skill or portable migration.

The frozen run reached working artifacts in 22.5 minutes. Estimated coordinator time was seven minutes authoring, three minutes reasoning and eleven minutes formatting/repair; measured controller subprocess time was 46.87 seconds. These are not a speed comparison with the old system or the large DRL paper. Forty-four ID-minting calls were avoidable; installed instructions now recommend the existing batch-ID option. The live graph has five major items and no hidden intermediate, so hidden-claim behavior remains software-fixture evidence rather than live-pilot evidence.

## Phase and release status

C0-C4 implement the controller specification. C5 software tests, the live reasoning pilot and actual browser acceptance are separate evidence categories. A completed test suite does not certify graph completeness or mathematical truth.

Skill release metadata remains at its existing value. R8 release/distribution, a machine-wide skill installation, commits and publication were not performed. The database workflow remains explicitly selectable as a pilot through the installed instruction route; the released v1.5 workflow remains separate.

For use, start at [the shipped coordinator workflow](../../stat-paper-proofcheck/references/controller-workflow.md). The [implementation plan](../controller-implementation-plan.md) remains the interface specification; this record owns what was actually delivered and validated.
