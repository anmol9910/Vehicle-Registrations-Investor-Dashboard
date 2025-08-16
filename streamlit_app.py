import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Vahan Registrations – Investor View", layout="wide")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    cat_growth = pd.read_csv("category_year_bucketed_growth.csv")
    cat_detail = pd.read_csv("category_year_detail.csv")

    # Manufacturer quarterly
    mfr_q = pd.read_csv("manufacturer_quarterly.csv")
    mfr_q.rename(columns={
        "Manufacturer": "manufacturer",
        "Quarter": "quarter",
        "Quarterly_Sales": "registrations"
    }, inplace=True)
    mfr_q["quarter"] = pd.to_datetime(mfr_q["quarter"])

    # Manufacturer quarterly growth
    mfr_growth = pd.read_csv("manufacturer_quarterly_growth.csv")
    mfr_growth.rename(columns={
        "Manufacturer": "manufacturer",
        "Quarter": "quarter",
        "Quarterly_Sales": "registrations"
    }, inplace=True)
    mfr_growth["quarter"] = pd.to_datetime(mfr_growth["quarter"])

    # -------------------------------
    # Calculate missing growth columns
    # -------------------------------
    if "qoq_pct" not in mfr_growth.columns or "yoy_pct" not in mfr_growth.columns:
        mfr_growth = mfr_growth.sort_values(["manufacturer", "quarter"])
        mfr_growth["qoq_pct"] = (
            mfr_growth.groupby("manufacturer")["registrations"].pct_change() * 100
        )
        mfr_growth["yoy_pct"] = (
            mfr_growth.groupby("manufacturer")["registrations"].pct_change(periods=4) * 100
        )

    # 🔧 Fill NaN with 0 so charts don't break
    mfr_growth["qoq_pct"] = mfr_growth["qoq_pct"].fillna(0)
    mfr_growth["yoy_pct"] = mfr_growth["yoy_pct"].fillna(0)

    return cat_growth, cat_detail, mfr_q, mfr_growth


cat_growth, cat_detail, mfr_q, mfr_growth = load_data()

st.title("Vehicle Registrations (Vahan) – Investor Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Manufacturer filter
manufacturers = sorted(mfr_q["manufacturer"].dropna().unique().tolist())
sel_mfrs = st.sidebar.multiselect("Manufacturers", manufacturers, default=manufacturers[:10])

# Quarter range
if not mfr_q.empty:
    qmin, qmax = mfr_q["quarter"].min(), mfr_q["quarter"].max()
    start_q = st.sidebar.date_input("Start quarter", qmin.date())
    end_q = st.sidebar.date_input("End quarter", qmax.date())
else:
    start_q, end_q = date(2020, 1, 1), date.today()

# Category buckets
buckets = ["2W", "3W", "4W"]
sel_buckets = st.sidebar.multiselect("Vehicle category (bucket)", buckets, default=buckets)

# --- KPI Row ---
col1, col2, col3 = st.columns(3)
# Total registrations in selected quarters & manufacturers
mask_mfr = pd.Series(True, index=mfr_q.index)
if sel_mfrs:
    mask_mfr &= mfr_q["manufacturer"].isin(sel_mfrs)
mask_mfr &= mfr_q["quarter"].between(pd.to_datetime(start_q), pd.to_datetime(end_q))

tot_regs = int(mfr_q.loc[mask_mfr, "registrations"].sum())
col1.metric("Total registrations (filtered)", f"{tot_regs:,}")

# Latest quarter QoQ across selection
q_series = (mfr_q.loc[mask_mfr]
            .groupby("quarter")["registrations"].sum()
            .sort_index())
if len(q_series) >= 2:
    qoq = round(100 * (q_series.iloc[-1] - q_series.iloc[-2]) / q_series.iloc[-2], 2) if q_series.iloc[-2] else None
else:
    qoq = None
col2.metric("QoQ (total, latest)", "-" if qoq is None else f"{qoq}%")

# Category YoY latest year
if not cat_growth.empty:
    latest_year = int(cat_growth["year"].max())
    cat_latest = cat_growth[(cat_growth["year"] == latest_year) & (cat_growth["bucket"].isin(sel_buckets))]
    yoy_avg = cat_latest["yoy_pct"].mean()
else:
    yoy_avg = None
col3.metric("YoY (category, avg latest year)", "-" if pd.isna(yoy_avg) else f"{yoy_avg:.2f}%")

st.caption("Note: Category file is annual-only, so QoQ for categories is not computable from the provided data.")

# --- Charts ---
st.subheader("Manufacturer trends (Quarterly)")
mfr_view = mfr_q[mask_mfr].copy()
if sel_mfrs:
    mfr_view = mfr_view[mfr_view["manufacturer"].isin(sel_mfrs)]
fig1 = px.line(mfr_view, x="quarter", y="registrations", color="manufacturer", markers=True)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Manufacturer % change (QoQ & YoY) – latest quarter")
if not mfr_growth.empty:
    latest_q = mfr_growth["quarter"].max()
    g = mfr_growth[(mfr_growth["quarter"] == latest_q)]
    if sel_mfrs:
        g = g[g["manufacturer"].isin(sel_mfrs)]
    g = g.sort_values("registrations", ascending=False).head(30)  # top 30

    if not g.empty:
        g2 = g.melt(
            id_vars=["manufacturer"],
            value_vars=["qoq_pct", "yoy_pct"],
            var_name="metric",
            value_name="pct"
        )
        fig2 = px.bar(g2, x="manufacturer", y="pct", color="metric", barmode="group")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No manufacturer data available for the latest quarter.")
else:
    st.info("No quarterly growth data available.")

st.subheader("Category totals by year (2W / 3W / 4W)")
c = cat_growth[cat_growth["bucket"].isin(sel_buckets)].copy()
fig3 = px.bar(c, x="year", y="registrations", color="bucket", barmode="group")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Category YoY (latest year)")
if not cat_growth.empty:
    latest_year = int(cat_growth["year"].max())
    c_last = cat_growth[(cat_growth["year"] == latest_year) & (cat_growth["bucket"].isin(sel_buckets))]
    fig4 = px.bar(c_last, x="bucket", y="yoy_pct")
    st.plotly_chart(fig4, use_container_width=True)

st.caption("Data sources: Provided CSVs. Category buckets mapped heuristically: 'TWO WHEELER*' → 2W, 'THREE WHEELER*' → 3W, LMV/MMV/HMV/Light/Medium/Heavy → 4W.")

# -------------------------------
# Key Investor Insights Section
# -------------------------------
st.subheader("📊 Key Investor Insights")

# 1. Top growing manufacturer (latest quarter YoY)
if not mfr_growth.empty:
    top_yoy = mfr_growth[mfr_growth["quarter"] == latest_q].sort_values("yoy_pct", ascending=False).head(1)
    if not top_yoy.empty:
        st.markdown(f"**Top Growing Manufacturer (YoY):** {top_yoy.iloc[0]['manufacturer']} with {top_yoy.iloc[0]['yoy_pct']:.2f}% growth.")

# 2. Weakest manufacturer
if not mfr_growth.empty:
    low_yoy = mfr_growth[mfr_growth["quarter"] == latest_q].sort_values("yoy_pct", ascending=True).head(1)
    if not low_yoy.empty:
        st.markdown(f"**Weakest Manufacturer (YoY):** {low_yoy.iloc[0]['manufacturer']} with {low_yoy.iloc[0]['yoy_pct']:.2f}% decline.")

# 3. Best performing category latest year
if not cat_growth.empty:
    best_cat = cat_growth[cat_growth["year"] == latest_year].sort_values("yoy_pct", ascending=False).head(1)
    if not best_cat.empty:
        st.markdown(f"**Best Category (YoY):** {best_cat.iloc[0]['bucket']} with {best_cat.iloc[0]['yoy_pct']:.2f}% growth in {latest_year}.")

# 4. Risk Signal
if qoq is not None and qoq < 0:
    st.markdown(f"⚠️ **Risk Signal:** Overall market declined by {qoq}% in the latest quarter.")
else:
    st.markdown("✅ **Market Signal:** Overall registrations are stable or growing in the latest quarter.")
