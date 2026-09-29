import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.certificate_engine import certificate_engine
from app.services.certificate_dossier_generator import certificate_dossier_generator

logger = logging.getLogger("bis_assistant.certificates")

router = APIRouter(prefix="/certificates", tags=["Certificates & Licensing Studio"])


class CertificateSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Product or business search query")


class CertificateAssessRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Product name or business type")
    annual_turnover_tier: str = Field(default="small_medium", description="micro (<12L), small_medium (12L-20Cr), large (>20Cr)")
    has_udyam_msme: bool = Field(default=False, description="Whether applicant holds Udyam MSME certificate")
    checked_document_ids: List[str] = Field(default=[], description="List of document IDs the applicant possesses")


class GenerateDossierRequest(BaseModel):
    assessment: Dict[str, Any] = Field(..., description="Full assessment payload from /assess")
    applicant_name: Optional[str] = Field(default="Enterprise Applicant", max_length=200)


@router.get("/popular", summary="Get popular products and businesses for quick selection")
def get_popular_products():
    return {
        "success": True,
        "popular_products": certificate_engine.search_popular_products()
    }


@router.post("/search", summary="Search and resolve product standard and certificate requirements")
def search_product(request: CertificateSearchRequest):
    if certificate_engine.is_garbage_or_unrelated(request.query):
        return {
            "success": False,
            "error": "OUT_OF_SCOPE",
            "message": f"'{request.query}' does not match any recognized manufacturing standard, food product, or certification in India.",
            "suggestions": certificate_engine.search_popular_products()
        }

    profile = certificate_engine.resolve_product_profile(request.query)
    if not profile:
        return {
            "success": False,
            "error": "UNRECOGNIZED_PRODUCT",
            "message": f"Could not map '{request.query}' to an Indian Standard. Please choose from popular suggestions or type a standard like 'Packaged Water', 'Helmets', 'TMT Sariya'.",
            "suggestions": certificate_engine.search_popular_products()
        }

    return {
        "success": True,
        "product": profile
    }


@router.post("/assess", summary="Run gap analysis, calculate readiness score, and compute fee concessions")
def assess_certificate_readiness(request: CertificateAssessRequest):
    result = certificate_engine.assess_readiness(
        query=request.query,
        annual_turnover_tier=request.annual_turnover_tier,
        has_udyam_msme=request.has_udyam_msme,
        checked_document_ids=request.checked_document_ids
    )
    return result


@router.post("/generate-dossier", summary="Generate downloadable statutory application dossier PDF")
def generate_application_dossier(request: GenerateDossierRequest):
    try:
        pdf_path = certificate_dossier_generator.generate_dossier_pdf(
            assessment_data=request.assessment,
            applicant_name=request.applicant_name or "Enterprise Applicant"
        )
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Failed to generate statutory dossier PDF.")

        filename = os.path.basename(pdf_path)
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error generating certificate dossier: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
