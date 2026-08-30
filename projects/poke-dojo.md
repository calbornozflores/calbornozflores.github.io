@def title = "Poke Dojo"
@def tags = ["project", "python", "fastapi", "xgboost", "webapp"]

# Poke Dojo

~~~
<span class="section-label">Project</span>
~~~

A full-stack quiz web app with five game modes, a real-time Battle Arena (2-player VS and a Solo Challenge), a Daily Challenge, and a per-user machine learning model that analyses which questions are personally hardest for you.

---

## Motivation

I wanted a project that went beyond a static quiz: real-time multiplayer, persistent accounts, a global leaderboard, and enough usage data per player to make the difficulty analysis genuinely personal rather than a fixed question bank.

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">FastAPI</span>
  <span class="skill-badge">SQLAlchemy</span>
  <span class="skill-badge">XGBoost</span>
  <span class="skill-badge">Jinja2</span>
  <span class="skill-badge">Google OAuth</span>
  <span class="skill-badge">Fly.io</span>
</div>
~~~

FastAPI + SQLAlchemy back a Jinja2/vanilla-JS frontend, with SQLite locally and a Supabase Postgres database for the global leaderboard. Each player gets their own XGBoost model trained on their answer history, used to surface the questions that are hardest for *them* specifically — not just the hardest questions overall. A difficulty-capped exponential moving average tracks skill over time, and a "Shadow" opponent in Solo mode learns and mimics the player's own response times.

---

## Results

Deployed and running continuously on Fly.io, with Google OAuth accounts and a live global leaderboard.

~~~
<div class="callout-box">
  <strong>Key takeaway:</strong> Personalizing difficulty per user — rather than shipping one fixed difficulty curve — made the "hardest questions" feature genuinely useful instead of just frustrating.
</div>
~~~

[Try it live →](https://poke-dojo.fly.dev) · [View on GitHub →](https://github.com/calbornozflores/poke-dojo)
