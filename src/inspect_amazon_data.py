
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "amazon_real"

files = [
    "stops.parquet",
    "routes.parquet",
    "travel_times.parquet",
]

for filename in files:
    path = DATA_DIR / filename

    print("\n" + "=" * 50)
    print(f"FILE: {filename}")
    print("=" * 50)

    if not path.exists():
        print(f"File not found: {path}")
        continue

    try:
        df = pd.read_parquet(path)

        print("Rows and columns:", df.shape)
        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nFirst 5 rows:")
        print(df.head().to_string())

        print("\nMissing values:")
        print(df.isna().sum().to_string())

    except Exception as error:
        print("Could not read file:", error)
