"""
FastAPI Endpoints for Procurement Recommendation & Tender Specification Generation (SIH26108)
Enables procurement officials to identify Indian Standards, check mandatory QCOs,
identify allied standards, and generate GeM-ready tender specification clauses.
"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Response
import pymupdf as fitz

from app.models.schemas import (
    ProcurementRecommendRequest,
    ProcurementRecommendResponse,
    ProcurementClauseRequest,
    ProcurementClauseResponse,
    ProcurementTenderParseResponse
)
from app.services.procurement_service import procurement_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/procurement", tags=["Procurement & Tender Standards Recommendation Engine"])


@router.post("/recommend", response_model=ProcurementRecommendResponse)
async def recommend_procurement_standard(request: ProcurementRecommendRequest):
    """
    Recommends the most relevant Indian Standard(s) based on product description,
    technical specifications, or tender clause text.
    Provides latest version, active amendments, mandatory QCO check, and allied standards.
    """
    try:
        rec = procurement_service.recommend_standard(request.query)
        if not rec.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=rec.get("error", "Failed to process procurement query.")
            )
        return ProcurementRecommendResponse(**rec)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recommend_procurement_standard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating standards recommendation: {str(e)}"
        )


@router.post("/upload-tender", response_model=ProcurementTenderParseResponse)
async def upload_and_parse_tender(file: UploadFile = File(...)):
    """
    Ingests a tender document (PDF or text file), extracts technical deliverables,
    and returns Indian Standards recommendations for each identified tender item.
    """
    raw_filename = os.path.basename(file.filename or "tender.pdf")
    ext = raw_filename.lower().split(".")[-1]

    if ext not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF (.pdf) or text (.txt) tender documents are supported."
        )

    try:
        contents = await file.read()
        extracted_text = ""

        if ext == "pdf":
            try:
                doc = fitz.open(stream=contents, filetype="pdf")
                for page_num in range(min(len(doc), 30)):  # Read up to first 30 pages
                    extracted_text += doc[page_num].get_text() + "\n"
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Failed to read the tender PDF. Please ensure the document is not password-protected."
                )
        else:
            extracted_text = contents.decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded tender document does not contain readable text."
            )

        # Pre-screen document domain relevance against recipes, source code, resumes, etc.
        is_rel, rel_reason, rel_msg = procurement_service.validate_tender_document_relevance(extracted_text)
        if not is_rel:
            return ProcurementTenderParseResponse(
                success=False,
                total_items_found=0,
                items=[],
                is_relevant=False,
                relevance_reason=rel_reason,
                message=rel_msg
            )

        items = procurement_service.parse_tender_document_text(extracted_text)

        summary_msg = (
            f"Successfully parsed and extracted {len(items)} procurement items from tender document."
            if items
            else "Tender document processed, but no direct Indian Standard matches were found for the identified line items."
        )

        return ProcurementTenderParseResponse(
            success=True,
            total_items_found=len(items),
            items=items,
            is_relevant=True,
            relevance_reason=rel_reason,
            message=summary_msg
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_and_parse_tender: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse tender document: {str(e)}"
        )


@router.post("/generate-clause", response_model=ProcurementClauseResponse)
async def generate_gem_tender_clause(request: ProcurementClauseRequest):
    """
    Generates a customized, official GeM tender clause for procurement tender specifications.
    """
    try:
        custom_params = {}
        if request.delivery_timeline_days:
            custom_params["delivery_timeline_days"] = request.delivery_timeline_days
        if request.third_party_inspection_agency:
            custom_params["third_party_inspection_agency"] = request.third_party_inspection_agency

        clause = procurement_service.generate_custom_gem_clause(request.is_code, custom_params)
        return ProcurementClauseResponse(
            is_code=request.is_code,
            clause=clause
        )
    except Exception as e:
        logger.error(f"Error in generate_gem_tender_clause: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tender clause: {str(e)}"
        )


@router.get("/categories")
async def get_procurement_categories():
    """Returns all unique procurement sectors supported by the recommendation engine."""
    return {
        "success": True,
        "categories": procurement_service.get_all_categories()
    }


@router.get("/standards-by-category")
async def get_standards_by_category(category: str):
    """Returns all standards under a given procurement category."""
    stds = procurement_service.get_standards_by_category(category)
    return {
        "success": True,
        "category": category,
        "total_standards": len(stds),
        "standards": stds
    }


@router.get("/ministries")
async def get_procurement_ministries():
    """Returns all unique issuing ministries for Quality Control Orders (QCOs)."""
    return {
        "success": True,
        "ministries": procurement_service.get_all_ministries()
    }


@router.get("/standards-by-ministry")
async def get_standards_by_ministry(ministry: str):
    """Returns all standards regulated by a given ministry under mandatory QCOs."""
    stds = procurement_service.get_standards_by_ministry(ministry)
    return {
        "success": True,
        "ministry": ministry,
        "total_standards": len(stds),
        "standards": stds
    }


class ExportBoqRequest(BaseModel):
    """Request body for bulk GeM BoQ CSV export."""
    items: Optional[List[Dict[str, Any]]] = None
    is_code: Optional[str] = None  # legacy single-standard mode


@router.post("/export-gem-boq")
async def export_gem_boq_csv(request: ExportBoqRequest):
    """
    Generates a formatted CSV Schedule of Requirements (SOR) table
    compatible with Government e-Marketplace (GeM) bulk tender uploads.

    Accepts either:
      - { "items": [...] }  -- bulk mode (multiple tender items)
      - { "is_code": "IS 1786" }  -- legacy single-standard mode
    """
    # Bulk mode: delegate to service method
    if request.items:
        csv_data = procurement_service.export_gem_boq_csv(request.items)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="GeM_BoQ_Bulk_Export.csv"'}
        )

    # Legacy single-standard mode
    is_code = (request.is_code or "").strip()
    std = procurement_service._standards_registry.get(is_code.upper())
    if not std:
        std = procurement_service._standards_registry.get(f"IS {is_code.upper()}")

    if not std:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Standard '{is_code}' not found in procurement catalog."
        )

    header = "Item No,Deliverable Name,Mandatory Indian Standard,Active Amendments,Certification Scheme,Issuing Ministry,NABL Testing Standard,GeM Specification Clause\n"
    test_methods = "; ".join([t["code"] for t in std.get("allied_standards", {}).get("test_methods", [])])
    amendments = "; ".join([f"Amd {a['number']} ({a['year']})" for a in std.get("active_amendments", [])])
    clean_clause = std.get("gem_tender_clause", "").replace('"', '""')

    row = (
        f'1,"{std.get("title")}","{std.get("code")}","{amendments}",'
        f'"{std.get("mandatory_certification", {}).get("scheme")}","{std.get("mandatory_certification", {}).get("issuing_ministry")}",'
        f'"{test_methods}","{clean_clause}"\n'
    )

    csv_data = header + row
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="GeM_BoQ_Spec_{std.get("id")}.csv"'}
    )
