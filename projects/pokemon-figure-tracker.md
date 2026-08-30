@def title = "Pokémon Figure Tracker"
@def tags = ["project", "python", "automation", "github-actions", "scraping"]

# Pokémon Figure Tracker

~~~
<span class="section-label">Project</span>
~~~

A daily-scheduled scraper and emailer that watches a retail site for newly listed collectible figures and sends a notification before they sell out — running entirely on GitHub Actions, with no server or laptop involved.

---

## Motivation

Limited-run collectibles list and sell out fast, and checking a catalog page manually every day doesn't scale. The interesting part of this project isn't the scraping itself — it's making the whole thing run unattended and for free, with its own state tracked in version control.

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">Python</span>
  <span class="skill-badge">Requests</span>
  <span class="skill-badge">BeautifulSoup4</span>
  <span class="skill-badge">GitHub Actions</span>
  <span class="skill-badge">SMTP</span>
</div>
~~~

A GitHub Actions cron workflow runs the scraper daily, respecting the target site's `robots.txt` and a politeness delay between requests. Already-seen product codes are diffed against the previous run and committed back to the repository as state, so only genuinely new listings trigger an email — and a "silent baseline" first run avoids dumping the entire existing catalog into one notification.

---

## Results

Runs unattended, on a schedule, for free, with the workflow itself maintaining its own state via git commits.

~~~
<div class="callout-box">
  <strong>Key takeaway:</strong> Committing scraper state back to the repository turns GitHub Actions into a zero-infrastructure, idempotent cron job — no database or server needed.
</div>
~~~

[View on GitHub →](https://github.com/calbornozflores/pokemon-figure-tracker)
