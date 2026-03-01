from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import traceback
from generator import generate_timetable

app = FastAPI(title="MEC Timetable AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MEC Timetable AI Backend Running 🚀"}


@app.post("/generate")
async def generate(
    subjects_file: UploadFile = File(...),
    rooms_file:    UploadFile = File(...),
    teachers_file: UploadFile = File(...),
):
    try:
        df_subjects  = pd.read_csv(BytesIO(await subjects_file.read()))
        df_rooms     = pd.read_csv(BytesIO(await rooms_file.read()))
        df_teachers  = pd.read_csv(BytesIO(await teachers_file.read()))

        df_subjects.columns  = df_subjects.columns.str.strip().str.lower()
        df_rooms.columns     = df_rooms.columns.str.strip().str.lower()
        df_teachers.columns  = df_teachers.columns.str.strip().str.lower()

        print(f"✅ Received: {len(df_subjects)} subjects, "
              f"{len(df_rooms)} rooms, {len(df_teachers)} teachers")

        result = generate_timetable(df_subjects, df_rooms, df_teachers)

        # Serialise — fill NaN with "---" before converting to dict
        serialised = {}
        for key, df in result.items():
            clean = df.fillna("---").astype(str)
            # Reset index so Day column is included for division tables
            if key != "raw":
                clean = clean.reset_index()
            serialised[key] = clean.to_dict(orient="list")

        return serialised

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}