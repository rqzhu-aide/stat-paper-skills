# Independent Challenge Protocol

This file is the sole semantic authority for proofcheck challenger selection,
blinding, evidence, reconciliation, and artifact binding. Reporting projects
these records but does not redefine them.

## Select the effective-critical set

The effective-critical set is the union of:

- manifest-declared critical units (every target unit must be declared
  critical);
- every in-scope unit affected by an open, deferred, or resolved load-bearing
  S0 or S1 issue, including a historical required challenge retained after
  repair; and
- when the manifest sets `audit_scope.verified_challenge_sample_rate` to a
  finite number in (0, 1], a deterministic sample drawn from all in-scope
  units: score each as sha256 of `<source_snapshot_sha256>:<unit_id>` and take
  the exact ceiling of rate times the in-scope count with the lowest scores.
  Membership is a pure function of the source snapshot and the in-scope set,
  so the sample is reproducible, identical at every computation site, and
  cannot be steered by editing critical declarations or issue records; units
  the sample shares with the other two branches are already required, so the
  overlap costs nothing. Set a nonzero rate (0.2 is a reasonable default) for
  a Full audit so that units the primary checker marked verified without
  incident still receive independent re-derivation; a unit wrongly marked
  verified never promotes itself through an issue.

For each unit, set covered_issue_ids to the exact sorted triggering issue set.
Use an empty list only when the unit is critical solely by manifest declaration
or sampling. A resolved severe issue remains a trigger for the fresh
post-repair challenge.

## Build a blinded packet

Start the challenger from a fresh context and generate:

    python "<skill-root>/scripts/proofcheck.py" packet --root "<audit-root>" --unit-id <unit-id> --mode challenge --output "<challenge-packet.json>"

The packet must contain the current source-snapshot identity, exact locked
source, normalized obligation, unit inventory, direct dependency contracts,
relevant downstream uses, neutral issue triggers, and all risk aspects. Exact
line number and text remain visible. Enclosing span hashes, source-member file
hashes, source snapshot, and semantic context hashes retain traceability;
redundant per-line hashes are not model-visible.

Each issue trigger contains only its ID, severity, structured target_contract,
target_contract_sha256, and neutral propagation evidence. Do not expose the
primary reasoning, steps, finding narrative, summary, verdict, repair proposal,
report, unrelated ledger, or prior conversation.

For a historical challenge whose old downstream path was retired, reconstruct
the sealed prior dependency registry. Expose only the neutral retired edges
that cut a prior root-to-unit path, the exact neutral current route when one
exists, and current retirement anchors. Record explicitly when no current
structural route exists. Do not expose archived statuses, compatibility
verdicts, or issue backlinks.

Source-locked code, configuration, and other valid evidence outside the LaTeX
snapshot must be projected as portable names, exact ranges, hashes, and lines,
without host-specific paths.

## Perform the challenge

A same-context reread is not independent. Record one of:

- fresh_context_same_model;
- different_model;
- independent_human.

For a challenge covering an S0 issue, prefer `different_model` or
`independent_human` when available: same-model blind spots correlate exactly
where a fatal finding matters most. `fresh_context_same_model` remains valid;
the recorded independence level discloses the limitation in the final report.

One fresh challenger pass should assess all triggering issues for one unit.
Closely related units may share one call only when every complete packet fits
and the output gives each unit a separate verdict, assessment set, and
disagreement list. The challenger need not duplicate the full atomic ledger.

The challenger must:

- inspect the exact source and obligation in order;
- test the primary proof target without seeing the primary answer;
- check all direct dependencies and relevant later uses;
- apply all eight risk aspects;
- assess every neutral issue target and its downstream relevance;
- give a separate unit verdict and source-anchored disagreement list.

If a challenger is unavailable, disclose the audit as single-pass and do not
claim independent confirmation.

## Record exact challenge evidence

Record:

- source_snapshot_sha256;
- challenged_ledger_sha256, computed from the canonical ledger without
  independent_check;
- challenge_context_sha256, copied from the exact challenge packet
  context_binding_sha256;
- challenge_artifact_sha256;
- generated_utc;
- independence level;
- primary, challenger, and reconciled verdicts;
- ordered disagreements and resolution;
- exact artifact path;
- exact covered_issue_ids.

For every covered issue, record one issue_assessments object containing exactly:

- issue_id;
- target_contract_sha256;
- assessment, using only confirmed, not_confirmed, or unclear;
- substantive target_assessment;
- substantive downstream_assessment.

The assessment ID set must equal covered_issue_ids. Both lists are empty for a
manifest-only critical unit. Listing an issue ID without assessing its exact
target and downstream relevance is not coverage.

Fix the blinded artifact and challenger record before reconciliation. An
agreed challenge has identical challenger and reconciled verdicts equal to the
final unit status, with no disagreements. A resolved challenge has a reconciled
verdict equal to the final unit status, at least one recorded disagreement, and
a substantive resolution.

## Bind the artifact

After the blinded narrative, verdict, and assessment rows are fixed, run:

    python "<skill-root>/scripts/proofcheck.py" bind-challenge --root "<audit-root>" --unit-id <unit-id>

The command inserts or replaces exactly one proofcheck-challenge-binding-v1
JSON block, verifies current packet semantics, and writes the artifact and
ledger transactionally. The binding block's unit ID, context hash, challenger
verdict, and canonical issue assessments must equal the ledger. Do not hand-edit
it. Rerun the command whenever the artifact or assessment changes.

Finalization reconstructs the challenge packet and rejects a stale semantic
context, stale target-contract hash, missing or extra issue, stale ledger or
artifact hash, invalid independence level, or unresolved reconciliation.
