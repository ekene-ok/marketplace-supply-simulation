-- 02_cheapest_plan.sql
-- For each plan type, the cheapest schedule that meets the target:
-- 90% of orders on time across the day and at least 85% in every hour.

CREATE OR REPLACE VIEW cheapest_plan_meeting_target AS
SELECT *
FROM scenario_summary
WHERE meets_target
QUALIFY ROW_NUMBER() OVER (PARTITION BY plan_type ORDER BY courier_hours_per_day) = 1;
