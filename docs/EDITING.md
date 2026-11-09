# Editing the website

A short guide to changing the site, checking it locally and publishing it.
Full conventions are in `CLAUDE.md`.

## 1. Start the local preview

1. Open a terminal and `cd ~/RGFell.github.io`.
2. Run `quarto preview --port 4200`.
3. Open the printed address (http://localhost:4200) in your browser.
4. Leave it running while you edit: the page reloads each time you save.
5. Press `Ctrl+C` in the terminal to stop it.

After editing `publications/publications.bib`, stop and restart the preview, because the
publication lists are only rebuilt when it starts.

## 2. Edit text

Open the page's file in any text editor (VS Code works well), save, and check the preview.

| File | Page |
|---|---|
| `index.qmd` | Home |
| `about.qmd` | About |
| `cv.qmd` | CV (web page and the downloadable PDF) |
| `research.qmd` | Research |
| `projects.qmd` | Projects |
| `teaching.qmd` | Teaching |
| `contact.qmd` | Contact |

Publications and Reports are the exception: never edit those pages. Add or change the
record in `publications/publications.bib` and the lists are rebuilt from it.

## 3. Replace or add an image

1. Put the original in `_source/`. That folder is never published, and large photos
   there are never committed.
2. Prepare the web version: crop to 3:2 for project and paper cards (about 1200 px wide,
   never enlarged), strip the metadata (EXIF/GPS), and export it twice, as `.webp` and
   `.jpg`, each under 200 KB. Use the same name for both, e.g. `glacier.webp` and `glacier.jpg`.
3. Save both in `images/projects/` (cards) or `images/` (other page images).
4. Reference it in the page with the `<figure class="project-figure">` block. Copy one from
   `projects.qmd` and change the file names, the `alt` text (what the image shows) and,
   if the image or its data isn't yours, the credit line.

Easiest: ask Claude Code, e.g. *"Add `_source/glacier.png` as the image for the hāpua
project: 3:2 crop, WebP and JPEG, strip metadata, write alt text."*
By hand: crop and export in GIMP or https://squoosh.app (which also strips metadata).

## 4. Add a news item

1. Copy a file in `news/`, e.g. `news/2026-11-02-conference-season.qmd`.
2. Rename the copy `YYYY-MM-DD-short-name.qmd`.
3. Edit `title`, `date`, `description` and `categories`, then the text.
4. Write in the third person ("Rodrigo presented…"), three sentences at most.
   The newest five appear on Home.

## 5. Add a project

All projects are on one page, `projects.qmd`, not in separate files. Copy an existing
`## ` section (from its heading down to the next `---`), paste it in date order (current
projects first) and edit it. Give it a short anchor, e.g. `{#my-project}`. Keep the hidden
Collaborators block (`::: {.content-hidden}` … `:::`) until you have the names; delete
its two `:::` lines to show it.

## 6. Save and publish

1. `git status` to see what changed.
2. `git add -A`
3. `git commit -m "Add hāpua project image"` (a plain description of the change).
4. `git push origin main`. This starts the GitHub Actions workflow, which builds and
   publishes the site.
5. Check it: on https://github.com/RGFell/RGFell.github.io open the **Actions** tab (a green
   tick means it worked), then open https://rgfell.github.io a minute or two later.

Don't edit files in GitHub's web editor for anything beyond a one-line typo fix: it skips
the local preview, so you only find build problems after publishing.

## 7. When to ask Claude Code instead

These parts are generated or checked by code, so don't edit them by hand:

- the collaborator graph and table on About (`_scripts/network.py`);
- the CV PDF and its privacy check (`files/`, `_scripts/publish_cv_pdf.py`);
- the publication lists and Home cards (`_scripts/build_publications.py`);
- the publishing workflow (`.github/workflows/publish.yml`).

Also ask if a build fails or the Actions tab shows a red cross.
