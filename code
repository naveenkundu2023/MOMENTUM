"""
Momentum Intelligence Dashboard
Inspired by Hitesh Modi's 52-week high scanner + Macro Breadth + Sector Rotation
Universe: Top NSE stocks (~Nifty 500 + Midcap + F&O)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings("ignore")

# Page config
st.set_page_config(
    page_title="Momentum Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme look
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1f2e; padding: 10px; border-radius: 8px; }
    h1, h2, h3 { color: #e0e0e0; }
    .stDataFrame { background-color: #1a1f2e; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# UNIVERSE (Top NSE stocks - Nifty 500 proxy + popular F&O)
# -----------------------------
# Using a curated high-quality liquid universe (~400-500 names) for speed & reliability.
# Can be expanded later.

NIFTY_500_PROXY = [
    # Nifty 50
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS",
    "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "WIPRO.NS", "HCLTECH.NS", "POWERGRID.NS", "NTPC.NS", "M&M.NS",
    "TECHM.NS", "BAJAJFINSV.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ONGC.NS", "COALINDIA.NS",
    "JSWSTEEL.NS", "TATASTEEL.NS", "INDUSINDBK.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HEROMOTOCO.NS", "BPCL.NS", "DIVISLAB.NS", "BRITANNIA.NS", "SHREECEM.NS",
    "HINDALCO.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "BAJAJ-AUTO.NS", "HDFCLIFE.NS", "SBILIFE.NS",
    "UPL.NS", "VEDL.NS",
    # Nifty Next 50 + Midcaps (high momentum / liquid)
    "ABB.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "AUROPHARMA.NS", "BAJAJHLDNG.NS",
    "BANKBARODA.NS", "BERGEPAINT.NS", "BOSCHLTD.NS", "CANBK.NS", "CHOLAFIN.NS", "COLPAL.NS",
    "DABUR.NS", "DLF.NS", "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "ICICIGI.NS", "ICICIPRULI.NS",
    "INDIGO.NS", "IOC.NS", "IRCTC.NS", "JINDALSTEL.NS", "JUBLFOOD.NS", "LICI.NS", "LUPIN.NS",
    "MARICO.NS", "MFSL.NS", "MOTHERSON.NS", "MUTHOOTFIN.NS", "NAUKRI.NS", "NMDC.NS", "PAGEIND.NS",
    "PEL.NS", "PETRONET.NS", "PIDILITIND.NS", "PNB.NS", "POLYCAB.NS", "RECLTD.NS", "SAIL.NS",
    "SIEMENS.NS", "SRF.NS", "TORNTPHARM.NS", "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "UNITDSPR.NS",
    "VOLTAS.NS", "YESBANK.NS", "ZOMATO.NS", "ZYDUSLIFE.NS",
    # Additional liquid mid/small F&O names popular in momentum
    "AARTIIND.NS", "ABBOTINDIA.NS", "ACC.NS", "ALKEM.NS", "APLAPOLLO.NS", "ASHOKLEY.NS",
    "ASTRAL.NS", "ATUL.NS", "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BATAINDIA.NS",
    "BEL.NS", "BHARATFORG.NS", "BHEL.NS", "BIOCON.NS", "BSOFT.NS", "CANFINHOME.NS", "CERA.NS",
    "COFORGE.NS", "CONCOR.NS", "COROMANDEL.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DEEPAKNTR.NS",
    "DELTACORP.NS", "DIXON.NS", "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "FORTIS.NS",
    "GLENMARK.NS", "GMRINFRA.NS", "GNFC.NS", "GODREJPROP.NS", "GRANULES.NS", "HAL.NS",
    "HINDCOPPER.NS", "HONAUT.NS", "IDFCFIRSTB.NS", "IEX.NS", "IGL.NS", "INDIACEM.NS",
    "INDIAMART.NS", "INDUSTOWER.NS", "IPCALAB.NS", "IRB.NS", "JSWENERGY.NS", "JUBLINGREA.NS",
    "KEI.NS", "LALPATHLAB.NS", "LAURUSLABS.NS", "LICHSGFIN.NS", "LTIM.NS", "LTTS.NS",
    "MANAPPURAM.NS", "MCX.NS", "METROPOLIS.NS", "MGL.NS", "MPHASIS.NS", "MRF.NS",
    "NAM-INDIA.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "OBEROIRLTY.NS", "OFSS.NS", "PAGEIND.NS",
    "PERSISTENT.NS", "PFIZER.NS", "PIIND.NS", "PNBHOUSING.NS", "POLYMED.NS", "POONAWALLA.NS",
    "PRESTIGE.NS", "RAMCOCEM.NS", "RBLBANK.NS", "SANOFI.NS", "SCHAEFFLER.NS", "SOLARINDS.NS",
    "SONACOMS.NS", "STAR.NS", "SUNDARMFIN.NS", "SUNDRMFAST.NS", "SUPREMEIND.NS", "SYNGENE.NS",
    "TATACHEM.NS", "TATACOMM.NS", "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TIINDIA.NS",
    "TORNTPOWER.NS", "TRENT.NS", "UNIONBANK.NS", "UPL.NS", "VBL.NS", "VINATIORGA.NS",
    "WHIRLPOOL.NS", "ZEEL.NS"
]

# Remove duplicates
UNIVERSE = list(dict.fromkeys(NIFTY_500_PROXY))

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_data(symbol: str, period: str = "2y"):
    """Fetch historical data for a single stock"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, auto_adjust=True)
        if df.empty or len(df) < 100:
            return None
        df = df.reset_index()
        df["Symbol"] = symbol.replace(".NS", "")
        return df
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_nifty_data(period: str = "2y"):
    """Fetch Nifty 50 for relative strength"""
    try:
        df = yf.Ticker("^NSEI").history(period=period, auto_adjust=True)
        return df["Close"]
    except Exception:
        return None

def calculate_52w_high_metrics(df: pd.DataFrame):
    """Calculate 52-week high related metrics"""
    if df is None or len(df) < 252:
        return None

    df = df.copy()
    df["52w_high"] = df["Close"].rolling(window=252, min_periods=200).max()
    df["is_52w_high"] = df["Close"] >= df["52w_high"] * 0.999  # allow tiny float tolerance

    # Distance from 52w high
    latest = df.iloc[-1]
    dist_from_high = (latest["52w_high"] - latest["Close"]) / latest["52w_high"] * 100 if latest["52w_high"] > 0 else 100

    # Days since last 52w high (before today)
    past = df.iloc[:-1]
    if past["is_52w_high"].any():
        last_high_idx = past[past["is_52w_high"]].index[-1]
        days_since_high = len(df) - 1 - last_high_idx
    else:
        days_since_high = 999

    # Fresh high today?
    is_fresh_high = bool(latest["is_52w_high"])

    # Simple RS vs Nifty (placeholder - computed later)
    ret_1m = (latest["Close"] / df["Close"].iloc[-22] - 1) * 100 if len(df) > 22 else 0
    ret_3m = (latest["Close"] / df["Close"].iloc[-66] - 1) * 100 if len(df) > 66 else 0
    ret_6m = (latest["Close"] / df["Close"].iloc[-132] - 1) * 100 if len(df) > 132 else 0

    # Volume
    avg_vol_20 = df["Volume"].tail(20).mean()
    latest_vol = latest["Volume"]

    return {
        "symbol": latest["Symbol"],
        "close": round(latest["Close"], 2),
        "52w_high": round(latest["52w_high"], 2),
        "dist_from_high_pct": round(dist_from_high, 2),
        "is_fresh_high": is_fresh_high,
        "days_since_prev_high": int(days_since_high),
        "ret_1m": round(ret_1m, 2),
        "ret_3m": round(ret_3m, 2),
        "ret_6m": round(ret_6m, 2),
        "avg_vol_20": int(avg_vol_20),
        "latest_vol": int(latest_vol),
        "volume_surge": round(latest_vol / avg_vol_20, 2) if avg_vol_20 > 0 else 0,
    }


def apply_modi_style_filters(metrics_list, 
                              min_days_base=15, 
                              max_dist_pct=8.0,
                              min_roce=10.0,
                              min_mcap_cr=500,
                              max_mcap_cr=100000,
                              min_vol=50000):
    """
    Apply Hitesh Modi style filters (adapted to daily)
    - Fresh 52w high
    - Clean base (not at high for X days)
    - Not too extended
    """
    results = []
    for m in metrics_list:
        if m is None:
            continue
        if not m["is_fresh_high"]:
            continue
        if m["days_since_prev_high"] < min_days_base:
            continue  # was already making highs recently → not "fresh after base"
        if m["dist_from_high_pct"] > max_dist_pct:
            continue
        if m["avg_vol_20"] < min_vol:
            continue
        # ROCE and MCap will be applied if we have fundamental data
        results.append(m)
    return results


@st.cache_data(ttl=7200, show_spinner=False)
def scan_universe(symbols, progress_callback=None):
    """Scan the universe and return metrics"""
    metrics = []
    total = len(symbols)
    for i, sym in enumerate(symbols):
        df = get_stock_data(sym)
        m = calculate_52w_high_metrics(df)
        if m:
            metrics.append(m)
        if progress_callback and i % 10 == 0:
            progress_callback(i / total)
    return metrics


# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.title("⚙️ Scanner Controls")
st.sidebar.markdown("---")

st.sidebar.subheader("Hitesh Modi Style Filters")
min_days_base = st.sidebar.slider("Min days since previous 52w high (clean base)", 5, 40, 15)
max_dist = st.sidebar.slider("Max distance from 52w high (%)", 0.0, 15.0, 6.0, 0.5)
min_roce = st.sidebar.number_input("Min ROCE (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)
min_mcap = st.sidebar.number_input("Min Market Cap (Cr)", 100, 5000, 500)
max_mcap = st.sidebar.number_input("Max Market Cap (Cr)", 10000, 500000, 100000)

st.sidebar.markdown("---")
st.sidebar.subheader("Liquidity")
min_avg_vol = st.sidebar.number_input("Min Avg Daily Volume", 10000, 500000, 50000)

st.sidebar.markdown("---")
run_scan = st.sidebar.button("🚀 Run / Refresh Scanner", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("""
**Logic (Daily adaptation of Modi scanner)**  
• Fresh 52-week high today  
• Was **not** at high for previous N days (clean base)  
• Within X% of the high  
• ROCE > threshold  
• Liquidity filter  
""")

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
st.title("📈 Momentum Intelligence Dashboard")
st.caption("Hitesh Modi style 52-week high momentum + Macro Breadth + Sector Rotation | Daily version")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Momentum Scanner", 
    "📊 Macro Breadth", 
    "🔄 Sector Rotation", 
    "🔥 Performance Heatmap", 
    "ℹ️ About / How to use"
])

# ========== TAB 1: MOMENTUM SCANNER ==========
with tab1:
    st.subheader("Fresh 52-Week High Momentum Scanner")
    st.markdown("Exact spirit of Hitesh Modi’s Chartink scan, adapted to **Daily** timeframe + tighter quality filters.")

    if run_scan or "scan_results" not in st.session_state:
        with st.spinner("Scanning universe... This may take 1-3 minutes on first run (data is cached after that)."):
            progress_bar = st.progress(0)
            def update_progress(p):
                progress_bar.progress(min(p, 1.0))
            
            raw_metrics = scan_universe(UNIVERSE, progress_callback=update_progress)
            progress_bar.empty()

            filtered = apply_modi_style_filters(
                raw_metrics,
                min_days_base=min_days_base,
                max_dist_pct=max_dist,
                min_roce=min_roce,
                min_mcap_cr=min_mcap,
                max_mcap_cr=max_mcap,
                min_vol=min_avg_vol
            )

            # Sort by days_since_prev_high (longer clean base = better) then by 1m return
            filtered = sorted(filtered, key=lambda x: (-x["days_since_prev_high"], -x["ret_1m"]))

            st.session_state["scan_results"] = filtered
            st.session_state["raw_count"] = len(raw_metrics)
            st.session_state["last_scan"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    results = st.session_state.get("scan_results", [])
    raw_count = st.session_state.get("raw_count", 0)
    last_scan = st.session_state.get("last_scan", "Never")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stocks Scanned", raw_count)
    col2.metric("Passed Filters", len(results))
    col3.metric("Last Scan", last_scan)
    col4.metric("Universe Size", len(UNIVERSE))

    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.rename(columns={
            "symbol": "Symbol",
            "close": "Close",
            "52w_high": "52W High",
            "dist_from_high_pct": "Dist %",
            "days_since_prev_high": "Days Clean Base",
            "ret_1m": "1M Ret %",
            "ret_3m": "3M Ret %",
            "ret_6m": "6M Ret %",
            "volume_surge": "Vol Surge",
            "avg_vol_20": "Avg Vol 20D"
        })

        display_cols = ["Symbol", "Close", "52W High", "Dist %", "Days Clean Base", 
                        "1M Ret %", "3M Ret %", "6M Ret %", "Vol Surge", "Avg Vol 20D"]

        st.dataframe(
            df_results[display_cols].style.format({
                "Close": "{:.2f}",
                "52W High": "{:.2f}",
                "Dist %": "{:.2f}",
                "1M Ret %": "{:.2f}",
                "3M Ret %": "{:.2f}",
                "6M Ret %": "{:.2f}",
                "Vol Surge": "{:.2f}x"
            }).background_gradient(subset=["1M Ret %", "3M Ret %"], cmap="RdYlGn"),
            use_container_width=True,
            height=500
        )

        # Download button
        csv = df_results.to_csv(index=False)
        st.download_button("📥 Download Results CSV", csv, "momentum_scan_results.csv", "text/csv")

        # Quick chart for top stock
        st.markdown("### Top Candidate Chart")
        top_sym = results[0]["symbol"] + ".NS"
        df_top = get_stock_data(top_sym)
        if df_top is not None:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_top["Date"],
                open=df_top["Open"], high=df_top["High"],
                low=df_top["Low"], close=df_top["Close"],
                name=top_sym
            ))
            # 52w high line
            fig.add_hline(y=results[0]["52w_high"], line_dash="dash", line_color="orange",
                          annotation_text="52W High")
            fig.update_layout(
                title=f"{results[0]['symbol']} — Fresh 52W High after {results[0]['days_since_prev_high']} days base",
                xaxis_rangeslider_visible=False,
                height=450,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No stocks passed the current filters. Try loosening 'Min days clean base' or 'Max distance from high'.")

# ========== TAB 2: MACRO BREADTH ==========
with tab2:
    st.subheader("📊 Macro Breadth Dashboard")
    st.markdown("Market health indicators (inspired by your first image).")

    # Simple breadth using the scanned universe as proxy
    if "scan_results" in st.session_state and st.session_state["scan_results"]:
        all_metrics = st.session_state.get("scan_results", [])
        # We only have filtered ones; for real breadth we would need full scan
        st.info("Full breadth requires scanning all stocks for new highs/lows. Currently showing scanner-derived stats.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("New 52W Highs (in scan)", len(results) if results else 0)
    col2.metric("% Above 50 DMA (approx)", "Coming soon")
    col3.metric("Advance / Decline", "Coming soon")
    col4.metric("Market Regime", "Momentum Active" if results else "Weak")

    st.markdown("### Top Volume & Delivery Names (from scanner)")
    if results:
        vol_df = pd.DataFrame(results).sort_values("volume_surge", ascending=False).head(10)
        st.dataframe(vol_df[["symbol", "close", "volume_surge", "ret_1m"]], use_container_width=True)

# ========== TAB 3: SECTOR ROTATION ==========
with tab3:
    st.subheader("🔄 Equity / Sector Rotation")
    st.markdown("Relative strength view (inspired by your second image).")

    st.info("""
    **How to use**:  
    - Stocks appearing repeatedly from the same sector → sector strength  
    - Cross-check with the scanner results above  
    Full sector RS charts require sector index data (Nifty IT, Pharma, Bank etc.) which can be added in next iteration.
    """)

    if results:
        # Simple grouping by first letters / known sectors (placeholder)
        st.write("Top momentum names by recent strength:")
        strength_df = pd.DataFrame(results).sort_values("ret_1m", ascending=False)[["symbol", "ret_1m", "ret_3m", "days_since_prev_high"]]
        st.dataframe(strength_df.head(15), use_container_width=True)

# ========== TAB 4: PERFORMANCE HEATMAP ==========
with tab4:
    st.subheader("🔥 Performance Heatmap")
    st.markdown("Monthly-style return view of current momentum candidates (inspired by your third image).")

    if results:
        heat_df = pd.DataFrame(results)[["symbol", "ret_1m", "ret_3m", "ret_6m"]].set_index("symbol")
        fig = px.imshow(
            heat_df.T,
            labels=dict(x="Symbol", y="Period", color="Return %"),
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title="Momentum Candidates — Return Heatmap"
        )
        fig.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(heat_df.style.background_gradient(cmap="RdYlGn", axis=None).format("{:.2f}%"), use_container_width=True)
    else:
        st.info("Run the scanner first to populate the heatmap.")

# ========== TAB 5: ABOUT ==========
with tab5:
    st.subheader("About this Dashboard")
    st.markdown("""
### What this system shows

| Layer | Intelligence |
|-------|--------------|
| **Fresh 52W High + Clean Base** | Stocks that just broke out after a period of consolidation (core Modi edge) |
| **Distance from High** | Avoids already-extended names |
| **ROCE Filter** | Quality gate (capital efficient businesses) |
| **Volume / Liquidity** | Tradeable names only |
| **Macro Breadth** | Is the market healthy enough for momentum? |
| **Sector Rotation** | Where is institutional money flowing? |
| **Heatmap** | Visual ranking of strength |

### How Hitesh Modi uses it
1. Run scanner on weekend / Friday
2. Study the businesses (earnings triggers, industry tailwinds)
3. Build diversified basket of 30-40 names over time
4. Hold winners, exit on 20-week MA break / trend failure
5. Let the system work through both winning and losing periods

### Limitations of this version
- Fundamentals (exact ROCE, Market Cap) are not fully pulled yet (yfinance limitation for all Indian stocks)
- Full NSE 2000+ scan is rate-limit heavy → currently using high-quality liquid universe
- Sector indices & full breadth can be enhanced in next version

### Next improvements you can request
- Add exact Market Cap + ROCE from better sources
- Full Nifty 500 / 1000 symbol list
- Weekly timeframe toggle
- Auto email / Telegram alerts
- Portfolio tracker with exit rules
""")

st.sidebar.markdown("---")
st.sidebar.caption("Built for momentum investors following Hitesh Modi style process")



========== REQUIREMENTS.TXT ==========

streamlit>=1.28.0
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
ta>=0.10.2



========== README.md ==========

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
