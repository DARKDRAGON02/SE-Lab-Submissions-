# Fruit Catcher Repair Lab

This project is a 2D arcade catch-and-dodge game using **Pygame**. It introduces students to sprite collision checking, continuous horizontal movement, falling entity lifecycle management, life counters, and game state transitions within an object-oriented codebase.
---

## What's Provided

A working Fruit Catcher game with:

- A controllable basket at the bottom with clamped screen-edge boundaries
- Falling fruits (Apples, Oranges, Grapes) that spawn at randomized x-coordinates with independent falling speeds
- Keyboard controls supporting both `A` / `D` and `Left` / `Right` arrow keys
- Live score and lives HUD display
- A Game Over screen overlay with restart functionality

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Use A / D or Left / Right arrows to slide the basket. Press R to restart after Game Over.

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the floor miss scoring and life deduction bug

Allowing fruits to fall past the bottom of the screen currently increments the player's score instead of penalizing them. In game_engine.update(), the miss check executes self.score += 1 when fruit.is_missed(self.height) is true. Furthermore, self.lives is never decremented when a fruit is dropped, meaning the player cannot lose lives. Fix this block so that missing a fruit decreases self.lives by 1 (and triggers self.game_state = "GAME_OVER" when self.lives <= 0), ensuring points are only earned on successful basket catches.

### Task 2: Implement rotten fruit / hazard bombs

Introduce a hazard item into Fruit (e.g., a black or green spiked bomb/rotten fruit) that occasionally spawns instead of regular fruit. If caught in the basket, deduct a life or penalize points immediately, adding a dodge dynamic to the catching gameplay.
 
### Task 3: Implement dynamic falling speed escalation

Fruits currently drop at constant randomized speed bands throughout the entire session. In game_engine, add dynamic difficulty progression: as the player's score increases, gradually shorten self.spawn_delay and increase the baseline fall speed of newly spawned fruits.

### Task 4: Implement fruit splash particle effects

Catching or dropping a fruit currently removes it instantly from the list. Create a lightweight particle emitter system that bursts tiny colored circular droplets matching the fruit's color whenever a fruit hits the basket rim or splatters against the floor.
---

## Expected Behavior

- Sliding the basket catches falling fruits, removing them and awarding +1 point per catch.
- Missing a fruit and letting it touch the ground deducts 1 life without increasing the score.
- Losing all 3 lives displays the GAME OVER banner and freezes further updates.
- Pressing R after losing resets the score, restores lives to 3, and clears lingering fruits.

## Folder Structure

```
fruit_catcher/
├── game/
│   ├── basket.py
│   ├── fruit.py
│   └── game_engine.py
├── main.py
└── README.md
```

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

---

## Implementation Notes (Lab Completed)

### What changed

| Task | File | Change |
| --- | --- | --- |
| 1. Miss bug | `game/game_engine.py` | `_handle_miss()` now calls `_lose_life()` instead of `self.score += 1`; points are only awarded inside `_handle_catch()` |
| 2. Hazard bombs | `game/fruit.py`, `game/game_engine.py` | `Fruit` gained `is_hazard` / `points`; a spiked green bomb spawns randomly and is drawn with `_render_hazard()` |
| 3. Speed escalation | `game/game_engine.py` | `level`, `current_spawn_delay`, `speed_bonus` and `hazard_chance` properties scale with the score |
| 4. Splash particles | `game/particles.py` (new) | `Particle` + `ParticleSystem` emit colour-matched droplets on every catch and floor splat |

### Game rules after the fix

- Catch an edible fruit: **+1 point**, fruit removable, splash droplets burst at the basket rim.
- Let an edible fruit hit the floor: **-1 life**, score unchanged, orange droplets splatter upward.
- Catch a spiked bomb: **-1 life and -2 points** (score never drops below 0).
- Dodge a bomb (let it fall past): no penalty, which is the point of the dodge mechanic.
- Losing all 3 lives shows **GAME OVER** and freezes the simulation; **[R]** restarts.

### Difficulty curve (Task 3)

`level = score // 5`, and each level makes the run harder:

| Level | Spawn delay | Fall-speed bonus | Bomb chance |
| --- | --- | --- | --- |
| 1 (score 0-4) | 750 ms | +0.0 | 12% |
| 3 (score 10-14) | 610 ms | +1.0 | 18% |
| 7 (score 30-34) | 330 ms | +3.0 | 30% |
| 10+ (score 45+) | 260 ms (floor) | +4.5 (cap) | 35% (cap) |

Newly spawned fruit speed is `random.uniform(4.0, 6.5) + speed_bonus`, and two bombs are never
spawned back to back.

### Recording the "before" video

The original buggy code is still in git history. To film the broken behaviour:

```bash
git stash          # park the fixes (particles.py is untracked and simply goes unused)
python main.py     # record ~10s: the score climbs every time fruit lands on the floor
git stash pop      # restore the fixes before recording the "after" video
```

