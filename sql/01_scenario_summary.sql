-- 01_scenario_summary.sql
-- One row per staffing scenario: service level, speed, courier hours and cost.
-- On-time = delivered within 35 minutes of the order.
-- Service target: at least 90% on time across the day AND at least 85% in every hour.

CREATE OR REPLACE VIEW scenario_summary AS
WITH hours AS (
    SELECT scenario, ANY_VALUE(plan_type) AS plan_type, SUM(couriers) AS courier_hours_per_day
    FROM staffing GROUP BY scenario
),
hourly AS (
    SELECT scenario, hour, AVG((delivery_min <= 35)::INT) AS hour_on_time
    FROM orders GROUP BY scenario, hour
),
worst AS (
    SELECT scenario, MIN(hour_on_time) AS worst_hour_on_time_rate FROM hourly GROUP BY scenario
),
perf AS (
    SELECT scenario,
           COUNT(*) / ANY_VALUE(a.reps)                         AS orders_per_day,
           AVG((delivery_min <= 35)::INT)                       AS on_time_rate,
           QUANTILE_CONT(delivery_min, 0.5)                     AS p50_delivery_min,
           QUANTILE_CONT(delivery_min, 0.9)                     AS p90_delivery_min,
           AVG(courier_wait_min)                                AS avg_wait_for_courier_min
    FROM orders, assumptions a
    GROUP BY scenario
)
SELECT h.scenario, h.plan_type, h.courier_hours_per_day,
       ROUND(p.orders_per_day, 0)                                        AS orders_per_day,
       ROUND(p.on_time_rate, 4)                                          AS on_time_rate,
       ROUND(w.worst_hour_on_time_rate, 4)                               AS worst_hour_on_time_rate,
       (p.on_time_rate >= 0.90 AND w.worst_hour_on_time_rate >= 0.85)    AS meets_target,
       ROUND(p.p50_delivery_min, 1)                                      AS p50_delivery_min,
       ROUND(p.p90_delivery_min, 1)                                      AS p90_delivery_min,
       ROUND(p.avg_wait_for_courier_min, 1)                              AS avg_wait_for_courier_min,
       ROUND(p.orders_per_day / h.courier_hours_per_day, 2)              AS orders_per_courier_hour,
       ROUND(h.courier_hours_per_day * a.courier_hourly_cost
             / p.orders_per_day, 2)                                      AS courier_cost_per_order
FROM hours h
JOIN perf p USING (scenario)
JOIN worst w USING (scenario)
CROSS JOIN assumptions a
ORDER BY h.plan_type, h.courier_hours_per_day;
