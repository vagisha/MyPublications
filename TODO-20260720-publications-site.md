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

### Step 2 — Design the page ⬜ TODO
Goal: layout with a publications list and citation growth chart(s).
- [ ] Decide charts (cumulative citations/year, citations per paper, h-index, etc.)
- [ ] Decide layout & style
- [ ] Build page generator script → save to `scripts/`
- [ ] Generate into `site/`
- [ ] Review with the user

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
