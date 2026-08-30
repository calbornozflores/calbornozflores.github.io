@def title = "Speed Reader"
@def tags = ["project", "javascript", "html", "no-build"]

# Speed Reader

~~~
<span class="section-label">Project</span>
~~~

A browser-based RSVP (rapid serial visual presentation) speed reader that displays text one word at a time at a configurable pace, with support for pasted text, `.txt`, `.epub`, and `.rtf` files — and zero build tooling or framework dependencies.

---

## Motivation

I wanted to read faster without installing another app, so the constraint became the interesting part: could a fully-featured reader — including file parsing for formats like EPUB — run as a single static HTML page with no backend and no npm install?

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">JavaScript</span>
  <span class="skill-badge">HTML / CSS</span>
  <span class="skill-badge">IndexedDB</span>
  <span class="skill-badge">Ollama (optional)</span>
</div>
~~~

EPUB files are unzipped with the browser's native `DecompressionStream`, and RTF is parsed by hand — no vendored libraries for either. Reading position and history are kept in IndexedDB so a session can resume later. An optional local-AI mode connects to a locally-running Ollama model for incremental "summary so far" and "characters so far" prompts, feeding only the newly-read delta each time rather than re-summarizing from the start — with no calls to any cloud service.

---

## Results

Runs entirely by opening `index.html` — no server, no dependencies, and the AI features work fully offline against a local model.

~~~
<div class="callout-box">
  <strong>Key takeaway:</strong> Modern browser APIs (native decompression, IndexedDB) remove the need for a build step or vendored libraries even for tasks — like EPUB parsing — that usually reach for a package.
</div>
~~~

[View on GitHub →](https://github.com/calbornozflores/speed-reader)
