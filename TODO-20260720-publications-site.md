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

### Step 1 — Gather publication data ⬜ IN PROGRESS
Goal: collect the list of papers + citation counts broken down by year
(needed for the growth charts).
- [x] Identify the author profile — **ORCID 0000-0003-1922-439X**
      (Vagisha Sharma, University of Washington; proteomics / mass-spec informatics)
- [x] Wrote `scripts/find_orcid.py` (reusable ORCID lookup by name/affiliation)
- [ ] Decide primary data source (ORCID has only 3 works & no citation history →
      recommend **OpenAlex keyed by ORCID** for full list + citations-by-year)
- [ ] Write reusable fetch script → save to `scripts/`
- [ ] Save raw + cleaned data → `data/`
- [ ] Review data for accuracy with the user

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
- _(pending)_ Primary data source for citation-by-year data.

---

## Open questions

- Which author profile identifies you (Scholar / ORCID / OpenAlex URL)?
- Which source should be primary for citation-by-year data?
- Which charts do you want on the page?
- Where to host the live page?
