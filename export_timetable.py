"""
export_timetable.py — MEC Timetable Export (v5)
Clean fix: use P1-P6 as column names, add timing as first data row.
"""

import numpy as np
import pandas as pd
import random
from timetable_env import TimetableEnv

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS   = ["P1", "P2", "P3", "P4", "P5", "P6"]

WEEKDAY_TIMES = ["9:30-10:30", "10:30-11:30", "11:30-12:30",
                 "1:30-2:30",  "2:30-3:30",   "3:30-4:30"]
FRIDAY_TIMES  = ["9:30-10:30", "10:30-11:30", "11:30-12:30",
                 "2:00-3:00",  "3:00-4:00",   "4:00-5:00"]

# ── Schedule ──────────────────────────────────────────────────────────────────
env      = TimetableEnv()
obs, _   = env.reset()
subjects = env.df_subjects
rooms    = env.df_rooms

print("Scheduling...\n")
for idx, row in subjects.iterrows():
    required = int(row["required_hours"])
    placed   = 0
    for _ in range(required):
        valid = env.get_valid_actions(idx)
        if valid:
            random.shuffle(valid)
            obs, reward, *_ = env.step(valid[0])
            if reward > 0:
                placed += 1
                print(f"  ✅ {row['course_code']:8} ({row['division']:5}) {placed}/{required}")
        else:
            print(f"  ⚠️  {row['course_code']:8} ({row['division']:5}) no slot for hour {placed+1}")

id_to_code = {i+1: r["course_code"] for i, r in subjects.iterrows()}
id_to_div  = {i+1: r["division"]    for i, r in subjects.iterrows()}

def get_cell(division, day, period):
    for r in range(env.num_rooms):
        cid = env.state[day, period, r]
        if cid != 0 and (id_to_div[cid] == division or id_to_div[cid] == "ALL"):
            return f"{id_to_code[cid]} [{rooms.iloc[r]['room_name']}]"
    return "---"

# ── Per-division export ────────────────────────────────────────────────────────
print("\nExporting CSVs...")
COLS = ["Day"] + PERIODS   # exactly 7 columns always

for div in ["CS6A", "CS6B", "CS6C"]:
    rows = []

    # Row 1: timing header (shows what time each period is)
    timing_row = {"Day": "TIMING (Mon-Thu)"}
    for p, t in enumerate(WEEKDAY_TIMES):
        timing_row[PERIODS[p]] = t
    rows.append(timing_row)

    timing_fri = {"Day": "TIMING (Friday)"}
    for p, t in enumerate(FRIDAY_TIMES):
        timing_fri[PERIODS[p]] = t
    rows.append(timing_fri)

    rows.append({c: "---" for c in COLS})  # blank separator row

    # Data rows
    for d, day_name in enumerate(DAY_NAMES):
        row_data = {"Day": day_name}
        for p in range(6):
            row_data[PERIODS[p]] = get_cell(div, d, p)
        rows.append(row_data)

    pd.DataFrame(rows, columns=COLS).to_csv(f"MEC_Timetable_{div}.csv", index=False)
    print(f"  📄 MEC_Timetable_{div}.csv  ({len(COLS)} columns)")

# ── Full raw timetable ─────────────────────────────────────────────────────────
raw_rows = []
for d in range(5):
    times = FRIDAY_TIMES if d == 4 else WEEKDAY_TIMES
    for p in range(6):
        entry = {"Day": DAY_NAMES[d], "Period": PERIODS[p], "Time": times[p]}
        for r in range(env.num_rooms):
            cid = env.state[d, p, r]
            entry[rooms.iloc[r]["room_name"]] = id_to_code[cid] if cid != 0 else "---"
        raw_rows.append(entry)

pd.DataFrame(raw_rows).to_csv("MEC_Full_Timetable_Raw.csv", index=False)
print("  📄 MEC_Full_Timetable_Raw.csv")

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*50}\nPLACEMENT SUMMARY\n{'='*50}")
all_ok = True
for idx, row in subjects.iterrows():
    placed   = int(np.sum(env.state == idx + 1))
    required = int(row["required_hours"])
    ok       = placed >= required
    all_ok   = all_ok and ok
    print(f"  {'✅' if ok else '⚠️ '} {row['course_code']:8} ({row['division']:5}) {placed}/{required}")

print(f"\n{'🎉 All placed!' if all_ok else '⚠️  Some missing — run again.'}")