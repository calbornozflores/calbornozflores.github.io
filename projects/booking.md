@def title = "Booking Booking"
@def tags = ["project", "booking", "python", "scraping"]

# Booking Booking

~~~
<span class="section-label">Project</span>
~~~

A Python web scraper to automatically search, filter, and compare hotel prices on Booking.com — built out of frustration with how much time manual price hunting takes.

---

## Motivation

Booking trips in South America means sifting through hundreds of options with constantly shifting prices. I wanted a tool that would do that work automatically: check a city, apply filters (price range, rating, distance from centre), and surface only the options worth looking at — without me having to open a browser.

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">Python</span>
  <span class="skill-badge">BeautifulSoup</span>
  <span class="skill-badge">Requests</span>
  <span class="skill-badge">Pandas</span>
</div>
~~~

The scraper sends structured requests to Booking.com, parses the HTML response to extract hotel name, price, rating, and location, and returns a ranked table of results. Parameters (city, dates, filters) are configurable so the same script works for any trip.

---

## Results

A clean CLI tool that replaces 20 minutes of tab-switching with a single command. Running it across a few trips to Buenos Aires and Lima surfaced deals that weren't obvious from the default search ordering — usually because Booking's default sort prioritises sponsored listings.

~~~
<div class="callout-box">
  <strong>Key takeaway:</strong> Booking's default sort is not optimal for the traveller. Sorting by price-to-rating ratio consistently surfaced better value options.
</div>
~~~

[View on GitHub →](https://github.com/calbornozflores/booking-booking)
