# Git Workflow

This repository uses a simple workflow so authored workshop content and implementation changes stay distinguishable.

## Baseline

- `main` is the canonical branch.
- Keep `main` deployable.
- Use small commits that match one task or one change area.

## Preflight Before Editing

Run:

```bash
git status --short
```

Then inspect the files you plan to touch:

```bash
git diff -- path/to/file
```

If `slides/index.qmd` or `slides/ai_for_research_workshop_slides.md` already contain local user edits, preserve the text unless the task explicitly asks for rewriting.

## Preferred Change Split

- Visual/layout changes: `index.html`, `assets/site.css`, slide CSS/JS/includes
- Slide content changes: `slides/index.qmd`, `slides/ai_for_research_workshop_slides.md`
- Deployment/automation changes: `.github/workflows/`, `README.md`, config files

## Validation

Before committing slide-related work:

```bash
quarto render slides/index.qmd
```

Before a final handoff:

```bash
git diff --stat
git status --short
```

## Commit Style

Use short, direct commit messages, for example:

- `Add repo git workflow and validation`
- `Adjust landing page hero layout`
- `Add automatic slide figure numbering`
