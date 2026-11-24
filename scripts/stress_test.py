"""Forecast-error stress test: what happens when real demand misses the forecast?

Schedules are planned on the forecast demand curve. Each runs 30 simulated days at actual demand
from 20% below to 20% above forecast. Orders are stored in DuckDB and analysed in SQL
(sql/04_forecast_stress.sql).
"""
from pathlib import Path
import sys
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import duckdb
import pandas as pd
from sim.model import run_day, Params, DEMAND, OPEN_HOUR, CLOSE_HOUR

ROOT = Path(__file__).resolve().parents[1]
REPS, FLOOR = 30, 6
SCHEDULES = {"shaped_0.36": 0.36, "shaped_0.39": 0.39, "shaped_0.42": 0.42, "shaped_0.45": 0.45}
SCALES = [0.8, 0.9, 1.0, 1.1, 1.2]

orders, staffing = [], []
for name, k in SCHEDULES.items():
    plan = {h: max(FLOOR, math.ceil(DEMAND[h] * k)) for h in range(OPEN_HOUR, CLOSE_HOUR)}
    for h, c in plan.items():
        staffing.append({"scenario": name, "hour": h, "couriers": c})
    for s in SCALES:
        for rep in range(REPS):
            for r in run_day(Params(plan, demand_scale=s, seed=20_000 + rep)):
                r.update(scenario=name, demand_scale=s, rep=rep)
                orders.append(r)

con = duckdb.connect(str(ROOT / "simulation.duckdb"))
odf, sdf = pd.DataFrame(orders), pd.DataFrame(staffing)
con.execute("CREATE OR REPLACE TABLE stress_orders AS SELECT * FROM odf")
con.execute("CREATE OR REPLACE TABLE stress_staffing AS SELECT * FROM sdf")
con.execute((ROOT / "sql" / "04_forecast_stress.sql").read_text())
con.sql("SELECT * FROM forecast_stress").write_csv(str(ROOT / "results" / "forecast_stress_test.csv"))
print(con.sql("SELECT * FROM forecast_stress ORDER BY scenario, demand_scale"))
con.close()
