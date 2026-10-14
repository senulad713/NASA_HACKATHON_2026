
# Terrain.py

⦿ Seed Number 42 allows me to get the exact same hills every time I run the code
     If there was no seed i would have gotten a different outcome each time
⦿ Size 50 creates a 50 x 50 grid
```python
def make_terrain(size=50, seed=42)
```
## Coordinates (Mesh grids)
---

```python
import numpy as np
y, x = np.mgrid[0:4, 0:4]
print(y)
print(x)
```

⦿ In short, it lets the code draw shapes on the map, like hills, the crater and hazard patches
⦿ It works like a spreadsheet. `y` is the row number down the left side and `x` is the column letter       across the top, written into every cell so NumPy can use them in calculations
⦿ NumPy treats a grid like a table or spreadsheet, and tables are always read row first, then                column. That's why `mgrid` gives back `y` first

```python
y, x = np.mgrid[0:3, 0:3]
```
Output ->     y              x
          0 0 0        0 1 2
          1 1 1        0 1 2
          2 2 2        0 1 2
⦿ For example : Top left coordinate would be [y=0 , x=0] , Bottom left corner [y = 2, x=0]

## Looping to locate Hill

![[Pasted image 20260930221753.png|507]]

| *Setting* | *What it controls*               | *Real-world meaning*         |
| --------- | -------------------------------- | ---------------------------- |
| `cx, cy`  | **Where** the hill is            | where you pour the sand      |
| `height`  | **How tall** (15–45 m)           | how much sand you pour       |
| `width`   | **How spread out** (4–8 squares) | a narrow pile or a wide pile |

```python
for _ in range(6):                          
        cx, cy = rng.uniform(0, size, 2)        
        height = rng.uniform(15, 45)          
        width = rng.uniform(4, 8)               
        elevation += height * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * width ** 2))
```

⦿ The rule is simple: **the closer a square is to the center, the taller it gets.**
⦿ That long line of code does exactly this. For every square, it:

1. works out **how far** the square is from the center, and
2. turns that distance into a **height**: close means tall, far means low.

| *Line*                       | *Picks*                | *Unit*                    | *Controls*                         |
| ---------------------------- | ---------------------- | ------------------------- | ---------------------------------- |
| height = rng.uniform(15, 45) | a number from 15 to 45 | metres                    | **how tall** the hill is           |
| width = rng.uniform(4, 8)    | a number from 4 to 8   | squares (1 square = 10 m) | **how spread out** it is (40–80 m) |
⦿ Because these lines are inside `pythonfor _ in range(6):`, they run **6 times**, and each hill gets      **new random values**. For example:
##### Q) What is the difference between a hill with [width = 4] and [width = 8]?

⦿ Both hills are the **same height**, and one spreads that height over a much longer distance.
⦿ Picture two hills, both 30 m tall:

- One goes from flat to its peak in **4 squares**
- The other goes from flat to its peak in **8 squares**
  
⦿ The hill with [width = 8] will have a less steeper hill for the rover to easily climb over

##### Q) Quick check : if `width` came out as **4** and `height` as **45**, would that hill be gentle           or steep?

A) It's steep: it has the tallest possible height (45 m) packed into the narrowest possible width (4          squares). It would be difficult for the rover to drive over it

Limitations so far : 
‣ I have only set a fixed max height and min width so this is just a test map
    Hill height (15 - 45m) 
    Hill width (4 - 8cells)
‣ My hills are basically smooth but real Martian hills have pits and crators which would play a huge    role of whether the rover can travel through it etc.
‣ One cell is only 10m so small rocks and boulders wont be detected which would also be                  important to calculate the path the rove should take
‣ I have also only used a 500m x 500m map which is tiny compared to Mars
‣ My way of long and lat is the grid system

## Crater section
---
```python
cx, cy = size * 0.5, size * 0.5
```

⦿ This is where the crater goes, this crater is not **randomized**. 
⦿ `size` is 50, so 50 × 0.5 = 25. The crater center is at **(25, 25)**, the middle of the map

```python
r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
```

⦿ Just checks how far every square is from the middle of the crater
⦿ Pythagoras theorem

| ***Step             *** | ***Code             *** | ***What it does                                        *** | ***Answer   *** |
| ----------------------- | ----------------------- | ---------------------------------------------------------- | --------------- |
| 1                       | `x - cx`                | How many steps **across**? 28 − 25                         | 3               |
| 2                       | `y - cy`                | How many steps **down**? 29 − 25                           | 4               |
| 3                       | `** 2`                  | Square them: 3×3 and 4×4                                   | 9 and 16        |
| 4                       | `+`                     | Add them: 9 + 16                                           | 25              |
| 5                       | `np.sqrt`               | Square root of 25                                          | 5               |

```python
 elevation += -35 * np.exp(-(r ** 2) / (2 * 4 ** 2)) + 12 * np.exp(-((r - 7) ** 2) / (2 * 1.5 ** 2))
```

⦿ This is exactly like a hill, but with a **minus** height : **−35 m**. A negative hill is a **hole**
        ‣ It's deepest at the center (35 m down).
        ‣ It gets shallower moving outward, like the hills getting lower
        ‣ +**12** means "build up 12." **Plus = wall**

```
   wall        wall
    ▲   hole    ▲
 ───┘╲         ╱└───
      ╲_______╱
```

⦿I havent accounted for the small bumps(Just an uniform crator)

⦿ We have now added hills and a crator but the ground is still too smooth now so we are gonna         add small bumps randomly onto the terrain.

## Small Random Bumps
---
```python
elevation += rng.normal(0, 0.5, (size, size))
```

| **Part              ** | **Meaning                                 **                                      |
| ---------------------- | --------------------------------------------------------------------------------- |
| `0`                    | The numbers are **centred on 0**, so on average they don't raise or lower the map |
| `0.5`                  | They're **small**, usually between **−1 m and +1 m**                              |
| `(size, size)`         | Make a whole 50×50 grid of them, one per square                                   |

## Slope
---
```python
dz_dy, dz_dx = np.gradient(elevation, CELL_SIZE_M) 
slope = np.degrees(np.arctan(np.sqrt(dz_dx ** 2 + dz_dy ** 2)))
```

⦿ Imagine walking on the map:
    ‣ **Flat ground:** you walk and your height doesn't change. **Slope = 0°**
    ‣ **A gentle ramp:** you go up a little with each step. **Small slope**
    ‣ **A steep hill:** you go up a lot with each step. **Big slope**

| *Result* | *Question it answers*                                         |
| -------- | ------------------------------------------------------------- |
| `dz_dx`  | How much does height change moving **across** (left ↔ right)? |
| `dz_dy`  | How much does height change moving **down** (up ↔ down)?      |
Example `dz_dx` = 0.3 and `dz_dy` = 0.4

| Step        | Calculation               | Result  |
| ----------- | ------------------------- | ------- |
| Square both | 0.3² + 0.4² = 0.09 + 0.16 | 0.25    |
| Square root | √0.25                     | **0.5** |
⦿ So the total steepness is **0.5**: you go up 0.5 m for every 1 m walked.
$$
0.5 (steepness) → np.arctan → 0.46  radians → np.degrees → 26.6°
$$
⦿ If the angle in degrees is more than 25 degrees that square is blocked as the rover cannot drive       over it.

## Roughness
---
```python
padded = np.pad(elevation, 1, mode="edge")
    neighbours_mean = sum(
    padded[1 + dr: 1 + dr + size, 1 + dc: 1 + dc + size]
    for dr in (-1, 0, 1) for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)   ) / 8
    roughness = np.abs(elevation - neighbours_mean)
    roughness = roughness / roughness.max()
```

⦿ The basic idea : Is this square different from the ones around it 
	‣ If it's about the **same height** as its neighbours, it's **smooth**
	‣ If it **sticks up or dips down** compared with them, it's **rough** (a rock, a pit, a bump)

##### Step 1: Add a border
```python
padded = np.pad(elevation, 1, mode="edge")
```

⦿ The problem: 
   First if we look at a square in the middle of the map
```
 ■  ■  ■
 ■  ●  ■      8 neighbours ✅
 ■  ■  ■
```

   Now look at the **top-left corner** square. There's **nothing above it** and **nothing to its left**, because that's the edge of the map
```
 ✖  ✖  ✖
 ✖  ●  ■      only 3 neighbours ❌
 ✖  ■  ■      (✖ = off the map, nothing there)
```

⦿ `np.pad` adds an **extra ring of squares** around the whole map, like a **picture frame**
⦿ To fill the frame, it **copies the height of the nearest edge square** - thats what `mode="edge"` runs

```
Before:            After np.pad (frame added):

                   1  1  2  3  3
  1  2  3          1  1  2  3  3
  4  5  6    →     4  4  5  6  6
  7  8  9          7  7  8  9  9
                   7  7  8  9  9
```
##### Why copy the edge?
⦿ Copying the edge value pretends the ground **carries on the same** just past the edge. That's a          reasonable guess
##### Step 2: find the average of the neighbours
```
 ↖  ↑  ↗
 ←  ●  →      ● = the square we're checking
 ↙  ↓  ↘
```
⦿ Every square has **8 neighbours** around it. Together with itself, that's a little **3×3 block**

⦿  For every square, this:
1. Looks at the **8 neighbours** (up, down, left, right and the 4 diagonals).
2. **Skips the centre square**. That's your `if (dr, dc) != (0, 0)` line.
3. **Adds up** the 8 heights and **divides by 8** to get the average.
```python
(-1,-1)  (-1,0)  (-1,+1)
( 0,-1)  ( 0,0)  ( 0,+1)      (0,0) = centre → skipped
(+1,-1)  (+1,0)  (+1,+1)
```
##### Step 3 : how different is the square?
```python
roughness = np.abs(elevation - neighbours_mean)
```
⦿ **Square's height minus the neighbours' average.** `np.abs` removes the minus sign, so a bump         **up** and a dip **down** both count as rough

```python
roughness = roughness / roughness.max()
```

Example : 

|        | Center | 8 neighbours | Neighbours' average | Difference | Result |
| ------ | ------ | ------------ | ------------------- | ---------- | ------ |
| Smooth | 10 m   | all 10 m     | 10 m                | 0          | smooth |
| Bump   | 14 m   | all 10 m     | 10 m                | 4          | rough  |
| Dip    | 7 m    | all 10 m     | 10 m                | 3          |  rough |

#### In one sentence
Roughness = how different a square's height is from the average of its 8 neighbours, scaled from 0                       (smooth) to 1 (roughest)

## Hazards
---

```python
hazard = np.zeros((size, size))
for _ in range(5):
    hx, hy = rng.uniform(0, size, 2)
    hw = rng.uniform(2, 5)
    hazard += np.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * hw ** 2))
hazard = np.clip(hazard, 0, 1)
```

Some ground is **dangerous even if it's flat**:
- **rock fields:** sharp rocks can damage the wheels
- **loose sand:** the rover can **sink and get stuck**. 

⦿ The code is similar to the hill loop

|               | *Hills*                 | *Hazards*                             |
| ------------- | --------------------- | ----------------------------------- |
| Start with    | `np.zeros` (flat map) | `np.zeros` (no danger anywhere)     |
| How many      | `range(6)` = 6 hills  | `range(5)` = **5 danger patches**   |
| Random centre | `cx, cy`              | `hx, hy`                            |
| Random width  | `width` = 4–8         | `hw` = **2–5** (smaller patches)    |
| Shape         | Gaussian bump         | Gaussian bump, the **same formula** |
| What it adds  | **height** in metres  | danger level                        |

⦿ The only acc difference is that the height is not changed its tht the hazards go on a different           map so that the rover can track it seperatly

| *Hazard value* | *Meaning*                                      |
| ------------ | -------------------------------------------- |
| **0**        | safe ground 🟢                               |
| **0.5**      | some risk, the edge of a rock field 🟡       |
| **1**        | very dangerous, the centre of a sand trap 🔴 |
###### Why `np.clip`?
```python
hazard = np.clip(hazard, 0, 1)
```

What happens if **two patches overlap**? Their values **add up**:
    ‣  0.8 + 0.6 = **1.4**

⦿  1.4 is off the scale. `np.clip` **cuts anything over 1 down to 1** (and anything below 0 up to 0)

| ***Before                  *** | ***After `np.clip`                                   *** |
| ------------------------------ | -------------------------------------------------------- |
| 1.4                            | **1.0**                                                  |
| 0.7                            | 0.7 (unchanged)                                          |
| 0.0                            | 0.0 (unchanged)                                          |
##### How the rover uses it
   ‣ Hazard **≥ 0.9**: **blocked**, too dangerous to enter 
   ‣ Hazard **below 0.9**: allowed, but **costs more** the higher it is

### Final condition :
---
⦿  For every square, this line asks: **"Can the rover drive here at all?"**

| Rule                 | Code                     | Meaning                  |
| -------------------- | ------------------------ | ------------------------ |
| 1. Not too steep     | `slope <= MAX_SLOPE_DEG` | slope is **25° or less** |
| 2. Not too dangerous | `hazard < 0.9`           | hazard is **below 0.9**  |
⦿  `&` means **AND**. A square is traversable only if **both** rules are true

| *Slope       * | *Hazard     * | *Rule 1 (≤ 25°)    * | *Rule 2 (< 0.9)  * | *Traversable?                    * |
| -------------- | ------------- | -------------------- | ------------------ | ---------------------------------- |
| 10°            | 0.2           | ✅                    | ✅                  | **True**, can drive                |
| 30°            | 0.2           | ❌                    | ✅                  | **False**, too steep               |
| 10°            | 0.95          | ✅                    | ❌                  | **False**, too dangerous           |
| 30°            | 0.95          | ❌                    | ❌                  | **False**, both                    |

#                                            Planner.py
---

| *Line*                                           | *What it brings in*                                                            | *Used for in `planner.py`*                                           |
| ------------------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `import heapq`                                   | A **priority queue**: a list that always hands you the **smallest** item first | **A***: always checking the cheapest square next                     |
| `import math`                                    | Basic **maths** tools                                                          | `math.hypot` (move length: 10 m or 14.1 m) and `math.inf` (infinity) |
| `import numpy as np`                             | **NumPy**, nicknamed `np`                                                      | `np.mean`, `np.diff` etc. for the route metrics                      |
| `from terrain import CELL_SIZE_M, MAX_SLOPE_DEG` | Two **settings** from your own `terrain.py`                                    | Cell size (10 m) and slope limit (25°)                               |

## What is the cost model? (Every Move has a price)
----

| ***Ground                                          *** | ***Price                                                 *** |
| ---------------------------------------------------- | ---------------------------------------------------------- |
| Flat, safe, smooth                                   | **cheap** 🟢                                               |
| Steep, bumpy, rocky                                  | **expensive** 🔴                                           |
| Blocked                                              | **can't go at all** 🚫                                     |
⦿ A* then finds the route where the **total bill is smallest**. That's how the rover avoids hard ground     even when it's shorter

##### What makes up the price?

| *#* | *Thing*       | *Why it costs more                                    * | *Example*                      |
| --- | ------------- | ------------------------------------------------------- | ------------------------------ |
| 1   | **Distance**  | longer = more battery and time                          | 10 m straight, 14.1 m diagonal |
| 2   | **Slope**     | steep = slipping, tipping, more energy                  | 20° costs much more than 5°    |
| 3   | **Hazard**    | rocks or sand = damage or getting stuck                 | hazard 0.8 costs a lot         |
| 4   | **Roughness** | bumpy = slower, more wear                               | roughness 1 costs a bit more   |
| 5   | **Climbing**  | going uphill uses extra energy                          | climbing 5 m costs extra       |
⦿ **Perfect ground** means slope = 0, hazard = 0, roughness = 0, and no climbing (flat)
##### *Straight move*

| ***Piece                        *** | ***Calculation                                   *** | ***Value                          *** |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| Distance                            | straight move                                        | **10**                                |
| Slope part                          | 3 × (0/25)² = 3 × 0                                  | 0                                     |
| Hazard part                         | 4 × 0                                                | 0                                     |
| Roughness part                      | 1 × 0                                                | 0                                     |
| **Penalty**                         | 1 + 0 + 0 + 0                                        | **1**                                 |
| Climb part                          | 0.5 × 0                                              | 0                                     |
| **Cost**                            | 10 × 1 + 0                                           | **10** ✅                              |
###### The math part of this
$$\text{cost}(a \to b) = d \times \left(1 + w_s \left(\frac{S_b}{25}\right)^2 + w_h H_b + w_r R_b\right) + w_c \times \max(0,\; E_b - E_a)$$

| *Symbol                   * | *Meaning                                                 * | *Unit / range                             * |
| --------------------------- | ---------------------------------------------------------- | ------------------------------------------- |
| a → b                       | moving **from** square a **to** square b                   |                                             |
| **d**                       | distance of the move                                       | 10 m straight, 14.1 m diagonal              |
| **S_b**                     | slope of square b                                          | degrees (0–25)                              |
| **25**                      | max allowed slope (`MAX_SLOPE_DEG`)                        | degrees                                     |
| **H_b**                     | hazard of square b                                         | 0–1                                         |
| **R_b**                     | roughness of square b                                      | 0–1                                         |
| **E_a, E_b**                | elevation (height) of squares a and b                      | metres                                      |
| **max(0, E_b − E_a)**       | metres climbed (downhill = 0)                              | metres                                      |
```
  ●───────┐
  │╲      │
  │  ╲    │  10 m down
  │    ╲  │
  └──────●
    10 m across
```

   10² + 10² = 100 + 100 
   √200 = 14.1 diagonal distance
⦿ `math.hypot` is just Python's built-in Pythagoras tool.

In simple words : 
```
cost = distance × (1 + slope extra + hazard extra + roughness extra) + climb extra
```

### Weights : the rovers personality 

![[weights_comparison.png|544]]

| *Line                            * | *Weights (slope, hazard, rough, climb)* | *Personality*                                |
| ---------------------------------- | --------------------------------------- | -------------------------------------------- |
| ⚪ White dashed                     | 0, 0, 0, 0                              | **"I only care about distance"**             |
| 🔴 Red                             | 3, 4, 1, 0.5                            | **"Balanced and careful"** (your safe route) |
| 🔵 blue                            | 0, **20**, 0, 0                         | **"I'm terrified of rocks and sand"**        |
| 🟢 Green                           | **20**, 0, 0, 0                         | **"I'm terrified of slopes"**                |

| *Route                        * | *Distance*           | *Steepest slope*      | *Avg hazard*       | *What it did*                                                                                                               |
| ------------------------------- | -------------------- | --------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| ⚪ Shortest                      | **616 m** (shortest) | 19°                   | 0.10               | cut straight through, **brushing the big hazard patch**<br>**shortest**, but **riskier**                                    |
| 🔴 Safe                         | 665 m                | 14.9°                 | 0.02               | went a bit around, **avoiding both**<br>**good at everything, best at nothing**                                             |
| 🔵 Hates hazards                | 677 m                | **21.5°** (steepest!) | **0.005** (safest) | swung **far left** to dodge every red patch, but climbed steeper ground<br>**safest from rocks**, but **steeper**           |
| 🟢 Hates slopes                 | **696 m** (longest)  | **12.2°** (flattest)  | 0.10               | hugged flat ground, **squeezing right past the hazard patch**<br>**flattest**, but **drives near rocks** and is **longest** |
⦿ That's called a **trade-off**, and it's exactly what the trial means by "decide how factors like slope, distance, hazards and energy affect routing." There's no single "correct" route. The weights decide what "best" means.

#### Justifying

| Decision                                    | Why it makes sense                                                                                                                                            |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Start from distance**                  | Every metre driven uses battery and time, so even perfect ground has a cost.                                                                                  |
| **2. Multiply by a penalty (not just add)** | Bad ground is worse the **longer** you drive on it. 50 m of rocky ground is worse than 10 m, so the extras scale with distance.                               |
| **3. Square the slope**                     | Gentle slopes barely matter, but steep ones get dangerous **quickly** (slipping, tipping over). Squaring makes 20° four times worse than 10°, not just twice. |
| **4. Hazard gets the biggest weight (4)**   | Rocks and sand can **end the mission**.                                                                                                                       |
| **5. Only uphill costs extra**              | Climbing uses energy; going downhill doesn't. Downhill steepness is already covered by the slope penalty.                                                     |
| **6. Hard limits block squares completely** | Some ground is never worth the risk (slope > 25°, hazard ≥ 0.9). No cost is high enough, so those squares are simply off-limits.                              |
⦿ I made hazard the biggest weight as in 2009 spirit rover got stuck in sand and rock and never moved again.

###### IMPORTANT : 

|Weight|What it protects against|
|---|---|
|**Hazard**|rocks breaking wheels, sand trapping the rover|
|**Roughness**|**bumps and shaking**|
## A* model
---
#### Heuristic model

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
| `CELL_SIZE_M *`        | × 10, so it’s in **metres**                   |
| `return`               | hands back the guess                          |
### A* part 

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

| Code                                            | What it does                                                                                                                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `def astar(t, start, goal, w):`                 | creates the A* function with 4 inputs(t - terrain, start square, goal square, w - weights)<br>                                                                                       |
| `rows, cols = t["elevation"].shape`             | - `.shape` gives the **size** of the grid: `(50, 50)`<br>- breaks it into: `rows = 50`, `cols = 50`<br>- It’s used later to check moves don’t go **off the         edge** of the map |
| `ok = t["traversable"]`                         | - gives the True/False drivable map a short name<br>                                                                                                                                 |
| `if not ok[start] or not ok[goal]:`             | - checks whether the start **or** goal is blocked<br>- `ok[start]` asks: is the start square drivable?<br>- `not ok[start]` means the start is **blocked**                           |
| `return None`                                   | - If the **start OR the goal** is blocked gives up               straight away, no route<br>- `return None` means “**no route**” (`None`= nothing)                                   |
| `open_list = [(heuristic(start, goal), start)]` | - to-do list with the start (f = guess, since g = 0)<br>- f = guess (0) + h                                                                                                          |
| `g = {start: 0.0}`                              | - notebook: cost to reach the start is 0                                                                                                                                             |
| `came_from = {}`                                | - empty for now as nothing has been explored yet                                                                                                                                     |
| `while open_list:`                              | - loop while the to-do list has squares in it                                                                                                                                        |
| `_, cur = heapq.heappop(open_list)`             | -`cur` = the **current** square being explored<br>- takes out the square with the **smallest f**                                                                                     |

---
``` python
if cur == goal:
    path = [cur]
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    return path[::-1]
```

| Line                      | Meaning                                                                         |
| ------------------------- | ------------------------------------------------------------------------------- |
| `if cur == goal:`         | is this the goal? 🎉                                                            |
| `path = [cur]`            | start a list with the goal in it                                                |
| `while cur in came_from:` | Keep going while the current square has a parent (a square it was reached from) |
| `cur = came_from[cur]`    | step back to where it came from                                                 |
| `path.append(cur)`        | and add that to the list                                                        |
| `return path[::-1]`       | reverse it (start → goal) and hand it back                                      |

---
```python
if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or not ok[nxt]:
    continue
```

Two checks:

| Check                | Meaning                                 |
| -------------------- | --------------------------------------- |
| `0 <= nxt[0] < rows` | row is between 0 and 49 (on the map)    |
| `0 <= nxt[1] < cols` | column is between 0 and 49 (on the map) |
| `not ok[nxt]`        | the square is **blocked**               |

---
```python
if dr and dc and not (ok[cur[0] + dr, cur[1]] and ok[cur[0], cur[1] + dc]):
    continue
```

| Part                      | Meaning                                        |
| ------------------------- | ---------------------------------------------- |
| `dr and dc`               | both are non-zero, so it’s a **diagonal** move |
| `ok[cur[0] + dr, cur[1]]` | the square **straight up/down** from here      |
| `ok[cur[0], cur[1] + dc]` | the square **straight left/right** from here   |
| `not (... and ...)`       | if **either** side square is blocked…          |
| `continue`                | …skip this diagonal move                       |
```
 R  #        moving R (rover) to G (goal)
 #   G        both side squares are #, so the rover would squeeze through → blocked
```

##### The basic algorithm

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

| Idea              | Question it answers                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| To-do list        | “Which square should I check **next**?”<br>it always hands back the square that **looks best** first (lowest cost so far + guess to goal) |
| Parent list       | “Which square did I come **from**?”<br>for every square A* reaches, it writes down **which square it came from** (its “parent”)           |
| Working backwards | “What’s the full **route**, start to goal?”<br>once the goal is reached, A* uses the parent list to **trace the route back** to the start |
## Route Metrics
---
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

| Metric               | Question it answers                      | How it’s worked out                                           |
| -------------------- | ---------------------------------------- | ------------------------------------------------------------- |
| **distance_m**       | How far does the rover drive?            | add up the length of every move (10m + 13m + 12m)             |
| **route_cost**       | How “expensive” is the route overall?    | add up `step_cost` for every move                             |
| **elevation_gain_m** | How much does it climb in total?         | add up only the **uphill** bits<br>downhill is not considered |
| **max_slope_deg**    | What’s the steepest square on the route? | the biggest slope of any square on it                         |
| **avg_hazard**       | How risky is the route on average?       | average hazard of all squares on it                           |
eg: 

| Metric           | Shortest  | Safe (chosen) | What it shows            |
| ---------------- | --------- | ------------- | ------------------------ |
| distance_m       | **616.0** | 665.3         | safe is 50m longer       |
| route_cost       | 1364.0    | **1064.2**    | but safe is **cheaper**  |
| elevation_gain_m | 39.4      | 40.3          | about the same climbing  |
| max_slope_deg    | 19.0      | **14.9**      | safe avoids steep ground |
| avg_hazard       | 0.10      | **0.019**     | safe is ~5× less risky   |
⦿ `route_metrics` measures a finished route (distance, cost, climbing, steepest slope and average hazard) using the same cost rules for every route, so they can be compared fairly

# Main.py
---

``` python
parser = argparse.ArgumentParser()
parser.add_argument("--start", nargs=2, type=int, default=[5, 5])
parser.add_argument("--goal", nargs=2, type=int, default=[44, 44])
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--size", type=int, default=50)
args = parser.parse_args()

start, goal = tuple(args.start), tuple(args.goal)
t = make_terrain(args.size, args.seed)
```

| **Bit                                          ** | **Plain meaning                                                 ** |
| ------------------------------------------------- | ------------------------------------------------------------------ |
| `"--start"`                                       | the name of the order                                              |
| `nargs=2`                                         | it needs **2 numbers** (row, col)                                  |
| `type=int`                                        | whole numbers only (5, not 5.7)                                    |
| `default=[5, 5]`                                  | if they don’t order it, give them **5, 5**                         |
```python
start, goal = tuple(args.start), tuple(args.goal)
```
⦿ The waiter wrote the start as `[5, 5]` with square brackets. The map wants `(5, 5)` with round      brackets, so `tuple()` swaps the brackets. Same numbers, different box.
	
*Check "python basics" to learn more about argparse*

```python
safe = astar(t, start, goal, SAFE_WEIGHTS)
shortest = astar(t, start, goal, SHORTEST_WEIGHTS)
```

⦿  This runs A* **twice** on the same map, with the same start and goal. The only difference is the rover’s personality:
     - **`safe`**: a careful rover that avoids slopes and hazards
     - **`shortest`**: a rushing rover that only cares about distance
⦿  Each one gives back a **list of squares**, which is the route.

Limitation :
>The program doesn’t know **why** the square is blocked (steep or hazard). It only knows the square is blocked.
>When no route exists, the program doesn’t explain why (too steep, hazard, or walled off)

```python
m_short, m_safe = route_metrics(t, shortest), route_metrics(t, safe)
for key in m_safe:
    print(f"{key:18}{m_short[key]:>12}{m_safe[key]:>14}")
```

| Line                 | Meaning                                               |
| -------------------- | ----------------------------------------------------- |
| `route_metrics(...)` | make a report card for **each** route                 |
| `for key in m_safe:` | go through each score name (distance_m, route_cost …) |
| `print(...)`         | print one row: name, shortest’s score, safe’s score   |
The `:18`, `:>12` and `:>14` just set **how wide** each column is, so it lines up neatly like a table:

```
                      SHORTEST   SAFE (best)
distance_m               616.0         665.3
route_cost              1364.0        1064.2
```

```python
for path, colour, label in [(shortest, "white", "Shortest"), (safe, "red", "Safe (chosen)")]:
    rows, cols = zip(*path)
    ax.plot(cols, rows, color=colour, lw=2.2, label=label,
            ls="--" if label == "Shortest" else "-")
```

**The loop** runs twice:

|Time|Route|Colour|Line style|
|---|---|---|---|
|1st|shortest|⚪ white|`--` dashed|
|2nd|safe|🔴 red|`-` solid|
**`zip(*path)`** splits the route into two lists:
```
path = [(5,5), (6,6), (7,7)]
        ↓
rows = (5, 6, 7)
cols = (5, 6, 7)
```
