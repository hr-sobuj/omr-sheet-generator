from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import math
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), "SolaimanLipi.ttf")
pdfmetrics.registerFont(TTFont('Bangla', FONT_PATH))

def generate_omr(institute_name, total_questions, options_per_question, use_bangla=False):
    file_path = "omr_sheet.pdf"
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
        c.setFont("Bangla", 10)
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
    return file_path
