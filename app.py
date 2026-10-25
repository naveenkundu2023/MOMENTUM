"""
52-Week High Momentum Scanner
Dark • Colorful • Professional Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os

warnings.filterwarnings("ignore")
os.environ["YFINANCE_CACHE_DIR"] = "/tmp"

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

st.set_page_config(
    page_title="52-Week High Momentum Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== PREMIUM DARK + COLORFUL CSS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0e17;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #22d3ee, #818cf8, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem !important;
}

.subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 18px 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f172a;
    border-radius: 12px;
    padding: 6px;
    gap: 6px;
    border: 1px solid #1e293b;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: #94a3b8;
    font-weight: 500;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.6rem 1.4rem;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.4);
}

/* Section headers */
.section-header {
    color: #e2e8f0;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 1.2rem 0 0.8rem 0;
    padding-left: 10px;
    border-left: 4px solid #3b82f6;
}

/* Control panel */
.control-panel {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ====================== UNIVERSE ======================
UNIVERSE = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","HINDUNILVR.NS",
    "ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS",
    "BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS",
    "WIPRO.NS","HCLTECH.NS","POWERGRID.NS","NTPC.NS","M&M.NS","TECHM.NS",
    "BAJAJFINSV.NS","ADANIENT.NS","ADANIPORTS.NS","ONGC.NS","COALINDIA.NS",
    "JSWSTEEL.NS","TATASTEEL.NS","INDUSINDBK.NS","CIPLA.NS","DRREDDY.NS","EICHERMOT.NS",
    "GRASIM.NS","HEROMOTOCO.NS","BPCL.NS","DIVISLAB.NS","BRITANNIA.NS",
    "HINDALCO.NS","TATACONSUM.NS","APOLLOHOSP.NS","BAJAJ-AUTO.NS","HDFCLIFE.NS","SBILIFE.NS",
    "ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","AUROPHARMA.NS",
    "BANKBARODA.NS","BERGEPAINT.NS","CANBK.NS","CHOLAFIN.NS","COLPAL.NS",
    "DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","HAVELLS.NS","ICICIGI.NS",
    "INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS","JUBLFOOD.NS","LICI.NS","LUPIN.NS",
    "MARICO.NS","MOTHERSON.NS","MUTHOOTFIN.NS","NAUKRI.NS","NMDC.NS",
    "PIDILITIND.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS",
    "SIEMENS.NS","SRF.NS","TORNTPHARM.NS","TRENT.NS","TVSMOTOR.NS","VOLTAS.NS",
    "ZOMATO.NS","ZYDUSLIFE.NS","ALKEM.NS","APLAPOLLO.NS","ASHOKLEY.NS",
    "ASTRAL.NS","BEL.NS","BHARATFORG.NS","BHEL.NS","BIOCON.NS",
    "COFORGE.NS","CONCOR.NS","CROMPTON.NS","CUMMINSIND.NS","DIXON.NS",
    "ESCORTS.NS","FEDERALBNK.NS","GODREJPROP.NS","GRANULES.NS","HAL.NS",
    "IDFCFIRSTB.NS","INDUSTOWER.NS","JSWENERGY.NS","KEI.NS","LAURUSLABS.NS",
    "LICHSGFIN.NS","LTIM.NS","LTTS.NS","MCX.NS","MPHASIS.NS",
    "OBEROIRLTY.NS","OFSS.NS","PERSISTENT.NS","PIIND.NS","POLYMED.NS",
    "PRESTIGE.NS","SOLARINDS.NS","SONACOMS.NS","TATACHEM.NS","TATAELXSI.NS",
    "TATAMOTORS.NS","TATAPOWER.NS","TIINDIA.NS","TORNTPOWER.NS","UNIONBANK.NS","VBL.NS"
]
UNIVERSE = list(dict.fromkeys(UNIVERSE))

# ====================== CORE LOGIC ======================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(symbol):
    if not YF_AVAILABLE:
        return None
    try:
        df = yf.Ticker(symbol).history(period="2y", auto_adjust=True)
        if df is None or len(df) < 260:
            return None
        df = df.reset_index()
        df["Symbol"] = symbol.replace(".NS", "")
        return df
    except Exception:
        return None

def compute_metrics(df):
    if df is None or len(df) < 260:
        return None
    try:
        df = df.copy()
        df["h52"] = df["Close"].rolling(252, min_periods=200).max()
        df["at_high"] = df["Close"] >= df["h52"] * 0.996

        latest = df.iloc[-1]
        high = float(latest["h52"])
        close = float(latest["Close"])
        dist = ((high - close) / high * 100) if high > 0 else 99

        # Clean base: how many days since last time it was at high
        past = df.iloc[:-1]
        days_base = 999
        if past["at_high"].any():
            days_base = len(df) - 1 - past[past["at_high"]].index[-1]

        if not bool(latest["at_high"]):
            return None

        def r(n):
            return round((close / float(df["Close"].iloc[-n]) - 1) * 100, 2) if len(df) > n else 0.0

        avg_vol = float(df["Volume"].tail(20).mean())
        surge = round(float(latest["Volume"]) / avg_vol, 2) if avg_vol > 0 else 0
        rs = round(r(22)*0.5 + r(66)*0.3 + r(132)*0.2, 1)

        return {
            "symbol": latest["Symbol"],
            "close": round(close, 2),
            "high52": round(high, 2),
            "dist": round(dist, 2),
            "base": int(days_base),
            "r1w": r(5), "r1m": r(22), "r3m": r(66), "r6m": r(132),
            "vol": int(avg_vol), "surge": surge, "rs": rs
        }
    except Exception:
        return None

def filter_results(data, min_base=10, max_dist=8.0, min_vol=20000):
    out = []
    for m in data:
        if m and m["base"] >= min_base and m["dist"] <= max_dist and m["vol"] >= min_vol:
            out.append(m)
    return sorted(out, key=lambda x: (-x["rs"], -x["base"]))

# ====================== HEADER ======================
st.markdown("# 52-Week High Momentum Scanner")
st.markdown('<p class="subtitle">Fresh 52-week highs after clean consolidation • Professional momentum intelligence</p>', unsafe_allow_html=True)

if not YF_AVAILABLE:
    st.error("yfinance missing. Please put `yfinance` in requirements.txt and reboot.")
    st.stop()

# ====================== CONTROLS (MAIN PAGE) ======================
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
st.markdown("**Scanner Controls**")
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1])
with c1:
    min_base = st.slider("Min Clean Base (days)", 5, 35, 10)
with c2:
    max_dist = st.slider("Max Distance from High (%)", 1.0, 12.0, 7.0, 0.5)
with c3:
    min_vol = st.number_input("Min Avg Volume", 10000, 200000, 20000, 5000)
with c4:
    st.write("")
    st.write("")
    run = st.button("🚀 Run Full Scan", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ====================== SCAN ======================
if run or "data" not in st.session_state:
    bar = st.progress(0)
    txt = st.empty()
    raw = []
    total = len(UNIVERSE)
    for i, sym in enumerate(UNIVERSE):
        txt.markdown(f"<span style='color:#94a3b8'>Scanning {i+1}/{total} — <b>{sym.replace('.NS','')}</b></span>", unsafe_allow_html=True)
        m = compute_metrics(fetch_data(sym))
        if m:
            raw.append(m)
        bar.progress((i+1)/total)
    filtered = filter_results(raw, min_base, max_dist, min_vol)
    st.session_state["data"] = filtered
    st.session_state["raw"] = len(raw)
    st.session_state["time"] = datetime.now().strftime("%H:%M")
    bar.empty()
    txt.empty()

results = st.session_state.get("data", [])
raw_n = st.session_state.get("raw", 0)
scan_t = st.session_state.get("time", "—")

# ====================== KPI CARDS ======================
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Universe Scanned", raw_n)
k2.metric("Passed Filters", len(results))
k3.metric("Avg RS Score", f"{np.mean([x['rs'] for x in results]):.1f}" if results else "—")
k4.metric("Avg Base Days", f"{np.mean([x['base'] for x in results]):.0f}" if results else "—")
k5.metric("Last Scan", scan_t)

st.markdown("")

# ====================== TABS ======================
t1, t2, t3, t4 = st.tabs(["📊 Macro Breadth", "🔄 Equity Rotation", "🔥 Performance Heatmap", "📋 Full Results + Chart"])

# ----- MACRO BREADTH -----
with t1:
    st.markdown('<p class="section-header">Macro Breadth Overview</p>', unsafe_allow_html=True)
    
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Fresh 52W Highs", len(results), delta=None)
    b2.metric("Strong Momentum (RS>12)", len([x for x in results if x["rs"] > 12]))
    b3.metric("Volume Surge > 1.8x", len([x for x in results if x["surge"] > 1.8]))
    b4.metric("Deep Base (>18 days)", len([x for x in results if x["base"] > 18]))
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Top Gainers (1M Return)**")
        if results:
            g = pd.DataFrame(results).nlargest(8, "r1m")[["symbol","close","r1m","r3m","surge"]]
            g.columns = ["Symbol","Close","1M %","3M %","Vol Surge"]
            st.dataframe(g, use_container_width=True, hide_index=True)
    
    with col_b:
        st.markdown("**Highest Volume Surge**")
        if results:
            v = pd.DataFrame(results).nlargest(8, "surge")[["symbol","close","surge","r1m","base"]]
            v.columns = ["Symbol","Close","Vol Surge","1M %","Base Days"]
            st.dataframe(v, use_container_width=True, hide_index=True)

# ----- EQUITY ROTATION -----
with t2:
    st.markdown('<p class="section-header">Equity Rotation — Relative Strength Leaders</p>', unsafe_allow_html=True)
    
    if results:
        top = pd.DataFrame(results).head(15)
        st.dataframe(
            top[["symbol","close","rs","r1m","r3m","base","surge"]].rename(columns={
                "symbol":"Symbol","close":"Close","rs":"RS Score","r1m":"1M %",
                "r3m":"3M %","base":"Base Days","surge":"Vol Surge"
            }),
            use_container_width=True, hide_index=True
        )
        
        if PLOTLY_AVAILABLE:
            fig = go.Figure(go.Bar(
                x=top["symbol"], y=top["rs"],
                marker=dict(color=top["rs"], colorscale="Turbo", showscale=True),
                text=top["rs"], textposition="outside"
            ))
            fig.update_layout(
                title="RS Score Ranking",
                template="plotly_dark", height=360,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=40), xaxis_tickangle=-40
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No stocks passed filters. Loosen the controls and run again.")

# ----- HEATMAP -----
with t3:
    st.markdown('<p class="section-header">Performance Heatmap</p>', unsafe_allow_html=True)
    
    if results and PLOTLY_AVAILABLE:
        h = pd.DataFrame(results)[["symbol","r1w","r1m","r3m","r6m"]].set_index("symbol")
        h.columns = ["1W","1M","3M","6M"]
        fig = px.imshow(h.T, color_continuous_scale="RdYlGn", aspect="auto",
                        title="Return Matrix of Momentum Names")
        fig.update_layout(height=340, template="plotly_dark",
                          paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(h.style.background_gradient(cmap="RdYlGn", axis=None).format("{:.1f}%"),
                     use_container_width=True)
    elif results:
        st.dataframe(pd.DataFrame(results)[["symbol","r1w","r1m","r3m","r6m"]], use_container_width=True)
    else:
        st.info("Run the scanner to generate the heatmap.")

# ----- FULL RESULTS + CHART -----
with t4:
    st.markdown('<p class="section-header">Complete Scanner Output</p>', unsafe_allow_html=True)
    
    if results:
        df = pd.DataFrame(results)
        show = df[["symbol","close","high52","dist","base","r1w","r1m","r3m","r6m","surge","rs"]].copy()
        show.columns = ["Symbol","Close","52W High","Dist %","Base","1W%","1M%","3M%","6M%","Vol Surge","RS"]
        
        st.dataframe(
            show.style.background_gradient(subset=["RS","1M%","3M%"], cmap="RdYlGn")
            .format({"Close":"{:.1f}","52W High":"{:.1f}","Dist %":"{:.1f}",
                     "1W%":"{:.1f}","1M%":"{:.1f}","3M%":"{:.1f}","6M%":"{:.1f}",
                     "Vol Surge":"{:.2f}x","RS":"{:.1f}"}),
            use_container_width=True, height=380
        )
        
        st.download_button("📥 Download CSV", show.to_csv(index=False),
                           f"52w_momentum_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        
        st.markdown('<p class="section-header">Stock Chart</p>', unsafe_allow_html=True)
        sel = st.selectbox("Choose stock", [x["symbol"] for x in results])
        s = next(x for x in results if x["symbol"] == sel)
        dfc = fetch_data(sel + ".NS")
        
        if dfc is not None and PLOTLY_AVAILABLE:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.73, 0.27], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=dfc["Date"], open=dfc["Open"], high=dfc["High"],
                                         low=dfc["Low"], close=dfc["Close"], name="Price"), row=1, col=1)
            fig.add_hline(y=s["high52"], line_dash="dash", line_color="#f59e0b", row=1, col=1)
            fig.add_trace(go.Bar(x=dfc["Date"], y=dfc["Volume"], marker_color="#6366f1", opacity=0.55), row=2, col=1)
            fig.update_layout(
                title=f"{sel}  •  Base {s['base']}d  •  Dist {s['dist']}%  •  RS {s['rs']}",
                template="plotly_dark", height=540, xaxis_rangeslider_visible=False, showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No stocks passed the current filters. Try reducing Min Clean Base or increasing Max Distance, then run again.")

st.markdown("---")
st.caption("52-Week High Momentum Scanner  •  Fresh breakouts after clean base  •  For research use only")
