"""README charts in the portfolio chart style: one message per chart, one highlight colour, direct labels."""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import brand_style as b

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "results", ROOT / "charts"
OUT.mkdir(exist_ok=True)
HL = b.PROJECT["marketplace-supply-simulation"]
SRC = "SimPy simulation, 30 days per schedule, about 630 orders a day; courier cost $22 an hour"

# Chart 1: staffing to the rush costs far less per order for the same service
s = pd.read_csv(RES / "scenario_summary.csv").set_index("scenario")
flat, rush = s.loc["flat_28"], s.loc["shaped_0.39"]
fig, ax = b.chart(height=3.5, label_in=1.75)
b.hbar(ax, ["Same staff all day", "Staff to the rush"], [flat.courier_cost_per_order, rush.courier_cost_per_order], {1},
       lambda v: f"${v:.2f}", HL)
b.titles(fig, "Staffing couriers to the lunch and dinner rush cuts cost per order by 31%",
         f"Courier cost per order. Both hit the service target; the rush schedule uses "
         f"{rush.courier_hours_per_day:.0f} hours a day, not {flat.courier_hours_per_day:.0f}")
b.credit(fig, SRC)
b.save(fig, OUT / "01_service_vs_courier_hours.png")

# Chart 2: forecast stress test
f = pd.read_csv(RES / "forecast_stress_test.csv")
fig, ax = b.chart(height=4.6, label_in=0.45, xaxis=True, right_in=1.1)
for sc, col, lbl in [("shaped_0.36", b.CONTEXT, "No buffer\n234 hrs"), ("shaped_0.39", HL, "9% buffer\n255 hrs")]:
    d = f[f.scenario == sc].sort_values("demand_scale")
    x = (d.demand_scale - 1) * 100
    ax.plot(x, d.worst_hour_on_time_rate * 100, color=col, linewidth=2.4)
    ax.text(x.iloc[-1] + 1, d.worst_hour_on_time_rate.iloc[-1] * 100, lbl, va="center", fontsize=b.VALUE,
            color=HL if col == HL else b.MUTED)
ax.axhline(85, color=b.HAIRLINE, linewidth=1)
ax.text(-20, 84.7, "85% floor", va="top", fontsize=9.5, color=b.MUTED)
ax.set_xlim(-21, 21)
ax.set_xticks([-20, -10, 0, 10, 20])
ax.set_xticklabels(["-20%", "-10%", "Forecast", "+10%", "+20%"])
ax.set_ylim(76, 96)
ax.set_yticks([80, 90])
ax.set_yticklabels(["80%", "90%"])
ax.set_xlabel("Actual demand against forecast", color=b.MUTED, fontsize=9.5)
b.line_axes(ax)
b.titles(fig, "A 9% buffer keeps deliveries on time when demand beats the forecast",
         "On-time rate in the day's slowest hour, for the rush schedule with and without a buffer")
b.credit(fig, SRC)
b.save(fig, OUT / "02_forecast_stress_test.png")

# Chart 3: the buffered schedule hour by hour
from math import ceil
sys.path.insert(0, str(ROOT))
from sim.model import DEMAND, OPEN_HOUR, CLOSE_HOUR
hours = list(range(OPEN_HOUR, CLOSE_HOUR))
couriers = [max(6, ceil(DEMAND[h] * 0.39)) for h in hours]
fig, ax = b.chart(height=4.4, label_in=0.0, right_in=0.3, xaxis="ticks")
b.vbar(ax, [f"{x % 12 or 12}{'am' if x < 12 else 'pm'}" for x in hours], couriers,
       {i for i, c in enumerate(couriers) if c > 28}, lambda v: f"{v}", HL)
ax.axhline(28, color=b.HAIRLINE, linewidth=1)
ax.text(len(hours) - 0.5, 28.8, "Same all day: 28", ha="right", fontsize=9.5, color=b.MUTED)
ax.tick_params(axis="x", labelsize=9.5)
b.titles(fig, "Couriers should follow the lunch and dinner rush",
         "Couriers online each hour in the recommended 255-hour schedule")
b.credit(fig, SRC)
b.save(fig, OUT / "03_hourly_schedule.png")
print("charts saved")
