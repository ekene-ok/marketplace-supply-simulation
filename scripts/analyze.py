"""Run the SQL analysis over the simulated orders and export results/."""
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
con = duckdb.connect(str(ROOT / "simulation.duckdb"))
for f in sorted((ROOT / "sql").glob("*.sql")):
    con.execute(f.read_text())
for v in ["scenario_summary", "cheapest_plan_meeting_target", "hourly_service", "worst_hour"]:
    con.sql(f"SELECT * FROM {v}").write_csv(str(ROOT / "results" / f"{v}.csv"))
print(con.sql("SELECT * FROM scenario_summary"))
print(con.sql("SELECT * FROM cheapest_plan_meeting_target"))
print(con.sql("SELECT * FROM worst_hour"))
print(con.sql("SELECT plan_type, hour, couriers, orders_per_hour, on_time_rate, p90_delivery_min FROM hourly_service"))
