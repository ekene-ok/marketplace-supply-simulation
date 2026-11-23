"""Run staffing scenarios through the simulation and store every order in DuckDB.

Scenarios
  flat_N      N couriers online every hour (the simple schedule)
  shaped_K    couriers each hour = max(6, ceil(K x expected orders that hour)): matched to
              demand, with a floor of 6 so quiet hours keep enough cover
Each scenario runs 30 simulated days with different random seeds.
"""
from pathlib import Path
import sys
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import duckdb
import pandas as pd
from sim.model import run_day, Params, DEMAND, OPEN_HOUR, CLOSE_HOUR

ROOT = Path(__file__).resolve().parents[1]
REPS = 30
COURIER_HOURLY_COST = 22.0  # CAD per online courier hour (planning assumption)

scenarios = {}
for n in range(20, 41, 2):
    scenarios[f"flat_{n}"] = {h: n for h in range(OPEN_HOUR, CLOSE_HOUR)}
FLOOR = 6  # minimum couriers online in any hour, so quiet hours are not starved
for k in [0.24, 0.27, 0.30, 0.33, 0.36, 0.39, 0.42, 0.45, 0.48]:
    scenarios[f"shaped_{k:.2f}"] = {h: max(FLOOR, math.ceil(DEMAND[h] * k)) for h in range(OPEN_HOUR, CLOSE_HOUR)}

orders, staffing = [], []
for name, plan in scenarios.items():
    for h, c in plan.items():
        staffing.append({"scenario": name, "plan_type": name.split("_")[0], "hour": h, "couriers": c})
    for rep in range(REPS):
        for r in run_day(Params(plan, seed=10_000 + rep)):
            r.update(scenario=name, rep=rep)
            orders.append(r)

con = duckdb.connect(str(ROOT / "simulation.duckdb"))
odf, sdf = pd.DataFrame(orders), pd.DataFrame(staffing)
con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM odf")
con.execute("CREATE OR REPLACE TABLE staffing AS SELECT * FROM sdf")
con.execute(f"CREATE OR REPLACE TABLE assumptions AS SELECT {COURIER_HOURLY_COST} AS courier_hourly_cost, {REPS} AS reps")
print(f"{len(odf):,} simulated orders across {len(scenarios)} scenarios x {REPS} days")
con.close()
