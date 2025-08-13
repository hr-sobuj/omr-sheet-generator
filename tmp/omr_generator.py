from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import math
import os

# Adjust path if needed
FONT_PATH = os.path.join(os.path.dirname(__file__), "SolaimanLipi.ttf")
# Register Bangla font (ensure the TTF exists)
try:
    pdfmetrics.registerFont(TTFont('Bangla', FONT_PATH))
except Exception as e:
    # If registration fails, print so you know — keep going (but Bangla won't render without font)
    print("Bangla font registration failed:", e)

def to_bangla_numeral(num: int) -> str:
    bn_digits = "০১২৩৪৫৬৭৮৯"
    return "".join(bn_digits[int(d)] for d in str(num))

def generate_omr(institute_name, total_questions, options_per_question, use_bangla=False):
    file_path = "omr_sheet.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 40, institute_name)

    total_columns = 4
    questions_per_col = math.ceil(total_questions / total_columns)
    col_width = width / total_columns
    start_y = height - 80
    row_gap = 20  # increased a bit to avoid overlap

    # Option letters and font for options
    if use_bangla:
        option_letters = ["ক", "খ", "গ", "ঘ", "ঙ", "চ"][:options_per_question]
    else:
        option_letters = ["A", "B", "C", "D", "E", "F"][:options_per_question]

    question_number = 1

    for col in range(total_columns):
        for row in range(questions_per_col):
            if question_number > total_questions:
                break

            x_start = col * col_width + 20
            y_pos = start_y - (row * row_gap)

            # Draw question number: choose font and numeral style
            if use_bangla:
                # If you want Bengali numerals and Bangla font:
                # Ensure Bangla font is registered; if not, fallback to Helvetica
                try:
                    c.setFont("Bangla", 10)
                    q_label = to_bangla_numeral(question_number) + "."
                except:
                    c.setFont("Helvetica", 10)
                    q_label = f"{question_number}."
            else:
                c.setFont("Helvetica", 10)
                q_label = f"{question_number}."

            c.setFillColor(colors.black)
            c.drawString(x_start, y_pos, q_label)

            # Draw option circles and letters (use appropriate font for letters)
            # Keep option letter font consistent: Bangla font for Bengali letters, Helvetica for English.
            for i, letter in enumerate(option_letters):
                cx = x_start + 30 + (i * 24)
                cy = y_pos - 3  # align circles a bit lower

                c.setStrokeColor(colors.red)
                c.setFillColor(colors.white)
                c.circle(cx, cy, 7, stroke=1, fill=1)

                # Draw option letter
                if use_bangla:
                    try:
                        c.setFont("Bangla", 10)
                    except:
                        c.setFont("Helvetica", 10)
                else:
                    c.setFont("Helvetica", 10)

                # center letter vertically inside circle (small y-adjust)
                c.setFillColor(colors.black)
                c.drawCentredString(cx, cy - 3, letter)

            question_number += 1

    c.save()
    return file_path
