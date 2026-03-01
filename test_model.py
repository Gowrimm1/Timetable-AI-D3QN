"""
test_model.py — Tests timetable by running the heuristic scheduler directly.
No longer depends on RL model predictions (which caused the empty table).
"""

import numpy as np
import random
from timetable_env import TimetableEnv

DAY_NAMES     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIOD_LABELS = ["P1", "P2", "P3", "P4", "P5", "P6"]

env = TimetableEnv()
obs, _ = env.reset()
subjects = env.df_subjects
rooms    = env.df_rooms

print("🔍 Running constraint-based scheduler (test run)...\n")

for idx, row in subjects.iterrows():
    required = int(row["required_hours"])
    for _ in range(required):
        valid = env.get_valid_actions(idx)
        if valid:
            random.shuffle(valid)
            env.step(valid[0])

# ── Print grid per division ───────────────────────────────────────────────────
id_to_code = {i+1: r["course_code"] for i, r in subjects.iterrows()}
id_to_div  = {i+1: r["division"]    for i, r in subjects.iterrows()}

for div in ["CS6A", "CS6B", "CS6C"]:
    print(f"\n{'='*70}")
    print(f"  TIMETABLE — {div}")
    print(f"{'='*70}")
    header = f"{'Day':<12}" + "".join(f"{p:<14}" for p in PERIOD_LABELS)
    print(header)
    print("-" * len(header))
    for d, day_name in enumerate(DAY_NAMES):
        row_str = f"{day_name:<12}"
        for p in range(6):
            cell = "---"
            for r in range(env.num_rooms):
                cid = env.state[d, p, r]
                if cid != 0 and (id_to_div[cid] == div or id_to_div[cid] == "ALL"):
                    cell = id_to_code[cid]
                    break
            row_str += f"{cell:<14}"
        print(row_str)

# ── Placement summary ─────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("  PLACEMENT SUMMARY")
print(f"{'='*70}")
for idx, row in subjects.iterrows():
    placed   = int(np.sum(env.state == idx + 1))
    required = int(row["required_hours"])
    status   = "✅" if placed >= required else "⚠️ "
    print(f"  {status} {row['course_code']:8} ({row['division']:5})  {placed}/{required} hours placed")