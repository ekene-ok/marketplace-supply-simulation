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

# Chart 1: service vs courier hours ---------------------------------------------------------
s = pd.read_csv(RES / "scenario_summary.csv")
fig, ax = b.figure(8, 5)
for plan, col, lw in [("flat", b.CONTEXT, 2.2), ("shaped", HL, 2.6)]:
    d = s[s.plan_type == plan].sort_values("courier_hours_per_day")
    ax.plot(d.courier_hours_per_day, d.on_time_rate * 100, color=col, linewidth=lw, marker="o", markersize=4)
ax.axhline(90, color=b.HAIRLINE, linewidth=1)
ax.text(530, 90.3, "Target: 90% on time", ha="right", va="bottom", fontsize=9.5, color=b.MUTED)
pick = s[s.scenario == "shaped_0.36"].iloc[0]
top = s[s.scenario == "shaped_0.45"].iloc[0]
flat = s[s.scenario == "flat_28"].iloc[0]
ax.annotate(f"{pick.courier_hours_per_day:.0f} hours: {pick.on_time_rate:.1%}", (pick.courier_hours_per_day, pick.on_time_rate * 100),
            xytext=(10, -20), textcoords="offset points", ha="left", fontsize=10, color=b.INK)
ax.annotate(f"{top.courier_hours_per_day:.0f} hours: {top.on_time_rate:.1%}", (top.courier_hours_per_day, top.on_time_rate * 100),
            xytext=(0, 12), textcoords="offset points", ha="center", fontsize=10, color=b.INK)
ax.text(372, 84.5, f"Flat schedule needs {flat.courier_hours_per_day:.0f} hours\nfor {flat.on_time_rate:.1%}", fontsize=9.5, color=b.MUTED)
ax.text(188, 72, "Shaped to demand", fontsize=10, color=HL)
ax.set_ylim(64, 97)
ax.set_xlim(150, 535)
ax.set_xlabel("Courier hours per day", color=b.MUTED, fontsize=10)
ax.set_yticks([70, 80, 90])
ax.set_yticklabels(["70%", "80%", "90%"])
b.clean(ax, keep="x")
b.headline(fig, "Past about 93% on time, extra couriers buy almost nothing",
           "Share of deliveries within 35 minutes, by courier hours scheduled per day")
b.source(fig, SRC)
b.finish(fig, OUT / "01_service_vs_courier_hours.png", top=0.83, bottom=0.17, left=0.08)

# Chart 2: forecast stress test ---------------------------------------------------------------
f = pd.read_csv(RES / "forecast_stress_test.csv")
fig, ax = b.figure(8, 5)
for sc, col, lw, lbl in [("shaped_0.36", b.CONTEXT, 2.2, "Planned on forecast: 234 hours"),
                         ("shaped_0.39", HL, 2.6, "One step up: 255 hours")]:
    d = f[f.scenario == sc].sort_values("demand_scale")
    x = (d.demand_scale - 1) * 100
    ax.plot(x, d.worst_hour_on_time_rate * 100, color=col, linewidth=lw, marker="o", markersize=4)
    ax.text(x.iloc[-1] + 1.2, d.worst_hour_on_time_rate.iloc[-1] * 100, lbl, va="center", fontsize=10,
            color=HL if col == HL else b.MUTED)
ax.axhline(85, color=b.HAIRLINE, linewidth=1)
ax.text(-20, 85.3, "Floor: 85% in every hour", va="bottom", fontsize=9.5, color=b.MUTED)
ax.set_xlim(-22, 46)
ax.set_xticks([-20, -10, 0, 10, 20])
ax.set_xticklabels(["-20%", "-10%", "Forecast", "+10%", "+20%"])
ax.set_ylim(76, 96)
ax.set_yticks([80, 85, 90, 95])
ax.set_yticklabels(["80%", "85%", "90%", "95%"])
ax.set_xlabel("Actual demand compared with forecast", color=b.MUTED, fontsize=10)
b.clean(ax, keep="x")
b.headline(fig, "Nine percent more courier hours protect service if demand runs high",
           "On-time rate in the worst hour of the day, when actual demand misses the forecast")
b.source(fig, SRC)
b.finish(fig, OUT / "02_forecast_stress_test.png", top=0.83, bottom=0.17, left=0.08)

# Chart 3: the buffered schedule hour by hour -------------------------------------------------
from math import ceil
sys.path.insert(0, str(ROOT))
from sim.model import DEMAND, OPEN_HOUR, CLOSE_HOUR
hours = list(range(OPEN_HOUR, CLOSE_HOUR))
couriers = [max(6, ceil(DEMAND[h] * 0.39)) for h in hours]
fig, ax = b.figure(8, 5)
peak = max(couriers)
ax.bar(hours, couriers, width=0.65, color=[HL if c == peak else b.CONTEXT for c in couriers])
for x, c in zip(hours, couriers):
    ax.text(x, c + 0.6, f"{c}", ha="center", fontsize=10, color=b.INK if c == peak else b.MUTED)
ax.axhline(28, color=b.HAIRLINE, linewidth=1)
ax.text(15, 28.6, "Flat schedule: 28 all day", ha="center", fontsize=9.5, color=b.MUTED)
ax.set_xticks(hours)
ax.set_xticklabels([f"{x % 12 or 12}{'am' if x < 12 else 'pm'}" for x in hours])
ax.set_yticks([])
ax.set_ylim(0, 46)
b.clean(ax, keep="x")
b.headline(fig, "Couriers should follow the lunch and dinner rush",
           "Couriers online each hour in the recommended schedule (255 hours a day, minimum of 6)")
b.source(fig, SRC)
b.finish(fig, OUT / "03_hourly_schedule.png", top=0.83, bottom=0.12, left=0.04)
print("charts saved")
