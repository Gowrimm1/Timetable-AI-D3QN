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
        # Read locally for preview
        df = pd.read_csv(uploaded_file)

        st.success("File uploaded successfully!")
        st.subheader("📊 Data Preview")
        st.dataframe(df, use_container_width=True)

        if st.button("🚀 Send to AI Generator"):

            with st.spinner("Generating timetable..."):

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

                    # If backend sends error
                    if "error" in result:
                        st.error(f"Backend Error: {result['error']}")
                    else:
                        st.success("✅ Timetable Generated Successfully!")

                        st.subheader("📅 Generated Timetable")

                        for semester, timetable in result.items():

                            st.markdown(f"## Semester {semester}")

                            # Convert properly preserving MON/TUE index
                            timetable_df = pd.DataFrame.from_dict(
                                timetable,
                                orient="index"
                            )

                            st.dataframe(
                                timetable_df,
                                use_container_width=True
                            )

                else:
                    st.error("❌ Failed to connect to backend.")

    except Exception as e:
        st.error(f"Error reading file: {e}")