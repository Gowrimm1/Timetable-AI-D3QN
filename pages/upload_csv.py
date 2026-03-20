import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Upload Data", layout="wide")
st.title("📂 Upload MEC Subject Allotment CSV")
st.markdown("Upload the **single combined CSV** to generate timetables for all semesters.")

with st.expander("📥 Download CSV Template"):
    sample = """course_code,subject_name,teacher_code,all_teachers,division,semester,required_hours,room_type_needed,is_honours,scheme
CST302,CD,APR,APR,CS6A,S6,4,Theory,False,3+1+0
CSL332,N/W LAB,MDL,MDL,CS6A,S6,3,Lab_Network,False,0+0+3
CSD334,MPROJ,AFM,AFM,CS6A,S6,3,Lab_Project,False,0+0+3"""
    st.download_button("⬇ Download Template", sample,
                       "template.csv", "text/csv")

st.divider()

uploaded = st.file_uploader("Upload SubAllotment CSV", type=["csv"])

REQUIRED = {"course_code","subject_name","teacher_code","division",
            "semester","required_hours","room_type_needed","is_honours"}

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip().str.lower()
    missing = REQUIRED - set(df.columns)

    if missing:
        st.error(f"❌ Missing columns: {missing}")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Semesters", df["semester"].nunique())
        col3.metric("Divisions", df["division"].nunique())

        all_sems = sorted(df["semester"].unique().tolist())
        selected = st.multiselect("Select semesters:", all_sems, default=all_sems)

        sem_tabs = st.tabs(all_sems)
        for tab, sem in zip(sem_tabs, all_sems):
            with tab:
                st.dataframe(df[df["semester"]==sem],
                             use_container_width=True, height=200)

        st.divider()

        if st.button("🚀 Generate Timetable", type="primary",
                     use_container_width=True, disabled=not selected):
            with st.spinner("⏳ Generating..."):
                try:
                    resp = requests.post(
                        "http://127.0.0.1:8000/generate",
                        files={"allotment_file":(
                            "allotment.csv", uploaded.getvalue(), "text/csv")},
                        data={"semesters": ",".join(selected)}
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ Timetables Generated!")
                            st.session_state["timetable_result"] = result

                            # Separate division tabs from raw tabs
                            div_keys = sorted([k for k in result
                                               if not k.startswith("raw")])
                            raw_keys = [k for k in result if k.startswith("raw")]

                            tabs = st.tabs(div_keys + ["📋 Full (All Rooms)"])
                            for i, div in enumerate(div_keys):
                                with tabs[i]:
                                    st.dataframe(pd.DataFrame(result[div]),
                                                 use_container_width=True)
                            with tabs[-1]:
                                raw_tabs = st.tabs(raw_keys) if raw_keys else []
                                for rt, rk in zip(raw_tabs, raw_keys):
                                    with rt:
                                        st.dataframe(pd.DataFrame(result[rk]),
                                                     use_container_width=True)
                    else:
                        st.error(f"❌ Status {resp.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not running.\n```\nuvicorn api:app --reload\n```")
                except Exception as e:
                    st.error(f"❌ {e}")