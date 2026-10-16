import pandas as pd
from pathlib import Path

# Find the project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "deliveries.csv"

# Check whether the dataset exists
if not DATA_FILE.exists():
    raise FileNotFoundError(
        "Dataset not found. Run: python src/generate_data.py"
    )

# Load the CSV file
df = pd.read_csv(DATA_FILE)

print("===== DATA QUALITY REPORT =====")

# 1. Dataset size
print(f"\nTotal records: {len(df)}")
print(f"Total columns: {len(df.columns)}")

# 2. Column names
print("\nColumns:")
print(df.columns.tolist())

# 3. Missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# 4. Duplicate order IDs
print("\nDuplicate order IDs:")
print(df["order_id"].duplicated().sum())

# 5. Delivery status counts
print("\nDelivery status counts:")
print(df["delivery_status"].value_counts())

# 6. Validate expected columns
required_columns = [
    "order_id",
    "driver_id",
    "region",
    "scheduled_delivery_time",
    "actual_delivery_time",
    "scheduled_minutes",
    "actual_minutes",
    "delivery_status",
]

missing_columns = set(required_columns) - set(df.columns)
assert not missing_columns, f"Missing columns: {missing_columns}"

# 7. Validate record IDs
assert len(df) == 1000, "Expected 1,000 records"
assert df["order_id"].notna().all(), "Missing order IDs"
assert df["order_id"].is_unique, "Duplicate order IDs found"

# 8. Validate allowed statuses
allowed_statuses = {"Delivered", "Failed", "In Transit"}
assert set(df["delivery_status"]).issubset(allowed_statuses)

print("\nVALIDATION PASSED")