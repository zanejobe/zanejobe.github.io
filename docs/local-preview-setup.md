# Local Preview Setup Log

This note records the local Jekyll preview setup used for this repository.

## Goal

Run a local copy of the GitHub Pages site so visual CSS changes can be checked at:

```sh
http://127.0.0.1:4000/
```

## What happened

- macOS system Ruby was `2.6.10`, which is too old for the current gem dependency set.
- Homebrew `ruby` installed Ruby `4.0.3`, but Jekyll 3.9 / Liquid 4 had compatibility issues with Ruby 4.
- Homebrew `ruby@3.3` installed successfully, but local Jekyll rendering hit a Liquid `tainted?` compatibility error.
- Homebrew `ruby@3.1` built the site successfully, then `jekyll serve` failed because Ruby 3 no longer ships `webrick` by default.

## Recommended local workflow

Install project gems with Ruby 3.1:

```sh
PATH="/usr/local/opt/ruby@3.1/bin:$PATH" bundle install
```

Build the site:

```sh
PATH="/usr/local/opt/ruby@3.1/bin:$PATH" bundle exec jekyll build
```

Serve the generated `_site` directory:

```sh
python3 -m http.server 4001 --directory _site
```

Open pages such as:

```sh
http://127.0.0.1:4001/publications/
```

Verification from the terminal:

```sh
curl --silent --fail "http://127.0.0.1:4001/publications/"
```

Note: `jekyll serve` can work once `webrick` is installed, but the static `_site` preview is more reliable for this repo because it avoids local live-server quirks while still showing the generated HTML/CSS that will be deployed.

## Gemfile notes

The local preview needs explicit dependencies that modern Ruby no longer includes by default:

- `csv`: required by Jekyll under newer Ruby versions.
- `webrick`: required by `jekyll serve` under Ruby 3+.

GitHub Actions should continue using the workflow-defined Ruby version. Local preview should use Ruby 3.1 unless the Jekyll/GitHub Pages stack is upgraded.
