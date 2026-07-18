# Agent Quickstart for `zanejobe.github.io`

This file is a practical onboarding guide for coding agents working in this repository.
Goal: make focused, low-risk edits to content and layout, then verify the site still builds.

## What This Repository Is

- Personal academic website built with Jekyll and the Minimal Mistakes remote theme.
- Primary pages are in `_pages`.
- Navigation is configured in `_data/navigation.yml`.
- Some page content is generated from data files and Liquid templates (especially CV/publications).
- Deployment is via GitHub Actions workflow in `.github/workflows/github-pages.yml`.

## High-Level Architecture

- `_config.yml`: Site-wide config (title, URL, plugins, defaults, scripts).
- `_pages/`: Top-level pages (`/`, `/cv/`, `/publications/`, etc.).
- `_includes/`: Reusable Liquid/HTML partials (for example, publications rendering).
- `_data/`: YAML data used by templates/pages (`grants_major.yml`, `grants_student.yml`, `mentees.yml`, navigation).
- `scripts/render-cv-pdf.mjs`: Playwright script used in CI to generate the downloadable CV PDF.
- `docs/local-preview-setup.md`: Local environment notes and known Ruby/Jekyll constraints.

## Current Runtime and Tooling Assumptions

- `Gemfile` includes:
  - `github-pages`
  - `csv` (needed by Jekyll on newer Ruby setups)
  - `webrick` (needed for `jekyll serve` on Ruby 3+)
- GitHub Actions builds with Ruby `3.3`.
- Local preview is currently most reliable with Homebrew Ruby `3.1` (see `docs/local-preview-setup.md`).

## Fast Start: Local Preview

Use the static preview workflow documented in `docs/local-preview-setup.md`.
This is more reliable than `jekyll serve` for this repository:

```sh
PATH="/usr/local/opt/ruby@3.1/bin:$PATH" bundle install
PATH="/usr/local/opt/ruby@3.1/bin:$PATH" bundle exec jekyll build
python3 -m http.server 4001 --directory _site
```

Then open:

- `http://127.0.0.1:4001/`
- `http://127.0.0.1:4001/cv/`
- `http://127.0.0.1:4001/publications/`

Quick health check:

```sh
curl --silent --fail "http://127.0.0.1:4001/publications/"
```

Do not assume the Cursor browser tool can load localhost. If it opens `about:blank`,
use the normal browser or verify with `curl`.

## Edit Map: If You Need To Change X

- **Top nav items** -> `_data/navigation.yml`
- **Site metadata / defaults / plugins** -> `_config.yml`
- **Publications page shell** -> `_pages/publications.md`
- **Publications list + custom publication styles/scripts** -> `_includes/publications-from-cv.md`
- **CV page content** -> `_pages/cv.md`
- **Grant/funding values used by CV calculations** -> `_data/grants_major.yml` and `_data/grants_student.yml`
- **CV mentoring lists (advisees, committee, undergrads, postdocs/staff, Shell interns)** -> `_data/mentees.yml`
- **CV downloadable PDF generation logic** -> `scripts/render-cv-pdf.mjs` and workflow file
- **Deployment behavior** -> `.github/workflows/github-pages.yml`

## Important Behavior to Preserve

- `/publications/` includes `_includes/publications-from-cv.md` through Liquid include.
- The publications include contains:
  - Long markdown publication content,
  - Inline CSS for publication link styling,
  - Inline JS that sets external links to open in a new tab.
- The CV page includes Liquid math over data files (for fundraising totals). YAML numeric integrity matters.
- CI generates the CV PDF into `_site/files/Zane_Jobe_CV_2026.pdf` during build before Pages deploy.

## Conventions and Guardrails

- Keep changes scoped to the user request; avoid broad formatting rewrites.
- Preserve existing front matter structure in `_pages/*.md`.
- Be careful with YAML indentation and numeric fields in `_data/*.yml`.
- Prefer editing data files/templates over hardcoding repeated content in multiple places.
- Do not change deployment workflow or toolchain versions unless explicitly requested.
- If touching CSS/JS embedded in markdown/includes, verify both desktop render and basic mobile layout.

## Validation Checklist Before Handoff

1. Site builds locally with `bundle exec jekyll build`.
2. `_site` is served locally with `python3 -m http.server 4001 --directory _site`.
3. Target page renders as expected in browser.
4. No Liquid/YAML parsing errors in terminal output.
5. Key routes still work:
   - `/`
   - `/cv/`
   - `/publications/`
6. If workflow/script changes were made, confirm CI assumptions still match local behavior.

## Common Pitfalls

- Ruby/Jekyll compatibility can fail on newer system Ruby versions.
- Missing `webrick` causes `jekyll serve` failures on Ruby 3+.
- `jekyll serve` may be slow or stale locally; prefer building once and serving `_site`.
- Cursor browser automation may not load localhost even when `curl` confirms the server is working.
- Small YAML indentation mistakes can break Liquid loops/calculations.
- Inline scripts/styles in markdown include files are easy to accidentally break with aggressive editing.

## Suggested Agent Workflow

1. Read this file and `docs/local-preview-setup.md`.
2. Inspect only the files relevant to the requested change.
3. Implement minimal edits.
4. Run local preview/build checks.
5. Report what changed, what was validated, and any residual risks.
