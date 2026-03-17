# Workshop Website

Simple repository for the Bamberg workshop website and slide deck for 18-19 March 2026.

## Structure

- `index.html`: landing page with schedule and material links.
- `assets/site.css`: shared styling for the landing page.
- `slides/index.qmd`: Quarto revealjs source for the workshop slides.
- `slides/ai_for_research_workshop_slides.md`: user-authored draft/source notes for Session 1.
- `slides/media/`: optional place for future slide-specific assets.
- `notebooks/workshop_notebook.ipynb`: placeholder notebook that can later be replaced in-place.
- `.github/workflows/deploy-pages.yml`: GitHub Pages build and deployment workflow.
- `.github/workflows/validate.yml`: validation workflow for repository structure and slide rendering.
- `GIT_WORKFLOW.md`: repo-level git workflow notes.

## Git workflow

The repo now has a simple git workflow:

- repo-level agent rules in `AGENTS.md`
- a documented local workflow in `GIT_WORKFLOW.md`
- a validation workflow that renders the slides on pushes and pull requests

This is intended to make authored slide text easier to protect while still allowing layout and deployment work to move quickly.

## Local preview

Render the slide deck from `slides/`:

```bash
quarto render slides/index.qmd
```

Preview the deck locally:

```bash
quarto preview slides/index.qmd
```

The root page is plain HTML/CSS and can be opened directly in a browser.

## Deployment

The GitHub Actions workflow renders the Quarto deck, copies the landing page and notebook into `_site/`, and deploys everything to GitHub Pages.

The published materials live at:

- `/` for the workshop landing page
- `/slides/` for the slide deck
- `/notebooks/workshop_notebook.ipynb` for the notebook file
