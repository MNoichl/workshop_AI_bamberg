# Workshop Slide Decks

Deck sources:

- [index.qmd](/Users/Noich001/Desktop/workshop_AI_bamberg/slides/index.qmd) for Session 1
- [programming.qmd](/Users/Noich001/Desktop/workshop_AI_bamberg/slides/programming.qmd) for Session 3

Render from the repository root with:

```bash
quarto render slides
```

Preview a specific deck locally with:

```bash
quarto preview slides/index.qmd
```

## Deployment

The GitHub Pages workflow renders the Session 1 and Session 3 decks. Session 2 now runs from the shared notebook rather than a separate deck.

## Notes

- Edit the `.qmd` sources, not the generated `.html` output.
- Put any future slide assets under `slides/media/` so they are easy to commit and publish.
- Put modal-only local image assets under `slides/images/` and unignore the specific files you want committed in `slides/.gitignore`.
- The landing page lives in [index.html](/Users/Noich001/Desktop/workshop_AI_bamberg/index.html).
- The notebook link targets [workshop_notebook.ipynb](/Users/Noich001/Desktop/workshop_AI_bamberg/notebooks/workshop_notebook.ipynb).
