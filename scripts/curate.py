#!/usr/bin/env python3
"""Apply persistent curation decisions to the fetched publications.

Reads the raw fetched list (`data/publications.json`) and the persistent
decisions (`data/curation.json`), then writes the filtered list used to build
the page. Because every decision lives in curation.json, re-running the whole
pipeline (fetch -> curate) reproduces the same result with no manual work.

Curation applied, in order:
  1. Drop any paper whose OpenAlex id is in `excluded_ids` (e.g. name collisions).
  2. Drop any id in `force_drop_ids`.
  3. Preprint de-duplication (policy `drop_preprint_if_published_exists`):
     drop a preprint if a published (non-preprint) paper has the same
     normalized title, UNLESS its id is in `force_keep_preprint_ids`.

Outputs:
  data/publications_filtered.json   curated list (input to the page builder)
  data/publications_filtered.csv    flat CSV of the curated list

Usage:
  python -X utf8 scripts/curate.py
  python -X utf8 scripts/curate.py --in data/publications.json \
      --curation data/curation.json --out data/publications_filtered.json
"""
import argparse
import csv
import json
import re


def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def short_id(x):
    return (x or "").rstrip("/").split("/")[-1]


def curate(pubs, curation):
    excluded = {short_id(e["openalex_id"]) for e in curation.get("excluded_ids", [])}
    force_drop = {short_id(x) for x in curation.get("force_drop_ids", [])}
    force_keep_pre = {short_id(x) for x in curation.get("force_keep_preprint_ids", [])}

    log = []

    # 1 + 2: hard exclusions
    kept = []
    for p in pubs:
        sid = short_id(p["openalex_id"])
        if sid in excluded:
            log.append(f"DROP (excluded)      {sid}  {p['title'][:70]}")
            continue
        if sid in force_drop:
            log.append(f"DROP (force_drop)    {sid}  {p['title'][:70]}")
            continue
        kept.append(p)

    # 3: preprint de-duplication
    policy = (curation.get("preprint_policy") or {}).get("rule")
    if policy == "drop_preprint_if_published_exists":
        published_titles = {
            norm_title(p["title"]) for p in kept if p.get("type") != "preprint"
        }
        deduped = []
        for p in kept:
            sid = short_id(p["openalex_id"])
            if (p.get("type") == "preprint"
                    and norm_title(p["title"]) in published_titles
                    and sid not in force_keep_pre):
                log.append(f"DROP (preprint dup)  {sid}  {p['title'][:70]}")
                continue
            deduped.append(p)
        kept = deduped

    return kept, log


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", default="data/publications.json")
    ap.add_argument("--curation", default="data/curation.json")
    ap.add_argument("--out", dest="out", default="data/publications_filtered.json")
    args = ap.parse_args()

    pubs = json.load(open(args.inp, encoding="utf-8"))
    curation = json.load(open(args.curation, encoding="utf-8"))

    kept, log = curate(pubs, curation)
    kept.sort(key=lambda w: (w["year"] or 0, w["cited_by_count"]), reverse=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)

    csv_path = args.out.rsplit(".", 1)[0] + ".csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "title", "authors", "venue", "type",
                    "cited_by_count", "doi", "openalex_id"])
        for p in kept:
            w.writerow([p["year"], p["title"], "; ".join(p["authors"]),
                        p["venue"], p["type"], p["cited_by_count"],
                        p["doi"], p["openalex_id"]])

    print("Curation log:")
    for line in log:
        print("  " + line)
    print(f"\nInput: {len(pubs)} papers -> kept {len(kept)} "
          f"(dropped {len(pubs) - len(kept)}).")
    total = sum(p["cited_by_count"] for p in kept)
    print(f"Curated total citations: {total}")
    print(f"Wrote: {args.out}\n       {csv_path}")


if __name__ == "__main__":
    main()
