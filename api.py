from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import BytesIO
import traceback
from generator import generate_all_timetables

app = FastAPI()

@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))

        print("CSV received successfully")
        print(df.head())

        result = generate_all_timetables(df)

        print("Generator returned:", result)

        result_dict = {
            str(sem): timetable.to_dict(orient="records")
            for sem, timetable in result.items()
        }

        return result_dict

    except Exception as e:
        print("ERROR OCCURRED:")
        traceback.print_exc()
        return {"error": str(e)}