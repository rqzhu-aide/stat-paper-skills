# Frozen-runtime pilot result

The scientific audit found a false lemma and a false theorem. The database and working reader were produced, but the audit remains **NONFINAL** because reconciliation and independent-check currentness hit two controller defects. This is an evaluation result, not a release or proof certificate.

All artifacts in this report are relative to this `work` directory. The frozen skill and raw manuscript were unchanged.

## Scientific findings

The error is at `paper.tex` line 16: convergence for each fixed coordinate does not imply convergence of a maximum over a growing set of coordinates.

On a one-point probability space, set

\[
m_n=n,\qquad X_{n,j}=\mathbf 1\{j=n\},\quad 1\leq j\leq n.
\]

For every fixed \(j\), the coordinate is zero for every \(n>j\). All stated coordinate convergence assumptions hold. Yet every row maximum equals one. At \(\varepsilon=1/2\), its tail probability is always one. The lemma is refuted.

The theorem uses that lemma without an application mismatch. Its final substitution is valid **conditional on** the maximum converging to zero. Under the actual manuscript assumptions, however, the same example gives \(\hat\theta_n=\theta_0+1\), refuting consistency. Primary successors now classify the lemma's written route as a gap and the theorem's local composition as conditionally supported. Separate statement-refutation findings retain both false conclusions and the exact counterexample. Original judgments remain preserved.

The fresh independent reviewer independently produced this same counterexample and distinguished conditional application validity from statement truth. Two real calibration responses were graded before qualification. The reviewer first saw only its balanced calibration packet, then only source packets and protocol. No primary conclusions were supplied before its original responses were saved.

## Delivered state

- `report.html`: current working graph and reader, revision 23, five items and four uses.
- `AUDIT.db` and `AUDIT-backup.db`: canonical database and complete recovery copy.
- `snapshot.json`: mathematical export, not a substitute for the database backup.
- `final-status.json`, `final-worklist.json`, `validation.json`, `report-receipt.json`: current status and software validation receipts.
- `invocation-timing.json`, `invocations.jsonl`, `telemetry-summary.json`: counts, timing estimates, and exact controller invocation receipts.
- `calibration-source.md`, `calibration-response.json`, `calibration-evidence.json`: actual calibration provenance.
- `independent-1/` and `independent-2/`: immutable original worker responses, reviewer-authored representation-only successors, envelopes and mappings.
- `reconcile-lemma-2/receipt-targets.json` and `reconcile-theorem-2/receipt-targets.json`: isolated reconciliation rejection evidence.

Structural validation passes. Both complete proof passages have explicit substantive and structural coverage. The current report passes machine checks for graph geometry, displayed evidence, navigation structure and self-contained resources. **Browser visual acceptance was not performed.** No external network or private installation was used.

## Workflow results and friction

The deliberate partial save preserved two complete application checks and an unfinished derivation without demanding final coverage. Recovery restored the original intake bytes, and the next preparation supplied the exact saved draft. One theorem assignment saved four mathematical checks, two source comparisons, three coverage spans and a finding together.

The shipped database instructions lacked qualification receipt fields, the `CheckKind` target table and adequate reconciliation shape guidance. Targeted inspection of the frozen implementation was needed. Version output also did not contain the protocol field that its instructions promised. This was not an unassisted clean instruction pass.

Several authoring errors were retained and rejected atomically: a downstream use outside a local packet, evidence anchors outside a global packet, updates outside reconciliation scope, and an initially incorrect owner-item reconciliation target. One broad mapping packet became stale after a separate response mapping. Corrected requests preserved the rejected originals. Forty-four identifier-minting invocations contributed avoidable authoring overhead.

Two defects remain isolated in the frozen runtime:

1. Preserved original reviews with an unmappable item-level `adversarial` row remain `needs_revision`. Their accepted representation-only successors do not remove the originals' permanent reconciliation veto. The final per-obligation batches were rejected solely for those historical pending responses.
2. Updating coverage links from old primary checks to their explicit successors staled four independent composition records, including the two accepted successor reviews, although source, proof spans and mathematical claims were unchanged.

The resulting state is 15 of 19 current obligations examined, zero drafts and no source limits. The remaining four are two independent composition-currentness obligations and two reconciliations. Counterexamples and mathematical reasoning are saved; remaining work is record recovery and adjudication acceptance. No result was marked supported to satisfy a completion counter.

## Effort and limits

The run reached the saved working artifacts in 22.5 minutes. Controller counts are exact: **120 launched invocations**, including five startup invocations outside the detailed log; **12 preparations**, of which ten prepared work; **20 submissions**, all retained, of which twelve committed mathematical records. Eight submissions were accepted immediately; four committed independent intake as pending mapping, and eight rejected without a mathematical commit. Two initial shared-Python launches were denied by the restricted terminal and then resolved using approved normal access.

Coordinator time estimates are approximately seven minutes authoring, three minutes scientific reading/reasoning, and eleven minutes formatting and repair. Measured controller subprocess time was 46.87 seconds; internal command telemetry recorded 5.117 seconds. These measures exclude some launch/approval overhead and do not measure model reasoning. The independent reviewer separately reported about two minutes reasoning and 2 minutes 21 seconds drafting/validation, overlapping coordinator work. Token counts and actual model API invocation counts were unavailable.

This short live graph has no registered hidden intermediate. It does not establish hidden-claim ordering, changed-prerequisite recovery, long-paper scalability or visual usability. The independent outcome differences were substantive questions of judgment scope that led to explicit primary corrections, not manufactured disagreement. The frozen-run evidence must remain separate from any later patched-runtime continuation.
