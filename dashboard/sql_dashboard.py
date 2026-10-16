
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "output" / "amazon_analytics.db"

st.set_page_config(
    page_title="Amazon Last-Mile Analytics",
    page_icon="🚚",
    layout="wide"
)

st.title("Amazon Last-Mile Delivery Analytics")
st.caption(
    "SQL-powered analysis of the public Amazon Last Mile Routing "
    "research dataset — historical data from 2018."
)


if not DB_PATH.exists():
    st.error("Database not found. Run src/load_amazon_to_sql.py first.")
    st.stop()


@st.cache_data
def query_data(sql, params=()):
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(sql, connection, params=params)


# Sidebar filters
st.sidebar.header("Dashboard Filters")

station_data = query_data("""
    SELECT station_code, COUNT(*) AS total_routes
    FROM routes
    GROUP BY station_code
    ORDER BY station_code
""")

stations = ["All"] + sorted(
    station_data["station_code"].dropna().tolist()
)

selected_station = st.sidebar.selectbox(
    "Select station",
    stations
)

if selected_station == "All":
    route_filter = ""
    params = ()
else:
    route_filter = "WHERE station_code = ?"
    params = (selected_station,)


# Summary metrics
overview = query_data(f"""
    SELECT
        COUNT(*) AS total_routes,
        ROUND(AVG(stop_count), 2) AS average_stops,
        SUM(stop_count) AS total_stops
    FROM routes
    {route_filter}
""", params)

if selected_station == "All":
    packages = query_data("""
        SELECT
            SUM(package_count) AS total_packages,
            SUM(delivered_count) AS delivered_packages
        FROM stops
        WHERE stop_type = 'Dropoff'
    """)
else:
    packages = query_data("""
        SELECT
            SUM(s.package_count) AS total_packages,
            SUM(s.delivered_count) AS delivered_packages
        FROM stops s
        JOIN routes r ON s.route_id = r.route_id
        WHERE s.stop_type = 'Dropoff'
          AND r.station_code = ?
    """, (selected_station,))

total_routes = int(overview.iloc[0]["total_routes"])
average_stops = overview.iloc[0]["average_stops"]
total_stops = int(overview.iloc[0]["total_stops"] or 0)
total_packages = int(packages.iloc[0]["total_packages"] or 0)
delivered_packages = int(
    packages.iloc[0]["delivered_packages"] or 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Routes", f"{total_routes:,}")
c2.metric("Total Stops", f"{total_stops:,}")
c3.metric(
    "Average Stops per Route",
    f"{average_stops:.2f}" if pd.notna(average_stops) else "N/A"
)
c4.metric("Delivered Packages", f"{delivered_packages:,}")

st.caption(f"Packages recorded: {total_packages:,}")

st.divider()


# Routes by station
st.subheader("Routes by Station")

routes_by_station = query_data("""
    SELECT
        station_code,
        COUNT(*) AS total_routes
    FROM routes
    GROUP BY station_code
    ORDER BY total_routes DESC
""")

st.bar_chart(
    routes_by_station.set_index("station_code")["total_routes"]
)


# Average stops by station
st.subheader("Average Stops per Route by Station")

average_stops_data = query_data("""
    SELECT
        station_code,
        ROUND(AVG(stop_count), 2) AS average_stops
    FROM routes
    GROUP BY station_code
    ORDER BY average_stops DESC
""")

st.bar_chart(
    average_stops_data.set_index("station_code")["average_stops"]
)


# Route score distribution
st.subheader("Route Score Distribution")

score_data = query_data("""
    SELECT
        COALESCE(route_score, 'Unknown') AS route_score,
        COUNT(*) AS total_routes
    FROM routes
    GROUP BY route_score
    ORDER BY total_routes DESC
""")

st.bar_chart(
    score_data.set_index("route_score")["total_routes"]
)

st.dataframe(score_data, use_container_width=True)


# Daily route trend
st.subheader("Daily Route Trend")

if selected_station == "All":
    daily_routes = query_data("""
        SELECT
            route_date,
            COUNT(*) AS total_routes
        FROM routes
        GROUP BY route_date
        ORDER BY route_date
    """)
else:
    daily_routes = query_data("""
        SELECT
            route_date,
            COUNT(*) AS total_routes
        FROM routes
        WHERE station_code = ?
        GROUP BY route_date
        ORDER BY route_date
    """, (selected_station,))

if not daily_routes.empty:
    daily_routes["route_date"] = pd.to_datetime(
        daily_routes["route_date"]
    )
    st.line_chart(
        daily_routes.set_index("route_date")["total_routes"]
    )
else:
    st.info("No daily route records found for this station.")


# Travel time analysis
st.subheader("Travel Time Analysis")

if selected_station == "All":
    travel_summary = query_data("""
        SELECT
            COUNT(*) AS travel_records,
            ROUND(AVG(travel_time_seconds) / 60.0, 2)
                AS average_minutes,
            ROUND(MAX(travel_time_seconds) / 60.0, 2)
                AS maximum_minutes
        FROM travel_times
    """)
else:
    travel_summary = query_data("""
        SELECT
            COUNT(*) AS travel_records,
            ROUND(AVG(t.travel_time_seconds) / 60.0, 2)
                AS average_minutes,
            ROUND(MAX(t.travel_time_seconds) / 60.0, 2)
                AS maximum_minutes
        FROM travel_times t
        JOIN routes r ON t.route_id = r.route_id
        WHERE r.station_code = ?
    """, (selected_station,))

t1, t2, t3 = st.columns(3)

t1.metric(
    "Travel-Time Records",
    f"{int(travel_summary.iloc[0]['travel_records']):,}"
)
t2.metric(
    "Average Travel Time",
    f"{travel_summary.iloc[0]['average_minutes']:.2f} min"
    if pd.notna(travel_summary.iloc[0]["average_minutes"])
    else "N/A"
)
t3.metric(
    "Maximum Travel Time",
    f"{travel_summary.iloc[0]['maximum_minutes']:.2f} min"
    if pd.notna(travel_summary.iloc[0]["maximum_minutes"])
    else "N/A"
)


# Route records table
st.subheader("Explore Route Records")

if selected_station == "All":
    route_records = query_data("""
        SELECT
            route_id,
            station_code,
            route_date,
            COALESCE(route_score, 'Unknown') AS route_score,
            stop_count
        FROM routes
        ORDER BY route_date, station_code
        LIMIT 1000
    """)
else:
    route_records = query_data("""
        SELECT
            route_id,
            station_code,
            route_date,
            COALESCE(route_score, 'Unknown') AS route_score,
            stop_count
        FROM routes
        WHERE station_code = ?
        ORDER BY route_date
        LIMIT 1000
    """, (selected_station,))

st.dataframe(route_records, use_container_width=True)

st.download_button(
    "Download Route Records as CSV",
    data=route_records.to_csv(index=False).encode("utf-8"),
    file_name="amazon_route_analysis.csv",
    mime="text/csv"
)

st.caption(
    "Source: public Amazon Last Mile Routing research dataset. "
    "Historical research data, not live Amazon operations."
)
