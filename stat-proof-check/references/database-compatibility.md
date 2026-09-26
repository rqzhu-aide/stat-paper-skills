# Database compatibility and migration


    python "<skill-root>/scripts/paper_audit.py" import-legacy <audit-folder> --db NEW.db --map MAPPING.json

Import creates a new database only. It preserves the original artifacts, writes an ID mapping, and
marks the imported checks as historical. It is refused on a database that already holds the import.
Never run new-format data through the legacy ledger validator, and never point the legacy runtime at
a new-format database.

New databases use storage format 4, record contract 4, and packet/projection version 2. The
`sql-superset/1` feature keeps overview records and optional audit extensions in one authoritative
database. The `route-review/1` feature records supplied-route review without relabeling historical
`item-audit/1` evidence. Native storage formats 2 and 3 are readable but must be explicitly upgraded
before writing:

    python "<skill-root>/scripts/paper_audit.py" migrate AUDIT.db --backup pre-controller.db

Migration preserves mathematical revisions and historical packet bytes, and moves historical
application fields to their canonical extensions. It does not recheck a proof or infer an exact
target from an old synopsis. Refresh exact target specifications and source boundaries as required
before seeking new audit credit.
An archify overview database instead uses `format: archify-paper-database-1` and `schema_version: 2` or `3`;
those identifiers are unrelated to native storage format 2. It is reported as exit 4 `INCOMPATIBLE`
until explicitly upgraded with `migrate-overview DB --backup BACKUP`, which preserves item, use, and
anchor identity, including regimes, issue notes, aliases, label/page locators, intermediate rows, and
premise groups. Review history imports under the overview's own applicability rule: the newest
observation matching each target's current content digest becomes the live record with its legacy
timestamp, while superseded or stale observations stay in the archived legacy export and the migration
report discloses how many were archived. The recorded scope and explicit exclusions carry onto the
paper record, and each unresolved inventory entry becomes an open source issue, so coverage limits stay
queryable. A migrated database requires
the `overview-bridge/1` feature; cores without it refuse the database cleanly. `attach DB --report report.html` registers a
proofcheck report on a compatible overview database without creating a second master.


The optional `work-context-extension/1` feature activates only after the first successful
version-2 work extension. Merely creating or migrating a database does not activate it.
Every tool opening an extended database, including Proof Graphify, needs a compatible core.
Older cores refuse unknown required features. Original packets and responses remain immutable;
the feature does not migrate storage format 4 or grant additional mathematical credit.
