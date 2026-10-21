# Academic Search Operations

## Contents

- [Purpose](#purpose)
- [1. Define the search boundary](#1-define-the-search-boundary)
- [2. Prefer structured scholarly evidence](#2-prefer-structured-scholarly-evidence)
- [3. Apply evidence ceilings](#3-apply-evidence-ceilings)
- [4. Verify the manuscript's own citations first](#4-verify-the-manuscripts-own-citations-first)
- [5. Search for uncited close work](#5-search-for-uncited-close-work)
- [6. Use the bundled fallback when needed](#6-use-the-bundled-fallback-when-needed)
- [7. Compare and stop responsibly](#7-compare-and-stop-responsibly)

## Purpose

Use this workflow to verify claim-bearing references and assess whether a manuscript's novelty claim survives comparison with real publications. Perform it after the reading required for the assessment scope so external knowledge does not overwrite the original reader observations.

For a precise citation-support question, verify the named record and inspect the content needed to resolve the attached claim. Section 5 and the novelty comparison and search-saturation requirements in section 7 apply when novelty, priority, originality, or broader related-work coverage is assessed, or when the requested citation judgment requires that comparison. A precise support check stops when the claim is resolved or a stated evidence ceiling is reached.

Treat literature search as evidence collection, not as a substitute for statistical review. A search result establishes neither novelty nor correctness by itself.

For a focused practical-usefulness comparison, verify materially relevant existing alternatives and the content needed to assess the claimed gain. Search by the scientific question or desired conclusion as well as the proposed technique, including simpler procedures and different method families. Stop at a supported comparison or a stated evidence ceiling; do not expand to a full novelty assessment unless the requested judgment requires it. Apply the same evidence ceilings and comparator verification/discovery labels.

## 1. Define the search boundary

Record:

- the exact novelty, priority, or citation-support claim being assessed;
- the manuscript sections and bibliography files available;
- the publication types and dates that matter;
- the sources searched, search date, and access limits;
- whether full text, abstracts, or metadata alone were inspected.

Check central claim-bearing references by default. Audit the entire bibliography only when the user asks or when repeated reference problems justify expansion.

## 2. Prefer structured scholarly evidence

Use the best available sources for the domain:

| Need | Preferred evidence |
|---|---|
| DOI and journal metadata | Crossref record, publisher page, or DOI resolver |
| Biomedical publication | PubMed or PMC record, then publisher or full text |
| Statistics, mathematics, ML, or CS preprint | arXiv record and version history, then conference or journal record when one exists |
| Broad discovery and citation neighborhood | OpenAlex or Semantic Scholar, followed by primary-record verification |
| Conference publication | Official proceedings, DOI record, or conference archive |
| Regional, non-English, or access-restricted literature | Available official database or a clearly labeled manual-check item |

Prefer primary and structured records. Use general web search to locate official records or full text, not as the sole basis for a strong bibliographic or novelty conclusion. Do not rely on search snippets.

## 3. Apply evidence ceilings

Match every conclusion to the strongest material actually inspected:

- **Metadata:** verifies bibliographic existence, identifiers, venue, and recorded dates only.
- **Abstract:** identifies possible relevance and coarse scope, but normally cannot establish fine distinctions in assumptions, theorem scope, algorithm details, or empirical design.
- **Decisive content:** supports a bounded substantive comparison only after the relevant method, theorem, assumptions, experiment, or result has been inspected.
- **Documented search neighborhood:** supports a bounded novelty judgment only after the applicable query families and close citation neighborhood have been examined.

If only metadata or abstracts are available for a decisive distinction, mark that distinction provisional or unassessed. Failure to find close work is negative search evidence, not proof of firstness.

## 4. Verify the manuscript's own citations first

For each central claim-bearing citation:

1. Extract the cited title, authors, year, venue, and identifier.
2. Resolve the DOI, PMID, arXiv ID, or exact title plus first author.
3. Compare the retrieved metadata with the manuscript entry.
4. Classify the record as `verified`, `mismatch`, `not_found`, `suspicious`, or `manual_needed`.
5. Inspect the abstract and, when material, the method, theorem, assumptions, experiment, or result cited.
6. Separately judge whether the publication supports the attached manuscript statement.

Keep three questions distinct:

- Does the publication exist with the cited metadata?
- Does it contain evidence relevant to the attached statement?
- How closely does it overlap with the manuscript's claimed contribution?

## 5. Search for uncited close work

Decompose each novelty claim into the target, statistical regime, construction, assumptions, guarantee, computational property, and application. Build several compact searches rather than one broad query:

1. target plus statistical regime;
2. construction plus established synonyms;
3. guarantee plus key assumptions;
4. application or data type plus methodological objective;
5. exact technical phrases when they are genuinely diagnostic.

Search terminology from both the manuscript and the closest verified references. When available, inspect related, cited, and citing publications. Search multiple source families when the claim crosses fields or publication types.

When practical usefulness is claimed, include methods that already answer the same scientific or decision question, even if their constructions and terminology differ. Reuse decisive comparisons already inspected rather than starting a separate search solely for practical value.

Deduplicate by DOI first, then by PMID or arXiv ID, then by normalized title, year, and first author. Treat preprints and later peer-reviewed versions as linked versions, not automatically as separate intellectual contributions.

## 6. Use the bundled fallback when needed

If no scholarly search interface is available, resolve the bundled standard-library script from the directory containing the loaded `SKILL.md`. Do not assume the caller's current working directory is the skill directory. Quote the resolved path when it contains spaces.

Use any available Python 3.10 or later launcher. Depending on the environment, this may be `python`, `python3`, `py -3`, or a bundled interpreter path. In the examples below, `python` denotes that launcher.

```bash
python "<skill-root>/scripts/academic_search.py" "target method statistical regime" --limit 20
python "<skill-root>/scripts/academic_search.py" "guarantee key assumption" --limit 20 --sort relevance_score
python "<skill-root>/scripts/academic_search.py" "method application" --year-from 2020 --limit 20
```

Set `OPENALEX_API_KEY` in the environment before running these commands so the key does not enter shell history. If environment configuration is unavailable, use `--api-key`. Use `python "<skill-root>/scripts/academic_search.py" --help` for all options. The script queries OpenAlex and returns title, DOI, authors, date, venue, work and source types, version when supplied, retraction and open-access flags, citations, abstract text when available, and OpenAlex ID.

The request sends the API key, search terms, and any author, affiliation, or ORCID filters to OpenAlex over HTTPS. Do not submit confidential manuscript prose or unnecessary personal identifiers.

Name-based author resolution is heuristic and selects one record without merging similar identities. Inspect `--list-authors`, then use an exact OpenAlex author ID or ORCID for any decisive author-specific search.

When re-ranking a text query by citation count or publication date, the script first retrieves a relevance-ranked candidate pool. It applies no relevance threshold by default. Use `--relevance-floor` only when a documented, query-specific reason justifies filtering, and record the chosen value because an aggressive threshold can hide close work.

The fallback is for discovery. For every candidate that changes the novelty judgment, verify the DOI, publisher, PubMed, arXiv, or official proceedings record and inspect enough content to support the comparison. If external verification or search was unavailable or excluded, apply the [offline comparison boundary](novelty-verification.md#4-report-a-bounded-conclusion). If completed external comparison was materially limited but supports a bounded judgment, label that conclusion provisional.

## 7. Compare and stop responsibly

For an actual novelty or related-work comparison, build the matrix specified in [novelty-verification.md](novelty-verification.md). Separate peer-reviewed publications, conference papers, and preprints. Record relevant version chronology when priority matters.

When priority matters, compare the earliest public version that contains the overlapping substance, not merely the later journal or conference date. State the manuscript reference date used for comparison and classify chronology as earlier, concurrent, later, or indeterminate when the record does not resolve it.

For novelty, priority, originality, or broader related-work coverage, stop only after the applicable decomposed query families have been searched and two materially different query refinements or citation-neighborhood passes add no candidate that changes the comparison. Do not claim an exhaustive search unless database coverage, query breadth, and screening justify it. A precise citation-support check follows the bounded stopping rule in Purpose.

For decisive publications, report a DOI, PMID, arXiv ID, or direct official link. State which publications were already cited, what was verified from full text, and what remains based only on metadata or abstract evidence.
