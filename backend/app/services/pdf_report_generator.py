import os
import sqlite3
import json
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from app.core.config import settings
from app.core.database import get_db_connection


class PDFReportGenerator:
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_audit_report(self, audit_id: str) -> Optional[str]:
        """Fetch audit from database and generate official PDF."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        audit = dict(row)
        pdf_path = os.path.join(self.reports_dir, f"{audit_id}.pdf")

        # Create Document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        primary_color = colors.HexColor("#0f172a")     # Slate 900
        brand_blue = colors.HexColor("#1e40af")        # Blue 800
        gold_color = colors.HexColor("#b45309")        # Amber 700
        pass_green = colors.HexColor("#15803d")        # Green 700
        fail_red = colors.HexColor("#b91c1c")          # Red 700
        light_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            'GovTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=brand_blue,
            alignment=1
        )

        subtitle_style = ParagraphStyle(
            'GovSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=primary_color,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0f172a")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("BUREAU OF INDIAN STANDARDS (BIS)", title_style))
        story.append(Paragraph("Government of India | Manak Bhavan, 9 Bahadur Shah Zafar Marg, New Delhi 110002", subtitle_style))
        story.append(Paragraph("<b>OFFICIAL PRODUCT CONFORMITY ASSESSMENT AUDIT REPORT</b>", ParagraphStyle('SubSub', parent=subtitle_style, fontSize=10, leading=14, textColor=gold_color)))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceBefore=2, spaceAfter=8))

        # 2. Metadata Grid
        verdict = audit.get("overall_verdict", "CONFORMING")
        verdict_color = pass_green if verdict == "CONFORMING" else (fail_red if verdict == "NON_CONFORMING" else gold_color)

        meta_data = [
            [
                Paragraph(f"<b>Audit Reference:</b> {audit['id']}", body_style),
                Paragraph(f"<b>Date Generated:</b> {audit.get('created_at', datetime.utcnow().strftime('%Y-%m-%d'))[:10]}", body_style)
            ],
            [
                Paragraph(f"<b>Standard Audited:</b> {audit['standard_is_code']}", body_style),
                Paragraph(f"<b>Title:</b> {audit.get('standard_title', 'Indian Standard')[:45]}", body_style)
            ],
            [
                Paragraph(f"<b>Product Name:</b> {audit['product_name']}", body_style),
                Paragraph(f"<b>Batch / Lot No:</b> {audit['batch_number']}", body_style)
            ],
            [
                Paragraph(f"<b>Manufacturer:</b> {audit['manufacturer_name']}", body_style),
                Paragraph(f"<b>Testing Lab:</b> {audit['testing_lab']}", body_style)
            ],
        ]

        meta_table = Table(meta_data, colWidths=[260, 280])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # 3. Overall Verdict Box
        verdict_banner = [
            [
                Paragraph(f"<font size='12'><b>OVERALL VERDICT: {verdict.replace('_', ' ')}</b></font>", ParagraphStyle('VTitle', parent=table_header_style, fontSize=11, alignment=1)),
                Paragraph(f"<b>Compliance Score:</b> {audit.get('compliance_score', 0)}%<br/><b>Passed:</b> {audit.get('passed_count', 0)} / {audit.get('total_count', 0)}", table_header_style)
            ]
        ]
        verdict_table = Table(verdict_banner, colWidths=[360, 180])
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verdict_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 8))

        # 4. Summary Text
        story.append(Paragraph("<b>Executive Compliance Summary:</b>", section_heading))
        story.append(Paragraph(audit.get("summary", ""), body_style))
        story.append(Spacer(1, 10))

        # 5. Parameter Table
        story.append(Paragraph("<b>Clause-by-Clause Parameter Evaluation:</b>", section_heading))
        
        param_data = [
            [
                Paragraph("<b>Parameter</b>", table_header_style),
                Paragraph("<b>Tested Value</b>", table_header_style),
                Paragraph("<b>Standard Limit</b>", table_header_style),
                Paragraph("<b>Clause Ref</b>", table_header_style),
                Paragraph("<b>Status</b>", table_header_style),
                Paragraph("<b>Remarks / Deviation</b>", table_header_style)
            ]
        ]

        parameter_results = json.loads(audit.get("parameter_results_json", "[]"))
        for p in parameter_results:
            p_status = p.get("status", "PASS")
            status_html = f"<font color='#15803d'><b>PASS</b></font>" if p_status == "PASS" else f"<font color='#b91c1c'><b>FAIL</b></font>"

            param_data.append([
                Paragraph(f"<b>{p.get('parameter_name', '')}</b>", table_cell_style),
                Paragraph(f"{p.get('tested_value', '')}", table_cell_style),
                Paragraph(f"{p.get('standard_limit', '')}", table_cell_style),
                Paragraph(f"{p.get('clause_reference', '')}", table_cell_style),
                Paragraph(status_html, table_cell_style),
                Paragraph(f"{p.get('remarks', '')[:100]}", table_cell_style)
            ])

        param_table = Table(param_data, colWidths=[95, 75, 95, 85, 45, 145])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), brand_blue),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(param_table)
        story.append(Spacer(1, 14))

        # 6. Legal Footer & Digital Verification Block
        footer_data = [
            [
                Paragraph("<b>Statutory Notice under BIS Act 2016:</b><br/>"
                          "This conformity report is generated by the AI-powered BIS Intelligent Assessment System "
                          "in accordance with standardized testing metrics. For legal certification or grant of ISI mark, "
                          "statutory sample testing under BIS (Conformity Assessment) Regulations must be executed.", 
                          ParagraphStyle('Legal', parent=body_style, fontSize=7, leading=8.5, textColor=colors.HexColor("#64748b"))),
                Paragraph("<b>Authorized AI Audit Engine</b><br/>"
                          "Verified & Digitally Sealed<br/>"
                          f"Ref: {audit['id']}<br/>"
                          "Bureau of Indian Standards", 
                          ParagraphStyle('Seal', parent=body_style, fontSize=7, leading=8.5, alignment=1))
            ]
        ]
        footer_table = Table(footer_data, colWidths=[380, 160])
        footer_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(KeepTogether(footer_table))

        # Build PDF
        doc.build(story)
        return pdf_path


pdf_report_generator = PDFReportGenerator()
