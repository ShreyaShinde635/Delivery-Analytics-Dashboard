
import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = PROJECT_ROOT / "output" / "cleaned_deliveries.csv"
DB_FILE = PROJECT_ROOT / "output" / "delivery_analytics.db"


def load_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            "Cleaned CSV not found. Run src/etl_pipeline.py first."
        )

    df = pd.read_csv(CSV_FILE)

    with sqlite3.connect(DB_FILE) as connection:
        df.to_sql(
            "deliveries",
            connection,
            if_exists="replace",
            index=False
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM deliveries"
        ).fetchone()[0]

    print("Data loaded into SQLite successfully!")
    print(f"Records loaded: {count}")
    print(f"Database location: {DB_FILE}")


if __name__ == "__main__":
    load_data()
