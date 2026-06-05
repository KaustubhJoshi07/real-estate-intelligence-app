import streamlit as st

import pandas as pd

import plotly.graph_objects as go

from pyathena import connect



# =========================================================

# PAGE CONFIG

# =========================================================

st.set_page_config(

    page_title="US Housing Intelligence Platform",

    page_icon="H",

    layout="wide",

    initial_sidebar_state="collapsed",

)



# =========================================================

# HTML RENDER HELPER

# =========================================================

def render(html: str):

    st.html(html)





# =========================================================

# CSS

# =========================================================

render("""

<style>

.stApp {

    background:

        radial-gradient(circle at top left, rgba(124,58,237,.18), transparent 30%),

        radial-gradient(circle at top right, rgba(34,197,94,.10), transparent 35%),

        linear-gradient(135deg, #050816 0%, #08111f 50%, #020617 100%);

    color: #e5e7eb;

}

.block-container {

    max-width: 1500px;

    padding-top: 1.5rem;

    padding-bottom: 4rem;

}

h1, h2, h3 {

    color: #f8fafc;

    letter-spacing: -0.03em;

}

.hero {

    padding: 28px 32px;

    border-radius: 22px;

    background: linear-gradient(135deg, rgba(15,23,42,.98), rgba(30,41,59,.86));

    border: 1px solid rgba(148,163,184,.25);

    box-shadow: 0 24px 70px rgba(0,0,0,.35);

    margin-bottom: 24px;

}

.hero-title {

    font-size: 34px;

    font-weight: 900;

    color: #f8fafc;

}

.hero-subtitle {

    margin-top: 6px;

    color: #cbd5e1;

    font-size: 16px;

}

.section-card {

    padding: 24px;

    border-radius: 22px;

    background: linear-gradient(145deg, rgba(15,23,42,.96), rgba(2,6,23,.92));

    border: 1px solid rgba(148,163,184,.22);

    box-shadow: 0 18px 55px rgba(0,0,0,.30);

    margin-top: 22px;

    margin-bottom: 22px;

}

.section-header {

    display: flex;

    justify-content: space-between;

    gap: 16px;

    align-items: center;

    margin-bottom: 18px;

}

.section-title {

    font-size: 26px;

    font-weight: 900;

    color: #f8fafc;

}

.section-subtitle {

    color: #94a3b8;

    font-size: 14px;

    margin-top: 4px;

}

.badge-purple {

    background: linear-gradient(135deg, #7c3aed, #4c1d95);

    color: #f5f3ff;

    padding: 10px 16px;

    border-radius: 14px;

    font-weight: 800;

    border: 1px solid rgba(196,181,253,.35);

}

.badge-green {

    background: linear-gradient(135deg, #16a34a, #14532d);

    color: #dcfce7;

    padding: 10px 16px;

    border-radius: 14px;

    font-weight: 800;

    border: 1px solid rgba(134,239,172,.35);

}

.zip-card {

    padding: 18px;

    border-radius: 18px;

    background: linear-gradient(145deg, rgba(15,23,42,.94), rgba(15,23,42,.66));

    border: 1px solid rgba(148,163,184,.22);

    margin-bottom: 14px;

}

.zip-purple {

    font-size: 20px;

    font-weight: 900;

    color: #c084fc;

    margin-bottom: 12px;

}

.zip-green {

    font-size: 20px;

    font-weight: 900;

    color: #4ade80;

    margin-bottom: 12px;

}

.metric-grid {

    display: grid;

    grid-template-columns: repeat(4, minmax(0, 1fr));

    gap: 12px;

}

.metric-card {

    min-height: 96px;

    padding: 14px;

    border-radius: 15px;

    background: linear-gradient(145deg, rgba(15,23,42,.98), rgba(30,41,59,.75));

    border: 1px solid rgba(148,163,184,.28);

}

.metric-label {

    font-size: 12px;

    color: #cbd5e1;

    font-weight: 800;

    margin-bottom: 10px;

}

.metric-value {

    font-size: 24px;

    color: #ffffff;

    font-weight: 950;

    white-space: nowrap;

}

.summary-card {

    padding: 20px;

    border-radius: 18px;

    background: linear-gradient(145deg, rgba(15,23,42,.96), rgba(2,6,23,.90));

    border: 1px solid rgba(148,163,184,.22);

    min-height: 410px;

}

.summary-title {

    font-size: 20px;

    font-weight: 900;

    color: #f8fafc;

    margin-bottom: 16px;

}

.summary-line {

    padding: 13px 14px;

    border-radius: 14px;

    background: rgba(15,23,42,.95);

    border: 1px solid rgba(148,163,184,.20);

    margin-bottom: 12px;

    color: #e5e7eb;

    font-weight: 650;

}

.insight-purple {

    margin-top: 14px;

    padding: 16px;

    border-radius: 14px;

    color: #d8b4fe;

    background: rgba(88,28,135,.20);

    border: 1px solid rgba(168,85,247,.55);

    font-weight: 800;

}

.insight-green {

    margin-top: 14px;

    padding: 16px;

    border-radius: 14px;

    color: #86efac;

    background: rgba(20,83,45,.22);

    border: 1px solid rgba(34,197,94,.55);

    font-weight: 800;

}

[data-testid="stSelectbox"] label {

    color: #cbd5e1 !important;

    font-weight: 800 !important;

}

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





def safe_float(x):

    if pd.isna(x):

        return 0.0

    return float(x)



def investment_opportunity(row):

    investment_score = safe_float(row["enhanced_investment_score"])

    appreciation_rank = safe_float(row["appreciation_rank"])

    growth_rank = safe_float(row["growth_rank"])



    opportunity = (

        investment_score * 0.50

        + appreciation_rank * 0.30

        + growth_rank * 0.20

    )



    return min(100, max(0, opportunity))





def investment_risk(row):

    price_rank = safe_float(row["price_rank"])

    negative_growth = max(0, -safe_float(row["yoy_growth_pct"]))

    low_family_stability = 100 - safe_float(row["family_stability_score"])



    risk = (

        price_rank * 0.45

        + negative_growth * 4

        + low_family_stability * 0.25

    )



    return min(100, max(0, risk))



def metric_card(label, value):

    return f"""

    <div class="metric-card">

        <div class="metric-label">{label}</div>

        <div class="metric-value">{value}</div>

    </div>

    """





def zip_metric_block(title, color_class, metrics):

    cards = "".join(metric_card(label, value) for label, value in metrics)

    return f"""

    <div class="zip-card">

        <div class="{color_class}">{title}</div>

        <div class="metric-grid">

            {cards}

        </div>

    </div>

    """





def winner_by(a, b, metric):

    return a if safe_float(a[metric]) >= safe_float(b[metric]) else b





def loser_by(a, b, metric):

    return b if safe_float(a[metric]) >= safe_float(b[metric]) else a





def investment_reason(winner, loser):

    score_gap = safe_float(winner["enhanced_investment_score"]) - safe_float(loser["enhanced_investment_score"])

    app_gap = safe_float(winner["appreciation_5yr_pct"]) - safe_float(loser["appreciation_5yr_pct"])

    yoy_gap = safe_float(winner["yoy_growth_pct"]) - safe_float(loser["yoy_growth_pct"])

    price_gap = safe_float(winner["current_home_value"]) - safe_float(loser["current_home_value"])



    reasons = [

        f"{score_gap:.1f} points higher investment score",

        f"{abs(app_gap):.1f}% difference in 5-year appreciation",

        f"{abs(yoy_gap):.1f}% stronger recent growth profile",

        f"{money(abs(price_gap))} home value difference",

    ]



    insight = (

        f"{winner['city']} is the stronger investment choice because it has a better combined score "

        f"across growth, price movement, and long-term appreciation."

    )

    return reasons, insight





def family_reason(winner, loser):

    score_gap = safe_float(winner["enhanced_family_score"]) - safe_float(loser["enhanced_family_score"])

    price_gap = safe_float(winner["current_home_value"]) - safe_float(loser["current_home_value"])

    yoy_gap = abs(safe_float(winner["yoy_growth_pct"])) - abs(safe_float(loser["yoy_growth_pct"]))



    reasons = [

        f"{score_gap:.1f} points higher family stability score",

        f"{money(abs(price_gap))} home value difference",

        f"{abs(yoy_gap):.1f}% difference in recent growth stability",

    ]



    insight = (

        f"{winner['city']} offers a stronger balance of livability, stability, "

        f"and long-term housing resilience."

    )

    return reasons, insight





def summary_panel(title, winner, reasons, insight, theme):

    line_html = "".join(f'<div class="summary-line">{r}</div>' for r in reasons)

    insight_class = "insight-purple" if theme == "purple" else "insight-green"



    return f"""

    <div class="summary-card">

        <div class="summary-title">{title}</div>

        <p><b>ZIP {winner['zip_code']} - {winner['city']}</b> is the stronger choice.</p>

        {line_html}

        <div class="{insight_class}">{insight}</div>

    </div>

    """





def make_driver_chart(title, labels, a_vals, b_vals, zip_a, zip_b, color_a, color_b):

    fig = go.Figure()



    fig.add_trace(go.Bar(

        y=labels,

        x=a_vals,

        orientation="h",

        name=f"ZIP {zip_a}",

        marker=dict(color=color_a, line=dict(color="rgba(255,255,255,.25)", width=1)),

        text=[f"{v:.1f}" for v in a_vals],

        textposition="outside",

        hovertemplate="%{y}: %{x:.1f}<extra></extra>",

    ))



    fig.add_trace(go.Bar(

        y=labels,

        x=b_vals,

        orientation="h",

        name=f"ZIP {zip_b}",

        marker=dict(color=color_b, line=dict(color="rgba(255,255,255,.20)", width=1)),

        text=[f"{v:.1f}" for v in b_vals],

        textposition="outside",

        hovertemplate="%{y}: %{x:.1f}<extra></extra>",

    ))



    fig.update_layout(

        title=dict(text=title, font=dict(size=18, color="#f8fafc")),

        template="plotly_dark",

        barmode="group",

        height=430,

        margin=dict(l=135, r=70, t=70, b=40),

        paper_bgcolor="rgba(15,23,42,0)",

        plot_bgcolor="rgba(15,23,42,0)",

        legend=dict(

            orientation="h",

            y=1.13,

            x=1,

            xanchor="right",

            font=dict(color="#e5e7eb"),

        ),

        xaxis=dict(

            gridcolor="rgba(148,163,184,.20)",

            zerolinecolor="rgba(148,163,184,.35)",

            tickfont=dict(color="#cbd5e1"),

        ),

        yaxis=dict(

            tickfont=dict(color="#f8fafc", size=12),

            autorange="reversed",

        ),

        font=dict(color="#e5e7eb"),

    )

    return fig



def make_opportunity_risk_matrix(zip_a_data, zip_b_data):

    fig = go.Figure()



    for row, color in [

        (zip_a_data, "#a855f7"),

        (zip_b_data, "#22c55e")

    ]:

        fig.add_trace(

            go.Scatter(

                x=[investment_opportunity(row)],

                y=[investment_risk(row)],

                mode="markers+text",

                text=[f"ZIP {row['zip_code']}"],

                textposition="top center",

                marker=dict(

                    size=34,

                    color=color,

                    line=dict(width=2, color="white")

                ),

                name=f"ZIP {row['zip_code']} - {row['city']}",

            )

        )



    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100, line=dict(color="rgba(255,255,255,.25)", dash="dash"))

    fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50, line=dict(color="rgba(255,255,255,.25)", dash="dash"))



    fig.add_annotation(x=75, y=25, text="Strong Buy", showarrow=False, font=dict(color="#86efac", size=14))

    fig.add_annotation(x=75, y=75, text="Aggressive Bet", showarrow=False, font=dict(color="#fde68a", size=14))

    fig.add_annotation(x=25, y=25, text="Stable Hold", showarrow=False, font=dict(color="#93c5fd", size=14))

    fig.add_annotation(x=25, y=75, text="Avoid / Monitor", showarrow=False, font=dict(color="#fca5a5", size=14))



    fig.update_layout(

        title="Opportunity vs Risk Matrix",

        template="plotly_dark",

        height=430,

        margin=dict(l=50, r=30, t=70, b=50),

        paper_bgcolor="rgba(15,23,42,0)",

        plot_bgcolor="rgba(15,23,42,0)",

        xaxis=dict(title="Investment Opportunity", range=[0, 100], gridcolor="rgba(148,163,184,.18)"),

        yaxis=dict(title="Market Risk", range=[100, 0], gridcolor="rgba(148,163,184,.18)"),

        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),

        font=dict(color="#e5e7eb"),

    )



    return fig



# =========================================================

# LOAD DATA

# =========================================================

with st.spinner("Loading housing intelligence layer from Athena..."):

    scores = run_query("""

        SELECT
            zip_code,
            city,
            state,
            current_home_value,
            yoy_growth_pct,
            appreciation_5yr_pct,
            state_name,
            county_name,
            investment_score,
            enhanced_investment_score,

            family_stability_score,
            family_safety_score,
            school_score,
            enhanced_family_score,

            enhanced_use_case

        FROM pbi_zip_scores_enriched

        WHERE current_home_value IS NOT NULL

    """)



# =========================================================

# HERO

# =========================================================

render("""

<div class="hero">

    <div class="hero-title">Real Estate Intelligence Platform</div>

    <div class="hero-subtitle">

        Data-driven ZIP code comparison for investment potential, family stability, and housing market intelligence.

    </div>

</div>

""")



# =========================================================

# FILTERS

# =========================================================

states = sorted(scores["state"].dropna().unique())



f1, f2, f3 = st.columns([1, 1, 1])



with f1:

    selected_state = st.selectbox(

        "Select State",

        states,

        index=states.index("TX") if "TX" in states else 0,

    )



state_df = scores[scores["state"] == selected_state].copy()

zip_options = sorted(state_df["zip_code"].dropna().unique())

state_name = state_df["state_name"].dropna().iloc[0] if not state_df.empty else selected_state



with f2:

    zip_a = st.selectbox("ZIP Code A", zip_options)



with f3:

    zip_b = st.selectbox("ZIP Code B", zip_options, index=1 if len(zip_options) > 1 else 0)



zip_a_data = state_df[state_df["zip_code"] == zip_a].iloc[0]

zip_b_data = state_df[state_df["zip_code"] == zip_b].iloc[0]



# =========================================================

# KPI STRIP

# =========================================================

render(f"""

<div class="section-card">

    <div class="metric-grid">

        {metric_card("ZIP Codes Indexed", f"{len(scores):,}")}

        {metric_card("States Covered", f"{scores['state'].nunique():,}")}

        {metric_card("Avg Home Value", money(scores["current_home_value"].mean()))}

        {metric_card("Avg Investment Score", num(scores["investment_score"].mean()))}

    </div>

</div>

""")



# =========================================================

# DECISION LOGIC

# =========================================================

inv_winner = winner_by(zip_a_data, zip_b_data, "enhanced_investment_score")

inv_loser = loser_by(zip_a_data, zip_b_data, "enhanced_investment_score")

fam_winner = winner_by(zip_a_data, zip_b_data, "enhanced_family_score")

fam_loser = loser_by(zip_a_data, zip_b_data, "enhanced_family_score")



inv_reasons, inv_insight = investment_reason(inv_winner, inv_loser)

fam_reasons, fam_insight = family_reason(fam_winner, fam_loser)



# =========================================================

# INVESTMENT SECTION

# =========================================================

render(f"""

<div class="section-card">

    <div class="section-header">

        <div>

            <div class="section-title">Investment Analysis</div>

            <div class="section-subtitle">Compare investment potential and financial growth indicators</div>

        </div>

        <div class="badge-purple">Winner: ZIP {inv_winner['zip_code']} - {inv_winner['city']}</div>

    </div>

</div>

""")



ia, ib = st.columns(2)



with ia:

    render(zip_metric_block(

        f"ZIP {zip_a} - {zip_a_data['city']}",

        "zip-purple",

        [

            ("Investment Score", num(zip_a_data["enhanced_investment_score"])),

            ("5Y Appreciation", pct(zip_a_data["appreciation_5yr_pct"])),

            ("1Y Growth", pct(zip_a_data["yoy_growth_pct"])),

            ("Home Value", money(zip_a_data["current_home_value"])),

        ],

    ))



with ib:

    render(zip_metric_block(

        f"ZIP {zip_b} - {zip_b_data['city']}",

        "zip-green",

        [

            ("Investment Score", num(zip_b_data["enhanced_investment_score"])),

            ("5Y Appreciation", pct(zip_b_data["appreciation_5yr_pct"])),

            ("1Y Growth", pct(zip_b_data["yoy_growth_pct"])),

            ("Home Value", money(zip_b_data["current_home_value"])),

        ],

    ))



chart_col, summary_col = st.columns([1.7, 1])



with chart_col:

    fig_inv = make_opportunity_risk_matrix(zip_a_data, zip_b_data)



    st.plotly_chart(

        fig_inv,

        use_container_width=True,

        config={"displayModeBar": False}

    )

    st.caption(

        "Ideal investment markets appear in the upper-right quadrant where opportunity is high and risk is low."

    )

with summary_col:

    render(summary_panel("Investment Summary", inv_winner, inv_reasons, inv_insight, "purple"))



# =========================================================

# FAMILY SECTION

# =========================================================

render(f"""

<div class="section-card">

    <div class="section-header">

        <div>

            <div class="section-title">Family Stability Analysis</div>

            <div class="section-subtitle">Compare livability, stability, and long-term family housing factors</div>

        </div>

        <div class="badge-green">Winner: ZIP {fam_winner['zip_code']} - {fam_winner['city']}</div>

    </div>

</div>

""")



fa, fb = st.columns(2)



with fa:

    render(zip_metric_block(

        f"ZIP {zip_a} - {zip_a_data['city']}",

        "zip-green",

        [

            ("Family Score", num(zip_a_data["enhanced_family_score"])),

            ("Home Value", money(zip_a_data["current_home_value"])),

            ("1Y Growth", pct(zip_a_data["yoy_growth_pct"])),

            ("5Y Appreciation", pct(zip_a_data["appreciation_5yr_pct"])),

        ],

    ))



with fb:

    render(zip_metric_block(

        f"ZIP {zip_b} - {zip_b_data['city']}",

        "zip-green",

        [

            ("Family Score", num(zip_b_data["enhanced_family_score"])),

            ("Home Value", money(zip_b_data["current_home_value"])),

            ("1Y Growth", pct(zip_b_data["yoy_growth_pct"])),

            ("5Y Appreciation", pct(zip_b_data["appreciation_5yr_pct"])),

        ],

    ))



chart_col, summary_col = st.columns([1.7, 1])



with chart_col:

    fig_fam = make_driver_chart(

        "Family Stability Driver Comparison",

        ["Family Score", "Home Value ($K)", "1Y Growth (%)", "5Y Appreciation (%)"],

        [

            safe_float(zip_a_data["enhanced_family_score"]),

            safe_float(zip_a_data["current_home_value"]) / 1000,

            safe_float(zip_a_data["yoy_growth_pct"]),

            safe_float(zip_a_data["appreciation_5yr_pct"]),

        ],

        [

            safe_float(zip_b_data["enhanced_family_score"]),

            safe_float(zip_b_data["current_home_value"]) / 1000,

            safe_float(zip_b_data["yoy_growth_pct"]),

            safe_float(zip_b_data["appreciation_5yr_pct"]),

        ],

        zip_a,

        zip_b,

        "#4ade80",

        "#f59e0b",

    )

    st.plotly_chart(fig_fam, use_container_width=True, config={"displayModeBar": False})



with summary_col:

    render(summary_panel("Family Stability Summary", fam_winner, fam_reasons, fam_insight, "green"))



# =========================================================

# HOME VALUE TREND

# =========================================================

render("""

<div class="section-card">

    <div class="section-title">Home Value Trend</div>

    <div class="section-subtitle">Historical monthly movement for selected ZIP codes</div>

</div>

""")



trend = run_query(f"""

    SELECT

        CAST(report_date AS DATE) AS report_date,

        CAST(zip_code AS VARCHAR) AS zip_code,

        home_value

    FROM pbi_zip_monthly

    WHERE state = '{selected_state}'

      AND CAST(zip_code AS VARCHAR) IN ('{zip_a}', '{zip_b}')

    ORDER BY report_date

""")



fig_trend = go.Figure()



for z, color in [(zip_a, "#a855f7"), (zip_b, "#22c55e")]:

    tmp = trend[trend["zip_code"] == z]

    if tmp.empty:

        continue



    city = zip_a_data["city"] if z == zip_a else zip_b_data["city"]



    fig_trend.add_trace(go.Scatter(

        x=tmp["report_date"],

        y=tmp["home_value"],

        mode="lines",

        name=f"ZIP {z} - {city}",

        line=dict(width=4, color=color),

        hovertemplate=f"<b>ZIP {z}</b><br>Date: %{{x}}<br>Home Value: $%{{y:,.0f}}<extra></extra>",

    ))



fig_trend.update_layout(

    template="plotly_dark",

    height=500,

    paper_bgcolor="rgba(15,23,42,0)",

    plot_bgcolor="rgba(15,23,42,0)",

    margin=dict(l=20, r=20, t=35, b=20),

    xaxis_title="Date",

    yaxis_title="Home Value",

    yaxis_tickformat="$,.0f",

    hovermode="x unified",

    font=dict(color="#e5e7eb"),

    xaxis=dict(gridcolor="rgba(148,163,184,.18)"),

    yaxis=dict(gridcolor="rgba(148,163,184,.18)"),

)

st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})



# =========================================================

# FULL COMPARISON

# =========================================================

st.header("Full Metric Comparison")



comparison = pd.DataFrame(

    {

        "Metric": [

            "City",

            "County",

            "Current Home Value",

            "1-Year Growth",

            "5-Year Appreciation",

            "Investment Score",

            "Family Stability Score",

            "Recommended Use Case",

        ],

        f"ZIP {zip_a}": [

            zip_a_data["city"],

            zip_a_data["county_name"],

            money(zip_a_data["current_home_value"]),

            pct(zip_a_data["yoy_growth_pct"]),

            pct(zip_a_data["appreciation_5yr_pct"]),

            num(zip_a_data["enhanced_investment_score"]),

            num(zip_a_data["enhanced_family_score"]),

            zip_a_data["enhanced_use_case"],

        ],

        f"ZIP {zip_b}": [

            zip_b_data["city"],

            zip_b_data["county_name"],

            money(zip_b_data["current_home_value"]),

            pct(zip_b_data["yoy_growth_pct"]),

            pct(zip_b_data["appreciation_5yr_pct"]),

            num(zip_b_data["investment_score"]),

            num(zip_b_data["family_stability_score"]),

            zip_b_data["enhanced_use_case"],

        ],

    }

)



st.dataframe(comparison, use_container_width=True, hide_index=True)



# =========================================================

# TOP ZIPS

# =========================================================

st.header(f"Top ZIP Codes - {state_name} ({selected_state})")



ta, tb = st.columns(2)



with ta:

    st.subheader("Top 10 Investment ZIPs")

    top_inv = state_df.sort_values("enhanced_investment_score", ascending=False).head(10)[

        ["zip_code", "city", "county_name", "current_home_value", "investment_score", "appreciation_5yr_pct"]

    ].copy()

    top_inv["current_home_value"] = top_inv["current_home_value"].apply(money)

    top_inv["appreciation_5yr_pct"] = top_inv["appreciation_5yr_pct"].apply(pct)

    st.dataframe(top_inv, use_container_width=True, hide_index=True)



with tb:

    st.subheader("Top 10 Family Stability ZIPs")

    top_fam = state_df.sort_values("enhanced_family_score", ascending=False).head(10)[

        ["zip_code", "city", "county_name", "current_home_value", "family_stability_score", "yoy_growth_pct"]

    ].copy()

    top_fam["current_home_value"] = top_fam["current_home_value"].apply(money)

    top_fam["yoy_growth_pct"] = top_fam["yoy_growth_pct"].apply(pct)

    st.dataframe(top_fam, use_container_width=True, hide_index=True)



st.caption("US Housing Intelligence Platform | Built on AWS S3 + Athena + Lightsail | Source: Zillow ZHVI")
