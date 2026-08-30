# Checker Calibration Canaries

Canaries test whether the checker detects mathematical errors rather than only
producing complete records. The sealed set contains planted defects and valid
proofs resembling common flaws, so it measures misses and false alarms.

## When and how

Run a session before local checking in every Focused or Full audit, and again
after any checker profile, configuration, or context change.

1. List ids and titles:

       python "<skill-root>/scripts/proofcheck.py" canary-list

2. Write packets outside the audit root. The session needs at least one
   flawed-style and one correct-style canary; sealed keys determine style.

       python "<skill-root>/scripts/proofcheck.py" canary-packet --canary-id <id> --output "<id>.canary-packet.json"

3. Give every packet in one session to the same fresh checker context. It
   returns one fixed JSON object per packet with `canary_id`,
   `argument_status`, `statement_status`, `defect_lines`, and a substantive
   `justification`. Fix all responses before grading. Never reuse a context ID
   across sessions.

4. Grade both styles together and record the reviewed checker binding:

       python "<skill-root>/scripts/proofcheck.py" canary-grade --response "<id>.response.json" --response "<other-id>.response.json" --session-id cal-001 --root "<audit-root>" --checker-profile-id "<profile-id>" --checker-configuration-id "<configuration-id>" --checker-context-id "<fresh-context-id>" --reviewed-binding

The record stores each complete response and canonical hash. Finalization
re-grades it against the sealed key and verifies the complete canary-bundle
digest, unique chronological sessions and canary ids, and consistent result
and session pass fields. Missing, stale, malformed, unbalanced, or failing
latest evidence blocks finalization. The recorded source snapshot and
validator hashes are provenance, not currency requirements: calibration
attests the checker, so a paper edit or validator release does not stale a
session; a changed canary bundle, a re-grade disagreement, or a changed
checker binding does.

The checker identifiers are reviewed coordinator declarations. The tool cannot
verify runtime checker identity; this exact limitation is stored in the
session. A changed profile, configuration, or context requires a new session.

## Existing proof work

Calibration is prospective. If live `audit/04_local_checks/*.ledger.json`
files exist, `canary-grade` records their hashes. Each must then be fully
rechecked under the declared binding and replaced or recompiled so its hash
changes. Re-run affected dependency and challenge checks. Removing an obsolete
ledger is acceptable only when ordinary scope gates agree. Do not grade again
to clear the hashes: another latest session snapshots the current ledgers and
starts a new boundary. Stale or malformed records are hash-archived byte-for-byte
under `audit/07_runtime/calibration-history/`; redirected or non-regular paths
are refused. Intact schema-2 archives reserve declared context IDs; unparseable
bytes cannot supply one. `canary-grade` holds an exclusive update lock across archival and
commit; packets and finalization fail closed while it exists. After a crash,
confirm no grading process is running, inspect the lock and record, remove the
lock manually, and rerun. Every packet and primary work context binds the latest passing session
receipt. A new session invalidates old packets, annotations, ledgers, and
challenges. First move each old live ledger into `audit/04_local_checks/history/`
with a name that does not end in `.ledger.json`, such as
`unit.ledger.pre-calibration.json`. Then regenerate the packet from the direct
live skeleton, create a fresh annotation scaffold, fully re-review, and
recompile the canonical ledger. `rebind-annotations` refuses a calibration
receipt change.

## Blinding and boundary

Never open `assets/canaries/*.key.json` or index rationales in a context that
checks a canary or the paper. The checker sees packets only. Expected answers
and key rationales are not recorded or printed. A pass is necessary evidence
against rubber-stamping, not proof of competence on the paper's hardest steps,
and never strengthens a proof verdict.
