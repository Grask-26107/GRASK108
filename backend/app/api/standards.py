import os
import re
import shutil
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Header
from app.core.config import settings
from app.models.schemas import (
    StandardUploadResponse,
    StandardMetadata,
    TableData,
    LicenseVerifyRequest,
    LicenseVerifyResponse,
    NutriAnalyzeRequest,
    NutriAnalyzeResponse
)
from app.services.pdf_table_parser import TableAwarePDFParser
from app.services.vector_store import vector_store_service
from app.services.license_verifier import license_verifier_service
from app.services.nutri_analyzer import nutri_analyzer_service
from app.services.bis_services_directory import (
    BIS_SERVICES_DIRECTORY,
    TESTING_LABORATORIES_DIRECTORY,
    search_testing_laboratories
)
from app.core.database import get_all_standards_db, delete_standard_db

router = APIRouter(prefix="/standards", tags=["BIS Standards & Verification Services"])
pdf_parser = TableAwarePDFParser()


@router.post("/upload", response_model=StandardUploadResponse)
async def upload_standard_pdf(
    file: UploadFile = File(...),
    is_code: str = Form(...),
    title: str = Form(...),
    year: str = Form(default="2024"),
    category: str = Form(default="General Standard"),
    x_admin_key: Optional[str] = Header(default=None)
):
    """
    Dynamic Admin Ingestion Endpoint:
    Uploads a BIS Standard PDF, executes Table-Aware parsing, extracts tables & clauses,
    generates embeddings, and registers chunks in ChromaDB without server restart.
    """
    # Enforce file extension
    raw_filename = os.path.basename(file.filename or "standard.pdf")
    if not raw_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only authentic PDF documents (.pdf) are accepted for BIS Standard ingestion."
        )

    # Sanitize filenames and parameters against path traversal and injection
    clean_code = re.sub(r'[^a-zA-Z0-9_\-\s:]', '', is_code).strip()
    clean_title = re.sub(r'[^a-zA-Z0-9_\-\s,\.]', '', title).strip()
    if not clean_code or not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid standard code or title parameters provided."
        )

    safe_is_prefix = re.sub(r'[^a-zA-Z0-9_]', '_', clean_code)
    safe_base_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_filename)
    safe_filename = f"{safe_is_prefix}_{safe_base_name}"
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, safe_filename))

    # Path traversal check
    if not file_path.startswith(os.path.abspath(settings.UPLOAD_DIR)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Illegal file path detected."
        )

    # Validate PDF Magic Bytes (prevent executable disguise attacks)
    header_bytes = await file.read(5)
    await file.seek(0)
    if header_bytes != b"%PDF-":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File signature validation failed: The uploaded file is not a valid PDF document."
        )

    # Save PDF locally with 25MB maximum size enforcement
    max_size = 25 * 1024 * 1024  # 25 MB
    total_bytes = 0

    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(64 * 1024)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > max_size:
                buffer.close()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Uploaded standard exceeds the maximum allowed file size of 25MB."
                )
            buffer.write(chunk)

    try:
        # Table-aware PDF parsing
        parsed_chunks = pdf_parser.parse_pdf(
            pdf_path=file_path,
            manual_is_code=clean_code,
            manual_title=clean_title
        )

        if not parsed_chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract verified text or tables from the provided PDF."
            )

        # Index into ChromaDB
        total_indexed = vector_store_service.add_chunks(parsed_chunks)
        tables_count = sum(1 for c in parsed_chunks if c.is_table)

        return StandardUploadResponse(
            status="SUCCESS",
            is_code=clean_code,
            title=clean_title,
            year=year,
            total_chunks=total_indexed,
            tables_extracted=tables_count,
            message=f"Standard {clean_code} successfully parsed and indexed with {tables_count} tables preserved."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error occurred while parsing standard PDF."
        )


@router.get("", response_model=List[StandardMetadata])
def list_standards():
    """Lists all BIS standards currently indexed in the vector repository."""
    standards = get_all_standards_db()
    results = []
    for s in standards:
        results.append(StandardMetadata(
            is_code=s["is_code"],
            title=s["title"],
            year=s["year"] or "2024",
            category=s["category"] or "National Standard",
            chunk_count=s["chunk_count"] or 0,
            table_count=s["table_count"] or 0,
            created_at=s["created_at"] or ""
        ))
    return results


@router.delete("/{is_code}")
def remove_standard(is_code: str):
    """Removes a standard from the vector store and database registry."""
    clean_code = re.sub(r'[^a-zA-Z0-9_\-\s:]', '', is_code).strip()
    success = vector_store_service.delete_standard(clean_code)
    if success:
        return {"status": "SUCCESS", "message": f"Standard {clean_code} deleted successfully."}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Standard {clean_code} could not be deleted or was not found."
    )


@router.get("/tables", response_model=List[TableData])
def get_extracted_tables(is_code: Optional[str] = None):
    """Returns all structured tables extracted from BIS standards."""
    raw_tables = vector_store_service.get_all_tables(is_code=is_code)
    formatted = []
    for t in raw_tables:
        formatted.append(TableData(
            id=t["id"],
            is_code=t["is_code"],
            table_number=t["table_number"],
            table_title=t["table_title"],
            clause=t["clause"],
            page_number=t["page_number"],
            columns=t["columns"],
            rows=t["rows"],
            markdown_repr=t["markdown_repr"]
        ))
    return formatted


@router.post("/verify-license", response_model=LicenseVerifyResponse)
def verify_bis_license(payload: LicenseVerifyRequest):
    """
    MANAK-Vision Statutory Verification Engine:
    Validates CM/L numbers (Scheme-I ISI Mark), 6-digit HUID (Gold Hallmarking),
    or CRS R-Numbers against authorized BIS registries and detects counterfeit patterns.
    """
    result = license_verifier_service.verify_identifier(
        identifier=payload.identifier,
        query_type=payload.query_type or "auto",
        image_base64=payload.image_base64
    )
    return LicenseVerifyResponse(**result)


@router.get("/services-directory")
def get_bis_services_directory() -> Dict[str, Any]:
    """
    Returns official information on BIS initiatives:
    - Standards Clubs (Schools & Colleges)
    - NITS Training Programs
    - Laboratory Recognition Scheme (LRS)
    - Consumer Protection & Grievance Redressal
    - 17 BIS Technical Departments
    """
    return BIS_SERVICES_DIRECTORY


@router.get("/laboratories")
def get_testing_laboratories(
    query: Optional[str] = None,
    standard_code: Optional[str] = None,
    region: Optional[str] = None,
    discipline: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search and retrieve accredited BIS Central/Regional and NABL recognized testing laboratories.
    Filter by standard_code (e.g. IS 14543), region (North/South/East/West), discipline, or search query.
    """
    return search_testing_laboratories(
        query=query or "",
        standard_code=standard_code or "",
        region=region or "",
        discipline=discipline or ""
    )


@router.post("/ocr-extract")
def extract_product_identifiers(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optical Recognition & Number Extractor:
    Extracts BIS CM/L, FSSAI 14-digit, Gold HUID, or CRS R-Numbers from raw OCR text or image metadata.
    """
    raw_text = payload.get("text", "")
    image_base64 = payload.get("image_base64")
    
    extracted = license_verifier_service.extract_from_image_and_text(text=raw_text, image_base64=image_base64)
    
    if extracted.get("is_relevant") is False:
        return {
            "status": "IRRELEVANT_DATA",
            "is_relevant": False,
            "relevance_reason": extracted.get("relevance_reason", "Irrelevant data detected: Media does not contain statutory marks."),
            "detected_subject": extracted.get("detected_subject", "Unrelated Subject"),
            "extracted_identifiers": [],
            "primary_identifier": None,
            "hybrid_summary": None,
            "llm_metadata": None,
            "verification": {
                "is_valid": False,
                "status": "IRRELEVANT_DATA",
                "is_relevant": False,
                "relevance_reason": extracted.get("relevance_reason", "Irrelevant data detected."),
                "detected_subject": extracted.get("detected_subject", "Unrelated Subject"),
                "mark_type": "Irrelevant / Non-Domain Data",
                "license_name": f"Irrelevant Media ({extracted.get('detected_subject')})",
                "guidelines": [
                    "Irrelevant data detected: Uploaded image does not depict BIS ISI Mark, CM/L license, FSSAI license, Gold Hallmark, CRS R-Number, or GS1 barcode.",
                    "Please capture or upload a clear photo of the product packaging or certification mark."
                ]
            }
        }

    # Auto-verify primary match if found
    verification_result = None
    if extracted.get("primary"):
        p = extracted["primary"]
        verification_result = license_verifier_service.verify_identifier(
            identifier=p["value"],
            query_type=p["type"] or "auto",
            image_base64=image_base64
        )
        # Enrich with LLM vision metadata if available
        if extracted.get("llm_metadata") and verification_result:
            meta = extracted["llm_metadata"]
            if meta.get("brand_name") and "GS1 Enterprise Brand" in str(verification_result.get("brand_name", "")):
                verification_result["brand_name"] = meta["brand_name"]
            if meta.get("company") and "GS1 Registered Enterprise" in str(verification_result.get("company", "")):
                verification_result["company"] = meta["company"]
                verification_result["company_name"] = meta["company"]
            if meta.get("parent_company") and "GS1 India Enterprise" in str(verification_result.get("parent_company", "")):
                verification_result["parent_company"] = meta["parent_company"]
            if meta.get("product_name") and "Packaged Consumer Commodity" in str(verification_result.get("product_name", "")):
                verification_result["product_name"] = meta["product_name"]

    # If no identifier was found, but the media or text relates to certification marks (e.g. ISI logo without CM/L)
    if not verification_result:
        combined_text = f"{raw_text} {extracted.get('hybrid_summary') or ''} {extracted.get('relevance_reason') or ''}".lower()
        has_mark_mention = any(k in combined_text for k in ["isi", "bis", "cml", "cm/l", "standard mark", "hallmark", "fssai", "crs"])
        
        if has_mark_mention or "mark" in str(extracted.get("detected_subject", "")).lower():
            verification_result = {
                "is_valid": False,
                "status": "SUSPECT_COUNTERFEIT (MISSING MANDATORY CM/L)",
                "is_relevant": True,
                "relevance_reason": "Certification mark detected without mandatory statutory license number.",
                "detected_subject": extracted.get("detected_subject") or "Suspect Mark Packaging",
                "mark_type": "Suspect Non-Conforming Mark",
                "license_type": "None",
                "license_name": "Incomplete / Fake Certification Mark",
                "brand_name": "Unverified Commercial Product",
                "company": "Unlicensed Manufacturer",
                "company_name": "Unlicensed Manufacturer",
                "parent_company": "N/A",
                "product_name": "Uncertified Product Bearing Incomplete Mark",
                "product_type": "Suspect Counterfeit",
                "flagship_products": "N/A",
                "issue_year": "N/A",
                "expiry_date": "N/A",
                "identifier": "No License Number Printed",
                "standard_code": "None",
                "manufacturer": "Unlicensed",
                "operating_unit": "Unverified Facility",
                "valid_until": "Invalid",
                "details": {
                    "violation": "ISI or certification logo detected without mandatory statutory license digits."
                },
                "guidelines": [
                    "⚠️ Suspect Counterfeit Detected: The mark was detected without the mandatory statutory license number.",
                    "Under Section 16 & 29 of the BIS Act 2016, displaying the ISI Mark without a valid 7-digit CM/L license number is an illegal statutory offence.",
                    "Genuine ISI Mark requirements: (1) Indian Standard IS Code at TOP, (2) Oval ISI Logo in CENTER, (3) 7-digit CM/L License Number at BOTTOM."
                ],
                "bis_care_instructions": "Check your physical product packaging for the 7-digit CM/L number located directly below the ISI mark.",
                "grievance_redressal": "Report counterfeit products on the BIS Care App or National Consumer Helpline at 1915."
            }

    return {
        "status": "SUCCESS",
        "is_relevant": True,
        "relevance_reason": extracted.get("relevance_reason", "Relevant certification mark data detected."),
        "detected_subject": extracted.get("detected_subject", "Packaging / Document"),
        "extracted_identifiers": extracted.get("all", []),
        "primary_identifier": extracted.get("primary"),
        "hybrid_summary": extracted.get("hybrid_summary"),
        "llm_metadata": extracted.get("llm_metadata"),
        "verification": verification_result
    }


@router.post("/analyze-ingredients", response_model=NutriAnalyzeResponse)
def analyze_food_ingredients(payload: NutriAnalyzeRequest):
    """
    FSSAI Nutri-Score & Hidden Ingredient Decrypter Engine:
    Inspects nutrition table & ingredients list for:
    - High sodium, trans fats, palm oil, hidden sugars (maltodextrin, HFCS, invert syrup)
    - Hazardous chemical additives (INS 102, 110, 122, 171, 621 MSG, 211, 320 BHA)
    - Specialized clinical safety profiles (Diabetic, Gluten-Sensitive / Celiac, Infant & Child, Heart / Hypertension)
    - Returns definitive verdict: HARMFUL, CAUTION, or SECURE with official FSSAI Nutri-Score (Grade A to E).
    """
    try:
        result = nutri_analyzer_service.analyze(
            text=payload.text,
            image_base64=payload.image_base64,
            persona=payload.persona or "general",
            language=payload.language or "en"
        )
        return NutriAnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nutrition analysis error: {str(e)}"
        )


