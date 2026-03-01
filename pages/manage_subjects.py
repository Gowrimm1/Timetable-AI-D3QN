import streamlit as st
from storage import add_subject, get_all_subjects, get_all_teachers

st.title("📚 Manage Subjects")

teachers_df = get_all_teachers()

if teachers_df.empty:
    st.warning("Please add teachers first.")
else:
    st.markdown("### Add New Subject")

    col1, col2, col3 = st.columns(3)

    with col1:
        subject_name = st.text_input("Subject Name")

    with col2:
        semester = st.number_input("Semester", min_value=1, max_value=8, step=1)

    with col3:
        hours = st.number_input("Total Weekly Hours", min_value=1, step=1)

    col4, col5, col6 = st.columns(3)

    with col4:
        is_lab = st.selectbox("Is Lab?", ["No", "Yes"])

    with col5:
        lab_hours = st.number_input("Continuous Lab Hours", min_value=0, step=1)

    with col6:
        teacher_name = st.selectbox("Select Teacher", teachers_df["name"])

    if st.button("Add Subject"):
        teacher_id = int(
            teachers_df[teachers_df["name"] == teacher_name]["id"].values[0]
        )

        add_subject(subject_name, semester, hours, is_lab, lab_hours, teacher_id)
        st.success("Subject added successfully!")

st.markdown("---")
st.markdown("### Existing Subjects")

subjects_df = get_all_subjects()

if subjects_df.empty:
    st.info("No subjects added yet.")
else:
    st.dataframe(subjects_df, use_container_width=True)