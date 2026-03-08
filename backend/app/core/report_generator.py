from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import pandas as pd
from ..db.models import History

def generate_pdf_report(records: list[History], username: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, f"LensFlow Analysis Report for {username}")

    # Watermark
    c.saveState()
    c.setFont("Helvetica", 60)
    c.setFillAlpha(0.1)
    c.rotate(45)
    c.drawString(3 * inch, 3 * inch, "LensFlow AI")
    c.restoreState()

    # Table Header
    y = height - 2 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Time")
    c.drawString(3 * inch, y, "Category")
    c.drawString(5 * inch, y, "Title")
    
    y -= 20
    c.line(1 * inch, y + 10, 7.5 * inch, y + 10)

    # Content
    c.setFont("Helvetica", 10)
    for record in records:
        if y < 1 * inch:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            y = height - 1 * inch
            c.drawString(1 * inch, y, "Time")
            c.drawString(3 * inch, y, "Category")
            c.drawString(5 * inch, y, "Title")
            y -= 20
        
        c.drawString(1 * inch, y, str(record.timestamp))
        c.drawString(3 * inch, y, record.category)
        c.drawString(5 * inch, y, record.title[:30] + "..." if len(record.title) > 30 else record.title)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

def generate_excel_report(records: list[History]) -> BytesIO:
    data = []
    for r in records:
        data.append({
            "Timestamp": r.timestamp,
            "Category": r.category,
            "Title": r.title,
            "Summary": r.summary
        })
    
    buffer = BytesIO()
    # Use context manager for ExcelWriter
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='History')
    
    buffer.seek(0)
    return buffer
