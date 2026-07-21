# vsharma-publications

A personal, shareable web page of my published papers, with charts showing how
citations have grown over the years.

## Project layout

```
scripts/   Reusable scripts (data fetching, processing, page generation)
data/      Gathered publication + citation data (JSON/CSV)
site/      The generated web page and assets
```

## Live page

**https://vagisha.github.io/vsharma-publications/**

Published via GitHub Pages, deployed automatically by
`.github/workflows/deploy-pages.yml` whenever `site/index.html` changes on
`main`. The page is a single standalone HTML file (no external dependencies).

## Status

1. ✅ **Gather publication data** — papers + citation-by-year counts.
2. ✅ **Design the page** — publications list + citation growth charts.
3. ✅ **Publish it live** — a shareable web page.

## Running the scripts

Scripts live in `scripts/`. Each is runnable on its own; see the header comment
in each file for usage. Python scripts are run with UTF-8 mode.

### Reproducible pipeline

```
# 1. (one-time) find the ORCID iD
python -X utf8 scripts/find_orcid.py "Vagisha Sharma" --affiliation "University of Washington"

# 2. fetch all works + citations-by-year from OpenAlex (retries if busy)
python -X utf8 scripts/fetch_openalex.py --orcid 0000-0003-1922-439X --mailto vagisha@gmail.com

# 3. apply persistent curation decisions (data/curation.json) -> filtered list
python -X utf8 scripts/curate.py

# 4. (optional) regenerate the review spreadsheet
python -X utf8 scripts/make_review_sheet.py
```

All manual review decisions (which papers are not mine, how preprints are
handled) live in **`data/curation.json`**, so re-running steps 2–3 reproduces
the curated list with no manual work.

### Data files (`data/`)

| File | What it is |
|---|---|
| `openalex_works_raw.json` | Full raw OpenAlex records (source of truth) |
| `publications.json` / `.csv` | Cleaned, all fetched works (32) |
| `publications_review.xlsx` | Human review sheet with flag column |
| `curation.json` | Persistent curation decisions |
| `publications_filtered.json` / `.csv` | Curated list used to build the page (27) |
