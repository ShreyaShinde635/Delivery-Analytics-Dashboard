import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "output" / "cleaned_deliveries.csv"


def test_pipeline_output_exists():
    assert OUTPUT_FILE.exists(), (
        "Cleaned dataset not found. Run: python src/etl_pipeline.py"
    )


def test_record_count():
    df = pd.read_csv(OUTPUT_FILE)
    assert len(df) == 1000, "Expected 1000 output records"


def test_order_ids_are_unique():
    df = pd.read_csv(OUTPUT_FILE)
    assert df["order_id"].notna().all()
    assert df["order_id"].is_unique


def test_delivery_status_values():
    df = pd.read_csv(OUTPUT_FILE)
    allowed = {"Delivered", "Failed", "In Transit"}
    assert set(df["delivery_status"]).issubset(allowed)


def test_delivered_orders_have_actual_time():
    df = pd.read_csv(OUTPUT_FILE)
    delivered = df["delivery_status"] == "Delivered"

    assert df.loc[delivered, "actual_delivery_time"].notna().all()


def test_non_delivered_orders_have_no_actual_time():
    df = pd.read_csv(OUTPUT_FILE)
    not_delivered = df["delivery_status"] != "Delivered"

    assert df.loc[not_delivered, "actual_delivery_time"].isna().all()


if __name__ == "__main__":
    test_pipeline_output_exists()
    test_record_count()
    test_order_ids_are_unique()
    test_delivery_status_values()
    test_delivered_orders_have_actual_time()
    test_non_delivered_orders_have_no_actual_time()

    print("All 6 data quality tests passed!")