# alexsavio.github.io

Personal blog of **Alexandre Manhães Savio** — freelance Software, Cloud & AI engineer.
Long-form writing on engineering practice, with a recurring *First Principles* series.

Live at <https://alexsavio.github.io>.

![Publish Github Pages](https://github.com/alexsavio/alexsavio.github.io/workflows/Publish%20Github%20Pages/badge.svg?branch=dev&event=page_build)

## Stack

- [Pelican](https://getpelican.com/) — static site generator
- [`uv`](https://github.com/astral-sh/uv) — Python dependency management
- [`just`](https://github.com/casey/just) — task runner (see `justfile`)
- Custom `fancy-terminal` theme (lives in `themes/fancy-terminal/`) with a Catppuccin Latte palette
- GitHub Pages via `ghp-import` (deploys `output/` to the `master` branch)

## Quick start

```bash
just install        # uv sync
just dev            # clean build + watch + serve at http://localhost:8000
```

Other useful commands:

```bash
just serve-dev      # autoreload dev server only
just build          # one-shot dev build
just publish        # production build via publishconf.py (absolute URLs)
just github-deploy  # build for prod + force-push output to master (GH Pages)
just check          # format + lint + build
```

## Repository layout

```
content/                     # Markdown posts, one file per article
├── pages/                   # Standalone pages (About, Work with me)
│   ├── about.md
│   └── work-with-me.md
├── imgs/                    # Images referenced by content + site assets
│   └── alex_headshot.png
├── first_principles_*.md    # The First Principles series (Engineering category)
└── *.md                     # Everything else (Python, Tools categories)

themes/fancy-terminal/       # Custom Pelican theme
├── templates/               # Jinja templates (base, index, article, page, archives, …)
└── static/css/style.css     # All styles, Catppuccin Latte palette

pelicanconf.py               # Dev/local build config
publishconf.py               # Production overrides (SITEURL, feeds, …)
justfile                     # Task runner
scripts/                     # Helper scripts (most ignored — kept local)
```

## Content workflow

### Writing a new post

1. Create `content/<slug>.md` with the Pelican metadata block:

    ```
    Title: Post title
    Date: 2026-04-10 12:00:00
    Category: Engineering   # or Python, or Tools
    Tags: tag1, tag2, tag3
    Slug: post-slug
    Author: Alexandre M. Savio
    Email: alexsavio@gmail.com
    Summary: 1–3 sentence summary used in feeds and previews.
    Status: draft
    ```

2. Write the post, preview at `http://localhost:8000/drafts/<slug>.html` while `just dev` is running.
3. When ready, flip `Status: draft` → `Status: published`.
4. Commit and deploy (see below).

### Categories (kept intentionally narrow)

| Category      | Used for                                                  |
|---------------|-----------------------------------------------------------|
| `Engineering` | First Principles series, long-form essays, retrospectives |
| `Python`      | Python tutorials, installs, library deep-dives            |
| `Tools`       | Git, shell, env management, LaTeX, dev tooling            |

### First Principles series

Posts in the series carry one extra metadata line:

```
Series: First Principles
```

The [`pelican-series`](https://pypi.org/project/pelican-series/) plugin auto-orders them by date,
computes `article.series.{index, all, previous, next}`, and the theme renders a
*"Part N of M"* navigation block at the top of each post.

### Drafts

Any post with `Status: draft` is built into `output/drafts/` and is **not** linked from the
home page, archives, sitemap, or feeds. It's there for local preview only.

## Plugins

All plugins are installed from PyPI under the `pelican.plugins.*` namespace and auto-discovered
(no `PLUGIN_PATHS`, no submodule):

| Plugin                                                                    | Role                                            |
|---------------------------------------------------------------------------|-------------------------------------------------|
| [`pelican-sitemap`](https://pypi.org/project/pelican-sitemap/)            | XML sitemap for SEO                             |
| [`pelican-series`](https://pypi.org/project/pelican-series/)              | First Principles series navigation              |
| [`pelican-related-posts`](https://pypi.org/project/pelican-related-posts/)| *You might also like* block on article pages    |

To update any of them: `uv lock --upgrade`.

## Deployment

GitHub Pages. Pushing to `dev` is the development branch; `master` is a **build-artifact branch**
that `ghp-import` rewrites from `output/` on every deploy.

```bash
just github-deploy    # publish (prod build) + ghp-import + force-push master
```

The force-push is expected — `master` is regenerated on every deploy and holds no
source code. Do not commit directly to it.

## Licence / credits

Content © Alexandre Manhães Savio. The custom theme is MIT-licensed.
