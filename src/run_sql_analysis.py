
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "output" / "amazon_analytics.db"

queries = {
    "Total routes": """
        SELECT COUNT(*) AS total_routes
        FROM routes
    """,

    "Routes by station": """
        SELECT station_code, COUNT(*) AS total_routes
        FROM routes
        GROUP BY station_code
        ORDER BY total_routes DESC
    """,

    "Average stops by station": """
        SELECT station_code,
               ROUND(AVG(stop_count), 2) AS average_stops
        FROM routes
        GROUP BY station_code
        ORDER BY average_stops DESC
    """,

    "Route score distribution": """
        SELECT COALESCE(route_score, 'Unknown') AS route_score,
               COUNT(*) AS total_routes
        FROM routes
        GROUP BY route_score
        ORDER BY total_routes DESC
    """,

    "Package totals by stop type": """
        SELECT stop_type,
               SUM(package_count) AS total_packages,
               SUM(delivered_count) AS delivered_packages,
               SUM(rejected_count) AS rejected_packages
        FROM stops
        GROUP BY stop_type
        ORDER BY total_packages DESC
    """,

    "Average travel time by station": """
        SELECT r.station_code,
               ROUND(AVG(t.travel_time_seconds) / 60.0, 2)
                   AS average_travel_minutes
        FROM travel_times t
        JOIN routes r ON t.route_id = r.route_id
        GROUP BY r.station_code
        ORDER BY average_travel_minutes DESC
    """
}

with sqlite3.connect(DB_PATH) as connection:
    for title, query in queries.items():
        print(f"\n{'=' * 55}")
        print(title.upper())
        print("=" * 55)

        cursor = connection.execute(query)
        print(" | ".join(item[0] for item in cursor.description))

        for row in cursor.fetchall():
            print(" | ".join(str(value) for value in row))

print("\nSQL analysis completed successfully!")
