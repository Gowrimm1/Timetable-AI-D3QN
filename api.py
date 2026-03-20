from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import traceback
from generator import generate_timetable

app = FastAPI(title="MEC Timetable AI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "MEC Timetable AI Backend Running 🚀"}

@app.post("/generate")
async def generate(
    allotment_file: UploadFile = File(...),
    semesters: str = Form(default="")
):
    try:
        df = pd.read_csv(BytesIO(await allotment_file.read()))
        df.columns = df.columns.str.strip().str.lower()

        if semesters.strip():
            sem_list = [s.strip() for s in semesters.split(",")]
            df = df[df["semester"].isin(sem_list)]

        print(f"✅ {len(df)} rows | Sems: {df['semester'].unique().tolist()}")

        result = generate_timetable(df)

        serialised = {}
        for key, frame in result.items():
            clean = frame.fillna("---").astype(str).reset_index(drop=True)
            serialised[key] = clean.to_dict(orient="list")

        return serialised

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}