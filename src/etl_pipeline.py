import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "deliveries.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_pipeline():
    print("Starting delivery ETL pipeline...")

    # 1. EXTRACT: Read raw data
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Run: python src/generate_data.py"
        )

    df = pd.read_csv(DATA_FILE)
    input_count = len(df)

    print(f"Extracted {input_count} records")

    # 2. VALIDATE: Check required fields
    required_columns = [
        "order_id",
        "driver_id",
        "region",
        "scheduled_delivery_time",
        "actual_delivery_time",
        "delivery_status",
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df["order_id"].isna().any():
        raise ValueError("Order IDs contain missing values")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs found")

    # 3. TRANSFORM: Parse timestamps
    df["scheduled_delivery_time"] = pd.to_datetime(
        df["scheduled_delivery_time"], errors="raise"
    )

    df["actual_delivery_time"] = pd.to_datetime(
        df["actual_delivery_time"], errors="coerce"
    )

    # 4. TRANSFORM: Calculate delay in minutes
    df["delay_minutes"] = (
        df["actual_delivery_time"] - df["scheduled_delivery_time"]
    ).dt.total_seconds() / 60

    # 5. TRANSFORM: Calculate delivery performance
    df["on_time_delivery"] = (
        df["delivery_status"].eq("Delivered")
        & df["delay_minutes"].le(0)
    )

    # 6. TRANSFORM: Add a delivery date
    df["delivery_date"] = (
        df["scheduled_delivery_time"].dt.date.astype(str)
    )

    # 7. VALIDATE: Check business rules
    delivered = df["delivery_status"].eq("Delivered")

    if df.loc[delivered, "actual_delivery_time"].isna().any():
        raise ValueError(
            "Delivered orders must have an actual delivery timestamp"
        )

    if df.loc[~delivered, "actual_delivery_time"].notna().any():
        raise ValueError(
            "Non-delivered orders should not have an actual delivery timestamp"
        )

    # 8. LOAD: Save transformed data
    output_file = OUTPUT_DIR / "cleaned_deliveries.csv"
    df.to_csv(output_file, index=False)

    print("\nETL pipeline completed successfully!")
    print(f"Input records: {input_count}")
    print(f"Output records: {len(df)}")
    print(f"Output file: {output_file}")
    print(f"Delivered orders: {delivered.sum()}")
    print(f"On-time deliveries: {df['on_time_delivery'].sum()}")

    return df


if __name__ == "__main__":
    run_pipeline()