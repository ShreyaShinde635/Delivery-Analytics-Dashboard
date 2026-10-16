
-- 1. Total number of routes
SELECT COUNT(*) AS total_routes
FROM routes;

-- 2. Number of routes at each station
SELECT
    station_code,
    COUNT(*) AS total_routes
FROM routes
GROUP BY station_code
ORDER BY total_routes DESC;

-- 3. Average number of stops per station
SELECT
    station_code,
    ROUND(AVG(stop_count), 2) AS average_stops
FROM routes
GROUP BY station_code
ORDER BY average_stops DESC;

-- 4. Route score distribution
SELECT
    COALESCE(route_score, 'Unknown') AS route_score,
    COUNT(*) AS total_routes
FROM routes
GROUP BY route_score
ORDER BY total_routes DESC;

-- 5. Total packages and delivered packages by stop type
SELECT
    stop_type,
    SUM(package_count) AS total_packages,
    SUM(delivered_count) AS delivered_packages,
    SUM(rejected_count) AS rejected_packages
FROM stops
GROUP BY stop_type
ORDER BY total_packages DESC;

-- 6. Average travel time by station
SELECT
    r.station_code,
    ROUND(AVG(t.travel_time_seconds) / 60.0, 2)
        AS average_travel_minutes
FROM travel_times AS t
JOIN routes AS r
    ON t.route_id = r.route_id
GROUP BY r.station_code
ORDER BY average_travel_minutes DESC;
