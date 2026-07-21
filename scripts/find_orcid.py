#!/usr/bin/env python3
"""Search the ORCID public API for a researcher by name (and optional affiliation).

Usage:
    python -X utf8 scripts/find_orcid.py "Vagisha Sharma" --affiliation "University of Washington"

Prints candidate ORCID iDs with names and current employer/affiliation so you
can confirm the right person. No API key required (public API).
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

ORCID_SEARCH = "https://pub.orcid.org/v3.0/expanded-search/"


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def search(name, affiliation=None, rows=20):
    # Build a Lucene query for the ORCID search API.
    parts = [f'family-name:"{name.split()[-1]}"']
    if len(name.split()) > 1:
        parts.append(f'given-names:"{name.split()[0]}"')
    if affiliation:
        parts.append(f'affiliation-org-name:"{affiliation}"')
    q = " AND ".join(parts)
    url = ORCID_SEARCH + "?" + urllib.parse.urlencode({"q": q, "rows": rows})
    return _get(url)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name", help='Full name, e.g. "Vagisha Sharma"')
    ap.add_argument("--affiliation", default=None, help="Institution name")
    ap.add_argument("--rows", type=int, default=20)
    args = ap.parse_args()

    data = search(args.name, args.affiliation, args.rows)
    results = data.get("expanded-result") or []
    if not results:
        print("No results. Try without --affiliation or check the spelling.")
        sys.exit(1)

    for r in results:
        oid = r.get("orcid-id", "?")
        given = r.get("given-names", "") or ""
        family = r.get("family-names", "") or ""
        orgs = r.get("institution-name") or []
        print(f"{oid}  {given} {family}")
        if orgs:
            print(f"    affiliations: {', '.join(orgs)}")
        print(f"    https://orcid.org/{oid}")
        print()


if __name__ == "__main__":
    main()
