import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Upload Data", layout="wide")

st.title("📂 Upload MEC Timetable Data")
st.markdown("Upload all 3 CSV files below, then click **Generate Timetable**.")

# ── Download sample files ─────────────────────────────────────────────────────
with st.expander("📥 Download Sample CSV Templates"):
    col1, col2, col3 = st.columns(3)

    sample_subjects = """course_code,subject_name,teacher_code,division,semester,required_hours,room_type_needed,is_honours
CST302,Compiler Design,APR,CS6A,S6,4,Theory,False
CST304,CGIP,LMS,CS6A,S6,4,Theory,False"""

    sample_rooms = """room_id,room_name,room_type,division_allowed
1,B202,Theory,CS6A
2,B302,Theory,CS6B"""

    sample_teachers = """teacher_code,teacher_name,designation
APR,Ms. Aparna M,Asst. Prof
LMS,Ms. Lekshmi Subha M S,Asst. Prof"""

    col1.download_button("⬇ subjects_template.csv",
                         sample_subjects, "subjects_template.csv", "text/csv")
    col2.download_button("⬇ rooms_template.csv",
                         sample_rooms, "rooms_template.csv", "text/csv")
    col3.download_button("⬇ teachers_template.csv",
                         sample_teachers, "teachers_template.csv", "text/csv")

st.divider()

# ── Upload sections ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📚 Subjects CSV")
    subjects_file = st.file_uploader("Upload subjects.csv", type=["csv"],
                                     key="subjects")
    if subjects_file:
        df_sub = pd.read_csv(subjects_file)
        required_cols = {"course_code", "subject_name", "teacher_code",
                         "division", "semester", "required_hours",
                         "room_type_needed", "is_honours"}
        missing = required_cols - set(df_sub.columns.str.lower())
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            st.success(f"✅ {len(df_sub)} subjects loaded")
            st.dataframe(df_sub, use_container_width=True, height=200)

with col2:
    st.subheader("🏫 Rooms CSV")
    rooms_file = st.file_uploader("Upload rooms.csv", type=["csv"],
                                  key="rooms")
    if rooms_file:
        df_rooms = pd.read_csv(rooms_file)
        required_cols = {"room_id", "room_name", "room_type", "division_allowed"}
        missing = required_cols - set(df_rooms.columns.str.lower())
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            st.success(f"✅ {len(df_rooms)} rooms loaded")
            st.dataframe(df_rooms, use_container_width=True, height=200)

with col3:
    st.subheader("👩‍🏫 Teachers CSV")
    teachers_file = st.file_uploader("Upload teachers.csv", type=["csv"],
                                     key="teachers")
    if teachers_file:
        df_teachers = pd.read_csv(teachers_file)
        required_cols = {"teacher_code", "teacher_name", "designation"}
        missing = required_cols - set(df_teachers.columns.str.lower())
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            st.success(f"✅ {len(df_teachers)} teachers loaded")
            st.dataframe(df_teachers, use_container_width=True, height=200)

st.divider()

# ── Generate button ───────────────────────────────────────────────────────────
all_uploaded = subjects_file and rooms_file and teachers_file

if not all_uploaded:
    missing_files = []
    if not subjects_file:  missing_files.append("Subjects")
    if not rooms_file:     missing_files.append("Rooms")
    if not teachers_file:  missing_files.append("Teachers")
    st.warning(f"⚠️  Still needed: **{', '.join(missing_files)}**")

if st.button("🚀 Generate Timetable", disabled=not all_uploaded,
             type="primary", use_container_width=True):

    with st.spinner("⏳ Generating timetable — this may take 10–30 seconds..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/generate",
                files={
                    "subjects_file": (
                        "subjects.csv",
                        subjects_file.getvalue(),
                        "text/csv"
                    ),
                    "rooms_file": (
                        "rooms.csv",
                        rooms_file.getvalue(),
                        "text/csv"
                    ),
                    "teachers_file": (
                        "teachers.csv",
                        teachers_file.getvalue(),
                        "text/csv"
                    ),
                }
            )

            if response.status_code == 200:
                result = response.json()

                if "error" in result:
                    st.error(f"❌ Backend Error: {result['error']}")
                else:
                    st.success("✅ Timetable Generated Successfully!")
                    st.session_state["timetable_result"] = result
                    st.info("👉 Go to **Timetable Viewer** page to see the full timetable.")

                    # Quick preview
                    st.subheader("📅 Quick Preview")
                    tabs = st.tabs(["CS6A", "CS6B", "CS6C", "Full (All Rooms)"])
                    for i, div in enumerate(["CS6A", "CS6B", "CS6C", "raw"]):
                        with tabs[i]:
                            if div in result:
                                st.dataframe(
                                    pd.DataFrame(result[div]),
                                    use_container_width=True
                                )
                            else:
                                st.info("No data for this division.")
            else:
                st.error(f"❌ Backend returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure `api.py` is running:\n\n"
                     "```\nuvicorn api:app --reload\n```")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")