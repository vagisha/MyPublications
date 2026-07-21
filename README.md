# MyPublications

A personal, shareable web page of my published papers, with charts showing how
citations have grown over the years.

## Project layout

```
scripts/   Reusable scripts (data fetching, processing, page generation)
data/      Gathered publication + citation data (JSON/CSV)
site/      The generated web page and assets
```

## Status

Work in progress. Steps:

1. **Gather publication data** — papers + citation-by-year counts.
2. **Design the page** — publications list + citation growth charts.
3. **Publish it live** — a shareable web page.

## Running the scripts

Scripts live in `scripts/`. Each is runnable on its own; see the header comment
in each file for usage. Python scripts are run with UTF-8 mode:

```
python -X utf8 scripts/<script>.py
```
