"""
generator.py — MEC Timetable Generator (v10)
Fixes:
  1. Lab subjects show correctly in division view
  2. Theory NOT scheduled during the division's own lab block
  3. CSD334_CS6C gets its own separate lab block (no more fallback confusion)
  4. All divisions' lab sessions properly tracked and blocked for theory
"""

import random
import numpy as np
import pandas as pd

DAY_NAMES     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
WEEKDAY_TIMES = ["9:30-10:30","10:30-11:30","11:30-12:30",
                 "1:30-2:30","2:30-3:30","3:30-4:30"]
FRIDAY_TIMES  = ["9:30-10:30","10:30-11:30","11:30-12:30",
                 "2:00-3:00","3:00-4:00","4:00-5:00"]

HONOURS_DAYS   = {1, 4}
HONOURS_PERIOD = 4
HONOURS_ROOM   = "Room_310"
DIVISION_ROOMS = {"CS6A": "B202", "CS6B": "B302", "CS6C": "B303"}
LAB_BLOCKS     = [(0,1,2), (3,4,5)]


def generate_timetable(df_subjects, df_rooms, df_teachers):
    df_subjects.columns = df_subjects.columns.str.strip().str.lower()
    df_rooms.columns    = df_rooms.columns.str.strip().str.lower()

    room_names = df_rooms["room_name"].tolist()
    num_rooms  = len(room_names)
    room_idx   = {name: i for i, name in enumerate(room_names)}
    net_labs   = [r for r in room_names if "Network" in r]
    proj_labs  = [r for r in room_names if "Project" in r]

    state  = np.zeros((5, 6, num_rooms), dtype=int)
    placed = [0] * len(df_subjects)
    req    = df_subjects["required_hours"].astype(int).tolist()

    id_to_code = {i+1: r["course_code"] for i, r in df_subjects.iterrows()}
    id_to_div  = {i+1: r["division"]    for i, r in df_subjects.iterrows()}

    # Track which (day, block) each division is busy in lab
    # div_lab_blocks[division] = list of (day, block) tuples
    div_lab_blocks = {"CS6A": [], "CS6B": [], "CS6C": []}

    def get_idx(code, division):
        rows = df_subjects[(df_subjects["course_code"]==code) &
                           (df_subjects["division"]==division)]
        return rows.index[0] if not rows.empty else None

    def teacher_busy(code, day, period):
        for r in range(num_rooms):
            cid = state[day, period, r]
            if cid != 0 and df_subjects.iloc[cid-1]["teacher_code"] == code:
                return True
        return False

    def block_teacher_free(code, day, block):
        return all(not teacher_busy(code, day, p) for p in block)

    def block_room_free(rname, day, block):
        ri = room_idx[rname]
        return all(state[day, p, ri] == 0 for p in block)

    def place_block(idx, rname, day, block):
        ri = room_idx[rname]
        for p in block:
            state[day, p, ri] = idx + 1
        placed[idx] += 3

    def div_in_lab(division, day, period):
        """True if this division has a lab session at (day, period)."""
        for (d, blk) in div_lab_blocks[division]:
            if d == day and period in blk:
                return True
        return False

    # ── STEP 1: Two shared lab sessions (all 3 divisions simultaneously) ──────
    # Session 1: Net_Lab_1→CS6A, Net_Lab_2→CS6B, Net_Lab_3→CS6C, Proj→CS6A
    # Session 2: Net_Lab_1→CS6A, Net_Lab_2→CS6B, Net_Lab_3→CS6C, Proj→CS6B
    # CS6C CSD334: separate block in Net_Lab (since only 1 Project_Lab)

    csl = {div: get_idx("CSL332", div) for div in ["CS6A","CS6B","CS6C"]}
    csd = {div: get_idx("CSD334", div) for div in ["CS6A","CS6B","CS6C"]}

    valid_blocks = [
        (day, block)
        for day in range(5)
        for block in LAB_BLOCKS
        if not (day in HONOURS_DAYS and HONOURS_PERIOD in block)
    ]

    used_slots = []

    # Place 2 shared CSL332 sessions (all 3 divisions in network labs)
    # + CSD334 for CS6A (session1) and CS6B (session2) in project lab
    proj_rotation = ["CS6A", "CS6B"]
    shared_sessions = 0

    candidates = list(valid_blocks)
    random.shuffle(candidates)

    for day, block in candidates:
        if shared_sessions >= 2:
            break
        if (day, block) in used_slots:
            continue

        # All 3 CSL332 teachers free
        if not all(block_teacher_free(
                df_subjects.iloc[csl[div]]["teacher_code"], day, block)
                for div in ["CS6A","CS6B","CS6C"] if csl[div] is not None):
            continue

        # CSD334 teacher for this session's proj div must be free
        proj_div = proj_rotation[shared_sessions]
        if not block_teacher_free(
                df_subjects.iloc[csd[proj_div]]["teacher_code"], day, block):
            continue

        # All 3 net labs free
        if not all(block_room_free(net_labs[i], day, block) for i in range(3)):
            continue

        # Project lab free
        if not block_room_free(proj_labs[0], day, block):
            continue

        # Place CSL332 for all 3 divisions
        for i, div in enumerate(["CS6A","CS6B","CS6C"]):
            if csl[div] is not None:
                place_block(csl[div], net_labs[i], day, block)
                div_lab_blocks[div].append((day, block))

        # Place CSD334 for proj_div in project lab
        place_block(csd[proj_div], proj_labs[0], day, block)

        used_slots.append((day, block))
        shared_sessions += 1
        slot = "Morning P1-P3" if block[0]==0 else "Afternoon P4-P6"
        print(f"  Shared LAB session {shared_sessions}: {DAY_NAMES[day]} {slot}")
        print(f"    CSL332: CS6A→{net_labs[0]}, CS6B→{net_labs[1]}, CS6C→{net_labs[2]}")
        print(f"    CSD334: {proj_div}→{proj_labs[0]}")

    # Place CSD334 for CS6C (and CS6B if not placed) in remaining net lab slots
    for div in ["CS6B", "CS6C"]:
        ci = csd[div]
        if ci is None or placed[ci] >= req[ci]:
            continue

        random.shuffle(candidates)
        for day, block in candidates:
            if (day, block) in used_slots:
                continue
            if day in HONOURS_DAYS and HONOURS_PERIOD in block:
                continue

            teacher = df_subjects.iloc[ci]["teacher_code"]
            if not block_teacher_free(teacher, day, block):
                continue

            # Find any free net lab
            net = next((l for l in net_labs
                        if block_room_free(l, day, block)), None)
            if net:
                place_block(ci, net, day, block)
                div_lab_blocks[div].append((day, block))
                used_slots.append((day, block))
                slot = "Morning P1-P3" if block[0]==0 else "Afternoon P4-P6"
                print(f"  CSD334_{div}: {DAY_NAMES[day]} {slot} → {net}")
                break

    print(f"\n  Lab blocks per division:")
    for div, blocks in div_lab_blocks.items():
        for d, b in blocks:
            slot = "Morning" if b[0]==0 else "Afternoon"
            print(f"    {div}: {DAY_NAMES[d]} {slot}")

    # ── STEP 2: Honours ───────────────────────────────────────────────────────
    hon = df_subjects[df_subjects["is_honours"].astype(str).str.lower()=="true"]
    for idx, row in hon.iterrows():
        placed[idx] = 0
        for day in sorted(HONOURS_DAYS):
            if state[day, HONOURS_PERIOD, room_idx[HONOURS_ROOM]] == 0:
                state[day, HONOURS_PERIOD, room_idx[HONOURS_ROOM]] = idx + 1
                placed[idx] += 1
                print(f"  HON: {DAY_NAMES[day]} P{HONOURS_PERIOD+1} → {HONOURS_ROOM}")

    # ── STEP 3: Theory — skip division's own lab periods ──────────────────────
    theory = df_subjects[
        (df_subjects["is_honours"].astype(str).str.lower() != "true") &
        (~df_subjects["course_code"].isin(["CSL332","CSD334"]))
    ].sort_values("required_hours", ascending=False)

    for idx, row in theory.iterrows():
        division = row["division"]
        teacher  = row["teacher_code"]
        t_room   = DIVISION_ROOMS.get(division)
        if not t_room:
            continue
        ri     = room_idx[t_room]
        needed = req[idx]
        placed[idx] = 0

        slots = [(d, p) for d in range(5) for p in range(6)]
        random.shuffle(slots)

        for day, period in slots * 10:
            if placed[idx] >= needed:
                break

            # Skip Honours slot
            if day in HONOURS_DAYS and period == HONOURS_PERIOD:
                continue
            # ── KEY FIX: skip if division is in lab at this period ────────────
            if div_in_lab(division, day, period):
                continue
            # Theory room must be free
            if state[day, period, ri] != 0:
                continue
            # Teacher must be free
            if teacher_busy(teacher, day, period):
                continue
            # Max 2 of same subject per day
            if sum(1 for p in range(6)
                   if state[day, p, ri] == idx+1) >= 2:
                continue
            # No back-to-back same subject
            before = period > 0 and state[day, period-1, ri] == idx+1
            after  = period < 5 and state[day, period+1, ri] == idx+1
            if before or after:
                continue
            # Max 2 theory periods for this teacher today
            if sum(1 for p in range(6)
                   if state[day, p, ri] != 0 and
                   df_subjects.iloc[state[day, p, ri]-1]["teacher_code"] == teacher
                   ) >= 2:
                continue

            state[day, period, ri] = idx + 1
            placed[idx] += 1

    # ── Build DataFrames ──────────────────────────────────────────────────────
    def get_cell(division, day, period):
        # 1. Theory room
        t_room = DIVISION_ROOMS.get(division)
        if t_room:
            cid = state[day, period, room_idx[t_room]]
            if cid != 0 and (id_to_div[cid]==division or id_to_div[cid]=="ALL"):
                return f"{id_to_code[cid]} [{t_room}]"

        # 2. Honours room
        cid = state[day, period, room_idx[HONOURS_ROOM]]
        if cid != 0 and id_to_div[cid] == "ALL":
            return f"{id_to_code[cid]} [{HONOURS_ROOM}]"

        # 3. Lab rooms — match by division
        for r, rname in enumerate(room_names):
            if rname in (t_room, HONOURS_ROOM):
                continue
            cid = state[day, period, r]
            if cid != 0 and id_to_div[cid] == division:
                return f"{id_to_code[cid]} [{rname}]"

        # 4. Show lab period as "LAB SESSION" if division is in lab
        if div_in_lab(division, day, period):
            return "LAB SESSION"

        return "---"

    def build_division_df(division):
        wday = {"Day": "Time (Mon-Thu)"}
        fri  = {"Day": "Time (Friday)"}
        sep  = {"Day": ""}
        for p in range(6):
            wday[f"P{p+1}"] = WEEKDAY_TIMES[p]
            fri[f"P{p+1}"]  = FRIDAY_TIMES[p]
            sep[f"P{p+1}"]  = ""
        rows = [wday, fri, sep]
        for d, day_name in enumerate(DAY_NAMES):
            row = {"Day": day_name}
            for p in range(6):
                row[f"P{p+1}"] = get_cell(division, d, p)
            rows.append(row)
        return pd.DataFrame(rows, columns=["Day","P1","P2","P3","P4","P5","P6"])

    def build_raw_df():
        rows = []
        for d in range(5):
            times = FRIDAY_TIMES if d == 4 else WEEKDAY_TIMES
            for p in range(6):
                entry = {"Day": DAY_NAMES[d], "Period": f"P{p+1}", "Time": times[p]}
                for r, rname in enumerate(room_names):
                    cid = state[d, p, r]
                    entry[rname] = id_to_code[cid] if cid != 0 else "---"
                rows.append(entry)
        return pd.DataFrame(rows)

    result = {
        "CS6A": build_division_df("CS6A"),
        "CS6B": build_division_df("CS6B"),
        "CS6C": build_division_df("CS6C"),
        "raw":  build_raw_df(),
    }

    print("\n── Placement Summary ──")
    all_ok = True
    for idx, row in df_subjects.iterrows():
        actual = int(np.sum(state == idx + 1))
        r = req[idx]
        ok = actual >= r
        all_ok = all_ok and ok
        print(f"  {'✅' if ok else '❌'} {row['course_code']:8} "
              f"({row['division']:5}) {actual}/{r}")
    print(f"\n  {'🎉 All placed!' if all_ok else '⚠️  Some missing'}")
    return result