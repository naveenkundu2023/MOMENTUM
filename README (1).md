# Momentum Intelligence Dashboard

**Hitesh Modi style 52-week high momentum scanner + Macro Breadth + Sector Rotation**

Daily version of the popular Chartink scanner used by @imhiteshmodi, enhanced with quality filters, relative strength, and visual analytics.

---

## Features

| Feature | Description |
|---------|-------------|
| **Fresh 52W High Scanner** | Exact spirit of Modi's scan: stocks making new 52-week highs after a clean multi-day/week base |
| **Tight Filters** | Distance from high, clean base length, ROCE > 10%, liquidity, market-cap range |
| **Macro Breadth** | New highs count, volume leaders, market health view |
| **Sector Rotation** | Strength ranking of momentum candidates |
| **Performance Heatmap** | 1M / 3M / 6M return matrix of shortlisted stocks |
| **Interactive Charts** | Candlestick of top candidates with 52-week high line |
| **CSV Export** | Download full results |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the dashboard

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

---

## Scanner Logic (Daily adaptation of Modi Chartink)

- Today's Close is a **fresh 52-week high**
- Stock was **not** at 52-week high for the previous N days (default 15) → clean base
- Distance from 52-week high ≤ X% (default 6%)
- ROCE > threshold (default 10%)
- Minimum average daily volume filter
- Market-cap range filter

This captures the same edge: **fresh strength after consolidation**, not continuous highs.

---

## Sidebar Controls

- Min days since previous 52w high (clean base length)
- Max distance from 52w high (%)
- Min ROCE (%)
- Min / Max Market Cap
- Min average volume

Adjust these to make the scan tighter or looser.

---

## Universe

Currently uses a high-quality liquid universe (~350–400 stocks):
- Nifty 50
- Nifty Next 50
- Popular Midcaps
- High-liquidity F&O names

This covers the stocks where real institutional momentum money operates. Can be expanded to full Nifty 500 / 1000.

---

## How Hitesh Modi uses this process

1. **Scan** – Run every weekend / Friday
2. **Research** – Look at business triggers, earnings, industry tailwinds
3. **Buy** – Build diversified basket of 30–40 names over time
4. **Hold** – Let winners run
5. **Exit** – When stock breaks 20-week moving average / trend fails

---

## Requirements

See `requirements.txt`

Main packages:
- streamlit
- yfinance
- pandas
- numpy
- plotly

---

## Limitations (current version)

- Exact live ROCE & Market Cap for every stock are limited by free data sources
- Full 1000+ stock scan is rate-limit heavy → high-quality liquid universe used
- Sector indices and full Advance-Decline breadth can be enhanced later

---

## Future improvements

- Better fundamental data source (accurate ROCE, Market Cap, Debt/Equity)
- Full Nifty 500 / 1000 symbol list
- Weekly timeframe toggle
- Portfolio tracker with 20-week MA exit rule
- Telegram / email alerts

---

**Not financial advice. For educational and research purposes only. Always do your own due diligence.**
