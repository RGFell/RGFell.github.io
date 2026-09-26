# rgfell.github.io: Quarto academic website

Personal site of Rodrigo Gomez Fell (Antarctic glaciology, SAR remote sensing, University of Canterbury).
Built with Quarto and served by GitHub Pages at https://rgfell.github.io.

## Structure

```
_quarto.yml        Site config: navbar, footer, theme, SEO (site-url → sitemap, Open Graph)
theme-light.scss   Light-mode colours (Bootstrap variables)
theme-dark.scss    Dark-mode colours
styles.css         Layout and components shared by both modes (.hero, .theme-card, .todo …)
index.qmd          Home
about.qmd          About / biography
contact.qmd        Contact links
images/            All images (favicon, photos, figures)
_site/  .quarto/   Build output and cache: git-ignored, never edit
```

## Planned sections (not built yet)

Each section is one listing page plus a folder holding one `.qmd` file per item.
When you create one, also uncomment its entry in the `_quarto.yml` navbar.

| Section      | Listing page        | One file per item in                                   |
|--------------|---------------------|--------------------------------------------------------|
| CV           | `cv.qmd`            | (single page; optionally link a PDF in `files/`)       |
| Research     | `research.qmd`      | (single page)                                          |
| Projects     | `projects.qmd`      | `projects/<slug>.qmd`                                  |
| Publications | `publications.qmd`  | `publications/<year>-<firstauthor>-<keyword>.qmd`      |
| News         | `news.qmd`          | `news/<YYYY-MM-DD>-<slug>.qmd`                         |

Adding a paper, news item or project means adding **one file** to the matching folder;
the listing page picks it up automatically (Quarto `listing:` with `contents: <folder>`).
Every item needs front matter with at least `title`, `date` and `description`.

## Conventions

- Every page has a `description:` in its front matter (used for SEO and social cards).
- Every image needs alt text: `![Descriptive alt text](images/file.png)`.
- One `#`-level heading per page comes from `title:`; body headings start at `##`.
- Unconfirmed facts are marked `[TODO: …]{.todo}`. Never replace a TODO with a guess;
  ask Rodrigo. Check with `grep -rn TODO *.qmd` before publishing.
- Keep colours in the two `.scss` files and keep text contrast at WCAG AA or better.

## Commands

- `quarto preview`: live local preview
- `quarto render`: build into `_site/`
- Do **not** `git push` unless Rodrigo explicitly says so. The old Pelican blog is archived
  on the `pelican-archive` branch. Deployment method (GitHub Actions vs `quarto publish`) is still TODO.
