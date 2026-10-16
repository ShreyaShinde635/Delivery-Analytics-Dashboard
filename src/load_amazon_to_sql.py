
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "amazon_real"
OUTPUT = ROOT / "output"

OUTPUT.mkdir(exist_ok=True)
DB_PATH = OUTPUT / "amazon_analytics.db"

print("Loading Amazon research data into SQLite...")

stops = pd.read_parquet(DATA / "stops.parquet")
routes = pd.read_parquet(DATA / "routes.parquet")
travel = pd.read_parquet(DATA / "travel_times.parquet")

with sqlite3.connect(DB_PATH) as connection:
    routes.to_sql(
        "routes", connection, if_exists="replace", index=False
    )
    stops.to_sql(
        "stops", connection, if_exists="replace", index=False
    )
    travel.to_sql(
        "travel_times", connection, if_exists="replace", index=False
    )

    for table in ["routes", "stops", "travel_times"]:
        count = pd.read_sql_query(
            f"SELECT COUNT(*) AS total FROM {table}",
            connection
        )["total"].iloc[0]

        print(f"{table}: {count:,} rows loaded")

print(f"\nDatabase created: {DB_PATH}")
print("SQL data loading completed successfully!")
