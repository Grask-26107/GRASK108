import os
import re
import base64
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.core.config import settings
from app.models.schemas import (
    AuditRequest,
    AuditResponse,
    AuditReportExtractRequest,
    ExtractedLabReportData
)
from app.services.compliance_audit import compliance_audit_engine
from app.services.pdf_report_generator import pdf_report_generator
from app.services.lab_report_extractor import lab_report_extractor_service

router = APIRouter(prefix="/audit", tags=["Compliance Audit & Verification"])


@router.post("", response_model=AuditResponse)
def run_compliance_audit(request: AuditRequest):
    """
    Evaluates manufacturer product test parameters against official BIS Standard clauses.
    Outputs structured Pass/Fail checklist with tolerance bounds and clause citations.
    """
    try:
        response = compliance_audit_engine.perform_audit(request)
        # Pre-generate PDF report in background
        pdf_report_generator.generate_audit_report(response.audit_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing compliance audit: {str(e)}"
        )


@router.get("/report/{audit_id}")
def download_audit_report(audit_id: str):
    """Generates and downloads official Government-format PDF compliance audit report."""
    # Strict regex validation to prevent directory traversal
    if not re.match(r"^[A-Za-z0-9\-_]{5,80}$", audit_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audit identifier format."
        )

    pdf_path = pdf_report_generator.generate_audit_report(audit_id)
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit report for ID {audit_id} not found."
        )

    # Verify that the path is strictly within the designated reports directory
    abs_pdf_path = os.path.abspath(pdf_path)
    abs_reports_dir = os.path.abspath(settings.REPORTS_DIR)
    if not abs_pdf_path.startswith(abs_reports_dir):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to specified file path is prohibited."
        )

    return FileResponse(
        path=abs_pdf_path,
        filename=f"BIS_Audit_Report_{audit_id}.pdf",
        media_type="application/pdf"
    )


@router.get("/templates")
def get_audit_templates():
    """Returns ready-to-test sample audit templates across major BIS standards with safe cartoon/superhero pseudonyms."""
    return [
        {
            "id": "water_conforming",
            "name": "Packaged Water (Batch 402 - Conforming)",
            "standard_is_code": "IS 14543",
            "product_name": "Premium Mineral Enriched Packaged Water",
            "manufacturer_name": "Himalayan Mineral Springs Ltd",
            "batch_number": "HMS-2026-B402",
            "testing_lab": "BIS Central Laboratory, Sahibabad (NABL Accredited)",
            "parameters": [
                {"parameter_name": "pH Value", "tested_value": "7.35", "unit": "", "notes": "Tested via digital pH meter at 25°C"},
                {"parameter_name": "Total Dissolved Solids (TDS)", "tested_value": "125.0", "unit": "mg/L", "notes": "Gravimetric method"},
                {"parameter_name": "Turbidity", "tested_value": "0.45", "unit": "NTU", "notes": "Nephelometric method"},
                {"parameter_name": "Lead (as Pb)", "tested_value": "0.003", "unit": "mg/L", "notes": "AAS graphite furnace test"},
                {"parameter_name": "Arsenic (as As)", "tested_value": "0.002", "unit": "mg/L", "notes": "Hydride generation method"},
                {"parameter_name": "Nitrate (as NO3)", "tested_value": "14.2", "unit": "mg/L", "notes": "Spectrophotometric test"},
                {"parameter_name": "E. Coli", "tested_value": "0", "unit": "cfu/250ml", "notes": "Membrane filtration method"}
            ]
        },
        {
            "id": "water_failed_lead",
            "name": "Packaged Water (Batch 403 - Contaminated Lead / Non-Conforming)",
            "standard_is_code": "IS 14543",
            "product_name": "AquaSpring 1L Packaged Drinking Water",
            "manufacturer_name": "Delta Packaged Beverages Ltd",
            "batch_number": "DPB-2026-FAIL-03",
            "testing_lab": "Northern Regional Quality Testing Laboratory (NABL Accredited)",
            "parameters": [
                {"parameter_name": "pH Value", "tested_value": "7.1", "unit": "", "notes": ""},
                {"parameter_name": "Total Dissolved Solids (TDS)", "tested_value": "480.0", "unit": "mg/L", "notes": ""},
                {"parameter_name": "Lead (as Pb)", "tested_value": "0.024", "unit": "mg/L", "notes": "Exceeds 0.01 mg/L statutory limit!"},
                {"parameter_name": "Arsenic (as As)", "tested_value": "0.004", "unit": "mg/L", "notes": ""},
                {"parameter_name": "E. Coli", "tested_value": "0", "unit": "cfu/250ml", "notes": ""}
            ]
        },
        {
            "id": "tmt_steel_fe500d",
            "name": "TMT Steel Bar Grade Fe 500D (Structural Batch 88A)",
            "standard_is_code": "IS 1786",
            "product_name": "High Strength TMT Rebar 16mm Dia",
            "manufacturer_name": "Deccan High-Tensile Steel Mills Ltd",
            "batch_number": "DHSM-FE500D-88A",
            "testing_lab": "Central Metallurgy & Metrology Lab (NABL Accredited)",
            "parameters": [
                {"parameter_name": "Carbon (C) Content", "tested_value": "0.21", "unit": "%", "notes": "Optical emission spectrometry"},
                {"parameter_name": "Sulphur (S) Content", "tested_value": "0.035", "unit": "%", "notes": "Combustion infrared method"},
                {"parameter_name": "Phosphorus (P) Content", "tested_value": "0.032", "unit": "%", "notes": "Spectrometric method"},
                {"parameter_name": "0.2% Proof Stress / Yield Strength", "tested_value": "528.0", "unit": "N/mm²", "notes": "Universal testing machine"},
                {"parameter_name": "Tensile Strength to Yield Strength Ratio", "tested_value": "1.14", "unit": "ratio", "notes": "Ductility ratio calculation"},
                {"parameter_name": "Elongation (Gauge Length 5.65√A)", "tested_value": "17.5", "unit": "%", "notes": "Tensile fracture test"}
            ]
        },
        {
            "id": "hdpe_pipe_pe100",
            "name": "HDPE Pipe PE 100 PN 10 (Water Distribution Lot 12)",
            "standard_is_code": "IS 4984",
            "product_name": "HDPE Pipe 110mm OD SDR 11",
            "manufacturer_name": "Bharat High-Density Polymers & Infrastructure Corp",
            "batch_number": "BHDP-PE100-LOT12",
            "testing_lab": "CIPET National Polymer Testing Facility (NABL Accredited)",
            "parameters": [
                {"parameter_name": "Base Polymer Density at 27°C", "tested_value": "952.5", "unit": "kg/m³", "notes": "Density gradient column"},
                {"parameter_name": "Melt Flow Index (190°C / 5 kg)", "tested_value": "0.45", "unit": "g/10 min", "notes": "MFI plastometer"},
                {"parameter_name": "Carbon Black Content", "tested_value": "2.4", "unit": "%", "notes": "Pyrolysis in nitrogen"},
                {"parameter_name": "Hydrostatic Strength (100h at 20°C, PE 100)", "tested_value": "12.4", "unit": "MPa hoop stress", "notes": "No burst or leakage observed"}
            ]
        }
    ]


@router.post("/extract-lab-report", response_model=ExtractedLabReportData)
def extract_lab_report(request: AuditReportExtractRequest):
    """
    Multimodal Vision & Optical Text Extraction Engine for BIS Compliance Audits:
    Extracts IS standard code, manufacturer, batch number, testing laboratory,
    and observed parameters from scanned lab reports, camera captures, or OCR text.
    If auto_verify=True, instantly executes full conformity assessment and returns Pass/Fail verdict.
    """
    try:
        result = lab_report_extractor_service.extract_and_verify(
            raw_text=request.raw_text,
            image_base64=request.image_base64,
            auto_verify=request.auto_verify if request.auto_verify is not None else True
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting lab report: {str(e)}"
        )


@router.post("/upload-lab-report", response_model=ExtractedLabReportData)
async def upload_lab_report(
    file: UploadFile = File(...),
    auto_verify: bool = Form(default=True)
):
    """
    Direct File Upload for Lab Reports (PDF or Image):
    Accepts laboratory test report files, converts to high-resolution representation,
    extracts metadata and test parameters, and auto-verifies compliance.
    """
    try:
        content_bytes = await file.read()
        filename = (file.filename or "report.jpg").lower()

        raw_text = ""
        image_b64 = None

        if filename.endswith(".pdf"):
            import pymupdf as fitz
            doc = fitz.open(stream=content_bytes, filetype="pdf")
            for page in doc:
                raw_text += page.get_text() + "\n"
            if len(doc) > 0:
                pix = doc[0].get_pixmap(dpi=150)
                img_data = pix.tobytes("jpeg")
                image_b64 = f"data:image/jpeg;base64,{base64.b64encode(img_data).decode('utf-8')}"
        else:
            image_b64 = f"data:image/jpeg;base64,{base64.b64encode(content_bytes).decode('utf-8')}"

        result = lab_report_extractor_service.extract_and_verify(
            raw_text=raw_text,
            image_base64=image_b64,
            auto_verify=auto_verify
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing uploaded lab report file: {str(e)}"
        )

