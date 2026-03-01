import streamlit as st
import requests
import pandas as pd
import random

st.title("📅 Timetable Generator")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def generate_colors(subjects):
    colors = {}
    for sub in subjects:
        colors[sub] = f"background-color: #{random.randint(0, 0xFFFFFF):06x}"
    return colors

def style_timetable(df):
    subjects = pd.unique(df.values.ravel())
    subjects = [s for s in subjects if s != ""]
    color_map = generate_colors(subjects)

    def color_cells(val):
        if val in color_map:
            return color_map[val]
        return ""

    return df.style.applymap(color_cells)

if uploaded_file is not None:
    if st.button("Generate Timetable"):

        files = {"file": uploaded_file.getvalue()}

        response = requests.post(
            "http://127.0.0.1:8000/generate",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:
            result = response.json()
            st.success("Timetable Generated!")

            for semester, timetable in result.items():
                st.subheader(f"Semester {semester}")

                df = pd.DataFrame(timetable)
                styled_df = style_timetable(df)

                st.dataframe(styled_df, use_container_width=True)

        else:
            st.error("Failed to generate timetable")