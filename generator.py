"""
generator.py — MEC Timetable Generator (v15)
Lab sessions: STRICTLY 3 continuous periods — either P1-P2-P3 (morning)
              OR P4-P5-P6 (afternoon). No scattered individual placements.
Each division's lab sessions are on DIFFERENT days from each other.
Theory scheduler is BLOCKED from touching lab periods for that division.
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
LAB_BLOCKS     = [(0,1,2), (3,4,5)]   # morning P1-P3 or afternoon P4-P6

ROOM_NAMES = [
    "B202","B302","B303","B304",
    "Room_309","Room_310","Room_311","Room_201","Room_209",
    "Room_301","Room_210","Room_211",
    "Room_402","Room_213",
    "Room_409","Room_410","Room_509","Room_510","Room_511","Room_515",
    "Room_312","Room_512",
    "Room_401","Room_503","Room_501",
    "Room_314","Room_B307",
    "Room_315","Room_B207",
    "Room_B304",
    "Network_Lab_1","Network_Lab_2","Network_Lab_3","Project_Lab",
]

NET_LABS  = ["Network_Lab_1","Network_Lab_2","Network_Lab_3"]
PROJ_LABS = ["Project_Lab"]

DIVISION_ROOMS = {
    "CS2A":"Room_309","CS2B":"Room_310","CS2C":"Room_311","CS2CB":"Room_209",
    "CS4A":"Room_309","CS4B":"Room_310","CS4C":"Room_201","CS4CB":"Room_209",
    "CS6A":"B202","CS6B":"B302","CS6C":"B303","CS6CB":"B304",
    "CS8A":"Room_301","CS8B":"Room_201","CS8C":"Room_210","CS8CB":"Room_211",
    "EC2A":"Room_409","EC2B":"Room_410",
    "EC4A":"Room_409","EC4B":"Room_410",
    "EC6A":"Room_509","EC6B":"Room_510",
    "EC8A":"Room_511","EC8B":"Room_515",
    "EV2":"Room_312","EV4":"Room_512","EV6":"Room_512",
    "EB2":"Room_401","EB4":"Room_503","EB6":"Room_503","EB8":"Room_501",
    "EE2":"Room_314","EE4":"Room_B307","EE6":"Room_B307","EE8":"Room_B307",
    "ME2":"Room_315","ME4":"Room_B207","ME6":"Room_B207","ME8":"Room_B207",
    "CU2":"Room_402","CU4":"Room_B304","CU6":"Room_B304","CU8":"Room_213",
    "EEE":"Room_309",
}


def _schedule_one_semester(df_sem: pd.DataFrame) -> dict:
    sem = df_sem["semester"].iloc[0]
    room_names = ROOM_NAMES
    num_rooms  = len(room_names)
    room_idx   = {n: i for i, n in enumerate(room_names)}

    # ── Build subject list ────────────────────────────────────────────────────
    subjects  = []
    subj_info = {}
    subj_teach= {}

    for _, row in df_sem.iterrows():
        code = str(row["course_code"]).strip()
        div  = str(row["division"]).strip()
        tc   = str(row["teacher_code"]).strip()
        key  = (code, div)
        if key not in subj_info:
            subjects.append(key)
            subj_info[key] = {
                "required_hours":   int(row["required_hours"]),
                "room_type_needed": str(row["room_type_needed"]).strip(),
                "is_honours":       str(row["is_honours"]).strip().lower() == "true",
                "subject_name":     str(row["subject_name"]).strip(),
            }
            subj_teach[key] = []
        if tc and tc not in ("TBD","nan") and tc not in subj_teach[key]:
            subj_teach[key].append(tc)

    ns     = len(subjects)
    state  = np.zeros((5, 6, num_rooms), dtype=int)
    placed = [0] * ns
    req    = [subj_info[k]["required_hours"] for k in subjects]
    s_idx  = {k: i for i, k in enumerate(subjects)}

    divisions = list(dict.fromkeys(div for _, div in subjects))
    # div_lab_periods: which (day,period) each division is in lab
    div_lab_periods = {div: set() for div in divisions}
    # track which days each division already has a lab
    div_lab_days = {div: set() for div in divisions}

    # ── Helpers ───────────────────────────────────────────────────────────────
    def teacher_busy(tc, day, period):
        for r in range(num_rooms):
            cid = state[day, period, r]
            if cid != 0 and tc in subj_teach[subjects[cid-1]]:
                return True
        return False

    def any_free(idx, day, period):
        ts = subj_teach[subjects[idx]]
        return not ts or any(not teacher_busy(tc, day, period) for tc in ts)

    def block_any_free(idx, day, block):
        ts = subj_teach[subjects[idx]]
        return not ts or any(
            all(not teacher_busy(tc, day, p) for p in block) for tc in ts
        )

    def block_room_free(rname, day, block):
        ri = room_idx.get(rname)
        if ri is None: return False
        return all(state[day, p, ri] == 0 for p in block)

    def place_block(idx, rname, day, block):
        """Place subject idx in rname for all 3 periods of block."""
        ri = room_idx.get(rname)
        if ri is None: return False
        for p in block:
            state[day, p, ri] = idx + 1
        placed[idx] += 3
        return True

    def div_in_lab(div, day, period):
        return (day, period) in div_lab_periods.get(div, set())

    def mark_lab_periods(div, day, block):
        for p in block: div_lab_periods[div].add((day, p))
        div_lab_days[div].add(day)

    # Valid blocks: never put a lab in a block that includes the honours period
    valid_blocks = [
        (day, blk) for day in range(5) for blk in LAB_BLOCKS
        if not (day in HONOURS_DAYS and HONOURS_PERIOD in blk)
    ]

    # ── STEP 1: Lab scheduling — strictly continuous 3-hour blocks ───────────
    # Group lab subjects by type and find which divisions need them
    net_keys  = [(c,d) for (c,d) in subjects
                 if subj_info[(c,d)]["room_type_needed"] == "Lab_Network"]
    proj_keys = [(c,d) for (c,d) in subjects
                 if subj_info[(c,d)]["room_type_needed"] == "Lab_Project"]
    proj_divs = list(dict.fromkeys(d for _,d in proj_keys))

    net_day = None
    used_net_days = set()

    # Group net lab subjects by subject_name — schedule each group separately
    net_by_subj = {}
    for k in net_keys:
        sname = subj_info[k]["subject_name"]
        net_by_subj.setdefault(sname, []).append(k)

    for sname, group_keys in net_by_subj.items():
        group_divs = list(dict.fromkeys(d for _,d in group_keys))
        # If more divisions than net labs, split into batches of 3
        all_group_divs = group_divs
        all_group_keys = group_keys
        batches = [all_group_divs[i:i+len(NET_LABS)] 
                   for i in range(0, len(all_group_divs), len(NET_LABS))]
        group_divs = batches[0]
        group_keys = [k for k in all_group_keys if k[1] in group_divs]

        cands = list(valid_blocks)
        random.shuffle(cands)
        for day, blk in cands:
            if day in used_net_days: continue
            if not all(block_any_free(s_idx[k], day, blk)
                       for k in group_keys if k in s_idx):
                continue
            if not all(block_room_free(NET_LABS[i], day, blk)
                       for i in range(len(group_divs))):
                continue
            for i, div in enumerate(group_divs):
                dk = [(c,d) for (c,d) in group_keys if d == div]
                if dk:
                    place_block(s_idx[dk[0]], NET_LABS[i], day, blk)
                    mark_lab_periods(div, day, blk)
            used_net_days.add(day)
            if net_day is None: net_day = day
            slot = "Morning (P1-P3)" if blk[0]==0 else "Afternoon (P4-P6)"
            print(f"  NET LAB '{sname}' [{sem}]: {DAY_NAMES[day]} {slot}")
            # Schedule overflow batches on separate days
            for batch in batches[1:]:
                batch_keys = [k for k in all_group_keys if k[1] in batch]
                for day2, blk2 in cands:
                    if day2 in used_net_days: continue
                    if not all(block_any_free(s_idx[k], day2, blk2)
                               for k in batch_keys if k in s_idx): continue
                    if not all(block_room_free(NET_LABS[i], day2, blk2)
                               for i in range(len(batch))): continue
                    for i, div2 in enumerate(batch):
                        dk2 = [(c,d) for (c,d) in batch_keys if d == div2]
                        if dk2:
                            place_block(s_idx[dk2[0]], NET_LABS[i], day2, blk2)
                            mark_lab_periods(div2, day2, blk2)
                    used_net_days.add(day2)
                    slot2 = "Morning (P1-P3)" if blk2[0]==0 else "Afternoon (P4-P6)"
                    print(f"  NET LAB '{sname}' overflow [{sem}]: {DAY_NAMES[day2]} {slot2}")
                    break
            break

    # --- Project lab: all divisions, DIFFERENT day from net lab
    if proj_keys:
        cands = list(valid_blocks)
        random.shuffle(cands)
        for day, blk in cands:
            if day == net_day:
                continue
            # No division should already have a lab this day
            if any(day in div_lab_days.get(div, set()) for div in proj_divs):
                continue
            # All proj lab teachers free
            if not all(block_any_free(s_idx[k], day, blk)
                       for k in proj_keys if k in s_idx):
                continue
            # Project lab room free
            if not block_room_free(PROJ_LABS[0], day, blk):
                continue
            # Need enough net labs for overflow (CS6B/C go to net labs)
            free_nets = [l for l in NET_LABS if block_room_free(l, day, blk)]
            if len(free_nets) < max(0, len(proj_divs) - 1):
                continue
            # Place: first division → Project_Lab, others → Net_Labs
            for i, div in enumerate(proj_divs):
                dk = [(c,d) for (c,d) in proj_keys if d == div]
                if not dk: continue
                room = PROJ_LABS[0] if i == 0 else free_nets[i-1]
                place_block(s_idx[dk[0]], room, day, blk)
                mark_lab_periods(div, day, blk)
            slot = "Morning (P1-P3)" if blk[0]==0 else "Afternoon (P4-P6)"
            print(f"  PROJ LAB [{sem}]: {DAY_NAMES[day]} {slot}  ← different day ✅")
            break

    # ── STEP 2: Honours — in division's own room, preferring Tue/Fri P5 ──────
    for key in subjects:
        if not subj_info[key]["is_honours"]: continue
        idx   = s_idx[key]
        div   = key[1]
        needed= req[idx]
        placed[idx] = 0
        troom = DIVISION_ROOMS.get(div)
        if not troom or troom not in room_idx: continue
        ri = room_idx[troom]
        preferred = [(d, HONOURS_PERIOD) for d in sorted(HONOURS_DAYS)]
        other = [(d,p) for d in range(5) for p in range(6)
                 if not (d in HONOURS_DAYS and p == HONOURS_PERIOD)]
        random.shuffle(other)
        for day, period in preferred + other:
            if placed[idx] >= needed: break
            if div_in_lab(div, day, period): continue
            if state[day, period, ri] != 0: continue
            state[day, period, ri] = idx + 1
            placed[idx] += 1

    # ── STEP 3: Theory — never touch a division's lab periods ─────────────────
    theory_keys = sorted(
        [(c,d) for (c,d) in subjects
         if subj_info[(c,d)]["room_type_needed"] == "Theory"
         and not subj_info[(c,d)]["is_honours"]],
        key=lambda k: -subj_info[k]["required_hours"]
    )

    for key in theory_keys:
        idx   = s_idx[key]
        div   = key[1]
        troom = DIVISION_ROOMS.get(div)
        if not troom or troom not in room_idx:
            for rn in ROOM_NAMES:
                if "Lab" not in rn:
                    troom = rn
                    break
        ri    = room_idx.get(troom, 0)
        needed= req[idx]
        placed[idx] = 0

        slots = [(d,p) for d in range(5) for p in range(6)]
        random.shuffle(slots)

        for day, period in slots * 10:
            if placed[idx] >= needed: break
            # Skip honours period
            if day in HONOURS_DAYS and period == HONOURS_PERIOD: continue
            # ── KEY: skip if division is in a lab this period ─────────────────
            if div_in_lab(div, day, period): continue
            # Room must be free
            if state[day, period, ri] != 0: continue
            # Teacher free
            if not any_free(idx, day, period): continue
            # Max 2 of same subject per day
            if sum(1 for p in range(6) if state[day,p,ri]==idx+1) >= 2: continue
            # No back-to-back same subject
            if (period>0 and state[day,period-1,ri]==idx+1) or \
               (period<5 and state[day,period+1,ri]==idx+1): continue

            state[day, period, ri] = idx + 1
            placed[idx] += 1

    # ── Build output DataFrames ───────────────────────────────────────────────
    def get_cell(div, day, period):
        troom = DIVISION_ROOMS.get(div)
        # Theory room
        if troom and troom in room_idx:
            cid = state[day, period, room_idx[troom]]
            if cid != 0 and subjects[cid-1][1] == div:
                return f"{subjects[cid-1][0]} [{troom}]"
        # Lab rooms
        for r, rname in enumerate(room_names):
            if rname == troom: continue
            cid = state[day, period, r]
            if cid != 0 and subjects[cid-1][1] == div:
                return f"{subjects[cid-1][0]} [{rname}]"
        # Show lab session marker
        if div_in_lab(div, day, period):
            return "LAB SESSION"
        return "---"

    def build_div_df(div):
        wday={"Day":"Time (Mon-Thu)"}; fri={"Day":"Time (Friday)"}; sep={"Day":""}
        for p in range(6):
            wday[f"P{p+1}"]=WEEKDAY_TIMES[p]; fri[f"P{p+1}"]=FRIDAY_TIMES[p]
            sep[f"P{p+1}"]=""
        rows=[wday,fri,sep]
        for d,dn in enumerate(DAY_NAMES):
            row={"Day":dn}
            for p in range(6): row[f"P{p+1}"]=get_cell(div,d,p)
            rows.append(row)
        return pd.DataFrame(rows,columns=["Day","P1","P2","P3","P4","P5","P6"])

    def build_raw():
        rows=[]
        for d in range(5):
            times=FRIDAY_TIMES if d==4 else WEEKDAY_TIMES
            for p in range(6):
                e={"Day":DAY_NAMES[d],"Period":f"P{p+1}","Time":times[p]}
                for r,rn in enumerate(room_names):
                    cid=state[d,p,r]
                    e[rn]=subjects[cid-1][0] if cid!=0 else "---"
                rows.append(e)
        return pd.DataFrame(rows)

    result = {div: build_div_df(div) for div in divisions}
    result[f"raw_{sem}"] = build_raw()

    # Summary
    missed = [(subjects[i],placed[i],req[i])
              for i in range(ns) if placed[i] < req[i]]
    if missed:
        for key,p,r in missed:
            print(f"  ❌ {key[0]:12}({key[1]:8}) {p}/{r}")
    else:
        print(f"  ✅ All {ns} subjects placed for {sem}")

    return result


def generate_timetable(df_allotment: pd.DataFrame) -> dict:
    df_allotment.columns = df_allotment.columns.str.strip().str.lower()
    all_results = {}
    for sem in df_allotment["semester"].unique():
        df_sem = df_allotment[df_allotment["semester"]==sem].copy()
        print(f"\n── {sem} ({len(df_sem)} rows, "
              f"{df_sem['division'].nunique()} divisions) ──")
        all_results.update(_schedule_one_semester(df_sem))
    return all_results