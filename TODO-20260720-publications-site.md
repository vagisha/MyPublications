# TODO — Publications Website with Citation Growth Charts

**Created:** 2026-07-20
**Owner:** vagisha (vagisha@gmail.com)
**Repo:** https://github.com/vagisha/MyPublications

---

## Goal

Build a personal, shareable web page of my published papers, including charts
that show how my citations have grown over the years, and publish it live so I
can share the link with others.

Everything for this project lives inside this repository. Any code written is
saved as reusable scripts that can be run again.

---

## Constraints & conventions

- Run all Python with `python -X utf8 ...`.
- Keep all project files inside this folder.
- Save code as reusable, re-runnable scripts in `scripts/`.
- Multi-step process — wait for approval at each step before moving on.
- Keep this spec updated as work progresses.
- **The page must be a SINGLE STANDALONE HTML file** — all CSS, JS, chart
  rendering, and images inlined (base64); NO external/CDN requests, works offline.

---

## Plan & Progress

### Step 0 — Project setup ✅ DONE (2026-07-20)
- [x] Initialize git repository
- [x] Create structure: `scripts/`, `data/`, `site/`
- [x] Add `.gitignore` and `README.md`
- [x] Push to GitHub as a public repo

### Step 1 — Gather publication data ✅ DONE (2026-07-20)
Goal: collect the list of papers + citation counts broken down by year
(needed for the growth charts).
- [x] Identify the author profile — **ORCID 0000-0003-1922-439X**
      (Vagisha Sharma, University of Washington; proteomics / mass-spec informatics)
- [x] Wrote `scripts/find_orcid.py` (reusable ORCID lookup by name/affiliation)
- [x] Primary data source = **OpenAlex keyed by ORCID** (full list + citations-by-year)
- [x] Wrote `scripts/fetch_openalex.py` (retries when OpenAlex is busy)
- [x] Saved data: `data/openalex_works_raw.json`, `data/publications.json`,
      `data/publications.csv`
- [x] Wrote `scripts/make_review_sheet.py` → `data/publications_review.xlsx`
- [x] **USER reviewed** (2026-07-20): all mine except the CNN/apple-leaf paper.
- [x] Persisted decisions in `data/curation.json` (reproducible, no re-review)
- [x] Wrote `scripts/curate.py` → `data/publications_filtered.json/.csv`

**Fetched:** 32 works, 5,106 total citations → **curated to 27 works, 4,982 cites.**
**Citation-by-year:** 2012–2026 (cumulative ~9 → ~5,064; ~42 cites predate 2012;
2026 is a partial year — will be annotated on the chart).

**Curation decisions (in `data/curation.json`):**
- Excluded W4213271093 — "...Apple Leaf Disease Detection" (different Vagisha Sharma).
- Preprint policy: keep a preprint only if it has no published version.
  Dropped 4 preprints (QC framework, Comet, senescence atlas, phospho library);
  kept piNET (2019, no published counterpart).

### Step 2 — Design the page ✅ DONE (2026-07-20, approved by user)
Goal: layout with a publications list and citation growth chart(s).

**Design decisions (from Q&A on 2026-07-20):**
1. Header: "Vagisha Sharma" — subtitle "University of Washington" (no job title).
2. No bio text.
3. No photo/headshot.
4. Header links: ORCID only (https://orcid.org/0000-0003-1922-439X).
5. Charts (4, revised 2026-07-20 — dropped standalone cumulative-citations
   chart as redundant with the dual-axis line, replaced with top collaborators):
   citations/year (dual-axis: bars = per-year, line = cumulative, footnote on
   ~42 pre-2012 untracked citations); publications/year (dual-axis: bars =
   per-year, line = cumulative pub count); top-cited papers (bar chart); top
   collaborators (bar chart, count of shared publications, excludes self).
6. Stat tiles: total papers, total citations, h-index, years active.
7. Publications shown as a single **sortable + filterable table** (not cards),
   default sort = citation count descending. Columns: Title (linked to DOI),
   Authors, Type, Year, Citations.
8. Author list per row: show first + last author + up to 4 in between,
   expandable for the rest; bold "Vagisha Sharma" wherever it appears.
9. Style: light theme, bright multi-colored accents (not a single accent color).
10. Footer: data source (OpenAlex) + last-updated date + brief note on
    citation-counting methodology.

**Hard requirement:** page must be a **single standalone HTML file** — all
CSS/JS/chart-rendering inlined, no external/CDN requests, works offline.

- [x] Wrote `scripts/build_site.py` (charts hand-rolled in vanilla SVG/JS, no
      CDN deps) → generates `site/index.html`
- [x] Generated `site/index.html` (44 KB, 27 publications)
- [x] Verified in-browser: charts render correctly, table sort/filter/search
      work, DOI links resolve, name bolding + author-expand toggle work,
      no console errors, no external resource loads (confirmed standalone)
- [x] **USER reviewed and approved** (2026-07-20)

### Step 3 — Publish live ⬜ TODO
Goal: a shareable live URL.
- [ ] Decide hosting (Artifact / GitHub Pages / other)
- [ ] Publish
- [ ] Confirm the shareable link works

---

## Decisions log

- 2026-07-20: Repo created and pushed public as `MyPublications`.
- 2026-07-20: Convention — run Python with `-X utf8`.
- 2026-07-20: Primary data source = OpenAlex, keyed by ORCID.
- 2026-07-20: Excluded the CNN/apple-leaf paper (name collision).
- 2026-07-20: Preprints kept only when no published version exists.

---

## Open questions (for Step 2 — page design)

- Which charts do you want? (cumulative citations/year, citations-per-year bars,
  citations-per-paper, h-index, publications-per-year, ...)
- Visual style / branding (colors, light or dark, photo/bio/links)?
- Bold your name in each author list?
- Where to host the live page (Artifact vs GitHub Pages)?
