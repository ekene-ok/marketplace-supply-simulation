"""Discrete-event simulation of a delivery marketplace in one city (SimPy).

One simulated day runs 10:00 to 23:00. Orders arrive as a Poisson process whose rate
follows an hourly demand curve with lunch and dinner peaks. Each order:
  1. waits for a free courier (first come, first served)
  2. the courier travels to the restaurant (food has been cooking since the order)
  3. the courier waits if the food is not ready
  4. the courier delivers, then becomes free at the customer's location
Courier supply follows an hourly staffing plan. When the plan steps down, couriers finish
their current order before going offline.
"""
from dataclasses import dataclass
import numpy as np
import simpy

OPEN_HOUR, CLOSE_HOUR = 10, 23
# Orders per hour for a mid-sized launch city, 10:00 to 22:00 start hours.
DEMAND = {10: 18, 11: 48, 12: 72, 13: 46, 14: 24, 15: 20, 16: 26, 17: 58, 18: 98, 19: 104, 20: 66, 21: 36, 22: 18}
TO_RESTAURANT = (2.0, 3.0)   # gamma(shape, scale) minutes, mean 6
PREP = (4.0, 3.0)            # mean 12
TO_CUSTOMER = (3.0, 3.0)     # mean 9


@dataclass
class Params:
    staffing: dict            # hour -> couriers online
    demand_scale: float = 1.0
    seed: int = 0


def run_day(p: Params) -> list[dict]:
    rng = np.random.default_rng(p.seed)
    env = simpy.Environment(initial_time=OPEN_HOUR * 60)
    couriers = simpy.Store(env)
    state = {"online": 0, "next_id": 0}
    records = []

    def set_level(target):
        while state["online"] < target:
            couriers.put(state["next_id"])
            state["next_id"] += 1
            state["online"] += 1
        while state["online"] > target:
            env.process(retire())
            state["online"] -= 1

    def retire():
        yield couriers.get()  # takes the next courier to become free off the road

    def scheduler():
        for h in range(OPEN_HOUR, CLOSE_HOUR):
            set_level(p.staffing[h])
            yield env.timeout(60)

    def order(oid, t0):
        ready_at = t0 + rng.gamma(*PREP)
        c = yield couriers.get()
        assigned = env.now
        yield env.timeout(rng.gamma(*TO_RESTAURANT))
        food_wait = max(0.0, ready_at - env.now)
        yield env.timeout(food_wait)
        yield env.timeout(rng.gamma(*TO_CUSTOMER))
        records.append({"order_id": oid, "hour": int(t0 // 60), "placed_min": t0,
                        "courier_wait_min": assigned - t0, "food_wait_min": food_wait,
                        "delivery_min": env.now - t0})
        couriers.put(c)

    def arrivals():
        oid = 0
        while env.now < CLOSE_HOUR * 60:
            h = int(env.now // 60)
            rate = DEMAND[h] * p.demand_scale / 60.0
            gap = rng.exponential(1 / rate)
            # do not let one gap jump across an hour boundary at the old rate
            boundary = (h + 1) * 60
            if env.now + gap >= boundary:
                yield env.timeout(boundary - env.now)
                continue
            yield env.timeout(gap)
            if env.now < CLOSE_HOUR * 60:
                env.process(order(oid, env.now))
                oid += 1

    env.process(scheduler())
    env.process(arrivals())
    env.run(until=CLOSE_HOUR * 60 + 180)  # let late orders finish
    return records
