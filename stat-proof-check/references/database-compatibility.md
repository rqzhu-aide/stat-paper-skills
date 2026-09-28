# Database compatibility and migration

Use this reference for an explicitly requested legacy proof-check import or maintenance of an
existing proof-check database. Follow the [work-folder and separation rules](database-audit.md#choose-the-work-folder).
Run these examples from that root; `AUDIT.db` means its `audit.db`.

    python "<skill-root>/scripts/paper_audit.py" import-legacy <legacy-audit-folder> --db AUDIT.db --map work/authoring/legacy-mapping.json

Import creates a new database only. It preserves the original artifacts, writes an ID mapping, and
marks the imported checks as historical. It is refused on a database that already holds the import.
Never run new-format data through the legacy ledger validator, and never point the legacy runtime at
a new-format database.

New databases use storage format 4, record contract 4, and packet/projection version 2.
The `route-review/1` feature records supplied-route review without relabeling historical
`item-audit/1` evidence. Native storage formats 2 and 3 are readable but must be explicitly upgraded
before writing:

    python "<skill-root>/scripts/paper_audit.py" migrate AUDIT.db --backup work/backups/pre-controller.db

Migration preserves mathematical revisions and historical packet bytes, and moves historical
application fields to their canonical extensions. It does not recheck a proof or infer an exact
target from an old synopsis. Refresh exact target specifications and source boundaries as required
before seeking new audit credit.

Existing proof-check audits may already contain overview records through `sql-superset/1` and
`overview-bridge/1`. Preserve those records, identities, selection, comparisons and detailed audit
history when resuming that audit. Their presence creates no proof credit or exhaustive inventory.
Native overview stores marked `archify-paper-database-1` are not proof-check audit databases.

The optional `work-context-extension/1` feature activates only after the first successful
version-2 work extension. Merely creating or migrating a database does not activate it.
Every tool opening an extended database, including Proof Graphify, needs a compatible core.
Older cores refuse unknown required features. Original packets and responses remain immutable;
the feature does not migrate storage format 4 or grant additional mathematical credit.

The optional `audit-scope-binding/1` feature activates when full-audit packets or checks first
capture the effective audit scope. Older cores then refuse the database. Earlier full global
checks that did not capture this scope require reexamination and explicit successors; their
evidence remains unchanged, and unaffected local checks remain available. This is a renewal
requirement, not a mathematical refutation or a storage-format migration.
