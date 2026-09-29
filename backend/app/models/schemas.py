from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMode(str, Enum):
    INDUSTRY = "industry"
    CONSUMER = "consumer"


class Citation(BaseModel):
    is_code: str = Field(..., max_length=255, description="BIS Standard Code, e.g., IS 14543:2018")
    title: str = Field(..., max_length=500, description="Official Standard Title")
    clause: str = Field(default="General", max_length=255, description="Clause or Section Number, e.g., Clause 5.2")
    page_number: int = Field(default=1, ge=1, le=10000, description="Page number in original BIS document")
    snippet: str = Field(..., max_length=5000, description="Exact textual or tabular snippet retrieved")
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Vector similarity/confidence score (0.0 - 1.0)")
    is_table: bool = Field(default=False, description="Whether citation originates from an extracted table")
    table_number: Optional[str] = Field(default=None, max_length=100, description="Table Identifier, e.g., Table 2")


class ChatMessage(BaseModel):
    role: str = Field(..., max_length=20, description="user or assistant")
    content: str = Field(..., max_length=100000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's query")
    mode: ChatMode = Field(default=ChatMode.INDUSTRY, description="Target persona: industry or consumer")
    selected_standard: Optional[str] = Field(default=None, max_length=100, description="Filter search by specific IS Code, e.g. IS 14543")
    history: Optional[List[ChatMessage]] = Field(default=[], max_length=50, description="Previous conversation turns")
    language: Optional[str] = Field(default="en", max_length=10, description="Target language code (e.g., en, hi, te, ta, mr, bn, kn, gu, ml, pa, ur)")


class ChatResponse(BaseModel):
    id: str = Field(..., max_length=100, description="Unique response identifier for telemetry tracking")
    answer: str = Field(..., description="Generated answer grounded in standard")
    mode: ChatMode = Field(...)
    citations: List[Citation] = Field(default=[])
    table_references: List[Dict[str, Any]] = Field(default=[], description="Structured table chunks retrieved")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    is_hallucination_safe: bool = Field(default=True)
    needs_clarification: bool = Field(default=False, description="True if query is ambiguous and requires user disambiguation")
    disambiguation_options: List[Dict[str, str]] = Field(default=[], description="List of options for user clarification")
    refusal_triggered: bool = Field(default=False, description="True if query is out of BIS scope")
    suggested_followups: List[str] = Field(default=[])
    procurement_recommendation: Optional[Dict[str, Any]] = Field(default=None, description="Structured recommendation for SIH26108 procurement engine")
    language: Optional[str] = Field(default="en", max_length=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000, description="Markdown text to translate")
    target_language: str = Field(default="hi", max_length=10, description="Target ISO language code (e.g. hi, te, ta, mr, bn, kn, gu, ml, pa, ur, en)")


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    target_language: str
    language_name: str
    native_name: str



# Admin Standards Management
class StandardMetadata(BaseModel):
    is_code: str = Field(..., max_length=100)
    title: str = Field(..., max_length=250)
    year: str = Field(..., max_length=20)
    category: str = Field(..., max_length=100)
    chunk_count: int = Field(default=0, ge=0)
    table_count: int = Field(default=0, ge=0)
    created_at: str = Field(..., max_length=50)


class StandardUploadResponse(BaseModel):
    status: str
    is_code: str
    title: str
    year: str
    total_chunks: int
    tables_extracted: int
    message: str


class TableData(BaseModel):
    id: str = Field(..., max_length=150)
    is_code: str = Field(..., max_length=100)
    table_number: str = Field(..., max_length=50)
    table_title: str = Field(..., max_length=250)
    clause: str = Field(..., max_length=100)
    page_number: int = Field(default=1, ge=1)
    columns: List[str] = Field(default=[])
    rows: List[List[str]] = Field(default=[])
    markdown_repr: str = Field(default="")


# Compliance Audit Models
class ComplianceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"
    NOT_TESTED = "NOT_TESTED"


class OverallVerdict(str, Enum):
    CONFORMING = "CONFORMING"
    NON_CONFORMING = "NON_CONFORMING"
    CONDITIONAL_COMPLIANCE = "CONDITIONAL_COMPLIANCE"


class AuditParameterInput(BaseModel):
    parameter_name: str = Field(..., min_length=1, max_length=150, description="e.g., pH, Lead, Tensile Strength")
    tested_value: str = Field(..., min_length=1, max_length=50, description="Observed lab value, e.g., 7.2 or 0.02")
    unit: str = Field(default="", max_length=50, description="mg/L, N/mm2, mm, etc.")
    notes: Optional[str] = Field(default="", max_length=300)


class AuditRequest(BaseModel):
    standard_is_code: str = Field(..., min_length=2, max_length=100, description="IS standard to audit against, e.g., IS 14543")
    product_name: str = Field(..., min_length=2, max_length=200, description="Product under evaluation")
    manufacturer_name: str = Field(..., min_length=2, max_length=200, description="Manufacturer or Applicant entity")
    batch_number: str = Field(default="BATCH-DEFAULT-01", max_length=100)
    testing_lab: str = Field(default="NABL Accredited BIS Testing Lab", max_length=200)
    parameters: List[AuditParameterInput] = Field(..., min_length=1, max_length=100)


class ParameterAuditResult(BaseModel):
    parameter_name: str
    tested_value: str
    standard_limit: str
    unit: str
    clause_reference: str
    status: ComplianceStatus
    deviation: Optional[str] = None
    remarks: str


class AuditResponse(BaseModel):
    audit_id: str = Field(..., max_length=100)
    standard_is_code: str
    standard_title: str
    product_name: str
    manufacturer_name: str
    batch_number: str
    testing_lab: str
    overall_verdict: OverallVerdict
    passed_count: int
    failed_count: int
    warning_count: int
    total_count: int
    compliance_score_percent: float
    summary: str
    parameter_results: List[ParameterAuditResult]
    report_download_url: str
    created_at: str


class AuditReportExtractRequest(BaseModel):
    raw_text: Optional[str] = Field(default=None, description="Raw OCR or manual text of the laboratory test report")
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded photo or scan of the laboratory test report")
    auto_verify: Optional[bool] = Field(default=True, description="Whether to run full automated compliance audit immediately")


class ExtractedLabReportData(BaseModel):
    status: str = "SUCCESS"
    is_relevant: bool = True
    relevance_reason: Optional[str] = None
    detected_subject: Optional[str] = None
    corrected_text: Optional[str] = None
    standard_is_code: str
    product_name: str
    manufacturer_name: str
    batch_number: str
    testing_lab: str
    parameters: List[AuditParameterInput]
    extracted_text: str
    confidence_score: float = 0.95
    extraction_method: str = "Hybrid Vision + OCR Engine"
    verification: Optional[AuditResponse] = None


# Telemetry and Feedback
class FeedbackRating(str, Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


class FeedbackRequest(BaseModel):
    query_id: str = Field(..., min_length=1, max_length=100)
    rating: FeedbackRating
    query_text: Optional[str] = Field(default=None, max_length=2000)
    response_text: Optional[str] = Field(default=None, max_length=10000)
    mode: Optional[str] = Field(default=None, max_length=20)
    comments: Optional[str] = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: str
    recorded_at: str


class TelemetryDashboardResponse(BaseModel):
    total_queries: int
    industry_queries: int
    consumer_queries: int
    positive_feedback_count: int
    negative_feedback_count: int
    satisfaction_rate: float
    total_standards_indexed: int
    total_tables_indexed: int
    total_audits_performed: int
    audit_conformance_rate: float
    top_queried_standards: List[Dict[str, Any]]
    recent_audits: List[Dict[str, Any]]
    recent_feedback: List[Dict[str, Any]]


# License & Hallmark Verification Models
class LicenseVerifyRequest(BaseModel):
    identifier: str = Field(..., min_length=2, max_length=100, description="CM/L number, HUID, or CRS R-number")
    query_type: Optional[str] = Field(default="auto", description="cml, huid, crs, or auto")
    image_base64: Optional[str] = Field(default=None, description="Optional image data for simulated OCR / visual inspection")


class LicenseVerifyResponse(BaseModel):
    is_valid: bool
    status: str
    is_relevant: bool = True
    relevance_reason: Optional[str] = None
    detected_subject: Optional[str] = None
    corrected_text: Optional[str] = None
    mark_type: str
    identifier: str
    standard_code: str
    product_name: Optional[str] = "Statutory Certified Product"
    product_type: Optional[str] = None
    brand_name: Optional[str] = None
    company: Optional[str] = None
    company_name: Optional[str] = None
    parent_company: Optional[str] = None
    manufacturer: Optional[str] = "Registered Licensee"
    flagship_products: Optional[str] = None
    license_type: Optional[str] = None
    license_name: Optional[str] = None
    issue_year: Optional[str] = None
    expiry_date: Optional[str] = None
    structure_breakdown: Optional[Dict[str, str]] = None
    mrp: Optional[str] = None
    online_price: Optional[str] = None
    net_quantity: Optional[str] = None
    batch_no: Optional[str] = None
    barcode: Optional[str] = None
    multi_unit_facilities: Optional[List[Dict[str, str]]] = None
    packaging_registration: Optional[str] = None
    operating_unit: str
    valid_until: str
    details: Dict[str, Any] = Field(default={})
    guidelines: List[str] = Field(default=[])
    bis_care_instructions: str
    grievance_redressal: str


# FSSAI Nutri-Score & Hidden Ingredient Decrypter Models
class NutriAnalyzeRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Ingredients text or nutrition facts table text")
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded photo of nutrition label or ingredients")
    persona: Optional[str] = Field(default="general", description="general, diabetic, gluten_free, infant, heart")
    language: Optional[str] = Field(default="en", description="Target language code for verdict translation")


class NutriAnalyzeResponse(BaseModel):
    status: str = "SUCCESS"
    is_relevant: bool = True
    relevance_reason: Optional[str] = None
    detected_subject: Optional[str] = None
    corrected_text: Optional[str] = None
    product_name: str
    verdict: str
    verdict_badge: str
    nutri_score_grade: str
    nutri_score_points: int
    score_breakdown: Optional[Dict[str, int]] = None
    summary_verdict: str
    spoken_summary: str
    spoken_language: str
    sodium_mg: Optional[float] = None
    sodium_level: str
    trans_fat_g: Optional[float] = None
    trans_fat_status: str
    saturated_fat_g: Optional[float] = None
    added_sugar_g: Optional[float] = None
    added_sugar_level: str
    has_palm_oil: bool
    palm_oil_details: Optional[str] = None
    hidden_sugars: List[Dict[str, str]] = Field(default=[])
    harmful_additives: List[Dict[str, str]] = Field(default=[])
    beneficial_ingredients: List[str] = Field(default=[])
    persona_alerts: List[Dict[str, str]] = Field(default=[])
    fssai_compliance_notes: List[str] = Field(default=[])
    raw_extracted_ingredients: List[str] = Field(default=[])
    nutrition_table: Dict[str, Any] = Field(default={})
    all_ingredients_analysis: List[Dict[str, Any]] = Field(default=[])
    govt_limit_comparison: List[Dict[str, Any]] = Field(default=[])
    usual_items_summary: List[Dict[str, Any]] = Field(default=[])


# -------------------------------------------------------------------------
# SIH26108: AI-Powered Procurement & Tender Standards Recommendation Models
# -------------------------------------------------------------------------
class ProcurementRecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000, description="Product description, technical specifications, or tender clause")
    category: Optional[str] = Field(default=None, max_length=100, description="Optional filter by procurement sector")
    language: Optional[str] = Field(default="en", max_length=10, description="Language code")


class ProcurementRecommendResponse(BaseModel):
    success: bool
    match_found: bool
    confidence_score: float = Field(default=0.0)
    primary_standard: Optional[Dict[str, Any]] = None
    mandatory_certification: Optional[Dict[str, Any]] = None
    allied_standards: Optional[Dict[str, Any]] = None
    gem_tender_clause: Optional[str] = None
    obsolete_warning: Optional[Dict[str, Any]] = None
    foreign_standard_notice: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    security_flag: Optional[bool] = False
    security_notice: Optional[str] = None


class ProcurementClauseRequest(BaseModel):
    is_code: str = Field(..., max_length=50, description="Indian standard code (e.g. IS 1786)")
    delivery_timeline_days: Optional[int] = Field(default=None, description="Delivery period in days")
    third_party_inspection_agency: Optional[str] = Field(default=None, description="Inspection agency (e.g., RITES, SGS, NABL)")


class ProcurementClauseResponse(BaseModel):
    is_code: str
    clause: str


class ProcurementTenderParseResponse(BaseModel):
    success: bool
    total_items_found: int
    items: List[Dict[str, Any]] = Field(default=[])
    is_relevant: bool = True
    relevance_reason: Optional[str] = None
    message: Optional[str] = None
