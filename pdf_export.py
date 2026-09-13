"""
pdf_export.py
-------------
Renders any register (list of dicts) into a printable PDF table and/or CSV,
saved to the device's Downloads-equivalent folder so the user can open it
with any PDF/print app on the phone.
"""

import os
import csv
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

try:
    from android.storage import primary_external_storage_path  # type: ignore
    EXPORT_DIR = os.path.join(primary_external_storage_path(), "Download", "EcoShopRegisters")
except Exception:
    # Fallback for desktop testing
    EXPORT_DIR = os.path.join(os.path.expanduser("~"), "EcoShopRegisters")

os.makedirs(EXPORT_DIR, exist_ok=True)


def _timestamped_name(title, ext):
    safe = title.replace(" ", "_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe}_{stamp}.{ext}"


def export_to_pdf(title, headers, rows, subtitle=""):
    """
    headers: list[str]
    rows: list[list] (already formatted strings/numbers, same order as headers)
    Returns the saved file path.
    """
    filepath = os.path.join(EXPORT_DIR, _timestamped_name(title, "pdf"))
    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4),
                             leftMargin=1 * cm, rightMargin=1 * cm,
                             topMargin=1 * cm, bottomMargin=1 * cm)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Anamalai Tiger Reserve — Eco Shop", styles["Title"]),
        Paragraph(title, styles["Heading2"]),
    ]
    if subtitle:
        elements.append(Paragraph(subtitle, styles["Normal"]))
    elements.append(Spacer(1, 0.4 * cm))

    data = [headers] + rows
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F8E9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(table)
    doc.build(elements)
    return filepath


def export_to_csv(title, headers, rows):
    filepath = os.path.join(EXPORT_DIR, _timestamped_name(title, "csv"))
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return filepath
