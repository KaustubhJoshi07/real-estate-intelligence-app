import os
import streamlit as st
import pandas as pd
import plotly.express as px
from pyathena import connect

st.set_page_config(
    page_title="Real Estate Intelligence Platform",
    layout="wide"
)

ATHENA_REGION = os.environ["ATHENA_REGION"]
ATHENA_DATABASE = os.environ["ATHENA_DATABASE"]
ATHENA_S3_OUTPUT = os.environ["ATHENA_S3_OUTPUT"]

@st.cache_resource
def get_connection():
    return connect(
        region_name=ATHENA_REGION,
        schema_name=ATHENA_DATABASE,
        s3_staging_dir=ATHENA_S3_OUTPUT
    )

@st.cache_data(ttl=3600)
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

st.title("Real Estate + Economic Intelligence Platform")
st.caption("State-scoped ZIP code comparison using home value growth, appreciation, investment score, and family stability score.")

scores = run_query("""
SELECT
    CAST(zip_code AS VARCHAR) AS zip_code,
    state,
    state_name,
    city,
    county_name,
    current_home_value,
    yoy_growth_pct,
    appreciation_5yr_pct,
    investment_score,
    family_stability_score
FROM pbi_zip_scores
WHERE current_home_value IS NOT NULL
""")

states = sorted(scores["state"].dropna().unique())

selected_state = st.selectbox("Select State", states)

state_df = scores[scores["state"] == selected_state].copy()
zip_options = sorted(state_df["zip_code"].dropna().unique())

col1, col2 = st.columns(2)

with col1:
    zip_a = st.selectbox("Select ZIP A", zip_options)

with col2:
    zip_b = st.selectbox(
        "Select ZIP B",
        zip_options,
        index=1 if len(zip_options) > 1 else 0
    )

zip_a_data = state_df[state_df["zip_code"] == zip_a].iloc[0]
zip_b_data = state_df[state_df["zip_code"] == zip_b].iloc[0]

st.divider()

st.subheader("ZIP Code Comparison")

c1, c2, c3, c4 = st.columns(4)

c1.metric(f"{zip_a} Home Value", f"${zip_a_data['current_home_value']:,.0f}")
c2.metric(f"{zip_b} Home Value", f"${zip_b_data['current_home_value']:,.0f}")
c3.metric(f"{zip_a} Investment Score", f"{zip_a_data['investment_score']:.1f}")
c4.metric(f"{zip_b} Investment Score", f"{zip_b_data['investment_score']:.1f}")

comparison = pd.DataFrame({
    "Metric": [
        "City",
        "County",
        "Current Home Value",
        "1-Year Growth %",
        "5-Year Appreciation %",
        "Investment Score",
        "Family Stability Score"
    ],
    f"ZIP {zip_a}": [
        zip_a_data["city"],
        zip_a_data["county_name"],
        f"${zip_a_data['current_home_value']:,.0f}",
        f"{zip_a_data['yoy_growth_pct']:.2f}%",
        f"{zip_a_data['appreciation_5yr_pct']:.2f}%",
        f"{zip_a_data['investment_score']:.2f}",
        f"{zip_a_data['family_stability_score']:.2f}"
    ],
    f"ZIP {zip_b}": [
        zip_b_data["city"],
        zip_b_data["county_name"],
        f"${zip_b_data['current_home_value']:,.0f}",
        f"{zip_b_data['yoy_growth_pct']:.2f}%",
        f"{zip_b_data['appreciation_5yr_pct']:.2f}%",
        f"{zip_b_data['investment_score']:.2f}",
        f"{zip_b_data['family_stability_score']:.2f}"
    ]
})

st.dataframe(comparison, use_container_width=True, hide_index=True)

investment_winner = zip_a if zip_a_data["investment_score"] >= zip_b_data["investment_score"] else zip_b
family_winner = zip_a if zip_a_data["family_stability_score"] >= zip_b_data["family_stability_score"] else zip_b

col1, col2 = st.columns(2)

with col1:
    st.success(f"Best Investment ZIP: {investment_winner}")

with col2:
    st.info(f"Best Family Stability ZIP: {family_winner}")

st.divider()

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

fig = px.line(
    trend,
    x="report_date",
    y="home_value",
    color="zip_code",
    title="Home Value Trend Comparison"
)

st.plotly_chart(fig, use_container_width=True)
