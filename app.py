"""
Momentum Intelligence Dashboard
Hitesh Modi style 52-week high momentum scanner
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings("ignore")

# Fix for Streamlit Cloud yfinance cache issues
import os
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Momentum Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1f2e; padding: 10px; border-radius: 8px; }
    h1, h2, h3 { color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# Universe - high quality liquid NSE stocks
UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS",
    "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "WIPRO.NS", "HCLTECH.NS", "POWERGRID.NS", "NTPC.NS", "M&M.NS", "TECHM.NS",
    "BAJAJFINSV.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ONGC.NS", "COALINDIA.NS",
    "JSWSTEEL.NS", "TATASTEEL.NS", "INDUSINDBK.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HEROMOTOCO.NS", "BPCL.NS", "DIVISLAB.NS", "BRITANNIA.NS",
    "HINDALCO.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "BAJAJ-AUTO.NS", "HDFCLIFE.NS", "SBILIFE.NS",
    "ABB.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "AUROPHARMA.NS",
    "BANKBARODA.NS", "BERGEPAINT.NS", "CANBK.NS", "CHOLAFIN.NS", "COLPAL.NS",
    "DABUR.NS", "DLF.NS", "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "ICICIGI.NS",
    "INDIGO.NS", "IOC.NS", "IRCTC.NS", "JINDALSTEL.NS", "JUBLFOOD.NS", "LICI.NS", "LUPIN.NS",
    "MARICO.NS", "MOTHERSON.NS", "MUTHOOTFIN.NS", "NAUKRI.NS", "NMDC.NS",
    "PIDILITIND.NS", "PNB.NS", "POLYCAB.NS", "RECLTD.NS", "SAIL.NS",
    "SIEMENS.NS", "SRF.NS", "TORNTPHARM.NS", "TRENT.NS", "TVSMOTOR.NS", "VOLTAS.NS",
    "ZOMATO.NS", "ZYDUSLIFE.NS", "ALKEM.NS", "APLAPOLLO.NS", "ASHOKLEY.NS",
    "ASTRAL.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", "BIOCON.NS",
    "COFORGE.NS", "CONCOR.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DIXON.NS",
    "ESCORTS.NS", "FEDERALBNK.NS", "GODREJPROP.NS", "GRANULES.NS", "HAL.NS",
    "IDFCFIRSTB.NS", "INDUSTOWER.NS", "JSWENERGY.NS", "KEI.NS", "LAURUSLABS.NS",
    "LICHSGFIN.NS", "LTIM.NS", "LTTS.NS", "MCX.NS", "MPHASIS.NS",
    "OBEROIRLTY.NS", "OFSS.NS", "PERSISTENT.NS", "PIIND.NS", "POLYMED.NS",
    "PRESTIGE.NS", "SOLARINDS.NS", "SONACOMS.NS", "TATACHEM.NS", "TATAELXSI.NS",
    "TATAMOTORS.NS", "TATAPOWER.NS", "TIINDIA.NS", "TORNTPOWER.NS", "UNIONBANK.NS",
    "VBL.NS"
]

UNIVERSE = list(dict.fromkeys(UNIVERSE))

@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_data(symbol: str, period: str = "2y"):
    if not YF_AVAILABLE:
        return None
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, auto_adjust=True)
        if df is None or df.empty or len(df) < 100:
            return None
        df = df.reset_index()
        if "Date" not in df.columns and "index" in df.columns:
            df = df.rename(columns={"index": "Date"})
        df["Symbol"] = symbol.replace(".NS", "")
        return df
    except Exception:
        return None

def calculate_52w_high_metrics(df: pd.DataFrame):
    if df is None or len(df) < 252:
        return None
    try:
        df = df.copy()
        df["52w_high"] = df["Close"].rolling(window=252, min_periods=200).max()
        df["is_52w_high"] = df["Close"] >= (df["52w_high"] * 0.998)

        latest = df.iloc[-1]
        high_val = latest["52w_high"]
        close_val = latest["Close"]
        dist_from_high = ((high_val - close_val) / high_val * 100) if high_val > 0 else 100

        past = df.iloc[:-1]
        if past["is_52w_high"].any():
            last_high_idx = past[past["is_52w_high"]].index[-1]
            days_since_high = len(df) - 1 - last_high_idx
        else:
            days_since_high = 999

        is_fresh_high = bool(latest["is_52w_high"])

        ret_1m = ((close_val / df["Close"].iloc[-22] - 1) * 100) if len(df) > 22 else 0
        ret_3m = ((close_val / df["Close"].iloc[-66] - 1) * 100) if len(df) > 66 else 0
        ret_6m = ((close_val / df["Close"].iloc[-132] - 1) * 100) if len(df) > 132 else 0

        avg_vol_20 = df["Volume"].tail(20).mean()
        latest_vol = latest["Volume"]

        return {
            "symbol": latest["Symbol"],
            "close": round(float(close_val), 2),
            "52w_high": round(float(high_val), 2),
            "dist_from_high_pct": round(float(dist_from_high), 2),
            "is_fresh_high": is_fresh_high,
            "days_since_prev_high": int(days_since_high),
            "ret_1m": round(float(ret_1m), 2),
            "ret_3m": round(float(ret_3m), 2),
            "ret_6m": round(float(ret_6m), 2),
            "avg_vol_20": int(avg_vol_20) if not np.isnan(avg_vol_20) else 0,
            "volume_surge": round(float(latest_vol / avg_vol_20), 2) if avg_vol_20 > 0 else 0,
        }
    except Exception:
        return None

def apply_modi_style_filters(metrics_list, min_days_base=15, max_dist_pct=6.0, min_vol=30000):
    results = []
    for m in metrics_list:
        if m is None:
            continue
        if not m.get("is_fresh_high", False):
            continue
        if m.get("days_since_prev_high", 0) < min_days_base:
            continue
        if m.get("dist_from_high_pct", 100) > max_dist_pct:
            continue
        if m.get("avg_vol_20", 0) < min_vol:
            continue
        results.append(m)
    return results

@st.cache_data(ttl=7200, show_spinner=False)
def scan_universe(symbols):
    metrics = []
    for sym in symbols:
        df = get_stock_data(sym)
        m = calculate_52w_high_metrics(df)
        if m:
            metrics.append(m)
    return metrics

# Sidebar
st.sidebar.title("⚙️ Scanner Controls")
st.sidebar.markdown("---")

min_days_base = st.sidebar.slider("Min days clean base", 5, 40, 15)
max_dist = st.sidebar.slider("Max distance from 52w high (%)", 0.0, 15.0, 6.0, 0.5)
min_avg_vol = st.sidebar.number_input("Min Avg Daily Volume", 10000, 500000, 30000)

st.sidebar.markdown("---")
run_scan = st.sidebar.button("🚀 Run / Refresh Scanner", type="primary", use_container_width=True)

st.sidebar.info("""
**Logic (Modi style)**  
• Fresh 52-week high today  
• Clean base (not at high for N days)  
• Within X% of the high  
• Liquidity filter  
""")

# Main
st.title("📈 Momentum Intelligence Dashboard")
st.caption("Hitesh Modi style 52-week high momentum scanner | Daily version")

if not YF_AVAILABLE:
    st.error("yfinance is not installed. Please check requirements.txt and reboot the app.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Momentum Scanner",
    "📊 Macro Breadth",
    "🔄 Strength Ranking",
    "🔥 Heatmap"
])

with tab1:
    st.subheader("Fresh 52-Week High Momentum Scanner")

    if run_scan or "scan_results" not in st.session_state:
        with st.spinner("Scanning universe... First run may take 1-3 minutes (then cached)."):
            raw_metrics = scan_universe(UNIVERSE)
            filtered = apply_modi_style_filters(
                raw_metrics,
                min_days_base=min_days_base,
                max_dist_pct=max_dist,
                min_vol=min_avg_vol
            )
            filtered = sorted(filtered, key=lambda x: (-x["days_since_prev_high"], -x["ret_1m"]))
            st.session_state["scan_results"] = filtered
            st.session_state["raw_count"] = len(raw_metrics)
            st.session_state["last_scan"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    results = st.session_state.get("scan_results", [])
    raw_count = st.session_state.get("raw_count", 0)
    last_scan = st.session_state.get("last_scan", "Never")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stocks Scanned", raw_count)
    c2.metric("Passed Filters", len(results))
    c3.metric("Last Scan", last_scan)
    c4.metric("Universe Size", len(UNIVERSE))

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
                        "1M Ret %", "3M Ret %", "6M Ret %", "Vol Surge"]

        st.dataframe(
            df_results[display_cols],
            use_container_width=True,
            height=450
        )

        csv = df_results.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "momentum_scan.csv", "text/csv")

        # Chart of top name
        st.markdown("### Top Candidate Chart")
        top = results[0]
        top_sym = top["symbol"] + ".NS"
        df_top = get_stock_data(top_sym)
        if df_top is not None and "Date" in df_top.columns:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_top["Date"],
                open=df_top["Open"], high=df_top["High"],
                low=df_top["Low"], close=df_top["Close"],
                name=top["symbol"]
            ))
            fig.add_hline(y=top["52w_high"], line_dash="dash", line_color="orange",
                          annotation_text="52W High")
            fig.update_layout(
                title=f"{top['symbol']} — Fresh 52W High after {top['days_since_prev_high']} days base",
                xaxis_rangeslider_visible=False,
                height=420,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No stocks passed the filters. Try lowering 'Min days clean base' or increasing 'Max distance from high'.")

with tab2:
    st.subheader("📊 Macro Breadth")
    st.metric("New 52W Highs (scanner)", len(results) if results else 0)
    st.metric("Market Regime", "Momentum Active" if results else "Weak / No signals")
    if results:
        st.markdown("### Highest Volume Surge")
        vol_df = pd.DataFrame(results).sort_values("volume_surge", ascending=False).head(8)
        st.dataframe(vol_df[["symbol", "close", "volume_surge", "ret_1m"]], use_container_width=True)

with tab3:
    st.subheader("🔄 Strength Ranking")
    if results:
        strength_df = pd.DataFrame(results).sort_values("ret_1m", ascending=False)[
            ["symbol", "ret_1m", "ret_3m", "days_since_prev_high"]
        ]
        st.dataframe(strength_df.head(20), use_container_width=True)
    else:
        st.info("Run the scanner first.")

with tab4:
    st.subheader("🔥 Performance Heatmap")
    if results:
        heat_df = pd.DataFrame(results)[["symbol", "ret_1m", "ret_3m", "ret_6m"]].set_index("symbol")
        fig = px.imshow(
            heat_df.T,
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title="Return Heatmap (1M / 3M / 6M)"
        )
        fig.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(heat_df, use_container_width=True)
    else:
        st.info("Run the scanner first.")

st.sidebar.markdown("---")
st.sidebar.caption("Modi-style momentum scanner")
