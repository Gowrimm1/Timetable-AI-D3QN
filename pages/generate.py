import streamlit as st

st.set_page_config(layout="wide")

st.title("⚡ Generate Timetable")

if st.button("Generate Timetable"):
    if ("subjects" in st.session_state and
        "teachers" in st.session_state and
        "rooms" in st.session_state and
        not st.session_state.subjects.empty and
        not st.session_state.teachers.empty and
        not st.session_state.rooms.empty):

        st.success("Timetable generated successfully! (Demo Mode)")
        st.session_state.generated = True
    else:
        st.error("Please add Subjects, Teachers and Rooms first.")