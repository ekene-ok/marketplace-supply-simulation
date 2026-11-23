-- 03_hourly_view.sql
-- Hour-by-hour service for the two cheapest qualifying plans: where does each one
-- fall short? A daily average can hide a dinner rush that customers remember.

CREATE OR REPLACE VIEW hourly_service AS
SELECT c.plan_type, o.scenario, o.hour,
       ANY_VALUE(s.couriers)                                   AS couriers,
       COUNT(*) / ANY_VALUE(a.reps)                            AS orders_per_hour,
       ROUND(AVG((o.delivery_min <= 35)::INT), 3)              AS on_time_rate,
       ROUND(QUANTILE_CONT(o.delivery_min, 0.9), 1)            AS p90_delivery_min,
       ROUND(AVG(o.courier_wait_min), 1)                       AS avg_wait_for_courier_min
FROM orders o
JOIN cheapest_plan_meeting_target c USING (scenario)
JOIN staffing s ON s.scenario = o.scenario AND s.hour = o.hour
CROSS JOIN assumptions a
GROUP BY c.plan_type, o.scenario, o.hour
ORDER BY c.plan_type, o.hour;

-- Worst hour for each plan.
CREATE OR REPLACE VIEW worst_hour AS
SELECT plan_type, scenario, hour, on_time_rate, p90_delivery_min
FROM hourly_service
QUALIFY ROW_NUMBER() OVER (PARTITION BY plan_type ORDER BY on_time_rate) = 1;
