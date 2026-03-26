import random
import numpy as np
import pandas as pd
from collections import defaultdict
from copy import deepcopy

# Configuration Constants
DAY_NAMES     = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
WEEKDAY_TIMES = ["9:30-10:30","10:30-11:30","11:30-12:30", "1:30-2:30","2:30-3:30","3:30-4:30"]
FRIDAY_TIMES  = ["9:30-10:30","10:30-11:30","11:30-12:30", "2:00-3:00","3:00-4:00","4:00-5:00"]

HONOURS_DAYS   = {1, 4}   # Tue, Fri
HONOURS_PERIOD = 4         # P5 (0-indexed)

# Lab block definitions
S2_LAB_BLOCKS  = [(0,1),(1,2),(3,4),(4,5)]      # 2 consecutive periods
S4_LAB_BLOCKS  = [(0,1,2),(3,4,5)]              # 3 consecutive periods

ROOM_NAMES = [
    "B202","B302","B303","B304", "Room_309","Room_310","Room_311","Room_201","Room_209",
    "Room_301","Room_210","Room_211","Room_402","Room_213", "Room_409","Room_410","Room_509",
    "Room_510","Room_511","Room_515", "Room_312","Room_512", "Room_401","Room_503","Room_501",
    "Room_314","Room_B307", "Room_315","Room_B207", "Room_B304", "Network_Lab_1","Network_Lab_2",
    "Network_Lab_3","Project_Lab",
]
NET_LABS  = ["Network_Lab_1","Network_Lab_2","Network_Lab_3"]

DIVISION_ROOMS = {
    "C2A":"Room_309","C2B":"Room_310","C2C":"Room_311","C2CB":"Room_209",
    "C4A":"Room_309","C4B":"Room_310","C4C":"Room_201","C4CB":"Room_209",
    "C6A":"B202","C6B":"B302","C6C":"B303","C6CB":"B304",
    "C8A":"Room_301","C8B":"Room_201","C8C":"Room_210","C8CB":"Room_211",
    "CS2A":"Room_309","CS2B":"Room_310","CS2C":"Room_311","CS2CB":"Room_209",
    "CS4A":"Room_309","CS4B":"Room_310","CS4C":"Room_201","CS4CB":"Room_209",
    "CS6A":"B202","CS6B":"B302","CS6C":"B303","CS6CB":"B304",
    "CS8A":"Room_301","CS8B":"Room_201","CS8C":"Room_210","CS8CB":"Room_211",
    "E2A":"Room_409","E2B":"Room_410", "E4A":"Room_409","E4B":"Room_410",
    "E6A":"Room_509","E6B":"Room_510", "E8A":"Room_511","E8B":"Room_515",
    "EC2A":"Room_409","EC2B":"Room_410", "EC4A":"Room_409","EC4B":"Room_410",
    "EC6A":"Room_509","EC6B":"Room_510", "EC8A":"Room_511","EC8B":"Room_515",
    "EV2":"Room_312","EV4":"Room_512","EV6":"Room_512", "EB2":"Room_401",
    "EB4":"Room_503","EB6":"Room_503","EB8":"Room_501", "EE2":"Room_314",
    "EE4":"Room_B307","EE6":"Room_B307","EE8":"Room_B307", "ME2":"Room_315",
    "ME4":"Room_B207","ME6":"Room_B207","ME8":"Room_B207", "CU2":"Room_402",
    "CU4":"Room_B304","CU6":"Room_B304","CU8":"Room_213",
}

FILLERS = [
    {"course_code":"LIB", "subject_name":"Library/Self Study", "teacher_code":"LIB", "required_hours":1,"room_type_needed":"Theory"},
    {"course_code":"PE", "subject_name":"Physical Education", "teacher_code":"PE", "required_hours":1,"room_type_needed":"Theory"},
    {"course_code":"MENTOR", "subject_name":"Mentoring", "teacher_code":"HOD", "required_hours":1,"room_type_needed":"Theory"},
]

def _is_lab_subject(row):
    n, c, r = str(row.get("subject_name","")).upper(), str(row.get("course_code","")).upper(), str(row.get("room_type_needed","")).upper()
    return "LAB" in n or "LAB" in c or "W/S" in n or r in ["LAB", "LAB_NETWORK", "LAB_PROJECT"]

def _pad_dataframe(df):
    extras = []
    for div in df["division"].unique():
        total = df[df["division"]==div]["required_hours"].sum()
        sem = df[df["division"]==div]["semester"].iloc[0]
        fi = 0
        while total < 30:
            f = deepcopy(FILLERS[fi % len(FILLERS)])
            f.update({"division": div, "semester": sem, "is_honours": False})
            extras.append(f)
            total += 1
            fi += 1
    return pd.concat([df, pd.DataFrame(extras)], ignore_index=True) if extras else df

def _schedule_one_semester(df_sem: pd.DataFrame) -> dict:
    sem = df_sem["semester"].iloc[0]
    df_sem = df_sem.copy()
    df_sem["room_type_needed"] = df_sem.apply(lambda r: "Lab" if _is_lab_subject(r) else r["room_type_needed"], axis=1)
    df_sem = _pad_dataframe(df_sem)

    num_rooms, room_idx = len(ROOM_NAMES), {n: i for i, n in enumerate(ROOM_NAMES)}
    subjects, subj_info, subj_teach = [], {}, {}

    for _, row in df_sem.iterrows():
        key = (str(row["course_code"]).strip(), str(row["division"]).strip())
        if key not in subj_info:
            subjects.append(key)
            subj_info[key] = {
                "required_hours": int(row["required_hours"]),
                "room_type_needed": str(row["room_type_needed"]),
                "is_honours": str(row.get("is_honours","")).lower()=="true",
                "subject_name": str(row["subject_name"]),
                "is_lab": _is_lab_subject(row),
            }
            subj_teach[key] = []
        tc = str(row.get("teacher_code","")).strip()
        if tc not in ["TBD", "nan", "LIB", "PE"] and tc not in subj_teach[key]:
            subj_teach[key].append(tc)

    state = np.zeros((5, 6, num_rooms), dtype=int)
    placed, div_used = [0] * len(subjects), {div: set() for _, div in subjects}
    lab_days = defaultdict(set)
    div_lab_total_slots = defaultdict(int) 

    # --- Teacher Schedule Tracking (Across all rooms/divisions) ---
    teacher_schedule = defaultdict(lambda: np.zeros((5, 6), dtype=int))

    def is_teacher_resting(t_codes, day, period):
        """Constraint: No 3 or more continuous theory classes"""
        for tc in t_codes:
            if tc in ["TBD", "nan", "LIB", "PE"]: continue
            sched = teacher_schedule[tc][day]
            # Check if placing here creates 3 in a row
            # Case 1: [T, T, New]
            if period >= 2 and sched[period-1] == 1 and sched[period-2] == 1: return False
            # Case 2: [New, T, T]
            if period <= 3 and sched[period+1] == 1 and sched[period+2] == 1: return False
            # Case 3: [T, New, T]
            if 0 < period < 5 and sched[period-1] == 1 and sched[period+1] == 1: return False
        return True

    def place_block(idx, rname, day, blk):
        ri = room_idx.get(rname)
        t_codes = subj_teach[subjects[idx]]
        for p in blk:
            state[day, p, ri] = idx + 1
            div_used[subjects[idx][1]].add((day, p))
            for tc in t_codes:
                if tc not in ["TBD", "nan", "LIB", "PE"]: teacher_schedule[tc][day][p] = 1
        placed[idx] += len(blk)
        lab_days[subjects[idx]].add(day)
        div_lab_total_slots[subjects[idx][1]] += len(blk)

    # STEP 1: Labs (With 6hr/2 sitting fix for S4+)
    lab_keys = [k for k in subjects if subj_info[k]["is_lab"]]
    for key in lab_keys:
        idx, div, hrs = subjects.index(key), key[1], subj_info[key]["required_hours"]
        troom = DIVISION_ROOMS.get(div)
        
        if sem in ["S4", "S6", "S8"]:
            blocks_to_place = int(hrs) if hrs > 0 else 1
            blk_choices, slots_per_blk = S4_LAB_BLOCKS, 3
            lab_room = NET_LABS[0] if "NETWORK" in subj_info[key]["room_type_needed"].upper() else troom
        else:
            blocks_to_place = 2 if hrs >= 2 else 1
            blk_choices, slots_per_blk = S2_LAB_BLOCKS, 2
            lab_room = troom

        placed_blocks, days = 0, list(range(5))
        random.shuffle(days)
        for day in days:
            if placed_blocks >= blocks_to_place: break
            if sem == "S2" and div_lab_total_slots[div] >= 4: break 
            if any(abs(day - d) < 2 for d in lab_days[key]): continue 

            for blk in blk_choices:
                if all((day, p) not in div_used[div] and state[day, p, room_idx[lab_room]] == 0 for p in blk):
                    place_block(idx, lab_room, day, blk)
                    placed_blocks += 1
                    break

    # STEP 2 & 3: Theory & Honours (Standard Placement + Resting Constraint)
    other_keys = [k for k in subjects if not subj_info[k]["is_lab"]]
    for key in sorted(other_keys, key=lambda k: -subj_info[k]["required_hours"]):
        idx, div, needed = subjects.index(key), key[1], subj_info[key]["required_hours"]
        t_codes = subj_teach[key]
        ri = room_idx.get(DIVISION_ROOMS.get(div, ROOM_NAMES[0]))
        
        # Shuffle days and periods for variety
        slots = [(d, p) for d in range(5) for p in range(6)]
        random.shuffle(slots)
        
        for day, period in slots:
            if placed[idx] >= needed: break
            
            # Check Division, Room, and Teacher Resting constraint
            if (day, period) not in div_used[div] and state[day, period, ri] == 0:
                if is_teacher_resting(t_codes, day, period):
                    state[day, period, ri] = idx + 1
                    div_used[div].add((day, period))
                    for tc in t_codes:
                        if tc not in ["TBD", "nan", "LIB", "PE"]: teacher_schedule[tc][day][period] = 1
                    placed[idx] += 1

    # Visualization: Show "LAB" for all practicals
    def get_cell(div, d, p):
        for r, rn in enumerate(ROOM_NAMES):
            cid = state[d, p, r]
            if cid != 0 and subjects[cid-1][1] == div:
                info = subj_info[subjects[cid-1]]
                return f"{'LAB' if info['is_lab'] else info['subject_name']} [{rn}]"
        return "---"

    res = {}
    for div in set(d for _, d in subjects):
        rows = [{"Day": DAY_NAMES[d], **{f"P{p+1}": get_cell(div, d, p) for p in range(6)}} for d in range(5)]
        res[div] = pd.DataFrame(rows)
    return res

def generate_timetable(df_allotment: pd.DataFrame) -> dict:
    df_allotment.columns = df_allotment.columns.str.strip().str.lower()
    all_results = {}
    for sem in df_allotment["semester"].unique():
        all_results.update(_schedule_one_semester(df_allotment[df_allotment["semester"] == sem]))
    return all_results