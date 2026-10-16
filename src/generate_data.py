import pandas as pd
import numpy as np
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Reproducible sample data
rng = np.random.default_rng(42)
number_of_records = 1000

regions = ["Hyderabad", "Vijayawada", "Chennai", "Bengaluru", "Guntur"]
statuses = ["Delivered", "Failed", "In Transit"]

# Generate scheduled delivery times
start_time = pd.Timestamp("2026-09-01 08:00:00")

scheduled_times = (
    start_time
    + pd.to_timedelta(rng.integers(0, 30 * 24 * 60, number_of_records), unit="m")
)

# Generate delivery durations
scheduled_minutes = rng.integers(20, 91, number_of_records)
delay_minutes = rng.integers(-15, 46, number_of_records)
actual_minutes = scheduled_minutes + delay_minutes

# Generate delivery statuses
delivery_status = rng.choice(
    statuses,
    size=number_of_records,
    p=[0.88, 0.07, 0.05]
)

# Actual time is not available for failed or in-transit deliveries
actual_delivery_times = []

for i in range(number_of_records):
    if delivery_status[i] == "Delivered":
        actual_delivery_times.append(
            scheduled_times[i] + pd.Timedelta(minutes=int(delay_minutes[i]))
        )
    else:
        actual_delivery_times.append(pd.NaT)

# Create dataset
df = pd.DataFrame({
    "order_id": [f"ORD{i:05d}" for i in range(1, number_of_records + 1)],
    "driver_id": rng.integers(1001, 1101, number_of_records),
    "region": rng.choice(regions, number_of_records),
    "scheduled_delivery_time": scheduled_times,
    "actual_delivery_time": actual_delivery_times,
    "scheduled_minutes": scheduled_minutes,
    "actual_minutes": np.where(delivery_status == "Delivered", actual_minutes, np.nan),
    "delivery_status": delivery_status
})

# Save raw dataset
output_file = DATA_DIR / "deliveries.csv"
df.to_csv(output_file, index=False)

print("Synthetic delivery dataset created!")
print(f"File: {output_file}")
print(f"Total records: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nDelivery status counts:")
print(df["delivery_status"].value_counts())
print("\nPreview:")
print(df.head(10).to_string(index=False))