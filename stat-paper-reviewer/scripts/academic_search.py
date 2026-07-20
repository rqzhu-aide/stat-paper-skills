#!/usr/bin/env python3
# Adapted from https://github.com/wp-a/nature-academic-search (MIT License).
# See ../LICENSE for the retained upstream notice.
# /// script
# requires-python = ">=3.10"
# ///
"""Fallback literature discovery for stat-paper-reviewer using OpenAlex.

This self-contained script uses only the Python standard library. It supports
literature discovery when no scholarly search integration is available.

Source: OpenAlex (https://openalex.org). The API requires a free API key.
OpenAlex indexes records deposited by sources including Crossref, PubMed, and
arXiv. Use its results for discovery and bibliographic triage. Verify decisive
publication metadata, status, and content against persistent or publisher
records before making a strong novelty judgment.

Usage:
    # Replace `python3` with any available Python 3.10+ launcher.
    # By topic
    python3 academic_search.py "orthogonal score cross-fitting" [--limit 10] [--year-from 2020] [--sort cited_by_count|relevance_score|publication_date]
    # By author (name resolution is heuristic; verify the selected identity)
    python3 academic_search.py --author "Researcher Name"
    # By author + topic within that author's works
    python3 academic_search.py "semiparametric efficiency" --author "Researcher Name" --sort publication_date
    # By author constrained to an institution
    python3 academic_search.py --author "Researcher Name" --affiliation "Institution Name"
    # List same-name author records, then pick the right institution / ID
    python3 academic_search.py --author "Researcher Name" --list-authors
    # By ORCID (preferred when names are ambiguous)
    python3 academic_search.py --orcid ORCID_ID
    # By exact author ID (skip name resolution)
    python3 academic_search.py --author-id OPENALEX_AUTHOR_ID

Pass --api-key or set OPENALEX_API_KEY. Queries and filters are sent to
OpenAlex over HTTPS. Do not submit confidential manuscript text or personal
identifiers that are unnecessary for the search.

Output: JSON records with publication metadata, status fields, and abstract text.
Per-source failures (HTTP 429 rate-limit, timeouts, network errors) are reported
on stderr and exit non-zero, so a caller can treat this source independently and
fall back to another tool.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error


OPENALEX_API = "https://api.openalex.org/works"
AUTHORS_API = "https://api.openalex.org/authors"
API_KEY: str | None = None


def _add_api_key(params: dict) -> dict:
    """Add the required OpenAlex API key without mutating the caller's dict."""
    if not API_KEY:
        raise RuntimeError("OpenAlex API key is required")
    params = dict(params)
    params["api_key"] = API_KEY
    return params


def _institution(author: dict) -> str:
    insts = author.get("last_known_institutions") or []
    if isinstance(insts, list) and insts:
        return insts[0].get("display_name", "") or ""
    # Fall back to the most recent listed affiliation if no last-known institution.
    for aff in (author.get("affiliations") or []):
        n = (aff.get("institution") or {}).get("display_name")
        if n:
            return n
    return ""


def _aff_match(author: dict, affiliation: str) -> bool:
    """True if `affiliation` matches the author's PRIMARY (last-known) institution.

    Match only the last-known institution rather than every historical
    affiliation. This reduces false matches from namesakes with an old or
    incidental connection to the requested institution.
    """
    aff = affiliation.lower()
    names = [inst.get("display_name", "") for inst in (author.get("last_known_institutions") or [])]
    if not names:
        names = [_institution(author)]  # fall back to most recent listed affiliation
    return any(aff in (n or "").lower() for n in names)


def _candidate_summary(results: list[dict]) -> list[dict]:
    """Return distinct records without merging identities that look similar."""
    candidates = []
    for author in results:
        candidates.append({
            "name": author.get("display_name", ""),
            "institution": _institution(author),
            "works_count": author.get("works_count") or 0,
            "id": (author.get("id") or "").rsplit("/", 1)[-1],
            "orcid": author.get("orcid") or "",
        })
    return sorted(candidates, key=lambda candidate: -candidate["works_count"])


def fetch_author_candidates(name: str, per_page: int = 50) -> list[dict]:
    params = _add_api_key({"search": name, "per_page": min(per_page, 100)})
    url = f"{AUTHORS_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data.get("results", [])


def resolve_author(name: str, affiliation: str | None = None) -> dict | None:
    """Heuristically resolve a name to one OpenAlex author record.

    Names and institutions do not uniquely identify a person, so this function
    never merges records. It selects one candidate and returns all candidates for
    inspection. Use an exact OpenAlex ID or ORCID for a decisive author search.
    """
    results = fetch_author_candidates(name)
    if not results:
        return None

    candidates = _candidate_summary(results)
    pool = results
    if affiliation:
        pool = [a for a in results if _aff_match(a, affiliation)]
        if not pool:
            return {"ids": [], "display_name": name, "institution": "",
                    "works_count": 0, "candidates": candidates,
                    "no_affiliation_match": affiliation}

    # Prefer candidates that have a known institution, then the most prolific.
    pool = sorted(pool, key=lambda a: (_institution(a) == "", -(a.get("works_count") or 0)))
    best = pool[0]
    best_inst = _institution(best)

    return {
        "ids": [(best.get("id") or "").rsplit("/", 1)[-1]],
        "display_name": best.get("display_name", ""),
        "institution": best_inst,
        "works_count": best.get("works_count") or 0,
        "candidates": candidates,
    }


def resolve_by_orcid(orcid: str) -> dict | None:
    """Resolve an ORCID (bare 0000-... or full URL) to its OpenAlex author ID(s)."""
    oid = orcid.strip().rsplit("/", 1)[-1]
    # 0000-0000-0000-0000 is a checksum-valid but unassigned placeholder some
    # records carry; reject it so it can't resolve to whoever holds that junk tag.
    if set(oid) <= {"0", "-"}:
        return None
    params = _add_api_key({"filter": f"orcid:{oid}"})
    url = f"{AUTHORS_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    results = data.get("results", [])
    # Defensive: only keep records that actually carry the requested ORCID, so a
    # server-side filter miss can't resolve to an unrelated author. OpenAlex
    # stores orcid as a full URL, e.g. https://orcid.org/0000-....
    results = [a for a in results if (a.get("orcid") or "").rstrip("/").endswith(oid)]
    if not results:
        return None
    best = results[0]
    return {
        "ids": [(best.get("id") or "").rsplit("/", 1)[-1]],
        "display_name": best.get("display_name", ""),
        "institution": _institution(best),
        "works_count": best.get("works_count") or 0,
        "candidates": _candidate_summary(results),
    }


def search(query: str | None = None, limit: int = 10, year_from: int | None = None,
           sort: str = "relevance_score", author_id: str | None = None,
           relevance_floor: float = 0.0) -> list[dict]:
    if not 0.0 <= relevance_floor <= 1.0:
        raise ValueError("relevance_floor must be between 0 and 1")
    # A text query is ranked by relevance. Asking OpenAlex to sort that query by
    # cited_by_count / publication_date *server-side* discards relevance entirely
    # and surfaces off-topic mega-cited (or merely newest) papers that only loosely
    # match. So when a query and a non-relevance sort are combined, fetch a larger
    # relevance-ranked candidate pool and re-sort it locally (see end of function),
    # keeping only the topically relevant top results. Without a query (e.g. author
    # browse) there is no relevance to preserve, so sort server-side as before.
    rerank = bool(query) and sort != "relevance_score"
    per_page = min(max(limit * 5, limit), 100) if rerank else min(limit, 50)

    params = _add_api_key({"per_page": per_page})
    if query:
        params["search"] = query
    if not rerank:
        if sort != "relevance_score":
            params["sort"] = sort + ":desc"
        elif not query:
            # Author-only browse: relevance is meaningless, default to most-cited.
            params["sort"] = "cited_by_count:desc"

    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if author_id:
        # Accept a bare ID, a full URL, or an OR-list; normalise each segment.
        ids = "|".join(p.rsplit("/", 1)[-1] for p in author_id.split("|"))
        filters.append(f"author.id:{ids}")
    if filters:
        params["filter"] = ",".join(filters)

    url = f"{OPENALEX_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    results = []
    for work in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in work.get("authorships", [])
        ]
        doi = work.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]

        abstract_index = work.get("abstract_inverted_index")
        abstract = ""
        if abstract_index:
            # Reconstruct abstract from inverted index
            word_positions = []
            for word, positions in abstract_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join(w for _, w in word_positions)

        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        results.append({
            "title": work.get("title", ""),
            "doi": doi,
            "authors": authors,
            "year": work.get("publication_year"),
            "publication_date": work.get("publication_date", ""),
            "cited_by_count": work.get("cited_by_count", 0),
            "venue": source.get("display_name", ""),
            "source_type": source.get("type", ""),
            "work_type": work.get("type", ""),
            "version": primary_location.get("version", ""),
            "is_retracted": bool(work.get("is_retracted", False)),
            "is_oa": (work.get("open_access") or {}).get("is_oa"),
            "abstract": abstract,
            "openalex_id": work.get("id", ""),
            # Present only for query searches (server orders by relevance then).
            "relevance_score": work.get("relevance_score"),
        })

    if rerank:
        # An optional relative relevance floor can suppress weak matches before
        # local re-ranking. It is disabled by default because a fixed threshold
        # does not transfer reliably across topics, fields, or query lengths.
        scores = [r["relevance_score"] for r in results if r.get("relevance_score")]
        if scores and relevance_floor > 0:
            cutoff = relevance_floor * max(scores)
            results = [r for r in results if (r.get("relevance_score") or 0) >= cutoff]
        sort_keys = {
            "cited_by_count": lambda r: r.get("cited_by_count") or 0,
            "publication_date": lambda r: r.get("publication_date") or "",
        }
        results.sort(key=sort_keys[sort], reverse=True)

    # We may have over-fetched a candidate pool; return only the requested number.
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="Fallback literature discovery via OpenAlex")
    parser.add_argument("query", nargs="?", default=None,
                        help="Search query (optional when --author/--author-id/--orcid is given)")
    parser.add_argument("--author", default=None,
                        help="Filter by author name (resolved to OpenAlex author IDs)")
    parser.add_argument("--affiliation", default=None,
                        help="Constrain --author to an institution (case-insensitive substring); "
                             "disambiguates colliding names")
    parser.add_argument("--orcid", default=None,
                        help="Resolve author by ORCID (unambiguous); takes precedence over --author")
    parser.add_argument("--list-authors", action="store_true",
                        help="List same-name author records for --author and exit")
    parser.add_argument("--author-id", default=None,
                        help="Filter by exact OpenAlex author ID(s); OR-join multiple IDs with '|'")
    parser.add_argument("--limit", type=int, default=10, help="Number of results (max 50)")
    parser.add_argument("--year-from", type=int, default=None, help="Filter papers from this year")
    parser.add_argument("--sort", default="relevance_score",
                        choices=["relevance_score", "cited_by_count", "publication_date"],
                        help="Sort order. With a query, cited_by_count/publication_date "
                             "re-rank within the relevance-matched pool (not the whole DB)")
    parser.add_argument("--relevance-floor", type=float, default=0.0,
                        help="Optional minimum relevance as a fraction of the top score "
                             "before local re-ranking; 0 disables filtering (default)")
    parser.add_argument("--api-key", default=None,
                        help="OpenAlex API key (falls back to OPENALEX_API_KEY env)")
    parser.add_argument("--compact", action="store_true", help="Compact output (one line per paper)")
    args = parser.parse_args()

    global API_KEY
    API_KEY = args.api_key or os.environ.get("OPENALEX_API_KEY") or None
    if not API_KEY:
        parser.error("OpenAlex requires an API key; pass --api-key or set OPENALEX_API_KEY")

    if not 1 <= args.limit <= 50:
        parser.error("--limit must be between 1 and 50")
    if not 0.0 <= args.relevance_floor <= 1.0:
        parser.error("--relevance-floor must be between 0 and 1")

    if (not args.query and not args.author and not args.author_id
            and not args.orcid and not args.list_authors):
        parser.error("provide a search query, or use --author / --author-id / --orcid")

    def _fmt_candidate(candidate: dict) -> str:
        return (f"  {(candidate['institution'] or 'unknown institution'):<42} | "
                f"{candidate['works_count']:>5} works | {candidate['id']}")

    # --list-authors: dump distinct same-name records and exit.
    if args.list_authors:
        if not args.author:
            parser.error("--list-authors requires --author")
        try:
            cands = _candidate_summary(fetch_author_candidates(args.author))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            print(f"ERROR: author lookup failed: {e}", file=sys.stderr)
            return 1
        if not cands:
            print(f"ERROR: no author found in OpenAlex: {args.author}", file=sys.stderr)
            return 1
        print(f"Candidate author records for \"{args.author}\" (by works count, desc):", file=sys.stderr)
        for c in cands[:15]:
            print(_fmt_candidate(c))
        print("-> use --affiliation \"keyword\" or --author-id <ID> to pin the right person", file=sys.stderr)
        return 0

    author_id = args.author_id
    matched = None
    if not author_id and (args.orcid or args.author):
        try:
            matched = (resolve_by_orcid(args.orcid) if args.orcid
                       else resolve_author(args.author, args.affiliation))
        except urllib.error.HTTPError as e:
            print(f"ERROR: author lookup returned HTTP {e.code}: {e.reason}", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            print(f"ERROR: author lookup failed: {e}", file=sys.stderr)
            return 1
        if not matched or not matched.get("ids"):
            if matched and matched.get("no_affiliation_match"):
                print(f"ERROR: author \"{args.author}\" has no record at institution "
                      f"\"{matched['no_affiliation_match']}\". Options (by works count):", file=sys.stderr)
                for c in (matched.get("candidates") or [])[:10]:
                    print(_fmt_candidate(c), file=sys.stderr)
            elif args.orcid:
                print(f"ERROR: no author found in OpenAlex for ORCID: {args.orcid}", file=sys.stderr)
            else:
                print(f"ERROR: no author found in OpenAlex: {args.author}", file=sys.stderr)
            return 1
        author_id = matched["ids"][0]
        inst = matched["institution"] or "unknown institution"
        print(f"Matched author: {matched['display_name']} | {inst} | "
              f"selected one record, ~{matched['works_count']} works | "
              f"{author_id}", file=sys.stderr)
        if args.author and not args.orcid:
            print("WARNING: name-based author resolution is heuristic; verify the identity "
                  "or use --orcid / --author-id for decisive searches", file=sys.stderr)
        # Warn on silent collisions: same name, other institutions present, and the
        # caller didn't pin it down with --affiliation/--orcid.
        if args.author and not args.affiliation and not args.orcid:
            others = [c for c in (matched.get("candidates") or [])
                      if c["institution"] and c["institution"] != matched["institution"]]
            if others:
                tops = "; ".join(f"{c['institution']} ({c['works_count']} works)" for c in others[:3])
                print(f"WARNING: same-name authors at other institutions exist; "
                      f"if this is the wrong one add --affiliation or --orcid: {tops}",
                      file=sys.stderr)

    if args.query and args.sort != "relevance_score":
        floor_note = (f" with relative relevance floor {args.relevance_floor:g}"
                      if args.relevance_floor > 0 else " with no relevance threshold")
        print(f"INFO: recalled a relevance-ranked pool, then re-ranked by {args.sort}{floor_note} "
              f"and kept the top {args.limit}", file=sys.stderr)

    try:
        results = search(args.query, args.limit, args.year_from, args.sort, author_id,
                         args.relevance_floor)
    except urllib.error.HTTPError as e:
        hint = " (429 = rate-limited; retry later or lower --limit)" if e.code == 429 else ""
        print(f"ERROR: OpenAlex returned HTTP {e.code}: {e.reason}{hint}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"ERROR: network request failed (check connectivity): {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("ERROR: OpenAlex returned a non-JSON response (service may be down; retry)", file=sys.stderr)
        return 1

    if args.compact:
        for r in results:
            authors_str = ", ".join(r["authors"][:3])
            if len(r["authors"]) > 3:
                authors_str += " et al."
            status = f"{r['work_type']}/{r['source_type']}"
            if r["is_retracted"]:
                status += "/RETRACTED"
            print(f"[{r['year']}] {r['title']} | {authors_str} | {r['venue']} | {status} | DOI:{r['doi']} | Cited:{r['cited_by_count']}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
