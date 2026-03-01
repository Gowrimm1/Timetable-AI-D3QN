import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🏫 Manage Rooms")

if "rooms" not in st.session_state:
    st.session_state.rooms = pd.DataFrame(
        columns=["Room Name", "Capacity"]
    )

st.markdown("### Add New Room")

col1, col2 = st.columns(2)

with col1:
    room_name = st.text_input("Room Name")

with col2:
    capacity = st.number_input("Capacity", 10, 200, 30)

if st.button("Add Room"):
    if room_name:
        new_row = pd.DataFrame([[room_name, capacity]],
                               columns=["Room Name", "Capacity"])
        st.session_state.rooms = pd.concat(
            [st.session_state.rooms, new_row],
            ignore_index=True
        )
        st.success("Room added successfully!")

st.markdown("---")
st.markdown("### Existing Rooms")
st.dataframe(st.session_state.rooms, use_container_width=True)