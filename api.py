from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import BytesIO
import traceback
from generator import generate_all_timetables

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Timetable AI Backend Running 🚀"}


@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))

        print("✅ CSV received successfully")
        print(df.head())

        # Generate timetable
        result = generate_all_timetables(df)

        print("✅ Generator executed")

        # Convert DataFrames to dictionary (preserve MON/TUE index)
        result_dict = {
            str(sem): timetable.to_dict(orient="index")
            for sem, timetable in result.items()
        }

        return result_dict

    except Exception as e:
        print("❌ ERROR OCCURRED:")
        traceback.print_exc()
        return {"error": str(e)}