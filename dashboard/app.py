
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = PROJECT_ROOT / "output" / "cleaned_deliveries.csv"

st.set_page_config(
    page_title="Delivery Analytics",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Delivery Analytics Dashboard")
st.write("Upload delivery data or explore the sample dataset.")

uploaded_file = st.sidebar.file_uploader(
    "Upload a delivery CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the CSV: {error}")
        st.stop()
else:
    if not DEFAULT_FILE.exists():
        st.error("Sample data not found. Run python src/etl_pipeline.py first.")
        st.stop()

    df = pd.read_csv(DEFAULT_FILE)
    st.info("Showing the generated sample dataset.")

# Required columns in the uploaded CSV
required = [
    "order_id",
    "driver_id",
    "region",
    "scheduled_delivery_time",
    "actual_delivery_time",
    "delivery_status"
]

missing = [column for column in required if column not in df.columns]

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Please check the required column names shown below.")
    st.code(", ".join(required))
    st.stop()

# Basic data quality checks
if df["order_id"].isna().any():
    st.error("Some records have a missing order_id.")
    st.stop()

if df["order_id"].duplicated().any():
    st.error("Duplicate order_id values found. Please correct the CSV.")
    st.stop()

valid_statuses = ["Delivered", "Failed", "In Transit"]

if not df["delivery_status"].isin(valid_statuses).all():
    st.error("delivery_status must contain Delivered, Failed, or In Transit.")
    st.stop()

# Transform uploaded data into analytics-ready data
df["scheduled_delivery_time"] = pd.to_datetime(
    df["scheduled_delivery_time"], errors="coerce"
)
df["actual_delivery_time"] = pd.to_datetime(
    df["actual_delivery_time"], errors="coerce"
)

if df["scheduled_delivery_time"].isna().any():
    st.error("Some scheduled delivery times are missing or invalid.")
    st.stop()

delivered_mask = df["delivery_status"].eq("Delivered")

if df.loc[delivered_mask, "actual_delivery_time"].isna().any():
    st.error("Delivered records must have an actual delivery time.")
    st.stop()

if df.loc[~delivered_mask, "actual_delivery_time"].notna().any():
    st.warning(
        "Some undelivered records have actual delivery times. "
        "Please verify these records."
    )

df["delay_minutes"] = (
    df["actual_delivery_time"] - df["scheduled_delivery_time"]
).dt.total_seconds() / 60

df["on_time_delivery"] = (
    delivered_mask & df["delay_minutes"].le(0)
)

df["delivery_date"] = (
    df["scheduled_delivery_time"].dt.strftime("%Y-%m-%d")
)

# Filters
st.sidebar.header("Filters")

regions = sorted(df["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Regions", regions, default=regions
)

statuses = sorted(df["delivery_status"].unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Delivery status", statuses, default=statuses
)

filtered = df[
    df["region"].isin(selected_regions)
    & df["delivery_status"].isin(selected_statuses)
].copy()

# KPIs
delivered = filtered[
    filtered["delivery_status"] == "Delivered"
]

total_orders = len(filtered)
delivered_count = len(delivered)

on_time_rate = (
    100 * delivered["on_time_delivery"].sum() / delivered_count
    if delivered_count else 0
)

avg_delay = delivered["delay_minutes"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Delivered Orders", f"{delivered_count:,}")
c3.metric("On-Time Rate", f"{on_time_rate:.1f}%")
c4.metric(
    "Average Delay",
    f"{avg_delay:.1f} min" if pd.notna(avg_delay) else "N/A"
)

# Charts and details
st.subheader("Orders by Delivery Status")
if not filtered.empty:
    st.bar_chart(filtered["delivery_status"].value_counts())

st.subheader("Regional Performance")
if not filtered.empty:
    regional = filtered.groupby("region").agg(
        total_orders=("order_id", "count"),
        delivered_orders=(
            "delivery_status",
            lambda values: (values == "Delivered").sum()
        ),
        on_time_orders=("on_time_delivery", "sum")
    )
    st.dataframe(regional, use_container_width=True)
    st.bar_chart(regional)

st.subheader("Daily Order Trend")
if not filtered.empty:
    daily = (
        filtered.groupby("delivery_date")
        .size()
        .rename("orders")
        .sort_index()
    )
    st.line_chart(daily)

st.subheader("Delivery Records")
st.dataframe(filtered, use_container_width=True)

st.download_button(
    "Download Analytics Data",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="delivery_analytics_output.csv",
    mime="text/csv"
)
