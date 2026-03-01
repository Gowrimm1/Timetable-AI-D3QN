"""
generator.py — MEC Constraint-Based Timetable Generator
Replaces the old random scheduler with the D3QN-environment heuristic.
"""

import random
import numpy as np
import pandas as pd

DAY_NAMES     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIOD_LABELS = ["P1", "P2", "P3", "P4", "P5", "P6"]
WEEKDAY_TIMES = ["9:30-10:30", "10:30-11:30", "11:30-12:30",
                 "1:30-2:30",  "2:30-3:30",   "3:30-4:30"]
FRIDAY_TIMES  = ["9:30-10:30", "10:30-11:30", "11:30-12:30",
                 "2:00-3:00",  "3:00-4:00",   "4:00-5:00"]

HONOURS_DAYS   = {1, 4}   # Tuesday, Friday (0-indexed)
HONOURS_PERIOD = 4         # Period 5 (0-indexed)
HONOURS_ROOM   = "Room_310"

DIVISION_ROOMS = {"CS6A": "B202", "CS6B": "B302", "CS6C": "B303"}


def generate_timetable(df_subjects, df_rooms, df_teachers):
    """
    Main entry point called by api.py.
    Returns dict of DataFrames: keys = "CS6A", "CS6B", "CS6C", "raw"
    """
    df_subjects.columns = df_subjects.columns.str.strip().str.lower()
    df_rooms.columns    = df_rooms.columns.str.strip().str.lower()
    df_teachers.columns = df_teachers.columns.str.strip().str.lower()

    num_days    = 5
    num_periods = 6
    room_names  = df_rooms["room_name"].tolist()
    num_rooms   = len(room_names)

    # state[d][p][r] = course_idx+1 or 0
    state   = np.zeros((num_days, num_periods, num_rooms), dtype=int)
    placed  = [0] * len(df_subjects)
    required = df_subjects["required_hours"].astype(int).tolist()

    id_to_code = {i+1: r["course_code"] for i, r in df_subjects.iterrows()}
    id_to_div  = {i+1: r["division"]    for i, r in df_subjects.iterrows()}
    room_idx   = {name: i for i, name in enumerate(room_names)}
    room_type  = {r["room_name"]: r["room_type"] for _, r in df_rooms.iterrows()}

    def is_teacher_busy(teacher_code, day, period):
        for r in range(num_rooms):
            cid = state[day, period, r]
            if cid != 0:
                if df_subjects.iloc[cid-1]["teacher_code"] == teacher_code:
                    return True
        return False

    def get_valid_slots(idx):
        row      = df_subjects.iloc[idx]
        division = row["division"]
        is_hon   = str(row["is_honours"]).lower() == "true"
        need_type= row["room_type_needed"]
        valid    = []

        for d in range(num_days):
            for p in range(num_periods):
                if is_hon:
                    if d not in HONOURS_DAYS or p != HONOURS_PERIOD:
                        continue
                else:
                    if d in HONOURS_DAYS and p == HONOURS_PERIOD:
                        continue

                if is_teacher_busy(row["teacher_code"], d, p):
                    continue

                for r, rname in enumerate(room_names):
                    if room_type[rname] != need_type:
                        continue
                    if is_hon and rname != HONOURS_ROOM:
                        continue
                    if not is_hon and need_type == "Theory" and division != "ALL":
                        if rname != DIVISION_ROOMS.get(division):
                            continue
                    if state[d, p, r] != 0:
                        continue
                    valid.append((d, p, r))
        return valid

    # ── Schedule ──────────────────────────────────────────────────────────────
    for idx in range(len(df_subjects)):
        for _ in range(required[idx]):
            slots = get_valid_slots(idx)
            if slots:
                random.shuffle(slots)
                d, p, r = slots[0]
                state[d, p, r] = idx + 1
                placed[idx]   += 1

    # ── Build per-division DataFrames ─────────────────────────────────────────
    def build_division_df(division):
        rows = []
        for d, day_name in enumerate(DAY_NAMES):
            times = FRIDAY_TIMES if d == 4 else WEEKDAY_TIMES
            row   = {"Day": day_name}
            for p in range(num_periods):
                cell = "---"
                for r in range(num_rooms):
                    cid = state[d, p, r]
                    if cid != 0:
                        div = id_to_div[cid]
                        if div == division or div == "ALL":
                            cell = f"{id_to_code[cid]} [{room_names[r]}]"
                            break
                row[f"P{p+1}  {times[p]}"] = cell
            rows.append(row)
        return pd.DataFrame(rows).set_index("Day")

    # ── Build raw full-state DataFrame ────────────────────────────────────────
    def build_raw_df():
        rows = []
        for d in range(num_days):
            times = FRIDAY_TIMES if d == 4 else WEEKDAY_TIMES
            for p in range(num_periods):
                entry = {
                    "Day":    DAY_NAMES[d],
                    "Period": f"P{p+1}",
                    "Time":   times[p],
                }
                for r in range(num_rooms):
                    cid = state[d, p, r]
                    entry[room_names[r]] = id_to_code[cid] if cid != 0 else "---"
                rows.append(entry)
        return pd.DataFrame(rows)

    result = {
        "CS6A": build_division_df("CS6A"),
        "CS6B": build_division_df("CS6B"),
        "CS6C": build_division_df("CS6C"),
        "raw":  build_raw_df(),
    }

    # ── Placement log ─────────────────────────────────────────────────────────
    print("\n── Placement Summary ──")
    for idx, row in df_subjects.iterrows():
        p = placed[idx]
        r = required[idx]
        print(f"  {'OK' if p>=r else 'MISS'} {row['course_code']:8} "
              f"({row['division']:5}) {p}/{r}")

    return result