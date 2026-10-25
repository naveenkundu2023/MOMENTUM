"""
52-Week High Momentum Scanner Dashboard
Professional multi-panel analytics dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings("ignore")
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

# Safe imports
YF_AVAILABLE = False
PLOTLY_AVAILABLE = False

try:
    import yfinance as yf
    YF_AVAILABLE = True
except Exception:
    pass

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except Exception:
    pass

# Page config
st.set_page_config(
    page_title="52-Week High Momentum Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - professional dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(180deg, #0b0e14 0%, #111827 100%);
    }
    
    .stMetric {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .stMetric label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    
    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }
    
    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f172a;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
        color: white !important;
    }
    
    div[data-testid="stDataFrame"] {
        background: #0f172a;
        border-radius: 12px;
        border: 1px solid #1e293b;
    }
    
    .sidebar .sidebar-content {
        background: #0f172a;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    .card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #1e293b;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== UNIVERSE ======================
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
    "VBL.NS", "PAGEIND.NS", "PERSISTENT.NS", "COFORGE.NS", "LTTS.NS"
]
UNIVERSE = list(dict.fromkeys(UNIVERSE))

# ====================== DATA FUNCTIONS ======================
@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_data(symbol: str, period: str = "2y"):
    if not YF_AVAILABLE:
        return None
    try:
        df = yf.Ticker(symbol).history(period=period, auto_adjust=True)
        if df is None or df.empty or len(df) < 120:
            return None
        df = df.reset_index()
        df["Symbol"] = symbol.replace(".NS", "")
        return df
    except Exception:
        return None

def calc_metrics(df):
    if df is None or len(df) < 252:
        return None
    try:
        df = df.copy()
        df["52w_high"] = df["Close"].rolling(252, min_periods=200).max()
        df["is_high"] = df["Close"] >= df["52w_high"] * 0.997

        latest = df.iloc[-1]
        high = float(latest["52w_high"])
        close = float(latest["Close"])
        dist = ((high - close) / high * 100) if high > 0 else 99

        past = df.iloc[:-1]
        days_since = 999
        if past["is_high"].any():
            days_since = len(df) - 1 - past[past["is_high"]].index[-1]

        def ret(n):
            if len(df) > n:
                return round((close / float(df["Close"].iloc[-n]) - 1) * 100, 2)
            return 0.0

        avg_vol = float(df["Volume"].tail(20).mean())
        vol_surge = round(float(latest["Volume"]) / avg_vol, 2) if avg_vol > 0 else 0

        # Simple RS score
        rs_score = round((ret(22) * 0.5 + ret(66) * 0.3 + ret(132) * 0.2), 2)

        return {
            "symbol": latest["Symbol"],
            "close": round(close, 2),
            "high_52w": round(high, 2),
            "dist_pct": round(dist, 2),
            "fresh_high": bool(latest["is_high"]),
            "days_base": int(days_since),
            "ret_1w": ret(5),
            "ret_1m": ret(22),
            "ret_3m": ret(66),
            "ret_6m": ret(132),
            "avg_vol": int(avg_vol),
            "vol_surge": vol_surge,
            "rs_score": rs_score
        }
    except Exception:
        return None

def apply_filters(data, min_base=12, max_dist=7.0, min_vol=25000):
    out = []
    for m in data:
        if not m or not m["fresh_high"]:
            continue
        if m["days_base"] < min_base:
            continue
        if m["dist_pct"] > max_dist:
            continue
        if m["avg_vol"] < min_vol:
            continue
        out.append(m)
    return out

@st.cache_data(ttl=7200, show_spinner=False)
def run_scan(symbols):
    results = []
    for sym in symbols:
        df = get_stock_data(sym)
        m = calc_metrics(df)
        if m:
            results.append(m)
    return results

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("## ⚙️ Scanner Settings")
    st.markdown("---")
    
    min_base = st.slider("Min Clean Base (days)", 5, 40, 12, help="Days since previous 52-week high")
    max_dist = st.slider("Max Distance from High (%)", 0.5, 12.0, 6.0, 0.5)
    min_vol = st.number_input("Min Avg Volume", 10000, 500000, 25000, step=5000)
    
    st.markdown("---")
    scan_btn = st.button("🚀 Run Full Scan", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Filters Applied")
    st.caption(f"• Fresh 52-week high")
    st.caption(f"• Clean base ≥ {min_base} days")
    st.caption(f"• Within {max_dist}% of high")
    st.caption(f"• Volume ≥ {min_vol:,.0f}")

# ====================== HEADER ======================
st.title("52-Week High Momentum Scanner")
st.caption("Professional momentum intelligence • Fresh breakouts after consolidation • Daily universe scan")

if not YF_AVAILABLE:
    st.error("yfinance package missing. Please ensure requirements.txt is correct and reboot the app.")
    st.code("streamlit\nyfinance\npandas\nnumpy\nplotly\nrequests\nbeautifulsoup4\nlxml")
    st.stop()

# ====================== RUN SCAN ======================
if scan_btn or "scan_data" not in st.session_state:
    with st.spinner("Scanning universe for fresh 52-week highs... This may take 1-2 minutes on first run."):
        raw = run_scan(UNIVERSE)
        filtered = apply_filters(raw, min_base, max_dist, min_vol)
        filtered = sorted(filtered, key=lambda x: (-x["rs_score"], -x["days_base"]))
        st.session_state["scan_data"] = filtered
        st.session_state["raw_count"] = len(raw)
        st.session_state["scan_time"] = datetime.now().strftime("%H:%M:%S")

results = st.session_state.get("scan_data", [])
raw_count = st.session_state.get("raw_count", 0)
scan_time = st.session_state.get("scan_time", "-")

# ====================== KPI ROW ======================
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Universe Scanned", f"{raw_count}")
k2.metric("Passed Filters", f"{len(results)}")
k3.metric("Avg RS Score", f"{np.mean([r['rs_score'] for r in results]):.1f}" if results else "-")
k4.metric("Avg Base Days", f"{np.mean([r['days_base'] for r in results]):.0f}" if results else "-")
k5.metric("Last Scan", scan_time)

st.markdown("")

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Scanner Results",
    "📈 Macro Breadth",
    "🔥 Performance Heatmap",
    "📉 Stock Detail"
])

# ----- TAB 1: SCANNER -----
with tab1:
    st.subheader("Fresh 52-Week High Breakouts")
    
    if results:
        df = pd.DataFrame(results)
        df_display = df[["symbol", "close", "high_52w", "dist_pct", "days_base", 
                         "ret_1w", "ret_1m", "ret_3m", "ret_6m", "vol_surge", "rs_score"]].copy()
        df_display.columns = ["Symbol", "Close", "52W High", "Dist %", "Base Days",
                              "1W %", "1M %", "3M %", "6M %", "Vol Surge", "RS Score"]
        
        st.dataframe(
            df_display.style
            .background_gradient(subset=["RS Score", "1M %", "3M %"], cmap="RdYlGn")
            .format({
                "Close": "{:.2f}",
                "52W High": "{:.2f}",
                "Dist %": "{:.2f}",
                "1W %": "{:.2f}",
                "1M %": "{:.2f}",
                "3M %": "{:.2f}",
                "6M %": "{:.2f}",
                "Vol Surge": "{:.2f}x",
                "RS Score": "{:.1f}"
            }),
            use_container_width=True,
            height=480
        )
        
        st.download_button(
            "📥 Download Full Results (CSV)",
            df_display.to_csv(index=False),
            file_name=f"52w_momentum_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No stocks currently pass the filters. Try reducing 'Min Clean Base' or increasing 'Max Distance'.")

# ----- TAB 2: MACRO BREADTH -----
with tab2:
    st.subheader("Market Breadth Overview")
    
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Fresh 52W Highs", len(results))
    b2.metric("Strong Momentum (RS > 15)", len([r for r in results if r["rs_score"] > 15]))
    b3.metric("High Volume Surge (>2x)", len([r for r in results if r["vol_surge"] > 2]))
    b4.metric("Extended Base (>20d)", len([r for r in results if r["days_base"] > 20]))
    
    st.markdown("### Top Volume Surge Names")
    if results:
        vol_top = pd.DataFrame(results).sort_values("vol_surge", ascending=False).head(10)
        vol_top = vol_top[["symbol", "close", "vol_surge", "ret_1m", "rs_score"]]
        vol_top.columns = ["Symbol", "Close", "Vol Surge", "1M %", "RS Score"]
        st.dataframe(vol_top, use_container_width=True)
    
    st.markdown("### Strength Distribution")
    if results and PLOTLY_AVAILABLE:
        scores = [r["rs_score"] for r in results]
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=scores, nbinsx=15, marker_color="#3b82f6", opacity=0.8))
        fig.update_layout(
            title="RS Score Distribution of Breakouts",
            xaxis_title="RS Score",
            yaxis_title="Count",
            template="plotly_dark",
            height=320,
            margin=dict(t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

# ----- TAB 3: HEATMAP -----
with tab3:
    st.subheader("Performance Heatmap")
    
    if results and PLOTLY_AVAILABLE:
        heat_df = pd.DataFrame(results)[["symbol", "ret_1w", "ret_1m", "ret_3m", "ret_6m"]].set_index("symbol")
        heat_df.columns = ["1W", "1M", "3M", "6M"]
        
        fig = px.imshow(
            heat_df.T,
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title="Return Heatmap — Selected Momentum Names",
            labels=dict(color="Return %")
        )
        fig.update_layout(height=340, template="plotly_dark", margin=dict(t=50))
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            heat_df.style.background_gradient(cmap="RdYlGn", axis=None).format("{:.2f}%"),
            use_container_width=True
        )
    elif results:
        st.dataframe(pd.DataFrame(results)[["symbol", "ret_1w", "ret_1m", "ret_3m", "ret_6m"]], use_container_width=True)
    else:
        st.info("Run the scanner to populate the heatmap.")

# ----- TAB 4: STOCK DETAIL -----
with tab4:
    st.subheader("Individual Stock Chart")
    
    if results:
        symbols = [r["symbol"] for r in results]
        selected = st.selectbox("Select stock", symbols)
        
        stock_data = next((r for r in results if r["symbol"] == selected), None)
        df_chart = get_stock_data(selected + ".NS")
        
        if stock_data and df_chart is not None and PLOTLY_AVAILABLE:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Close", f"₹{stock_data['close']}")
            c2.metric("52W High", f"₹{stock_data['high_52w']}")
            c3.metric("Distance", f"{stock_data['dist_pct']}%")
            c4.metric("Base Days", stock_data["days_base"])
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.05, row_heights=[0.7, 0.3])
            
            fig.add_trace(go.Candlestick(
                x=df_chart["Date"],
                open=df_chart["Open"], high=df_chart["High"],
                low=df_chart["Low"], close=df_chart["Close"],
                name="Price"
            ), row=1, col=1)
            
            fig.add_hline(y=stock_data["high_52w"], line_dash="dash", line_color="#f59e0b",
                          annotation_text="52W High", row=1, col=1)
            
            fig.add_trace(go.Bar(
                x=df_chart["Date"], y=df_chart["Volume"],
                name="Volume", marker_color="#3b82f6", opacity=0.5
            ), row=2, col=1)
            
            fig.update_layout(
                title=f"{selected} — Fresh 52-Week High Setup",
                template="plotly_dark",
                height=560,
                xaxis_rangeslider_visible=False,
                showlegend=False,
                margin=dict(t=50, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Key Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("1M Return", f"{stock_data['ret_1m']}%")
            m2.metric("3M Return", f"{stock_data['ret_3m']}%")
            m3.metric("6M Return", f"{stock_data['ret_6m']}%")
            m4.metric("RS Score", f"{stock_data['rs_score']}")
    else:
        st.info("No stocks available. Run the scanner first.")

st.markdown("---")
st.caption("52-Week High Momentum Scanner • Data via Yahoo Finance • For research & educational use only")
