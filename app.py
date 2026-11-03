"""
52-Week High Momentum Scanner
Dark • Colorful • Professional Analytics Dashboard
+ Broker Recommendations & Confidence Simulator
(Updated presentation: Stock-grouped table | Last-5-day highlight | Age color gradation | 90D consolidated)
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
div[data-testid="stDataFrame"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
}
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
.section-header {
    color: #e2e8f0;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 1.2rem 0 0.8rem 0;
    padding-left: 10px;
    border-left: 4px solid #3b82f6;
}
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

# ====================== BROKER TRACK RECORD ======================
BROKER_TRACK = {
    "SBI Securities":      {"hit_any": 74.3, "hit_end": 48.6, "actual_12m": 19.8, "n": 70},
    "Bonanza":             {"hit_any": 72.6, "hit_end": 50.5, "actual_12m": 18.1, "n": 95},
    "Chola Wealth Direct": {"hit_any": 66.7, "hit_end": 48.5, "actual_12m": 22.3, "n": 99},
    "IDBI Capital":        {"hit_any": 72.2, "hit_end": 44.1, "actual_12m": 10.9, "n": 836},
    "Geojit BNP Paribas":  {"hit_any": 75.5, "hit_end": 43.3, "actual_12m": 8.3,  "n": 1734},
    "ICICI Securities":    {"hit_any": 66.5, "hit_end": 41.9, "actual_12m": 17.0, "n": 3121},
    "ICICI Direct":        {"hit_any": 71.1, "hit_end": 40.4, "actual_12m": 15.4, "n": 1541},
    "Axis Direct":         {"hit_any": 67.3, "hit_end": 38.5, "actual_12m": 3.8,  "n": 2128},
    "Motilal Oswal":       {"hit_any": 64.3, "hit_end": 37.5, "actual_12m": 4.6,  "n": 2905},
    "Prabhudas Lilladhar": {"hit_any": 64.8, "hit_end": 38.2, "actual_12m": 4.5,  "n": 1768},
    "Sharekhan":           {"hit_any": 58.8, "hit_end": 33.2, "actual_12m": 5.1,  "n": 955},
    "BOB Capital Markets": {"hit_any": 65.7, "hit_end": 36.9, "actual_12m": 3.0,  "n": 1082},
    "LKP Securities":      {"hit_any": 55.0, "hit_end": 44.0, "actual_12m": 14.4, "n": 100},
    "Ventura":             {"hit_any": 41.9, "hit_end": 27.1, "actual_12m": 18.9, "n": 210},
    "Emkay":               {"hit_any": 57.3, "hit_end": 27.0, "actual_12m": -0.9, "n": 478},
    "Anand Rathi":         {"hit_any": 44.0, "hit_end": 22.6, "actual_12m": -1.6, "n": 266},
    "Arihant Capital":     {"hit_any": 60.5, "hit_end": 32.6, "actual_12m": 14.5, "n": 43},
    "AUM Capital":         {"hit_any": 55.3, "hit_end": 34.2, "actual_12m": 22.0, "n": 38},
    "Hem Securities":      {"hit_any": 61.9, "hit_end": 31.7, "actual_12m": 6.1,  "n": 126},
    "BP Wealth":           {"hit_any": 63.2, "hit_end": 29.8, "actual_12m": -3.2, "n": 57},
    "Edelweiss":           {"hit_any": 53.8, "hit_end": 29.8, "actual_12m": -0.4, "n": 517},
    "Yes Securities":      {"hit_any": 26.3, "hit_end": 15.8, "actual_12m": 2.4,  "n": 38},
    "HDFC Securities":     {"hit_any": 60.0, "hit_end": 35.0, "actual_12m": 6.0,  "n": 0},
    "Kotak Securities":    {"hit_any": 62.0, "hit_end": 36.0, "actual_12m": 7.0,  "n": 0},
    "JM Financial":        {"hit_any": 60.0, "hit_end": 35.0, "actual_12m": 5.0,  "n": 0},
    "Systematix":          {"hit_any": 55.0, "hit_end": 30.0, "actual_12m": 4.0,  "n": 0},
    "SMIFS":               {"hit_any": 58.0, "hit_end": 32.0, "actual_12m": 5.0,  "n": 0},
    "Nuvama":              {"hit_any": 62.0, "hit_end": 36.0, "actual_12m": 8.0,  "n": 0},
    "DAM Capital":         {"hit_any": 60.0, "hit_end": 35.0, "actual_12m": 6.0,  "n": 0},
    "Joindre Capital":     {"hit_any": 55.0, "hit_end": 30.0, "actual_12m": 5.0,  "n": 0},
    "Religare":            {"hit_any": 58.0, "hit_end": 32.0, "actual_12m": 5.0,  "n": 0},
}

# ====================== RECENT BROKER RECOMMENDATIONS ======================
# Structure: symbol -> list of dicts with broker, rating, target, date, upside_pct, horizon (months), entry (optional)
# Dates are approximate based on public reports as of early Nov 2026. Update regularly.
SAMPLE_RECOS = {
    "RELIANCE": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 1520, "date": "2026-11-02", "upside_pct": 21, "horizon": 12},
    ],
    "ITC": [
        {"broker": "Nuvama", "rating": "Buy (Upgraded)", "target": 310, "date": "2026-11-03", "upside_pct": None, "horizon": 12},
        {"broker": "Emkay", "rating": "Add", "target": 300, "date": "2026-11-03", "upside_pct": None, "horizon": 12},
        {"broker": "DAM Capital", "rating": "Buy", "target": 355, "date": "2026-11-03", "upside_pct": None, "horizon": 12},
    ],
    "JSWSTEEL": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-11-02", "upside_pct": 24, "horizon": 12},
    ],
    "TATAPOWER": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
        {"broker": "Religare", "rating": "Buy", "target": None, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
    ],
    "LT": [
        {"broker": "JM Financial", "rating": "Buy", "target": 4510, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Geojit BNP Paribas", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "SMIFS", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-10-28", "upside_pct": None, "horizon": 12},
    ],
    "TVSMOTOR": [
        {"broker": "Emkay", "rating": "Buy", "target": 4200, "date": "2026-10-29", "upside_pct": 24, "horizon": 12},
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 4159, "date": "2026-10-29", "upside_pct": 23, "horizon": 12},
        {"broker": "Geojit BNP Paribas", "rating": "Buy", "target": 4233, "date": "2026-11-01", "upside_pct": 17, "horizon": 12},
    ],
    "SUNPHARMA": [
        {"broker": "BOB Capital Markets", "rating": "Buy", "target": 2109, "date": "2026-11-01", "upside_pct": 19.5, "horizon": 12},
    ],
    "ASHOKLEY": [
        {"broker": "Joindre Capital", "rating": "Buy", "target": 184, "date": "2026-10-21", "upside_pct": 21, "horizon": 12},
        {"broker": "Axis Direct", "rating": "Buy", "target": None, "date": "2026-10-27", "upside_pct": None, "horizon": 12},
    ],
    "DIXON": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 15900, "date": "2026-11-02", "upside_pct": 29, "horizon": 12},
    ],
    "INFY": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 1300, "date": "2026-11-02", "upside_pct": 13, "horizon": 12},
    ],
    "HCLTECH": [
        {"broker": "Religare", "rating": "Buy", "target": 1680, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
    ],
    "BAJFINANCE": [
        {"broker": "Religare", "rating": "Buy", "target": 1096, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
        {"broker": "ICICI Direct", "rating": "Buy", "target": 1180, "date": "2026-10-13", "upside_pct": 18, "horizon": 12},
    ],
    "KOTAKBANK": [
        {"broker": "Religare", "rating": "Accumulate", "target": 518, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 500, "date": "2026-10-28", "upside_pct": None, "horizon": 12},
        {"broker": "ICICI Direct", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Geojit BNP Paribas", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "ICICIBANK": [
        {"broker": "ICICI Direct", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-10-28", "upside_pct": None, "horizon": 12},
    ],
    "ADANIPORTS": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Geojit BNP Paribas", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "TATASTEEL": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 220, "date": "2026-09-21", "upside_pct": 24, "horizon": 12},
        {"broker": "Multiple (Diwali)", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "MARICO": [
        {"broker": "Emkay", "rating": "Buy", "target": 1000, "date": "2026-11-03", "upside_pct": None, "horizon": 12},
    ],
    "GRANULES": [
        {"broker": "Emkay", "rating": "Buy", "target": 950, "date": "2026-11-03", "upside_pct": None, "horizon": 12},
    ],
    "PERSISTENT": [
        {"broker": "Axis Direct", "rating": "Buy", "target": 6615, "date": "2026-10-21", "upside_pct": 13, "horizon": 12},
    ],
    "AUROPHARMA": [
        {"broker": "Axis Direct", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Motilal Oswal", "rating": "Buy", "target": None, "date": "2026-10-15", "upside_pct": None, "horizon": 12},
    ],
    "SOLARINDS": [
        {"broker": "Motilal Oswal", "rating": "Buy", "target": 23000, "date": "2026-09-21", "upside_pct": 18, "horizon": 12},
        {"broker": "Jefferies", "rating": "Buy", "target": None, "date": "2026-09-08", "upside_pct": None, "horizon": 12},
    ],
    "APLAPOLLO": [
        {"broker": "Axis Direct", "rating": "Buy", "target": 2340, "date": "2026-10-27", "upside_pct": 15, "horizon": 12},
    ],
    "BANKBARODA": [
        {"broker": "ICICI Direct", "rating": "Buy", "target": 340, "date": "2026-10-13", "upside_pct": 17, "horizon": 12},
    ],
    "UNIONBANK": [
        {"broker": "Systematix", "rating": "Buy", "target": 205, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
    ],
    "WIPRO": [
        {"broker": "SMC Global", "rating": "Buy", "target": 225, "date": "2026-11-02", "upside_pct": None, "horizon": 12},
    ],
    "ZOMATO": [
        {"broker": "Axis Direct", "rating": "Buy", "target": 365, "date": "2026-10-27", "upside_pct": 15, "horizon": 12},
        {"broker": "Multiple (Diwali)", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "HAL": [
        {"broker": "Axis Direct", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": 22, "horizon": 12},
    ],
    "BEL": [
        {"broker": "Multiple", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "TECHM": [
        {"broker": "Multiple (Diwali)", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
        {"broker": "Axis Direct", "rating": "Buy", "target": 2150, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "BHARTIARTL": [
        {"broker": "Multiple (Diwali / Jefferies)", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "SBIN": [
        {"broker": "Multiple", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
    "HDFCBANK": [
        {"broker": "Multiple", "rating": "Buy", "target": None, "date": "2026-11-01", "upside_pct": None, "horizon": 12},
    ],
}

def get_broker_confidence(broker_name: str) -> float:
    for key in BROKER_TRACK:
        if key.lower() in broker_name.lower() or broker_name.lower() in key.lower():
            t = BROKER_TRACK[key]
            hit_score = t["hit_any"] * 0.4 + t["hit_end"] * 0.3
            act = max(min(t["actual_12m"], 25), -10)
            act_score = ((act + 10) / 35) * 100 * 0.3
            return round(hit_score + act_score, 1)
    return 45.0

def parse_date(dstr):
    try:
        return datetime.strptime(dstr, "%Y-%m-%d")
    except Exception:
        return datetime(2026, 1, 1)

def days_ago(dstr):
    return (datetime.now() - parse_date(dstr)).days

def age_color(days):
    """Return background color based on age of recommendation"""
    if days <= 5:
        return "background-color: #14532d; color: #86efac; font-weight: 700;"   # Fresh green
    elif days <= 15:
        return "background-color: #1e3a2f; color: #bbf7d0;"
    elif days <= 30:
        return "background-color: #1e293b; color: #e2e8f0;"
    elif days <= 60:
        return "background-color: #1c1917; color: #a8a29e;"
    else:
        return "background-color: #0f172a; color: #64748b;"

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
st.markdown('<p class="subtitle">Fresh 52-week highs after clean consolidation • Stock-grouped Broker Recommendations with age highlighting</p>', unsafe_allow_html=True)

if not YF_AVAILABLE:
    st.error("yfinance missing. Please put `yfinance` in requirements.txt and reboot.")
    st.stop()

# ====================== CONTROLS ======================
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
t1, t2, t3, t4, t5 = st.tabs([
    "📊 Macro Breadth",
    "🔄 Equity Rotation",
    "🔥 Performance Heatmap",
    "📋 Full Results + Chart",
    "🏦 Broker Recos (Stock Grouped)"
])

# ----- MACRO BREADTH -----
with t1:
    st.markdown('<p class="section-header">Macro Breadth Overview</p>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Fresh 52W Highs", len(results))
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

# ----- BROKER RECOMMENDATIONS (STOCK GROUPED) -----
with t5:
    st.markdown('<p class="section-header">Broker Recommendations — Stock Grouped View</p>', unsafe_allow_html=True)
    
    st.markdown("""
    **Presentation Rules**  
    - Grouped by Stock → Brokers sorted by most recent date first  
    - **Last 5 days** highlighted in bright green  
    - Color fades as recommendation ages (green → neutral → muted)  
    - Single consolidated table for last **90 days**  
    - Separate section for longer-horizon / multi-bagger ideas (>12 months)  
    """)
    
    # ---------- Build flat recent recommendations (last 90 days) ----------
    today = datetime.now()
    rows_90d = []
    long_horizon = []
    
    for sym, recs in SAMPLE_RECOS.items():
        for rec in recs:
            d = parse_date(rec["date"])
            age = (today - d).days
            horizon = rec.get("horizon", 12)
            
            row = {
                "Symbol": sym,
                "Broker": rec["broker"],
                "Rating": rec["rating"],
                "Target": rec.get("target"),
                "Upside %": rec.get("upside_pct"),
                "Date": rec["date"],
                "Age (days)": age,
                "Horizon (m)": horizon,
                "Broker Conf": get_broker_confidence(rec["broker"])
            }
            
            if horizon and horizon > 12:
                long_horizon.append(row)
            elif age <= 90:
                rows_90d.append(row)
    
    # Sort: Symbol then most recent date first
    if rows_90d:
        df90 = pd.DataFrame(rows_90d)
        df90 = df90.sort_values(["Symbol", "Date"], ascending=[True, False])
        
        # Color styling function
        def style_age(row):
            styles = [""] * len(row)
            age = row["Age (days)"]
            # Apply to the whole row for visual grouping, stronger on Date & Age
            base = age_color(age)
            for i in range(len(row)):
                styles[i] = base
            return styles
        
        st.markdown("#### Consolidated Broker Calls — Last 90 Days (Stock Grouped)")
        st.caption("Bright green = last 5 days | Color fades with age | Sorted by stock then latest date")
        
        styled = df90.style.apply(style_age, axis=1).format({
            "Target": "{:.0f}",
            "Upside %": "{:.1f}",
            "Broker Conf": "{:.1f}",
            "Age (days)": "{:.0f}",
            "Horizon (m)": "{:.0f}"
        })
        
        st.dataframe(styled, use_container_width=True, height=520, hide_index=True)
        
        # Quick filter for last 5 days
        last5 = df90[df90["Age (days)"] <= 5]
        if not last5.empty:
            st.markdown("#### 🔥 Fresh Calls (Last 5 Days)")
            st.dataframe(
                last5.style.apply(lambda r: ["background-color: #14532d; color: #86efac; font-weight:700"]*len(r), axis=1)
                .format({"Target": "{:.0f}", "Upside %": "{:.1f}", "Broker Conf": "{:.1f}"}),
                use_container_width=True, hide_index=True
            )
    else:
        st.info("No recommendations within last 90 days in SAMPLE_RECOS.")
    
    # ---------- Longer horizon / Multi-bagger section ----------
    st.markdown("#### Longer Horizon / Multi-bagger Ideas (Horizon > 12 months)")
    if long_horizon:
        df_long = pd.DataFrame(long_horizon).sort_values(["Symbol", "Date"], ascending=[True, False])
        st.dataframe(df_long, use_container_width=True, hide_index=True)
    else:
        st.info("No multi-bagger / >12-month horizon recommendations currently loaded. Add them to SAMPLE_RECOS with horizon > 12.")
    
    # ---------- Matches with scanner hits ----------
    st.markdown("#### Overlap with Current 52W-High Scanner Hits")
    if results:
        match_rows = []
        for r in results:
            sym = r["symbol"]
            recs = SAMPLE_RECOS.get(sym, [])
            for rec in recs:
                age = days_ago(rec["date"])
                if age <= 90:
                    match_rows.append({
                        "Symbol": sym,
                        "Close": r["close"],
                        "RS": r["rs"],
                        "Base": r["base"],
                        "Broker": rec["broker"],
                        "Rating": rec["rating"],
                        "Target": rec.get("target"),
                        "Upside %": rec.get("upside_pct"),
                        "Date": rec["date"],
                        "Age (days)": age,
                        "Broker Conf": get_broker_confidence(rec["broker"])
                    })
        if match_rows:
            match_df = pd.DataFrame(match_rows).sort_values(["Symbol", "Date"], ascending=[True, False])
            st.success(f"{len(match_rows)} matching recent broker calls found on current filtered names.")
            st.dataframe(match_df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent broker coverage on the current filtered 52W-high names.")
    else:
        st.info("Run the scanner to see overlaps.")
    
    # ---------- Broker Confidence Leaderboard ----------
    st.markdown("#### Broker Historical Confidence Leaderboard")
    track_rows = []
    for name, t in BROKER_TRACK.items():
        conf = get_broker_confidence(name)
        track_rows.append({
            "Broker": name,
            "Confidence": conf,
            "Hit Any %": t["hit_any"],
            "Hit at 12M %": t["hit_end"],
            "Actual 12M Ret %": t["actual_12m"],
            "Sample Size": t["n"]
        })
    track_df = pd.DataFrame(track_rows).sort_values("Confidence", ascending=False)
    st.dataframe(
        track_df.style.background_gradient(subset=["Confidence", "Hit Any %", "Actual 12M Ret %"], cmap="RdYlGn")
        .format({"Confidence": "{:.1f}", "Hit Any %": "{:.1f}", "Hit at 12M %": "{:.1f}", "Actual 12M Ret %": "{:.1f}"}),
        use_container_width=True, height=320
    )
    
    st.info("""
    **How to maintain this view**  
    1. Update `SAMPLE_RECOS` with new calls (include accurate date + optional horizon).  
    2. Horizon > 12 will automatically go to the multi-bagger section.  
    3. Age coloring and last-5-day highlight work automatically from the date field.  
    4. Source: Trendlyne + individual broker reports. Keep refreshing weekly.
    """)

st.markdown("---")
st.caption("52-Week High Momentum Scanner + Stock-Grouped Broker Recommendations  •  Last-5-day highlight + Age color gradation  •  Research use only")
