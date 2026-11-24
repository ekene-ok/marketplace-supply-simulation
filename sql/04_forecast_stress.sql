-- Forecast stress test: service and cost for each schedule when actual demand misses the forecast.
-- On time = delivered within 35 minutes. Worst hour = lowest hourly on-time rate across the day.
CREATE OR REPLACE VIEW forecast_stress AS
WITH hourly AS (
    SELECT scenario, demand_scale, hour, AVG(CASE WHEN delivery_min <= 35 THEN 1 ELSE 0 END) AS on_time
    FROM stress_orders
    GROUP BY scenario, demand_scale, hour
),
worst AS (
    SELECT scenario, demand_scale, MIN(on_time) AS worst_hour_on_time_rate
    FROM hourly
    GROUP BY scenario, demand_scale
),
daily AS (
    SELECT scenario, demand_scale,
           COUNT(*) / 30.0                                            AS orders_per_day,
           AVG(CASE WHEN delivery_min <= 35 THEN 1 ELSE 0 END)        AS on_time_rate,
           QUANTILE_CONT(delivery_min, 0.9)                           AS p90_delivery_min
    FROM stress_orders
    GROUP BY scenario, demand_scale
),
hours AS (
    SELECT scenario, SUM(couriers) AS courier_hours_per_day FROM stress_staffing GROUP BY scenario
)
SELECT
    d.scenario,
    d.demand_scale,
    h.courier_hours_per_day,
    ROUND(d.orders_per_day, 0)                                   AS orders_per_day,
    ROUND(d.on_time_rate, 4)                                     AS on_time_rate,
    ROUND(w.worst_hour_on_time_rate, 4)                          AS worst_hour_on_time_rate,
    ROUND(d.p90_delivery_min, 1)                                 AS p90_delivery_min,
    ROUND(h.courier_hours_per_day * 22.0 / d.orders_per_day, 2)  AS courier_cost_per_order,
    d.on_time_rate >= 0.90 AND w.worst_hour_on_time_rate >= 0.85 AS meets_target
FROM daily d
JOIN worst w USING (scenario, demand_scale)
JOIN hours h USING (scenario)
ORDER BY d.scenario, d.demand_scale;
