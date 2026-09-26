# Portable and Fail-Closed Review Runs

## Purpose

Use this protocol to prevent an interrupted, partially delegated, or partially
read manuscript review from being presented as a completed review. It governs
execution evidence only. It does not change the scientific review criteria.
Hash checks detect accidental or unacknowledged changes to recorded inputs and
artifacts. Because the manifest is not signed, the bundle is not an adversarially
tamper-proof audit log.

Use a durable run bundle for:

- every delegated review;
- every review whose result must be resumed, moved, or independently checked;
- every multi-file manuscript packet, including a main PDF with supplements;
- any review for which the user requests an execution audit trail.

A single-manuscript interactive review, including a full review of one PDF,
proceeds without a run bundle. In that case still apply section 3's source-map
discipline directly before substantive reading: verify page mapping, visually
check claim-bearing equations, symbols, tables, and figures against rendered
pages, and state any extraction limits in the report's assessment boundary.
Classify any execution failure with the categories in section 2 and report it
as an execution limitation, never as manuscript evidence.

## 1. Resolve helpers independently of the working directory

Derive `<skill-root>` from the absolute location of the loaded `SKILL.md`. Never
assume that the current working directory is the skill directory. Invoke helpers
by their resolved absolute paths:

```text
python "<skill-root>/scripts/review_run.py" --help
python "<skill-root>/scripts/academic_search.py" --help
```

Use any available Python 3.10 or later launcher. Do not encode an operating
system username, home directory, drive letter, shell syntax, or installation
layout in a review instruction or run artifact.

## 2. Preflight before substantive reading

Choose a new empty review-bundle directory and inventory every supplied file by
role. Use exactly one `--main`; repeat `--supplement` and `--companion` as needed.

First run:

```text
python "<skill-root>/scripts/review_run.py" doctor --root "<review-bundle>" --main "<main-file>" --supplement "<supplement-file>"
```

The preflight checks that the helper can start, every input can be read and
hashed, and the chosen output location can be written. Classify any failure as
one of:

- `execution-start`: the helper process did not start;
- `input-read`: an input is absent or unreadable;
- `output-write`: the bundle location cannot be written;
- `extraction`: readable PDF bytes could not be converted into a reliable text
  and page map;
- `external-source`: a required literature source or network operation failed;
- `integrity`: a copied input, stage artifact, manifest, or report fails its hash
  or lifecycle check.

Retry an execution-start failure at most once when a transient cause is
plausible. Do not run operating-system repair commands, alter global security
settings, rewrite access-control lists, or silently switch to an informal review.
If the retry fails, stop with `NONFINAL`, the failed operation, and the failure
category. Do not imply that manuscript reading or review stages completed.

After a passing preflight, initialize the run:

```text
python "<skill-root>/scripts/review_run.py" init --root "<review-bundle>" --profile full --main "<main-file>" --supplement "<supplement-file>"
```

Add `--delegated` when any stage will be assigned to another worker. The full
profile requires a literature-stage outcome by default. For a focused profile,
add `--require-stage literature` when an actual novelty, priority, related-work,
or citation-support judgment is required.

Initialization copies, hashes, and locks the supplied files into `inputs/`. It
also records the skill name and version and copies the exact `SKILL.md`,
reviewer references, and helper scripts into `protocol/`, with a combined
protocol digest in the manifest. This snapshot identifies the instructions that
governed the run even when the installed skill changes later. The manifest
stores only forward-slash, bundle-relative active paths, so the complete bundle
can be moved across folders and operating systems. Integrity checks cover the
input and protocol snapshots and reject symlinks, junctions, and other
redirected internal path components; bundle evidence must remain physically
self-contained.

## 3. Build a first-class source map

Do not begin the first-reader pass until a durable `source_map` artifact exists.
For every main, supplement, and companion file, record:

- its role, displayed title, file type, and whether it is the canonical copy;
- page count or source-file coverage when available;
- the relationship between physical PDF pages, printed page labels, sections,
  and extracted-text locations;
- extraction method and any OCR or missing-symbol limitations;
- visual verification of equations, tables, figures, and pages that determine a
  finding;
- whether a main PDF already contains an appended supplement;
- whether an appended and standalone supplement are byte-identical,
  content-equivalent, different versions, or not assessable.

Do not count duplicated supplements twice. If versions differ, retain both as
separate sources and identify which supports each finding. A readable PDF is not
yet review-ready merely because text extraction returned some text. Mark the
source map `limited` when extraction or page alignment is incomplete but a
bounded review remains supportable. Mark it `not_assessable` and stop when the
manuscript content cannot be read reliably enough to ground findings.

Register the source map from any working directory:

```text
python "<skill-root>/scripts/review_run.py" stage --root "<review-bundle>" --name source_map --artifact "<source-map-file>"
```

## 4. Record durable stage completion

The required stages depend on the initialized profile:

| Stage | Durable evidence |
|---|---|
| `intake` | Copied, hash-locked source files; completed by `init` |
| `source_map` | File roles, canonical copies, extraction and page mapping |
| `first_reader` | Manuscript-order trace of consequential reader events |
| `fact_base` | Provenance and support-status ledger |
| `claim_chain` | Problem-to-boundary alignment assessment |
| `literature` | Search boundary, verified records, and comparison evidence |
| `patterned_prose` | Private candidate adjudication and bounded classification |
| `synthesis` | Prioritized diagnosis and finding set |
| `qa` | Grounding, calibration, mathematical-paraphrase, and output checks |

Each completed stage must have at least one readable artifact. Register it with:

```text
python "<skill-root>/scripts/review_run.py" stage --root "<review-bundle>" --name first_reader --artifact "<first-reader-record>"
```

Use `--outcome limited` or `--outcome not_assessable` with a precise `--note`
when a stage was closed under a real evidence ceiling. Do not mark an interrupted
or merely attempted stage complete.

For a full review, close `literature` as `complete` only when the required
external comparison was actually performed. Use `limited` when material
comparators or full text could not be checked, and `not_assessable` when no
scholarly search route was available or external search was explicitly excluded.
In the latter case, the report may assess positioning clarity but must leave
substantive novelty and its score unassessed. Close `patterned_prose` with a
brief negative-screen artifact when no recurrent candidate survives
reconstruction; load and apply the detailed prose-alarm protocol only when a
candidate survives or the user requests that assessment.

For delegated runs, initialize with `--delegated` and identify each stage
producer with `--producer`. A worker message, summary, or claimed completion is
not durable stage evidence. Save the returned analysis as a file, verify that it
answers the assigned stage, and register that file. The parent reviewer owns the
shared fact base, resolves conflicts, completes synthesis, and runs QA.

Run `status` after every delegated return and before synthesis:

```text
python "<skill-root>/scripts/review_run.py" status --root "<review-bundle>"
```

The helper verifies current hashes and reports missing or limited stages. If a
source or artifact changes after registration, treat the stage as stale and
rerun or explicitly close it under the resulting limitation.

Replacing a registered upstream stage invalidates its recorded downstream
stages, including synthesis and QA. Previously copied artifact files may remain
for audit history, but they are not current stage evidence until the affected
stages are rerun and registered again.

## 5. Finalize or fail closed

Finalize only after the report has passed reviewer QA:

```text
python "<skill-root>/scripts/review_run.py" finalize --root "<review-bundle>" --report "<review-report>"
```

Finalization fails when a required stage is missing, an input, protocol, or
artifact hash changed, or a limitation was not explicitly acknowledged. When
required stages are legitimately limited or not assessable, state those exact
limits in the report and rerun finalization with `--acknowledge-limits`.

Do not deliver a full-review verdict unless finalization succeeds and a final
`status` check reports `finalized` with integrity `ok`. If work stops earlier:

- use `PARTIAL` only for a user-requested best-effort result that identifies the
  completed stages, missing stages, and conclusions that must not yet be relied
  on;
- use `NONFINAL` when execution, source mapping, integrity, or required evidence
  prevents a supportable review;
- never relabel an ad hoc analysis as completion of a missing reviewer stage.

A bounded review of a deliberately supplied excerpt can still be final within
its stated scope. That evidentiary boundary is different from an interrupted
workflow.
