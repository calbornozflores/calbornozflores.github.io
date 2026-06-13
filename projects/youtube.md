@def title = "Investing x YouTube"
@def tags = ["project", "youtube", "finance", "api"]

# Investing x YouTube

~~~
<span class="section-label">Project</span>
~~~

An analysis of whether the S&P 500 stock picks promoted by popular finance YouTubers actually beat the market — pulling video data via the YouTube Data API and correlating it with historical price data.

---

## Motivation

Finance YouTube is a massive space. Channels with millions of subscribers regularly publish videos with titles like "This stock will 10x in 2024". I wanted to know: does following these recommendations actually work? Do the stocks these creators talk about outperform the broader S&P 500 index in the weeks after a video goes live?

---

## Approach

~~~
<div class="skill-group">
  <span class="skill-badge">Python</span>
  <span class="skill-badge">YouTube Data API</span>
  <span class="skill-badge">Pandas</span>
  <span class="skill-badge">yfinance</span>
  <span class="skill-badge">Matplotlib</span>
</div>
~~~

1. **Data collection:** Used the YouTube Data API to pull video titles, publish dates, and view counts from a curated list of top finance channels.
2. **Ticker extraction:** Parsed video titles and descriptions with regex and keyword matching to extract S&P 500 stock tickers mentioned.
3. **Price data:** Pulled historical daily price data for each mentioned ticker via `yfinance`.
4. **Analysis:** Compared 30-day returns of mentioned stocks against the SPY ETF benchmark from the video publish date.

---

## Results

~~~
<div class="callout-box">
  Popular finance YouTubers mention stocks that are <strong>already moving</strong> — the mentions lag the price action, not lead it. Buying on the video publish date generally underperformed SPY on a 30-day horizon.
</div>
~~~

The more interesting finding was view count correlation: videos with very high views (>500k) showed slightly negative returns vs. benchmark, while lower-view videos with genuine analysis occasionally outperformed. This aligns with the idea that by the time a recommendation is viral, the move has already happened.

[View on GitHub →](https://github.com/calbornozflores/spy-youtube)
