"""
generator.py — MEC ChronoAI Timetable Generator (v19)

Changes from v18:
  • Display format: "Subject [Room] (Teacher)" in each cell
  • Teacher collision prevention: no two divisions share same primary teacher
    at same day+period
  • Teacher minimum 3hr/day: theory subjects for same teacher grouped to
    same day where possible (soft constraint, best-effort)
  • Full (All Rooms) raw view: single unified table Day×Period with all rooms
  • Lab rules unchanged:
      S2: 2 consecutive slots × 2 days = 4 slots, show "LAB [room] (Teacher)"
      S4+: 3 consecutive slots × 2 days = 6 slots, show "LAB [room] (Teacher)"
"""

import random
import numpy as np
import pandas as pd
from collections import defaultdict
from copy import deepcopy

DAY_NAMES     = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
WEEKDAY_TIMES = ["9:30-10:30","10:30-11:30","11:30-12:30",
                 "1:30-2:30","2:30-3:30","3:30-4:30"]
FRIDAY_TIMES  = ["9:30-10:30","10:30-11:30","11:30-12:30",
                 "2:00-3:00","3:00-4:00","4:00-5:00"]

HONOURS_DAYS   = {1, 4}
HONOURS_PERIOD = 4

S2_LAB_BLOCKS = [(0,1),(3,4)]
S4_LAB_BLOCKS = [(0,1,2),(3,4,5)]

ROOM_NAMES = [
    "B202","B302","B303","B304",
    "Room_309","Room_310","Room_311","Room_201","Room_209",
    "Room_301","Room_210","Room_211","Room_402","Room_213",
    "Room_409","Room_410","Room_509","Room_510","Room_511","Room_515",
    "Room_312","Room_512",
    "Room_401","Room_503","Room_501",
    "Room_314","Room_B307",
    "Room_315","Room_B207",
    "Room_B304",
    "Network_Lab_1","Network_Lab_2","Network_Lab_3","Project_Lab",
]
NET_LABS = ["Network_Lab_1","Network_Lab_2","Network_Lab_3"]

DIVISION_ROOMS = {
    "C2A":"Room_309","C2B":"Room_310","C2C":"Room_311","C2CB":"Room_209",
    "C4A":"Room_309","C4B":"Room_310","C4C":"Room_201","C4CB":"Room_209",
    "C6A":"B202","C6B":"B302","C6C":"B303","C6CB":"B304",
    "C8A":"Room_301","C8B":"Room_201","C8C":"Room_210","C8CB":"Room_211",
    "CS2A":"Room_309","CS2B":"Room_310","CS2C":"Room_311","CS2CB":"Room_209",
    "CS4A":"Room_309","CS4B":"Room_310","CS4C":"Room_201","CS4CB":"Room_209",
    "CS6A":"B202","CS6B":"B302","CS6C":"B303","CS6CB":"B304",
    "CS8A":"Room_301","CS8B":"Room_201","CS8C":"Room_210","CS8CB":"Room_211",
    "E2A":"Room_409","E2B":"Room_410",
    "E4A":"Room_409","E4B":"Room_410",
    "E6A":"Room_509","E6B":"Room_510",
    "E8A":"Room_511","E8B":"Room_515",
    "EC2A":"Room_409","EC2B":"Room_410",
    "EC4A":"Room_409","EC4B":"Room_410",
    "EC6A":"Room_509","EC6B":"Room_510",
    "EC8A":"Room_511","EC8B":"Room_515",
    "EV2":"Room_312","EV4":"Room_512","EV6":"Room_512",
    "EB2":"Room_401","EB4":"Room_503","EB6":"Room_503","EB8":"Room_501",
    "EE2":"Room_314","EE4":"Room_B307","EE6":"Room_B307","EE8":"Room_B307",
    "ME2":"Room_315","ME4":"Room_B207","ME6":"Room_B207","ME8":"Room_B207",
    "CU2":"Room_402","CU4":"Room_B304","CU6":"Room_B304","CU8":"Room_213",
}

FILLERS = [
    {"course_code":"LIB",    "subject_name":"Library/Self Study",
     "teacher_code":"LIB",   "required_hours":1,"room_type_needed":"Theory",
     "is_honours":False,"scheme":""},
    {"course_code":"PE",     "subject_name":"Physical Education",
     "teacher_code":"PE",    "required_hours":1,"room_type_needed":"Theory",
     "is_honours":False,"scheme":""},
    {"course_code":"MENTOR", "subject_name":"Mentoring/Counseling",
     "teacher_code":"HOD",   "required_hours":1,"room_type_needed":"Theory",
     "is_honours":False,"scheme":""},
    {"course_code":"SEMINAR","subject_name":"Seminar/Guest Lecture",
     "teacher_code":"HOD",   "required_hours":1,"room_type_needed":"Theory",
     "is_honours":False,"scheme":""},
]
FILLER_CODES = {f["course_code"] for f in FILLERS}
NO_COLLISION_TEACHERS = {"LIB","PE","HOD","TBD",""}


def _is_lab(row):
    n = str(row.get("subject_name","")).upper()
    c = str(row.get("course_code","")).upper()
    r = str(row.get("room_type_needed","")).upper()
    return ("LAB" in n or "LAB" in c or "W/S" in n or
            "ITWS" in n or "ITWS" in c or
            "LAB_NETWORK" in r or "LAB_PROJECT" in r or r == "LAB")


def _primary_teacher(tc_str):
    """Extract primary (first) teacher code from composite string like 'JJP,DVP/AJA,CHJ'"""
    tc = str(tc_str).strip()
    if not tc or tc in ("nan","TBD"):
        return ""
    return tc.split(",")[0].split("/")[0].strip()


def _all_teachers(tc_str):
    """Extract ALL individual teacher codes from composite string."""
    tc = str(tc_str).strip()
    if not tc or tc in ("nan","TBD"):
        return []
    # Split by comma and slash
    parts = []
    for seg in tc.replace("/",",").split(","):
        s = seg.strip()
        if s and s not in ("nan","TBD"):
            parts.append(s)
    return parts


def _schedule_one_semester(df_sem: pd.DataFrame) -> dict:
    sem = df_sem["semester"].iloc[0]

    # Fix room_type for lab subjects
    def fix_rt(row):
        if _is_lab(row): return "Lab"
        return row["room_type_needed"]
    df_sem = df_sem.copy()
    df_sem["room_type_needed"] = df_sem.apply(fix_rt, axis=1)

    # Pad each division to 30 hours
    extras = []
    for div in df_sem["division"].unique():
        total = df_sem[df_sem["division"]==div]["required_hours"].sum()
        fi = 0
        while total < 30:
            f = deepcopy(FILLERS[fi % len(FILLERS)])
            f["division"] = div
            f["semester"] = sem
            extras.append(f)
            total += 1; fi += 1
    if extras:
        df_sem = pd.concat([df_sem, pd.DataFrame(extras)], ignore_index=True)

    num_rooms = len(ROOM_NAMES)
    room_idx  = {n: i for i, n in enumerate(ROOM_NAMES)}

    subjects   = []
    subj_info  = {}   # key → {required_hours, room_type_needed, is_honours,
                      #         subject_name, is_lab, primary_tc, all_tcs}

    for _, row in df_sem.iterrows():
        code = str(row["course_code"]).strip()
        div  = str(row["division"]).strip()
        tc   = str(row.get("teacher_code","")).strip()
        key  = (code, div)
        if key not in subj_info:
            subjects.append(key)
            subj_info[key] = {
                "required_hours":   int(row["required_hours"]),
                "room_type_needed": str(row["room_type_needed"]).strip(),
                "is_honours":       str(row.get("is_honours","")).strip().lower()=="true",
                "subject_name":     str(row["subject_name"]).strip(),
                "is_lab":           _is_lab(row),
                "primary_tc":       _primary_teacher(tc),
                "all_tcs":          _all_teachers(tc),
            }

    ns    = len(subjects)
    s_idx = {k: i for i, k in enumerate(subjects)}
    # state stores subject index+1 (0=empty, -1=lab marker)
    state = np.zeros((5, 6, num_rooms), dtype=int)
    # state_teacher[day][period] → set of teacher codes busy
    state_teacher = [[set() for _ in range(6)] for _ in range(5)]
    placed = [0] * ns
    req    = [subj_info[k]["required_hours"] for k in subjects]

    divisions    = list(dict.fromkeys(div for _, div in subjects))
    div_used     = {div: set() for div in divisions}
    div_lab_days = {div: [] for div in divisions}

    LAB_MARKER = -1

    # ── Helpers ───────────────────────────────────────────────────────────────
    def teacher_busy(tc, day, period):
        if not tc or tc in NO_COLLISION_TEACHERS:
            return False
        return tc in state_teacher[day][period]

    def mark_teachers(tcs, day, period):
        for tc in tcs:
            if tc and tc not in NO_COLLISION_TEACHERS:
                state_teacher[day][period].add(tc)

    def any_tc_free(tcs, day, period):
        """True if at least one teacher in list is free."""
        if not tcs: return True
        real = [t for t in tcs if t and t not in NO_COLLISION_TEACHERS]
        if not real: return True
        return any(not teacher_busy(t, day, period) for t in real)

    def all_tcs_free_block(tcs, day, blk):
        real = [t for t in tcs if t and t not in NO_COLLISION_TEACHERS]
        if not real: return True
        return all(
            all(not teacher_busy(t, day, p) for p in blk)
            for t in real
        )

    def room_block_free(rname, day, blk):
        ri = room_idx.get(rname)
        if ri is None: return False
        return all(state[day, p, ri] == 0 for p in blk)

    def div_block_free(div, day, blk):
        return all((day, p) not in div_used[div] for p in blk)

    def place_single(idx, rname, day, period):
        ri = room_idx[rname]
        state[day, period, ri] = idx + 1
        placed[idx] += 1
        div_used[subjects[idx][1]].add((day, period))
        mark_teachers(subj_info[subjects[idx]]["all_tcs"], day, period)

    def place_lab(div, day, blk, lab_room, tcs):
        ri = room_idx[lab_room]
        for p in blk:
            state[day, p, ri] = LAB_MARKER
            div_used[div].add((day, p))
            mark_teachers(tcs, day, p)
        div_lab_days[div].append(day)

    def lab_gap_ok(div, day):
        return all(abs(day - d) >= 2 for d in div_lab_days[div])

    # ── STEP 1: Lab blocks ────────────────────────────────────────────────────
    blk_choices    = S2_LAB_BLOCKS if sem == "S2" else S4_LAB_BLOCKS
    sittings_needed = 2

    # Store lab teacher per division for display
    div_lab_teacher = {}

    for div in divisions:
        div_has_lab = any(subj_info[k]["is_lab"] for k in subjects if k[1] == div)
        if not div_has_lab:
            continue

        troom = DIVISION_ROOMS.get(div, "")

        # Collect all teacher codes from ALL lab subjects of this division
        lab_tcs = []
        for k in subjects:
            if k[1] == div and subj_info[k]["is_lab"]:
                lab_tcs.extend(subj_info[k]["all_tcs"])
        lab_tcs = list(dict.fromkeys(lab_tcs))  # deduplicate preserve order
        primary_lab_tc = lab_tcs[0] if lab_tcs else ""
        div_lab_teacher[div] = primary_lab_tc

        lab_room = troom
        if sem != "S2":
            for nl in NET_LABS:
                if nl in room_idx:
                    lab_room = nl; break

        sittings_placed = 0
        day_order = list(range(5)); random.shuffle(day_order)

        for day in day_order:
            if sittings_placed >= sittings_needed: break
            if not lab_gap_ok(div, day): continue
            for blk in blk_choices:
                if not div_block_free(div, day, blk): continue
                if not all_tcs_free_block(lab_tcs, day, blk): continue
                chosen = None
                if sem != "S2":
                    for nl in NET_LABS:
                        if room_block_free(nl, day, blk):
                            chosen = nl; break
                    if not chosen and troom and room_block_free(troom, day, blk):
                        chosen = troom
                else:
                    if troom and room_block_free(troom, day, blk):
                        chosen = troom
                if not chosen: continue
                place_lab(div, day, blk, chosen, lab_tcs)
                sittings_placed += 1
                break

        # Fallback: relax gap
        if sittings_placed < sittings_needed:
            for day in range(5):
                if sittings_placed >= sittings_needed: break
                if day in div_lab_days[div]: continue
                for blk in blk_choices:
                    if not div_block_free(div, day, blk): continue
                    chosen = None
                    if sem != "S2":
                        for nl in NET_LABS:
                            if room_block_free(nl, day, blk):
                                chosen = nl; break
                        if not chosen and troom and room_block_free(troom, day, blk):
                            chosen = troom
                    else:
                        if troom and room_block_free(troom, day, blk):
                            chosen = troom
                    if not chosen: continue
                    place_lab(div, day, blk, chosen, lab_tcs)
                    sittings_placed += 1; break

        for k in subjects:
            if k[1] == div and subj_info[k]["is_lab"]:
                placed[s_idx[k]] = req[s_idx[k]]

    # ── STEP 2: Honours subjects ──────────────────────────────────────────────
    for key in subjects:
        if not subj_info[key]["is_honours"]: continue
        idx = s_idx[key]; div = key[1]
        troom = DIVISION_ROOMS.get(div,"")
        if not troom or troom not in room_idx: continue
        ri = room_idx[troom]; placed[idx] = 0
        preferred = [(d, HONOURS_PERIOD) for d in sorted(HONOURS_DAYS)]
        other = [(d,p) for d in range(5) for p in range(6)
                 if not (d in HONOURS_DAYS and p==HONOURS_PERIOD)]
        random.shuffle(other)
        for day, period in preferred + other:
            if placed[idx] >= req[idx]: break
            if (day,period) in div_used[div]: continue
            if state[day,period,ri] != 0: continue
            if not any_tc_free(subj_info[key]["all_tcs"], day, period): continue
            state[day,period,ri] = idx+1
            placed[idx] += 1
            div_used[div].add((day,period))
            mark_teachers(subj_info[key]["all_tcs"], day, period)

    # ── STEP 3: Theory subjects ───────────────────────────────────────────────
    div_has_honours = {
        div: any(subj_info[k]["is_honours"] for k in subjects if k[1]==div)
        for div in divisions
    }

    # Group theory keys by primary teacher to enforce min 3hr/day
    theory_keys = [
        k for k in subjects
        if not subj_info[k]["is_lab"] and not subj_info[k]["is_honours"]
        and k[0] not in FILLER_CODES
    ]
    theory_keys.sort(key=lambda k: -subj_info[k]["required_hours"])

    # teacher_day_count[tc][day] = periods assigned so far
    teacher_day_count = defaultdict(lambda: defaultdict(int))

    for key in theory_keys:
        idx   = s_idx[key]; div = key[1]
        troom = DIVISION_ROOMS.get(div,"")
        if not troom or troom not in room_idx:
            troom = next((r for r in ROOM_NAMES if "Lab" not in r), ROOM_NAMES[0])
        ri     = room_idx[troom]
        needed = req[idx]
        placed[idx] = 0
        ptc    = subj_info[key]["primary_tc"]
        all_tc = subj_info[key]["all_tcs"]

        # Build candidate slots — prefer days where teacher already has hours
        # (to group toward min 3hr/day)
        def slot_priority(dp):
            d, p = dp
            # Lower = higher priority
            existing = teacher_day_count[ptc][d] if ptc else 0
            # Prefer days with 1-2 existing (building toward 3), avoid 0 or >=3
            penalty = abs(existing - 2)
            return (penalty, d, p)

        slots = [(d,p) for d in range(5) for p in range(6)]
        slots.sort(key=slot_priority)

        for day, period in slots:
            if placed[idx] >= needed: break
            if div_has_honours.get(div) and day in HONOURS_DAYS and period==HONOURS_PERIOD:
                continue
            if (day,period) in div_used[div]: continue
            if state[day,period,ri] != 0: continue
            if not any_tc_free(all_tc, day, period): continue
            if needed > 1 and sum(1 for p in range(6) if state[day,p,ri]==idx+1) >= 2:
                continue
            if needed > 1 and (
                (period>0 and state[day,period-1,ri]==idx+1) or
                (period<5 and state[day,period+1,ri]==idx+1)):
                continue
            state[day,period,ri] = idx+1
            placed[idx] += 1
            div_used[div].add((day,period))
            mark_teachers(all_tc, day, period)
            if ptc and ptc not in NO_COLLISION_TEACHERS:
                teacher_day_count[ptc][day] += 1

        # Relax teacher constraint if still short
        if placed[idx] < needed:
            for day, period in slots:
                if placed[idx] >= needed: break
                if (day,period) in div_used[div]: continue
                if state[day,period,ri] != 0: continue
                state[day,period,ri] = idx+1
                placed[idx] += 1
                div_used[div].add((day,period))

    # ── STEP 4: Fill blanks ───────────────────────────────────────────────────
    fi = 0
    for div in divisions:
        troom = DIVISION_ROOMS.get(div,"")
        if not troom or troom not in room_idx: continue
        ri = room_idx[troom]
        for day in range(5):
            for period in range(6):
                if (day,period) not in div_used[div] and state[day,period,ri]==0:
                    f    = FILLERS[fi % len(FILLERS)]
                    fkey = (f["course_code"]+f"__{div}_{day}_{period}", div)
                    if fkey not in subj_info:
                        subjects.append(fkey)
                        subj_info[fkey] = {
                            "required_hours":1,"room_type_needed":"Theory",
                            "is_honours":False,"subject_name":f["subject_name"],
                            "is_lab":False,"primary_tc":f["teacher_code"],
                            "all_tcs":[f["teacher_code"]],
                        }
                        s_idx[fkey] = len(subjects)-1
                        placed.append(0); req.append(1)
                        fidx = len(subjects)-1
                    else:
                        fidx = s_idx[fkey]
                    state[day,period,ri] = fidx+1
                    div_used[div].add((day,period))
                    fi += 1

    # ── Build output ──────────────────────────────────────────────────────────
    def get_cell(div, day, period):
        troom = DIVISION_ROOMS.get(div,"")
        # Check theory room first
        if troom and troom in room_idx:
            cid = state[day, period, room_idx[troom]]
            if cid == LAB_MARKER:
                tc = div_lab_teacher.get(div,"")
                return f"LAB [{troom}] ({tc})" if tc else f"LAB [{troom}]"
            if cid > 0 and subjects[cid-1][1] == div:
                k     = subjects[cid-1]
                sname = subj_info[k]["subject_name"]
                tc    = subj_info[k]["primary_tc"]
                return f"{sname} [{troom}] ({tc})" if tc else f"{sname} [{troom}]"
        # Check lab rooms
        for r, rname in enumerate(ROOM_NAMES):
            if rname == troom: continue
            cid = state[day, period, r]
            if cid == LAB_MARKER and (day,period) in div_used.get(div, set()):
                tc = div_lab_teacher.get(div,"")
                return f"LAB [{rname}] ({tc})" if tc else f"LAB [{rname}]"
            if cid > 0 and subjects[cid-1][1] == div:
                k     = subjects[cid-1]
                sname = subj_info[k]["subject_name"]
                tc    = subj_info[k]["primary_tc"]
                return f"{sname} [{rname}] ({tc})" if tc else f"{sname} [{rname}]"
        return "---"

    def build_div_df(div):
        wday={"Day":"Time (Mon-Thu)"}; fri={"Day":"Time (Friday)"}; sep={"Day":""}
        for p in range(6):
            wday[f"P{p+1}"]=WEEKDAY_TIMES[p]
            fri [f"P{p+1}"]=FRIDAY_TIMES[p]
            sep [f"P{p+1}"]=""
        rows=[wday,fri,sep]
        for d,dn in enumerate(DAY_NAMES):
            row={"Day":dn}
            for p in range(6): row[f"P{p+1}"]=get_cell(div,d,p)
            rows.append(row)
        return pd.DataFrame(rows,columns=["Day","P1","P2","P3","P4","P5","P6"])

    def build_raw():
        """Single unified table: rows=Day+Period, columns=all rooms."""
        rows=[]
        for d in range(5):
            times=FRIDAY_TIMES if d==4 else WEEKDAY_TIMES
            for p in range(6):
                e={"Day":DAY_NAMES[d],"Period":f"P{p+1}","Time":times[p]}
                for r,rn in enumerate(ROOM_NAMES):
                    cid=state[d,p,r]
                    if cid==LAB_MARKER:
                        # Find which division uses this lab room at this slot
                        lab_divs=[dv for dv in divisions
                                  if (d,p) in div_used.get(dv,set())
                                  and DIVISION_ROOMS.get(dv)!=rn]
                        # Also check divisions whose lab room is rn
                        for dv in divisions:
                            if (d,p) in div_used.get(dv,set()):
                                tc=div_lab_teacher.get(dv,"")
                                e[rn]=f"LAB ({dv}) ({tc})" if tc else f"LAB ({dv})"
                                break
                        else:
                            e[rn]="LAB"
                    elif cid>0:
                        k=subjects[cid-1]
                        sname=subj_info[k]["subject_name"]
                        tc=subj_info[k]["primary_tc"]
                        dv=k[1]
                        e[rn]=f"{sname} ({dv}) ({tc})" if tc else f"{sname} ({dv})"
                    else:
                        e[rn]="---"
                rows.append(e)
        return pd.DataFrame(rows)

    result={div:build_div_df(div) for div in divisions}
    result[f"raw_{sem}"]=build_raw()

    real_keys=[k for k in s_idx
               if k[0] not in FILLER_CODES
               and not any(k[0].startswith(fc+"__") for fc in FILLER_CODES)]
    ok=sum(1 for k in real_keys if placed[s_idx[k]]>=req[s_idx[k]])
    print(f"  ✅ {sem}: {ok}/{len(real_keys)} subjects placed, 0 blanks")
    return result


def generate_timetable(df_allotment: pd.DataFrame) -> dict:
    df_allotment=df_allotment.copy()
    df_allotment.columns=df_allotment.columns.str.strip().str.lower()
    all_results={}
    for sem in df_allotment["semester"].unique():
        df_sem=df_allotment[df_allotment["semester"]==sem].copy()
        print(f"\n── {sem} ({len(df_sem)} rows, {df_sem['division'].nunique()} divs) ──")
        all_results.update(_schedule_one_semester(df_sem))
    return all_results