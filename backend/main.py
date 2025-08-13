from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from omr_generator import generate_omr
import os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/generate-omr")
def generate_omr_api(
    institute_name: str = Query(...),
    total_questions: int = Query(...),
    options_per_question: int = Query(...)
):
    file_path = generate_omr(institute_name, total_questions, options_per_question)
    return FileResponse(file_path, media_type="application/pdf", filename="omr_sheet.pdf")
