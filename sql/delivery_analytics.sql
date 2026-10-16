
-- 1. Total number of orders
SELECT COUNT(*) AS total_orders
FROM deliveries;

-- 2. Orders by delivery status
SELECT delivery_status, COUNT(*) AS order_count
FROM deliveries
GROUP BY delivery_status
ORDER BY order_count DESC;

-- 3. On-time delivery rate among delivered orders
SELECT
    COUNT(*) AS delivered_orders,
    SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END)
        AS on_time_orders,
    ROUND(
        100.0 * SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS on_time_rate_percent
FROM deliveries
WHERE delivery_status = 'Delivered';

-- 4. Average delay among delivered orders
SELECT ROUND(AVG(delay_minutes), 2) AS average_delay_minutes
FROM deliveries
WHERE delivery_status = 'Delivered';

-- 5. Performance by region
SELECT
    region,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN delivery_status = 'Delivered' THEN 1 ELSE 0 END)
        AS delivered_orders,
    SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END)
        AS on_time_orders
FROM deliveries
GROUP BY region
ORDER BY on_time_orders DESC;

-- 6. Daily delivery trend
SELECT
    delivery_date,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN delivery_status = 'Delivered' THEN 1 ELSE 0 END)
        AS delivered_orders
FROM deliveries
GROUP BY delivery_date
ORDER BY delivery_date;
