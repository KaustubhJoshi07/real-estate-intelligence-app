import html

import boto3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from botocore.exceptions import ClientError
from pyathena import connect

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Real Estate Intelligence Platform",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# HTML RENDER HELPER
# =========================================================
def render(markup: str) -> None:
    st.html(markup)


def esc(value) -> str:
    return html.escape(str(value))

# =========================================================
# CSS
# =========================================================
render("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(124,58,237,.16), transparent 30%),
        radial-gradient(circle at top right, rgba(34,197,94,.10), transparent 35%),
        linear-gradient(135deg, #050816 0%, #08111f 50%, #020617 100%);
    color: #e5e7eb;
}
.block-container {
    max-width: 1500px;
    padding-top: 1.3rem;
    padding-bottom: 4rem;
}
h1, h2, h3 { color: #f8fafc; letter-spacing: -0.03em; }
[data-testid="stSelectbox"] label { color: #cbd5e1 !important; font-weight: 800 !important; }
.card {
    border-radius: 22px;
    background: linear-gradient(145deg, rgba(15,23,42,.96), rgba(2,6,23,.92));
    border: 1px solid rgba(148,163,184,.24);
    box-shadow: 0 18px 55px rgba(0,0,0,.30);
}
.hero {
    padding: 28px 32px;
    margin: 18px 0 24px 0;
    display: grid;
    grid-template-columns: 1.3fr .9fr;
    gap: 22px;
    align-items: center;
}
.hero-title { font-size: 36px; line-height: 1; font-weight: 950; color: #f8fafc; }
.hero-subtitle { margin-top: 10px; color: #cbd5e1; font-size: 16px; }
.data-note { margin-top: 16px; color: #38bdf8; font-size: 13px; font-weight: 750; }
.data-status { margin-top: 12px; color: #4ade80; font-size: 14px; font-weight: 850; }
.zip-pill {
    padding: 18px 20px;
    border-radius: 16px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.25);
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 12px;
}
.zip-pill-item { display: flex; gap: 12px; align-items: center; }
.dot-purple, .dot-green { width: 22px; height: 22px; border-radius: 999px; display: inline-block; }
.dot-purple { background: linear-gradient(135deg,#a855f7,#7c3aed); }
.dot-green { background: linear-gradient(135deg,#4ade80,#22c55e); }
.zip-pill-main { color: #ffffff; font-weight: 950; font-size: 18px; }
.zip-pill-sub { color: #cbd5e1; font-size: 13px; margin-top: 2px; }
.vs { color: #cbd5e1; font-weight: 900; }
.reco-wrap {
    padding: 24px;
    margin-bottom: 24px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 18px;
}
.reco-card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(15,23,42,.64);
    border: 1px solid rgba(148,163,184,.22);
    min-height: 150px;
}
.reco-label { font-size: 12px; font-weight: 950; letter-spacing: .05em; text-transform: uppercase; }
.green { color: #4ade80; }
.purple { color: #c084fc; }
.blue { color: #38bdf8; }
.reco-title { margin-top: 10px; font-size: 28px; line-height: 1.05; font-weight: 950; }
.reco-reason { margin-top: 14px; color: #f8fafc; font-weight: 750; font-size: 14px; line-height: 1.55; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
.panel { padding: 24px; }
.panel-title { font-size: 20px; font-weight: 950; color: #f8fafc; margin-bottom: 18px; }
.factor-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.factor-table th { color: #cbd5e1; text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(148,163,184,.22); }
.factor-table td { color: #f8fafc; padding: 14px 10px; border-bottom: 1px solid rgba(148,163,184,.16); vertical-align: top; }
.factor-sub { color: #94a3b8; font-size: 12px; margin-top: 2px; }
.winner-green { color:#4ade80; font-weight: 950; }
.winner-purple { color:#c084fc; font-weight: 950; }
.score-row { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 22px; }
.score-label { color: #f8fafc; font-weight: 900; margin-bottom: 6px; }
.score-sub { color: #cbd5e1; font-size: 12px; margin-bottom: 12px; }
.score-value { font-size: 28px; font-weight: 950; }
.bar-track { height: 9px; border-radius: 999px; background: rgba(148,163,184,.22); overflow: hidden; }
.bar-fill-purple { height: 100%; background: linear-gradient(90deg,#a855f7,#c084fc); border-radius: 999px; }
.bar-fill-green { height: 100%; background: linear-gradient(90deg,#22c55e,#86efac); border-radius: 999px; }
.info-box {
    margin-top: 18px;
    padding: 18px 20px;
    border-radius: 16px;
    background: rgba(14,116,144,.16);
    border: 1px solid rgba(56,189,248,.35);
    color: #dbeafe;
    line-height: 1.55;
}
.ai-list { display: grid; gap: 16px; }
.ai-item { display: grid; grid-template-columns: 54px 1fr; gap: 16px; align-items: start; padding-bottom: 16px; border-bottom: 1px solid rgba(148,163,184,.16); }
.ai-icon { width: 48px; height: 48px; border-radius: 999px; display:flex; align-items:center; justify-content:center; font-weight:950; color:#fff; }
.ai-icon.green-bg { background: rgba(34,197,94,.35); }
.ai-icon.purple-bg { background: rgba(168,85,247,.35); }
.ai-icon.yellow-bg { background: rgba(245,158,11,.35); }
.ai-icon.blue-bg { background: rgba(14,165,233,.35); }
.ai-title { font-weight: 950; margin-bottom: 6px; }
.ai-text { color: #e5e7eb; line-height: 1.55; font-size: 14px; }
.small-note { color: #94a3b8; font-size: 12px; margin-top: 14px; }
.kpi-wrap { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin-bottom:24px; }
.kpi-card { padding: 18px; border-radius: 16px; background: rgba(15,23,42,.72); border: 1px solid rgba(148,163,184,.22); }
.kpi-label { font-size: 12px; color: #cbd5e1; font-weight: 850; }
.kpi-value { margin-top: 10px; color: #fff; font-size: 24px; font-weight: 950; }
.quick { display:grid; grid-template-columns: .8fr 1.2fr 1.2fr 1.2fr; gap: 18px; padding: 20px; margin-bottom: 24px; align-items:center; }
.quick-title { font-size: 20px; font-weight: 950; color: #f8fafc; }
.quick-text { color:#e5e7eb; line-height: 1.45; }
.footer-note { margin-top: 18px; color:#94a3b8; font-size:12px; }

.grade-pair { display:grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 22px; }
.grade-card {
    padding: 18px;
    border-radius: 16px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.22);
}
.grade-label { color:#cbd5e1; font-size:13px; font-weight:850; margin-bottom:8px; }
.grade-value { font-size:36px; font-weight:950; line-height:1; }
.grade-sub { color:#94a3b8; font-size:12px; margin-top:8px; }
.info-dot {
    display:inline-flex; align-items:center; justify-content:center;
    width:15px; height:15px; border-radius:999px;
    background:rgba(56,189,248,.18); color:#7dd3fc;
    border:1px solid rgba(56,189,248,.40);
    font-size:10px; font-weight:950; margin-left:6px; vertical-align:middle;
}


.filter-note {
    margin-top: 10px;
    color: #93c5fd;
    font-size: 12px;
    line-height: 1.45;
}
.assistant-box {
    margin: 18px 0 24px 0;
    padding: 22px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(14,116,144,.18), rgba(15,23,42,.82));
    border: 1px solid rgba(56,189,248,.35);
}
.assistant-title { font-size: 20px; font-weight: 950; color:#f8fafc; }
.assistant-placeholder {
    margin-top: 14px;
    padding: 16px 18px;
    border-radius: 14px;
    background: rgba(2,6,23,.55);
    border: 1px dashed rgba(125,211,252,.38);
    color:#cbd5e1;
    line-height:1.55;
}
.decision-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
.decision-card {
    padding: 24px;
    border-radius: 22px;
    background: linear-gradient(145deg, rgba(15,23,42,.96), rgba(2,6,23,.92));
    border: 1px solid rgba(148,163,184,.24);
    box-shadow: 0 18px 55px rgba(0,0,0,.30);
}
.decision-investment { border-color: rgba(168,85,247,.45); }
.decision-family { border-color: rgba(34,197,94,.45); }
.decision-header { display:flex; align-items:center; gap: 14px; margin-bottom: 18px; }
.decision-icon { width:44px; height:44px; border-radius:999px; display:flex; align-items:center; justify-content:center; font-weight:950; color:white; }
.decision-icon.invest { background: rgba(168,85,247,.35); }
.decision-icon.family { background: rgba(34,197,94,.35); }
.decision-title { font-size: 22px; font-weight: 950; color:#f8fafc; }
.decision-sub { color:#94a3b8; font-size:13px; margin-top:3px; }
.recommended-box {
    padding: 20px;
    border-radius: 16px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.22);
    margin-bottom: 16px;
}
.recommended-label { color:#cbd5e1; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:.05em; }
.recommended-title { margin-top:8px; color:#4ade80; font-size:28px; font-weight:950; }
.choice-badge { display:inline-block; margin-left: 10px; padding:5px 10px; border-radius:999px; background:rgba(34,197,94,.15); color:#86efac; border:1px solid rgba(34,197,94,.25); font-size:12px; font-weight:900; vertical-align:middle; }
.ai-mini-box {
    padding: 18px;
    border-radius: 16px;
    background: rgba(14,116,144,.12);
    border: 1px solid rgba(56,189,248,.24);
    margin-bottom: 16px;
}
.ai-mini-title { color:#7dd3fc; font-weight:950; margin-bottom:8px; }
.ai-mini-text { color:#e5e7eb; line-height:1.55; font-size:14px; }
.zip-choice-row { display:grid; grid-template-columns: 1fr auto 1fr; gap: 14px; align-items:center; }
.zip-choice { padding: 14px; border-radius: 14px; background: rgba(15,23,42,.62); border:1px solid rgba(148,163,184,.18); }
.zip-choice-title { color:#f8fafc; font-weight:850; }
.zip-choice-tag { margin-top:8px; display:inline-block; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:900; background:rgba(148,163,184,.14); color:#cbd5e1; }
.zip-choice-tag.better { background:rgba(34,197,94,.16); color:#86efac; }
.zip-choice-tag.good { background:rgba(168,85,247,.16); color:#d8b4fe; }
.vs-circle { width:36px; height:36px; border-radius:999px; background:rgba(15,23,42,.9); display:flex; align-items:center; justify-content:center; color:#cbd5e1; font-weight:950; }


.grade-badge { display:inline-block; min-width:42px; text-align:center; padding:5px 10px; border-radius:999px; font-weight:950; }
.grade-badge.green { background:rgba(34,197,94,.16); color:#86efac; }
.grade-badge.blue { background:rgba(14,165,233,.16); color:#7dd3fc; }
.grade-badge.purple { background:rgba(168,85,247,.16); color:#d8b4fe; }
.lead-pill { display:inline-block; padding:6px 14px; border-radius:999px; background:rgba(34,197,94,.16); color:#86efac; font-weight:950; }
.at-glance-card { padding:24px; margin-bottom:24px; }
.trend-wrap { display:grid; grid-template-columns: 2fr .85fr; gap:20px; align-items:stretch; }
.trend-side-card { padding:20px; border-radius:18px; background:rgba(15,23,42,.72); border:1px solid rgba(148,163,184,.22); }
.trend-change { font-size:30px; font-weight:950; margin:8px 0 18px; }
.trend-dot { display:inline-block; width:12px; height:12px; border-radius:999px; margin-right:8px; }
.trend-dot.purple-bg { background:#a855f7; }
.trend-dot.green-bg { background:#22c55e; }

</style>
""")

# =========================================================
# ATHENA CONNECTION
# =========================================================
@st.cache_resource
def get_connection():
    return connect(
        region_name="us-east-1",
        schema_name="default",
        s3_staging_dir="s3://real-estate-economic-intelligence-kj/athena-results/",
        work_group="primary",
    )


@st.cache_data(ttl=3600, show_spinner=False)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(query, conn)


@st.cache_data(ttl=3600, show_spinner=False)
def load_states() -> pd.DataFrame:
    """
    Lightweight query: only loads the list of states that have at least
    two complete ZIP records. This keeps the first app load small.
    """
    return run_query("""
        SELECT
            state,
            MAX(state_name) AS state_name,
            COUNT(*) AS complete_zip_count
        FROM pbi_zip_scores_enriched
        GROUP BY state
        HAVING COUNT(*) >= 2
        ORDER BY state
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_scores_for_state(selected_state: str) -> pd.DataFrame:
    """
    Loads only the selected state's complete ZIP records instead of loading
    every ZIP in the full dataset. This reduces Athena data transfer and memory.
    """
    safe_state = selected_state.replace("'", "''")
    return run_query(f"""
        SELECT
            CAST(zip_code AS VARCHAR) AS zip_code,
            city,
            state,
            state_name,
            county_name,
            current_home_value,
            yoy_growth_pct,
            appreciation_5yr_pct,
            appreciation_rank,
            growth_rank,
            price_rank,
            investment_score,
            base_family_stability_score,
            school_score,
            school_grade,
            city_safety_indicator,
            city_safety_grade,
            safety_data_level,
            investment_fit_score,
            family_fit_score,
            enhanced_use_case
        FROM pbi_zip_scores_enriched
        WHERE state = '{safe_state}'
        ORDER BY zip_code
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_selected_trend(state_a: str, zip_a: str, state_b: str, zip_b: str) -> pd.DataFrame:
    """
    Loads monthly home-value trend only for the two selected ZIP codes.
    Supports cross-state comparison.
    """
    safe_state_a = str(state_a).replace("'", "''")
    safe_state_b = str(state_b).replace("'", "''")
    safe_zip_a = str(zip_a).replace("'", "''")
    safe_zip_b = str(zip_b).replace("'", "''")
    return run_query(f"""
        SELECT
            CAST(report_date AS DATE) AS report_date,
            CAST(zip_code AS VARCHAR) AS zip_code,
            state,
            home_value
        FROM pbi_zip_monthly
        WHERE
            (state = '{safe_state_a}' AND CAST(zip_code AS VARCHAR) = '{safe_zip_a}')
            OR
            (state = '{safe_state_b}' AND CAST(zip_code AS VARCHAR) = '{safe_zip_b}')
        ORDER BY report_date
    """)

# =========================================================
# HELPERS
# =========================================================
def money(x):
    if pd.isna(x):
        return "N/A"
    return f"${float(x):,.0f}"


def pct(x):
    if pd.isna(x):
        return "N/A"
    return f"{float(x):.1f}%"


def num(x):
    if pd.isna(x):
        return "N/A"
    return f"{float(x):.1f}"


def safe_float(x) -> float:
    if pd.isna(x):
        return 0.0
    return float(x)


def grade(score: float) -> str:
    score = safe_float(score)
    if score >= 80:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 50:
        return "Moderate"
    return "Needs Review"


def winner_by(a, b, metric: str):
    return a if safe_float(a[metric]) >= safe_float(b[metric]) else b


def winner_lower(a, b, metric: str):
    return a if safe_float(a[metric]) <= safe_float(b[metric]) else b


def color_class_for_zip(zip_value, zip_a):
    return "winner-purple" if str(zip_value) == str(zip_a) else "winner-green"


def investment_strength(row) -> float:
    return min(100, max(0, safe_float(row["investment_fit_score"])))


def risk_level(row) -> float:
    # Lower is better. This risk indicator intentionally does NOT use crime data,
    # because current crime data is city-level and should not drive ZIP-level scores.
    negative_growth = max(0, -safe_float(row["yoy_growth_pct"]))
    risk = (
        safe_float(row["price_rank"]) * 0.45
        + negative_growth * 4.0
        + (100 - safe_float(row["base_family_stability_score"])) * 0.25
    )
    return min(100, max(0, risk))


def letter_grade(score: float) -> str:
    score = safe_float(score)
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def grade_color_class(grade_value: str) -> str:
    grade_value = str(grade_value or "N/A")
    if grade_value in ("A+", "A"):
        return "green"
    if grade_value == "B":
        return "blue"
    if grade_value in ("C", "D", "F"):
        return "purple"
    return "blue"


def risk_category(row) -> str:
    risk = risk_level(row)
    if risk < 35:
        return "Lower Risk"
    if risk < 60:
        return "Moderate Risk"
    return "Higher Risk"


def score_bar(label: str, sub: str, score_a: float, score_b: float, zip_a: str, zip_b: str) -> str:
    # User-facing display uses grades instead of exact composite numbers to avoid false precision.
    grade_a = letter_grade(score_a)
    grade_b = letter_grade(score_b)
    return f"""
    <div class="grade-pair">
        <div class="grade-card">
            <div class="grade-label">{esc(label)} - ZIP {esc(zip_a)}</div>
            <div class="grade-value purple">{esc(grade_a)}</div>
            <div class="grade-sub">{esc(sub)}</div>
        </div>
        <div class="grade-card">
            <div class="grade-label">{esc(label)} - ZIP {esc(zip_b)}</div>
            <div class="grade-value green">{esc(grade_b)}</div>
            <div class="grade-sub">{esc(sub)}</div>
        </div>
    </div>
    """

def kpi_card(label: str, value: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{esc(label)}</div>
        <div class="kpi-value">{esc(value)}</div>
    </div>
    """


def factor_row(label: str, sub: str, val_a: str, val_b: str, winner_zip: str, winner_city: str, zip_a: str, tooltip: str = "") -> str:
    cls = color_class_for_zip(winner_zip, zip_a)
    info = f'<span class="info-dot" title="{esc(tooltip)}">i</span>' if tooltip else ""
    return f"""
    <tr>
        <td><b>{esc(label)}</b>{info}<div class="factor-sub">{esc(sub)}</div></td>
        <td><span class="purple"><b>{esc(val_a)}</b></span></td>
        <td><span class="green"><b>{esc(val_b)}</b></span></td>
        <td><span class="{cls}">{esc(winner_zip)} - {esc(winner_city)}</span></td>
    </tr>
    """

def make_market_positioning(zip_a_data, zip_b_data):
    fig = go.Figure()

    for row, color in [(zip_a_data, "#a855f7"), (zip_b_data, "#22c55e")]:
        fig.add_trace(go.Scatter(
            x=[investment_strength(row)],
            y=[risk_level(row)],
            mode="markers+text",
            text=[f"ZIP {row['zip_code']}"],
            textposition="top center",
            marker=dict(size=28, color=color, line=dict(width=2, color="white")),
            name=f"ZIP {row['zip_code']} - {row['city']}",
            customdata=[[letter_grade(row["investment_fit_score"]), risk_category(row)]],
            hovertemplate="Investment Potential: %{customdata[0]}<br>Market Risk: %{customdata[1]}<extra></extra>",
        ))

    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="rgba(255,255,255,.25)", dash="dash"))
    fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="rgba(255,255,255,.25)", dash="dash"))

    fig.add_annotation(x=25, y=18, text="Stable but Slower", showarrow=False, font=dict(color="#38bdf8", size=13))
    fig.add_annotation(x=75, y=18, text="Best Balance", showarrow=False, font=dict(color="#4ade80", size=13))
    fig.add_annotation(x=25, y=82, text="Needs Caution", showarrow=False, font=dict(color="#f87171", size=13))
    fig.add_annotation(x=75, y=82, text="High Upside / Higher Risk", showarrow=False, font=dict(color="#fbbf24", size=13))

    fig.update_layout(
        title=dict(text="Market Positioning", font=dict(size=20, color="#f8fafc")),
        template="plotly_dark",
        height=500,
        margin=dict(l=50, r=30, t=70, b=55),
        paper_bgcolor="rgba(15,23,42,0)",
        plot_bgcolor="rgba(15,23,42,0)",
        xaxis=dict(title="Investment Strength", range=[0, 100], showticklabels=False, gridcolor="rgba(148,163,184,.18)"),
        yaxis=dict(title="Risk Level", range=[100, 0], showticklabels=False, gridcolor="rgba(148,163,184,.18)"),
        legend=dict(orientation="h", y=1.14, x=1, xanchor="right"),
        font=dict(color="#e5e7eb"),
    )
    return fig


def make_home_trend(trend_df, zip_a, zip_b, city_a, city_b, state_a=None, state_b=None):
    fig = go.Figure()
    series = [
        (zip_a, state_a, "#a855f7", city_a),
        (zip_b, state_b, "#22c55e", city_b),
    ]
    for z, st_code, color, city in series:
        tmp = trend_df[trend_df["zip_code"].astype(str) == str(z)].copy()
        if st_code is not None and "state" in tmp.columns:
            tmp = tmp[tmp["state"].astype(str) == str(st_code)]
        if tmp.empty:
            continue
        fig.add_trace(go.Scatter(
            x=tmp["report_date"],
            y=tmp["home_value"],
            mode="lines+markers",
            name=f"ZIP {z} - {city}",
            line=dict(width=4, color=color),
            marker=dict(size=5),
            hovertemplate=f"<b>ZIP {z}</b><br>Date: %{{x}}<br>Home Value: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        template="plotly_dark",
        height=460,
        paper_bgcolor="rgba(15,23,42,0)",
        plot_bgcolor="rgba(15,23,42,0)",
        margin=dict(l=20, r=20, t=15, b=20),
        xaxis_title="Date",
        yaxis_title="Home Value",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
        font=dict(color="#e5e7eb"),
        xaxis=dict(gridcolor="rgba(148,163,184,.18)"),
        yaxis=dict(gridcolor="rgba(148,163,184,.18)"),
        legend=dict(orientation="h", y=-0.18, x=0.25),
    )
    return fig


def affordability_grade(row) -> str:
    # Lower home value is better for affordability. price_rank increases as home value increases.
    return letter_grade(100 - safe_float(row["price_rank"]))


def market_stability_grade(row) -> str:
    return letter_grade(row["base_family_stability_score"])


def grade_badge(value: str, color: str = "") -> str:
    color_cls = color if color else grade_color_class(value)
    return f'<span class="grade-badge {color_cls}">{esc(value)}</span>'


def at_glance_row(label: str, sub: str, val_a: str, val_b: str, winner_label: str, tooltip: str = "") -> str:
    info = f'<span class="info-dot" title="{esc(tooltip)}">i</span>' if tooltip else ""
    return f"""
    <tr>
        <td><b>{esc(label)}</b>{info}<div class="factor-sub">{esc(sub)}</div></td>
        <td>{val_a}</td>
        <td>{val_b}</td>
        <td><span class="lead-pill">{esc(winner_label)}</span></td>
    </tr>
    """


def row_identity(row) -> str:
    return f"{row['zip_code']} - {row['city']}"


def same_row(a, b) -> bool:
    return str(a["zip_code"]) == str(b["zip_code"]) and str(a["state"]) == str(b["state"])


def who_leads(winner_row, zip_a_data, zip_b_data) -> str:
    if same_row(winner_row, zip_a_data):
        return str(zip_a_data["city"])
    if same_row(winner_row, zip_b_data):
        return str(zip_b_data["city"])
    return "Tie"


def five_year_change(trend_df, zip_code: str, state_code: str | None = None):
    tmp = trend_df[trend_df["zip_code"].astype(str) == str(zip_code)].copy()
    if state_code is not None and "state" in tmp.columns:
        tmp = tmp[tmp["state"].astype(str) == str(state_code)]
    if tmp.empty:
        return None
    tmp["report_date"] = pd.to_datetime(tmp["report_date"])
    tmp = tmp.sort_values("report_date")
    latest = tmp.iloc[-1]
    target_date = latest["report_date"] - pd.DateOffset(years=5)
    base = tmp[tmp["report_date"] >= target_date]
    if base.empty:
        base_row = tmp.iloc[0]
    else:
        base_row = base.iloc[0]
    if pd.isna(base_row["home_value"]) or float(base_row["home_value"]) == 0:
        return None
    return ((float(latest["home_value"]) - float(base_row["home_value"])) / float(base_row["home_value"])) * 100

def build_zip_context(row) -> str:
    return f"""
ZIP Code: {row.get('zip_code')}
City: {row.get('city')}
State: {row.get('state')}
County: {row.get('county_name')}
Current Home Value: {money(row.get('current_home_value'))}
YoY Growth: {pct(row.get('yoy_growth_pct'))}
5-Year Appreciation: {pct(row.get('appreciation_5yr_pct'))}
Investment Potential Grade: {letter_grade(row.get('investment_fit_score'))}
Family Rating Grade: {letter_grade(row.get('family_fit_score'))}
School Grade: {row.get('school_grade')}
Community Safety Grade: {row.get('city_safety_grade')}
Safety Data Level: {row.get('safety_data_level')}
Enhanced Use Case: {row.get('enhanced_use_case')}
"""


def generate_bedrock_answer(user_question: str, zip_a_row, zip_b_row) -> str:
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    prompt = f"""
You are an AI real estate ZIP advisor.

Your job:
Answer the user's question by comparing only the two ZIP codes below.

Important rules:
- Use only the provided data.
- Do not invent missing facts.
- Do not guarantee future returns.
- Do not predict exact future home values.
- Do not claim a ZIP will produce a specific future return.
- If the user asks for future returns, explain that future returns cannot be guaranteed.
- You may discuss historical appreciation, recent growth, affordability, school grade, family rating, investment potential, and city-level safety.
- Safety is city-level only, not ZIP-level. Mention this limitation when safety matters.
- Keep the answer practical, clear, and professional.

User question:
{user_question}

ZIP 1:
{build_zip_context(zip_a_row)}

ZIP 2:
{build_zip_context(zip_b_row)}

Response style:
- Do not use Markdown formatting.
- Do not use asterisks.
- Do not use numbered headings like "1.", "2.", "3.".
- Use short executive-style sections.
- Keep the answer concise and product-ready.

Answer format exactly:

EXECUTIVE RECOMMENDATION

Answer:
Write 2 to 3 clear sentences answering the user's question directly.

Confidence:
High, Medium, or Low. Explain in one short sentence why.

Best Fit:
State which ZIP is better for the user's stated goal. If the user goal is unclear, separate the answer into Family Fit and Investment Fit.

Key Drivers:
- Driver 1
- Driver 2
- Driver 3

Trade-Offs / Risks:
- Risk 1
- Risk 2

Important Limitation:
Mention if future returns cannot be guaranteed, if the question asks about future returns.
Mention that safety is city-level only if safety is part of the answer.

Final Recommendation:
One practical recommendation sentence.
"""

    try:
        response = client.converse(
            modelId="amazon.nova-lite-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 650,
                "temperature": 0.2
            }
        )
    
        return response["output"]["message"]["content"][0]["text"]

    except ClientError as e:
        return f"AI recommendation unavailable. Bedrock error: {e.response['Error']['Message']}"
    except Exception as e:
        return f"AI recommendation unavailable. Error: {str(e)}"

# =========================================================
# LOAD AVAILABLE STATES
# =========================================================
with st.spinner("Loading available states from Athena..."):
    states_df = load_states()

if states_df.empty:
    st.error("No states found with at least two complete ZIP records.")
    st.stop()

# =========================================================
# HERO
# =========================================================
render("""
<div class="card hero" style="grid-template-columns: 1fr;">
    <div>
        <div class="hero-title">Real Estate Intelligence Platform</div>
        <div class="hero-subtitle">
            Discover the best ZIP code for investment, family living, and long-term growth.
        </div>
        <div class="data-note">Analysis includes only ZIP codes with complete data across all key factors.</div>
        <div class="data-status">Data Accuracy Rule: Missing-data ZIPs are excluded from comparison.</div>
    </div>
</div>
""")

# =========================================================
# FILTERS
# =========================================================
states = sorted(states_df["state"].dropna().astype(str).unique())

render("""
<div class="card panel" style="margin-bottom: 18px;">
    <div class="panel-title" style="margin-bottom: 6px;">Compare Two ZIP Codes</div>
    <div class="factor-sub">Choose any two ZIP codes. They can be from the same state or different states.</div>
    <div class="filter-note">Note: Investment and family ratings use ZIP-level housing and school data. Community safety is displayed separately as a city-level indicator.</div>
</div>
""")

f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
with f1:
    state_a = st.selectbox(
        "State for ZIP 1",
        states,
        index=states.index("TX") if "TX" in states else 0,
        key="state_a",
    )

with f3:
    default_state_b = states.index("TX") if "TX" in states else 0
    state_b = st.selectbox(
        "State for ZIP 2",
        states,
        index=default_state_b,
        key="state_b",
    )

with st.spinner(f"Loading complete ZIP records for {state_a}..."):
    state_df_a = load_scores_for_state(state_a)

with st.spinner(f"Loading complete ZIP records for {state_b}..."):
    state_df_b = load_scores_for_state(state_b)

if state_df_a.empty:
    st.error(f"No complete ZIP records found for {state_a}.")
    st.stop()
if state_df_b.empty:
    st.error(f"No complete ZIP records found for {state_b}.")
    st.stop()

state_df_a["zip_code"] = state_df_a["zip_code"].astype(str)
state_df_b["zip_code"] = state_df_b["zip_code"].astype(str)
zip_options_a = sorted(state_df_a["zip_code"].dropna().unique())
zip_options_b = sorted(state_df_b["zip_code"].dropna().unique())

with f2:
    zip_a = st.selectbox("ZIP Code 1", zip_options_a, index=0, key="zip_a")

with f4:
    default_b = 1 if (state_a == state_b and len(zip_options_b) > 1) else 0
    zip_b = st.selectbox("ZIP Code 2", zip_options_b, index=default_b, key="zip_b")

if state_a == state_b and zip_a == zip_b:
    st.warning("Select two different ZIP codes for comparison.")
    st.stop()

zip_a_data = state_df_a[state_df_a["zip_code"] == str(zip_a)].iloc[0]
zip_b_data = state_df_b[state_df_b["zip_code"] == str(zip_b)].iloc[0]

selected_states_label = state_a if state_a == state_b else f"{state_a} vs {state_b}"
state_name_a = zip_a_data["state_name"] if "state_name" in zip_a_data else state_a
state_name_b = zip_b_data["state_name"] if "state_name" in zip_b_data else state_b

# Combined dataframe used only for bottom ranking tables.
state_df = pd.concat([state_df_a, state_df_b], ignore_index=True).drop_duplicates(subset=["state", "zip_code"])
state_name = selected_states_label

# =========================================================
# AI ZIP ADVISOR - SIMPLE INPUT
# =========================================================

st.markdown("### Ask AI about these ZIP codes")

q_col, btn_col = st.columns([8.5, 1.5], vertical_alignment="bottom")

with q_col:
    ai_question = st.text_input(
        "Ask your question",
        placeholder="Example: I have a family with 2 kids. Which ZIP is better?",
        key="ai_question_box"
    )

with btn_col:
    
    generate_ai = st.button(
        "Ask AI",
        key="generate_ai",
        use_container_width=True
    )

if generate_ai:
    if not ai_question.strip():
        st.warning("Please enter a question before asking AI.")
    else:
        with st.spinner("AI is analyzing the selected ZIP codes..."):
            ai_answer = generate_bedrock_answer(
                ai_question,
                zip_a_data,
                zip_b_data
            )

        render(f"""
        <div class="assistant-box">
            <div class="assistant-title">AI Recommendation</div>
            <div class="assistant-placeholder">
                {esc(ai_answer).replace(chr(10), "<br>")}
            </div>
        </div>
        """)

# =========================================================
# DECISION LOGIC
# =========================================================
inv_winner = winner_by(zip_a_data, zip_b_data, "investment_fit_score")
inv_loser = zip_b_data if str(inv_winner["zip_code"]) == str(zip_a_data["zip_code"]) and str(inv_winner["state"]) == str(zip_a_data["state"]) else zip_a_data

fam_winner = winner_by(zip_a_data, zip_b_data, "family_fit_score")
fam_loser = zip_b_data if str(fam_winner["zip_code"]) == str(zip_a_data["zip_code"]) and str(fam_winner["state"]) == str(zip_a_data["state"]) else zip_a_data

# =========================================================
# DECISION SUMMARY - INVESTMENT AND FAMILY
# =========================================================
def option_tag(row, winner_row, zip_a_ref):
    is_winner = str(row["zip_code"]) == str(winner_row["zip_code"]) and str(row["state"]) == str(winner_row["state"])
    return "Better Option" if is_winner else "Good Option"

def tag_class(row, winner_row):
    is_winner = str(row["zip_code"]) == str(winner_row["zip_code"]) and str(row["state"]) == str(winner_row["state"])
    return "better" if is_winner else "good"

render(f"""
<div class="decision-grid">
    <div class="decision-card decision-investment">
        <div class="decision-header">
            <div class="decision-icon invest">I</div>
            <div>
                <div class="decision-title">Decision Summary - Investment</div>
                <div class="decision-sub">Separate recommendation for investment potential</div>
            </div>
        </div>
        <div class="recommended-box">
            <div class="recommended-label">Recommended for Investment</div>
            <div class="recommended-title">{esc(inv_winner['zip_code'])} - {esc(inv_winner['city'])}<span class="choice-badge">Stronger Choice</span></div>
        </div>
        <div class="ai-mini-box">
            <div class="ai-mini-title">AI Insight</div>
            <div class="ai-mini-text">ZIP {esc(inv_winner['zip_code'])} - {esc(inv_winner['city'])} shows stronger investment potential based on long-term appreciation, recent momentum, affordability, and school support. Community safety is shown separately and is not used in this recommendation.</div>
        </div>
        <div class="zip-choice-row">
            <div class="zip-choice"><div class="zip-choice-title">{esc(zip_a)} - {esc(zip_a_data['city'])}</div><span class="zip-choice-tag {tag_class(zip_a_data, inv_winner)}">{option_tag(zip_a_data, inv_winner, zip_a)}</span></div>
            <div class="vs-circle">vs</div>
            <div class="zip-choice"><div class="zip-choice-title">{esc(zip_b)} - {esc(zip_b_data['city'])}</div><span class="zip-choice-tag {tag_class(zip_b_data, inv_winner)}">{option_tag(zip_b_data, inv_winner, zip_a)}</span></div>
        </div>
    </div>

    <div class="decision-card decision-family">
        <div class="decision-header">
            <div class="decision-icon family">F</div>
            <div>
                <div class="decision-title">Decision Summary - Family</div>
                <div class="decision-sub">Separate recommendation for family living</div>
            </div>
        </div>
        <div class="recommended-box">
            <div class="recommended-label">Recommended for Families</div>
            <div class="recommended-title">{esc(fam_winner['zip_code'])} - {esc(fam_winner['city'])}<span class="choice-badge">Stronger Choice</span></div>
        </div>
        <div class="ai-mini-box">
            <div class="ai-mini-title">AI Insight</div>
            <div class="ai-mini-text">ZIP {esc(fam_winner['zip_code'])} - {esc(fam_winner['city'])} has the stronger family rating based on ZIP-level school quality, housing stability, appreciation, and affordability. Safety is displayed separately as a city-level indicator.</div>
        </div>
        <div class="zip-choice-row">
            <div class="zip-choice"><div class="zip-choice-title">{esc(zip_a)} - {esc(zip_a_data['city'])}</div><span class="zip-choice-tag {tag_class(zip_a_data, fam_winner)}">{option_tag(zip_a_data, fam_winner, zip_a)}</span></div>
            <div class="vs-circle">vs</div>
            <div class="zip-choice"><div class="zip-choice-title">{esc(zip_b)} - {esc(zip_b_data['city'])}</div><span class="zip-choice-tag {tag_class(zip_b_data, fam_winner)}">{option_tag(zip_b_data, fam_winner, zip_a)}</span></div>
        </div>
    </div>
</div>
""")

# =========================================================
# AT-A-GLANCE COMPARISON
# =========================================================
app_winner = winner_by(zip_a_data, zip_b_data, "appreciation_5yr_pct")
growth_winner = winner_by(zip_a_data, zip_b_data, "yoy_growth_pct")
school_winner = winner_by(zip_a_data, zip_b_data, "school_score")
safety_winner = winner_by(zip_a_data, zip_b_data, "city_safety_indicator")
afford_winner = winner_lower(zip_a_data, zip_b_data, "current_home_value")
inv_winner_for_row = winner_by(zip_a_data, zip_b_data, "investment_fit_score")
fam_winner_for_row = winner_by(zip_a_data, zip_b_data, "family_fit_score")
stability_winner = winner_by(zip_a_data, zip_b_data, "base_family_stability_score")

at_glance_rows = "".join([
    at_glance_row(
        "School Quality",
        "ZIP-level school grade",
        grade_badge(zip_a_data["school_grade"]),
        grade_badge(zip_b_data["school_grade"]),
        who_leads(school_winner, zip_a_data, zip_b_data),
        "School grade is calculated from ZIP-level school data."
    ),
    at_glance_row(
        "Investment Potential",
        "Composite grade, not an exact score",
        grade_badge(letter_grade(zip_a_data["investment_fit_score"])),
        grade_badge(letter_grade(zip_b_data["investment_fit_score"])),
        who_leads(inv_winner_for_row, zip_a_data, zip_b_data),
        "Investment Potential uses ZIP-level housing appreciation, recent growth, affordability, and school support. City-level safety is not used."
    ),
    at_glance_row(
        "Family Rating",
        "Composite grade, not an exact score",
        grade_badge(letter_grade(zip_a_data["family_fit_score"])),
        grade_badge(letter_grade(zip_b_data["family_fit_score"])),
        who_leads(fam_winner_for_row, zip_a_data, zip_b_data),
        "Family Rating uses ZIP-level school quality, housing stability, appreciation, and affordability. City-level safety is not used."
    ),
    at_glance_row(
        "Affordability",
        "Lower home value is better",
        grade_badge(affordability_grade(zip_a_data)),
        grade_badge(affordability_grade(zip_b_data)),
        who_leads(afford_winner, zip_a_data, zip_b_data),
        "Affordability grade is based on relative home value. Lower current home value is treated as more affordable."
    ),
    at_glance_row(
        "Community Safety",
        "City-level indicator only",
        f'{grade_badge(zip_a_data["city_safety_grade"])} <span class="factor-sub">City-Level</span>',
        f'{grade_badge(zip_b_data["city_safety_grade"])} <span class="factor-sub">City-Level</span>',
        who_leads(safety_winner, zip_a_data, zip_b_data),
        "Safety is currently based on city-level crime data, not ZIP-level crime data. It is shown as context only and is not used in Investment Potential or Family Rating."
    ),
    at_glance_row(
        "Market Stability",
        "Housing stability signal",
        grade_badge(market_stability_grade(zip_a_data)),
        grade_badge(market_stability_grade(zip_b_data)),
        who_leads(stability_winner, zip_a_data, zip_b_data),
        "Market Stability uses housing affordability, appreciation, and recent growth."
    ),
])

render(f"""
<div class="card at-glance-card">
    <div class="panel-title">At-a-Glance Comparison <span style="font-size:13px;color:#cbd5e1;">See how the two ZIP codes compare across key factors</span></div>
    <table class="factor-table">
        <thead>
            <tr>
                <th>Key Factors</th>
                <th><span class="dot-purple"></span> ZIP {esc(zip_a)} - {esc(zip_a_data['city'])}</th>
                <th><span class="dot-green"></span> ZIP {esc(zip_b)} - {esc(zip_b_data['city'])}</th>
                <th>Who Leads</th>
            </tr>
        </thead>
        <tbody>{at_glance_rows}</tbody>
    </table>
    <div class="small-note" style="text-align:center; margin-top:14px;">
        Grades: A+ (90-100) | A (80-89) | B (70-79) | C (60-69) | D (50-59) | F (Below 50). Higher grades are better.
    </div>
</div>
""")

# =========================================================
# HOME VALUE TREND
# =========================================================
trend = load_selected_trend(state_a, str(zip_a), state_b, str(zip_b))
fig_trend = make_home_trend(trend, zip_a, zip_b, zip_a_data["city"], zip_b_data["city"], state_a, state_b)
change_a = five_year_change(trend, str(zip_a), state_a)
change_b = five_year_change(trend, str(zip_b), state_b)
change_a_text = "N/A" if change_a is None else f"{change_a:+.1f}%"
change_b_text = "N/A" if change_b is None else f"{change_b:+.1f}%"
trend_leader = None
if change_a is not None and change_b is not None:
    trend_leader = zip_a_data if change_a >= change_b else zip_b_data

render("""
<div class="card panel" style="margin-bottom:0;">
    <div class="panel-title">Home Value Trend</div>
    <div class="factor-sub">Historical monthly home value movement for selected ZIP codes</div>
</div>
""")

trend_left, trend_right = st.columns([2.2, .8], gap="large")
with trend_left:
    st.plotly_chart(fig_trend, width="stretch", config={"displayModeBar": False})
with trend_right:
    leader_text = "Trend leader unavailable"
    if trend_leader is not None:
        leader_text = f"{trend_leader['city']} has stronger 5-year home value growth."
    render(f"""
    <div class="trend-side-card">
        <div class="grade-label">5-Year Change</div>
        <div style="margin-top:18px;">
            <div><span class="trend-dot purple-bg"></span><b>ZIP {esc(zip_a)} - {esc(zip_a_data['city'])}</b></div>
            <div class="trend-change purple">{esc(change_a_text)}</div>
            <div><span class="trend-dot green-bg"></span><b>ZIP {esc(zip_b)} - {esc(zip_b_data['city'])}</b></div>
            <div class="trend-change green">{esc(change_b_text)}</div>
        </div>
        <div class="small-note">{esc(leader_text)}</div>
    </div>
    """)

# =========================================================
# TOP ZIPS
# =========================================================
st.header(f"Top ZIP Codes - {state_name}")
ta, tb = st.columns(2)

with ta:
    st.subheader("Top 10 Investment Potential ZIPs")

    top_inv = state_df.sort_values("investment_fit_score", ascending=False).head(10)[[
        "zip_code",
        "city",
        "county_name",
        "state",
        "current_home_value",
        "investment_fit_score",
        "appreciation_5yr_pct",
        "school_grade",
        "city_safety_grade"
    ]].copy()

    top_inv["investment_grade"] = top_inv["investment_fit_score"].apply(letter_grade)
    top_inv["current_home_value"] = top_inv["current_home_value"].apply(money)
    top_inv["appreciation_5yr_pct"] = top_inv["appreciation_5yr_pct"].apply(pct)
    top_inv = top_inv.drop(columns=["investment_fit_score"])

    top_inv = top_inv.rename(columns={
        "zip_code": "ZIP",
        "city": "City",
        "county_name": "County",
        "state": "State",
        "current_home_value": "Home Value",
        "appreciation_5yr_pct": "5Y Appreciation",
        "school_grade": "School Grade",
        "city_safety_grade": "Safety Grade",
        "investment_grade": "Investment Grade"
    })

    st.dataframe(top_inv, width="stretch", hide_index=True)

with tb:
    st.subheader("Top 10 Family Rating ZIPs")

    top_fam = state_df.sort_values("family_fit_score", ascending=False).head(10)[[
        "zip_code",
        "city",
        "county_name",
        "state",
        "current_home_value",
        "family_fit_score",
        "school_grade",
        "city_safety_grade"
    ]].copy()

    top_fam["family_grade"] = top_fam["family_fit_score"].apply(letter_grade)
    top_fam["current_home_value"] = top_fam["current_home_value"].apply(money)
    top_fam = top_fam.drop(columns=["family_fit_score"])

    top_fam = top_fam.rename(columns={
        "zip_code": "ZIP",
        "city": "City",
        "county_name": "County",
        "state": "State",
        "current_home_value": "Home Value",
        "school_grade": "School Grade",
        "city_safety_grade": "Safety Grade",
        "family_grade": "Family Grade"
    })

    st.dataframe(top_fam, width="stretch", hide_index=True)

render("""
<div class="footer-note">
    Data Accuracy First: ZIPs missing required housing or school fields are excluded from analysis. Community safety is shown as a city-level indicator and is not used in composite grades.
    Built on AWS S3 + Athena + Lightsail. Source includes Zillow ZHVI and curated enrichment layers.
</div>
""")
