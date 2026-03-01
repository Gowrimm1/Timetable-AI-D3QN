import streamlit as st
from storage import add_teacher, get_all_teachers, delete_teacher

st.title("👩‍🏫 Manage Teachers")

st.markdown("### Add New Teacher")

col1, col2 = st.columns(2)

with col1:
    teacher_name = st.text_input("Teacher Name")

with col2:
    department = st.text_input("Department")

if st.button("Add Teacher"):
    if teacher_name.strip() and department.strip():
        add_teacher(teacher_name.strip(), department.strip())
        st.success("Teacher added successfully!")
        st.rerun()
    else:
        st.warning("Please fill all fields.")

st.markdown("---")
st.markdown("### Existing Teachers")

teachers_df = get_all_teachers()

if teachers_df.empty:
    st.info("No teachers added yet.")
else:
    for index, row in teachers_df.iterrows():
        col1, col2, col3, col4 = st.columns([1, 3, 3, 1])

        col1.write(row["id"])
        col2.write(row["name"])
        col3.write(row["department"])

        if col4.button("❌", key=f"delete_{row['id']}"):
            delete_teacher(row["id"])
            st.rerun()