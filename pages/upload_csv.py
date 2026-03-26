import streamlit as st
import pandas as pd
import requests
from copy import deepcopy

st.set_page_config(page_title="Upload Data", layout="wide")
st.title("📂 Upload MEC Subject Allotment CSV")
st.markdown("Upload the **single combined CSV** to generate timetables for all semesters.")

with st.expander("📥 Download CSV Template"):
    sample = """course_code,subject_name,teacher_code,division,semester,required_hours,room_type_needed,is_honours,scheme
CHEM,CHEM,NGP,C2A,S2,4,Theory,False,
CHEM_LAB_ITWS,CHEM LAB/ITWS,NGP,C2A,S2,2,Lab,False,
OS_LAB_DBMS_LA,OS LAB/DBMS LAB,JJP,C4A,S4,2,Lab,False,
CST302,CD,APR,C6A,S6,4,Theory,False,3+1+0"""
    st.download_button("⬇ Download Template", sample, "template.csv", "text/csv")

st.divider()

uploaded = st.file_uploader("Upload SubAllotment CSV", type=["csv"])

REQUIRED = {"course_code","subject_name","teacher_code","division",
            "semester","required_hours","room_type_needed","is_honours"}

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

def is_lab_subject(row):
    n = str(row.get("subject_name","")).upper()
    c = str(row.get("course_code","")).upper()
    return ("LAB" in n or "LAB" in c or "W/S" in n or "ITWS" in n or "ITWS" in c)

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip().str.lower()
    missing = REQUIRED - set(df.columns)

    if missing:
        st.error(f"❌ Missing columns: {missing}")
    else:
        # Fix room_type: Theory→Lab for lab subjects, Lab_Network→Lab
        df["room_type_needed"] = df.apply(
            lambda r: "Lab" if (is_lab_subject(r) and r["room_type_needed"]=="Theory")
                      else ("Lab" if r["room_type_needed"]=="Lab_Network"
                      else r["room_type_needed"]),
            axis=1
        )

        # Pad divisions to 30 hours with fillers
        extras = []
        for div in df["division"].unique():
            sem   = df[df["division"]==div]["semester"].iloc[0]
            total = df[df["division"]==div]["required_hours"].sum()
            fi    = 0
            while total < 30:
                f = deepcopy(FILLERS[fi % len(FILLERS)])
                f["division"] = div
                f["semester"] = sem
                extras.append(f)
                total += 1
                fi    += 1
        if extras:
            df = pd.concat([df, pd.DataFrame(extras)], ignore_index=True)
            st.info(f"ℹ️ Added {len(extras)} filler slots to eliminate blank periods.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Semesters", df["semester"].nunique())
        col3.metric("Divisions", df["division"].nunique())

        all_sems = sorted(df["semester"].unique().tolist())
        selected = st.multiselect("Select semesters:", all_sems, default=all_sems)

        sem_tabs = st.tabs(all_sems)
        for tab, sem in zip(sem_tabs, all_sems):
            with tab:
                st.dataframe(df[df["semester"]==sem], use_container_width=True, height=200)

        st.divider()

        if st.button("🚀 Generate Timetable", type="primary",
                     use_container_width=True, disabled=not selected):
            with st.spinner("⏳ Generating..."):
                try:
                    cleaned_bytes = df.to_csv(index=False).encode()
                    resp = requests.post(
                        "http://127.0.0.1:8000/generate",
                        files={"allotment_file": ("allotment.csv", cleaned_bytes, "text/csv")},
                        data={"semesters": ",".join(selected)}
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ Timetables Generated!")
                            st.session_state["timetable_result"] = result
                            div_keys = sorted([k for k in result if not k.startswith("raw")])
                            raw_keys = [k for k in result if k.startswith("raw")]
                            tabs = st.tabs(div_keys + ["📋 Full (All Rooms)"])
                            for i, div in enumerate(div_keys):
                                with tabs[i]:
                                    st.dataframe(pd.DataFrame(result[div]), use_container_width=True)
                            with tabs[-1]:
                                raw_tabs = st.tabs(raw_keys) if raw_keys else []
                                for rt, rk in zip(raw_tabs, raw_keys):
                                    with rt:
                                        st.dataframe(pd.DataFrame(result[rk]), use_container_width=True)
                    else:
                        st.error(f"❌ Status {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not running.\n```\nuvicorn api:app --reload\n```")
                except Exception as e:
                    st.error(f"❌ {e}")