
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "amazon_real"

st.set_page_config(
    page_title="Amazon Last-Mile Analytics",
    page_icon="🚚",
    layout="wide"
)

st.title("Amazon Last-Mile Delivery Analytics")
st.caption(
    "Analysis of the public Amazon Last Mile Routing "
    "research dataset (historical data from 2018)."
)

@st.cache_data
def load_data():
    stops = pd.read_parquet(DATA / "stops.parquet")
    routes = pd.read_parquet(DATA / "routes.parquet")
    travel = pd.read_parquet(DATA / "travel_times.parquet")
    return stops, routes, travel

try:
    stops, routes, travel = load_data()
except Exception as error:
    st.error(f"Could not load dataset: {error}")
    st.stop()

st.sidebar.header("Filters")

stations = ["All"] + sorted(
    routes["station_code"].dropna().unique().tolist()
)
selected_station = st.sidebar.selectbox(
    "Select station", stations
)

filtered_routes = routes.copy()

if selected_station != "All":
    filtered_routes = filtered_routes[
        filtered_routes["station_code"] == selected_station
    ]

route_ids = set(filtered_routes["route_id"])
filtered_stops = stops[stops["route_id"].isin(route_ids)]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Routes", f"{len(filtered_routes):,}")
c2.metric("Stops", f"{len(filtered_stops):,}")
c3.metric(
    "Packages",
    f"{filtered_stops['package_count'].sum():,}"
)
c4.metric(
    "Delivered packages",
    f"{filtered_stops['delivered_count'].sum():,}"
)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Routes by station")
    station_counts = (
        filtered_routes.groupby("station_code")
        .size()
        .sort_values(ascending=False)
    )
    st.bar_chart(station_counts)

with right:
    st.subheader("Average stops per route")
    average_stops = (
        filtered_routes.groupby("station_code")["stop_count"]
        .mean()
        .sort_values(ascending=False)
    )
    st.bar_chart(average_stops)

st.subheader("Route score distribution")
st.write(
    filtered_routes["route_score"]
    .value_counts(dropna=False)
    .rename_axis("Route score")
    .reset_index(name="Count")
)

st.subheader("Travel-time distribution")

travel_filtered = travel[
    travel["route_id"].isin(route_ids)
].copy()

travel_filtered["travel_minutes"] = (
    travel_filtered["travel_time_seconds"] / 60
)

st.metric(
    "Average travel time",
    f"{travel_filtered['travel_minutes'].mean():.2f} minutes"
)

st.line_chart(
    travel_filtered["travel_minutes"]
    .reset_index(drop=True)
)

st.subheader("Route records")
st.dataframe(filtered_routes, use_container_width=True)

st.download_button(
    "Download filtered routes as CSV",
    data=filtered_routes.to_csv(index=False).encode("utf-8"),
    file_name="amazon_route_analysis.csv",
    mime="text/csv"
)
