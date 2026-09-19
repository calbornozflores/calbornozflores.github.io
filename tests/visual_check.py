"""
Automated visual/layout checks for the Pipeline DAG pages (index.html, experience.html).

Run after any change to those two pages instead of eyeballing them manually:

    cd tests
    uv sync
    uv run playwright install chromium   # once, on a fresh machine
    uv run python visual_check.py

Rebuilds the site, serves __site/ locally, opens each page in headless Chromium at a
couple of viewport sizes, and checks for every visual bug already hit once:
overlapping nodes, nodes clipped vertically by their container (the homepage is also
checked horizontally — see below), text overflowing its box, a scrollbar appearing, an
unexpectedly small scale factor, and a stray white gap at the top of the page. It also
runs a real click-through at the desktop viewport (not just a layout snapshot): click a
node to open its detail panel and click close — this is what caught a real bug once (a
detail panel that opened but silently failed to close). Screenshots are saved to
tests/screenshots/ regardless of pass/fail.

Note: neither page has zoom/fit buttons anymore (wheel-zoom and drag-to-pan are still
there, just not the visible +/−/Fit cluster) — deliberately removed, so there's no
button-driven zoom check here anymore. The Experience page is also fit to the viewport's
HEIGHT only (not width), so at its default zoom the graph is normally wider than the
viewport and gets intentionally cropped on the left, anchored to show the current/most-
recent role by default (see `resetView()` in experience.html) — horizontal clipping there
is by design, not a bug, which is why the clipping check below only applies left/right
containment on the homepage.

Implementation note: the interaction click-through runs in its own fresh
sync_playwright() session per page, separate from the layout-check session above.
This isolation was added while chasing what looked like Chromium-level click
flakiness on the Experience page's "Tech Lead" node; the actual cause turned out
to be a real application bug, not a browser/driver quirk — the old detail panel
floated over the graph and could end up sitting on top of the very node whose
click opened it, so the click sometimes landed on the panel instead. That design
is gone (the detail view now renders in a plain below-graph panel, like the
homepage's project summary, so nothing can float over a node anymore), so this
per-page session isolation is likely no longer load-bearing — it's left in place
because it's harmless, not because it's still needed.
"""

import http.server
import re
import socket
import subprocess
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "__site"
SCREENSHOTS = Path(__file__).resolve().parent / "screenshots"

PAGES = ["/", "/experience/"]
VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 900},
    {"name": "laptop", "width": 1280, "height": 800},
]
# Minimum acceptable fit-to-screen scale factor per page at the desktop viewport —
# see check 5 below and CLAUDE.md's testing section for how these were chosen.
SCALE_FLOOR = {"/": 0.55, "/experience/": 0.35}

failures = []
passed = 0


def check(label, condition, detail=""):
    global passed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failures.append(f"{label} — {detail}")
        print(f"  FAIL  {label} — {detail}")


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(port):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(SITE), **kw)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def rects_overlap(a, b, tolerance=2):
    ix = min(a["right"], b["right"]) - max(a["left"], b["left"])
    iy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
    return ix > tolerance and iy > tolerance


def wait_for_layout(page):
    """Wait for the actual layout pipeline to finish, not a guessed delay.

    Root cause of a real flaky-test investigation: both pages measure node text and run
    dagre only after `document.fonts.load(...)` resolves, and that resolves over the
    network (Google Fonts). Its timing varies run to run — a fixed wait_for_timeout was
    sometimes too short on the denser Experience page (20 nodes vs. the homepage's 7),
    so a click could land before dagScale had been sized/positioned at all, silently
    missing its target with no error. `dagScale.style.width` is only set once dagre's
    layout has actually completed, so waiting on it is a real readiness signal instead
    of a number that happened to work in manual testing.
    """
    page.wait_for_function("document.getElementById('dagScale').style.width !== ''", timeout=10000)
    page.wait_for_timeout(100)  # let the resulting paint settle


def get_scale(page):
    t = page.evaluate("getComputedStyle(document.getElementById('dagScale')).transform")
    if not t or t == "none":
        return 1.0
    m = re.match(r"matrix\(([^,]+),", t)
    return float(m.group(1)) if m else 1.0


def real_click(page, selector):
    """A direct move-then-click at an element's center, like an actual pointing device —
    deliberately NOT page.click()'s locator action, which re-verifies the target is the
    top hit-test result at each retry step and has been flakier than a plain click for
    this DAG UI in practice."""
    box = page.eval_on_selector(selector, "el => { const r = el.getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2}; }")
    page.mouse.move(box["x"], box["y"])
    page.mouse.down()
    page.mouse.up()


def run_layout_checks(p, base):
    """Phase 1: pure layout/metrics snapshots — no real interaction, so this part has
    never shown the driver-session flakiness described in the module docstring."""
    for vp in VIEWPORTS:
        for path in PAGES:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            label = f"{path or '/'} @ {vp['name']} ({vp['width']}x{vp['height']})"
            print(f"\n== {label} ==")
            page.goto(base + path, wait_until="networkidle")
            wait_for_layout(page)

            shot_name = (path.strip("/") or "home") + f"-{vp['name']}.png"
            # full_page=False (i.e. a plain viewport screenshot) is deliberate, not just the
            # default: these pages are specifically designed to have no scroll, so a viewport
            # screenshot already captures everything.
            page.screenshot(path=str(SCREENSHOTS / shot_name))

            metrics = page.evaluate(
                """() => {
                const nodes = [...document.querySelectorAll('.node')].map(el => {
                    const r = el.getBoundingClientRect();
                    return {id: el.dataset.id, top: r.top, left: r.left, right: r.right, bottom: r.bottom};
                });
                const viewportEl = document.getElementById('dagViewport');
                const vr = viewportEl ? viewportEl.getBoundingClientRect() : null;
                const overflowEls = [...document.querySelectorAll('.n-id, .n-kind')]
                    .filter(el => el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)
                    .map(el => el.textContent.trim());
                const scaleEl = document.getElementById('dagScale');
                let scale = 1;
                if (scaleEl) {
                    const t = getComputedStyle(scaleEl).transform;
                    if (t && t !== 'none') {
                        const m = t.match(/matrix\\(([^,]+),/);
                        if (m) scale = parseFloat(m[1]);
                    }
                }
                const idlePlaceholder = [...document.querySelectorAll('body *')].find(el =>
                    el.children.length === 0 && /hover a node/i.test(el.textContent || '')
                );
                const idlePlaceholderVisible = idlePlaceholder
                    ? idlePlaceholder.getClientRects().length > 0 && getComputedStyle(idlePlaceholder).display !== 'none'
                    : false;
                return {
                    scrollW: document.documentElement.scrollWidth,
                    scrollH: document.documentElement.scrollHeight,
                    innerW: window.innerWidth,
                    innerH: window.innerHeight,
                    nodes,
                    viewportRect: vr ? {top: vr.top, left: vr.left, right: vr.right, bottom: vr.bottom} : null,
                    overflowEls,
                    scale,
                    idlePlaceholderVisible
                };
            }"""
            )

            # 1. no scrollbar
            check(
                f"{label}: no horizontal scrollbar",
                metrics["scrollW"] <= metrics["innerW"] + 1,
                f"scrollWidth={metrics['scrollW']} > innerWidth={metrics['innerW']}",
            )
            check(
                f"{label}: no vertical scrollbar",
                metrics["scrollH"] <= metrics["innerH"] + 1,
                f"scrollHeight={metrics['scrollH']} > innerHeight={metrics['innerH']}",
            )

            # 2. no overlapping nodes
            nodes = metrics["nodes"]
            overlaps = [
                (nodes[i]["id"], nodes[j]["id"])
                for i in range(len(nodes))
                for j in range(i + 1, len(nodes))
                if rects_overlap(nodes[i], nodes[j])
            ]
            check(f"{label}: no overlapping nodes ({len(nodes)} nodes)", not overlaps, f"overlaps: {overlaps}")

            # 3. every node vertically inside the dag viewport (not clipped/crowded top-to-
            # bottom on either page). Horizontal containment is only required on the homepage
            # — the Experience page is fit to height only and its default view is deliberately
            # cropped left/right (see the module docstring), so a node past either side edge
            # there is expected, not a bug.
            if metrics["viewportRect"]:
                vr = metrics["viewportRect"]
                clipped = [
                    n["id"]
                    for n in nodes
                    if n["top"] < vr["top"] - 1
                    or n["bottom"] > vr["bottom"] + 1
                    or (path == "/" and (n["left"] < vr["left"] - 1 or n["right"] > vr["right"] + 1))
                ]
                check(f"{label}: no node clipped by its container", not clipped, f"clipped: {clipped}")

            # 4. no text overflowing its box
            check(
                f"{label}: no node text overflow",
                not metrics["overflowEls"],
                f"overflowing: {metrics['overflowEls']}",
            )

            # 5. neither graph should be shrunk more than necessary on a normal desktop
            # viewport. Threshold is a judgment call, re-calibrated by looking at the actual
            # screenshot each time it's touched — see CLAUDE.md's testing section.
            if vp["name"] == "desktop":
                min_scale = SCALE_FLOOR[path]
                check(
                    f"{label}: graph not overly compressed",
                    metrics["scale"] >= min_scale,
                    f"scale factor={metrics['scale']:.2f} < floor {min_scale}",
                )

            # 6. no idle "Hover a node..." placeholder pill visible on load
            check(
                f"{label}: no idle hover-placeholder pill visible",
                not metrics["idlePlaceholderVisible"],
                "found a visible element containing 'hover a node' with no interaction yet",
            )

            # 7. no white gap at the very top of the page (sample the top edge)
            from PIL import Image

            img = Image.open(SCREENSHOTS / shot_name)
            samples = [img.getpixel((x, 2)) for x in (5, img.width // 2, img.width - 5)]
            white_like = [s for s in samples if sum(s[:3]) > 650]
            check(
                f"{label}: no white gap at top of page",
                not white_like,
                f"top-edge pixel samples={samples}",
            )

            page.close()
            browser.close()


def run_interaction_smoke_test(page, path, label):
    """A real click-through, not just a layout snapshot — this is exactly the kind of thing
    a static check can't catch: a panel that opens on click but silently fails to close
    (hit once, from a floating detail panel that could intercept its own close button)."""
    default_scale = get_scale(page)

    # There's no zoom button anymore (deliberately removed) — exercise the mouse-wheel path
    # instead, which is now the only way to zoom. One wheel event over the viewport, then the
    # exact opposite, should zoom in and then return acceptably close to the original scale.
    box = page.eval_on_selector(
        "#dagViewport", "el => { const r = el.getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2}; }"
    )
    page.mouse.move(box["x"], box["y"])
    page.mouse.wheel(0, -300)
    page.wait_for_timeout(120)
    zoomed_scale = get_scale(page)
    check(f"{label}: wheel zoom-in changes scale", zoomed_scale > default_scale, f"{zoomed_scale} <= {default_scale}")
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(120)
    check(
        f"{label}: wheel zoom-out returns close to original scale",
        abs(get_scale(page) - default_scale) < 0.02,
        f"got {get_scale(page)}, expected ~{default_scale}",
    )

    if path == "/":
        # poke_dojo now lives inside the collapsed `entertainment` group, so the group
        # has to be opened before the node it holds even exists in the DOM.
        check(
            f"{label}: grouped nodes are hidden until the group is expanded",
            page.query_selector("#n-poke") is None and page.query_selector("#n-pgol") is None,
            "grouped nodes rendered while collapsed",
        )
        real_click(page, "#n-entertainment")
        page.wait_for_selector("#n-poke", timeout=3000)
        check(
            f"{label}: expanding the group reveals its projects",
            all(page.query_selector(sel) for sel in ("#n-poke", "#n-poke_web", "#n-pgol")),
            "expanded group is missing children",
        )

        # The expanded graph is the widest the homepage ever gets, and the layout pass
        # only ever runs its checks against the collapsed default.
        exp_rects = page.eval_on_selector_all(
            ".node", "els => els.map(e => { const r = e.getBoundingClientRect(); return [e.dataset.id, r.left, r.top, r.right, r.bottom]; })"
        )
        overlaps = [
            (a[0], b[0])
            for i, a in enumerate(exp_rects)
            for b in exp_rects[i + 1:]
            if rects_overlap(
                {"left": a[1], "top": a[2], "right": a[3], "bottom": a[4]},
                {"left": b[1], "top": b[2], "right": b[3], "bottom": b[4]},
            )
        ]
        check(f"{label}: expanded graph has no overlapping nodes", not overlaps, f"overlapping: {overlaps}")
        vp = page.eval_on_selector(
            "#dagViewport", "el => { const r = el.getBoundingClientRect(); return {left: r.left, right: r.right}; }"
        )
        outside = [r[0] for r in exp_rects if r[1] < vp["left"] - 2 or r[3] > vp["right"] + 2]
        check(f"{label}: expanded graph stays inside the viewport", not outside, f"outside: {outside}")
        expanded_scale = get_scale(page)
        check(
            f"{label}: expanded graph stays above the scale floor",
            expanded_scale >= SCALE_FLOOR["/"],
            f"{expanded_scale} < {SCALE_FLOOR['/']}",
        )

        node_id, close_selector, expect_text = "#n-poke", "#closeSummary", "Poke Dojo"
        panel_selector = ".summary"
    else:
        node_id, close_selector, expect_text = "#n-tech_lead", "#closeDetail", "Data Science Tech Lead"
        panel_selector = ".detail-card"

    real_click(page, node_id)
    page.wait_for_timeout(200)
    check(f"{label}: click opens the detail/summary panel", page.is_visible(panel_selector), "panel not visible after click")
    check(
        f"{label}: panel shows the right content",
        expect_text in (page.inner_text(panel_selector) if page.is_visible(panel_selector) else ""),
        f"expected {expect_text!r} in panel text",
    )
    if page.is_visible(panel_selector):
        real_click(page, close_selector)
        page.wait_for_timeout(150)
        check(f"{label}: close button actually closes the panel", not page.is_visible(panel_selector), "panel still visible after closing")
    else:
        check(f"{label}: close button actually closes the panel", False, "skipped — panel never opened")

    if path == "/":
        # Re-collapsing has to remove the children again, and must not leave a pinned
        # panel behind for a node that is no longer on screen.
        real_click(page, "#n-pgol")
        page.wait_for_timeout(200)
        real_click(page, "#n-entertainment")
        page.wait_for_timeout(300)
        check(
            f"{label}: collapsing the group hides its projects again",
            page.query_selector("#n-poke") is None and page.query_selector("#n-pgol") is None,
            "grouped nodes still rendered after collapsing",
        )
        check(
            f"{label}: collapsing closes a panel pinned to a hidden node",
            not page.is_visible(".summary"),
            "summary panel outlived the node that opened it",
        )
        # Laying out twice must land in exactly the same place; measuring node boxes
        # through #dagScale's transform used to make the graph drift on every toggle.
        first = page.eval_on_selector("#dagScale", "el => el.style.width")
        real_click(page, "#n-entertainment")
        page.wait_for_timeout(250)
        real_click(page, "#n-entertainment")
        page.wait_for_timeout(250)
        check(
            f"{label}: re-layout is idempotent",
            page.eval_on_selector("#dagScale", "el => el.style.width") == first,
            f"graph width drifted from {first}",
        )


def run_interaction_checks(base):
    """Phase 2: real click-throughs, desktop viewport only. Each page gets its own fresh
    sync_playwright() session — see the module docstring for why that isolation matters."""
    vp = VIEWPORTS[0]
    for path in PAGES:
        label = f"{path or '/'} @ {vp['name']} ({vp['width']}x{vp['height']})"
        print(f"\n== {label} — interaction ==")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            page.goto(base + path, wait_until="networkidle")
            wait_for_layout(page)
            run_interaction_smoke_test(page, path, label)
            page.close()
            browser.close()


def main():
    print("Rebuilding site...")
    # build_site.py needs `markdown`, which this test venv also declares as a dependency
    # (via pyproject.toml) precisely so this call is self-contained.
    subprocess.run([sys.executable, str(ROOT / "_assets/scripts/build_site.py")], check=True, cwd=ROOT)

    port = free_port()
    httpd = start_server(port)
    base = f"http://127.0.0.1:{port}"
    SCREENSHOTS.mkdir(exist_ok=True)

    try:
        with sync_playwright() as p:
            run_layout_checks(p, base)
        run_interaction_checks(base)
    finally:
        httpd.shutdown()

    print(f"\n{passed} passed, {len(failures)} failed.")
    print(f"Screenshots saved to {SCREENSHOTS}")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
