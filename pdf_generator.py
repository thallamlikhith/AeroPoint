"""
pdf_generator.py
Creates a clean PDF report using ReportLab.
Includes:
- AI text report
- Mistake table (CSV)
- Mistake images (frames)
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import os


# ----------------------------------------------------
# Main PDF builder
# ----------------------------------------------------
def create_pdf_report(
        gemini_text: str,
        mistakes_csv: str = None,
        images: list = None,
        output_path: str = "analysis_report.pdf"
):
    """
    Creates a full PDF report combining:
    - AI text (Gemini output)
    - Mistakes table
    - Mistake frame images
    """

    # Template
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>🏸 Badminton AI Analysis Report</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # ----------------------------------------------------
    # 1️⃣ AI Report Text
    # ----------------------------------------------------
    elements.append(Paragraph("<b>AI-Generated Technical Report</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    try:
        with open(gemini_text, "r", encoding="utf-8") as f:
            text = f.read()

        for line in text.split("\n"):
            elements.append(Paragraph(line.replace("•", "- "), styles["BodyText"]))
            elements.append(Spacer(1, 4))

    except Exception as e:
        elements.append(Paragraph(f"Error loading report text: {e}", styles["BodyText"]))

    elements.append(Spacer(1, 20))

    # ----------------------------------------------------
    # 2️⃣ Mistakes Table
    # ----------------------------------------------------
    if mistakes_csv and os.path.exists(mistakes_csv):
        elements.append(Paragraph("<b>Mistake Summary Table</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        df = pd.read_csv(mistakes_csv)

        # Build table
        table_data = [df.columns.tolist()] + df.values.tolist()
        table = Table(table_data)

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
        ]

        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 20))

    # ----------------------------------------------------
    # 3️⃣ Mistake Images
    # ----------------------------------------------------
    if images:
        elements.append(Paragraph("<b>Extracted Mistake Frames</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        for img_path in images:
            if os.path.exists(img_path):
                try:
                    elements.append(Image(img_path, width=350, height=250))
                    elements.append(Spacer(1, 12))
                except Exception as e:
                    elements.append(Paragraph(f"Error loading image {img_path}: {e}", styles["BodyText"]))

    # ----------------------------------------------------
    # Build PDF
    # ----------------------------------------------------
    try:
        doc.build(elements)
        print(f"PDF generated: {output_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")
