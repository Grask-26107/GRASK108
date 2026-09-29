"""
Laboratory Report Optical & Multimodal Text Extractor with Automated BIS Audit Verification
Extracts IS Standard Codes, Manufacturer/Batch Metadata, and Observed Laboratory Test Parameters
from scanned test certificates, camera captures, and OCR streams.
"""

import re
import io
import json
import logging
import base64
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

from app.core.config import settings
from app.models.schemas import (
    AuditParameterInput,
    AuditRequest,
    AuditResponse,
    ExtractedLabReportData
)
from app.services.compliance_audit import compliance_audit_engine, STANDARD_BENCHMARKS
from app.services.pdf_report_generator import pdf_report_generator
from app.services.domain_relevance_guard import domain_relevance_guard

logger = logging.getLogger(__name__)


# Dictionary of known parameter aliases for robust tabular extraction
KNOWN_PARAMETER_MAP = {
    # IS 14543 / Water Parameters
    "ph": ("pH Value", ""),
    "ph value": ("pH Value", ""),
    "tds": ("Total Dissolved Solids (TDS)", "mg/L"),
    "total dissolved solids": ("Total Dissolved Solids (TDS)", "mg/L"),
    "turbidity": ("Turbidity", "NTU"),
    "lead": ("Lead (as Pb)", "mg/L"),
    "lead as pb": ("Lead (as Pb)", "mg/L"),
    "arsenic": ("Arsenic (as As)", "mg/L"),
    "arsenic as as": ("Arsenic (as As)", "mg/L"),
    "nitrate": ("Nitrate (as NO3)", "mg/L"),
    "nitrate as no3": ("Nitrate (as NO3)", "mg/L"),
    "e. coli": ("Escherichia coli (E. coli)", "cfu/250ml"),
    "ecoli": ("Escherichia coli (E. coli)", "cfu/250ml"),
    "escherichia coli": ("Escherichia coli (E. coli)", "cfu/250ml"),
    "coliform": ("Coliform Bacteria", "cfu/250ml"),
    "coliform bacteria": ("Coliform Bacteria", "cfu/250ml"),

    # IS 1786 / Steel Parameters
    "carbon": ("Carbon (C) Content", "%"),
    "carbon content": ("Carbon (C) Content", "%"),
    "sulphur": ("Sulphur (S) Content", "%"),
    "sulphur content": ("Sulphur (S) Content", "%"),
    "sulfur": ("Sulphur (S) Content", "%"),
    "phosphorus": ("Phosphorus (P) Content", "%"),
    "phosphorus content": ("Phosphorus (P) Content", "%"),
    "yield strength": ("0.2% Proof Stress / Yield Strength (Fe 500)", "N/mm²"),
    "proof stress": ("0.2% Proof Stress / Yield Strength (Fe 500)", "N/mm²"),
    "0.2% proof stress": ("0.2% Proof Stress / Yield Strength (Fe 500)", "N/mm²"),
    "tensile strength": ("Tensile Strength to Yield Strength Ratio (TS/YS)", "ratio"),
    "tensile ratio": ("Tensile Strength to Yield Strength Ratio (TS/YS)", "ratio"),
    "ts/ys ratio": ("Tensile Strength to Yield Strength Ratio (TS/YS)", "ratio"),
    "elongation": ("Elongation (Gauge Length 5.65√A)", "%"),

    # IS 4984 / HDPE Pipe Parameters
    "density": ("Base Polymer Density at 27°C", "kg/m³"),
    "base polymer density": ("Base Polymer Density at 27°C", "kg/m³"),
    "mfi": ("Melt Flow Index (190°C / 5 kg)", "g/10 min"),
    "melt flow index": ("Melt Flow Index (190°C / 5 kg)", "g/10 min"),
    "carbon black": ("Carbon Black Content", "%"),
    "carbon black content": ("Carbon Black Content", "%"),
    "hydrostatic strength": ("Hydrostatic Strength (100h at 20°C, PE 100)", "MPa hoop stress"),
    "hydrostatic pressure": ("Hydrostatic Strength (100h at 20°C, PE 100)", "MPa hoop stress"),

    # IS 1293 / Electrical Socket Parameters
    "insulation resistance": ("Insulation Resistance at 500V DC", "MΩ"),
    "terminal temperature rise": ("Terminal Temperature Rise under Rated Current", "°C"),
    "temperature rise": ("Terminal Temperature Rise under Rated Current", "°C"),
    "breaking capacity": ("Breaking Capacity (250V AC, 1.25 In)", "cycles"),

    # IS 10500 / Drinking Water (Potable)
    "total hardness": ("Total Hardness (as CaCO3)", "mg/L"),
    "hardness": ("Total Hardness (as CaCO3)", "mg/L"),
    "chloride": ("Chlorides (as Cl)", "mg/L"),
    "chlorides": ("Chlorides (as Cl)", "mg/L"),
    "fluoride": ("Fluoride (as F)", "mg/L"),

    # IS 269 / Portland Cement
    "soundness": ("Soundness (Le Chatelier)", "mm"),
    "initial setting time": ("Initial Setting Time", "minutes"),
    "initial setting": ("Initial Setting Time", "minutes"),
    "final setting time": ("Final Setting Time", "minutes"),
    "final setting": ("Final Setting Time", "minutes"),
    "compressive strength": ("28-Day Compressive Strength", "MPa"),
    "28-day compressive strength": ("28-Day Compressive Strength", "MPa"),
    "insoluble residue": ("Insoluble Residue", "%"),
    "magnesia": ("Magnesia (MgO) Content", "%")
}


class LabReportExtractorService:
    def __init__(self):
        pass

    def _extract_with_gemini_vision(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Extract structured lab test data using Gemini Multimodal Vision if key is available."""
        if not settings.GEMINI_API_KEY:
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_name = settings.GEMINI_MODEL or "gemini-3.8-flash"
            vision_model = genai.GenerativeModel(model_name)

            clean_b64 = image_base64
            if "," in clean_b64:
                clean_b64 = clean_b64.split(",", 1)[1]
            img_bytes = base64.b64decode(clean_b64)
            pil_img = Image.open(io.BytesIO(img_bytes))

            prompt = (
                "You are an expert Bureau of Indian Standards (BIS) Laboratory Compliance Auditor.\n"
                "Examine this physical or digital laboratory test certificate / lab report image carefully.\n"
                "Extract all metadata and observed test parameters into a strict JSON object with these keys:\n"
                "{\n"
                '  "standard_is_code": "e.g. IS 14543 or IS 1786 or IS 4984 (or best match from certificate)",\n'
                '  "product_name": "e.g. Packaged Drinking Water or TMT Rebars or HDPE Pipe",\n'
                '  "manufacturer_name": "e.g. Manufacturer, Brand or Customer Name listed",\n'
                '  "batch_number": "e.g. Batch/Lot/Sample number",\n'
                '  "testing_lab": "e.g. Name of the testing lab or NABL accreditation",\n'
                '  "parameters": [\n'
                '    {\n'
                '      "parameter_name": "Name of parameter (e.g. pH Value, Lead, TDS, Turbidity, Carbon)",\n'
                '      "tested_value": "Numerical or qualitative observed value (e.g. 7.35 or 0.003 or Nil)",\n'
                '      "unit": "e.g. mg/L, NTU, %, N/mm², cfu/250ml",\n'
                '      "notes": "Test method, clause, or observations"\n'
                '    }\n'
                '  ],\n'
                '  "extracted_text_summary": "Full raw text seen on the certificate"\n'
                "}\n"
                "Return ONLY raw JSON, without markdown formatting or backticks."
            )

            from app.core.gemini_manager import gemini_manager
            raw_text, _ = gemini_manager.generate_with_fallback([prompt, pil_img])
            if not raw_text:
                return None
            raw_text = raw_text.strip()
            # Remove ```json ... ``` wrapper if present
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
            
            data = json.loads(raw_text)
            logger.info("Gemini Vision extraction succeeded for lab report.")
            return data
        except Exception as e:
            logger.warning(f"Gemini Vision lab report extraction fallback triggered: {e}")
            return None

    def _extract_with_heuristics_and_regex(self, text: str) -> Dict[str, Any]:
        """
        High-precision rule-based parser that scans text for BIS Standards,
        batch numbers, manufacturer, lab info, and parameter tables.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Standard IS Code detection
        is_code = "IS 14543"  # default
        is_match = re.search(r'\b(IS\s*[:\-]?\s*\d{3,5}(?:\s*:\s*\d{4})?)\b', text, re.IGNORECASE)
        if is_match:
            raw_code = is_match.group(1).upper()
            raw_code = re.sub(r'[:\-]', ' ', raw_code)
            raw_code = re.sub(r'\s+', ' ', raw_code).strip()
            is_code = raw_code
        else:
            # Check for standard names
            t_lower = text.lower()
            if "tmt" in t_lower or "steel" in t_lower or "rebar" in t_lower or "fe 500" in t_lower:
                is_code = "IS 1786"
            elif "hdpe" in t_lower or "polyethylene" in t_lower or "pipe" in t_lower:
                is_code = "IS 4984"
            elif "socket" in t_lower or "plug" in t_lower or "250 v" in t_lower:
                is_code = "IS 1293"
            elif "water" in t_lower:
                is_code = "IS 14543"

        # 2. Product Name detection
        product_name = ""
        matched_std = None
        for k, v in STANDARD_BENCHMARKS.items():
            if k.lower() in is_code.lower():
                matched_std = v
                break

        prod_match = re.search(
            r'(?:product|sample\s*description|commodity|sample\s*name)[:\s\-]+([^\n,;]+)',
            text,
            re.IGNORECASE
        )
        if prod_match and len(prod_match.group(1).strip()) > 3:
            product_name = prod_match.group(1).strip()
        elif matched_std:
            product_name = matched_std["title"]
        else:
            product_name = "Quality Inspected Sample"

        # 3. Manufacturer Name detection
        manufacturer_name = ""
        mfg_match = re.search(
            r'(?:manufacturer|customer|client|sample\s*source|m/s\.?|issued\s*to)[:\s\-]+([^\n;]+)',
            text,
            re.IGNORECASE
        )
        if mfg_match and len(mfg_match.group(1).strip()) > 3:
            manufacturer_name = mfg_match.group(1).strip()
        else:
            manufacturer_name = "Audited Manufacturing Plant"

        # 4. Batch Number detection
        batch_number = ""
        batch_match = re.search(
            r'(?:batch(?:\s*no\.?|\s*number)?|lot(?:\s*no\.?|\s*number)?|sample\s*id|job\s*no\.?)[:\s\-]+([A-Za-z0-9\-_/]+)',
            text,
            re.IGNORECASE
        )
        if batch_match:
            batch_number = batch_match.group(1).strip()
        else:
            import datetime
            batch_number = f"AUDIT-BATCH-{datetime.datetime.utcnow().strftime('%Y%m%d')}-01"

        # 5. Testing Lab detection
        testing_lab = ""
        lab_match = re.search(
            r'(?:testing\s*lab(?:oratory)?|tested\s*by|test\s*house|laboratory\s*name)[:\s\-]+([^\n;]+)',
            text,
            re.IGNORECASE
        )
        if lab_match and len(lab_match.group(1).strip()) > 3:
            testing_lab = lab_match.group(1).strip()
        elif "nabl" in text.lower():
            testing_lab = "NABL Accredited Testing Facility"
        else:
            testing_lab = "BIS Recognized Testing Laboratory"

        # 6. Parameter Extraction
        parameters: List[AuditParameterInput] = []
        found_param_keys = set()

        def normalize_key(s: str) -> str:
            return re.sub(r'[^a-z0-9]', '', s.lower())

        # Phase A: Known Parameter scanning
        for alias, (std_name, default_unit) in KNOWN_PARAMETER_MAP.items():
            pattern = rf'(?i)\b{re.escape(alias)}\b[^\d\n]*?([<>]?\s*[-+]?\d*\.?\d+|nil|absent|not\s*detected|present|pass)'
            match = re.search(pattern, text)
            norm_std = normalize_key(std_name)
            if match and norm_std not in found_param_keys:
                raw_val = match.group(1).strip()
                val_clean = "0" if raw_val.lower() in ["nil", "absent", "not detected"] else raw_val
                
                # Check for unit right after value on same line
                unit = default_unit
                unit_pattern = rf'(?i){re.escape(raw_val)}\s*([a-zA-Z/%²³°][a-zA-Z/%²³°0-9\-_]{{0,14}})'
                unit_match = re.search(unit_pattern, text)
                if unit_match:
                    u_cand = unit_match.group(1).strip()
                    if u_cand.lower() not in ["and", "or", "to", "the", "tested", "clause", "is", "max", "min", "per", "nil", "pass"]:
                        unit = u_cand

                parameters.append(AuditParameterInput(
                    parameter_name=std_name,
                    tested_value=val_clean,
                    unit=unit,
                    notes=f"Detected via OCR from lab report ({alias})"
                ))
                found_param_keys.add(norm_std)
                found_param_keys.add(normalize_key(alias))

        # Phase B: Generic Table/Row scanning (e.g., "Turbidity: 0.45 NTU" or "pH = 7.3")
        for line in lines:
            line_clean = line.strip()
            # Match formats like: Parameter Name | Value | Unit or Parameter: Value Unit
            m = re.match(
                r'^(?:[0-9]{1,2}[\.\)]\s*)?([A-Za-z\s\(\)/_\-\.%]{3,40})\s*[:=\|\t]\s*([<>]?\s*[-+]?\d*\.?\d+|nil|absent|pass)\s*([a-zA-Z/%²³°][A-Za-z/%²³°0-9\-_]{0,14})?',
                line_clean,
                re.IGNORECASE
            )
            if m:
                p_name = m.group(1).strip()
                p_val = m.group(2).strip()
                p_unit = (m.group(3) or "").strip()

                if p_name.lower() in ["batch", "date", "sample", "product", "standard", "code", "report", "lot", "page", "result", "sr no", "sl no"]:
                    continue

                norm_p = normalize_key(p_name)
                # Check if already covered
                already_exists = any(norm_p in k or k in norm_p for k in found_param_keys)
                if not already_exists and len(parameters) < 15:
                    val_clean = "0" if p_val.lower() in ["nil", "absent"] else p_val
                    parameters.append(AuditParameterInput(
                        parameter_name=p_name,
                        tested_value=val_clean,
                        unit=p_unit,
                        notes="Parsed from table row"
                    ))
                    found_param_keys.add(norm_p)

        # Strict rule: Do not inject dummy parameters if no parameters were detected
        return {
            "standard_is_code": is_code,
            "product_name": product_name,
            "manufacturer_name": manufacturer_name,
            "batch_number": batch_number,
            "testing_lab": testing_lab,
            "parameters": parameters,
            "extracted_text_summary": text[:2000]
        }

    def extract_and_verify(
        self,
        raw_text: Optional[str] = None,
        image_base64: Optional[str] = None,
        auto_verify: bool = True
    ) -> ExtractedLabReportData:
        """
        Coordinates Multimodal Vision + Local OCR text processing with strict
        topic/relevance guard and automated BIS compliance audit verification.
        """
        extracted_data: Optional[Dict[str, Any]] = None
        method = "Local Rule-Based & Regex Parser"
        detected_subject = "Lab Test Report"
        corrected_text_summary = ""

        # 1. Clean grammatical and spelling mistakes in raw text if present
        text_to_parse = raw_text or ""
        if text_to_parse.strip():
            corr_result = domain_relevance_guard.clean_and_correct_text(text_to_parse, "audit_compliance")
            text_to_parse = corr_result["corrected_text"]
            corrected_text_summary = text_to_parse

        # 2. If Image is provided, check multimodal subject & feature relevance FIRST
        if image_base64:
            inspection = domain_relevance_guard.inspect_image_for_feature(
                image_base64=image_base64,
                feature="audit_compliance",
                extra_text=text_to_parse
            )
            detected_subject = inspection.get("detected_subject", "Unknown Image")

            if not inspection.get("is_relevant", False):
                logger.info(f"Audit compliance rejected image: {inspection.get('relevance_reason')}")
                return ExtractedLabReportData(
                    status="IRRELEVANT_DATA",
                    is_relevant=False,
                    relevance_reason=inspection.get("relevance_reason", "Uploaded image does not contain laboratory test report data."),
                    detected_subject=detected_subject,
                    corrected_text=corrected_text_summary,
                    standard_is_code="",
                    product_name="Irrelevant Media",
                    manufacturer_name="Unrelated Content",
                    batch_number="N/A",
                    testing_lab="N/A",
                    parameters=[],
                    extracted_text=inspection.get("raw_text") or "Irrelevant image detected: No laboratory test parameters found.",
                    confidence_score=0.98,
                    extraction_method="Domain Relevance Guard",
                    verification=None
                )

            # If image inspection already extracted valid parameters, use them
            if inspection.get("extracted_data") and inspection["extracted_data"].get("parameters"):
                extracted_data = inspection["extracted_data"]
                method = "Gemini Multimodal Vision AI"
            elif inspection.get("raw_text") and not text_to_parse:
                text_to_parse = inspection["raw_text"]

        # 3. If only text provided (no image), check text relevance to audit compliance
        elif text_to_parse.strip():
            is_rel, rel_reason, _ = domain_relevance_guard.check_text_relevance(text_to_parse, "audit_compliance")
            if not is_rel:
                logger.info(f"Audit compliance rejected text: {rel_reason}")
                return ExtractedLabReportData(
                    status="IRRELEVANT_DATA",
                    is_relevant=False,
                    relevance_reason=rel_reason,
                    detected_subject="unrelated text",
                    corrected_text=corrected_text_summary,
                    standard_is_code="",
                    product_name="Irrelevant Text",
                    manufacturer_name="Unrelated Content",
                    batch_number="N/A",
                    testing_lab="N/A",
                    parameters=[],
                    extracted_text=text_to_parse,
                    confidence_score=0.95,
                    extraction_method="Domain Relevance Guard",
                    verification=None
                )

        # 4. If structured data not already populated by vision, use heuristic parser on text
        if not extracted_data:
            if not text_to_parse.strip() and not image_base64:
                return ExtractedLabReportData(
                    status="IRRELEVANT_DATA",
                    is_relevant=False,
                    relevance_reason="No laboratory report text or image was provided.",
                    detected_subject="empty input",
                    corrected_text="",
                    standard_is_code="",
                    product_name="",
                    manufacturer_name="",
                    batch_number="",
                    testing_lab="",
                    parameters=[],
                    extracted_text="",
                    confidence_score=1.0,
                    extraction_method="None",
                    verification=None
                )

            extracted_data = self._extract_with_heuristics_and_regex(text_to_parse)

        # Normalize extracted parameters into AuditParameterInput
        param_objects: List[AuditParameterInput] = []
        raw_params = extracted_data.get("parameters", [])
        for p in raw_params:
            if isinstance(p, dict):
                p_name = p.get("parameter_name") or p.get("name") or "Observed Parameter"
                p_val = str(p.get("tested_value") or p.get("value") or "0")
                p_unit = str(p.get("unit") or "")
                p_notes = str(p.get("notes") or "")
                param_objects.append(AuditParameterInput(
                    parameter_name=p_name,
                    tested_value=p_val,
                    unit=p_unit,
                    notes=p_notes
                ))
            elif isinstance(p, AuditParameterInput):
                param_objects.append(p)

        # If zero parameters could be extracted, do NOT falsely pass or auto-verify
        if not param_objects:
            logger.info("Audit compliance extractor found 0 valid parameters in input.")
            return ExtractedLabReportData(
                status="IRRELEVANT_DATA",
                is_relevant=False,
                relevance_reason="Irrelevant Data Detected: No laboratory test parameters or test values could be parsed from the provided input.",
                detected_subject=detected_subject,
                corrected_text=corrected_text_summary,
                standard_is_code=extracted_data.get("standard_is_code") or "",
                product_name=extracted_data.get("product_name") or "Unverified Product",
                manufacturer_name=extracted_data.get("manufacturer_name") or "N/A",
                batch_number=extracted_data.get("batch_number") or "N/A",
                testing_lab=extracted_data.get("testing_lab") or "N/A",
                parameters=[],
                extracted_text=extracted_data.get("extracted_text_summary") or text_to_parse,
                confidence_score=0.90,
                extraction_method=method,
                verification=None
            )

        std_code = str(extracted_data.get("standard_is_code") or "IS 14543")
        prod_name = str(extracted_data.get("product_name") or "Laboratory Test Sample")
        mfg_name = str(extracted_data.get("manufacturer_name") or "Audited Manufacturer")
        batch_no = str(extracted_data.get("batch_number") or "BATCH-LAB-01")
        test_lab = str(extracted_data.get("testing_lab") or "NABL Accredited Testing Laboratory")
        summary_text = str(extracted_data.get("extracted_text_summary") or text_to_parse or "Laboratory report processed successfully.")

        # 5. Automated Verification if requested
        verification_response: Optional[AuditResponse] = None
        if auto_verify and param_objects:
            try:
                audit_req = AuditRequest(
                    standard_is_code=std_code,
                    product_name=prod_name,
                    manufacturer_name=mfg_name,
                    batch_number=batch_no,
                    testing_lab=test_lab,
                    parameters=param_objects
                )
                verification_response = compliance_audit_engine.perform_audit(audit_req)
                # Pre-generate official PDF
                pdf_report_generator.generate_audit_report(verification_response.audit_id)
                logger.info(f"Auto-verification completed for lab report: {verification_response.overall_verdict}")
            except Exception as audit_err:
                logger.error(f"Auto-verification error: {audit_err}", exc_info=True)

        return ExtractedLabReportData(
            status="SUCCESS",
            is_relevant=True,
            relevance_reason="Relevant laboratory test certificate verified.",
            detected_subject=detected_subject,
            corrected_text=corrected_text_summary,
            standard_is_code=std_code,
            product_name=prod_name,
            manufacturer_name=mfg_name,
            batch_number=batch_no,
            testing_lab=test_lab,
            parameters=param_objects,
            extracted_text=summary_text,
            confidence_score=0.96 if "Gemini" in method else 0.90,
            extraction_method=method,
            verification=verification_response
        )

    extract_lab_report = extract_and_verify


lab_report_extractor_service = LabReportExtractorService()
