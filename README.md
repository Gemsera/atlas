# Atlas Passive Tree Planner (PoE1)

Static web app — no build step. Tree data and sprites come from GGG's official export
(https://github.com/grindinggear/atlastree-export, 3.30.0 preview 2).

## Deploy to GitHub Pages
1. Push the contents of this folder to a repo (root of `main`, or a `docs/` folder).
2. Repo → Settings → Pages → Source: "Deploy from a branch", pick the branch and folder.
3. Open `https://<user>.github.io/<repo>/`.

Shared trees live in the URL hash (`#s-…` standard, `#r-…` ruthless), so links work on any host.

## Run locally
`python3 -m http.server` in this folder, then open http://localhost:8000
(opening index.html directly from disk won't work — the data is loaded with fetch).

## Updating to a new patch
Replace `tree-standard.json` / `tree-ruthless.json` / `sprites.json` / `assets/` by re-running
`python3 tools/prep.py <atlastree-export dir> .` against a fresh clone of atlastree-export.
