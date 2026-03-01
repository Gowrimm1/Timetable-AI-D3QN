import streamlit as st
from storage import initialize_storage

initialize_storage()

st.set_page_config(
    page_title="AI Timetable ERP",
    layout="wide",
    page_icon="🎓"
)

st.markdown(
    """
    <div style='text-align: center; padding-top: 150px;'>
        <h1 style='font-size: 60px;'>🎓 AI Timetable ERP</h1>
        <p style='font-size: 22px; color: grey;'>
            Intelligent Academic Scheduling System
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("➡ Go to Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")