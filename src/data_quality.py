
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "amazon_real"
OUTPUT = ROOT / "output"

OUTPUT.mkdir(exist_ok=True)

stops = pd.read_parquet(DATA / "stops.parquet")
routes = pd.read_parquet(DATA / "routes.parquet")
travel = pd.read_parquet(DATA / "travel_times.parquet")

checks = []

def record_check(name, passed, details):
    checks.append({
        "check_name": name,
        "status": "PASS" if passed else "CHECK",
        "details": details
    })

# Check 1: Required IDs must not be missing
record_check(
    "Stop route IDs not missing",
    stops["route_id"].notna().all(),
    f"Missing IDs: {stops['route_id'].isna().sum()}"
)

record_check(
    "Route IDs not missing",
    routes["route_id"].notna().all(),
    f"Missing IDs: {routes['route_id'].isna().sum()}"
)

# Check 2: Route IDs should be unique in the routes table
record_check(
    "Route IDs unique",
    routes["route_id"].is_unique,
    f"Duplicate route IDs: {routes['route_id'].duplicated().sum()}"
)

# Check 3: Package counts should not be negative
record_check(
    "Package counts non-negative",
    stops["package_count"].ge(0).all(),
    f"Negative counts: {stops['package_count'].lt(0).sum()}"
)

# Check 4: Delivery and rejection counts should not be negative
record_check(
    "Delivery counts non-negative",
    (
        stops["delivered_count"].ge(0).all()
        and stops["rejected_count"].ge(0).all()
        and stops["delivery_attempted_count"].ge(0).all()
    ),
    "Checked delivered, rejected and attempted counts"
)

# Check 5: Delivered count should not exceed package count
record_check(
    "Delivered count within package count",
    stops["delivered_count"].le(stops["package_count"]).all(),
    f"Rows to review: {stops['delivered_count'].gt(stops['package_count']).sum()}"
)

# Check 6: Travel time should not be negative
record_check(
    "Travel times non-negative",
    travel["travel_time_seconds"].ge(0).all(),
    f"Negative travel times: {travel['travel_time_seconds'].lt(0).sum()}"
)

# Check 7: Every route referenced by a stop exists in routes
unknown_routes = ~stops["route_id"].isin(routes["route_id"])

record_check(
    "Stop route IDs exist in routes table",
    not unknown_routes.any(),
    f"Stops with unknown routes: {unknown_routes.sum()}"
)

# Display and save results
report = pd.DataFrame(checks)

print("\n===== AMAZON DATA QUALITY REPORT =====")
print(report.to_string(index=False))

report_path = OUTPUT / "data_quality_report.csv"
report.to_csv(report_path, index=False)

print(f"\nReport saved to: {report_path}")
print("\nPASS means the check passed.")
print("CHECK means review the reported condition; it does not automatically mean the data is wrong.")
