@def title = "Earth Trip Visualizer"
@def tags = ["project", "python", "pyqt6", "numpy", "visualization"]

# Earth Trip Visualizer

~~~
<span class="section-label">Project</span>
~~~

A PyQt6 desktop app that turns a list of cities and transport modes into a cinematic 9:16 fly-through video of the route on a 3D globe — the kind of clip you'd post to Instagram Stories or TikTok after a trip.

---

## Motivation

Sharing a trip usually means a map screenshot or a slideshow. I wanted something closer to the sweeping "camera flies across the Earth" shots from documentaries, generated automatically from just a list of cities — without dragging in a heavyweight geospatial stack.

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">Python</span>
  <span class="skill-badge">PyQt6</span>
  <span class="skill-badge">NumPy</span>
  <span class="skill-badge">Pillow</span>
  <span class="skill-badge">geopy</span>
  <span class="skill-badge">ffmpeg</span>
</div>
~~~

No Cartopy, no matplotlib. The 3D globe is a from-scratch orthographic projection built on plain numpy — camera basis vectors, great-circle slerp for the flight path (correct across antimeridian crossings), and a log-space perceptually-uniform zoom easing curve. At high zoom the renderer swaps the equirectangular world texture for reprojected satellite tiles. Cities are geocoded with Nominatim, and the final frames are encoded to MP4 with ffmpeg.

---

## Results

A single command turns a short itinerary into a rendered video — roughly 30 seconds of render time for a two-city trip at around 100ms/frame on Apple Silicon.

~~~
<div class="callout-box">
  <strong>Key takeaway:</strong> A correct orthographic projection and a well-chosen easing curve for zoom go a long way — the "cinematic" feel comes almost entirely from camera motion, not from texture fidelity.
</div>
~~~

[View on GitHub →](https://github.com/calbornozflores/earth-trip-visualizer)
