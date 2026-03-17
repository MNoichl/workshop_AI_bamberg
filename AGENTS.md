# Repo Agent Notes

These instructions apply to the whole repository.

## Git Preflight

Before editing any file:

1. Run `git status --short`.
2. Inspect the diff for every file you plan to touch.
3. If a file already contains uncommitted user edits, preserve them unless the user explicitly asked you to rewrite that text.

## Slide Content Boundaries

The following files should be treated as user-authored content first and template/code second:

- `slides/index.qmd`
- `slides/ai_for_research_workshop_slides.md`

For layout, theme, deployment, or interaction tasks:

- prefer editing HTML/CSS/JS/config files over rewriting slide prose
- do not paraphrase or "clean up" slide wording unless the user explicitly asks for textual edits
- if a change requires modifying existing slide text, keep the change as narrow as possible and mention it clearly

## Workflow Expectations

- Keep `main` in a deployable state.
- Prefer small, topical commits.
- After slide-related changes, run `quarto render slides/index.qmd`.
- Do not edit generated slide output (`slides/index.html`, `slides/index_files/`) by hand.

## Slide Template

When working inside `slides/`, also follow the local instructions in `slides/AGENTS.md`.
