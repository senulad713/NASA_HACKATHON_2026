"""
main.py - run the Mini Mars Rover Route Planner.

    py main.py                              (default start/goal)
    py main.py --start 5 5 --goal 45 45     (choose your own, as row col)
    py main.py --seed 7                     (a different random terrain)
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt #plt nickname
from matplotlib.colors import ListedColormap

from terrain import make_terrain, CELL_SIZE_M, MAX_SLOPE_DEG
from planner import astar, route_metrics, SAFE_WEIGHTS, SHORTEST_WEIGHTS

parser = argparse.ArgumentParser()
parser.add_argument("--start", nargs=2, type=int, default=[5, 5]) #this is the beginning of the route, the starting point of the rover
parser.add_argument("--goal", nargs=2, type=int, default=[44, 44]) #this is the end of the route, the goal point of the rover
parser.add_argument("--seed", type=int, default=42) #seed number for the terrain 
parser.add_argument("--size", type=int, default=50) #grid scale 50 x 50, the size of the terrain grid
args = parser.parse_args()

start, goal = tuple(args.start), tuple(args.goal)
t = make_terrain(args.size, args.seed)

# ---- plan two routes ----
safe = astar(t, start, goal, SAFE_WEIGHTS)
shortest = astar(t, start, goal, SHORTEST_WEIGHTS)

if safe is None:
    print("No route found - start/goal blocked or destination unreachable.")
    raise SystemExit

print(f"Grid: {args.size}x{args.size} cells, {CELL_SIZE_M:.0f} m per cell, "
      f"slope limit {MAX_SLOPE_DEG:.0f} deg\n")
print(f"{'':18}{'SHORTEST':>12}{'SAFE (best)':>14}")
m_short, m_safe = route_metrics(t, shortest), route_metrics(t, safe)
for key in m_safe:
    print(f"{key:18}{m_short[key]:>12}{m_safe[key]:>14}")

# ---- plot ----
fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
extent = None

def draw_routes(ax):
    for path, colour, label in [(shortest, "white", "Shortest"), (safe, "red", "Safe (chosen)")]:
        rows, cols = zip(*path)
        ax.plot(cols, rows, color=colour, lw=2.2, label=label,
                ls="--" if label == "Shortest" else "-")
    ax.scatter(*start[::-1], c="lime", s=120, edgecolors="black", zorder=5, label="Start")
    ax.scatter(*goal[::-1], c="gold", s=180, marker="*", edgecolors="black", zorder=5, label="Goal")
    blocked = np.ma.masked_where(t["traversable"], np.ones_like(t["slope"]))
    ax.imshow(blocked, cmap=ListedColormap(["black"]), alpha=0.55)

# 1) elevation
im = axes[0].imshow(t["elevation"], cmap="copper")
fig.colorbar(im, ax=axes[0], label="Elevation (m)")
draw_routes(axes[0])
axes[0].set_title("Elevation + routes (black = blocked)")
axes[0].legend(loc="lower left", fontsize=8)

# 2) slope
im = axes[1].imshow(t["slope"], cmap="magma")
fig.colorbar(im, ax=axes[1], label="Slope (deg)")
draw_routes(axes[1])
axes[1].set_title(f"Slope (blocked if > {MAX_SLOPE_DEG:.0f} deg)")

# 3) hazard
im = axes[2].imshow(t["hazard"], cmap="Reds")
fig.colorbar(im, ax=axes[2], label="Hazard (0-1)")
draw_routes(axes[2])
axes[2].set_title("Hazard (rocks / loose sand)")

for ax in axes:
    ax.set_xlabel("column (x 10 m)")
    ax.set_ylabel("row (x 10 m)")

fig.suptitle("Mini Mars Rover Route Planner - shortest vs safe route", fontsize=14)
plt.tight_layout()
plt.savefig("route_result.png", dpi=120)
print("\nSaved plot -> route_result.png")
plt.show()
