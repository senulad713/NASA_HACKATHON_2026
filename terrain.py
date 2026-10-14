"""
terrain.py - makes a fake (synthetic) Mars terrain grid.

Every cell of the grid has:
  elevation   (metres)
  slope       (degrees)      -> CALCULATED from elevation
  roughness   (0..1)         -> how bumpy the ground is
  hazard      (0..1)         -> rocks / loose sand risk
  traversable (True/False)   -> can the rover enter this cell at all?
"""

import numpy as np

CELL_SIZE_M = 10.0      # each cell = 10 m x 10 m of ground (assumption)
MAX_SLOPE_DEG = 25.0    # steeper than this = blocked (hard constraint, assumption)


def make_terrain(size=50, seed=42):
    rng = np.random.default_rng(seed)          # same seed -> same map every time
    y, x = np.mgrid[0:size, 0:size]            # row / column index of every cell

    # ---- 1. Elevation: flat plain + some hills + a crater ----
    elevation = np.zeros((size, size))

    for _ in range(6):                          # 6 random hills (Gaussian "bumps"), range(n) 'n' value of hills formed
        cx, cy = rng.uniform(0, size, 2)        # hill centre
        height = rng.uniform(15, 45)           # hill height in metres (15 - 45m) randomly chosen
        width = rng.uniform(4, 8)               # hill width in cells
        elevation += height * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * width ** 2))

    # a crater in the middle: a dip with a raised rim crator always has the same place
    cx, cy = size * 0.5, size * 0.5
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    elevation += -35 * np.exp(-(r ** 2) / (2 * 4 ** 2)) + 12 * np.exp(-((r - 7) ** 2) / (2 * 1.5 ** 2))

    # small random bumps everywhere (like small rocks/ripples)
    elevation += rng.normal(0, 0.5, (size, size))

    # ---- 2. Slope (derived from elevation) ----
    # np.gradient = how much elevation changes per cell in each direction.
    # Divide by cell size to get metres-per-metre, then slope = arctan(sqrt(dz/dx^2 + dz/dy^2)).
    dz_dy, dz_dx = np.gradient(elevation, CELL_SIZE_M)
    slope = np.degrees(np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2)))

    # ---- 3. Roughness: how different a cell is from its neighbours ----
    padded = np.pad(elevation, 1, mode="edge")
    neighbours_mean = sum(
        padded[1 + dr: 1 + dr + size, 1 + dc: 1 + dc + size]
        for dr in (-1, 0, 1) for dc in (-1, 0, 1)
    ) / 9
    roughness = np.abs(elevation - neighbours_mean)
    roughness = roughness / roughness.max()     # normalise to 0..1

    # ---- 4. Hazards: a few random rock fields / sand patches ----
    hazard = np.zeros((size, size))
    for _ in range(5):
        hx, hy = rng.uniform(0, size, 2)
        hw = rng.uniform(2, 5)
        hazard += np.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * hw ** 2))
    hazard = np.clip(hazard, 0, 1)

    # ---- 5. Traversable? (hard constraints) ----
    traversable = (slope <= MAX_SLOPE_DEG) & (hazard < 0.9)

    return {
        "elevation": elevation,
        "slope": slope,
        "roughness": roughness,
        "hazard": hazard,
        "traversable": traversable,
    }
