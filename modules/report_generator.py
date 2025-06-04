# modules/report_generator.py

from fpdf import FPDF
import os
from datetime import datetime

class StyledPDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.set_text_color(40, 40, 90)
        self.cell(0, 10, "AI Mock Interview Report", ln=True, align='C')
        self.ln(10)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 9)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_pdf_report(path, category, results, transcript=""):
    pdf = StyledPDF()
    pdf.add_page()

    # Metadata
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Category: {category}", ln=True)
    pdf.ln(10)

    # Scores
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(33, 33, 33)
    pdf.cell(0, 10, f"Overall Score: {results.get('overall', 0)}/10", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_fill_color(240, 240, 255)
    pdf.ln(5)

    for label in ["fluency", "vocabulary", "confidence", "structure", "factual"]:
        score = results.get(label, 0)
        pdf.cell(50, 8, f"{label.capitalize()}:", 0, 0)
        bar_width = (score / 10.0) * 100
        pdf.set_fill_color(80, 130, 250)
        pdf.cell(bar_width, 8, '', 0, 1, fill=True)
        pdf.set_fill_color(240, 240, 255)

    # Feedback
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(40, 60, 90)
    pdf.cell(0, 10, "Feedback & Suggestions", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0)
    pdf.multi_cell(0, 10, results.get("feedback", "No feedback available."))

    # Transcript
    if transcript.strip():
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(40, 60, 90)
        pdf.cell(0, 10, "Transcript", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 8, transcript.strip())

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return path
