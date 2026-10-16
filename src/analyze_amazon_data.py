
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "amazon_real"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the public Amazon research dataset
stops = pd.read_parquet(DATA_DIR / "stops.parquet")
routes = pd.read_parquet(DATA_DIR / "routes.parquet")
travel = pd.read_parquet(DATA_DIR / "travel_times.parquet")

print("\n===== AMAZON ROUTE ANALYTICS =====")

# 1. Overall route metrics
print("\n1. ROUTE OVERVIEW")
print("Total routes:", len(routes))
print("Unique stations:", routes["station_code"].nunique())
print("Total planned stops:", routes["stop_count"].sum())

# 2. Stop and package metrics
print("\n2. DELIVERY STOP OVERVIEW")
print("Total stop records:", len(stops))
print("Total packages:", stops["package_count"].sum())
print("Delivered packages:", stops["delivered_count"].sum())
print("Rejected packages:", stops["rejected_count"].sum())

packages = stops["package_count"].sum()
delivered = stops["delivered_count"].sum()

if packages > 0:
    print("Package delivery percentage:",
          round(delivered / packages * 100, 2), "%")

# 3. Performance by station
print("\n3. STATION PERFORMANCE")
station_summary = routes.groupby("station_code").agg(
    total_routes=("route_id", "count"),
    average_stops=("stop_count", "mean")
).reset_index()

station_summary["average_stops"] = (
    station_summary["average_stops"].round(2)
)

print(station_summary.to_string(index=False))
station_summary.to_csv(
    OUTPUT_DIR / "station_performance.csv", index=False
)

# 4. Route score distribution
print("\n4. ROUTE SCORE DISTRIBUTION")
print(routes["route_score"].value_counts(dropna=False).to_string())

# 5. Travel-time analysis
print("\n5. TRAVEL TIME ANALYSIS")
print("Travel-time records:", len(travel))
print("Average travel time (minutes):",
      round(travel["travel_time_seconds"].mean() / 60, 2))
print("Median travel time (minutes):",
      round(travel["travel_time_seconds"].median() / 60, 2))
print("Maximum travel time (minutes):",
      round(travel["travel_time_seconds"].max() / 60, 2))

# 6. Save route-level report
route_summary = routes[
    ["route_id", "station_code", "route_date",
     "route_score", "stop_count"]
].copy()

route_summary.to_csv(
    OUTPUT_DIR / "amazon_route_summary.csv", index=False
)

print("\nReports saved in the output folder.")
print("Analytics completed successfully!")
