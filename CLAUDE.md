# rgfell.github.io: Quarto academic website

Personal site of Rodrigo Gomez-Fell (Antarctic glaciology, SAR remote sensing, University of Canterbury).
Built with Quarto and served by GitHub Pages at https://rgfell.github.io.

## Structure

```
_quarto.yml        Site config: navbar, footer icons, theme, SEO, render list, pre-render hook
theme-light.scss   Light-mode colours; --rgf-bg-strength and --rgf-panel for the page photo
theme-dark.scss    Dark-mode colours; same two variables
styles.css         Layout and components shared by both modes (.hero, .cv, .pub-list, .todo …)
index.qmd          Home: profile card (left, sticky) + intro, theme keyword tags, selected publications,
                   news timeline, positions/education (CSS grid in styles.css, no JavaScript)
about.qmd          About: 1:2 grid; left = photo, collaborator graph + table, education;
                   right = biography, community, research interests (max ~70 characters per line)
cv.qmd  research.qmd  contact.qmd     Single pages
projects.qmd       All projects on one page, one ## section each (anchors used by other pages)
news/              One .qmd per news item (shown on Home, newest 5); _metadata.yml shows year only
_templates/        news-timeline.ejs: listing template for the Home news timeline
publications.qmd   Journal articles, preprints, conference papers, book chapters (generated list)
reports.qmd        Technical and project reports (generated list)
publications/      publications.bib (single source of truth), apa.csl, _list-*.md (generated, git-ignored)
_scripts/build_publications.py   Pre-render: .bib -> grouped, APA-formatted lists, Home cards, network
_scripts/network.py              Collaborator network SVG + table for the About page (plain Python)
_scripts/publish_cv_pdf.py       Post-render: cv.qmd (Typst PDF) -> files/CV_Rodrigo_Gomez_Fell.pdf
_environment       SOURCE_DATE_EPOCH so the CV PDF is byte-identical when nothing changed
files/             CV_Rodrigo_Gomez_Fell.pdf: the ONLY public CV, generated from cv.qmd; never edit by hand
images/            Web-ready images: profile.jpg/.webp, bg-glacier.webp and bg-iceberg.webp (page
                   backgrounds, 1600x1200), images/projects/ for project card images
_source/           Never published (leading underscore). Original CVs in _source/docs and
                   full-resolution photos are git-ignored and stay local
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
| `@phdthesis`     | Publications → Theses                            |
| `@techreport`    | Reports                                          |

Entries are grouped by `year`, newest first, and Rodrigo's name is bolded automatically
(spellings are in `MY_NAME` in the script). For a DOI, get the metadata with
`curl -LH "Accept: application/x-bibtex" https://doi.org/<DOI>` and tidy it. Never invent a
field: leave out what you can't source. Protect capitals with braces: `{Antarctica}`.
`quarto preview` runs the script only at startup, so restart it after editing the `.bib`.

### Feature a paper on Home ("Selected publications" cards)
In its `.bib` record add `keywords = {featured}` (aim for 5–6 in total), plus
`tag = {Short topic}` and `summary = {One plain-language sentence.}`. Cards are ordered newest first.

### Add a card image (project or featured paper)
Put the original in `_source/` (git-ignored if .jpg/.png). Export a 3:2 crop, about 1200 px wide
(never upscale a smaller original), as both `.webp` and `.jpg`, each under 200 KB, with all
metadata stripped, into `images/projects/`. Charts and multi-panel figures: pad to 3:2 on white
rather than cropping away data. Then:
- Project: use the `<picture>` block at the top of the project's section in `projects.qmd`
  (WebP source + JPEG fallback, `alt` describing what the image shows). Put a credit in `<figcaption class="image-credit">` when the
  image or its data is not Rodrigo's (e.g. "Contains modified Copernicus Sentinel data (2024).").
- Featured paper: in its `.bib` record add `image = {images/projects/pub-<name>.jpg}`,
  `imagealt = {...}` and, if needed, `imagecredit = {...}` (one line each). The script uses the
  `.webp` sibling automatically. Without `image`, the card shows a blue banner with the journal.
Only use figures you have the right to publish (see Licensing below).

### Social card
`images/social-card.jpg` (1200 x 630) is the default Open Graph/Twitter image (`website: image:`
in `_quarto.yml`); Home sets it explicitly because Quarto would otherwise use the first image on
the page. Pages with their own `image:` (About) use that instead; Projects sets the social card
explicitly for the same reason.

### A report
Same as above, with `@techreport` (`institution`, `number`, `type` as available).
APA would drop a report's `note`, so the build script appends it at the end of the entry
(e.g. "… University of Canterbury. Issued for Use."). Other fields APA ignores, such as
`client`, stay in the `.bib` only; put the client in `type`
(e.g. `type = {Report prepared for Environment Canterbury}`) to show it.

### A project
All projects live on **one page**, `projects.qmd`: there are no separate project pages.
Add a new `## ` section there, in order (current projects first, newest start year first;
unconfirmed dates last), separated by `---`. Give it a short, stable anchor, because other
pages link to it as `projects.qmd#<anchor>` (e.g. Research "Current projects", news items).

````markdown
## Short project title {#my-anchor}

```{=html}
<figure class="project-figure">
  <picture>
    <source srcset="images/projects/<name>.webp" type="image/webp">
    <img src="images/projects/<name>.jpg" width="1200" height="800" loading="lazy" alt="What the image shows.">
  </picture>
  <figcaption class="image-credit">Credit, if the image or data is not Rodrigo's.</figcaption>
</figure>
```

**Years:** 2026–2028

### Summary
### My role                      # first person, e.g. "I am a researcher on this project."

::: {.content-hidden}
### Collaborators
- Name, institution            # hidden until filled in; delete the ::: fences to publish
:::

### Funding                      # only if the funder is confirmed; otherwise omit the section
### Related publications
Cite from the .bib with @key (e.g. @baker2026hapua); references appear at the bottom of the
page. Otherwise write "None yet."
````

### Add a guest lecture, talk or panel (CV)
In `cv.qmd`: guest lectures go under **Teaching and supervision**, invited talks and panels
under **Invited talks and panels**, as `- **YEAR** · Role, title, event or course, institution`.
Unknown details: `[[TODO: …]{.todo}]{.content-visible when-format="html"}` so the TODO shows
on the web page for review but never in the PDF. Add a news item too when the date is known.

### Collaborator network (About page)
Built automatically at every render from the `@article` entries in `publications.bib` by
`_scripts/network.py`; nothing to edit by hand. Adding a journal article updates it.
- Nodes are co-authors, Rodrigo at the centre; edges join people who share an article
  (thicker = more shared articles); node size = articles shared with Rodrigo.
- Merge rule: accents, case, hyphens and spaces in family names are ignored; given names must
  share the first initial and, where both are written out, the first name (so "Marsh, Oliver" =
  "Marsh, Oliver J."; "González, Alejandro" ≠ "González, Inti"). Rodrigo = family Gomez-Fell /
  Gomez Fell / Gómez / Gomez with a first name starting with R.
- Only Rodrigo and his **top 10** co-authors are drawn (all labelled; `TOP_N` in network.py), and
  the "Frequent co-authors" table lists exactly the same 10. Ranking: shared articles, then most recent shared article, then
  name; people tied at the cut-off but left out are printed in the build log.
- The build log prints every merge, every same-surname pair kept apart, dropped authors and
  any @article with a truncated author list ("others"). Check it after adding papers.

### Update the CV (web page and PDF)
Edit `cv.qmd` only. Every `quarto render` builds both the web page and a Typst PDF from it,
and `_scripts/publish_cv_pdf.py` copies the PDF to `files/CV_Rodrigo_Gomez_Fell.pdf`
(commit that file) and `_site/files/`. Blocks marked `.content-visible when-format="typst"`
appear only in the PDF (contact header), `when-format="html"` only on the web.
If `pdftotext` is on PATH (or `PDFTOTEXT` points to it), the script fails the build when
the PDF contains a phone number, postal address or date of birth. Never publish the
original CVs, and never "redact" a PDF by drawing boxes: the text stays in the file.

### A news item
Create `news/<YYYY>-<slug>.qmd`:

```markdown
---
title: "Short headline"
date: 2026-03-15        # add "# TODO: exact date" if only the year is certain
description: "One or two sentences shown in the Home timeline."
categories: [award]     # e.g. award, grant, event, fieldwork, conference, paper
---

Optional longer text for the item's own page.
```

The Home page lists the newest five (year only). A full News page (`news.qmd`, navbar entry
commented out in `_quarto.yml`) is planned for Stage 3; then link it from the Home news section.

## Licensing (footer notice on every page; set in `_quarto.yml` page-footer)

- **Text and original photographs: CC BY 4.0** (© Rodrigo Gomez-Fell) unless stated otherwise.
- **Satellite-derived images keep their provider's terms** (Copernicus Sentinel, UMBRA, …) and carry a credit in `<figcaption class="image-credit">` where they appear. Don't
  guess licence wording: leave a hidden TODO until Rodrigo confirms it.
- **Publisher figures become citation-only cards.** Don't publish figures from papers unless the
  paper is open access under a licence that allows it (e.g. CC BY). Otherwise give the featured
  card no `image` field: it shows the journal-name banner with the title linked to the DOI.
  Figures removed for this reason are kept locally in `_source/removed-publisher-figures/`.
- **Restricted-access data never goes on a public page**, whatever its licence (e.g. ESA BIOMASS
  cal/val data, available only to approved teams). Such images live in
  `_source/removed-restricted-images/` (git-ignored). Use a public alternative instead.
- **ESA images:** only use an image whose esa.int page shows "LICENCE: ESA Standard Licence"
  (prefer ones without "Additional permission may be required"). Copy the CREDIT line from that
  page exactly, e.g. `Image: ESA - J. Huart (ESA Standard Licence)`, linking the licence to
  https://www.esa.int/ESA_Multimedia/Terms_and_conditions_of_use_of_images_and_videos_available_on_the_esa_website
  (the old .../ESA_Multimedia/Copyright_Notice URL returns 404). Don't crop out or alter the ESA logo.
- **Umbra (tasked data):** credit "SAR imagery courtesy of Umbra" (Umbra publishes no wording).

## Conventions

- **Name:** always **Rodrigo Gomez-Fell** on the site and in page titles. In author lists,
  keep each paper's own spelling (Gomez-Fell, Gomez Fell, Gómez, Gomez); `MY_NAME` in
  `_scripts/build_publications.py` bolds all of them.
- **Privacy (public repo):** never commit anything containing Rodrigo's phone number, postal
  address or date of birth. Original CVs (any format) stay in `_source/docs/` and are
  git-ignored; only the redacted `files/CV_Rodrigo_Gomez_Fell.pdf` is tracked and published.
  Email on the site is the institutional one, written as plain text (no `mailto:`).
- **Voice:** page text is in the **first person** ("I", "my"), plain and concise, with New Zealand
  spelling (organised, characterise, using). Keep **third person** in `title:` and `description:`
  (they appear in search results and social cards), and keep the CV as a list without pronouns.
  **Exception: news items (`news/*.qmd`) are always in the third person** ("Rodrigo received…"),
  so the Home timeline reads consistently.
  Text Rodrigo has written himself is his: change only person and typos.
- Web images: strip EXIF/GPS, JPEG under 150 KB, WebP where it helps; originals go in `_source/`.
- Every page has a `description:` in its front matter (SEO and social cards; hidden on the page).
- Every image needs alt text. One `#` heading per page comes from `title:`; body headings start at `##`.
- Unconfirmed facts are marked `[TODO: …]{.todo}`. Never replace a TODO with a guess;
  ask Rodrigo. Check with `grep -rn TODO --include=*.qmd .` before publishing.
- Keep colours in the two `.scss` files and keep text contrast at WCAG AA or better.
- **Page background photo:** `--rgf-bg-image` in `styles.css` picks the photo;
  `--rgf-bg-strength` (light 0.55, dark 0.40) sets how visible it is, and `--rgf-panel`
  (white 0.80 / page colour 0.78) is the panel behind content. Measured worst-case contrast
  stays AA up to strength 0.6 (light) and 0.45 (dark) with those panels.

## Commands

- `quarto preview --port 4200`: live local preview. Stop it before a full `quarto render`,
  because both write to `_site/` and can collide.
- `quarto render`: build into `_site/` (runs `_scripts/build_publications.py` first)
- Do **not** `git push` unless Rodrigo explicitly says so. The old Pelican blog is archived
  on the `pelican-archive` branch. Deployment method (GitHub Actions vs `quarto publish`) is still TODO.
