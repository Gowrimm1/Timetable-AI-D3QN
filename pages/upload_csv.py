import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Upload Data", layout="wide")

st.title("📂 Upload CSV File")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)

        st.success("File uploaded successfully!")
        st.subheader("📊 Data Preview")
        st.dataframe(df, use_container_width=True)

        # Send to backend
        if st.button("🚀 Send to AI Generator"):
            with st.spinner("Sending data to backend..."):

                response = requests.post(
                    "http://127.0.0.1:8000/generate",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "text/csv"
                        )
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Timetable Generated Successfully!")
                    st.subheader("📅 Generated Timetable")

                    # Debug: show raw response
                    # st.write(result)

                    for semester, timetable in result.items():
                        st.write(f"### Semester {semester}")

                        st.write("Raw data received:")
                        st.write(timetable)

                        if isinstance(timetable, list):
                            timetable_df = pd.DataFrame(timetable)
                            st.dataframe(timetable_df, use_container_width=True)
                        else:
                            st.error("Returned data is not in expected format.")

                else:
                    st.error(f"❌ Backend Error: {response.status_code}")

    except Exception as e:
        st.error(f"Error reading file: {e}")