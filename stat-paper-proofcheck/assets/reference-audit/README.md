# Complete Reference Audit

This directory contains one complete, finalized proofcheck audit, small enough
to read end to end. Use it as the canonical example of every record the
protocol requires: compare your in-progress records against the matching file
here whenever a schema or gate error is unclear. Do not copy its facts into a
real audit, and never edit it in place.

## Contents

- `paper/paper.tex`: the audited two-unit manuscript. `lem:growing-max`
  promotes per-fixed-j convergence in probability to a maximum over a growing
  index range (a real and classic error), and `thm:main` consumes exactly that
  conclusion.
- `proofcheck-audit/`: the finalized portable audit root. `delivery-check`
  reports `FINAL` with `usable_finalization: true` as shipped; the audit moves
  with the skill because it was scaffolded with `--portable-sources`.
- `workbench/`: the context-transfer files that by rule live outside an audit
  root: the compact annotation files both ledgers were compiled from, and the
  graded canary responses of the recorded calibration session.

## What it demonstrates

- A refuted conclusion: `lem:growing-max` C001 is `refuted` with a
  `counterexample` failure whose `computation` record locks the exact-rational
  instantiation script under `audit/05_adversarial/`.
- Canonical propagation: one root issue `I-001` (S1, `statement_refuted`,
  load-bearing) reaches `thm:main` through registry use `D001`; the theorem's
  conclusion is `not_established`, never `refuted`, because an invalid or
  unsupported proof does not establish falsity.
- An evidence-backed severity grading: `I-001.repair_search` records two
  failed strategies and one surviving strengthened-hypothesis candidate, so
  S1 rather than S0 is grounded in attempted repairs.
- Repair-cost triage on both suggested changes: the strengthened-hypothesis
  route is classified `unit_statement` / `adds_regularity_or_moment`, while
  the weakened fixed-range variant costs no assumption but records
  `claim_cost: restricts_scope`.
- Fresh-context challenges on both effective-critical units, with per-issue
  assessments bound by `bind-challenge`.
- A recorded passing checker-calibration session in
  `audit/07_runtime/CALIBRATION.json` (session `cal-001`).
- A defects-found final report whose issue index and detailed findings are
  generated projections, including the repair-search table.

## Verifying it

From the skill root:

```bash
python scripts/proofcheck.py status --root assets/reference-audit/proofcheck-audit
python scripts/proofcheck.py delivery-check --root assets/reference-audit/proofcheck-audit
```

After a validator change, this shipped copy goes stale by design (the
protocol identity is part of every challenge binding). Refresh a copy with
the bundled helper, which revalidates the protocol, mechanically rebinds both
challenges without touching any recorded judgment, and re-finalizes:

```bash
python assets/reference-audit/refresh_reference_audit.py <copy-of-proofcheck-audit>
```

Never mutate this shipped copy in place. The regression test
(`tests/test_reference_audit.py`) runs the same helper on a temporary copy,
so a validator change that breaks any record here fails the suite
immediately; to re-ship, run the helper on a copy and replace this directory
with the result.
