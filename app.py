import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Customer RFM Intelligence Dashboard", layout="wide")

st.title("📊 Customer RFM Intelligence Dashboard")
st.markdown("Percentile-based RFM Segmentation with Business Insights")

# -----------------------------
# File Upload
# -----------------------------
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

    # -----------------------------
    # Analysis Date Selection
    # -----------------------------
    st.subheader("📅 Select Analysis Date")

    analysis_date = st.date_input(
        "Choose a date to calculate Recency",
        value=df["order_date"].max(),
        min_value=df["order_date"].min(),
        max_value=datetime.today()
    )

    snapshot_date = pd.to_datetime(analysis_date)

    st.info(
        f"Recency is calculated as difference between {snapshot_date.date()} "
        f"and each customer's last order date."
    )

    if snapshot_date < df["order_date"].min():
        st.error("Analysis date cannot be earlier than dataset start date.")
        st.stop()

    # -----------------------------
    # RFM Calculation
    # -----------------------------
    rfm = df.groupby("user_id").agg({
        "order_date": lambda x: (snapshot_date - x.max()).days,
        "order_id": "count",
        "order_value": "sum"
    }).reset_index()

    rfm.columns = ["user_id", "Recency", "Frequency", "Monetary"]

    # -----------------------------
    # Percentile-Based Scoring
    # -----------------------------
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

    # -----------------------------
    # Segmentation Logic
    # -----------------------------
    def segment(row):
        if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
            return "Champion Customer"
        elif row["F_Score"] >= 4 and row["R_Score"] >= 3:
            return "Loyal Customer"
        elif row["R_Score"] >= 3:
            return "Fence Sitter"
        elif row["R_Score"] == 2:
            return "At Risk Customer"
        else:
            return "Churned Customer"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    # -----------------------------
    # Sidebar Filter
    # -----------------------------
    st.sidebar.header("Filters")
    segment_filter = st.sidebar.multiselect(
        "Select Segment",
        options=rfm["Segment"].unique(),
        default=rfm["Segment"].unique()
    )

    rfm_filtered = rfm[rfm["Segment"].isin(segment_filter)]

    # -----------------------------
    # KPI Section
    # -----------------------------
    total_customers = len(rfm_filtered)
    active_customers = sum(rfm_filtered["Recency"] <= 30)
    avg_recency = round(rfm_filtered["Recency"].mean(), 1)
    avg_frequency = round(rfm_filtered["Frequency"].mean(), 1)
    avg_monetary = round(rfm_filtered["Monetary"].mean(), 0)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Customers", total_customers)
    col2.metric("Active Customers (≤30 days)", active_customers)
    col3.metric("Avg Recency (days)", avg_recency)
    col4.metric("Avg Frequency", avg_frequency)
    col5.metric("Avg Monetary (₹)", avg_monetary)

    st.markdown("---")

    # -----------------------------
    # Revenue Contribution by Segment
    # -----------------------------
    seg_revenue = rfm_filtered.groupby("Segment")["Monetary"].sum().reset_index()
    seg_revenue["Revenue_%"] = (
        seg_revenue["Monetary"] /
        seg_revenue["Monetary"].sum() * 100
    )

    fig_rev = px.bar(
        seg_revenue,
        x="Segment",
        y="Monetary",
        title="Revenue Contribution by Segment"
    )

    st.plotly_chart(fig_rev, use_container_width=True)

    # -----------------------------
    # Monthly Revenue Trend
    # -----------------------------
    monthly = df.groupby(
        pd.Grouper(key="order_date", freq="M")
    )["order_value"].sum().reset_index()

    fig_line = px.line(
        monthly,
        x="order_date",
        y="order_value",
        title="Monthly Revenue Trend"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # -----------------------------
    # RFM Score Distribution
    # -----------------------------
    st.subheader("RFM Score Distribution")

    colA, colB, colC = st.columns(3)

    colA.plotly_chart(
        px.histogram(rfm_filtered, x="R_Score",
                     title="Recency Score Distribution"),
        use_container_width=True
    )

    colB.plotly_chart(
        px.histogram(rfm_filtered, x="F_Score",
                     title="Frequency Score Distribution"),
        use_container_width=True
    )

    colC.plotly_chart(
        px.histogram(rfm_filtered, x="M_Score",
                     title="Monetary Score Distribution"),
        use_container_width=True
    )

    # -----------------------------
    # Preferred Product per Segment
    # -----------------------------
    preferred = (
        df.groupby(["user_id", "product_name"])
        .size()
        .reset_index(name="count")
    )

    preferred = preferred.loc[
        preferred.groupby("user_id")["count"].idxmax()
    ]

    rfm_pref = rfm_filtered.merge(
        preferred[["user_id", "product_name"]],
        on="user_id",
        how="left"
    )

    seg_product = (
        rfm_pref.groupby(["Segment", "product_name"])
        .size()
        .reset_index(name="count")
    )

    seg_product = seg_product.loc[
        seg_product.groupby("Segment")["count"].idxmax()
    ]

    st.subheader("Most Preferred Product by Segment")
    st.dataframe(seg_product, use_container_width=True)

    # -----------------------------
    # Final RFM Table
    # -----------------------------
    st.subheader("Customer RFM Table")
    st.dataframe(
        rfm_filtered.sort_values("RFM_Score", ascending=False),
        use_container_width=True
    )

    st.caption(
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    st.caption(
        "Recency calculated based on selected analysis date."
    )
