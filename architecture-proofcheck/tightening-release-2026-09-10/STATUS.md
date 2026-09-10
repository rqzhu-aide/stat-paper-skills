# Proofcheck release: targeted reliability repairs

Status: repairs and release verification complete. This release
publishes the current proofcheck 1.5 package, including the accumulated local
improvements and the five repairs from the
[10 September audit](../tightening-audit-2026-09-10.md).

| Repair | Result |
|---|---|
| Uncertainty in finding details | An inconclusive or presentation finding no longer acquires a failed-inference label in its proof path. Resolved findings remain historical. |
| Independent repair directions | Each direction retains its finding, exact target, scientific cost, and verification state. The summary does not infer that separate remedies are alternatives. |
| Multi-file theorem identities | Generated collisions use relative manuscript paths. Existing unambiguous and explicit identities remain stable; remaining collisions stop setup with both locations. |
| Source-selection ambiguity | Active literal `\includeonly` and content after `\end{document}` produce early diagnostics. Candidate sources remain intact until the checker reviews scope. Controls inside comments or other masked text do not trigger these warnings. |
| Lookup during drafting | Exact step lookup needs valid source binding, grouping, keys, and ranges. Unfinished mathematical annotations do not block reading the source. Compilation and submission retain their complete checks. |

The architecture remains unchanged: locked sources and reviewed scope feed
source-bound proof records, independent challenges, dependency checks, and one
canonical report projection. The opening summary and graph reuse those records.
These repairs add no model stage, schema migration, or mathematical acceptance
exception.

The root README now describes the report, source-layout guidance, shared Python
and LaTeX setup, and validated runtime-only installation. Separate local
writing-skill changes are excluded from this release.

## Verification

Focused source, lookup, and report regressions passed before release renewal.
The renewed reference is FINAL, current, and usable. Its source, ledgers,
mathematical judgments, calibration, and independent responses are unchanged.
Only its manifest release metadata, finalization record, HTML report, and
derived Markdown report changed. See [reference renewal](reference-renewal.json).

The exact staged Git tree passed skill metadata validation and portable
[reference delivery](staged-delivery.txt). All 13 installer tests passed, with
the staged installer unchanged; see [installer test receipt](installer-tests.receipt.json).
The [full frozen suite](full-suite/20260910T214509Z-3a79d9b5/receipt.json) ran 1072 tests: 1071 passed, 1 skipped, no failures or errors (19.01 minutes). The receipt records the skip reason. The complete package and runner hashes stayed unchanged throughout the run.

The [installed runtime](installation.json) contains 191 files and exactly matches the accepted release's runtime selection. Its reference is FINAL, current, and usable. The previous installation was preserved outside skill discovery. No duplicate installation was found in the checked locations.

Automated HTML/Markdown regressions check finding classification, source links,
repair ownership, and existing summary compactness limits. The browser URL
policy prevented a visual inspection of the local HTML; this release does not
claim a successful browser visual check.

Software regressions and a valid evidence bundle do not establish mathematical
expertise. The separate release-evaluation corpus retains its disclosed need
for independent expert review. This remains a non-formal proof auditing skill.

## Release contents

The Git-materialized proofcheck source contains 274 files, about 5.95 MB,
including developer tests and evaluations. Installed runtime excludes `tests/`,
`evals/`, caches, and bytecode. Historical report examples and development
working copies remain in the local Git-ignored `archived/` folder. The small
shipped reference retains the historical records needed to authenticate its
current evidence; it does not depend on the local archive.

Authenticated reference and acceptance files preserve their original bytes in
Git. The whitespace check accepts CRLF as a line ending, while still checking
other whitespace errors. See [staging selection and identities](staging.json).
