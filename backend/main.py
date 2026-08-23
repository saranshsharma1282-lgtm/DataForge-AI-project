import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import os
import shutil
from pathlib import Path


app = FastAPI()
app.add_middleware(
CORSMiddleware,
      allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_FOLDER = BASE_DIR / "data"
OUTPUT_FOLDER = BASE_DIR / "output"
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)



app.mount("/static", StaticFiles(directory=OUTPUT_FOLDER),name="static")
@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR /"index.html")


@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):

    # Check file name
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    # Check Excel extension
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid Excel file (.xlsx or .xls)"
        )

    # Create safe filename
    filename = os.path.basename(file.filename)

    input_path = UPLOAD_FOLDER / filename

    # Save uploaded file
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save uploaded file: {str(e)}"
        )

    finally:
        await file.close()

    # Read Excel file
    try:
        df = pd.read_excel(input_path)

    except Exception as e:
        # Remove invalid uploaded file
        if input_path.exists():
            input_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=f"Invalid or corrupted Excel file: {str(e)}"
        )

    # -------------------------
    # DATA CLEANING
    # -------------------------

    # Remove extra spaces from column names
    df.columns = df.columns.astype(str).str.strip()

    # Remove extra spaces from text columns
    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].astype(str).str.strip()

        # Convert "nan" strings back to missing values
        df[column] = df[column].replace("nan", pd.NA)

    # Remove duplicate rows
    before_duplicates = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before_duplicates - len(df)

    # Remove completely empty rows
    before_empty = len(df)
    df = df.dropna(how="all")
    empty_rows_removed = before_empty - len(df)

    # -------------------------
    # SAVE CLEANED FILE
    # -------------------------

    output_filename = f"cleaned_{Path(filename).stem}.xlsx"
    output_path = OUTPUT_FOLDER / output_filename

    try:
        df.to_excel(output_path, index=False, engine="openpyxl")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not create cleaned Excel file: {str(e)}"
        )

    return {
        "message": "Excel file uploaded and cleaned successfully",
        "original_file": filename,
        "cleaned_file": output_filename,
        "total_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "empty_rows_removed": empty_rows_removed,
        "download_url": f"/download/{output_filename}"
    }


@app.get("/download/{filename}")
def download_excel(filename: str):

    # Security: prevent paths like ../../something
    safe_filename = os.path.basename(filename)

    file_path = OUTPUT_FOLDER / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)