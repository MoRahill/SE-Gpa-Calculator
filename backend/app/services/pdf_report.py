"""Builds a downloadable PDF summary of a student's academic progress, for
an advisor to export and keep or share."""

import io

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image


def generate_student_report_pdf(
    student_name: str,
    student_email: str,
    advisor_name: str,
    cumulative_gpa: float,
    degree_progress: dict,
    semesters: list[dict],
    chart_png_bytes: bytes | None = None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=18)
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    elements = []
    elements.append(Paragraph(f"Academic Progress Report: {student_name}", title_style))
    elements.append(Paragraph(f"{student_email} &nbsp;&middot;&nbsp; Advisor: {advisor_name}", normal_style))
    elements.append(Spacer(1, 16))

    # Summary stats table
    summary_data = [
        ["Cumulative GPA", f"{cumulative_gpa:.2f}"],
        ["Credits completed", f"{degree_progress['credits_completed']}"],
        ["Credits required to graduate", f"{degree_progress['credits_required']}"],
        ["Credits remaining", f"{degree_progress['credits_remaining']}"],
        ["Estimated courses remaining", str(degree_progress["courses_remaining_estimate"])],
        ["Estimated semesters remaining", str(degree_progress["semesters_remaining_estimate"])],
    ]
    summary_table = Table(summary_data, colWidths=[2.8 * inch, 2.8 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    if chart_png_bytes:
        elements.append(Paragraph("GPA trend", heading_style))
        img_buffer = io.BytesIO(chart_png_bytes)
        elements.append(Image(img_buffer, width=5.5 * inch, height=3.1 * inch))
        elements.append(Spacer(1, 16))

    elements.append(Paragraph("Course history by semester", heading_style))
    elements.append(Spacer(1, 8))

    for sem in semesters:
        elements.append(Paragraph(f"{sem['term']}  —  GPA: {sem['gpa']:.2f}", styles["Heading4"]))
        course_rows = [["Course", "Credits", "Grade"]] + [
            [c["course_name"], str(c["credit_hours"]), c["grade"]] for c in sem["courses"]
        ]
        course_table = Table(course_rows, colWidths=[3.2 * inch, 1.2 * inch, 1.2 * inch])
        course_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b5bdb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(course_table)
        elements.append(Spacer(1, 14))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
