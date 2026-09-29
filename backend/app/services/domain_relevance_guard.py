"""
Domain Relevance & Semantic Sanitizer Guard (DomainRelevanceGuard)
Part of GRASK AI (SIH26107).

Core Responsibilities:
1. Multimodal Vision & Image Relevance Validation:
   - Inspects uploaded and camera-captured images for target features:
     * 'audit_compliance': Lab reports, test certificates, parameter tables.
     * 'nutri_score': Packaged food labels, nutritional tables, ingredients lists.
     * 'mark_check': Product packaging showing BIS ISI Mark, CM/L, FSSAI 14-digit, Gold Hallmark HUID, CRS R-Number, or GS1 barcode.
     * 'chat_standards': BIS standards, product quality, QCO orders, Indian Standards.
   - Accurately classifies unrelated subjects (e.g. cars, vehicles, animals, nature, selfies, non-domain items).
   - Prevents state contamination and dummy parameter injection for irrelevant images.

2. Grammar, Spelling, Sentence, and Semantic Error Correction & Fixing:
   - Identifies and corrects typos, misspelled technical terms, and phonetic colloquialisms.
   - Repairs broken sentence structures and ungrammatical expressions.
   - Performs semantic entity alignment (e.g. normalizing standard numbers, parameter names, license codes).

3. Text Topic & Feature Relevance Verification:
   - Determines whether text input is strictly relevant to the active feature.
   - Rejects out-of-scope inputs (cars, movies, sports, programming, personal advice, etc.).
"""

import re
import io
import json
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

from app.core.config import settings
from app.core.gemini_manager import gemini_manager
from app.services.nlp_query_processor import TYPO_CORRECTION_MAP, ROMANIZED_INDIAN_PHONETIC_MAP
from app.services.query_language_guard import OUT_OF_SCOPE_NEGATIVE_PATTERNS, BIS_DOMAIN_KEYWORDS

logger = logging.getLogger("domain_relevance_guard")

# Specific automotive / vehicle negative patterns to definitively identify vehicle photos & queries
AUTOMOTIVE_PATTERNS = [
    r'\b(car|cars|automobile|automobiles|vehicle|vehicles|motorcar|sedan|suv|hatchback|coupe|convertible)\b',
    r'\b(truck|lorry|bus|van|jeep|tractor|scooter|motorcycle|bike|superbike|auto\s*rickshaw)\b',
    r'\b(toyota|honda|hyundai|suzuki|maruti|tata\s*motors|mahindra|ford|chevrolet|bmw|mercedes|audi|volkswagen|skoda|nissan|renault|kia|mg\s*motor|tesla|porsche|ferrari|lamborghini)\b',
    r'\b(engine|gearbox|transmission|accelerator|brake\s*pedal|clutch|steering\s*wheel|windshield|carburetor|speedometer|odometer|exhaust\s*pipe|radiator|alloy\s*wheel|headlight|taillight)\b',
    r'\b(horsepower|torque|mileage\s*of\s*car|car\s*photo|car\s*image|driving\s*speed|car\s*service|petrol\s*tank|diesel\s*engine)\b'
]

# Domain-specific positive keywords for each feature
FEATURE_DOMAIN_KEYWORDS = {
    "audit_compliance": [
        "test", "report", "certificate", "parameter", "tolerance", "limit", "clause",
        "ph", "tds", "lead", "arsenic", "nitrate", "turbidity", "compressive strength",
        "tensile", "elongation", "yield strength", "proof stress", "carbon", "sulphur",
        "phosphorus", "density", "mfi", "soundness", "hardness", "is 14543", "is 1786",
        "is 4984", "is 10500", "is 1293", "is 269", "is 4151", "is code", "standard",
        "nabl", "laboratory", "batch", "lot", "sample", "specimen", "conforming", "deviation",
        "non-conforming", "pass", "fail", "tested", "mg/l", "ntu", "n/mm2", "mpa", "cfu"
    ],
    "nutri_score": [
        "nutrition", "nutritional", "nutri", "facts", "table", "ingredient", "ingredients",
        "energy", "calories", "kcal", "protein", "carbohydrate", "carbs", "sugar", "sugars",
        "added sugar", "total sugar", "fat", "fats", "total fat", "saturated fat", "trans fat",
        "cholesterol", "sodium", "salt", "dietary fiber", "fiber", "palm oil", "palmolein",
        "edible vegetable oil", "refined flour", "maida", "whole wheat", "atta", "preservative",
        "additive", "ins", "e-number", "sweetener", "maltodextrin", "emulsifier", "fssai",
        "serving size", "per 100g", "per serving", "food", "biscuit", "cookie", "chips",
        "snack", "cereal", "noodle", "instant noodle", "juice", "beverage", "sauce", "edible"
    ],
    "mark_check": [
        "cml", "cm/l", "isi", "isi mark", "bis", "fssai", "license", "licence", "registration",
        "huid", "hallmark", "hallmarked", "gold", "silver", "jewellery", "ahc", "purity", "22k",
        "24k", "18k", "916", "crs", "r-number", "r-", "meity", "barcode", "ean", "gtin",
        "890", "qr code", "standard mark", "scheme-i", "scheme-ii", "conformity", "manufacturer"
    ],
    "procurement": [
        "tender", "procurement", "supply", "purchase", "boq", "specification", "bid", "bidding", "gem", "cppp",
        "cable", "cables", "wire", "wires", "pipe", "pipes", "pump", "pumps", "cement", "steel", "rebar", "rebars",
        "tmt", "fe 500", "fe 500d", "fe 550", "structural steel", "fire", "extinguisher", "extinguishers", "helmet",
        "helmets", "shoes", "footwear", "solar", "photovoltaic", "pv module", "battery", "batteries", "transformer",
        "transformers", "led", "luminaire", "street light", "street lights", "switch", "switchgear", "socket", "plug",
        "water", "drinking water", "cylinder", "lpg", "gold", "silver", "huid", "submersible", "conduit", "hdpe",
        "pvc", "gi pipe", "valves", "fasteners", "bolts", "nuts", "medical", "mask", "masks", "syringe", "syringes",
        "is 1786", "is 2062", "is 694", "is 7098", "is 269", "is 4984", "is 15683", "is 2925", "is 15298",
        "is 14286", "is 16046", "is 1180", "is 10322", "is 1293", "is 14543", "is 10500", "is 3196", "is 1417",
        "is 8034", "is 9537", "is 4985", "is 1239", "is 1363", "is 16289", "is 10258", "qco", "isi mark", "scheme-i",
        "scheme-ii", "crs", "bis", "nabl", "quality control order", "hospital", "railway", "school", "building"
    ],
    "chat_standards": BIS_DOMAIN_KEYWORDS
}

# Known non-HUID 6-character English words, car brands, and common terms that should NEVER match HUID
INVALID_HUID_WORDS = {
    "TOYOTA", "HONDA1", "NISSAN", "SUBARU", "DATSUN", "MARUTI", "SUZUKI", "MOTORS",
    "ENGINE", "CAR123", "CAR456", "DRIVE1", "WHEELS", "TIRES1", "YELLOW", "ORANGE",
    "BANANA", "APPLES", "FLOWER", "WINDOW", "LAPTOP", "CODING", "PYTHON", "REPORT",
    "SAMPLE", "SYSTEM", "ONLINE", "ACTIVE", "TESTED", "RANDOM", "NUMBER", "CREDIT",
    "DEBIT1", "SEARCH", "CANCEL", "SUBMIT", "BUTTON", "SELECT", "CHOOSE", "UPDATE",
    "MOBILE", "DEVICE", "CAMERA", "SCREEN", "ROUTER", "SERVER", "CLIENT", "HEADER"
}


class DomainRelevanceGuard:
    """
    Intelligent Input Sanitizer, Error Corrector, and Topic Relevance Guard.
    """

    def clean_and_correct_text(
        self,
        text: str,
        feature: str = "general"
    ) -> Dict[str, Any]:
        """
        Cleans typographical mistakes, fixes grammatical syntax, sentence structure,
        and semantic misalignments.
        Returns:
            {
                "original_text": str,
                "corrected_text": str,
                "corrections_made": List[str],
                "was_corrected": bool
            }
        """
        if not text or not text.strip():
            return {
                "original_text": "",
                "corrected_text": "",
                "corrections_made": [],
                "was_corrected": False
            }

        original = text.strip()
        cleaned = original
        corrections: List[str] = []

        # 1. Dictionary & Phonetic Typo Replacement
        words = re.findall(r'\b[A-Za-z0-9\-_./%]+\b', cleaned)
        for w in words:
            w_lower = w.lower()
            if w_lower in TYPO_CORRECTION_MAP:
                rep = TYPO_CORRECTION_MAP[w_lower]
                cleaned = re.sub(rf'\b{re.escape(w)}\b', rep, cleaned, flags=re.IGNORECASE)
                corrections.append(f"Typo fixed: '{w}' -> '{rep}'")
            elif w_lower in ROMANIZED_INDIAN_PHONETIC_MAP:
                rep = ROMANIZED_INDIAN_PHONETIC_MAP[w_lower]
                cleaned = re.sub(rf'\b{re.escape(w)}\b', rep, cleaned, flags=re.IGNORECASE)
                corrections.append(f"Phonetic resolved: '{w}' -> '{rep}'")

        # 2. Semantic Terminology Normalization based on feature
        if feature == "audit_compliance":
            cleaned = re.sub(r'(?i)\bph\s*val(?:ue)?\b', 'pH Value', cleaned)
            cleaned = re.sub(r'(?i)\btds\b', 'Total Dissolved Solids (TDS)', cleaned)
            cleaned = re.sub(r'(?i)\blead(?:\s*as\s*pb)?\b', 'Lead (as Pb)', cleaned)
            cleaned = re.sub(r'(?i)\barsenic(?:\s*as\s*as)?\b', 'Arsenic (as As)', cleaned)
            cleaned = re.sub(r'(?i)\bnitrate(?:\s*as\s*no3)?\b', 'Nitrate (as NO3)', cleaned)
            cleaned = re.sub(r'(?i)\btensil(?:e)?\s*streng(?:ht|th)\b', 'Tensile Strength', cleaned)
            cleaned = re.sub(r'(?i)\byield\s*streng(?:ht|th)\b', 'Yield Strength', cleaned)
            cleaned = re.sub(r'(?i)\bis\s*(\d{3,5})\b', r'IS \1', cleaned)
        elif feature == "nutri_score":
            cleaned = re.sub(r'(?i)\bingridients\b', 'ingredients', cleaned)
            cleaned = re.sub(r'(?i)\bpalmoil\b', 'palm oil', cleaned)
            cleaned = re.sub(r'(?i)\bsodum\b', 'sodium', cleaned)
            cleaned = re.sub(r'(?i)\bcalores\b', 'calories', cleaned)
            cleaned = re.sub(r'(?i)\bcarbhydrates?\b', 'carbohydrates', cleaned)
            cleaned = re.sub(r'(?i)\bproteen\b', 'protein', cleaned)
            cleaned = re.sub(r'(?i)\bsugr\b', 'sugar', cleaned)
        elif feature == "mark_check":
            cleaned = re.sub(r'(?i)\bcml\s*[:\-]?\s*(\d{7,10})\b', r'CM/L-\1', cleaned)
            cleaned = re.sub(r'(?i)\br\s*[:\-]?\s*(\d{8})\b', r'R-\1', cleaned)
            cleaned = re.sub(r'(?i)\bfssai\s*(?:lic(?:ense)?|no\.?)?\s*[:\-]?\s*(\d{14})\b', r'\1', cleaned)

        # 3. Clean up extra punctuation, consecutive spaces
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        cleaned = re.sub(r'\s+([,.:;?!])', r'\1', cleaned).strip()

        # 4. Use Gemini LLM for grammar & sentence fixes if sentence is complex or broken
        if settings.GEMINI_API_KEY and len(cleaned.split()) >= 3:
            try:
                system_prompt = (
                    "You are a grammar and sentence structure corrector for a technical standards and compliance system. "
                    "Fix grammatical mistakes, spelling errors, sentence fragments, and awkward phrasing while preserving "
                    "the exact technical domain terms, numbers, codes, and intent. "
                    "Do NOT add new information. Return ONLY the corrected text without preamble, quotes, or markdown backticks."
                )
                gemini_text, _ = gemini_manager.generate_with_fallback(
                    prompt=f"Please fix grammar and sentence mistakes in this text:\n\n{cleaned}",
                    system_instruction=system_prompt
                )
                if gemini_text and len(gemini_text.strip()) > 2 and not gemini_text.strip().startswith("{"):
                    candidate = gemini_text.strip().strip('"\'')
                    if candidate.lower() != cleaned.lower():
                        corrections.append("Grammar and sentence structure repaired via AI")
                        cleaned = candidate
            except Exception as e:
                logger.debug(f"Gemini grammar fix skipped: {e}")

        was_corrected = (cleaned.strip() != original.strip())
        return {
            "original_text": original,
            "corrected_text": cleaned,
            "corrections_made": corrections,
            "was_corrected": was_corrected
        }

    def check_text_relevance(
        self,
        text: str,
        feature: str
    ) -> Tuple[bool, str, float]:
        """
        Verifies whether raw or corrected text is relevant to the given feature.
        Returns: (is_relevant: bool, reason: str, confidence: float)
        """
        if not text or not text.strip():
            return False, "Input is empty. Please provide text or an image to analyze.", 1.0

        t_clean = text.lower().strip()

        # Check negative automotive patterns first
        # Exception: For audit_compliance, if an IS standard code (e.g. IS 4151 helmets) and test report headers/parameters are present,
        # it is a statutory laboratory audit certificate, not an unrelated vehicle photo/query.
        has_statutory_lab_report = (
            feature == "audit_compliance" and
            bool(re.search(r'\bis\s*[:\-]?\s*\d{3,5}\b', t_clean)) and
            any(kw in t_clean for kw in ["test", "report", "certificate", "parameter", "pass", "fail", "limit", "tolerance"])
        )

        is_procurement_auto_exemption = (
            feature == "procurement" and
            any(kw in t_clean for kw in [
                "helmet", "helmets", "headgear", "petrol", "diesel", "gasoline", "fuel", "fuels",
                "battery", "batteries", "cable", "cables", "wire", "wires", "pipe", "pipes",
                "specification", "specifications", "tender", "supply", "procurement", "boq",
                "is ", "is:", "isi", "qco", "standard", "bs-vi", "bs6", "ron 91", "ron", "cetane",
                "hsd", "e20", "unleaded", "reflector", "visor", "chin strap"
            ])
        )
        if not has_statutory_lab_report and not is_procurement_auto_exemption:
            for pat in AUTOMOTIVE_PATTERNS:
                if re.search(pat, t_clean):
                    return (
                        False,
                        f"Irrelevant Data Detected: The text relates to automotive vehicles/machinery, which is not applicable to '{feature}'.",
                        0.99
                    )

        # Check general out-of-scope negative patterns
        if feature == "procurement":
            # For procurement, institutional buyers float tenders, provide specs or list engineering parameters
            has_procurement_item = any(kw in t_clean for kw in [
                "cable", "cables", "wire", "wires", "pipe", "pipes", "pump", "pumps", "cement", "steel", "rebar", "rebars",
                "extinguisher", "extinguishers", "helmet", "helmets", "headgear", "shoe", "shoes", "solar", "battery", "batteries",
                "transformer", "transformers", "led", "lighting", "luminaire", "luminaires", "switch", "switches", "socket", "sockets",
                "water", "cylinder", "cylinders", "lpg", "gold", "silver", "submersible", "conduit", "conduits", "hdpe", "pvc",
                "gi pipe", "valve", "valves", "fastener", "fasteners", "bolt", "bolts", "nut", "nuts", "mask", "masks", "syringe",
                "tender", "tenders", "procurement", "supply", "boq", "specification", "specifications", "is ", "is:", "bis", "gem",
                "qco", "isi mark", "fe 500", "fe 550", "fe 600", "fe 500d", "opc", "ppc", "concrete", "rcc", "m20", "m25", "m30", "m35", "m40",
                "tensile", "yield", "elongation", "compressive", "hydrostatic", "blaine", "soundness", "fineness", "viscosity",
                "cetane", "octane", "diesel", "petrol", "gasoline", "fuel", "poultry", "feed", "mash", "toy", "toys",
                "huid", "hallmark", "hallmarking", "karat", "carat", "916", "750", "astm", "eurocode", "iec", "din", "en 197",
                "flammability", "bursting", "discharge", "surge", "insulation", "resistance", "proof stress", "mandrel", "pe-100",
                "pe 100", "pe-80", "pe 80", "sluice", "cast iron", "spun iron", "ductile", "curing", "mix design", "code of practice", "motor spirit", "pet container", "pet preform", "overall migration", "secondary lithium", "power adapter", "transmission tower", "e350", "arsenic", "mercury", "cadmium", "nitrate", "turbidity", "coliform", "pesticide", "tds", "lead pb",
                "motorcycle", "motorbike", "two wheeler", "two-wheeler", "rider", "crash helmet",
                "desktop", "workstation", "laptop", "printer", "scanner", "router", "network switch",
                "electronic equipment", "it equipment", "tablet", "peripheral", "multifunctional",
                "bursting pressure", "discharge duration", "hydrostatic test", "salt spray",
                "lumen maintenance", "luminous efficacy", "harmonic distortion", "power factor",
                "photobiological", "color rendering", "correlated color", "cri", "cct",
                "damp heat", "thermal cycling", "hail impact", "electroluminescence", "bypass diode",
                "uv preconditioning", "light soaking", "irradiance", "stc", "pid",
                "polycyclic aromatic", "pah", "cfpp", "ron", "research octane",
                "charpy", "v-notch", "through-thickness", "ultrasonic testing", "normalizing",
                "potable water", "gravity main", "transmission main", "carbon black", "pe 100",
                "gravity transmission", "water conduit", "spun iron", "centrifugally cast",
                "insulation resistance", "dielectric strength", "locked rotor", "thrust bearing",
                "impeller", "dynamic balancing", "motor winding", "megaohm",
                "contact resistance", "earthing", "earth continuity",
                "xrf", "x-ray fluorescence", "fire rating", "flammability", "voc"
            ])
            if has_procurement_item:
                return True, "Relevant procurement tender or product specification detected.", 0.95

        for pat in OUT_OF_SCOPE_NEGATIVE_PATTERNS:
            if re.search(pat, t_clean):
                return (
                    False,
                    f"Irrelevant Data Detected: The text relates to an out-of-scope topic, which is not applicable to '{feature}'.",
                    0.95
                )

        # Check for positive keywords of the target feature
        expected_keywords = FEATURE_DOMAIN_KEYWORDS.get(feature, BIS_DOMAIN_KEYWORDS)
        matched_keywords = [kw for kw in expected_keywords if kw in t_clean]

        if feature == "procurement":
            if matched_keywords:
                return True, f"Relevant procurement tender item (matched {len(matched_keywords)} keywords).", 0.92
            return False, "Irrelevant Query: Please enter a product description, material grade, or technical specification.", 0.85

        elif feature == "audit_compliance":
            # For audit compliance, must have at least one testing parameter, IS code, or lab term
            has_is_code = bool(re.search(r'\bis\s*[:\-]?\s*\d{3,5}\b', t_clean))
            has_params = any(kw in t_clean for kw in ["ph", "tds", "lead", "turbidity", "carbon", "strength", "density", "test", "report", "value", "batch", "limit", "tolerance"])
            if has_is_code or has_params or len(matched_keywords) >= 1:
                return True, "Relevant laboratory test or compliance data detected.", 0.95
            else:
                return False, "Irrelevant Data Detected: No laboratory test parameters, IS standard references, or quality test data found in text.", 0.90

        elif feature == "nutri_score":
            # For nutri score, must reference food, nutrients, or ingredients
            has_nutrients = any(kw in t_clean for kw in ["energy", "kcal", "protein", "carbohydrate", "fat", "sugar", "sodium", "salt", "ingredients", "nutrition"])
            if has_nutrients or len(matched_keywords) >= 1:
                return True, "Relevant food safety and nutritional data detected.", 0.95
            else:
                return False, "Irrelevant Data Detected: Text does not contain food items, nutritional facts table, or ingredients list.", 0.90

        elif feature == "mark_check":
            # For mark check, must contain a license pattern, barcode, HUID, or mark query
            has_digits = bool(re.search(r'\d{6,14}', t_clean))
            has_mark_keyword = any(kw in t_clean for kw in ["cml", "isi", "fssai", "huid", "hallmark", "crs", "barcode", "ean", "890"])
            # Ensure not a known non-HUID dictionary word like TOYOTA
            clean_token = re.sub(r'[^A-Za-z0-9]', '', text.upper())
            if clean_token in INVALID_HUID_WORDS:
                return False, f"Irrelevant Data Detected: '{clean_token}' is a vehicle brand or common word, not a valid BIS mark or HUID.", 0.98

            if has_digits or has_mark_keyword:
                return True, "Relevant certification mark or license identifier detected.", 0.95
            else:
                return False, "Irrelevant Data Detected: No valid BIS CM/L, FSSAI License, Gold Hallmark, CRS Number, or GS1 Barcode found.", 0.90

        # Default chat_standards check
        if matched_keywords:
            return True, f"Relevant BIS domain query (matched {len(matched_keywords)} keywords).", 0.90

        return False, "Irrelevant Data Detected: Query is outside the Bureau of Indian Standards (BIS) and FSSAI statutory domain.", 0.85

    def inspect_image_for_feature(
        self,
        image_base64: str,
        feature: str,
        extra_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Multimodal visual analysis:
        Inspects image using Gemini Vision to classify subject and test relevance.
        Falls back to local OCR inspection if offline or Gemini fails.
        """
        if not image_base64:
            return {
                "is_relevant": False,
                "detected_subject": "no image provided",
                "relevance_reason": "No image data provided for inspection.",
                "raw_text": "",
                "extracted_data": None
            }

        clean_b64 = image_base64
        mime_type = "image/jpeg"
        if "data:" in clean_b64 and ";base64," in clean_b64:
            parts = clean_b64.split(";base64,")
            detected_mime = parts[0].replace("data:", "").strip()
            if detected_mime:
                mime_type = detected_mime
            clean_b64 = parts[1]
        elif "base64," in clean_b64:
            clean_b64 = clean_b64.split("base64,")[1]

        try:
            img_bytes = base64.b64decode(clean_b64)
            pil_img = Image.open(io.BytesIO(img_bytes))
        except Exception as img_err:
            logger.warning(f"Failed to decode base64 image: {img_err}")
            return {
                "is_relevant": False,
                "detected_subject": "invalid image format",
                "relevance_reason": "Failed to decode image data. Please upload a valid JPEG, PNG, or WebP image.",
                "raw_text": "",
                "extracted_data": None
            }

        # 1. Multimodal Gemini Vision Inspection
        if settings.GEMINI_API_KEY:
            try:
                feature_descriptions = {
                    "audit_compliance": (
                        "A physical or digital laboratory test certificate, chemical/physical test analysis report, "
                        "quality testing parameter sheet, or NABL/BIS lab inspection document. "
                        "Images of automobiles, cars, landscapes, pets, selfies, food items, or non-technical items ARE NOT RELEVANT."
                    ),
                    "nutri_score": (
                        "A packaged food label, nutritional information table (listing energy, protein, fat, carbohydrates, "
                        "sugar, sodium), food ingredients list, or packaged food commodity. "
                        "Images of cars, vehicles, electronics, hardware, machinery, cosmetics, landscapes, or faces ARE NOT RELEVANT."
                    ),
                    "mark_check": (
                        "Product packaging, label, or certificate bearing an authentic BIS Standard Mark (ISI mark), "
                        "CM/L license number, 14-digit FSSAI license, 6-character Gold Hallmark HUID, CRS R-Number, "
                        "or 13-digit GS1 barcode. "
                        "Images of cars, vehicles, landscapes, portraits, or general objects without certification marks ARE NOT RELEVANT."
                    )
                }

                target_desc = feature_descriptions.get(feature, "Bureau of Indian Standards or FSSAI product compliance.")

                prompt = (
                    f"You are a Senior Bureau of Indian Standards (BIS) and FSSAI Quality Inspection Officer.\n"
                    f"Analyze this uploaded image carefully to verify its authenticity and relevance for the '{feature}' feature.\n\n"
                    f"TARGET FEATURE CRITERIA:\n{target_desc}\n\n"
                    f"CRITICAL INSTRUCTIONS:\n"
                    f"1. Identify the detected subject in the image (e.g. 'automobile / car', 'landscape', 'dog / pet', "
                    f"'packaged biscuit label', 'water bottle label', 'cement lab test report', 'gold hallmark engraving', etc.).\n"
                    f"2. Determine 'is_relevant' (boolean: true or false).\n"
                    f"   - If the image depicts a car, vehicle, machine, animal, person, natural landscape, receipt, or "
                    f"any content unrelated to '{feature}', 'is_relevant' MUST BE false.\n"
                    f"   - NEVER fabricate or hallucinate lab parameters, nutrition facts, or licenses for unrelated images!\n"
                    f"3. In 'relevance_reason', provide a clear, polite explanation for the user.\n"
                    f"4. If 'is_relevant' is true, extract all visible text and structured fields into 'extracted_data'. If false, set 'extracted_data' to null.\n\n"
                    f"Return ONLY valid raw JSON with this exact schema (no markdown backticks, no markdown codeblocks):\n"
                    f"{{\n"
                    f'  "is_relevant": true or false,\n'
                    f'  "detected_subject": "Short 2-4 word description of subject",\n'
                    f'  "relevance_reason": "Explanation why it is relevant or irrelevant",\n'
                    f'  "raw_text": "All legible text visible in the image",\n'
                    f'  "extracted_data": null or {{\n'
                    f'    "standard_is_code": "IS XXXX if visible",\n'
                    f'    "product_name": "Product name if visible",\n'
                    f'    "manufacturer_name": "Company/brand if visible",\n'
                    f'    "batch_number": "Batch/lot if visible",\n'
                    f'    "testing_lab": "Lab name if visible",\n'
                    f'    "parameters": [ {{"parameter_name": "...", "tested_value": "...", "unit": "...", "notes": "..."}} ],\n'
                    f'    "extracted_facts": {{"energy_kcal": 0, "protein_g": 0, "carbs_g": 0, "total_sugar_g": 0, "added_sugar_g": 0, "total_fat_g": 0, "saturated_fat_g": 0, "trans_fat_g": 0, "sodium_mg": 0, "fiber_g": 0}},\n'
                    f'    "ingredients_list": ["..."],\n'
                    f'    "barcode": "13-digit barcode or null",\n'
                    f'    "cml": "CM/L or null",\n'
                    f'    "fssai": "14-digit FSSAI or null",\n'
                    f'    "huid": "6-character HUID or null",\n'
                    f'    "crs": "CRS R-Number or null"\n'
                    f'  }}\n'
                    f"}}"
                )

                raw_resp, model_used = gemini_manager.generate_with_fallback([
                    prompt,
                    {"mime_type": mime_type, "data": img_bytes}
                ])

                if raw_resp:
                    clean_text = raw_resp.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.startswith("```"):
                        clean_text = clean_text[3:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    clean_text = clean_text.strip()

                    parsed = json.loads(clean_text)
                    is_rel = bool(parsed.get("is_relevant", False))
                    subj = str(parsed.get("detected_subject", "Unidentified Image"))
                    reason = str(parsed.get("relevance_reason", ""))
                    extracted = parsed.get("extracted_data")

                    # Extra safety check: if subject contains vehicle/car keywords, force is_relevant=False
                    subj_lower = subj.lower()
                    if any(car_kw in subj_lower for car_kw in ["car", "vehicle", "automobile", "truck", "bike", "sedan", "suv"]):
                        is_rel = False
                        reason = f"Irrelevant Data Detected: The uploaded image shows a {subj}, which does not contain any data for {feature}."
                        extracted = None

                    logger.info(f"Gemini Vision Relevance ({feature}): is_relevant={is_rel}, subject='{subj}'")
                    return {
                        "is_relevant": is_rel,
                        "detected_subject": subj,
                        "relevance_reason": reason,
                        "raw_text": str(parsed.get("raw_text", "")),
                        "extracted_data": extracted if is_rel else None
                    }
            except Exception as v_err:
                logger.warning(f"Gemini Vision image inspection failed, executing local fallback: {v_err}")

        # 2. Local Fallback Inspection via OCR Text
        ocr_text = extra_text or ""
        if not ocr_text:
            try:
                import subprocess, tempfile, os
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                    tf.write(img_bytes)
                    tmp_path = tf.name
                try:
                    node_script = """
                    const { createWorker } = require('./frontend/node_modules/tesseract.js');
                    async function run() {
                        const worker = await createWorker('eng');
                        const res = await worker.recognize(process.argv[1]);
                        process.stdout.write(res.data.text);
                        await worker.terminate();
                    }
                    run();
                    """
                    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                    ocr_proc = subprocess.run(
                        ["node", "-e", node_script, tmp_path],
                        capture_output=True, text=True, timeout=25, cwd=project_root
                    )
                    if ocr_proc.returncode == 0 and ocr_proc.stdout:
                        ocr_text = ocr_proc.stdout.strip()
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
            except Exception as ocr_err:
                logger.debug(f"Local OCR inspection error: {ocr_err}")

        if not ocr_text or len(ocr_text.strip()) < 10:
            return {
                "is_relevant": False,
                "detected_subject": "non-text image / object",
                "relevance_reason": (
                    f"Irrelevant Data Detected: No legible laboratory parameters, nutrition facts, "
                    f"or certification marks found in the uploaded image. Please ensure the image is clear and relevant."
                ),
                "raw_text": ocr_text,
                "extracted_data": None
            }

        # Check OCR text against feature relevance
        is_rel, reason, _ = self.check_text_relevance(ocr_text, feature)
        return {
            "is_relevant": is_rel,
            "detected_subject": "document / packaging image" if is_rel else "unrelated visual media",
            "relevance_reason": reason,
            "raw_text": ocr_text,
            "extracted_data": None
        }


# Singleton instance
domain_relevance_guard = DomainRelevanceGuard()
