# Academic Search Operations

## Purpose

Use this workflow to verify claim-bearing references and assess whether a manuscript's central novelty claim survives comparison with real publications. Perform it after the sequential first-reader pass so external knowledge does not overwrite the original reading record.

Treat literature search as evidence collection, not as a substitute for statistical review. A search result establishes neither novelty nor correctness by itself.

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

## 3. Verify the manuscript's own citations first

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

## 4. Search for uncited close work

Decompose each novelty claim into the target, statistical regime, construction, assumptions, guarantee, computational property, and application. Build several compact searches rather than one broad query:

1. target plus statistical regime;
2. construction plus established synonyms;
3. guarantee plus key assumptions;
4. application or data type plus methodological objective;
5. exact technical phrases when they are genuinely diagnostic.

Search terminology from both the manuscript and the closest verified references. When available, inspect related, cited, and citing publications. Search multiple source families when the claim crosses fields or publication types.

Deduplicate by DOI first, then by PMID or arXiv ID, then by normalized title, year, and first author. Treat preprints and later peer-reviewed versions as linked versions, not automatically as separate intellectual contributions.

## 5. Use the bundled fallback when needed

If no scholarly search interface is available, run the bundled standard-library script from this skill folder:

Use any available Python 3.10 or later launcher. Depending on the environment, this may be `python`, `python3`, `py -3`, or a bundled interpreter path. In the examples below, `python` denotes that launcher.

```bash
python scripts/academic_search.py "target method statistical regime" --limit 20
python scripts/academic_search.py "guarantee key assumption" --limit 20 --sort relevance_score
python scripts/academic_search.py "method application" --year-from 2020 --limit 20
```

Set `OPENALEX_API_KEY` in the environment before running these commands so the key does not enter shell history. If environment configuration is unavailable, use `--api-key`. Use `python scripts/academic_search.py --help` for all options. The script queries OpenAlex and returns title, DOI, authors, date, venue, work and source types, version when supplied, retraction and open-access flags, citations, abstract text when available, and OpenAlex ID.

The request sends the API key, search terms, and any author, affiliation, or ORCID filters to OpenAlex over HTTPS. Do not submit confidential manuscript prose or unnecessary personal identifiers.

Name-based author resolution is heuristic and selects one record without merging similar identities. Inspect `--list-authors`, then use an exact OpenAlex author ID or ORCID for any decisive author-specific search.

When re-ranking a text query by citation count or publication date, the script first retrieves a relevance-ranked candidate pool. It applies no relevance threshold by default. Use `--relevance-floor` only when a documented, query-specific reason justifies filtering, and record the chosen value because an aggressive threshold can hide close work.

The fallback is for discovery. For every candidate that changes the novelty judgment, verify the DOI, publisher, PubMed, arXiv, or official proceedings record and inspect enough content to support the comparison. If network access is unavailable, report that external verification was not performed and keep the novelty conclusion provisional.

## 6. Compare and stop responsibly

Build the comparison matrix specified in [novelty-verification.md](novelty-verification.md). Separate peer-reviewed publications, conference papers, and preprints. Record relevant version chronology when priority matters.

Stop when new queries repeatedly return the same close neighborhood and no new candidate changes the comparison. Do not claim an exhaustive search unless database coverage, query breadth, and screening justify it.

For decisive publications, report a DOI, PMID, arXiv ID, or direct official link. State which publications were already cited, what was verified from full text, and what remains based only on metadata or abstract evidence.
