import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from app.core.config import settings


class CertificateDossierGenerator:
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_dossier_pdf(self, assessment_data: Dict[str, Any], applicant_name: str = "Enterprise Applicant") -> Optional[str]:
        """Generate a complete statutory application dossier PDF."""
        dossier_id = f"DOSSIER-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        pdf_path = os.path.join(self.reports_dir, f"{dossier_id}.pdf")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Color Palette
        brand_blue = colors.HexColor("#1e40af")
        dark_slate = colors.HexColor("#0f172a")
        accent_gold = colors.HexColor("#b45309")
        pass_green = colors.HexColor("#15803d")
        warning_amber = colors.HexColor("#d97706")
        danger_red = colors.HexColor("#b91c1c")
        light_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            'DossierTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=18,
            textColor=brand_blue,
            alignment=1
        )

        subtitle_style = ParagraphStyle(
            'DossierSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )

        section_heading = ParagraphStyle(
            'DossierSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=13,
            textColor=dark_slate,
            spaceBefore=6,
            spaceAfter=3
        )

        body_style = ParagraphStyle(
            'DossierBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#1e293b")
        )

        table_header = ParagraphStyle(
            'DossierTH',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.white
        )

        table_cell = ParagraphStyle(
            'DossierTD',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            leading=9,
            textColor=dark_slate
        )

        story = []

        # 1. Header
        story.append(Paragraph("NATIONAL CONFORMITY & STATUTORY LICENSING DOSSIER", title_style))
        story.append(Paragraph("Smart India Hackathon 2026 | Problem Statement: SIH26107 (Bureau of Indian Standards & FSSAI)", subtitle_style))
        story.append(Paragraph("<b>STATUTORY PRE-SUBMISSION AUDIT & READINESS CERTIFICATE</b>", ParagraphStyle('SubSub', parent=subtitle_style, fontSize=9.5, leading=13, textColor=accent_gold)))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceBefore=2, spaceAfter=6))

        # 2. Key Metadata & Score Card
        product = assessment_data.get("product", {})
        score = assessment_data.get("readiness_score", 0)
        score_color = pass_green if score >= 90 else (warning_amber if score >= 60 else danger_red)

        meta_rows = [
            [
                Paragraph(f"<b>Dossier Tracking ID:</b> {dossier_id}", body_style),
                Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%d %B %Y')}", body_style)
            ],
            [
                Paragraph(f"<b>Applicant Enterprise:</b> {applicant_name}", body_style),
                Paragraph(f"<b>MSME Udyam Status:</b> {'REGISTERED (50% Concession Active)' if assessment_data.get('has_udyam_msme') else 'NOT REGISTERED (Concession Pending)'}", body_style)
            ],
            [
                Paragraph(f"<b>Product Profile:</b> {product.get('title', 'N/A')}", body_style),
                Paragraph(f"<b>Indian Standard:</b> <b>{product.get('is_code', 'N/A')}</b>", body_style)
            ],
            [
                Paragraph(f"<b>Mandatory QCO Order:</b> {'YES - ILLEGAL TO SELL WITHOUT ISI/CRS' if product.get('mandatory_qco') else 'Voluntary Standards'}", body_style),
                Paragraph(f"<b>Overall Readiness:</b> <font color='{score_color.hexval()}'><b>{score}% ({assessment_data.get('status', '')})</b></font>", body_style)
            ]
        ]

        meta_table = Table(meta_rows, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 6))

        # 3. Applicable Certificates & Fees
        story.append(Paragraph("1. Applicable Statutory Certificates & Financial Assessment", section_heading))
        cert_rows = [
            [
                Paragraph("<b>Certificate / License</b>", table_header),
                Paragraph("<b>Governing Authority</b>", table_header),
                Paragraph("<b>Statutory Form</b>", table_header),
                Paragraph("<b>Gross Fee</b>", table_header),
                Paragraph("<b>MSME Concession</b>", table_header),
                Paragraph("<b>Net Fee</b>", table_header),
            ]
        ]

        certs = assessment_data.get("certificates", [])
        for c in certs:
            cert_rows.append([
                Paragraph(c.get("name", ""), table_cell),
                Paragraph(c.get("authority", ""), table_cell),
                Paragraph(c.get("statutory_form", ""), table_cell),
                Paragraph(f"₹{c.get('base_fee', 0):,}", table_cell),
                Paragraph(f"-₹{c.get('concession_applied', 0):,}", table_cell),
                Paragraph(f"<b>₹{c.get('net_fee', 0):,}</b>", table_cell),
            ])

        fin = assessment_data.get("financials", {})
        cert_rows.append([
            Paragraph("<b>TOTALS</b>", table_cell),
            Paragraph("-", table_cell),
            Paragraph("-", table_cell),
            Paragraph(f"<b>₹{fin.get('gross_statutory_fee', 0):,}</b>", table_cell),
            Paragraph(f"<b>-₹{fin.get('concessions_unlocked', 0):,}</b>", table_cell),
            Paragraph(f"<b>₹{fin.get('net_payable_fee', 0):,}</b>", table_cell),
        ])

        cert_table = Table(cert_rows, colWidths=[130, 110, 110, 60, 65, 65])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), brand_blue),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(cert_table)
        story.append(Spacer(1, 6))

        # 4. Prerequisites Checklist
        story.append(Paragraph("2. Statutory Documentation & Prerequisite Verification Status", section_heading))
        prereq_rows = [
            [
                Paragraph("<b>Required Document / Prerequisite</b>", table_header),
                Paragraph("<b>Category</b>", table_header),
                Paragraph("<b>Statutory Purpose / Rule</b>", table_header),
                Paragraph("<b>Status</b>", table_header),
            ]
        ]

        prereqs = assessment_data.get("prerequisites_checklist", [])
        for p in prereqs:
            status_text = "<font color='#15803d'><b>VERIFIED</b></font>" if p.get("checked") else "<font color='#b91c1c'><b>MISSING</b></font>"
            if not p.get("checked") and p.get("is_critical_blocker"):
                status_text = "<font color='#b91c1c'><b>CRITICAL BLOCKER</b></font>"
                
            prereq_rows.append([
                Paragraph(p.get("name", ""), table_cell),
                Paragraph(p.get("category", "").upper(), table_cell),
                Paragraph(p.get("description", ""), table_cell),
                Paragraph(status_text, table_cell),
            ])

        prereq_table = Table(prereq_rows, colWidths=[150, 70, 240, 80])
        prereq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), dark_slate),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ]))
        story.append(prereq_table)
        story.append(Spacer(1, 6))

        # 5. Mandatory In-House Factory Laboratory Equipment
        lab_tools = product.get("inhouse_lab_equipment", [])
        if lab_tools:
            story.append(Paragraph(f"3. Mandatory In-House Testing Laboratory Equipment ({product.get('is_code', '')})", section_heading))
            story.append(Paragraph("<i>Note: Bureau of Indian Standards visiting officers will physically verify calibration & operation of each apparatus before granting license.</i>", subtitle_style))
            story.append(Spacer(1, 2))
            
            tool_rows = []
            for i in range(0, len(lab_tools), 2):
                t1 = f"• {lab_tools[i]}"
                t2 = f"• {lab_tools[i+1]}" if i+1 < len(lab_tools) else ""
                tool_rows.append([Paragraph(t1, table_cell), Paragraph(t2, table_cell)])

            tool_table = Table(tool_rows, colWidths=[270, 270])
            tool_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), light_bg),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(tool_table)
            story.append(Spacer(1, 6))

        # 6. Official Portal Deep Links & Submission Procedure
        story.append(Paragraph("4. Step-by-Step Official Portal Submission Procedure", section_heading))
        steps = [
            "1. <b>Register on Udyam First:</b> If you do not have an MSME Udyam registration, visit <u>udyamregistration.gov.in</u> (100% Free). Obtain your 16-digit Udyam number in 24 hours.",
            "2. <b>Access Manakonline:</b> Visit <u>manakonline.in</u>, create an industry account, and select 'Product Certification (Scheme-I)'.",
            "3. <b>Upload Pre-requisites:</b> Upload the documents audited above into the designated sections of Form V.",
            "4. <b>Pay Concessional Statutory Fee:</b> Enter your Udyam number at the payment gateway to automatically deduct the 50% MSME concession.",
            "5. <b>Inspection Scheduling:</b> A BIS inspecting officer will be assigned for factory audit and verification of the in-house testing equipment listed above."
        ]
        for s in steps:
            story.append(Paragraph(s, body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94a3b8"), spaceBefore=4, spaceAfter=4))
        story.append(Paragraph(
            "<b>STATUTORY DISCLAIMER:</b> This dossier is generated by GRASK AI under Smart India Hackathon 2026 guidelines. "
            "It assists manufacturing and food business applicants in technical pre-audit and regulatory readiness. "
            "Statutory grant of license is subject to official inspection and testing under the BIS Act, 2016 and FSS Act, 2006.",
            ParagraphStyle('Disclaimer', parent=subtitle_style, fontSize=7, leading=9, textColor=colors.HexColor("#64748b"))
        ))

        # Build Document
        doc.build(story)
        return pdf_path


# Singleton
certificate_dossier_generator = CertificateDossierGenerator()
