"""
Minimal Franklin.jl site builder — converts source files to __site/ without Julia.
Handles: {{ insert }}, @def / +++ frontmatter, ~~~ raw HTML blocks, standard markdown.
"""

import os
import re
import shutil
import markdown as md

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = os.path.join(ROOT, "_layout")
CSS_SRC = os.path.join(ROOT, "_css")
ASSETS_SRC = os.path.join(ROOT, "_assets")
LIBS_SRC = os.path.join(ROOT, "_libs")
SITE = os.path.join(ROOT, "__site")

DEFAULTS = {
    "author": "Claudio Albornoz Flores",
    "hasmath": False,
    "hascode": False,
    "title": "Claudio's Portfolio",
}

# ── Layout helpers ────────────────────────────────────────────────────────────

def read_layout(name):
    return open(os.path.join(LAYOUT, name)).read()

def expand_inserts(html, ctx=None):
    """Recursively expand {{ insert file.html }} directives."""
    def replacer(m):
        fname = m.group(1).strip()
        try:
            inner = read_layout(fname)
            return expand_inserts(inner, ctx)
        except FileNotFoundError:
            return ""
    return re.sub(r"\{\{\s*insert\s+(\S+)\s*\}\}", replacer, html)

def expand_fills(html, ctx):
    """Replace {{ fill key }} with ctx value."""
    def replacer(m):
        key = m.group(1).strip()
        return str(ctx.get(key, ""))
    return re.sub(r"\{\{\s*fill\s+(\w+)\s*\}\}", replacer, html)

def expand_conditionals(html, ctx):
    """Resolve {{ if key }}...{{ end }} blocks."""
    def replacer(m):
        key = m.group(1).strip()
        body = m.group(2)
        return body if ctx.get(key) else ""
    return re.sub(r"\{\{\s*if\s+(\w+)\s*\}\}(.*?)\{\{\s*end\s*\}\}", replacer, html, flags=re.DOTALL)

def expand_isdef(html, ctx):
    """Resolve {{ isdef key }}...{{ end }} blocks."""
    def replacer(m):
        key = m.group(1).strip()
        body = m.group(2)
        return body if key in ctx else ""
    return re.sub(r"\{\{\s*isdef\s+(\w+)\s*\}\}(.*?)\{\{\s*end\s*\}\}", replacer, html, flags=re.DOTALL)

def render_template(html, ctx):
    html = expand_conditionals(html, ctx)
    html = expand_isdef(html, ctx)
    html = expand_inserts(html, ctx)
    html = expand_fills(html, ctx)
    # Strip any remaining {{ }} directives
    html = re.sub(r"\{\{[^}]*\}\}", "", html)
    return html

# ── Markdown / Franklin source compiler ──────────────────────────────────────

def parse_frontmatter(text):
    """Extract @def vars or +++ TOML block, return (ctx_dict, body)."""
    ctx = dict(DEFAULTS)
    lines = text.splitlines(keepends=True)
    body_start = 0

    if text.startswith("+++"):
        # TOML frontmatter
        end = text.index("+++", 3)
        block = text[3:end]
        for line in block.splitlines():
            m = re.match(r'(\w+)\s*=\s*"([^"]*)"', line)
            if m:
                ctx[m.group(1)] = m.group(2)
        body_start = end + 3
        body = text[body_start:].lstrip("\n")
    else:
        result_lines = []
        for i, line in enumerate(lines):
            m = re.match(r'@def\s+(\w+)\s*=\s*"([^"]*)"', line)
            if m:
                ctx[m.group(1)] = m.group(2)
                continue
            m2 = re.match(r'@def\s+(\w+)\s*=\s*(\S+)', line)
            if m2:
                val = m2.group(2)
                if val == "true":
                    ctx[m2.group(1)] = True
                elif val == "false":
                    ctx[m2.group(1)] = False
                continue
            result_lines.append(line)
        body = "".join(result_lines)

    return ctx, body

def franklin_to_html(body):
    """Convert Franklin markdown body to HTML, preserving ~~~ raw blocks."""
    parts = re.split(r"~~~", body)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Markdown section
            part = re.sub(r"\\tableofcontents|\\toc", "", part)
            part = re.sub(r"---+\s*\n", "<hr>\n", part)
            html_part = md.markdown(part, extensions=["extra", "tables"])
            out.append(html_part)
        else:
            # Raw HTML block
            out.append(part)
    return "\n".join(out)

def compile_md(src_path, out_dir, flat=False):
    """Compile a Franklin .md file and write to out_dir/index.html (or directly to
    out_dir if flat=True, e.g. for 404.html which GitHub Pages expects at site root)."""
    text = open(src_path).read()
    ctx, body = parse_frontmatter(text)
    content_html = franklin_to_html(body)

    # head.html already inserts body_layout.html via {{ insert body_layout.html }}
    # so we only need head + content (placed after sidebar) + foot
    head = render_template(read_layout("head.html"), ctx)
    foot = render_template(read_layout("foot.html"), ctx)

    full = (
        head
        + f'\n<div class="franklin-content">\n{content_html}\n</div>\n'
        + foot
    )

    if flat:
        os.makedirs(os.path.dirname(out_dir), exist_ok=True)
        open(out_dir, "w").write(full)
        print(f"  compiled  {src_path} → {out_dir}")
        return

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    open(out_path, "w").write(full)
    print(f"  compiled  {src_path} → {out_path}")

def compile_html(src_path, out_path, ctx=None):
    """Expand a raw HTML template and write to out_path."""
    text = open(src_path).read()
    c = dict(DEFAULTS)
    if ctx:
        c.update(ctx)
    full = render_template(text, c)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w").write(full)
    print(f"  compiled  {src_path} → {out_path}")

# ── CSS sync ─────────────────────────────────────────────────────────────────

def sync_css():
    dst = os.path.join(SITE, "css")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(CSS_SRC):
        src = os.path.join(CSS_SRC, f)
        shutil.copy2(src, os.path.join(dst, f))
        print(f"  copied    {src} → {dst}/{f}")

def sync_dir(src_root, dst_root, label):
    """Mirror src_root into dst_root exactly (removes anything stale in dst_root)."""
    if os.path.exists(dst_root):
        shutil.rmtree(dst_root)
    shutil.copytree(src_root, dst_root)
    print(f"  synced    {src_root} → {dst_root} ({label})")

def sync_assets():
    """Mirror the static files under _assets/ that pages actually reference (favicon,
    hamburger icon, and site images) into __site/assets/ — removes stale/orphaned images."""
    dst = os.path.join(SITE, "assets")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    for f in ("favicon.ico", "hamburger.svg"):
        shutil.copy2(os.path.join(ASSETS_SRC, f), os.path.join(dst, f))
    shutil.copytree(os.path.join(ASSETS_SRC, "minimal-mistakes"), os.path.join(dst, "minimal-mistakes"))
    print(f"  synced    {ASSETS_SRC} → {dst} (site images/icons)")

def sync_libs():
    sync_dir(LIBS_SRC, os.path.join(SITE, "libs"), "vendored JS/CSS libs")

# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Building site...")

    sync_css()
    sync_assets()
    sync_libs()

    compile_html(
        os.path.join(ROOT, "index.html"),
        os.path.join(SITE, "index.html"),
    )
    compile_html(
        os.path.join(ROOT, "experience.html"),
        os.path.join(SITE, "experience", "index.html"),
    )

    compile_md(os.path.join(ROOT, "404.md"), os.path.join(SITE, "404.html"), flat=True)
    compile_md(os.path.join(ROOT, "about.md"), os.path.join(SITE, "about"))

    print("\nDone.")
