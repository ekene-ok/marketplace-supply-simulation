"""README charts: one message per chart, one highlight colour, direct labels."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "results", ROOT / "charts"
OUT.mkdir(exist_ok=True)
SURFACE, INK, INK2 = "#ffffff", "#1a1a1a", "#6b6a66"
HIGHLIGHT, CONTEXT = "#2f8a2f", "#d9d8d3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def titles(fig, title, subtitle):
    fig.text(0.03, 0.97, title, fontsize=15, fontweight="bold", va="top")
    fig.text(0.03, 0.885, subtitle, fontsize=10.5, color=INK2, va="top")


best = pd.read_csv(RES / "cheapest_plan_meeting_target.csv").set_index("plan_type")

# Chart 1: courier hours needed to hit the same service target
fig, ax = plt.subplots(figsize=(9, 3.9))
vals = [best.loc["flat", "courier_hours_per_day"], best.loc["shaped", "courier_hours_per_day"]]
labels = [f"Flat ({int(best.loc['flat', 'scenario'].split('_')[1])} all day)", "Shaped to demand"]
ax.barh(labels, vals, height=0.5, color=[CONTEXT, HIGHLIGHT])
ax.text(vals[0] + 6, 0, f"{vals[0]:.0f} hours  (${best.loc['flat', 'courier_cost_per_order']:.2f} per order)",
        va="center", fontsize=11, color=INK2)
ax.text(vals[1] + 6, 1, f"{vals[1]:.0f} hours  (${best.loc['shaped', 'courier_cost_per_order']:.2f} per order)",
        va="center", fontsize=12, fontweight="bold")
for lbl, c in zip(ax.get_yticklabels(), [INK2, INK]):
    lbl.set_color(c)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks([])
ax.tick_params(axis="y", length=0, pad=8)
ax.set_xlim(0, 640)
cut = 1 - vals[1] / vals[0]
titles(fig, f"Matching couriers to demand needs {cut:.0%} fewer courier hours",
       "Courier hours per day to keep 90% of deliveries under 35 minutes, and at least 85%\n"
       "in every hour. 30 simulated days per schedule, about 630 orders a day.")
fig.subplots_adjust(left=0.22, right=0.97, top=0.66, bottom=0.05)
fig.savefig(OUT / "01_courier_hours_needed.png", dpi=200)
plt.close(fig)

# Chart 2: the shaped schedule hour by hour
h = pd.read_csv(RES / "hourly_service.csv")
shaped = h[h["plan_type"] == "shaped"].sort_values("hour")
flat_n = int(best.loc["flat", "scenario"].split("_")[1])
fig, ax = plt.subplots(figsize=(9, 5.0))
ax.bar(shaped["hour"], shaped["couriers"], width=0.65, color=HIGHLIGHT)
for x, c in zip(shaped["hour"], shaped["couriers"]):
    ax.text(x, c + 0.8, f"{c}", ha="center", fontsize=10, color=INK)
ax.axhline(flat_n, color=INK2, linewidth=1.2, linestyle=(0, (4, 3)))
ax.text(22.45, flat_n + 0.8, f"Flat schedule: {flat_n}", ha="right", fontsize=10, color=INK2)
ax.set_xticks(shaped["hour"])
ax.set_xticklabels([f"{x % 12 or 12}{'am' if x < 12 else 'pm'}" for x in shaped["hour"]])
for s in ax.spines.values():
    s.set_visible(False)
ax.set_yticks([])
ax.tick_params(axis="x", length=0, labelsize=10)
ax.set_ylim(0, 44)
titles(fig, "Couriers should follow the lunch and dinner rush",
       "Couriers online per hour in the shaped schedule (minimum of 6), against a flat 28.\n"
       "Every hour stays at 88% on time or better.")
fig.subplots_adjust(left=0.03, right=0.97, top=0.75, bottom=0.08)
fig.savefig(OUT / "02_hourly_schedule.png", dpi=200)
plt.close(fig)
print("Charts saved to charts/")
