# CLAUDE.md — calbornozflores.github.io

Personal portfolio and data science website for Claudio Albornoz Flores.

---

## Stack

| Layer | Tool |
|---|---|
| Static site generator | [Franklin.jl](https://github.com/tlienart/Franklin.jl) (Julia) |
| Theme | Minimal Mistakes v4.16.4 (adapted from Jekyll) |
| Hosting | GitHub Pages — served from the `gh-pages` branch |
| Build (Julia unavailable) | `_assets/scripts/build_site.py` (Python 3) |

**Julia is not currently installed.** All builds use the Python build script instead of Franklin's native `serve()` / `optimize()`.

---

## Repo layout

```
/                          Source files (main branch)
├── index.html             Homepage — static HTML with Franklin {{ insert }} directives
├── about.md               About Me page (Franklin markdown)
├── experience.md          Resume page (Franklin markdown) — kept in sync with cv/refined-modern/main.tex
├── 404.md                 404 page (Franklin markdown, compiled flat to __site/404.html)
├── projects/
│   ├── earth-trip-visualizer.md   Earth Trip Visualizer project page
│   ├── poke-dojo.md               Poke Dojo project page (live demo: poke-dojo.fly.dev)
│   ├── pokemon-figure-tracker.md  Pokémon Figure Tracker project page
│   └── speed-reader.md            Speed Reader project page (live demo: calbornozflores.github.io/speed-reader)
├── _layout/               HTML layout templates (Franklin partials)
│   ├── head.html          Page <head> + inserts body_layout.html
│   ├── body_layout.html   Sidebar with author profile; opens #main div
│   ├── masthead.html      Top nav bar (Home / About Me / Resume)
│   ├── foot.html          Closes #main, footer with social links + scripts
│   └── style.html         CSS link tags (franklin.css, minimal-mistakes.css, adjust.css)
├── _css/
│   ├── adjust.css         ALL custom styles — accent color, timeline, skill badges,
│   │                      callout boxes, stat chips, hero CTA, awards, project-card
│   │                      hover states, tech-tag chips, live-demo button
│   ├── minimal-mistakes.css  Theme CSS (do not edit)
│   └── franklin.css       Franklin default CSS (do not edit)
├── _assets/
│   ├── minimal-mistakes/  Site images: profile.png, home-page.jpg, spark-summit.jpeg,
│   │                      and per-project SVG card banners (earth-trip-visualizer.svg,
│   │                      poke-dojo.svg, pokemon-figure-tracker.svg, speed-reader.svg)
│   └── scripts/
│       └── build_site.py  Python build script (replaces Julia/Franklin)
├── _libs/                 Vendored JS/CSS (highlight.js, KaTeX, minimal-mistakes main.min.js)
├── __site/                Compiled static output — this is what gh-pages serves
├── Project.toml           Julia dependencies (Franklin.jl, NodeJS.jl)
└── Manifest.toml          Julia lockfile
```

**No Pokémon branding remains on the site** (removed August 2026 in favor of a fully professional presentation): the pokeball loader, `gallery.html`, `pokeball.html`, `poke_gallery/`, and `music/` were all deleted. `file-vault`, `ymca-swim-booker`, `pdf-sentence-replace`, and `face-guard` are deliberately **not** featured as projects (the first two are meant to stay private; the latter two have private GitHub repos).

---

## Deployment flow

The live site at `calbornozflores.github.io` is served from the **`gh-pages` branch**, which contains the contents of `__site/`. The `main` branch holds the source.

**To deploy changes:**

```bash
# 1. Edit source files on main branch
# 2. Rebuild __site/
python3 _assets/scripts/build_site.py

# 3. Commit everything to main
git add .
git commit -m "describe changes"
git push origin main

# 4. Push __site/ contents to gh-pages
git subtree push --prefix __site origin gh-pages
```

GitHub Pages typically takes 30–60 seconds to reflect the push.

---

## Build script (`_assets/scripts/build_site.py`)

Handles what Franklin.jl would normally do:

- `sync_css()` — mirrors `_css/` → `__site/css/` (clears the destination first, so removed CSS files don't linger)
- `sync_assets()` — mirrors `_assets/favicon.ico`, `_assets/hamburger.svg`, and `_assets/minimal-mistakes/` → `__site/assets/` (clears destination first; does **not** copy `_assets/scripts/` — build tooling stays out of the public output)
- `sync_libs()` — mirrors `_libs/` → `__site/libs/` (clears destination first)
- Expands `{{ insert file.html }}`, `{{ fill key }}`, `{{ if key }}...{{ end }}` directives in HTML templates
- Compiles Franklin markdown (`.md`) files via `compile_md(src, out_dir, flat=False)`:
  - Strips `@def` / `+++` frontmatter
  - Converts `~~~...~~~` raw HTML passthrough blocks
  - Converts standard markdown to HTML
  - Wraps content in `head.html` + `foot.html` (which already includes `body_layout.html` via `{{ insert }}`)
  - Writes to `out_dir/index.html`, or directly to `out_dir` as a file when `flat=True` (used for `404.md` → `__site/404.html`, since GitHub Pages expects the 404 page at site root, not in a subdirectory)
- Writes output to `__site/`

**Important:** `head.html` already inserts `body_layout.html` via `{{ insert body_layout.html }}`. Do NOT pass body_layout separately when building — it will render twice (double sidebar bug).

**All three `sync_*()` functions delete their destination directory before copying.** This means `__site/css/`, `__site/assets/`, and `__site/libs/` always exactly mirror source — no stale files survive a rebuild. (Before this was added, `__site/` accumulated years of orphaned Franklin-theme demo assets and old Pokémon-era files that a rebuild never cleaned up — see git history around August 2026 for the one-time cleanup.) Anything else under `__site/` (compiled pages, `404.html`, `Project.toml`, `Manifest.toml`, `package-lock.json`, `robots.txt`, `sitemap.xml`, `feed.xml`) is **not** cleared automatically — a newly-removed source page's old output must be deleted manually (`git rm -r __site/<stale-path>`).

---

## Custom CSS (`_css/adjust.css`)

All visual customisation lives here. Key components:

| Class | Purpose |
|---|---|
| `--accent` (#e63946) | CSS custom property — red accent used throughout |
| `.btn--primary` | Overridden to use `--accent` |
| `.btn--live` | Accent-filled button for a project with an always-on live demo (Poke Dojo, Speed Reader) |
| `.timeline` / `.timeline-item` | Red left-border job timeline on Resume page |
| `.skill-badge` | Pill-shaped tech tag |
| `.skill-group` / `.skill-group-label` | Badge group with uppercase label |
| `.tech-tag` / `.tech-tag-row` | Smaller pill tags on homepage project cards |
| `.callout-box` | Left-border highlighted box |
| `.stat-chip` | Dark chip with large red number (used on About page) |
| `.award-item` / `.award-year` | Award row with red year label |
| `.section-label` | Small red uppercase section header |
| `.hero-cta` | CTA button row in homepage hero |
| `.archive__item:hover` | Hover-lift + shadow on project cards |

---

## Page notes

### `index.html`
Raw HTML processed by the build script's `compile_html()`. No loading-spinner overlay — content renders immediately (the old jQuery pokeball-fade loader was removed). Features exactly 4 project cards, each linking out to its own `projects/<slug>.md` detail page.

### Markdown pages (`about.md`, `experience.md`, `projects/*.md`, `404.md`)
Compiled via `compile_md()`. Raw HTML blocks are embedded with `~~~...~~~`.

### Keeping `experience.md` in sync
This page is a manually-maintained mirror of `cv/refined-modern/main.tex` (a separate, private project) — there is no automated sync. When the CV changes (new role, new cert, updated skills), update `experience.md`'s Profile / Experience timeline / Education / Skills / Recognitions sections to match, and update `about.md`'s "What I do" paragraph if the current-role framing changed. Do not copy the CV PDF itself into this repo.

---

## Known state (August 2026)

- Julia / Franklin not installed locally — Python build script is the only build path
- `__site/` is committed to the repo and pushed to `gh-pages` for deployment
- Site content fully reflects the CV as of the Data Engineer role at ClaroVTR (Jun 2026–present); see the "Keeping `experience.md` in sync" note above for future updates
- 4 featured projects: `earth-trip-visualizer`, `poke-dojo` (live demo), `pokemon-figure-tracker`, `speed-reader` (live demo)
