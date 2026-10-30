# Public website

The free 1ml site is published at https://kiran-980.github.io/1ml/ from `main`.
It uses Python's standard library to render curated HTML, local CSS and optional
copy-button JavaScript. No package installation, paid service or tracking is needed.

From the repository root:

```sh
python -m unittest tests.test_website -v
python website/build.py
```

Only `build/site` is uploaded by the Pages workflow. Never upload the repository
root. `pages.json` defines unique page metadata; `content/` contains the copy and
`template.html` shares navigation, metadata and structured data. Install command
blocks are read from `docs/installation.md` to avoid stale duplicate commands.

For preview under the actual `/1ml/` prefix, copy the generated site into a local
preview directory's `1ml/` subdirectory and serve the preview directory with
`python -m http.server 8765 --bind 127.0.0.1 --directory <preview-directory>`.
Open `http://127.0.0.1:8765/1ml/`. Keep preview output outside tracked source.

The website check runs in the existing required `package-and-tools` suite. Pages
builds and checks again before deployment, which is restricted to `main`.
Source changes follow develop PR review and a checked promotion to main.

The sitemap contains canonical public URLs. This project site cannot set the
account domain's root `robots.txt`; a file at `/1ml/robots.txt` would not control
crawlers. Search Console verification/submission is a separate owner action.
No ranking, traffic or indexing outcome is guaranteed by a sitemap or audit score.

Keep starter prompts separate from executed examples, preserve MIT/free-access
messaging, and distinguish provider costs from plugin access. No public page
should reveal private automation artifacts or account credentials.
