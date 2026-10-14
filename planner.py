"""
planner.py - the cost model + A* route planner.

COST MODEL (the cost of moving from one cell into the next):

    step_cost = distance * (1
                            + w_slope  * (slope / MAX_SLOPE)^2
                            + w_hazard * hazard
                            + w_rough  * roughness)
                + w_climb * uphill_metres

  - distance   : 10 m straight, ~14.1 m diagonal. Longer = more time and battery.
  - slope      : squared, so gentle slopes are cheap but steep ones get expensive
                 fast (more energy, more wheel slip, tip-over risk).
  - hazard     : rocks / loose sand -> risk of damage or getting stuck.
  - roughness  : bumpy ground = slower driving and more wear.
  - climb      : going UP uses extra energy (going down doesn't get this penalty).
  - blocked    : cells that are not traversable can never be entered (hard constraint).

Setting every weight to 0 turns this into a pure "shortest path" planner,
which lets us compare "shortest" vs "best".
"""

import heapq        # to-do list that always gives back the smallest score first
import math         # math.hypot = Pythagoras
import numpy as np
from terrain import CELL_SIZE_M, MAX_SLOPE_DEG  # 10 m per square, 25 degree limit

# the 8 directions the rover can move in (4 straight + 4 diagonal)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1),  (1, 1)]
#          up       down    left    right   up-left  up-right  down-left down-right

# bigger weight = rover avoids that thing more (hazard is avoided the most)
SAFE_WEIGHTS = {"slope": 3.0, "hazard": 4.0, "rough": 1.0, "climb": 0.5} #the rovers personality
SHORTEST_WEIGHTS = {"slope": 0.0, "hazard": 0.0, "rough": 0.0, "climb": 0.0}  # cares only about distance


# ---------------- 1. COST OF ONE STEP ----------------
# t = terrain, a = square you leave, b = square you go to, w = weights
def step_cost(t, a, b, w):
    """Cost of driving from cell a to neighbour cell b."""
    distance = CELL_SIZE_M * math.hypot(b[0] - a[0], b[1] - a[1]) # b = the square ur going to, w = weights from the cost mode
    penalty = (1                                                    # 1 = perfect ground, no extra cost
               + w["slope"] * (t["slope"][b] / MAX_SLOPE_DEG) ** 2  # squared: steep gets expensive fast
               + w["hazard"] * t["hazard"][b]   #t =  terrain from terrian.py, a = the square ur leaving from,
               + w["rough"] * t["roughness"][b])
    climb = max(0.0, t["elevation"][b] - t["elevation"][a])   # only uphill counts
    return distance * penalty + w["climb"] * climb


# ---------------- 2. HEURISTIC (h = the guess) ----------------
def heuristic(a, b):
    """Straight-line distance in metres. The real cost is always >= distance,
    so this never over-estimates -> A* still finds the cheapest route."""
    return CELL_SIZE_M * math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------- 3. A* SEARCH ----------------
def astar(t, start, goal, w):
    rows, cols = t["elevation"].shape
    ok = t["traversable"]                           # True/False: can the rover enter?
    if not ok[start] or not ok[goal]:
        return None                                 # start or goal is inside blocked terrain

    open_list = [(heuristic(start, goal), start)]   # to-do list of (f, square)
    g = {start: 0.0}                                # g = cheapest cost so far to each square
    came_from = {}                                  # parent list: square -> where we came from

    while open_list:
        _, cur = heapq.heappop(open_list)           # take the square with the smallest f
        if cur == goal:                             # reached the goal: rebuild the route
            path = [cur]
            while cur in came_from:                 # follow parents back to the start
                cur = came_from[cur]
                path.append(cur)
            return path[::-1]                       # flip: goal->start becomes start->goal

        for dr, dc in MOVES:
            nxt = (cur[0] + dr, cur[1] + dc)
            if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or not ok[nxt]:
                continue #  skip this neighbour, go to the next direction
            ''' don't cut diagonally between two blocked cells moving diagonally can be hard for
            # a rover to do, so we don't allow it if either of the two adjacent cells is blocked'''
            if dr and dc and not (ok[cur[0] + dr, cur[1]] and ok[cur[0], cur[1] + dc]):
                continue
            new_g = g[cur] + step_cost(t, cur, nxt, w)      # cost to reach nxt this way
            if new_g < g.get(nxt, float("inf")):            # cheaper than before? (never seen = infinity)
                g[nxt] = new_g
                came_from[nxt] = cur
                heapq.heappush(open_list, (new_g + heuristic(nxt, goal), nxt))  # f = g + h

    return None                                     # no route exists


# ---------------- 4. ROUTE METRICS (the trip report card) ----------------
# zip(path, path[1:]) pairs each square with the next one = every step
def route_metrics(t, path):
    """Numbers that describe a route. Always scored with the SAFE cost model,
    so the two routes can be compared fairly."""
    dist = sum(CELL_SIZE_M * math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    cost = sum(step_cost(t, a, b, SAFE_WEIGHTS) for a, b in zip(path, path[1:]))
    elev = np.array([t["elevation"][p] for p in path])     # height of every square on the route
    return {
        "distance_m": round(dist, 1),
        "route_cost": round(cost, 1),
        "elevation_gain_m": round(float(np.sum(np.clip(np.diff(elev), 0, None))), 1),  # uphill only
        "max_slope_deg": round(float(max(t["slope"][p] for p in path)), 1),
        "avg_hazard": round(float(np.mean([t["hazard"][p] for p in path])), 3),
    }
