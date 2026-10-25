"""
Momentum Intelligence Dashboard
Hitesh Modi style 52-week high momentum scanner
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings("ignore")

# Fix common Streamlit Cloud cache issues
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

# Safe imports
YF_AVAILABLE = False
PLOTLY_AVAILABLE = False

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    pass

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    pass

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

# High quality liquid NSE universe
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
        high_val = float(latest["52w_high"])
        close_val = float(latest["Close"])
        dist = ((high_val - close_val) / high_val * 100) if high_val > 0 else 100

        past = df.iloc[:-1]
        if past["is_52w_high"].any():
            last_idx = past[past["is_52w_high"]].index[-1]
            days_since = len(df) - 1 - last_idx
        else:
            days_since = 999

        ret_1m = ((close_val / float(df["Close"].iloc[-22]) - 1) * 100) if len(df) > 22 else 0
        ret_3m = ((close_val / float(df["Close"].iloc[-66]) - 1) * 100) if len(df) > 66 else 0
        ret_6m = ((close_val / float(df["Close"].iloc[-132]) - 1) * 100) if len(df) > 132 else 0

        avg_vol = float(df["Volume"].tail(20).mean())
        latest_vol = float(latest["Volume"])

        return {
            "symbol": latest["Symbol"],
            "close": round(close_val, 2),
            "52w_high": round(high_val, 2),
            "dist_from_high_pct": round(dist, 2),
            "is_fresh_high": bool(latest["is_52w_high"]),
            "days_since_prev_high": int(days_since),
            "ret_1m": round(ret_1m, 2),
            "ret_3m": round(ret_3m, 2),
            "ret_6m": round(ret_6m, 2),
            "avg_vol_20": int(avg_vol) if avg_vol == avg_vol else 0,
            "volume_surge": round(latest_vol / avg_vol, 2) if avg_vol > 0 else 0,
        }
    except Exception:
        return None

def apply_filters(metrics_list, min_days=15, max_dist=6.0, min_vol=30000):
    out = []
    for m in metrics_list:
        if not m:
            continue
        if not m.get("is_fresh_high"):
            continue
        if m.get("days_since_prev_high", 0) < min_days:
            continue
        if m.get("dist_from_high_pct", 100) > max_dist:
            continue
        if m.get("avg_vol_20", 0) < min_vol:
            continue
        out.append(m)
    return out

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
min_days = st.sidebar.slider("Min days clean base", 5, 40, 15)
max_dist = st.sidebar.slider("Max distance from 52w high (%)", 0.0, 15.0, 6.0, 0.5)
min_vol = st.sidebar.number_input("Min Avg Volume", 10000, 500000, 30000)
run_btn = st.sidebar.button("🚀 Run Scanner", type="primary", use_container_width=True)

st.sidebar.info("Fresh 52w high after clean base (Modi style)")

# Main UI
st.title("📈 Momentum Intelligence Dashboard")
st.caption("Hitesh Modi style 52-week high scanner | Daily")

if not YF_AVAILABLE:
    st.error("❌ yfinance not installed. Check requirements.txt contains 'yfinance' and reboot the app.")
    st.code("streamlit\nyfinance\npandas\nnumpy\nplotly\nrequests\nbeautifulsoup4\nlxml", language="text")
    st.stop()

if not PLOTLY_AVAILABLE:
    st.warning("⚠️ plotly not installed. Charts will be disabled. Add 'plotly' to requirements.txt and reboot.")

tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "📊 Breadth", "🔥 Heatmap"])

with tab1:
    st.subheader("Fresh 52-Week High Scanner")

    if run_btn or "results" not in st.session_state:
        with st.spinner("Scanning... First run takes 1-3 min (then cached)"):
            raw = scan_universe(UNIVERSE)
            filtered = apply_filters(raw, min_days, max_dist, min_vol)
            filtered = sorted(filtered, key=lambda x: (-x["days_since_prev_high"], -x["ret_1m"]))
            st.session_state["results"] = filtered
            st.session_state["raw_count"] = len(raw)
            st.session_state["last"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    results = st.session_state.get("results", [])
    raw_count = st.session_state.get("raw_count", 0)
    last = st.session_state.get("last", "Never")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scanned", raw_count)
    c2.metric("Passed", len(results))
    c3.metric("Last Scan", last)
    c4.metric("Universe", len(UNIVERSE))

    if results:
        df = pd.DataFrame(results)
        df = df.rename(columns={
            "symbol": "Symbol", "close": "Close", "52w_high": "52W High",
            "dist_from_high_pct": "Dist %", "days_since_prev_high": "Days Base",
            "ret_1m": "1M %", "ret_3m": "3M %", "ret_6m": "6M %",
            "volume_surge": "Vol Surge"
        })
        cols = ["Symbol", "Close", "52W High", "Dist %", "Days Base", "1M %", "3M %", "6M %", "Vol Surge"]
        st.dataframe(df[cols], use_container_width=True, height=420)

        st.download_button("📥 Download CSV", df.to_csv(index=False), "momentum_scan.csv", "text/csv")

        # Chart
        if PLOTLY_AVAILABLE:
            top = results[0]
            df_top = get_stock_data(top["symbol"] + ".NS")
            if df_top is not None and "Date" in df_top.columns:
                fig = go.Figure(data=[go.Candlestick(
                    x=df_top["Date"], open=df_top["Open"], high=df_top["High"],
                    low=df_top["Low"], close=df_top["Close"]
                )])
                fig.add_hline(y=top["52w_high"], line_dash="dash", line_color="orange")
                fig.update_layout(
                    title=f"{top['symbol']} - Fresh 52W High after {top['days_since_prev_high']} days",
                    xaxis_rangeslider_visible=False, height=400, template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No stocks passed. Try lower 'Min days' or higher 'Max distance'.")

with tab2:
    st.subheader("Macro Breadth")
    st.metric("New 52W Highs", len(results) if results else 0)
    st.metric("Regime", "Momentum Active" if results else "Weak")
    if results:
        vol_df = pd.DataFrame(results).sort_values("volume_surge", ascending=False).head(8)
        st.dataframe(vol_df[["symbol", "close", "volume_surge", "ret_1m"]], use_container_width=True)

with tab3:
    st.subheader("Performance Heatmap")
    if results and PLOTLY_AVAILABLE:
        heat = pd.DataFrame(results)[["symbol", "ret_1m", "ret_3m", "ret_6m"]].set_index("symbol")
        fig = px.imshow(heat.T, color_continuous_scale="RdYlGn", aspect="auto",
                        title="1M / 3M / 6M Returns")
        fig.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(heat, use_container_width=True)
    elif results:
        st.dataframe(pd.DataFrame(results)[["symbol", "ret_1m", "ret_3m", "ret_6m"]], use_container_width=True)
    else:
        st.info("Run scanner first.")

st.sidebar.markdown("---")
st.sidebar.caption("Modi-style momentum")
