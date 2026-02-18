import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="AI-Powered RFM Dashboard", layout="wide")

st.title("📊 AI-Powered Customer RFM Intelligence Dashboard")

uploaded_file = st.file_uploader("Upload Order Data CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_cols = [
        "user_id",
        "order_id",
        "order_date",
        "product_name",
        "order_value",
        "discount_given"
    ]

    if not all(col in df.columns for col in required_cols):
        st.error("CSV must contain required columns.")
        st.stop()

    df["order_date"] = pd.to_datetime(df["order_date"])

    # -----------------------
    # Analysis Date Selector
    # -----------------------
    analysis_date = st.date_input(
        "Select Analysis Date",
        value=df["order_date"].max()
    )

    snapshot_date = pd.to_datetime(analysis_date)

    # -----------------------
    # RFM Calculation
    # -----------------------
    rfm = df.groupby("user_id").agg({
        "order_date": lambda x: (snapshot_date - x.max()).days,
        "order_id": "count",
        "order_value": "sum"
    }).reset_index()

    rfm.columns = ["user_id", "Recency", "Frequency", "Monetary"]

    # -----------------------
    # Percentile Scoring
    # -----------------------
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1,2,3,4,5]
    ).astype(int)
    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1,2,3,4,5]
    ).astype(int)

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str) +
        rfm["F_Score"].astype(str) +
        rfm["M_Score"].astype(str)
    )

    # -----------------------
    # Segmentation
    # -----------------------
    def segment(row):
        if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
            return "Champion"
        elif row["F_Score"] >= 4 and row["R_Score"] >= 3:
            return "Loyal"
        elif row["R_Score"] >= 3:
            return "Fence Sitter"
        elif row["R_Score"] == 2:
            return "At Risk"
        else:
            return "Churned"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    # -----------------------
    # KPI Section
    # -----------------------
    total_customers = len(rfm)
    total_revenue = rfm["Monetary"].sum()
    champion_revenue = rfm[rfm["Segment"]=="Champion"]["Monetary"].sum()
    at_risk_revenue = rfm[rfm["Segment"].isin(["At Risk","Churned"])]["Monetary"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", total_customers)
    col2.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    col3.metric("Champion Revenue", f"₹ {champion_revenue:,.0f}")
    col4.metric("Revenue At Risk", f"₹ {at_risk_revenue:,.0f}")

    st.markdown("---")

    # -----------------------
    # Revenue by Segment
    # -----------------------
    seg_revenue = rfm.groupby("Segment")["Monetary"].sum().reset_index()

    fig = px.pie(seg_revenue, names="Segment", values="Monetary",
                 title="Revenue Contribution by Segment")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------
    # Monthly Revenue Trend
    # -----------------------
    monthly = df.groupby(
        pd.Grouper(key="order_date", freq="M")
    )["order_value"].sum().reset_index()

    fig_line = px.line(monthly, x="order_date",
                       y="order_value",
                       title="Monthly Revenue Trend")
    st.plotly_chart(fig_line, use_container_width=True)

    # -----------------------
    # AI-Based Managerial Recommendation
    # -----------------------
    st.subheader("🤖 AI-Based Managerial Recommendations")

    revenue_dependency = champion_revenue / total_revenue

    if revenue_dependency > 0.50:
        st.warning("High revenue dependency on Champions. Risk of revenue concentration.")
    else:
        st.success("Revenue distribution is balanced across segments.")

    if at_risk_revenue > champion_revenue * 0.5:
        st.error("Significant revenue at risk. Immediate retention strategy required.")
    else:
        st.info("Revenue risk manageable.")

    st.markdown("""
    **Recommended Strategic Actions:**
    - Strengthen loyalty programs for Champions.
    - Launch re-engagement campaigns for At Risk & Churned segments.
    - Upsell Fence Sitters into Loyal category.
    - Monitor Recency trend monthly.
    """)

    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
