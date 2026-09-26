# rgfell.github.io: Quarto academic website

Personal site of Rodrigo Gomez-Fell (Antarctic glaciology, SAR remote sensing, University of Canterbury).
Built with Quarto and served by GitHub Pages at https://rgfell.github.io.

## Structure

```
_quarto.yml        Site config: navbar, footer icons, theme, SEO, render list, pre-render hook
theme-light.scss   Light-mode colours (Bootstrap variables)
theme-dark.scss    Dark-mode colours
styles.css         Layout and components shared by both modes (.hero, .cv, .pub-list, .todo …)
index.qmd  about.qmd  cv.qmd  research.qmd  contact.qmd     Single pages
projects.qmd       Listing (cards) over projects/*.qmd
projects/          One .qmd per project
publications.qmd   Journal articles, preprints, conference papers, book chapters (generated list)
reports.qmd        Technical and project reports (generated list)
publications/      publications.bib (single source of truth), apa.csl, _list-*.md (generated, git-ignored)
_scripts/build_publications.py   Pre-render: .bib -> grouped, APA-formatted lists
files/             Downloadable files: CV_Rodrigo_Gomez_Fell.pdf
images/            Web-ready images; images/projects/ for project card images
_source/           Never published (leading underscore). CVs in _source/docs (tracked);
                   full-resolution photos (*.jpg, *.png) are git-ignored and stay local
_site/  .quarto/   Build output and cache: git-ignored, never edit
```

## How to add content

### A paper, abstract, preprint or book chapter
Add one BibTeX record to `publications/publications.bib`, then `quarto render`.
The entry type picks the section:

| BibTeX type      | Appears under                                    |
|------------------|--------------------------------------------------|
| `@article`       | Publications → Journal articles                  |
| `@unpublished`   | Publications → Preprints (`howpublished` = server, `pubstate = {preprint}`) |
| `@inproceedings` | Publications → Conference papers and abstracts (abstract ID goes in `pages`) |
| `@incollection`  | Publications → Book chapters                     |
| `@techreport`    | Reports                                          |

Entries are grouped by `year`, newest first, and Rodrigo's name is bolded automatically
(spellings are in `MY_NAME` in the script). For a DOI, get the metadata with
`curl -LH "Accept: application/x-bibtex" https://doi.org/<DOI>` and tidy it. Never invent a
field: leave out what you can't source. Protect capitals with braces: `{Antarctica}`.
`quarto preview` runs the script only at startup, so restart it after editing the `.bib`.

### A report
Same as above, with `@techreport` (`institution`, `number`, `type` as available).

### A project
Create `projects/<slug>.qmd` and a card image in `images/projects/` (16:9, e.g. 800×450):

```markdown
---
title: "Short project title"
description: "One-line description shown on the card."
order: 5                      # position on the Projects page (lower = first)
years: "2026–2028"
image: ../images/projects/<slug>.jpg
image-alt: "What the image shows."
---

![](../images/projects/<slug>.jpg){fig-alt="What the image shows."}

**Years:** 2026–2028

## Summary
## Role
## Collaborators
## Funding
## Related publications
Cite entries from the .bib, e.g. [@gomezfell2024erebus], after adding
`bibliography: ../publications/publications.bib` and `csl: ../publications/apa.csl`
to the front matter. Otherwise write "None yet."
```

### Replace the CV PDF
Overwrite `files/CV_Rodrigo_Gomez_Fell.pdf` (keep the file name so links keep working;
keep the source copy in `_source/docs/`). Update the web version in `cv.qmd` to match.
The public PDF must not contain a phone number, home address or date of birth.

### News (Stage 3, not built yet)
Planned: `news.qmd` listing over `news/<YYYY-MM-DD>-<slug>.qmd`; uncomment it in the navbar.

## Conventions

- Name is spelled **Rodrigo Gomez-Fell** (as in the CVs). Text is third person, plain and concise.
- Web images: strip EXIF/GPS, JPEG under 150 KB, WebP where it helps; originals go in `_source/`.
- Every page has a `description:` in its front matter (SEO and social cards; hidden on the page).
- Every image needs alt text. One `#` heading per page comes from `title:`; body headings start at `##`.
- Unconfirmed facts are marked `[TODO: …]{.todo}`. Never replace a TODO with a guess;
  ask Rodrigo. Check with `grep -rn TODO --include=*.qmd .` before publishing.
- Keep colours in the two `.scss` files and keep text contrast at WCAG AA or better.

## Commands

- `quarto preview --port 4200`: live local preview. Stop it before a full `quarto render`,
  because both write to `_site/` and can collide.
- `quarto render`: build into `_site/` (runs `_scripts/build_publications.py` first)
- Do **not** `git push` unless Rodrigo explicitly says so. The old Pelican blog is archived
  on the `pelican-archive` branch. Deployment method (GitHub Actions vs `quarto publish`) is still TODO.
