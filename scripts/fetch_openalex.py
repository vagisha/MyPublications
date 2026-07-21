#!/usr/bin/env python3
"""Fetch all works for an author from OpenAlex (keyed by ORCID) and save them.

Pulls everything needed to build a publications page + citation-growth charts:
title, authors, venue, year, type, DOI/URL, total citations, and the
citations-received-per-year series (OpenAlex `counts_by_year`).

Outputs (into --out-dir, default `data/`):
  openalex_works_raw.json   full raw OpenAlex records (source of truth)
  publications.json         cleaned, trimmed records used by later steps
  publications.csv          flat CSV (one row per paper)

Usage:
  python -X utf8 scripts/fetch_openalex.py \
      --orcid 0000-0003-1922-439X --mailto vagisha@gmail.com

If OpenAlex is busy (HTTP 429/500/503) or times out, it pauses and retries
with exponential backoff, so you can safely re-run it.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"


def fetch_page(cursor, orcid, mailto, per_page=200, max_retries=8):
    params = {
        "filter": f"author.orcid:{orcid}",
        "per-page": per_page,
        "cursor": cursor,
    }
    if mailto:
        params["mailto"] = mailto  # OpenAlex "polite pool"
    url = API + "?" + urllib.parse.urlencode(params)

    delay = 2.0
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"MyPublications ({mailto})"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            busy = e.code in (429, 500, 502, 503, 504)
            if busy and attempt < max_retries:
                print(f"  OpenAlex busy (HTTP {e.code}); pausing {delay:.0f}s "
                      f"(attempt {attempt}/{max_retries})...", flush=True)
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries:
                print(f"  Network issue ({e}); pausing {delay:.0f}s "
                      f"(attempt {attempt}/{max_retries})...", flush=True)
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
    raise RuntimeError("Exhausted retries fetching OpenAlex")


def fetch_all(orcid, mailto):
    works, cursor, page = [], "*", 0
    while cursor:
        page += 1
        data = fetch_page(cursor, orcid, mailto)
        batch = data.get("results", [])
        works.extend(batch)
        cursor = data.get("meta", {}).get("next_cursor")
        total = data.get("meta", {}).get("count")
        print(f"  page {page}: +{len(batch)} works ({len(works)}/{total})", flush=True)
        if not batch:
            break
        time.sleep(0.2)  # be gentle
    return works


def _authors(work):
    out = []
    for a in work.get("authorships", []):
        name = (a.get("author") or {}).get("display_name")
        if name:
            out.append(name)
    return out


def _venue(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name")


def clean(work):
    counts = {c["year"]: c["cited_by_count"] for c in work.get("counts_by_year", [])}
    biblio = work.get("biblio") or {}
    oa = work.get("open_access") or {}
    return {
        "openalex_id": work.get("id"),
        "doi": (work.get("doi") or "").replace("https://doi.org/", "") or None,
        "title": work.get("display_name") or work.get("title"),
        "authors": _authors(work),
        "venue": _venue(work),
        "type": work.get("type"),
        "year": work.get("publication_year"),
        "publication_date": work.get("publication_date"),
        "cited_by_count": work.get("cited_by_count", 0),
        "counts_by_year": counts,  # {year: citations_received_that_year}
        "is_oa": oa.get("is_oa"),
        "oa_url": oa.get("oa_url"),
        "landing_page_url": (work.get("primary_location") or {}).get("landing_page_url"),
        "volume": biblio.get("volume"),
        "issue": biblio.get("issue"),
        "first_page": biblio.get("first_page"),
        "last_page": biblio.get("last_page"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orcid", required=True, help="e.g. 0000-0003-1922-439X")
    ap.add_argument("--mailto", default=None, help="email for OpenAlex polite pool")
    ap.add_argument("--out-dir", default="data")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    print(f"Fetching works for ORCID {args.orcid} from OpenAlex...")
    raw = fetch_all(args.orcid, args.mailto)
    print(f"Fetched {len(raw)} works total.")

    raw_path = os.path.join(args.out_dir, "openalex_works_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    cleaned = [clean(w) for w in raw]
    cleaned.sort(key=lambda w: (w["year"] or 0, w["cited_by_count"]), reverse=True)
    clean_path = os.path.join(args.out_dir, "publications.json")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(args.out_dir, "publications.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "title", "authors", "venue", "type",
                    "cited_by_count", "doi", "openalex_id"])
        for p in cleaned:
            w.writerow([p["year"], p["title"], "; ".join(p["authors"]),
                        p["venue"], p["type"], p["cited_by_count"],
                        p["doi"], p["openalex_id"]])

    total_cites = sum(p["cited_by_count"] for p in cleaned)
    print(f"\nSaved:\n  {raw_path}\n  {clean_path}\n  {csv_path}")
    print(f"\n{len(cleaned)} works, {total_cites} total citations.")


if __name__ == "__main__":
    main()
