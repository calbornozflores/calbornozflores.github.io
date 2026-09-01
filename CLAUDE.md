# CLAUDE.md — calbornozflores.github.io

Personal portfolio and data science website for Claudio Albornoz Flores.

---

## Stack

| Layer | Tool |
|---|---|
| Static site generator | [Franklin.jl](https://github.com/tlienart/Franklin.jl) (Julia) |
| Theme | Minimal Mistakes v4.16.4 (adapted from Jekyll) — used only for the shared nav/social-icon CSS classes; the homepage and Experience page are otherwise fully custom |
| Hosting | GitHub Pages — served from the `gh-pages` branch |
| Build (Julia unavailable) | `_assets/scripts/build_site.py` (Python 3) |

**Julia is not currently installed.** All builds use the Python build script instead of Franklin's native `serve()` / `optimize()`.

---

## Repo layout

```
/                          Source files (main branch)
├── index.html             Homepage — "The Pipeline": the site as an Airflow-style DAG
├── experience.html        Experience page — a career DAG (jobs + education/certs/recognitions)
├── about.md               About Me page (Franklin markdown)
├── 404.md                 404 page (Franklin markdown, compiled flat to __site/404.html)
├── _layout/               HTML layout templates (Franklin partials)
│   ├── head.html          Page <head> + inserts body_layout.html (used by about.md/404.md only)
│   ├── body_layout.html   Sidebar with author profile; opens #main div
│   ├── masthead.html      Top bar wrapping nav_sandwich.html — used by about.md/404.md only
│   ├── nav_sandwich.html  The hamburger menu itself (icon + Projects/Experience dropdown + toggle
│   │                      script) — a shared partial inserted three ways: wrapped in masthead.html's
│   │                      bar for About/404, and directly inline next to the page title on
│   │                      index.html/experience.html. About Me is not one of its links (the About
│   │                      page itself is untouched and still live at /about/, just not in nav).
│   ├── foot.html          Closes #main, footer with social links + scripts — used by about.md/404.md
│   ├── foot_scripts.html  Just the minimal-mistakes JS include — used by index.html/experience.html,
│   │                      which hand-write their own dark-themed footer instead of foot.html's
│   │                      light-themed one
│   └── style.html         CSS link tags (franklin.css, minimal-mistakes.css, adjust.css)
├── _css/
│   ├── adjust.css         About-page component styles — stat chips, callout boxes, section labels —
│   │                      plus the light-theme `.nav-sandwich` dropdown styles (masthead usage)
│   ├── pipeline.css       Everything for index.html/experience.html: DAG nodes/edges, the pinned
│   │                      project-summary panel, the Experience page's below-graph `.detail-card`,
│   │                      the contact strip, the career-graph legend, and the dark-theme
│   │                      `.nav-sandwich` dropdown styles (inline usage). Also sets
│   │                      `html{background:var(--bg)}`, overriding minimal-mistakes.css's global
│   │                      `html{background:#fff}` — without this a white sliver can show at the
│   │                      top/edges of these two dark pages.
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
├── tests/                 Automated visual/layout checks for index.html/experience.html —
│   │                      NOT part of the deployed site, uv-managed, see "Testing" below
│   ├── pyproject.toml
│   └── visual_check.py
├── Project.toml           Julia dependencies (Franklin.jl, NodeJS.jl)
└── Manifest.toml          Julia lockfile
```

**No Pokémon branding remains on the site** (removed August 2026). `file-vault`, `ymca-swim-booker`, `pdf-sentence-replace`, and `face-guard` are deliberately **not** featured as projects (the first two are meant to stay private; the latter two have private GitHub repos).

**There are no standalone project detail pages anymore** (`projects/*.md` were retired August 2026). Project write-ups now live entirely in `index.html`'s `PROJECTS` object and render as an in-page pinned summary panel — see "The Pipeline" below.

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

- `sync_css()` — mirrors `_css/` → `__site/css/` (clears destination first)
- `sync_assets()` — mirrors `_assets/favicon.ico`, `_assets/hamburger.svg`, and `_assets/minimal-mistakes/` → `__site/assets/` (clears destination first; does **not** copy `_assets/scripts/`)
- `sync_libs()` — mirrors `_libs/` → `__site/libs/` (clears destination first)
- `compile_html(src, out_path)` — expands `{{ insert }}`/`{{ fill }}`/`{{ if }}` directives only, no markdown conversion. Used for `index.html` → `__site/index.html` and `experience.html` → `__site/experience/index.html`.
- `compile_md(src, out_dir, flat=False)` — Franklin markdown compiler (frontmatter, `~~~` raw HTML blocks, markdown→HTML, wrapped in `head.html`+`foot.html`). Used for `about.md` and `404.md` (with `flat=True`, writing directly to `__site/404.html` since GitHub Pages expects it at site root).

**All three `sync_*()` functions delete their destination directory before copying** — `__site/css/`, `__site/assets/`, and `__site/libs/` always exactly mirror source, no stale files survive a rebuild. Anything else under `__site/` (compiled pages, `Project.toml`, `Manifest.toml`, `robots.txt`, etc.) is **not** cleared automatically — a removed source page's old output must be deleted manually (`git rm -r __site/<stale-path>`).

---

## "The Pipeline" — the homepage and Experience-page architecture (`index.html`, `experience.html`, `_css/pipeline.css`)

Both pages render a graph — edges as SVG `<path>`s, nodes as absolutely-positioned `.node` divs — sharing one dark navy/cyan palette (`--bg:#0b0f19; --panel:#131a2b; --line:#263252; --cyan:#3ddbd9; --good:#4caf7d; --gold:#e8b84b`) defined in `pipeline.css`. **Node positions are computed by `dagre`** (loaded from cdnjs, `dagre.graphlib.Graph` + `dagre.layout()`) — the same class of layered-graph algorithm Airflow's own graph view uses — not hand-picked coordinates. Hand-picked coordinates were tried first and caused a real overlap bug (two nodes landed on top of each other); dagre makes that structurally impossible given accurate node sizes.

**Layout pattern, in two passes (both pages, identical structure):**
1. **Measure**: create every `.node` div with its real content, append to the DOM with no position set, then read `getBoundingClientRect()` to get its *actual* rendered width/height. Nodes never wrap (`.node{white-space:nowrap}` in `pipeline.css`), so this is an exact size, not an estimate — an earlier version estimated width from character-counting the label alone, which under-counted nodes whose *second* line (the date/kind text) was longer than the title, and that mismatch between assumed and real size is what caused nodes to overlap once the real content rendered.
2. **Layout**: feed those exact measured sizes into `dagre.setNode(id, {width, height})`, run `dagre.layout()`, then apply the returned `{x, y}` (rank/column-based, not calendar-date-based — dagre doesn't know what a date is, it only knows the edge graph) to each node's `left`/`top`.

This whole two-pass process is wrapped in `Promise.all([document.fonts.load(...)]).then(...)` in both files — measuring before the real web font (IBM Plex Mono) has loaded would measure against the fallback font's metrics and produce sizes that don't match what's on screen a moment later.

**Fit-to-screen has diverged between the two pages** — they used to share identical `computeFit()`/`resetView()` code, but no longer do, because their graphs have fundamentally different shapes:

- **`index.html`** (7 nodes, roughly as tall as it is wide): `computeFit()` fits **both** width and height (`fitZoom = min(availW/naturalW, availH/naturalH, 1)`), so the whole graph is always visible with no cropping — the original, simpler model. `resetView()` centers it (`panX`/`panY` from leftover space on each axis, not zeroed) whenever it's smaller than the viewport on either axis.
- **`experience.html`** (20 nodes, much wider than tall): `computeFit()` fits **height only** (`fitZoom = min(availH/naturalH, 1)`) — width is not part of the constraint, so the default zoom is bigger than a both-dimensions fit would ever allow. The graph is then usually wider than the viewport at that zoom, and `resetView()` deliberately anchors it to the **right edge** rather than centering: `panX = Math.min(diffX/2, diffX)` where `diffX = clientWidth - naturalW*zoom` — this picks the centered value when the graph fits (`diffX >= 0`) and the full right-alignment value when it doesn't (`diffX < 0`), in one expression. The rationale: a career timeline's most-recent/current entry (rightmost, since older→newer runs left→right) is what a visitor cares about by default; earlier history is reached by dragging or wheel-panning left. This was a deliberate, requested trade-off — a full-width breakout (letting the DAG use the whole browser window instead of the header's ~1300px column) was tried first and reverted after review: it looked inconsistent with the text above it, so the graph is capped to that same column width, and the "look bigger" goal is met by cropping (fit-to-height + right-anchor) instead of by widening the column.

Both pages still share: a small floor (140px) in `computeFit()` on the vertical space it'll assume it has, purely so `naturalH * factor` never comes out as `NaN`/negative — it does **not** protect against overflow, so it must never be raised without re-verifying via `tests/visual_check.py` that no scrollbar reappears (raising it was exactly what caused a real regression once). `resetView()` runs on initial load, on window resize, and after every pin/unpin click on both pages.

**Interaction model** (same on both pages): hovering any node calls `applyTrace(id)`, which walks the edge list both directions (`ancestors()`/`descendants()`) and adds `.lit`/`.dim` to every node and edge — a general "trace the dependency chain" pattern, not literal DAG execution. There is no idle-state description panel on either page — the trace highlight is the only hover feedback; a description only appears once something is actually clicked (the homepage's `.summary` card, the Experience page's `.detail-card`, both below the graph in `#belowGraph`).

### Pan, zoom, and the removal of the log panel

Both pages originally reserved permanent vertical space for a `#log` panel showing an idle-state placeholder ("Hover a node to inspect it.") plus a one-line hover description — this shrank the space `computeFit()` had to work with and made both graphs harder to read than necessary. It's gone from both pages now:

- **`index.html`**: `#log` was deleted outright. The trace highlight on hover is feedback enough; the `.summary` card (which only appears on click) already explains itself and is a deliberate content reveal, not idle chrome.
- **`experience.html`**: the old in-flow log panel became a `.detail-card` rendered into `#detailSlot` inside `#belowGraph` on click only (same below-graph placement and pattern as the homepage's `.summary`) — there is no hover preview and no floating overlay (an earlier floating-overlay design was replaced with this below-graph card after it caused a real bug: the overlay could end up sitting on top of the very node whose click opened it).

Reclaiming that space (plus trimming header/subtitle margins) let `computeFit()`'s available-height number go up, directly raising the default scale factor on both graphs.

**Pan and zoom** were added on top of the existing `transform: scale(...)` on `#dagScale`, extended to `translate(panX, panY) scale(zoom)`. Mouse wheel zooms in/out centered on the cursor (standard "keep the point under the cursor fixed" math), clamped to `ZOOM_MIN_MULT`/`ZOOM_MAX_MULT` (0.5×–3.5× of `fitZoom`); click-and-drag pans (`.dag-viewport` keeps `overflow:hidden`, so panning never produces a page scrollbar). **There are no visible zoom buttons** (a `−`/`Fit`/`+` cluster existed briefly and was removed at the user's request — wheel-zoom and drag-pan are the only ways to zoom/pan now) and no way to explicitly "reset" other than reloading or resizing the window, since `resetView()` runs on both of those. On window resize, `computeFit()`/`resetView()` recompute the baseline and snap back to it rather than trying to preserve an arbitrary zoom/pan state.


### `index.html`
- Root node `you` → two stage nodes (`foundations`, `ml_stack`) → four project task nodes, defined in `PROJECTS` (name, image, tags, full description, links).
- **Click a project node**: toggles `pinned` and calls `renderSummary()`, which injects a `.summary` card (image, tags, full description, CTA buttons, a closing "for further details, see GitHub" line) into `#summarySlot`. Clicking the same node again, or its close button, un-pins it. The pinned state persists independently of hover — `syncPinnedNode()` re-applies the trace highlight for the pinned node on `mouseleave` so it doesn't reset. Because the summary panel changes the page's total height, both `renderSummary()` and its close handler call `resetView()` again. When a panel is newly shown (not closed), `renderSummary()` also calls `scrollToPanel()`, which smooth-scrolls it into view (`scrollIntoView({behavior:"smooth", block:"start"})`, instant instead under `prefers-reduced-motion`) — the panel usually renders below the fold, and this is the same `scrollToPanel()` helper `experience.html`'s `renderDetail()` uses for its `.detail-card`.
- **Click the `you` node**: navigates to `/experience/` (real page load, not in-page).
- Contact links (email/LinkedIn/GitHub — no phone or address) live in `.contact-strip` at the bottom.
- Dagre config: `nodesep: 34, ranksep: 96` — deliberately roomier than `experience.html`'s, since only 7 nodes need to fit; already fits at scale 1 (`fitZoom` is capped at 1 here).

### `experience.html`
- One graph, three conceptual lanes emerging from dagre's own ranking (not fixed y-coordinates): the main sequential job chain (`MAIN_EDGES`), concurrent/overlapping jobs branching off it (`PARALLEL_EDGES` — e.g. the AI Specialist stint overlapping the Tech Lead role), and education/certifications/recognitions branching off the job(s) they overlap (`ACH_EDGES`, dashed, class `.achievement`). **Edge direction convention**: for both of these, the edge points *from* the main-chain job *to* the branch (e.g. `tech_lead → ai_specialist`), which is what makes dagre place the branch at the very next rank/column and stack it vertically without overlap — pointing it the other way ranks the branch *before* its main node, which is backwards. An item overlapping two jobs (e.g. `ufro_council` spanning both Senior Data Scientist and Tech Lead) just gets two edges. See "Time rule" below for the additional `ORDER_EDGES`/`minlen` mechanisms that keep rank order chronological.
- `JOBS` and `ACHIEVEMENTS` each carry a short `label` (what's shown in the box) and the full CV text — jobs: `title`/`company`/`place`/`date`/`bullets`; achievements: `title`/`date`, optionally `place` (rendered next to `date` on the meta line) and either `bullets` (rendered as a real `<ul>`) or `desc` (rendered as a `<p>`) — all shown by `detailHTML()`. Box labels were deliberately shortened for the longest items (e.g. "Ingeniería Civil Matemática" → box says "UFRO Degree") — the full text still appears on hover/click; this is what fixed a real text-overflow bug, not a wider box guessed to compensate. Don't bury a location or a real bulleted list inside `desc` prose — that was a real bug (ACM ICPC, Spark Summit, Google Next, GCP Skills Boost all did this until fixed) — use `place`/`bullets` instead.
- **Click a node**: pins its full detail in a `.detail-card` below the graph (`#detailSlot` inside `#belowGraph`, same pin pattern and below-graph placement as the homepage's project summary) so it survives `mouseleave` — click again, or a different node, to change it.
- Dagre config: `nodesep: 18, ranksep: 40, marginx: 16` — tighter than the homepage's, since 20 nodes need to fit in a graph that's fit to height only (see "Fit-to-screen has diverged" above) — width is otherwise unbounded here, so tighter spacing directly raises the default zoom instead of just reducing how much gets cropped.

### Keeping this in sync with the CV
There is no automated sync with `cv/refined-modern/main.tex` (a separate, private project). When the CV changes:
- New/changed role → update `JOBS` in `experience.html` (and re-check whether it introduces a new time overlap requiring a parallel node/edge).
- New education/cert/recognition → add an entry to `ACHIEVEMENTS` and at least one edge in `ACH_EDGES` to whichever job(s) were active at that time.
- New project → add an entry to `PROJECTS` in `index.html`, a task node + edge in `NODES`/`EDGES`, and its SVG banner under `_assets/minimal-mistakes/`.

Do not copy the CV PDF itself into this repo. **After any change to either page, run `tests/visual_check.py`** (see "Testing" below) rather than eyeballing it — every check in that script maps to a real bug this graph has already had once.

**Time rule — nodes must render in chronological start-date order, left-to-right.** dagre only ranks by graph structure, not by date, so two nodes that just branch off the same parent(s) (same-rank siblings) have no guaranteed left-to-right order between them — don't assume it happens to match the calendar. `experience.html` handles this with two mechanisms, both defined right where `ALL_EDGES` is fed to `g.setEdge()`:
- **Sibling ordering** — add a pair to `ORDER_EDGES`, a list of layout-only hint edges fed to dagre for ranking but deliberately excluded from `ALL_EDGES`, so they're never drawn and never show up in `applyTrace()`'s ancestor/descendant walk (there's no real dependency, only a "renders after" requirement).
- **"Current/ongoing role always renders last"** — give that role's incoming edge a large `minlen` (currently `g.setEdge("tech_lead", "data_engineer", { minlen: 6 })`) comfortably exceeding the deepest branch, rather than chaining every branch leaf into it (which would need updating every time a new leaf is added elsewhere).

When adding a new job or achievement, check whether it needs an `ORDER_EDGES` entry against any existing sibling under the same parent, and if a new role becomes the current one, move the `minlen` override onto its incoming edge instead.

---

## Testing (`tests/`)

`tests/visual_check.py` is a Playwright-based script that catches the whole class of layout bugs these two DAG pages are prone to (overlap, clipping, text overflow, an unwanted scrollbar, an unexpectedly small scale factor, a stray white gap) automatically, instead of asking for a manual look after every change. It is **not part of the deployed site** — it's a dev-only tool, isolated in its own `uv`-managed `tests/pyproject.toml` (declares `playwright`, `pillow`, and `markdown` — the last one so it can invoke `build_site.py` itself without depending on whatever environment the site is normally built with).

**Setup (once, or on a fresh machine):**
```bash
cd tests
uv sync
uv run playwright install chromium
```

**Run after any change to `index.html`, `experience.html`, or `_css/pipeline.css`:**
```bash
cd tests
uv run python visual_check.py
```

It rebuilds the site, serves `__site/` locally, opens `/` and `/experience/` in headless Chromium at a couple of viewport sizes, runs the checks, saves screenshots to `tests/screenshots/` regardless of pass/fail, and exits non-zero if anything fails (with the specific failure printed). Read the screenshots directly for anything the checks don't cover — they're the fastest way to actually see what changed.

The one check that's a judgment call rather than a hard invariant is the homepage's minimum scale factor (currently `>= 0.55`) — it's calibrated against a manually-reviewed screenshot, not a law of nature. If a future change legitimately needs a lower value, look at the saved screenshot first and confirm it still reads as spacious before lowering the threshold.

---

## Known state (September 2026)

- Julia / Franklin not installed locally — Python build script is the only build path
- `__site/` is committed to the repo and pushed to `gh-pages` for deployment
- Homepage and Experience page are both dagre-laid-out "Pipeline" DAGs (see above) with pan/zoom and no idle log panel (see "Pan, zoom, and the removal of the log panel"); About page is the only remaining Franklin-markdown content page
- 5 featured projects, all summarized in-page on the homepage (no standalone project pages): `earth-trip-visualizer` (live demo — a from-scratch JS/Canvas port of the projection math, served from that repo's `docs/` on GitHub Pages since Pages can't run ffmpeg/Python; no video export, watch-only), `poke-dojo`, `poke-dojo-web` (live demo — a client-side, no-login static port of poke-dojo's game modes, chained as the next task after `poke` in `NODES`/`EDGES` since it's a follow-on to it), `pokemon-figure-tracker`, `speed-reader` (live demo). `poke-dojo` itself has no live-demo link on the site (its Fly.io hosting isn't the one linked from here) — `poke-dojo-web`'s GitHub Pages deployment is the live link for that game now.
- Nav is a hamburger ("sandwich") menu everywhere, linking only Projects (`/`) and Experience — see `_layout/nav_sandwich.html`
- `tests/visual_check.py` exists specifically because this pair of pages has already hit overlap, clipping, overflow, and scrollbar bugs once each — run it after touching either page, per "Testing" above
