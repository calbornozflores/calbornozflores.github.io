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
├── gallery.html           Pokémon gallery page
├── pokeball.html          Standalone pokeball + audio page
├── about.md               About Me page (Franklin markdown)
├── experience.md          Resume page (Franklin markdown)
├── projects/
│   ├── booking.md         Booking Booking project page
│   ├── youtube.md         Investing x YouTube project page
│   └── dphi.md            DPhi Changemaker project page
├── _layout/               HTML layout templates (Franklin partials)
│   ├── head.html          Page <head> + inserts body_layout.html
│   ├── body_layout.html   Sidebar with author profile; opens #main div
│   ├── masthead.html      Top nav bar (Home / About Me / Resume / Pokeball)
│   ├── foot.html          Closes #main, footer with social links + scripts
│   └── style.html         CSS link tags (franklin.css, minimal-mistakes.css, adjust.css)
├── _css/
│   ├── adjust.css         ALL custom styles — accent color, timeline, skill badges,
│   │                      callout boxes, stat chips, hero CTA, awards
│   ├── minimal-mistakes.css  Theme CSS (do not edit)
│   ├── franklin.css       Franklin default CSS (do not edit)
│   └── pokeball_pure.css  Pokeball animation (used only on index.html, gallery.html, pokeball.html)
├── _assets/
│   ├── minimal-mistakes/  Site images (profile.png, home-page.jpg, project card images)
│   └── scripts/
│       └── build_site.py  Python build script (replaces Julia/Franklin)
├── poke_gallery/
│   ├── script/gallery.js  Dynamically generates the gallery from a hardcoded image list
│   └── images/            800+ Pokémon figure photos
├── music/                 Pokemon audio files (Title Screen.mp3, Item Obtained.mp3)
├── __site/                Compiled static output — this is what gh-pages serves
├── Project.toml           Julia dependencies (Franklin.jl, NodeJS.jl)
└── Manifest.toml          Julia lockfile
```

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

- Copies `_css/` → `__site/css/`
- Expands `{{ insert file.html }}`, `{{ fill key }}`, `{{ if key }}...{{ end }}` directives in HTML templates
- Compiles Franklin markdown (`.md`) files:
  - Strips `@def` / `+++` frontmatter
  - Converts `~~~...~~~` raw HTML passthrough blocks
  - Converts standard markdown to HTML
  - Wraps content in `head.html` + `foot.html` (which already includes `body_layout.html` via `{{ insert }}`)
- Writes output to `__site/`

**Important:** `head.html` already inserts `body_layout.html` via `{{ insert body_layout.html }}`. Do NOT pass body_layout separately when building — it will render twice (double sidebar bug).

---

## Custom CSS (`_css/adjust.css`)

All visual customisation lives here. Key components:

| Class | Purpose |
|---|---|
| `--accent` (#e63946) | CSS custom property — red accent used throughout |
| `.btn--primary` | Overridden to use `--accent` |
| `.timeline` / `.timeline-item` | Red left-border job timeline on Resume page |
| `.skill-badge` | Pill-shaped tech tag |
| `.skill-group` / `.skill-group-label` | Badge group with uppercase label |
| `.callout-box` | Left-border highlighted box |
| `.stat-chip` | Dark chip with large red number (used on About page) |
| `.award-item` / `.award-year` | Award row with red year label |
| `.section-label` | Small red uppercase section header |
| `.hero-cta` | CTA button row in homepage hero |

---

## Page notes

### `index.html` and `gallery.html`
Raw HTML files processed by the build script's `compile_html()`. They include their own pokeball loader (`<div class="loader-wrapper">`) and jQuery fade-out. The `pokeball_pure.css` stylesheet is linked directly in these files.

### Markdown pages (`about.md`, `experience.md`, `projects/*.md`)
Compiled via `compile_md()`. Raw HTML blocks are embedded with `~~~...~~~`. The masthead does **not** include a pokeball loader — removing it fixed a double-pokeball and white-space bug caused by `pokeball_pure.css` `.container` being `100vh`.

### `pokeball.html`
Standalone page with CSS-only pokeball animation and autoplay Pokemon music. Not part of the Franklin template system.

### `poke_gallery/script/gallery.js`
Generates `<div class="feature__item">` cards dynamically from a hardcoded list of ~800 image filenames. Uses `lazysizes` for lazy loading.

---

## Known state (June 2026)

- Julia / Franklin not installed locally — Python build script is the only build path
- `__site/` is committed to the repo and pushed to `gh-pages` for deployment
- Project detail pages (`booking.md`, `youtube.md`, `dphi.md`) have been filled with content (were previously empty templates)
- Gallery page (`gallery.html`) compiles correctly but gallery images are only visible if `poke_gallery/images/` assets exist on the server
