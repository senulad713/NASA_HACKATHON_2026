# Martian Map: Rover Route Planner

Code notes for the three files in the project:

| File         | Job                                                                 |
| ------------ | ------------------------------------------------------------------- |
| `terrain.py` | Builds a fake Mars map: hills, a crater, bumps, slope, roughness, hazards |
| `planner.py` | Prices every move and uses **A\*** to find the cheapest route       |
| `main.py`    | Reads settings, runs the planner twice, compares and plots the routes |

## Contents

1. [terrain.py](#1-terrainpy)
   - [1.1 Settings: size and seed](#11-settings-size-and-seed)
   - [1.2 Coordinates (mesh grids)](#12-coordinates-mesh-grids)
   - [1.3 Hills](#13-hills)
   - [1.4 Crater](#14-crater)
   - [1.5 Small random bumps](#15-small-random-bumps)
   - [1.6 Slope](#16-slope)
   - [1.7 Roughness](#17-roughness)
   - [1.8 Hazards](#18-hazards)
   - [1.9 Traversable: the final condition](#19-traversable-the-final-condition)
2. [planner.py](#2-plannerpy)
   - [2.1 Imports](#21-imports)
   - [2.2 Cost model: every move has a price](#22-cost-model-every-move-has-a-price)
   - [2.3 Weights: the rover's personality](#23-weights-the-rovers-personality)
   - [2.4 Heuristic](#24-heuristic)
   - [2.5 A\* search](#25-a-search)
   - [2.6 Route metrics](#26-route-metrics)
3. [main.py](#3-mainpy)
   - [3.1 Command-line settings](#31-command-line-settings)
   - [3.2 Running A\* twice](#32-running-a-twice)
   - [3.3 Printing the comparison](#33-printing-the-comparison)
   - [3.4 Plotting the routes](#34-plotting-the-routes)
4. [Limitations](#4-limitations)

---

# 1. terrain.py

## 1.1 Settings: size and seed

```python
def make_terrain(size=50, seed=42):
```

- **`size=50`** creates a 50 × 50 grid. One cell = 10 m, so the map is 500 m × 500 m.
- **`seed=42`** gives the exact same hills every time the code runs. Without a seed, every run would produce a different map.

## 1.2 Coordinates (mesh grids)

In short, `mgrid` lets the code draw shapes on the map, like the hills, the crater and the hazard patches.

```python
y, x = np.mgrid[0:3, 0:3]
```

```
     y            x
   0 0 0        0 1 2
   1 1 1        0 1 2
   2 2 2        0 1 2
```

- It works like a spreadsheet: `y` is the **row number** down the side and `x` is the **column** across the top, written into every cell so NumPy can use them in calculations.
- NumPy reads grids like tables, **row first, then column**. That's why `mgrid` gives back `y` first.
- Examples: top-left corner is `[y=0, x=0]`; bottom-left corner is `[y=2, x=0]`.

## 1.3 Hills

![[Pasted image 20260930221753.png|507]]

```python
for _ in range(6):
    cx, cy = rng.uniform(0, size, 2)
    height = rng.uniform(15, 45)
    width = rng.uniform(4, 8)
    elevation += height * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * width ** 2))
```

| Setting  | What it controls                 | Unit                      | Real-world meaning            |
| -------- | -------------------------------- | ------------------------- | ----------------------------- |
| `cx, cy` | **where** the hill is            | grid squares              | where you pour the sand       |
| `height` | **how tall** (15–45)             | metres                    | how much sand you pour        |
| `width`  | **how spread out** (4–8)         | squares (1 square = 10 m), so 40–80 m | a narrow pile or a wide pile |

The loop runs **6 times**, and each hill gets **new random values**.

**The rule: the closer a square is to the centre, the taller it gets.** For every square, the long line:

1. works out **how far** the square is from the hill's centre, and
2. turns that distance into a **height**: close means tall, far means low.

#### Q) What is the difference between a hill with `width = 4` and `width = 8`?

Both hills can be the **same height**, but one spreads that height over a much longer distance. For two 30 m hills:

- one goes from flat to its peak in **4 squares**
- the other goes from flat to its peak in **8 squares**

The `width = 8` hill is less steep, so the rover can climb it more easily.

#### Q) If `width = 4` and `height = 45`, is the hill gentle or steep?

**Steep.** It has the tallest possible height (45 m) packed into the narrowest possible width (4 squares). The rover would struggle to drive over it.

## 1.4 Crater

```python
cx, cy = size * 0.5, size * 0.5
```

- The crater is **not randomised**. With `size = 50`, 50 × 0.5 = 25, so its centre is **(25, 25)**, the middle of the map.

```python
r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
```

- Works out how far every square is from the crater's centre, using **Pythagoras' theorem**.

Worked example for the square at x = 28, y = 29:

| Step | Code      | What it does                      | Answer   |
| ---- | --------- | --------------------------------- | -------- |
| 1    | `x - cx`  | steps **across**: 28 − 25         | 3        |
| 2    | `y - cy`  | steps **down**: 29 − 25           | 4        |
| 3    | `** 2`    | square them: 3 × 3 and 4 × 4      | 9 and 16 |
| 4    | `+`       | add them: 9 + 16                  | 25       |
| 5    | `np.sqrt` | square root of 25                 | **5**    |

```python
elevation += -35 * np.exp(-(r ** 2) / (2 * 4 ** 2)) + 12 * np.exp(-((r - 7) ** 2) / (2 * 1.5 ** 2))
```

This is built exactly like a hill, in two parts:

- **−35** → a negative hill is a **hole**. It's deepest at the centre (35 m down) and gets shallower moving outward.
- **+12** → builds up 12 m in a ring about 7 squares out. **Plus = wall** (the crater rim).

```
   wall        wall
    ▲   hole    ▲
 ───┘╲         ╱└───
      ╲_______╱
```

## 1.5 Small random bumps

With hills and a crater added, the ground is still too smooth, so small random bumps go on top:

```python
elevation += rng.normal(0, 0.5, (size, size))
```

| Part           | Meaning                                                                         |
| -------------- | ------------------------------------------------------------------------------- |
| `0`            | numbers are **centred on 0**, so on average they don't raise or lower the map   |
| `0.5`          | they're **small**, usually between **−1 m and +1 m**                            |
| `(size, size)` | makes a whole 50 × 50 grid of them, one per square                              |

## 1.6 Slope

```python
dz_dy, dz_dx = np.gradient(elevation, CELL_SIZE_M)
slope = np.degrees(np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2)))
```

Imagine walking on the map:

- **Flat ground:** your height doesn't change → **slope = 0°**
- **Gentle ramp:** you go up a little with each step → **small slope**
- **Steep hill:** you go up a lot with each step → **big slope**

| Result  | Question it answers                                        |
| ------- | ---------------------------------------------------------- |
| `dz_dx` | how much does height change moving **across** (left ↔ right)? |
| `dz_dy` | how much does height change moving **down** (up ↔ down)?   |

Worked example with `dz_dx = 0.3` and `dz_dy = 0.4`:

| Step        | Calculation                 | Result  |
| ----------- | --------------------------- | ------- |
| Square both | 0.3² + 0.4² = 0.09 + 0.16   | 0.25    |
| Square root | √0.25                       | **0.5** |

Total steepness is **0.5**: up 0.5 m for every 1 m walked.

$$
0.5 \xrightarrow{\text{np.arctan}} 0.46 \text{ rad} \xrightarrow{\text{np.degrees}} 26.6°
$$

A square steeper than **25°** is blocked, because the rover can't drive over it.

## 1.7 Roughness

```python
padded = np.pad(elevation, 1, mode="edge")
neighbours_mean = sum(
    padded[1 + dr: 1 + dr + size, 1 + dc: 1 + dc + size]
    for dr in (-1, 0, 1) for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
) / 8
roughness = np.abs(elevation - neighbours_mean)
roughness = roughness / roughness.max()
```

**The idea:** is this square different from the ones around it?

- About the **same height** as its neighbours → **smooth**
- **Sticks up or dips down** compared with them → **rough** (a rock, a pit, a bump)

### Step 1: add a border (`np.pad`)

A square in the middle has 8 neighbours, but a corner square only has 3:

```
 ■  ■  ■            ✖  ✖  ✖
 ■  ●  ■  8 ✅      ✖  ●  ■  only 3 ❌
 ■  ■  ■            ✖  ■  ■  (✖ = off the map)
```

`np.pad` adds an **extra ring of squares** around the map, like a picture frame. `mode="edge"` fills the frame by **copying the nearest edge square**:

```
Before:            After np.pad:

                   1  1  2  3  3
  1  2  3          1  1  2  3  3
  4  5  6    →     4  4  5  6  6
  7  8  9          7  7  8  9  9
                   7  7  8  9  9
```

Copying the edge pretends the ground **carries on the same** just past the edge, which is a reasonable guess.

### Step 2: average the 8 neighbours

```
 ↖  ↑  ↗          (-1,-1)  (-1,0)  (-1,+1)
 ←  ●  →          ( 0,-1)  ( 0,0)  ( 0,+1)    (0,0) = centre → skipped
 ↙  ↓  ↘          (+1,-1)  (+1,0)  (+1,+1)
```

For every square, the code:

1. looks at the **8 neighbours** (up, down, left, right and the 4 diagonals),
2. **skips the centre** (the `if (dr, dc) != (0, 0)` line),
3. **adds up** the 8 heights and **divides by 8**.

### Step 3: how different is the square?

```python
roughness = np.abs(elevation - neighbours_mean)
roughness = roughness / roughness.max()
```

- **Square's height minus the neighbours' average.** `np.abs` removes the minus sign, so a bump **up** and a dip **down** both count as rough.
- Dividing by the maximum scales everything from **0 to 1**.

|        | Centre | 8 neighbours | Average | Difference | Result |
| ------ | ------ | ------------ | ------- | ---------- | ------ |
| Smooth | 10 m   | all 10 m     | 10 m    | 0          | smooth |
| Bump   | 14 m   | all 10 m     | 10 m    | 4          | rough  |
| Dip    | 7 m    | all 10 m     | 10 m    | 3          | rough  |

> **In one sentence:** roughness = how different a square's height is from the average of its 8 neighbours, scaled from 0 (smooth) to 1 (roughest).

## 1.8 Hazards

```python
hazard = np.zeros((size, size))
for _ in range(5):
    hx, hy = rng.uniform(0, size, 2)
    hw = rng.uniform(2, 5)
    hazard += np.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * hw ** 2))
hazard = np.clip(hazard, 0, 1)
```

Some ground is **dangerous even if it's flat**:

- **Rock fields:** sharp rocks can damage the wheels.
- **Loose sand:** the rover can **sink and get stuck**.

The code is almost the same as the hill loop. The key difference is that hazards go on a **separate map**, so the height isn't changed and the rover can track danger on its own.

|               | Hills                 | Hazards                           |
| ------------- | --------------------- | --------------------------------- |
| Start with    | `np.zeros` (flat map) | `np.zeros` (no danger anywhere)   |
| How many      | `range(6)` = 6 hills  | `range(5)` = **5 danger patches** |
| Random centre | `cx, cy`              | `hx, hy`                          |
| Random width  | `width` = 4–8         | `hw` = **2–5** (smaller patches)  |
| Shape         | Gaussian bump         | Gaussian bump, **same formula**   |
| What it adds  | **height** in metres  | **danger level**                  |

| Hazard value | Meaning                                    |
| ------------ | ------------------------------------------ |
| **0**        | safe ground 🟢                             |
| **0.5**      | some risk, edge of a rock field 🟡         |
| **1**        | very dangerous, centre of a sand trap 🔴   |

### Why `np.clip`?

If two patches overlap, their values **add up** (0.8 + 0.6 = **1.4**), which is off the scale. `np.clip` cuts anything above 1 down to 1, and anything below 0 up to 0.

| Before | After `np.clip` |
| ------ | --------------- |
| 1.4    | **1.0**         |
| 0.7    | 0.7 (unchanged) |
| 0.0    | 0.0 (unchanged) |

### How the rover uses it

- Hazard **≥ 0.9** → **blocked**, too dangerous to enter.
- Hazard **below 0.9** → allowed, but **costs more** the higher it is.

## 1.9 Traversable: the final condition

For every square, this asks: **"Can the rover drive here at all?"**

| Rule                 | Code                     | Meaning                  |
| -------------------- | ------------------------ | ------------------------ |
| 1. Not too steep     | `slope <= MAX_SLOPE_DEG` | slope is **25° or less** |
| 2. Not too dangerous | `hazard < 0.9`           | hazard is **below 0.9**  |

`&` means **AND**: a square is traversable only if **both** rules are true.

| Slope | Hazard | Rule 1 (≤ 25°) | Rule 2 (< 0.9) | Traversable?             |
| ----- | ------ | -------------- | -------------- | ------------------------ |
| 10°   | 0.2    | ✅             | ✅             | **True**, can drive      |
| 30°   | 0.2    | ❌             | ✅             | **False**, too steep     |
| 10°   | 0.95   | ✅             | ❌             | **False**, too dangerous |
| 30°   | 0.95   | ❌             | ❌             | **False**, both          |

---

# 2. planner.py

## 2.1 Imports

| Line                                             | What it brings in                                                     | Used for                                                   |
| ------------------------------------------------ | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| `import heapq`                                   | a **priority queue**: always hands back the **smallest** item first   | A\*: always checking the cheapest square next              |
| `import math`                                    | basic maths tools                                                     | `math.hypot` (10 m or 14.1 m moves), `math.inf` (infinity) |
| `import numpy as np`                             | NumPy                                                                 | `np.mean`, `np.diff` etc. in the route metrics             |
| `from terrain import CELL_SIZE_M, MAX_SLOPE_DEG` | two settings from `terrain.py`                                        | cell size (10 m) and slope limit (25°)                     |

## 2.2 Cost model: every move has a price

| Ground              | Price               |
| ------------------- | ------------------- |
| Flat, safe, smooth  | **cheap** 🟢        |
| Steep, bumpy, rocky | **expensive** 🔴    |
| Blocked             | **can't go** 🚫     |

A\* finds the route with the **smallest total bill**. That's how the rover avoids hard ground even when it's shorter.

### What makes up the price?

| # | Factor        | Why it costs more                       | Example                        |
| - | ------------- | --------------------------------------- | ------------------------------ |
| 1 | **Distance**  | longer = more battery and time          | 10 m straight, 14.1 m diagonal |
| 2 | **Slope**     | steep = slipping, tipping, more energy  | 20° costs much more than 5°    |
| 3 | **Hazard**    | rocks or sand = damage or getting stuck | hazard 0.8 costs a lot         |
| 4 | **Roughness** | bumpy = slower, more wear               | roughness 1 costs a bit more   |
| 5 | **Climbing**  | going uphill uses extra energy          | climbing 5 m costs extra       |

### The formula

$$\text{cost}(a \to b) = d \times \left(1 + w_s \left(\frac{S_b}{25}\right)^2 + w_h H_b + w_r R_b\right) + w_c \times \max(0,\; E_b - E_a)$$

In words:

```
cost = distance × (1 + slope extra + hazard extra + roughness extra) + climb extra
```

| Symbol                    | Meaning                                  | Unit / range                   |
| ------------------------- | ---------------------------------------- | ------------------------------ |
| a → b                     | moving **from** square a **to** square b |                                |
| **d**                     | distance of the move                     | 10 m straight, 14.1 m diagonal |
| **S_b**                   | slope of square b                        | degrees (0–25)                 |
| **25**                    | max allowed slope (`MAX_SLOPE_DEG`)      | degrees                        |
| **H_b**                   | hazard of square b                       | 0–1                            |
| **R_b**                   | roughness of square b                    | 0–1                            |
| **E_a, E_b**              | elevation of squares a and b             | metres                         |
| **max(0, E_b − E_a)**     | metres climbed (downhill = 0)            | metres                         |
| **w_s, w_h, w_r, w_c**    | weights for slope, hazard, roughness, climb | see [2.3](#23-weights-the-rovers-personality) |

### Diagonal distance

```
  ●───────┐
  │╲      │
  │  ╲    │  10 m down
  │    ╲  │
  └──────●
    10 m across
```

10² + 10² = 200 → √200 = **14.1 m**. `math.hypot` is Python's built-in Pythagoras tool.

### Worked example: a straight move on perfect ground

Perfect ground = slope 0, hazard 0, roughness 0, no climbing. Using the safe weights (3, 4, 1, 0.5):

| Piece          | Calculation          | Value     |
| -------------- | -------------------- | --------- |
| Distance       | straight move        | **10**    |
| Slope part     | 3 × (0/25)² = 3 × 0  | 0         |
| Hazard part    | 4 × 0                | 0         |
| Roughness part | 1 × 0                | 0         |
| **Penalty**    | 1 + 0 + 0 + 0        | **1**     |
| Climb part     | 0.5 × 0              | 0         |
| **Cost**       | 10 × 1 + 0           | **10** ✅ |

So on perfect ground, cost = distance.

### Justifying the design

| Decision                                    | Why it makes sense                                                                                                     |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **1. Start from distance**                  | Every metre uses battery and time, so even perfect ground has a cost.                                                  |
| **2. Multiply by a penalty (not just add)** | Bad ground is worse the **longer** you drive on it: 50 m of rocks is worse than 10 m, so extras scale with distance.   |
| **3. Square the slope**                     | Gentle slopes barely matter, but steep ones get dangerous **quickly**. Squaring makes 20° four times worse than 10°, not twice. |
| **4. Hazard gets the biggest weight (4)**   | Rocks and sand can **end the mission**. In 2009 the Spirit rover got stuck in soft sand and never moved again.         |
| **5. Only uphill costs extra**              | Climbing uses energy; going downhill doesn't. Downhill steepness is already covered by the slope penalty.              |
| **6. Hard limits block squares completely** | Some ground is never worth the risk (slope > 25°, hazard ≥ 0.9), so those squares are simply off-limits.               |

Hazard vs roughness, since they sound similar:

| Weight        | What it protects against                         |
| ------------- | ------------------------------------------------ |
| **Hazard**    | rocks breaking wheels, sand trapping the rover   |
| **Roughness** | bumps and shaking                                |

## 2.3 Weights: the rover's personality

![[weights_comparison.png|544]]

| Line             | Weights (slope, hazard, rough, climb) | Personality                                  |
| ---------------- | ------------------------------------- | -------------------------------------------- |
| ⚪ White dashed  | 0, 0, 0, 0                            | "I only care about distance"                 |
| 🔴 Red           | 3, 4, 1, 0.5                          | "Balanced and careful" (the **safe** route)  |
| 🔵 Blue          | 0, **20**, 0, 0                       | "I'm terrified of rocks and sand"            |
| 🟢 Green         | **20**, 0, 0, 0                       | "I'm terrified of slopes"                    |

| Route           | Distance             | Steepest slope        | Avg hazard         | What it did                                                                                  |
| --------------- | -------------------- | --------------------- | ------------------ | -------------------------------------------------------------------------------------------- |
| ⚪ Shortest      | **616 m** (shortest) | 19°                   | 0.10               | cut straight through, brushing the big hazard patch. **Shortest, but riskier.**              |
| 🔴 Safe          | 665 m                | 14.9°                 | 0.02               | went a bit around, avoiding both. **Good at everything, best at nothing.**                   |
| 🔵 Hates hazards | 677 m                | **21.5°** (steepest)  | **0.005** (safest) | swung far left to dodge every red patch, but climbed steeper ground. **Safest from rocks, but steeper.** |
| 🟢 Hates slopes  | **696 m** (longest)  | **12.2°** (flattest)  | 0.10               | hugged flat ground, squeezing right past the hazard patch. **Flattest, but near rocks and longest.** |

This is a **trade-off**, which is exactly what the challenge means by "decide how factors like slope, distance, hazards and energy affect routing." There's no single correct route: **the weights decide what "best" means.**

## 2.4 Heuristic

```python
def heuristic(a, b):
    """Straight-line distance in metres..."""
    return CELL_SIZE_M * math.hypot(a[0] - b[0], a[1] - b[1])
```

| Code                   | Meaning                                       |
| ---------------------- | --------------------------------------------- |
| `def heuristic(a, b):` | a function that takes 2 squares, `a` and `b`  |
| `a[0] - b[0]`          | how many **rows** apart they are              |
| `a[1] - b[1]`          | how many **columns** apart they are           |
| `math.hypot(...)`      | Pythagoras: straight-line distance in squares |
| `CELL_SIZE_M *`        | × 10, so it's in **metres**                   |
| `return`               | hands back the guess                          |

## 2.5 A\* search

### The big picture

```
        ┌─────────────────────────────┐
        │    Start or goal blocked?   │── yes ──► return None
        └──────────────┬──────────────┘
                       │ no
        ┌──────────────▼──────────────┐
        │    Set up: to-do = [start]  │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
   ┌────│ Take best square from to-do │◄────────────┐
   │    └──────────────┬──────────────┘             │
   │                   │                            │
   │    ┌──────────────▼──────────────┐             │
   │    │ Is it the goal?             │── yes ──► build route, return it 🎉
   │    └──────────────┬──────────────┘             │
   │                   │ no                         │
   │    ┌──────────────▼──────────────┐             │
   │    │ Check 8 neighbours:         │             │
   │    │ cheaper? → note it, add to  │─────────────┘
   │    │ to-do list                  │
   │    └─────────────────────────────┘
   │
   └──► (to-do list empty?) ──► return None (no route)
```

| Idea              | Question it answers                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| To-do list        | "Which square should I check **next**?" Always the one that **looks best** (cost so far + guess to goal). |
| Parent list       | "Which square did I come **from**?" For every square reached, A\* writes down its parent.                |
| Working backwards | "What's the full **route**?" Once the goal is reached, A\* follows the parents back to the start.        |

### Setup

```python
def astar(t, start, goal, w):
    rows, cols = t["elevation"].shape
    ok = t["traversable"]
    if not ok[start] or not ok[goal]:
        return None

    open_list = [(heuristic(start, goal), start)]
    g = {start: 0.0}
    came_from = {}
```

| Code                                            | What it does                                                                                     |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `def astar(t, start, goal, w):`                 | the A\* function: `t` = terrain, start square, goal square, `w` = weights                        |
| `rows, cols = t["elevation"].shape`             | `.shape` gives the grid size `(50, 50)`; used later to stop moves going **off the edge**         |
| `ok = t["traversable"]`                         | gives the True/False drivable map a short name                                                   |
| `if not ok[start] or not ok[goal]:`             | is the start **or** goal blocked?                                                                |
| `return None`                                   | if so, give up straight away (`None` = no route)                                                 |
| `open_list = [(heuristic(start, goal), start)]` | to-do list holding the start; f = g + h = 0 + guess                                              |
| `g = {start: 0.0}`                              | notebook of cost so far: reaching the start costs 0                                              |
| `came_from = {}`                                | parent list, empty because nothing has been explored yet                                         |

### Main loop

| Code                                | What it does                                              |
| ----------------------------------- | --------------------------------------------------------- |
| `while open_list:`                  | keep looping while the to-do list has squares in it       |
| `_, cur = heapq.heappop(open_list)` | take out the square with the **smallest f**; `cur` = current square |

### Reached the goal: rebuild the route

```python
if cur == goal:
    path = [cur]
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    return path[::-1]
```

| Line                      | Meaning                                                  |
| ------------------------- | -------------------------------------------------------- |
| `if cur == goal:`         | is this the goal? 🎉                                     |
| `path = [cur]`            | start a list with the goal in it                         |
| `while cur in came_from:` | keep going while the current square has a parent         |
| `cur = came_from[cur]`    | step back to where it came from                          |
| `path.append(cur)`        | add that square to the list                              |
| `return path[::-1]`       | reverse it (start → goal) and hand it back               |

### Neighbour check 1: on the map and not blocked

```python
if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or not ok[nxt]:
    continue
```

| Check                | Meaning                                 |
| -------------------- | --------------------------------------- |
| `0 <= nxt[0] < rows` | row is between 0 and 49 (on the map)    |
| `0 <= nxt[1] < cols` | column is between 0 and 49 (on the map) |
| `not ok[nxt]`        | the square is **blocked**               |

### Neighbour check 2: no corner-cutting on diagonals

```python
if dr and dc and not (ok[cur[0] + dr, cur[1]] and ok[cur[0], cur[1] + dc]):
    continue
```

| Part                      | Meaning                                         |
| ------------------------- | ----------------------------------------------- |
| `dr and dc`               | both non-zero, so it's a **diagonal** move      |
| `ok[cur[0] + dr, cur[1]]` | the square **straight up/down** from here       |
| `ok[cur[0], cur[1] + dc]` | the square **straight left/right** from here    |
| `not (... and ...)`       | if **either** side square is blocked…           |
| `continue`                | …skip this diagonal move                        |

```
 R  #        moving R (rover) to G (goal)
 #  G        both side squares are #, so the rover would squeeze through → blocked
```

## 2.6 Route metrics

```python
def route_metrics(t, path):
    dist = sum(CELL_SIZE_M * math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    cost = sum(step_cost(t, a, b, SAFE_WEIGHTS) for a, b in zip(path, path[1:]))
    elev = np.array([t["elevation"][p] for p in path])
    return {
        "distance_m": round(dist, 1),
        "route_cost": round(cost, 1),
        "elevation_gain_m": round(float(np.sum(np.clip(np.diff(elev), 0, None))), 1),
        "max_slope_deg": round(float(max(t["slope"][p] for p in path)), 1),
        "avg_hazard": round(float(np.mean([t["hazard"][p] for p in path])), 3),
    }
```

| Metric               | Question it answers                      | How it's worked out                                   |
| -------------------- | ---------------------------------------- | ----------------------------------------------------- |
| **distance_m**       | How far does the rover drive?            | add up every move (e.g. 10 m + 14.1 m + 10 m …)       |
| **route_cost**       | How "expensive" is the route overall?    | add up `step_cost` for every move                     |
| **elevation_gain_m** | How much does it climb in total?         | add up only the **uphill** bits; downhill is ignored  |
| **max_slope_deg**    | What's the steepest square on the route? | the biggest slope of any square on it                 |
| **avg_hazard**       | How risky is the route on average?       | average hazard of all squares on it                   |

Every route is scored with the **same** rules (`SAFE_WEIGHTS`), so routes can be compared fairly:

| Metric           | Shortest  | Safe (chosen) | What it shows            |
| ---------------- | --------- | ------------- | ------------------------ |
| distance_m       | **616.0** | 665.3         | safe is ~50 m longer     |
| route_cost       | 1364.0    | **1064.2**    | but safe is **cheaper**  |
| elevation_gain_m | 39.4      | 40.3          | about the same climbing  |
| max_slope_deg    | 19.0      | **14.9**      | safe avoids steep ground |
| avg_hazard       | 0.10      | **0.019**     | safe is ~5× less risky   |

---

# 3. main.py

## 3.1 Command-line settings

```python
parser = argparse.ArgumentParser()
parser.add_argument("--start", nargs=2, type=int, default=[5, 5])
parser.add_argument("--goal", nargs=2, type=int, default=[44, 44])
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--size", type=int, default=50)
args = parser.parse_args()

start, goal = tuple(args.start), tuple(args.goal)
t = make_terrain(args.size, args.seed)
```

| Bit              | Plain meaning                                  |
| ---------------- | ---------------------------------------------- |
| `"--start"`      | the name of the setting                        |
| `nargs=2`        | it needs **2 numbers** (row, col)              |
| `type=int`       | whole numbers only (5, not 5.7)                |
| `default=[5, 5]` | if nothing is given, use **5, 5**              |

`tuple()` turns `[5, 5]` (a list, square brackets) into `(5, 5)` (a tuple, round brackets), which is what the map uses for indexing. Same numbers, different box.

*See "Python basics" for more on argparse.*

## 3.2 Running A\* twice

```python
safe = astar(t, start, goal, SAFE_WEIGHTS)
shortest = astar(t, start, goal, SHORTEST_WEIGHTS)
```

Same map, same start and goal; only the rover's personality changes:

- **`safe`**: a careful rover that avoids slopes and hazards
- **`shortest`**: a rushing rover that only cares about distance

Each call returns a **list of squares**, which is the route.

## 3.3 Printing the comparison

```python
m_short, m_safe = route_metrics(t, shortest), route_metrics(t, safe)
for key in m_safe:
    print(f"{key:18}{m_short[key]:>12}{m_safe[key]:>14}")
```

| Line                 | Meaning                                                   |
| -------------------- | --------------------------------------------------------- |
| `route_metrics(...)` | makes a report card for **each** route                    |
| `for key in m_safe:` | goes through each score name (distance_m, route_cost …)   |
| `print(...)`         | prints one row: name, shortest's score, safe's score      |

`:18`, `:>12` and `:>14` set **column widths** so the output lines up like a table:

```
                      SHORTEST   SAFE (best)
distance_m               616.0         665.3
route_cost              1364.0        1064.2
```

## 3.4 Plotting the routes

```python
for path, colour, label in [(shortest, "white", "Shortest"), (safe, "red", "Safe (chosen)")]:
    rows, cols = zip(*path)
    ax.plot(cols, rows, color=colour, lw=2.2, label=label,
            ls="--" if label == "Shortest" else "-")
```

The loop runs twice:

| Time | Route    | Colour   | Line style  |
| ---- | -------- | -------- | ----------- |
| 1st  | shortest | ⚪ white | `--` dashed |
| 2nd  | safe     | 🔴 red   | `-` solid   |

`zip(*path)` splits the route into separate row and column lists:

```
path = [(5,5), (6,6), (7,7)]
        ↓
rows = (5, 6, 7)
cols = (5, 6, 7)
```

`ax.plot` takes `cols` first because x (across) is the column and y (down) is the row.

---

# 4. Limitations

**Map scale and realism**

- Hill height (15–45 m) and width (4–8 cells) are fixed ranges, so this is a **test map**, not real Mars data.
- The map is only **500 m × 500 m**, tiny compared with Mars.
- Position uses the **grid system**, not real latitude and longitude.
- One cell is **10 m**, so small rocks and boulders aren't detected, even though they matter for the rover's path.

**Terrain shape**

- Hills are basically smooth; real Martian hills have pits and craters that affect whether the rover can pass.
- The crater is a single uniform shape with no small bumps of its own, and its position is fixed at the centre.

**Planner feedback**

- The program only knows a square is blocked, not **why** (too steep or too hazardous).
- When no route exists, it doesn't explain why (too steep, hazardous, or walled off).
