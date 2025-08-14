from fastapi import FastAPI, Query, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from pathlib import Path
import math
import os
import uuid
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

LOG = logging.getLogger("uvicorn.error")

FONT_NAME = "Bangla"
FONT_FILENAME = "SolaimanLipi.ttf"

def _register_font_if_exists(base_path: Path):
    font_path = base_path / FONT_FILENAME
    if font_path.exists():
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
            return True
        except Exception as e:
            LOG.exception("Font registration failed: %s", e)
            return False
    return False

def _generate_pdf(file_path: str, institute_name: str, total_questions: int, options_per_question: int, use_bangla: bool):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 40, institute_name)

    questions_per_col = math.ceil(total_questions / 4)
    col_width = width / 4
    start_y = height - 80

    if use_bangla:
        option_letters = ["ক", "খ", "গ", "ঘ", "ঙ", "চ"][:options_per_question]
        c.setFont(FONT_NAME if pdfmetrics.getRegisteredFontNames() and FONT_NAME in pdfmetrics.getRegisteredFontNames() else "Helvetica", 10)
    else:
        option_letters = ["A", "B", "C", "D", "E", "F"][:options_per_question]
        c.setFont("Helvetica", 10)

    for q in range(total_questions):
        col = q // questions_per_col
        row = q % questions_per_col
        x_start = col * col_width + 20
        y_pos = start_y - (row * 15)

        c.setFillColor(colors.black)
        c.drawString(x_start, y_pos, f"{q+1}.")

        for i, letter in enumerate(option_letters):
            cx = x_start + 30 + (i * 18)
            cy = y_pos + 3
            c.setStrokeColor(colors.red)
            c.setFillColor(colors.white)
            c.circle(cx, cy, 6, stroke=1, fill=1)

            c.setFillColor(colors.black)
            c.drawCentredString(cx, cy - 3, letter)

    c.save()

def _remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        LOG.exception("Failed to remove temporary file: %s", path)

@app.get("/generate-omr")
def generate_omr_api(
    background: BackgroundTasks,
    institute_name: str = Query(...),
    total_questions: int = Query(..., ge=1),
    options_per_question: int = Query(..., ge=2, le=6),
    use_bangla: bool = Query(False)
):
    tmp_dir = Path("/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_file = tmp_dir / f"omr_{uuid.uuid4().hex}.pdf"

    base_path = Path(__file__).parent
    _register_font_if_exists(base_path)

    try:
        _generate_pdf(str(out_file), institute_name, int(total_questions), int(options_per_question), bool(use_bangla))
    except Exception as e:
        LOG.exception("PDF generation failed: %s", e)
        raise HTTPException(status_code=500, detail="PDF generation failed")

    background.add_task(_remove_file, str(out_file))
    return FileResponse(str(out_file), media_type="application/pdf", filename="omr_sheet.pdf")
