import os
import re
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.models.schemas import ChatMode, ChatResponse, Citation, ChatMessage
from app.services.vector_store import vector_store_service
from app.services.online_standards_resolver import online_standards_resolver
from app.services.multilingual_translator import multilingual_translator
from app.services.standards_graph import standards_graph_service
from app.services.hybrid_retriever import hybrid_retriever_service
from app.services.bis_services_directory import search_testing_laboratories, TESTING_LABORATORIES_DIRECTORY, BIS_SERVICES_DIRECTORY
from app.services.nlp_query_processor import nlp_query_processor
from app.services.fssai_food_safety_service import fssai_food_safety_service
from app.services.bis_statutory_topics_service import bis_statutory_topics_service
from app.services.dual_verification_engine import dual_verification_engine
from app.services.query_language_guard import query_language_guard
from app.core.database import log_query

from app.core.security_guard import (
    sanitize_and_shield_input,
    anonymize_metadata,
    detect_multilingual_intent,
    detect_query_disambiguation,
    CARTOON_ALIASES
)

logger = logging.getLogger(__name__)

# Configure Google GenAI if key is present
try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        GENAI_AVAILABLE = True
    else:
        GENAI_AVAILABLE = False
except Exception:
    GENAI_AVAILABLE = False


STANDARDIZED_REFUSAL = (
    "**Official Notice from BIS Intelligent Assistant:**\n\n"
    "The Bureau of Indian Standards (BIS) repository is strictly dedicated to authoritative Indian Standards (IS Codes), "
    "statutory certification schemes (Scheme-I ISI Mark, Scheme-II CRS, Hallmarking, Eco-Mark, FMCS), "
    "laboratory test methods, quality control orders (QCO), and consumer safety benchmarks under the BIS Act 2016.\n\n"
    "Your inquiry falls outside this standardization domain. To ensure absolute data integrity and legal grounding, "
    "responses are restricted to verified Bureau of Indian Standards specifications.\n\n"
    "**Recommended Actions:**\n"
    "1. Inquire about any Indian Standard (e.g. `IS 14543` Water, `IS 1786` Steel, `IS 2796` Petrol, `IS 1374` Poultry Feeds).\n"
    "2. Consult the official BIS Manakonline Portal: [www.manakonline.in](https://www.manakonline.in).\n"
    "3. Use the BIS Care Mobile App to verify product license (CM/L) authenticity."
)


INDUSTRY_SYSTEM_PROMPT = """
You are the Bureau of Indian Standards (BIS) Official Technical Assistant & Industrial Certification Advisor for Industry, Manufacturers, Testing Laboratories, and Quality Engineers.
Your mission is to provide concise, clause-grounded, highly accurate guidance tailored SPECIFICALLY to the client's business inquiry and product domain.

CRITICAL INSTRUCTIONS FOR INDUSTRIAL RESPONSES:
1. Business Focus: Answer ONLY for the specific product or business domain the client inquired about (e.g. packaged water, TMT steel, HDPE pipes, electrical sockets, helmets). Do NOT dump unrequested, generic standards.
2. Multilingual & Romanized Dialect Recognition: Accurately interpret Romanized Indian dialect terminology across Telugu, Hindi, Tamil, Kannada, etc. (e.g., 'paala dukanam' = Milk Shop / Dairy Booth, 'sariya dukanam' = TMT Steel Rebar Shop, 'simantu dukanam' = Cement Shop, 'bangaaram dukanam' = Gold Jewellery Store).
3. Cross-Domain Negative Restrictions: Under NO circumstances cross product domains:
   - For dairy or food (milk, paneer, ghee, water, beverages), cite ONLY FSSAI and relevant food standards (FSSAI FoSCoS, IS 1224, IS 10484, IS 14543). NEVER cite cement (IS 269), steel (IS 1786), or electrical standards!
   - For civil/construction (cement, steel rebars, concrete), cite ONLY civil standards (IS 269, IS 1786, IS 456). NEVER cite food or jewelry standards!
   - For gold/jewelry, cite ONLY BIS Gold Hallmarking, 6-digit HUID, and IS 1417. NEVER cite cement or food standards!
   - If retrieved context contains unrelated standards from another domain, DISCARD that unrelated context completely and adhere strictly to the user's intended product domain!
4. Certification Scheme Specificity: Clearly specify the exact statutory BIS Certification Scheme applicable:
   - **Scheme-I (ISI Mark Scheme)**: Mandatory/Voluntary Product Certification for domestic manufacturing.
   - **Scheme-II (Compulsory Registration Scheme - CRS)**: Self-declaration of conformity for electronics and IT goods.
   - **Scheme-IV (Certificate of Conformity)**: Batch-wise conformity certification.
   - **FMCS**: Foreign Manufacturers Certification Scheme.
   - **Hallmarking**: For precious metal articles (Gold/Silver).
   - **Eco-Mark Scheme**: For eco-friendly products meeting environmental criteria.
5. Grounding & Zero Hallucination: Cite exact numerical limits, chemical bounds, units, tolerances, and referenced standard test methods (e.g., IS 3025, IS 1608, IS 228).
6. Table Formatting: MUST present technical parameters in a clean MARKDOWN TABLE with columns:
   `| Parameter / Characteristic | Permissible Limit / Requirement | Test Method (IS Code) |`
7. Structure:
   - **🎯 Business Assessment & Statutory Framework** (Statutory Scheme, Enforcing Authorities, QCO Status)
   - **📊 Mandatory Technical Specifications & Permissible Limits** (Use structured markdown tables)
   - **🧪 In-House Testing Laboratory & Quality Control Requirements** (Required test equipment, approved chemist/personnel, sampling records)
   - **💡 Actionable Next Steps for Certification** (Step-by-step Manakonline setup and verification roadmap)
"""

CONSUMER_SYSTEM_PROMPT = """
You are the Bureau of Indian Standards (BIS) Citizen & Consumer Protection Guide.
Your mission is to provide simplified, actionable, citizen-friendly advice to help Indian consumers understand safety standards, product quality, and their legal rights under the BIS Act 2016.

GUIDELINES:
1. Direct Focus: Address the consumer's exact product question directly in plain language without unnecessary technical jargon.
2. Dialect & Transliteration Awareness: Interpret Romanized Indian words accurately (e.g. 'paala' = milk, 'sariya' = steel rebar, 'simantu' = cement, 'bangaaram' = gold, 'theega' = wire).
3. Cross-Domain Negative Restrictions: Never cite civil/industrial manufacturing standards (like cement IS 269) for food, dairy, or consumer household goods!
4. Citizen Safety: Clearly explain WHY the standard matters for health and consumer safety.
5. The 4-Point Safety Checklist:
   - Point 1: Authentic BIS Mark (ISI Mark, 6-digit laser HUID for Gold, or CRS Logo for Electronics).
   - Point 2: License Number: 7 or 8-digit `CM/L-XXXXXXXX`, 6-digit `HUID`, or `R-XXXXXXXX`. Emphasize: An ISI logo without a CM/L number is 100% fake and illegal!
   - Point 3: Applicable Indian Standard number (e.g. `IS 14543`).
   - Point 4: Packaging and seal integrity: Tamper-evident seals, batch numbers, manufacturing/expiry dates, FSSAI logo (for food), and MRP.
6. Consumer Red Flags & Health/Safety Hazards: Real-world scam indicators and health hazards of substandard goods.
7. Verification & Grievances: Explain how consumers can verify the authentic mark using the official **BIS Care Mobile App** and file complaints on the National Consumer Helpline (1915).
8. Structure:
   - **🛡️ Plain English Summary: What Every Citizen Must Know**
   - **🔍 What Indian Consumers Must Check (The 4-Point Safety Checklist)**
   - **⚠️ Consumer Red Flags & Health Hazards**
   - **📲 How to Verify Authenticity on the BIS Care App & Report Fake Products**
"""


class RAGEngine:
    def __init__(self):
        self.min_similarity_threshold = 0.38

    def _format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Citation], List[Dict[str, Any]]]:
        citations: List[Citation] = []
        table_refs: List[Dict[str, Any]] = []
        context_parts = []

        for idx, chunk in enumerate(retrieved_chunks):
            is_code = chunk.get("is_code", "IS Code")
            doc_title = chunk.get("doc_title", "Indian Standard")
            clause = chunk.get("clause", "Clause")
            page_num = chunk.get("page_number", 1)
            sim_score = chunk.get("similarity", 0.0)
            is_table = chunk.get("is_table", False)
            table_num = chunk.get("table_number")
            table_title = chunk.get("table_title")

            snippet = chunk.get("text", "")[:350] + "..." if len(chunk.get("text", "")) > 350 else chunk.get("text", "")

            citation = Citation(
                is_code=is_code,
                title=doc_title,
                clause=clause,
                page_number=page_num,
                snippet=snippet,
                similarity_score=sim_score,
                is_table=is_table,
                table_number=table_num
            )
            citations.append(citation)

            if is_table and chunk.get("table_data"):
                table_refs.append({
                    "is_code": is_code,
                    "table_number": table_num or "Table",
                    "table_title": table_title or "Specifications",
                    "clause": clause,
                    "page_number": page_num,
                    "columns": chunk["table_data"].get("columns", []),
                    "rows": chunk["table_data"].get("rows", []),
                    "markdown": chunk["table_data"].get("markdown", "")
                })

            context_parts.append(
                f"--- [EXCERPT {idx+1}] ---\n"
                f"STANDARD: {is_code} | TITLE: {doc_title}\n"
                f"CLAUSE: {clause} | PAGE: {page_num}\n"
                f"{chunk.get('text')}\n"
            )

        context_str = "\n\n".join(context_parts)
        return context_str, citations, table_refs

    def _resolve_business_domain_standards(self, query: str) -> Optional[Dict[str, Any]]:
        """Maps any business or consumer inquiry in any Indian language, dialect, or typo to official BIS Standards."""
        q = query.lower()
        concept_key, canonical_name = detect_multilingual_intent(q)
        tokens = set(re.findall(r'[a-zA-Z0-9\u0900-\u097F\u0C00-\u0C7F\u0B80-\u0BFF\u0980-\u09FF\u0A80-\u0AFF\u0D00-\u0D7F]+', q))
        
        # 000a. Paints, Synthetic Enamels, Plastic Emulsions & Wall Coatings (IS 15489 / IS 2932 / IS 5410 / IS 428)
        if (concept_key == "paints_coatings" or any(k in q for k in [
            "rangu", "rangupani", "rangu pani", "paint", "paints", "painting", "enamel",
            "distemper", "emulsion", "wall putty", "putty", "cement paint", "varnish",
            "రంగు", "రంగు పని", "రంగులు", "रंग", "पेंट", "सफेदी", "is 15489", "is15489",
            "is 2932", "is2932", "is 5410", "is5410", "is 428", "is428"
        ])) and not any(k in q for k in ["iron", "sariya", "medicine", "meat", "poultry"]):
            return {
                "domain": "Paints, Synthetic Enamels, Plastic Emulsions & Wall Coatings Industry",
                "standards": [
                    {"code": "IS 15489:2004", "title": "Plastic Emulsion Paint - Specification", "clause": "Clause 5.0 Lead Limit (< 90 ppm), Scrub Resistance & Drying Time"},
                    {"code": "IS 2932:2003", "title": "Enamel, Synthetic, Exterior: (a) Undercoating, (b) Finishing - Specification", "clause": "Clause 4.0 Flash Point, Viscosity & Gloss Retention"},
                    {"code": "IS 5410:1992", "title": "Cement Paint - Specification", "clause": "Clause 5.0 Water Resistance, Adhesion & Accelerated Weathering"},
                    {"code": "IS 428:2013", "title": "Distemper, Oil Bound - Specification", "clause": "Clause 4.0 Fastness to Light & Washability"},
                    {"code": "IS 101", "title": "Methods of Sampling and Test for Paints, Varnishes and Related Products", "clause": "Part 8/Sec 5 Lead Content Estimation"}
                ],
                "scheme": "BIS Scheme-I (Mandatory ISI Mark) under the Paints and Allied Products (Quality Control) Order",
                "statutory_bodies": "Bureau of Indian Standards (BIS CHD 20 - Paints, Varnishes and Related Products) & Ministry of Environment, Forest and Climate Change (MoEFCC)",
                "table_markdown": (
                    "| Quality Parameter / Characteristic | Statutory Requirement (IS 15489 / IS 2932) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Lead Content Restriction | Maximum 90 ppm (0.009% by mass) (Zero tolerance for excess lead) | IS 101 (Part 8/Sec 5) ICP-OES / AAS |\n"
                    "| Drying Time (Surface Dry) | Maximum 30 to 45 minutes | IS 101 (Part 3/Sec 1) |\n"
                    "| Drying Time (Hard Dry) | Maximum 4 hours (Emulsion) / 18 hours (Enamel) | IS 101 (Part 3/Sec 1) |\n"
                    "| Wet Scrub Resistance | Minimum 1000 cycles (Premium) / 500 cycles (Regular) | IS 15489 Annex C Washability Test |\n"
                    "| Flash Point (Synthetic Enamels) | Not below 35 °C (Classified non-hazardous storage) | IS 101 (Part 1/Sec 6) Abel Closed Cup |\n"
                    "| Fineness of Grind | Minimum 6 Hegman Units (Smooth aerosol/brush atomization) | IS 101 (Part 3/Sec 5) |\n"
                    "| Hiding Power / Contrast Ratio | Not less than 0.90 at recommended film spread | IS 101 (Part 4/Sec 2) Reflectance |\n"
                    "| Volatile Organic Compounds (VOC) | Low VOC formulation (< 50 g/L for green building ratings) | Gas Chromatography (ISO 11890) |"
                ),
                "qc_requirements": (
                    "- **Atomic Absorption Spectrophotometer (AAS) / ICP-OES:** Laboratory instrument for verifying mandatory lead limits (< 90 ppm) in every production batch.\n"
                    "- **Wet Abrasion Scrub Tester:** Mechanized reciprocating brush machine for ASTM/IS scrub cycle validation.\n"
                    "- **Abel Closed Cup Flash Point Tester:** Mandatory safety instrument for solvent-based synthetic enamels.\n"
                    "- **Cryptometer & Hegman Gauge:** For measuring pigment dispersion, grind fineness, and film opacity."
                ),
                "licensing_steps": [
                    "Formulate paint batches with lead-free driers and certified non-toxic organic/inorganic pigments meeting the 90 ppm lead restriction.",
                    "Set up an in-house chemical testing laboratory equipped with AAS/ICP for lead testing, grind gauge, viscosity cups, and drying test ovens.",
                    "Submit Scheme-I ISI Mark application on the [BIS Manakonline Portal](https://www.manakonline.in) with manufacturing flow chart and recipe disclosures.",
                    "Undergo BIS factory audit, in-house lab verification, and independent NABL sample testing to obtain the CM/L license number."
                ],
                "consumer_summary": (
                    "When painting homes, walls, or furniture, substandard decorative paints frequently contain toxic neurotoxic lead pigments and "
                    "flammable heavy solvents. Under the Regulation of Lead contents in Household and Decorative Paints Rules and DPIIT Quality Control Orders, "
                    "it is legally MANDATORY that all household decorative paints, plastic emulsions (IS 15489), and synthetic enamels (IS 2932) carry the "
                    "official BIS ISI mark and maintain lead levels strictly below 90 ppm to protect children and families from irreversible lead poisoning."
                ),
                "consumer_checklist": (
                    "1. **Check BIS ISI Mark & CM/L:** Look for the rectangular ISI mark with the 7-digit CM/L license number stamped clearly on the paint container.\n"
                    "2. **Verify Lead Safe Declaration:** Ensure the label explicitly states: **'Lead Content does not exceed 90 ppm'** or displays the **'Lead Safe'** certification.\n"
                    "3. **Check Correct IS Standard:** Look for `IS 15489` (Plastic Emulsion for interior/exterior walls) or `IS 2932` (Gloss Synthetic Enamel for doors/grills).\n"
                    "4. **Smell & Pungency Check:** Beware of cheap unbranded paint thinners emitting overpowering petroleum/benzene fumes that cause acute headaches.\n"
                    "5. **Batch Number & Shelf Life:** Ensure the batch number, manufacturing date, and best-before shelf life (typically 24–36 months) are intact."
                ),
                "consumer_red_flags": (
                    "- Paint containers without an ISI mark or without a valid 7-digit CM/L license number.\n"
                    "- Paints with no lead statement or labeled 'for industrial use only' being sold for domestic home interior painting.\n"
                    "- Loose paint sold in unsealed secondhand tins at local hardware shops.\n"
                    "- Paint peeling, chalking, or blistering within weeks of application due to substandard binder resins."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care Mobile App**.\n"
                    "2. Select **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number printed on the paint bucket.\n"
                    "3. Confirm that the licensee name, brand name, and standard validity (IS 15489 / IS 2932) are active and authentic.\n"
                    "4. If a paint brand sells toxic lead-adulterated paint without an ISI mark, report the violation directly through the BIS Care App or call **1915**."
                )
            }

        # 000. Timber, Plywood, Wooden Flush Doors & Carpentry (IS 303 / IS 710 / IS 2202 / IS 1331)
        if (concept_key == "timber_carpentry" or any(k in q for k in [
            "chekka", "chekkapani", "chekka pani", "carpentry", "carpenter", "woodwork",
            "wood work", "plywood", "flush door", "flush doors", "wooden door", "timber",
            "lakdi", "badhai", "tarkhan", "maram", "maravelai", "చెక్క", "చెక్క పని",
            "కలప", "బడగ", "లకడీ", "लकड़ी", "बढ़ई", "is 303", "is303", "is 710", "is710",
            "is 2202", "is2202", "is 1331", "is1331"
        ])) and not any(k in q for k in ["iron", "sariya", "cement", "medicine"]):
            return {
                "domain": "Timber, Plywood, Wooden Flush Doors & Carpentry Industry",
                "standards": [
                    {"code": "IS 303:1989", "title": "Plywood for General Purposes - Specification", "clause": "Clause 5.0 Moisture, Glue Shear & Preservative Treatment"},
                    {"code": "IS 710:2010", "title": "Marine Plywood - Specification", "clause": "Clause 6.0 Boiling Water Proof (BWP) Adhesive & Tensile Strength"},
                    {"code": "IS 2202 (Part 1):1999", "title": "Wooden Flush Door Shutters (Solid Core Type) - Specification", "clause": "Clause 7.0 End Immersion, Knife Test & Impact Resistance"},
                    {"code": "IS 1331:1971", "title": "Specification for Cut Sizes of Timber", "clause": "Clause 4.0 Dimensions, Seasoning & Permissible Moisture"},
                    {"code": "IS 3629:1986", "title": "Specification for Structural Timber in Building", "clause": "Clause 5.0 Stress Grading & Knot Restrictions"}
                ],
                "scheme": "BIS Scheme-I (Mandatory ISI Mark) under Plywood & Wooden Flush Doors Quality Control Order (QCO)",
                "statutory_bodies": "Bureau of Indian Standards (BIS CED 09 / CED 20) & Ministry of Commerce and Industry (DPIIT)",
                "table_markdown": (
                    "| Quality Parameter / Characteristic | Statutory Requirement (IS 303 & IS 710) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Moisture Content (General Plywood) | 5.0% to 15.0% by mass | IS 1734 (Part 1) Oven Drying |\n"
                    "| Moisture Content (Marine Plywood) | 5.0% to 13.0% by mass | IS 1734 (Part 1) Gravimetric |\n"
                    "| Glue Shear Strength (Dry State) | Minimum 1350 N (MR Grade) / 1450 N (BWP Grade) | IS 1734 (Part 4) Shear Test |\n"
                    "| Water Resistance (BWP Grade) | Withstand 72 hours boiling in water without delamination | IS 710 Clause 6.1 (Boiling Test) |\n"
                    "| Mycological Test | No fungal decay after 3 weeks incubation at 27°C | IS 1734 (Part 6) Fungal Resistance |\n"
                    "| Tensile Strength (Along Grain) | Minimum 42.0 N/mm² (Marine Grade) | IS 1734 (Part 9) UTM Tensile |\n"
                    "| End Immersion Test (Flush Doors) | No delamination after 15 min immersion in water at 27°C | IS 2202 (Part 1) Annex D |\n"
                    "| Knife Test (Adhesion between Plies) | Pass Rating >= 4 (Excellent bonding of core veneers) | IS 1734 (Part 5) Knife Test |\n"
                    "| Preservative Retention (Borer Proof) | Minimum 12.0 kg/m³ Copper-Chrome-Boron (CCB) | IS 401 Vacuum Pressure Impregnation |\n"
                    "| Formaldehyde Emission Class | Class E1 (<= 0.124 mg/m³ air) | Desiccator Method / European Norm |"
                ),
                "qc_requirements": (
                    "- **Boiling Water Immersion Bath:** Thermostatically controlled 100°C water bath for 72-hour continuous BWP delamination testing.\n"
                    "- **Universal Testing Machine (UTM):** Calibrated tensiometer for glue adhesion shear strength and modulus of elasticity.\n"
                    "- **Vacuum Pressure Impregnation Plant:** Chemical treatment cylinder with CCB/CCA wood preservatives to prevent borer and termite attacks.\n"
                    "- **Knife Test Rig & Micrometer:** For veneer peel adhesion assessment and thickness tolerance checks (± 5%)."
                ),
                "licensing_steps": [
                    "Fabricate commercial plywood and flush door prototypes conforming to IS 303, IS 710, or IS 2202 in an established timber mill.",
                    "Set up an in-house quality testing laboratory with boiling water bath, UTM glue shear tester, and moisture balance.",
                    "Apply for Scheme-I ISI Mark on the [BIS Manakonline Portal](https://www.manakonline.in) under the Mandatory Wood-Based Boards QCO.",
                    "Undergo BIS factory audit, sampling verification, and independent NABL lab witness testing to receive the CM/L license number."
                ],
                "consumer_summary": (
                    "When buying plywood, flush doors, and woodwork for home interiors and furniture, substandard timber delaminates, warps with humidity, "
                    "and becomes infested with borers and termites within months. BIS ISI marking under IS 303 (Commercial MR Plywood) and IS 710 (Boiling Water Proof Marine Plywood) "
                    "is mandatory under DPIIT Quality Control Orders to guarantee water resistance and long-lasting structural strength."
                ),
                "consumer_checklist": (
                    "1. **Check Authentic ISI Mark & CM/L:** Look for the rectangular ISI logo and valid 7-digit CM/L number stamped indelibly on every plywood sheet.\n"
                    "2. **Verify Correct IS Code:** Look for `IS 303` (Commercial MR/BWR Plywood for dry areas) or `IS 710` (Marine Grade for kitchens and bathrooms).\n"
                    "3. **Inspect Ply Edges (No Core Gaps):** High quality calibrated plywood has zero hollow gaps between cross-band veneers.\n"
                    "4. **No Heavy Chemical Pungency:** Genuine E1 grade plywood does not emit eye-stinging toxic formaldehyde fumes.\n"
                    "5. **Boiling Water Spot Test:** Submerge a scrap corner in boiling water for 3 hours; substandard commercial ply swells and splits immediately."
                ),
                "consumer_red_flags": (
                    "- Plywood stamped with fake ink stickers or without a 7-digit CM/L license number.\n"
                    "- Sheets with visible core voids, uneven thickness, or warping when rested against a wall.\n"
                    "- Commercial ply falsely sold as 'Marine 710' at cheap unbranded prices.\n"
                    "- Plywood emitting overpowering, suffocating chemical fumes (excess toxic urea formaldehyde glue)."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App** on your smartphone.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit license number from the plywood stamp.\n"
                    "3. Verify manufacturer name, mill location, and standard validity (IS 303 / IS 710).\n"
                    "4. Report fake ISI-marked plywood or counterfeit wood brands on the app or call the **National Consumer Helpline** at **1915**."
                )
            }

        # 00. Palak Paneer, Fresh Paneer (IS 10484) & Green Leafy Vegetables Food Safety
        if any(k in q for k in ["paneer", "panneer", "panner", "palak", "cottage cheese"]) or (any(k in q for k in ["eating", "eat"]) and any(k in q for k in ["paneer", "palak", "curry"])):
            return {
                "domain": "Palak Paneer, Fresh Paneer (IS 10484) & Culinary Food Safety",
                "standards": [
                    {"code": "IS 10484:1983", "title": "Paneer - Specification", "clause": "Clause 4.0 Composition, Fat, Moisture & Hygiene"},
                    {"code": "FSSAI Dairy Regs 2.1.1", "title": "FSSAI Food Safety and Standards (Dairy Products) Regulations", "clause": "Standard for Paneer and Chhana"},
                    {"code": "IS 1224 (Part 1):1977", "title": "Determination of Fat in Whole Milk, Evaporated and Condensed Milk", "clause": "Clause 5.0 Gerber Fat Estimation"},
                    {"code": "IS 2491:2013", "title": "Food Hygiene - General Principles - Code of Practice", "clause": "Clause 6.0 Thermal Processing & Kitchen Hygiene"},
                    {"code": "FSSAI DART Manual", "title": "Detect Adulteration with Rapid Test (DART) - Dairy & Vegetables", "clause": "Starch Iodine Test & Malachite Green Dye Test"}
                ],
                "scheme": "FSSAI Statutory Food Safety Framework & BIS Scheme-I (Dairy Standards FAD 19)",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (BIS)",
                "table_markdown": (
                    "| Quality Parameter / Characteristic | Statutory Requirement (IS 10484 & FSSAI) | Test Method / Protocol |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Moisture Content | Maximum 60.0% by mass (Paneer) / 70.0% (Chhana) | IS 2785 / Gravimetric Drying |\n"
                    "| Milk Fat (Dry Matter Basis) | Not less than 50.0% by mass (Full Fat) / < 15.0% (Low Fat) | IS 1224 (Part 1) / Gerber Method |\n"
                    "| Starch & Foreign Flour | Completely Absent / Zero Tolerance | FSSAI DART (Iodine Solution Test) |\n"
                    "| Detergent, Urea & Neutralizers | Strictly Prohibited / Absent | DART Lather & Neutralizer Strip Test |\n"
                    "| Spinach Pesticide Residue | Compliant with FSSAI Maximum Residue Limits (MRLs) | Soak in 2% salt water or 1% baking soda for 15 min |\n"
                    "| Spinach Artificial Green Dye (Malachite Green) | Strictly Prohibited / Carcinogenic | FSSAI DART (Wet white cotton swab test) |\n"
                    "| Cooking Core Temperature | Minimum 75 °C thoroughly boiled | Thermal destruction of vegetative pathogens & E. coli |\n"
                    "| Coliform Bacteria | Max 90 CFU/g | IS 5401 |\n"
                    "| E. coli & Salmonella | Absent in 25g | IS 15185 / IS 5887 |"
                ),
                "qc_requirements": (
                    "- **Milk Source & Fat Standardization:** Paneer must be manufactured exclusively from potable milk meeting IS 1224 standards with zero synthetic adulterants.\n"
                    "- **Moisture & Texture Control:** Pressing and coagulation must maintain moisture below 60% without the addition of starch or hydrocolloids.\n"
                    "- **Cold Chain Maintenance:** Finished paneer blocks must be stored below 4 °C to inhibit psychrotrophic bacterial proliferation.\n"
                    "- **In-House Testing Facilities:** Gerber fat centrifuge, moisture oven, Gerber butyrometers, and iodine testing reagents."
                ),
                "licensing_steps": [
                    "Obtain FSSAI Manufacturing License (State or Central based on daily milk handling capacity) under Category 01.2 (Dairy) via FoSCoS.",
                    "Implement Schedule 4 hygiene standards complying with IS 2491 (Food Hygiene - Code of Practice).",
                    "Conduct regular batch microbiological and chemical testing at an FSSAI-notified NABL accredited laboratory.",
                    "Ensure vacuum-sealed packaging displaying 14-digit FSSAI license number, nutritional breakdown, and storage temperature <= 4 °C."
                ],
                "consumer_summary": (
                    "When consuming Palak Paneer, Indian consumers must verify both **Paneer authenticity** (governed by IS 10484 and FSSAI Dairy regulations) "
                    "and **Spinach (Palak) safety** (pesticide wash and absence of synthetic green dye like Malachite Green). "
                    "Unadulterated paneer is rich in milk protein and calcium, while synthetic counterfeit paneer poses severe gastrointestinal and kidney risks."
                ),
                "consumer_checklist": (
                    "1. **Home Iodine Test for Paneer Starch:** Boil a small piece of paneer in water, cool it, and add 2-3 drops of Iodine solution. If it turns blue/purple, starch or potato flour has been added to artificially inflate weight.\n"
                    "2. **Pesticide Wash for Spinach (Palak):** Soak fresh spinach in a 2% saltwater or 1% baking soda solution for 15 minutes, then rinse twice under running water to eliminate pesticide residues.\n"
                    "3. **Malachite Green Dye Check:** Rub wet spinach leaves with a damp white cotton swab or paper napkin. If bright green dye rubs off, the spinach was chemically colored with toxic Malachite Green.\n"
                    "4. **Reheating Caution:** Eat palak paneer fresh while hot (>65 °C). Never consume spinach curry left at room temperature for over 2 hours, as bacterial action converts naturally occurring nitrates into harmful nitrites."
                ),
                "consumer_red_flags": (
                    "- Paneer that feels unnaturally rubbery, chewy, smells sour, or leaves an oily chemical film in the mouth.\n"
                    "- Roadside paneer sold without refrigeration or submerged in murky water.\n"
                    "- Unnaturally glowing green spinach leaves that stain fingers or packaging.\n"
                    "- Stale leftover spinach dishes stored at warm ambient room temperatures."
                ),
                "bis_care_guide": (
                    "1. For packaged dairy products, check the 14-digit FSSAI license number and 'Use-By' date on the pack.\n"
                    "2. If dining at a restaurant or ordering online, verify their **FSSAI Food Hygiene Rating (1 to 5 Stars)**.\n"
                    "3. Report adulterated dairy, fake paneer, or contaminated food on the **FSSAI Food Safety Connect App** or call the **National Consumer Helpline (NCH)** at **1915**."
                )
            }

        # 00b. Milk Shop, Dairy Booth & Milk Products (FSSAI FoSCoS & IS 1224)
        if any(k in q for k in ["paala", "pala", "paalu", "doodh", "milk shop", "dairy booth", "milk booth", "paal kadai", "haalu angadi", "doodh dairy", "dairy parlour"]) or (any(k in q for k in ["milk", "dairy"]) and any(w in q for w in ["shop", "booth", "store", "dukan", "kadai", "angadi", "vyaparam", "parlour", "centre", "center"])):
            return {
                "domain": "Milk Shop, Dairy Booth & Fresh Milk Distribution",
                "standards": [
                    {"code": "FSSAI FoSCoS Reg.", "title": "FSSAI Dairy Products & Milk Safety Regulations", "clause": "Clause 2.1 Standard for Milk & Chilling"},
                    {"code": "IS 1224 (Part 1):1977", "title": "Determination of Fat in Whole Milk (Gerber Method)", "clause": "Clause 5.0 Gerber Fat Estimation"},
                    {"code": "IS 10500:2012", "title": "Drinking Water Specification (For Processing & Equipment Sanitation)", "clause": "Clause 4.0 Potable Quality"},
                    {"code": "IS 2491:2013", "title": "Food Hygiene - General Principles - Code of Practice", "clause": "Clause 6.0 Cold Chain & Sanitation"},
                    {"code": "FSSAI DART Manual", "title": "Rapid Testing for Milk Adulterants (Water, Detergent, Starch, Urea)", "clause": "DART Dairy Testing Protocol"}
                ],
                "scheme": "FSSAI FoSCoS Statutory Registration / State License & Cold Chain Safety",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI), Department of Animal Husbandry & Dairying",
                "table_markdown": (
                    "| Milk Variety / Category | Min Milk Fat (% by mass) | Min Solids-Not-Fat (% SNF) | Primary Quality Test (Method) |\n"
                    "| :--- | :--- | :--- | :--- |\n"
                    "| Cow Milk (Standardized) | Minimum 3.2% | Minimum 8.3% | IS 1224 Gerber Fat / Lactometer SNF |\n"
                    "| Buffalo Milk | Minimum 6.0% | Minimum 9.0% | IS 1224 Gerber Fat / Lactometer SNF |\n"
                    "| Toned Milk | Minimum 3.0% | Minimum 8.5% | Gerber Centrifugation Test |\n"
                    "| Double Toned Milk | Minimum 1.5% | Minimum 9.0% | Gerber Centrifugation Test |\n"
                    "| Full Cream Milk | Minimum 6.0% | Minimum 9.0% | IS 1224 (Part 1) Gerber Method |\n"
                    "| Milk Storage Temperature | Strictly <= 4.0 °C | Continuous Cold Chain | Calibrated Digital Thermometer |\n"
                    "| Adulterants (Urea/Detergent/Starch) | Completely Absent (0%) | Zero Tolerance | FSSAI DART Rapid Chemical Strips |"
                ),
                "qc_requirements": (
                    "- **Lactometer SNF Testing:** Quevenne or Zeal lactometer calibrated at 20°C to instantly check milk density and detect water dilution.\n"
                    "- **Gerber Fat Test Apparatus:** Centrifuge, butyrometers, calibrated pipettes, and analytical-grade sulfuric acid & isoamyl alcohol.\n"
                    "- **Digital Cold Chain Monitoring:** Refrigerator and insulated chill vats maintaining temperatures strictly at or below 4°C with digital temperature logs."
                ),
                "licensing_steps": [
                    "Determine capacity: Apply for FSSAI Basic Registration (< 500 liters/day or turnover < ₹12 Lakhs; ₹100/year fee) or State License (> 500 liters/day; ₹2,000–₹5,000/year fee) on [FoSCoS](https://foscos.fssai.gov.in).",
                    "Equip milk shop with food-grade SS 304 dispensing tanks, lactometer, Gerber testing kit, and 0–4°C chiller.",
                    "Obtain medical fitness certificates for all milk handlers and display the 14-digit FSSAI certificate on the storefront.",
                    "Ensure daily milk test logs for Fat%, SNF, and temperature are maintained for statutory food safety audits."
                ],
                "consumer_summary": (
                    "Milk is a daily dietary staple particularly for children and the elderly. Adulteration with water, detergent, urea, or starch, "
                    "or improper storage above 5°C leads to rapid bacterial multiplication causing acute food poisoning and gastric disorders. "
                    "FSSAI regulations mandate strict hygiene, minimum fat/SNF standards, and prominent 14-digit license displays."
                ),
                "consumer_checklist": (
                    "1. **Check 14-Digit FSSAI License:** Look for the mandatory FSSAI registration certificate displayed prominently at the dairy counter.\n"
                    "2. **Continuous Cold Storage (< 4°C):** Ensure milk packets and loose milk containers are kept chilled in working deep freezers or chillers.\n"
                    "3. **Check Lactometer Reading:** Pure cow/buffalo milk should show a lactometer reading of 28 to 32 at 20°C. Readings below 26 indicate water dilution.\n"
                    "4. **No Chemical Odor or Foam:** Shake milk with water in a bottle; persistent thick foam indicates harmful synthetic detergent adulteration."
                ),
                "consumer_red_flags": (
                    "- Warm or room-temperature milk pouches sweating in non-refrigerated crates.\n"
                    "- Milk that leaves a yellowish residue on heating or tastes bitter/soapy (synthetic milk).\n"
                    "- Dairy vendors refusing to show an active FSSAI registration number or testing records."
                ),
                "bis_care_guide": (
                    "1. Report adulterated or unhygienic milk shops on the FSSAI **Food Safety Connect** portal or app.\n"
                    "2. Dial the **National Consumer Helpline (1915)** for prompt municipal health enforcement.\n"
                    "3. For packaged dairy products carrying BIS ISI marks, verify license numbers via the **BIS Care App**."
                )
            }

        # 0. Soya Sauce, Soybean Condiments & Fermented Culinary Sauces
        if any(k in q for k in ["soya sauce", "soy sauce", "soya sos", "soy sos", "soya paste", "soybean sauce", "soya condiment", "soya"]):
            return {
                "domain": "Soya Sauce (Soy Sauce) & Soybean Culinary Products",
                "standards": [
                    {"code": "FSSAI Reg. 2.3.56", "title": "Soybean Sauce - Food Safety and Standards (Food Products Standards and Food Additives) Regulations", "clause": "Clause 2.3.56 Fermented Soybean Sauce"},
                    {"code": "IS 7837:2018", "title": "Edible Full-Fat Soya Flour - Specification", "clause": "Clause 4.0 Raw Material Purity & Trypsin Inactivation"},
                    {"code": "IS 3882:2020", "title": "Tomato Ketchup and Tomato Sauce - Specification", "clause": "Clause 4.0 Acidity, TSS & Microbiological Limits"},
                    {"code": "IS 15000:2013", "title": "Food Safety Management Systems (HACCP) - Requirements", "clause": "Clause 7.0 Hazard Analysis for Fermentation"},
                    {"code": "Codex CXS 301R-2011", "title": "Regional Standard for Fermented Soybean Sauce (Asian Region)", "clause": "Section 3.0 Composition & 3-MCPD Control"}
                ],
                "scheme": "FSSAI Statutory Food Safety Framework & Category 12.2.2 (Sauces & Condiments)",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (BIS FAD 16)",
                "table_markdown": (
                    "| Parameter / Characteristic | Statutory Requirement (FSSAI / Codex) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Total Nitrogen (Salt-Free Basis) | Not less than 1.0% by mass | AOAC 984.13 / IS 7837 |\n"
                    "| Total Soluble Solids (Salt-Free Basis) | Not less than 15.0% by mass | IS 3882 / Refractometric Brix |\n"
                    "| Acidity (Calculated as Acetic Acid) | Not less than 0.6% by mass | FSSAI Lab Manual / Titration |\n"
                    "| Trypsin Inhibitor Activity | Completely Inactivated / Absent | Thermal Challenge Test |\n"
                    "| 3-MCPD (Process Contaminant) | Maximum 0.02 mg/kg to 0.4 mg/kg | GC-MS/MS (Contaminants Regs) |\n"
                    "| Lead (as Pb) | Maximum 2.5 mg/kg | FSSAI Metal Contaminants |\n"
                    "| Arsenic (as As) | Maximum 1.1 mg/kg | FSSAI Metal Contaminants |\n"
                    "| Class II Preservatives (Benzoic/Sorbic) | Maximum 750 mg/kg | FSSAI Additives Appendix A |\n"
                    "| Synthetic Food Colors (Coal-Tar) | Completely Prohibited (Must be natural fermentation) | FSSAI Reg 2.1.2 |\n"
                    "| Total Plate Count | Max 10,000 CFU/g | IS 5402 |\n"
                    "| Yeast and Mould Count | Max 100 CFU/g | IS 5403 |\n"
                    "| Coliform Bacteria & E. coli | Absent in 1g / 25g | IS 5401 / IS 15185 |"
                ),
                "qc_requirements": (
                    "- **Trypsin Inhibitor Thermal Inactivation:** Raw soybeans must undergo validated thermal treatment to completely denature anti-nutritional trypsin inhibitors before fermentation.\n"
                    "- **Fermentation Monitoring:** Pure culture fermentation (Aspergillus oryzae / Aspergillus sojae) with tight control of temperature, salinity (14–18% NaCl), and aging.\n"
                    "- **3-MCPD Monitoring:** Regular GC-MS testing to confirm absence of carcinogenic 3-MCPD (common in cheap acid-hydrolyzed vegetable protein / HVP sauces).\n"
                    "- **In-House Testing Equipment:** Refractometer (0–50 °Brix), Kjeldahl nitrogen digestion assembly, pH meter, and microbiological incubation facilities."
                ),
                "licensing_steps": [
                    "Obtain FSSAI Manufacturing License (State or Central based on production capacity) under Category 12.2.2 via the [FoSCoS Portal](https://foscos.fssai.gov.in).",
                    "Establish sanitary food processing premises complying with FSSAI Schedule 4 hygiene standards and IS 2491 (Food Hygiene).",
                    "Submit baseline batch test reports from an FSSAI-notified NABL accredited laboratory verifying Nitrogen, TSS, 3-MCPD, and heavy metals.",
                    "Ensure compliant packaging labels with 14-digit FSSAI license number, mandatory allergen warnings ('Contains Soy / Wheat'), and net volume fill > 90%."
                ],
                "consumer_summary": (
                    "In India, Soya Sauce is regulated by the Food Safety and Standards Authority of India (FSSAI) under Regulation 2.3.56. "
                    "While there is no independent BIS ISI mark for soy sauce itself, allied soy ingredients must comply with BIS standards (IS 7837). "
                    "Consumers must distinguish between healthy, authentic naturally brewed soy sauce and cheap chemically hydrolyzed sauces containing carcinogenic 3-MCPD."
                ),
                "consumer_checklist": (
                    "1. **Check 14-Digit FSSAI License:** Ensure the 14-digit FSSAI license number (`100XXXXXXXXXXX`) is clearly printed on the label alongside the green vegetarian dot logo.\n"
                    "2. **Naturally Brewed vs Chemical Hydrolysis:** Always check the ingredient list. Prefer bottles labeled 'Naturally Brewed' or 'Fermented'. Beware of cheap chemical imitations labeled 'Acid-HVP' or 'Hydrolyzed Soy Protein'.\n"
                    "3. **Mandatory Allergen Warning:** By law, the label must display: **'Contains Soya'** (and 'Contains Wheat/Gluten' if fermented with wheat).\n"
                    "4. **No Bulging Caps or Foul Odor:** The bottle must be vacuum-sealed or tamper-evident. Never consume soy sauce from bulging bottles or bottles with cloudy surface mould."
                ),
                "consumer_red_flags": (
                    "- Cheap roadside bottles with faint xeroxed labels and no 14-digit FSSAI license number.\n"
                    "- Chemical soy sauces high in 3-MCPD process contaminants that pose carcinogenic and kidney toxicity risks.\n"
                    "- Bottles with sediment lumps, white surface mould scum, or alcoholic off-odors indicating contamination.\n"
                    "- Unlabelled artificial dark chemical coal-tar dyes (prohibited in authentic soy sauce)."
                ),
                "bis_care_guide": (
                    "1. Verify manufacturer credentials and license status on the **FSSAI Food Safety Connect App** or [FoSCoS Portal](https://foscos.fssai.gov.in).\n"
                    "2. For general food packaging, weights, or standards violations, verify through the **BIS Care App**.\n"
                    "3. If you find adulterated or fake soy sauce with hazardous chemicals, report it directly via **National Consumer Helpline (NCH)** at **1915** or file a complaint on the FSSAI grievance portal."
                )
            }

        # 0c. Frost-Free Refrigerators & Commercial Refrigerating Appliances (IS 17550)
        if any(k in q for k in ["refrigerator", "fridge", "frost free", "frost-free", "is 17550", "is17550"]):
            return {
                "domain": "Frost-Free Refrigerators & Household Refrigerating Appliances",
                "standards": [
                    {"code": "IS 17550 (Part 1 & 2):2021", "title": "Household Refrigerating Appliances - Characteristics and Test Methods", "clause": "Clause 5.0 Energy Consumption & Freezing Capacity"},
                    {"code": "IS 302 (Part 1):2008", "title": "Safety of Household and Similar Electrical Appliances - General Requirements", "clause": "Clause 8.0 Protection Against Electric Shock"},
                    {"code": "BEE Star Labeling Regs", "title": "Bureau of Energy Efficiency Star Rating Schedule for Frost-Free Refrigerators", "clause": "Star Labeling 1 to 5 Stars"}
                ],
                "scheme": "BEE Mandatory Star Labeling & BIS Scheme-I ISI Mark Certification",
                "statutory_bodies": "Bureau of Indian Standards (BIS CED / ETD), Bureau of Energy Efficiency (BEE), Ministry of Power",
                "table_markdown": (
                    "| Performance & Safety Parameter | Statutory Requirement | Test Standard / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Annual Energy Consumption | Must conform to labeled Star Rating (BEE Energy Consumption Table) | IS 17550 (Part 2) Clause 6.2 |\n"
                    "| Fresh Food Storage Temperature | 0 °C to +4 °C under tropical testing climate (+43 °C ambient) | IS 17550 (Part 1) Clause 5.1 |\n"
                    "| Freezer Compartment Temperature | Equal to or colder than -18 °C (Three-Star/Four-Star Freezer) | IS 17550 (Part 1) Clause 5.2 |\n"
                    "| Freezing Capacity Test | Freeze test packages from +25 °C to -18 °C within 24 hours | IS 17550 (Part 2) Clause 7.1 |\n"
                    "| Pull-Down Performance | Reach steady operating temperature from ambient within 4 hours | IS 17550 (Part 2) Clause 7.4 |\n"
                    "| High-Voltage Dielectric Strength | Withstand 1,250V AC for 1 minute without breakdown | IS 302 (Part 1) Clause 13.3 |\n"
                    "| Earth Continuity Resistance | Maximum 0.1 Ohm at 25A test current | IS 302 (Part 1) Clause 27.5 |\n"
                    "| Eco-Friendly Refrigerant Bound | Zero Ozone Depletion Potential (ODP = 0, R600a Isobutane) | Environment Protection Act |"
                ),
                "qc_requirements": (
                    "- **Climate Chamber Testing:** Environmental test room maintained at +16 °C, +32 °C, and +43 °C (Tropical Class T) with continuous temperature logging.\n"
                    "- **Electrical Safety Automated Test Bench:** 100% routine testing for insulation resistance (> 5 MΩ), earth continuity (< 0.1 Ω), and high voltage flash test."
                ),
                "licensing_steps": [
                    "Submit baseline type-test report from an accredited NABL laboratory to the Bureau of Energy Efficiency (BEE) for star label model registration.",
                    "Apply online on the official [BIS Manakonline Portal](https://www.manakonline.in) for Scheme-I ISI Mark under IS 17550.",
                    "Establish routine testing facilities for insulation resistance, earth bonding, and leakage current at the manufacturing line.",
                    "Undergo factory inspection and draw independent witness samples for confirmatory laboratory testing."
                ],
                "consumer_summary": (
                    "Frost-free refrigerators sold in India must display both the authentic BIS Standard Mark and the BEE Star Rating label. "
                    "A higher star rating (e.g. 5 Stars) saves significant electricity over the appliance's lifespan."
                ),
                "consumer_checklist": (
                    "1. **BEE Star Label Authenticity:** Ensure the BEE hologram star label features the correct Star Level, Year of Launch, and annual kWh consumption.\n"
                    "2. **BIS ISI Mark with CM/L Number:** Look for the ISI Mark embossed on the rear electrical rating plate alongside the 7 or 8-digit CM/L license number.\n"
                    "3. **Earthing Safety:** The appliance must be supplied with a factory-molded 3-pin plug (IS 1293) with an intact earth pin."
                ),
                "consumer_red_flags": (
                    "- Unbranded or assembled refrigerators with forged stickers and no CM/L number.\n"
                    "- Appliances missing star rating labels or using flammable uncertified refrigerants without safety markings."
                ),
                "bis_care_guide": "Verify model registration and CM/L license validity on the BIS Care App or via the BEE Star Label Portal."
            }

        # 0d. Electric Ceiling Fans and Regulators (IS 374)
        if any(k in q for k in ["ceiling fan", "electric fan", "is 374", "is374", "fan regulator"]):
            return {
                "domain": "Electric Ceiling Type Fans and Regulators",
                "standards": [
                    {"code": "IS 374:2019", "title": "Electric Ceiling Type Fans and Regulators - Specification", "clause": "Clause 4.0 Air Delivery & Service Value"},
                    {"code": "IS 302 (Part 2/Sec 80)", "title": "Safety of Household Electrical Appliances - Particular Requirements for Fans", "clause": "Clause 8.0 Safety & Electrical Insulation"},
                    {"code": "BEE Star Rating Schedule", "title": "Mandatory BEE Star Rating for Ceiling Fans (BLDC & Induction)", "clause": "Service Value Calculation"}
                ],
                "scheme": "BEE Mandatory Star Rating & BIS Scheme-I Mandatory Quality Control Order (QCO)",
                "statutory_bodies": "Bureau of Indian Standards (BIS ETD 23) & Bureau of Energy Efficiency (BEE)",
                "table_markdown": (
                    "| Technical & Safety Parameter | Statutory Requirement (1200 mm Sweep) | Standard Test Method |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Minimum Air Delivery | Not less than 210 m³/min (at rated voltage 230V) | IS 374 Clause 14.1 (Anemometer Chamber) |\n"
                    "| Minimum Service Value (Air Delivery / Power) | >= 4.0 m³/min/W (for 5-Star BEE) | IS 374 Clause 14.2 |\n"
                    "| Maximum Power Consumption (5-Star BLDC) | Maximum 30W to 35W at full speed | Digital Power Analyzer |\n"
                    "| Temperature Rise of Stator Windings | Maximum 70 °C (Class E) / 80 °C (Class B) | Resistance Method IS 374 |\n"
                    "| Insulation Resistance | Minimum 2.0 Mega-Ohm at 500V DC | Megger Insulation Tester |\n"
                    "| High Voltage Withstand | 1,500V AC applied for 1 minute without puncture | IS 302 (Part 1) |\n"
                    "| Suspension Hook & Downrod Tensile Strength | Withstand 1,000 N (approx 100 kg) tensile test | Mechanical Tensile Challenge |\n"
                    "| Earthing Resistance | Maximum 0.1 Ohm between motor body and earthing terminal | Earth Bond Tester |"
                ),
                "qc_requirements": (
                    "- **Air Delivery Testing Tunnel:** Standardized wind tunnel equipped with rotating vane anemometer calibrated to IS 374 geometry.\n"
                    "- **Dynamic Blade Balancing:** Precision electronic dynamic balancing rig to eliminate wobble and vibration at 350+ RPM.\n"
                    "- **Endurance Run:** 1,000-hour continuous thermal endurance test under elevated voltage."
                ),
                "licensing_steps": [
                    "Fabricate fan prototypes complying with IS 374 and achieve target service value (> 4.0 for BLDC models).",
                    "Conduct type testing in a BIS-recognized NABL testing laboratory.",
                    "Apply on the [BIS Manakonline Portal](https://www.manakonline.in) for Scheme-I ISI Mark under Mandatory Ceiling Fan QCO.",
                    "Register the model with BEE for star rating label clearance before commercial distribution."
                ],
                "consumer_summary": (
                    "Ceiling fans are under a mandatory BIS Quality Control Order (QCO) and BEE Star Rating. "
                    "Consumers should prefer 5-star BLDC fans which consume up to 60% less electricity compared to conventional induction fans."
                ),
                "consumer_checklist": (
                    "1. **Check Authentic ISI Mark:** The motor housing must feature the ISI mark alongside a valid 7 or 8-digit CM/L number.\n"
                    "2. **Check BEE Star Label:** Look for the official BEE star label showing service value and wattage.\n"
                    "3. **Safety Wire & Shackles:** Ensure the fan packaging includes the secondary safety cable to prevent catastrophic drops."
                ),
                "consumer_red_flags": (
                    "- Roadside unbranded ceiling fans without ISI mark or CM/L license number.\n"
                    "- Fans with paper-thin blades that vibrate excessively or run hot within 30 minutes."
                ),
                "bis_care_guide": "Verify CM/L number and manufacturer identity on the BIS Care App before purchase."
            }

        # 0d1. Domestic Electric Irons & Thermostat Safety (IS 366 / IS 302-2-3)
        if any(k in q for k in ["electric iron", "steam iron", "dry iron", "is 366", "is366", "thermostat", "ironing"]):
            return {
                "domain": "Domestic Electric Irons, Steam Irons & Thermostat Safety",
                "standards": [
                    {"code": "IS 366:1991", "title": "Electric Irons - Specification", "clause": "Clause 7.0 Operating Temperature, Thermostat Cut-Off & Safety"},
                    {"code": "IS 302 (Part 2/Sec 3):2007", "title": "Safety of Household and Similar Electrical Appliances - Particular Requirements for Electric Irons", "clause": "Clause 8.0 Electrical Insulation & Thermal Cut-Out"},
                    {"code": "IS 1293:2019", "title": "Plugs and Socket-Outlets of Rated Voltage up to 250V", "clause": "Clause 13.0 Three-Pin Earth Termination"}
                ],
                "scheme": "BIS Scheme-I Mandatory ISI Mark Certification under Electrical Appliances QCO",
                "statutory_bodies": "Bureau of Indian Standards (BIS ETD 32 - Electrical Appliances), DPIIT, Ministry of Consumer Affairs",
                "table_markdown": (
                    "| Parameter / Characteristic | Statutory Requirement (IS 366) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Soleplate Temperature Limits | Max 250 °C (Automatic Thermostat cutoff at dialed fabric setting) | IS 366 Clause 7.2 (Thermocouple) |\n"
                    "| Thermal Cutout / Thermal Fuse | Mandatory secondary non-self-resetting thermal cut-out | IS 302 (Part 2/Sec 3) Clause 19 |\n"
                    "| High Voltage Dielectric Test | Withstand 1,500V AC for 1 minute without insulation puncture | IS 302 (Part 1) Clause 13.3 |\n"
                    "| Earth Continuity Resistance | Maximum 0.1 Ohm at 25A test current | IS 302 (Part 1) Clause 27.5 |\n"
                    "| Leakage Current | Maximum 0.75 mA under full operating temperature | IS 302 (Part 1) Clause 16.2 |\n"
                    "| Drop & Mechanical Impact Test | Drop from 1.0 m height onto hardwood floor without body crack | IS 366 Clause 14.1 |"
                ),
                "qc_requirements": (
                    "- **Thermal Endurance & Thermostat Cycling Bench:** 500-hour automated thermostat endurance rig measuring cycle overshoot and hysteresis.\n"
                    "- **Digital High-Voltage Tester & Earth Bond Meter:** For 100% routine end-of-line electrical safety testing.\n"
                    "- **Soleplate Temperature Profiling:** Calibrated surface thermocouples logging soleplate heat distribution across 5 grid points."
                ),
                "licensing_steps": [
                    "Design electric iron models with dual thermal protection (automatic thermostat + secondary thermal fuse).",
                    "Submit prototype units to a BIS-recognized NABL laboratory for type approval under IS 366.",
                    "Apply for Scheme-I ISI Mark on [BIS Manakonline](https://www.manakonline.in).",
                    "Affix mandatory ISI mark with valid 7-digit CM/L license number on the rating plate."
                ],
                "consumer_summary": (
                    "Electric irons are under a mandatory BIS Quality Control Order (QCO). Uncertified irons lack thermal cutouts, "
                    "causing severe fabric burns, electrical shocks, and household fires."
                ),
                "consumer_checklist": (
                    "1. **Check ISI Mark:** Look for the ISI mark and 7-digit CM/L number on the rating plate under the iron heel.\n"
                    "2. **Check 3-Pin Molded Plug:** The power cord must have a molded 3-pin plug compliant with IS 1293 for protective earthing.\n"
                    "3. **Thermostat Indicator Lamp:** Verify that the thermostat indicator lamp clicks on and off reliably at different fabric settings."
                ),
                "consumer_red_flags": (
                    "- Cheap roadside irons with 2-pin flat plugs lacking earth connection.\n"
                    "- Irons without a thermal cutoff that overheat uncontrollably and scorch clothes."
                ),
                "bis_care_guide": "Verify the CM/L number printed on the electric iron rating plate using the BIS Care App."
            }

        # 0d2. Domestic Pressure Cookers & Safety Relief Valves (IS 2347)
        if any(k in q for k in ["pressure cooker", "cooker", "is 2347", "is2347", "fusible plug", "vent weight"]):
            return {
                "domain": "Domestic Pressure Cookers & Overpressure Safety Devices",
                "standards": [
                    {"code": "IS 2347:2017", "title": "Domestic Pressure Cookers - Specification", "clause": "Clause 5.0 Operating Pressure & Thermal Fusible Safety Plug"},
                    {"code": "IS 7466:1994", "title": "Rubber Gaskets for Domestic Pressure Cookers", "clause": "Clause 4.0 Food Grade Non-Toxic Polymer Compliance"},
                    {"code": "DPIIT Pressure Cookers QCO", "title": "Domestic Pressure Cookers (Quality Control) Order", "clause": "Mandatory Scheme-I ISI Mark"}
                ],
                "scheme": "BIS Scheme-I Mandatory ISI Mark Certification under Domestic Pressure Cookers QCO",
                "statutory_bodies": "Bureau of Indian Standards (BIS MED 33 - Utensils & Kitchen Appliances), DPIIT, CCPA",
                "table_markdown": (
                    "| Safety & Performance Characteristic | Statutory Requirement (IS 2347) | Standard Test Method |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Operating Working Pressure | Nominal 1.0 kgf/cm² (approx 100 kPa / 1 bar) | IS 2347 Clause 7.1 |\n"
                    "| Pressure Regulating Device (Vent Weight) | Operates smoothly to vent excess steam without sticking | IS 2347 Clause 7.2 |\n"
                    "| Safety Relief Device (Fusible Plug) | Operates between 1.3 kgf/cm² to 2.0 kgf/cm² (safety venting) | IS 2347 Clause 7.3 |\n"
                    "| Hydrostatic Proof Pressure Test | Withstand 2.0 times maximum working pressure (min 200 kPa) without rupture | IS 2347 Clause 8.1 |\n"
                    "| Burst Pressure Safety Bound | Not less than 3.0 times operating pressure (min 300 kPa) | Hydrostatic Burst Rig |\n"
                    "| Gasket Material Food Safety | Non-toxic food contact rubber/silicone conforming to IS 7466 | Food Simulant Migration Test |"
                ),
                "qc_requirements": (
                    "- **Hydrostatic Pressure Proof Rig:** Test chamber testing cooker bodies at 2.0x working pressure for 1 minute.\n"
                    "- **Fusible Safety Plug Melting Test:** Thermal oil bath verifying alloy melting temperature and relief venting.\n"
                    "- **Fatigue & Thermal Shock Cycles:** 1,000 cooking cycle simulation testing lid locking mechanism."
                ),
                "licensing_steps": [
                    "Manufacture cooker body and lid from certified food-grade virgin aluminium alloy or stainless steel.",
                    "Equip every lid with dual safety releases: calibrated weight valve + fusible plug.",
                    "Apply for BIS Scheme-I ISI mark on [BIS Manakonline](https://www.manakonline.in).",
                    "Laser-engrave the ISI logo, standard code IS 2347, and 7-digit CM/L license number on the cooker base."
                ],
                "consumer_summary": (
                    "Under the DPIIT Quality Control Order, selling non-ISI pressure cookers in India is illegal and dangerous. "
                    "Defective uncertified pressure cookers can explode under steam pressure, causing fatal injuries."
                ),
                "consumer_checklist": (
                    "1. **Check ISI Mark on Body & Lid:** Both cooker body and lid must bear the authentic ISI mark with a 7-digit CM/L number.\n"
                    "2. **Check Fusible Safety Plug:** Ensure the fusible safety plug under the lid handle is intact with visible silver metallic alloy.\n"
                    "3. **Check Vent Tube:** Ensure steam vent tube is clear and unobstructed before every cooking cycle."
                ),
                "consumer_red_flags": (
                    "- Cheap roadside cookers with lead solder used in place of certified bismuth fusible plugs.\n"
                    "- Cookers with paper stickers or missing CM/L numbers."
                ),
                "bis_care_guide": "Verify the CM/L number on the cooker base via the BIS Care App before purchase."
            }

        # 0e. Aluminium and Aluminium Alloy Foil for Pharmaceutical Packaging (IS 15392)
        if any(k in q for k in ["aluminium foil", "aluminum foil", "is 15392", "is15392", "pharma foil", "blister", "pharmaceutical packaging"]):
            return {
                "domain": "Aluminium and Aluminium Alloy Foil for Pharmaceutical Packaging",
                "standards": [
                    {"code": "IS 15392:2020", "title": "Aluminium and Aluminium Alloy Foil for Pharmaceutical Packaging - Specification", "clause": "Clause 5.0 Mechanical Properties & Pin-Hole Density"},
                    {"code": "IS 504:2018", "title": "Methods of Chemical Analysis of Aluminium and Its Alloys", "clause": "Clause 4.0 Chemical Composition & Purity"},
                    {"code": "DPIIT Aluminium QCO", "title": "Aluminium and Aluminium Alloys Quality Control Order", "clause": "Mandatory ISI Marking for Pharma Foil"}
                ],
                "scheme": "BIS Scheme-I Mandatory Product Certification (ISI Mark) under DPIIT Quality Control Order",
                "statutory_bodies": "Bureau of Indian Standards (BIS MTD 07), Department for Promotion of Industry and Internal Trade (DPIIT), CDSCO",
                "table_markdown": (
                    "| Parameter / Characteristic | Statutory Requirement (Push-Through Blister) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Aluminium Purity | Not less than 99.0% Al (Alloy 1200 / 8011) | IS 504 (Spectrometry / OES) |\n"
                    "| Nominal Thickness | 20 to 25 micron (Tolerance: ± 8%) | Micrometer / IS 15392 Clause 6 |\n"
                    "| Tensile Strength (Hard Temper H18) | Minimum 140 MPa | IS 1608 (Part 1) Tensile Test |\n"
                    "| Elongation at Fracture | Minimum 2.0% (for hard temper) | Tensile Testing Machine |\n"
                    "| Bursting Strength | Minimum 60 kPa | IS 15392 Annex B |\n"
                    "| Pin-Hole Density | ZERO pin-holes greater than 20 micron per m² | Optical Pin-hole Light Box Test |\n"
                    "| Heat-Seal Coating Adhesion to PVC/PVDC | Minimum 7.0 N/15 mm strip | Universal Testing Machine (UTM) |\n"
                    "| Lead (as Pb) Limit | Maximum 10 ppm (0.001%) | ICP-OES / Toxic Metals Bound |\n"
                    "| Arsenic (as As) Limit | Maximum 1 ppm (0.0001%) | Hydride Generation AAS |\n"
                    "| Odour and Taste Transfer | Completely Neutral / Odourless | Sensory Test (Pharma Grade) |"
                ),
                "qc_requirements": (
                    "- **Optical Pin-Hole Inspection Box:** Enclosed light transmission cabinet to inspect foil strip for micro-perforations that would compromise medicine stability.\n"
                    "- **Heat-Sealing Test Rig:** Laboratory heat sealer with digital temperature (160–200 °C), pressure, and dwell time control.\n"
                    "- **Chemical Purity Analysis:** Optical Emission Spectrometer (OES) to verify aluminium alloy composition (Alloy 8011/1200)."
                ),
                "licensing_steps": [
                    "Establish cold-rolling and slitting facility complying with cleanroom standards for pharmaceutical primary packaging.",
                    "Install pin-hole inspection tables, thickness gauges, and heat-seal peel testing instruments.",
                    "Apply online on the [BIS Manakonline Portal](https://www.manakonline.in) for Scheme-I ISI Mark under IS 15392.",
                    "Submit baseline testing reports verifying chemical purity, pin-holes, and microbiological cleanliness from an NABL accredited laboratory."
                ],
                "consumer_summary": (
                    "Aluminium pharmaceutical foil is critical for protecting life-saving medicines from moisture, oxygen, and contamination. "
                    "Under the DPIIT Quality Control Order, all blister and strip foil must carry the mandatory BIS ISI Mark."
                ),
                "consumer_checklist": (
                    "1. **Check Blister Packaging Integrity:** The foil must peel or push cleanly without flaking or tearing into jagged shreds.\n"
                    "2. **Look for Clean Printing:** Medicine strips must feature high-resolution batch, expiry, and manufacturer declarations on the aluminium backing.\n"
                    "3. **No Pin-Holes:** Discard medicine if the foil shows visible punctures, holes, or discoloration."
                ),
                "consumer_red_flags": (
                    "- Porous or brittle aluminium foil that exposes tablets to humidity and chemical degradation.\n"
                    "- Counterfeit medicine packaging using uncertified industrial aluminium foil high in toxic lead."
                ),
                "bis_care_guide": "Report uncertified or substandard pharmaceutical packaging via the BIS Care App or to state drug control authorities."
            }

        # 0b. Fresh Fruit Juices, Sugarcane Juice, Beverages & Shake Stalls
        if concept_key == "juice_beverage" or any(k in tokens for k in ["juice", "juce", "sugarcane", "ganna", "cheruku", "karumbu", "kabbu", "serdi", "aakh", "us", "beverage", "sharbat", "smoothie", "mocktail"]):
            return {
                "domain": "Fresh Fruit Juices, Sugarcane Juice & Beverage Centers",
                "standards": [
                    {"code": "FSSAI Reg. 2.3.6", "title": "Thermally Processed Fruit Juices & Fresh Extracted Beverages", "clause": "Clause 2.3.6 Quality & Contaminant Limits"},
                    {"code": "IS 10500:2012", "title": "Drinking Water Specification (Zero E.coli & Coliform Limits for Ice & Dilution)", "clause": "Clause 4.0 Drinking Water Requirements"},
                    {"code": "IS 2491:2013", "title": "Food Hygiene - General Principles - Code of Practice", "clause": "Clause 5.0 Establishment Design & Equipment"},
                    {"code": "IS 3881:2020", "title": "Tomato Juice & Fruit Beverages - Specification", "clause": "Clause 4.0 Natural Brix & Acidity"},
                    {"code": "FSSAI Schedule 4", "title": "General Hygienic and Sanitary Practices for Food Business Operators", "clause": "Part II Sanitary & Handler Hygiene Requirements"}
                ],
                "scheme": "FSSAI Food Safety Framework (Category 14.1.2 - Fruit Juices) & State Municipal Health Trade Clearance",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI), Ministry of Health & Family Welfare, Local Urban Local Bodies (ULB)",
                "table_markdown": (
                    "| Quality / Safety Parameter | Statutory Requirement | Statutory Standard / Test Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Ice & Preparation Water Potability | Zero E. coli / Coliforms per 250ml; TDS < 500 mg/L | IS 10500 / IS 14543 |\n"
                    "| Extraction Contact Surface | Food-Grade Stainless Steel (SS 304 / SS 316) | IS 2491 Clause 5.3 |\n"
                    "| Lubricant / Machine Oil Contamination | Completely ABSENT (Zero food contact) | FSSAI Schedule 4 Clause 4.2 |\n"
                    "| Artificial Sweeteners (Saccharin, etc.) | STRICTLY PROHIBITED in Fresh Juices | FSSAI Food Additives Reg 3.1 |\n"
                    "| Synthetic Chemical Dyes (Coal-Tar) | STRICTLY PROHIBITED (Zero Tolerance) | FSSAI Reg 2.1.2 |\n"
                    "| Sugarcane Juice Total Soluble Solids (TSS) | Min 16.0 °Brix (Natural cane sugar profile) | Handheld Refractometer / IS 3881 |\n"
                    "| Food Handler Medical Fitness | Mandatory Annual Form VII Health Certificate | FSSAI Schedule 4 Part II |\n"
                    "| Total Bacterial Plate Count | Max 10,000 CFU/ml | IS 5402 |\n"
                    "| Yeast & Mould Count | Max 100 CFU/ml | IS 5403 |"
                ),
                "qc_requirements": (
                    "- **Food-Grade Contact Equipment:** Crushing rollers, blades, and collection vessels must be certified Food-Grade Stainless Steel (SS 304). Roller drive axles must feature sealed food-grade bearings to prevent toxic petroleum grease from leaking into sugarcane stalks.\n"
                    "- **Ice Sourcing & Testing:** Commercial industrial cooling ice blocks (often transported on dirty floorboards and laden with sewage bacteria) are strictly prohibited. Only food-grade ice prepared from IS 10500 compliant potable water is permitted.\n"
                    "- **Fly & Pest Barriers:** Stalls must operate fly-catchers, mesh coverings, and foot-operated covered waste disposal bins.\n"
                    "- **Worker Hygiene:** Daily clean aprons, hairnets, hand sanitization, and clean potable water washing stations."
                ),
                "licensing_steps": [
                    "Register on the official [FSSAI FoSCoS Portal](https://foscos.fssai.gov.in) for Basic Registration (turnover < Rs. 12 Lakhs/year) or State License (turnover > Rs. 12 Lakhs/year) under Category 14.1.2.",
                    "Obtain Municipal Health Trade License / Sanitary Trade Permit from the local Municipal Corporation / Urban Local Body.",
                    "Register establishment under the State Shops & Commercial Establishments Act (Gumasta License) within 30 days of opening.",
                    "Register for free lifetime MSME Udyam Certificate on [udyamregistration.gov.in](https://udyamregistration.gov.in) for subsidized equipment financing.",
                    "Ensure commercial weighing scales and volume dispensing measures are stamped annually by the Legal Metrology Department on e-measure.",
                    "Prominently display the 14-digit FSSAI Registration number and Food Safety Display Board (FSDB) at the service counter."
                ],
                "consumer_summary": (
                    "Fresh sugarcane and fruit juices are refreshing and healthy, but roadside units pose severe health risks when unhygienic practices are followed. "
                    "Contaminated industrial ice, unwashed sugarcane stalks, toxic machine grease leaking from crushing rollers, and prohibited artificial sweeteners (saccharin) "
                    "can cause severe bacterial gastroenteritis, jaundice (Hepatitis A/E), typhoid, and heavy metal exposure."
                ),
                "consumer_checklist": (
                    "1. **Potable Ice Verification:** Check the ice being added. Pure food ice is clear with clean cubes. Beware of large cloudy industrial ice blocks dragged on burlap sacks across pavements — they frequently test positive for sewage coliforms!\n"
                    "2. **Crusher Rollers & Machine Grease:** Inspect the sugarcane crushing machine. Rollers must be clean stainless steel (SS 304). Look closely at the roller sides — there must be NO black machine grease or motor oil dripping onto the cane stalks or into the collection tray.\n"
                    "3. **Peeled & Washed Stalks:** Sugarcane stalks must have their outer muddy skin scraped/washed before crushing. Stalks stored directly on dusty roadsides harbor bird droppings and pesticide residues.\n"
                    "4. **No Artificial Sweeteners or Colors:** Natural sugarcane juice has a mild grassy sweetness. A lingering metallic or intensely sweet aftertaste indicates illegal addition of cheap synthetic Saccharin.\n"
                    "5. **FSSAI Number Displayed:** Look for the 14-digit FSSAI registration certificate and green vegetarian emblem displayed on the cart or shop."
                ),
                "consumer_red_flags": (
                    "- Crushed ice kept in dirty plastic thermocol boxes or placed directly on road dust.\n"
                    "- Black oily grease visible on the crushing gears, dripping into the juice cup.\n"
                    "- Swarms of houseflies settling on cut fruit slices and cane residue.\n"
                    "- Reusing unwashed glasses in a bucket of murky, stagnant standing water instead of fresh running water or disposable paper cups.\n"
                    "- Artificially neon green or yellow juice (unauthorized coal-tar dyes)."
                ),
                "bis_care_guide": (
                    "1. Report unhygienic juice stalls or contaminated beverages to the **FSSAI Food Safety Connect App** or local Municipal Health Officer.\n"
                    "2. Call the **National Consumer Helpline (NCH)** toll-free at **1915**.\n"
                    "3. For packaged bottled fruit juices, verify the manufacturer's license and CM/L details on the **BIS Care App**."
                )
            }

        # 0c. Food Services, Restaurants, Cafes, Catering & FSSAI Standards
        if concept_key == "food_hygiene" or any(k in tokens for k in [
            "restaurant", "restaurnt", "resturant", "restraunt", "restaraunt", "restrant", "restaurent",
            "food", "fud", "foood", "cafe", "dhaba", "canteen", "catering", "mess", "tiffin", "eatery",
            "hotel", "kitchen", "fast food", "street food", "cloud kitchen", "fssai", "foscos"
        ]):
            return {
                "domain": "Commercial Food Services, Restaurants, Cafes & Food Business Operators",
                "standards": [
                    {"code": "FSSAI Schedule 4", "title": "General Hygienic and Sanitary Practices for Food Business Operators under FSS Act 2006", "clause": "Part II Sanitary & Location Requirements"},
                    {"code": "IS 2491:2013", "title": "Food Hygiene - General Principles - Code of Practice", "clause": "Clause 5.0 Establishment Design & Equipment"},
                    {"code": "IS 10500:2012", "title": "Drinking & Cooking Water Potability (Strict Zero E.coli & Coliform Limits)", "clause": "Clause 4.0 Drinking Water Requirements"},
                    {"code": "IS/ISO 22000:2018", "title": "Food Safety Management Systems (HACCP) - Requirements for Food Chain", "clause": "Clause 7.0 Hazard Analysis & Critical Control Points"},
                    {"code": "FSSAI RUCO Regulations", "title": "Repurpose Used Cooking Oil Regulations (Total Polar Compounds - TPC Limit)", "clause": "Regulation 2.1.2 Cooking Oil Quality"}
                ],
                "scheme": "FSSAI Statutory Food Business Licensing (Basic, State, or Central License under FSS Act 2006)",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI), Ministry of Health & Family Welfare, State Food Safety Commissioners, Urban Local Bodies",
                "table_markdown": (
                    "| Quality / Safety Parameter | Statutory Requirement | Statutory Standard / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Cooking & Drinking Water Potability | Zero E. coli & Coliforms per 250ml; TDS < 500 mg/L | IS 10500 / IS 14543 |\n"
                    "| Used Cooking Oil Total Polar Compounds (TPC) | Maximum 25.0% (Repeated reheating strictly banned) | FSSAI RUCO / IS 542 |\n"
                    "| Food Preparation Contact Surfaces | Food-Grade Stainless Steel (SS 304 / SS 316) | IS 2491 Clause 5.3 |\n"
                    "| Hot Food Holding Temperature | Maintained at or above 65.0°C continuously | FSSAI Schedule 4 Clause 6.1 |\n"
                    "| Cold Food Holding & Salad Temperature | Maintained at or below 5.0°C continuously | FSSAI Schedule 4 Clause 6.1 |\n"
                    "| Frozen Meat / Seafood Storage | Maintained at or below -18.0°C continuously | IS 7049 Clause 5.0 |\n"
                    "| Monosodium Glutamate (MSG / Ajinomoto) | Permitted under GMP; strictly prohibited for infants | FSSAI Food Additives Reg 3.1 |\n"
                    "| Synthetic Food Colors (Coal-Tar) | Zero unpermitted dyes (Rhodamine B / Metanil Yellow strictly banned) | FSSAI Reg 2.1.2 |\n"
                    "| Food Handler Medical Fitness | Mandatory Annual Form VII Health Certification | FSSAI Schedule 4 Part II |\n"
                    "| Kitchen Chimney & Grease Traps | Mandatory Oil/Grease Separator & high exhaust stack | State SPCB CTE/CTO Rules |"
                ),
                "qc_requirements": (
                    "- **Food Safety Display Board (FSDB):** Color-coded green FSSAI Food Safety Display Board with the 14-digit FSSAI license/registration number must be displayed prominently at the entrance.\n"
                    "- **Cooking Oil Quality Monitoring:** Digital handheld oil tester (TPC meter) must be used to ensure frying oil does not cross 25% Total Polar Compounds. Blackened discarded oil must be surrendered to authorized RUCO aggregators for biodiesel conversion.\n"
                    "- **Water Testing:** Municipal/borewell water tested quarterly against IS 10500 potable limits by an FSSAI-notified NABL laboratory.\n"
                    "- **Staff Hygiene SOPs:** Daily clean uniforms, aprons, hairnets, disposable gloves, clean nail inspection, and exclusion of ill food handlers."
                ),
                "licensing_steps": [
                    "Apply for FSSAI License on the [FoSCoS Portal](https://foscos.fssai.gov.in) (Basic Registration for turnover < ₹12 Lakhs; State License for ₹12 Lakhs–₹20 Crores; Central License for > ₹20 Crores).",
                    "Obtain Municipal Health Trade License / Sanitary Permit from the local Municipal Corporation / Urban Local Body.",
                    "Obtain Eating House License from the State Police Licensing Department (for dine-in seating).",
                    "Secure Fire Safety NOC from the State Fire Services (mandatory for establishments with > 50 seats or high-rise premises).",
                    "Secure Consent to Establish (CTE) & Consent to Operate (CTO) from the State Pollution Control Board for kitchen exhaust stack and grease trap.",
                    "Register establishment under the State Shops and Commercial Establishments Act (Gumasta License) within 30 days.",
                    "Register for GSTIN (5% restaurant tax slab) on [gst.gov.in](https://www.gst.gov.in) and free MSME Udyam certificate on [udyamregistration.gov.in](https://udyamregistration.gov.in)."
                ],
                "consumer_summary": (
                    "Every restaurant, cafe, cloud kitchen, food truck, and eatery in India is mandated under Section 31 of the Food Safety and Standards Act 2006 "
                    "to operate exclusively with an active FSSAI License or Registration. Unhygienic commercial kitchens, rancid reused cooking oils (high in carcinogenic free radicals), "
                    "and contaminated water carry severe risks of bacterial gastroenteritis, salmonella, typhoid, and chemical food poisoning."
                ),
                "consumer_checklist": (
                    "1. **FSSAI Food Safety Display Board (FSDB):** Look for the green FSSAI board hung near the billing counter displaying the 14-digit license number (`100...` or `200...`).\n"
                    "2. **Potable Water Guarantee:** Restaurants must serve pure, safe drinking water conforming to IS 10500 free of charge to all patrons upon request.\n"
                    "3. **Fresh Non-Reheated Cooking Oil:** Food must not smell rancid or acrid. FSSAI strictly prohibits reusing frying oil after Total Polar Compounds reach 25%.\n"
                    "4. **Kitchen Hygiene & Clean Uniforms:** Food handlers and cooks must wear clean hairnets, aprons, and use clean tongs/gloves for ready-to-eat salads and bread.\n"
                    "5. **Itemized GST Bill:** Always demand an official printed bill with GSTIN and FSSAI number for consumer protection."
                ),
                "consumer_red_flags": (
                    "- Absence of the mandatory 14-digit FSSAI license number on bills, menu cards, or storefront.\n"
                    "- Food served lukewarm from open, fly-infested buffet chafers rather than maintained piping hot (> 65°C).\n"
                    "- Black, foaming, smoking oil used in deep fryers.\n"
                    "- Roadside grease overflowing from kitchen drains or foul kitchen sewage odor in dining areas.\n"
                    "- Handlers touching raw meats and then ready-to-eat salads without handwashing."
                ),
                "bis_care_guide": (
                    "1. Verify restaurant license authenticity on the official **FSSAI Food Safety Connect App** or [FoSCoS Portal](https://foscos.fssai.gov.in).\n"
                    "2. Lodge food poisoning complaints, adulteration reports, or unhygienic restaurant evidence directly on the FSSAI Food Safety Connect App.\n"
                    "3. For billing, tax, or consumer rights grievances, call the **National Consumer Helpline (NCH)** toll-free at **1915**."
                )
            }

        # 1. Packaged Drinking Water, Natural Mineral Water & Potable Water
        if (concept_key == "water" or "14543" in q or any(k in tokens for k in ["water", "bottle", "packaged water", "mineral water", "paani", "drinking water", "தண்ணீர்", "பாட்டில்", "నీరు"])) and not any(k in tokens for k in ["pipe", "pipes", "hdpe", "pvc", "cpvc", "plumbing", "solar", "heater", "heaters", "kusum", "pump", "pumps", "chekka", "chekkapani", "wood", "woodwork", "carpentry", "timber", "plywood", "badhai", "lakdi", "rangu", "rangupani", "paint", "paints", "enamel", "varnish", "distemper", "putty"]):
            return {
                "domain": "Packaged Drinking Water & Natural Mineral Water Industry",
                "standards": [
                    {"code": "IS 14543:2018", "title": "Packaged Drinking Water (Other than Natural Mineral Water) - Specification", "clause": "Clause 5.0 Physical, Chemical & Microbiological"},
                    {"code": "IS 13428:2005", "title": "Packaged Natural Mineral Water - Specification", "clause": "Clause 4.0 Source Water & Mineral Limits"},
                    {"code": "IS 10500:2012", "title": "Drinking Water (Potable Domestic Water Supply) - Specification", "clause": "Clause 4.0 Potable Parameters"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark Product Certification Scheme)",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (BIS)",
                "table_markdown": (
                    "| Parameter / Characteristic | Permissible Limit (IS 14543:2018 Table 2) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Total Dissolved Solids (TDS) | Max 500 mg/L | IS 3025 (Part 16) |\n"
                    "| pH Value | 6.5 to 8.5 | IS 3025 (Part 11) |\n"
                    "| Turbidity | Max 2 NTU | IS 3025 (Part 10) |\n"
                    "| Total Hardness (as CaCO3) | Max 200 mg/L | IS 3025 (Part 21) |\n"
                    "| Total Arsenic (as As) | Max 0.01 mg/L | IS 3025 (Part 37) |\n"
                    "| Lead (as Pb) | Max 0.01 mg/L (Table 2) | IS 3025 (Part 47) |\n"
                    "| Cadmium (as Cd) | Max 0.003 mg/L | IS 3025 (Part 41) |\n"
                    "| Mercury (as Hg) | Max 0.001 mg/L | IS 3025 (Part 48) |\n"
                    "| Chromium (as Cr) | Max 0.05 mg/L | IS 3025 (Part 52) |\n"
                    "| Copper (as Cu) | Max 0.05 mg/L | IS 3025 (Part 42) |\n"
                    "| Escherichia coli (E. coli) | Absent in 250 ml | IS 15185 |\n"
                    "| Coliform bacteria | Absent in 250 ml | IS 5401 (Part 1) |\n"
                    "| Yeast and Mould | Absent in 250 ml | IS 5403 |\n"
                    "| Faecal Streptococci | Absent in 250 ml | IS 15186 |"
                ),
                "qc_requirements": (
                    "- **In-House Testing Facility:** Must maintain a fully functional microbiology and chemical testing laboratory.\n"
                    "- **Key Lab Equipment:** Autoclave, laminar airflow cabinet, bacteriological incubator (37°C & 44°C), digital pH meter, TDS meter, turbidity meter, and analytical balance.\n"
                    "- **Approved Personnel:** Daily batch quality analysis must be supervised by a BIS-approved Chemist and Microbiologist.\n"
                    "- **Surveillance Records:** Daily production testing registers, ozonation levels (0.2–0.4 mg/L at bottling), and 7-day retention samples must be maintained for BIS factory surveillance."
                ),
                "licensing_steps": [
                    "Secure statutory borewell clearance from the Central Ground Water Authority (CGWA) and Consent to Operate (CTO) from the State Pollution Control Board.",
                    "Install complete water treatment plant (RO membranes, micron filters, UV sterilizer, ozonator) and set up the in-house testing lab.",
                    "Submit Scheme-I ISI Mark application on the official [BIS Manakonline Portal](https://www.manakonline.in) with factory layout and chemist/microbiologist credentials.",
                    "Undergo BIS factory audit, in-house testing verification, and sample draw for independent testing at a BIS-recognized NABL laboratory to receive CM/L license."
                ],
                "consumer_summary": (
                    "Packaged drinking water is governed under Section 16 of the Food Safety & Standards Act and the BIS Act 2016. "
                    "Because contaminated water carries severe health risks, NO manufacturer or seller is legally permitted to produce or sell bottled water "
                    "without an active BIS ISI mark and verified CM/L license number."
                ),
                "consumer_checklist": (
                    "1. **The Authentic ISI Mark:** Look for the official rectangular BIS ISI mark printed prominently on the bottle label or embossed on the 20-litre bubble top jar cap.\n"
                    "2. **The 7 or 8-Digit CM/L License Number:** Below or above the ISI logo, check for the license number formatted as `CM/L-XXXXXXXX` (e.g. `CM/L-8412345`). **Crucial Rule:** An ISI mark without a CM/L number is **100% fake and illegal**!\n"
                    "3. **Standard Code:** Confirm that **`IS 14543`** is printed alongside the ISI mark.\n"
                    "4. **Cap & Seal Integrity:** Ensure the tamper-evident heat-shrink neck sleeve seal is completely unbroken. Check the 14-digit FSSAI license number, batch code, date of manufacture, and Best Before date."
                ),
                "consumer_red_flags": (
                    "- **Refilled 20-Litre Bubble Tops:** Jars with broken seals, scratched caps, or lacking a printed CM/L number (common source of E. coli bacterial contamination).\n"
                    "- **Vague Marketing Claims:** Labels claiming 'Pure RO Water', 'Ozonated Alkaline Water', or 'Mineralized Water' WITHOUT an authentic ISI mark and CM/L number.\n"
                    "- **Health Hazards:** Substandard water can harbor heavy metals (Lead, Arsenic causing chronic toxicity) and pathogenic bacteria causing typhoid, cholera, and severe diarrhea."
                ),
                "bis_care_guide": (
                    "1. Download the free official **BIS Care Mobile App** from Google Play Store or Apple App Store.\n"
                    "2. Open the app and tap **'Verify License Details' (Verify CM/L)**.\n"
                    "3. Enter the 7 or 8-digit CM/L number from the bottle label.\n"
                    "4. The app instantly verifies manufacturer name, registered brand, factory address, and license validity.\n"
                    "5. **Lodge Complaint:** If the bottle is fake or details don't match, tap 'Lodge Complaint' directly in the app or call the **National Consumer Helpline (NCH)** at **1915**."
                )
            }

        # 1b. Dairy Products: Milk, Paneer, Ghee, Butter & Adulteration Testing
        if concept_key == "dairy" or any(k in tokens for k in ["milk", "dairy", "doodh", "dudh", "paneer", "panir", "ghee", "butter", "makhan", "curd", "dahi", "khoya", "mawa", "lactometer"]):
            return {
                "domain": "Dairy Industry, Milk Quality, Paneer & Ghee Adulteration Control",
                "standards": [
                    {"code": "FSSAI Reg. 2.1", "title": "Dairy Products and Analogues - FSSAI Food Products Standards", "clause": "Clause 2.1.1 Milk & Paneer Quality"},
                    {"code": "IS 1479 (Part 1 & 2)", "title": "Methods of Test for Dairy Industry (Chemical & Microbiological)", "clause": "Part 1 Chemical & Part 2 Micro"},
                    {"code": "IS 1224 (Part 1)", "title": "Determination of Milk Fat by Gerber Method", "clause": "Clause 4.0 Fat Determination"},
                    {"code": "IS 10484:2018", "title": "Paneer - Specification", "clause": "Clause 5.0 Moisture & Milk Fat Content"},
                    {"code": "IS 3520:2018", "title": "Ghee (Butter Oil) - Specification", "clause": "Clause 4.0 RM Value & Baudouin Test"}
                ],
                "scheme": "FSSAI Statutory Food Safety Framework & Category 01 (Dairy Products)",
                "statutory_bodies": "Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (FAD 19)",
                "table_markdown": (
                    "| Product / Parameter | Statutory Permissible Requirement | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Cow Milk Fat | Minimum 3.2% to 4.0% (State-specific) | IS 1224 (Gerber Method) |\n"
                    "| Cow Milk Solids-Not-Fat (SNF) | Minimum 8.3% to 8.5% | Lactometer Reading / IS 1479 |\n"
                    "| Buffalo Milk Fat | Minimum 5.0% to 6.0% | IS 1224 (Gerber Method) |\n"
                    "| Buffalo Milk SNF | Minimum 9.0% | IS 1479 (Part 1) |\n"
                    "| Ghee Reichert-Meissl (RM) Value | Minimum 26.0 to 28.0 (Proof of pure milk fat) | IS 3520 Clause 4.2 |\n"
                    "| Ghee Baudouin Test (Vanaspati) | Completely NEGATIVE (Absence of adulterant oil) | IS 3520 Clause 4.5 |\n"
                    "| Paneer Moisture (Max) | Maximum 70.0% by mass | IS 10484 Clause 5.1 |\n"
                    "| Paneer Milk Fat (Dry Basis) | Minimum 50.0% by mass | IS 10484 Clause 5.2 |\n"
                    "| Synthetic Adulterants (Urea, Detergent, Starch, Neutralizers) | COMPLETELY ABSENT (Zero Tolerance) | FSSAI Rapid Chemical Kits |\n"
                    "| Methylene Blue Reduction (MBRT) | > 4 hours (Good quality raw milk) | IS 1479 (Part 2) |\n"
                    "| Total Aflatoxin M1 | Maximum 0.5 mcg/kg | FSSAI Contaminants Regs |"
                ),
                "qc_requirements": (
                    "- **Adulteration Challenge Lab:** Rapid test strips and reagents to test every batch for urea, starch, detergent, ammonium sulphate, and neutralizers.\n"
                    "- **Key Lab Equipment:** Calibrated Gerber butyrometer with centrifuge, digital lactometer (density 1.028–1.032 at 20°C), Reichert-Meissl distillation assembly, and autoclave.\n"
                    "- **Cold Chain Monitoring:** Instant chilling to < 4°C within 3 hours of milking; continuous data logging in insulated milk tankers."
                ),
                "licensing_steps": [
                    "Register or apply for State/Central FSSAI License via the [FoSCoS Portal](https://foscos.fssai.gov.in) under Dairy Processing Category 01.",
                    "Implement mandatory FSSAI Schedule 4 sanitary hygiene facilities and milk reception dock (MRD) testing protocols.",
                    "Equip laboratory with calibrated Gerber fat testing centrifuges and rapid adulteration detection kits.",
                    "Mandatory packaging labeling: Fat %, SNF %, pasteurization type, 14-digit FSSAI number, and storage temp (< 4°C)."
                ],
                "consumer_summary": (
                    "Milk and ghee are essential household staples in India. Substandard or synthetic milk prepared with detergents, starch, and urea causes severe renal and gastrointestinal toxicity. "
                    "FSSAI and BIS standards mandate strict minimum fat, SNF, and RM values with zero tolerance for adulterants."
                ),
                "consumer_checklist": (
                    "1. **Check 14-Digit FSSAI License & Class:** Ensure the packet displays the 14-digit FSSAI number and specific class (Toned, Double Toned, Full Cream Milk).\n"
                    "2. **Simple Iodine Starch Test:** Add 2 drops of tincture iodine to 5 ml of boiled milk or mashed paneer. If it turns blue, starch or potato flour has been added!\n"
                    "3. **Lather & Palm Test (Detergent):** Rub milk vigorously between your palms. Real milk feels slippery; synthetic milk with detergent produces persistent lather and a bitter aftertaste.\n"
                    "4. **Ghee Purity:** Pure ghee melts immediately into brown liquid when dropped on a warm pan. Fake ghee with vanaspati takes longer to melt and stays yellowish."
                ),
                "consumer_red_flags": (
                    "- Milk that does not sour after 24 hours at room temperature (indicates hazardous chemical preservatives/formalin).\n"
                    "- Unusually white, thick paneer that tastes chewy like rubber (analog paneer prepared with palm oil and starch).\n"
                    "- Loose, unbranded ghee sold at abnormally low prices."
                ),
                "bis_care_guide": (
                    "1. Verify dairy plant license status on the **FSSAI Food Safety Connect App** or [FoSCoS Portal](https://foscos.fssai.gov.in).\n"
                    "2. For general food packaging, weights, or AGMARK violations, check via the **BIS Care App**.\n"
                    "3. Report synthetic milk or toxic dairy adulteration immediately to the **National Consumer Helpline (NCH)** at **1915** or call FSSAI toll-free **1800112100**."
                )
            }

        # 1c. Edible Vegetable Oils, Mustard, Groundnut & Blended Oils
        if concept_key == "edible_oil" or any(k in tokens for k in ["mustard oil", "sarson", "groundnut oil", "sunflower oil", "cooking oil", "edible oil", "argemone", "vanaspati", "refined oil"]):
            return {
                "domain": "Edible Vegetable Oils & Fats Industry",
                "standards": [
                    {"code": "FSSAI Reg. 2.2", "title": "Fats, Oils and Fat Emulsions - FSSAI Regulations", "clause": "Clause 2.2.1 Vegetable Oils"},
                    {"code": "IS 546:2020", "title": "Mustard Oil - Specification", "clause": "Clause 4.0 Acid Value & Purity"},
                    {"code": "IS 544:2020", "title": "Groundnut Oil - Specification", "clause": "Clause 4.0 Saponification & Iodine Value"},
                    {"code": "IS 542:2020", "title": "Coconut Oil - Specification", "clause": "Clause 4.0 Moisture & Free Fatty Acids"}
                ],
                "scheme": "FSSAI Mandatory Food Safety Framework & AGMARK Grading",
                "statutory_bodies": "FSSAI, Directorate of Marketing & Inspection (DMI - AGMARK), BIS",
                "table_markdown": (
                    "| Parameter / Characteristic | Permissible Limit (Mustard / Cooking Oil) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Acid Value (Virgin / Kachi Ghani) | Maximum 6.0 mg KOH/g | IS 548 (Part 1) |\n"
                    "| Acid Value (Refined Vegetable Oil) | Maximum 0.5 mg KOH/g | IS 548 (Part 1) |\n"
                    "| Peroxide Value | Maximum 10.0 meq oxygen/kg (Prevents rancidity) | IS 548 (Part 1) |\n"
                    "| Test for Argemone Oil | COMPLETELY NEGATIVE (Zero Tolerance) | Nitric Acid Test / TLC |\n"
                    "| Test for Mineral Oil (Holde's Test) | COMPLETELY NEGATIVE (Prohibited industrial oil) | IS 548 (Part 2) |\n"
                    "| Test for Castor Oil | Completely Negative | IS 548 (Part 2) |\n"
                    "| Vitamin A Fortification (+F Logo) | 6.0 to 9.9 mcg RE per gram of oil | FSSAI Fortification Regs |\n"
                    "| Vitamin D Fortification (+F Logo) | 0.11 to 0.165 mcg per gram of oil | FSSAI Fortification Regs |\n"
                    "| Synthetic Food Colors | Completely Prohibited in pure oils | FSSAI Reg 2.1.2 |"
                ),
                "qc_requirements": (
                    "- **Argemone Adulteration Check:** Mandatory nitric acid challenge test on every single raw seed batch before oil extraction to prevent toxic alkaloid contamination.\n"
                    "- **In-House Lab Equipment:** Abbe refractometer, Lovibond tintometer (color measurement), closed-cup flash point apparatus, and peroxide value titration assembly.\n"
                    "- **Ban on Loose Oil:** Sale of loose/unpackaged edible oil is strictly banned across India under the Food Safety and Standards (Prohibition and Restrictions on Sales) Regulations."
                ),
                "licensing_steps": [
                    "Obtain FSSAI Manufacturing License via [FoSCoS](https://foscos.fssai.gov.in) under Category 02 (Fats and Oils).",
                    "Apply for AGMARK Certificate of Authorization (CA) from the Directorate of Marketing and Inspection.",
                    "Submit NABL laboratory test report confirming absence of Argemone, Castor, and Mineral oils.",
                    "Pack in food-grade tin or PET bottles with mandatory +F fortification logo, AGMARK replica, and 14-digit FSSAI number."
                ],
                "consumer_summary": (
                    "Cooking oil is prone to hazardous adulteration with poisonous Argemone oil (which causes fatal epidemic dropsy and cardiac failure) and cheap industrial mineral oil. "
                    "Sale of loose, unsealed cooking oil is illegal in India. Always buy factory-sealed bottles with verified FSSAI and AGMARK marks."
                ),
                "consumer_checklist": (
                    "1. **Never Buy Loose Oil:** Loose edible oil is prohibited by law because it cannot be traced or tested for poisonous adulterants.\n"
                    "2. **Check for AGMARK & FSSAI:** Authentic edible oils display the AGMARK grade replica alongside the 14-digit FSSAI license number.\n"
                    "3. **Check for Fortified (+F) Logo:** Fortified cooking oils display the blue '+F' logo indicating Vitamin A and D enrichment.\n"
                    "4. **Nitric Acid Home Test (Argemone Check):** Add 5 ml of cooking oil to a small glass with 5 ml of concentrated nitric acid. Shake gently. A red or orange-brown ring indicates toxic Argemone oil!"
                ),
                "consumer_red_flags": (
                    "- Roadside unsealed tins or open plastic jars sold without brand labels.\n"
                    "- Bitter, chemical smell or oil that turns dark and smokes excessively at low frying temperatures.\n"
                    "- Missing date of packing, batch code, or manufacturer address."
                ),
                "bis_care_guide": (
                    "1. Verify cooking oil brand registration on the **FSSAI Food Safety Connect App**.\n"
                    "2. Check packaging compliance and net volume on the **BIS Care App**.\n"
                    "3. Report illegal loose oil sales or adulterated oil directly to **National Consumer Helpline (NCH)** at **1915**."
                )
            }

        # 1d. Spices & Condiments: Turmeric, Chilli Powder, Black Pepper
        if concept_key == "spices" or any(k in tokens for k in ["turmeric", "haldi", "chilli", "mirch", "pepper", "coriander", "dhaniya", "masala", "curcumin"]):
            return {
                "domain": "Spices & Condiments Quality & Adulteration Control",
                "standards": [
                    {"code": "FSSAI Reg. 2.9", "title": "Salts, Spices, Condiments and Related Products - FSSAI Regulations", "clause": "Clause 2.9.1 Spices Whole and Ground"},
                    {"code": "IS 3576:2010", "title": "Turmeric, Whole and Ground - Specification", "clause": "Clause 4.0 Curcumin & Lead Chromate Bounds"},
                    {"code": "IS 2445:2017", "title": "Chilli Powder - Specification", "clause": "Clause 4.0 Non-Volatile Ether Extract & Sudan Dye"},
                    {"code": "IS 1798:2018", "title": "Black Pepper, Whole and Ground - Specification", "clause": "Clause 4.0 Piperine & Light Berries"}
                ],
                "scheme": "FSSAI Food Safety Framework & Spices Board AGMARK Certification",
                "statutory_bodies": "FSSAI, Spices Board of India, Bureau of Indian Standards (FAD 25)",
                "table_markdown": (
                    "| Spice / Parameter | Statutory Requirement | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Turmeric Curcumin Content | Not less than 3.0% by mass | IS 3576 Clause 4.3 |\n"
                    "| Lead Chromate in Turmeric | COMPLETELY ABSENT (Zero Tolerance) | Chemical Ash Acid Test |\n"
                    "| Sudan Dyes (Sudan I to IV) in Chilli | COMPLETELY PROHIBITED (Carcinogenic Industrial Dye) | HPLC / LC-MS/MS |\n"
                    "| Non-Volatile Ether Extract (Chilli) | Minimum 12.0% by mass | IS 2445 Clause 4.2 |\n"
                    "| Total Ash (Turmeric & Chilli) | Maximum 8.0% to 9.0% by mass | IS 3576 / IS 2445 |\n"
                    "| Black Pepper Piperine Content | Minimum 4.0% by mass | IS 1798 Clause 4.2 |\n"
                    "| Papaya Seed Adulteration in Pepper | COMPLETELY ABSENT | Water Flotation Test |\n"
                    "| Aflatoxin B1 in Spices | Maximum 15.0 mcg/kg | FSSAI Contaminants Regs |\n"
                    "| Moisture Content | Maximum 10.0% to 12.0% | IS 1797 |"
                ),
                "qc_requirements": (
                    "- **Lead Chromate & Chemical Dye Screening:** Rigorous testing of raw turmeric fingers for toxic yellow chemical polishing before pulverization.\n"
                    "- **In-House Lab Equipment:** Muffle furnace for total ash determination, Soxhlet extraction assembly for ether extract, UV-Vis spectrophotometer for curcumin/piperine, and moisture balance.\n"
                    "- **Aflatoxin Prevention:** Pre-grinding moisture control (< 10%) with dedicated dry storage to prevent Aspergillus flavus fungal infestation."
                ),
                "licensing_steps": [
                    "Obtain FSSAI Manufacturing License via [FoSCoS](https://foscos.fssai.gov.in) under Category 09 (Spices and Condiments).",
                    "Register with the Spices Board of India (Certificate of Registration as Exporter of Spices - CRES).",
                    "Submit NABL laboratory test certificate confirming zero Lead Chromate, zero Sudan dyes, and compliant curcumin levels.",
                    "Package in moisture-proof laminate pouches with 14-digit FSSAI number and AGMARK grade seal."
                ],
                "consumer_summary": (
                    "Powdered spices in India are frequently adulterated: turmeric is polished with toxic neurotoxic Lead Chromate, chilli powder is spiked with carcinogenic Sudan dye and brick dust, and black pepper is mixed with papaya seeds. "
                    "FSSAI and BIS standards mandate strict chemical purity tests."
                ),
                "consumer_checklist": (
                    "1. **Check for AGMARK & FSSAI Number:** Look for the AGMARK green or red grade stamp and 14-digit FSSAI number on the spice pouch.\n"
                    "2. **Water Glass Test for Turmeric (Lead Chromate):** Dissolve 1 tsp turmeric powder in warm water. Real turmeric settles leaving pale yellow clear water; fake turmeric with lead chromate turns the entire water murky bright fluorescent yellow.\n"
                    "3. **Chilli Powder Brick Dust Check:** Rub a pinch of chilli powder on a smooth glass surface or add to water. Brick dust or synthetic dye feels gritty and sinks immediately leaving artificial red trails.\n"
                    "4. **Black Pepper Papaya Seed Check:** Drop black pepper corns into a glass of alcohol or water. Real dried pepper sinks; dried papaya seeds float to the surface!"
                ),
                "consumer_red_flags": (
                    "- Loose open heaps of spice powders sold without batch packaging at unorganized markets.\n"
                    "- Unnaturally bright fluorescent yellow turmeric or neon scarlet red chilli powder.\n"
                    "- Gritty texture when chewed."
                ),
                "bis_care_guide": (
                    "1. Verify spice manufacturer credentials on the **FSSAI Food Safety Connect App**.\n"
                    "2. Check packaging and weights compliance via the **BIS Care App**.\n"
                    "3. Report toxic spice adulteration directly to **National Consumer Helpline (NCH)** at **1915**."
                )
            }

        # 1e. Honey & Natural Apiculture Sweeteners
        if concept_key == "honey" or any(k in tokens for k in ["honey", "madhu", "shehad", "apiculture", "invert sugar", "c4 sugar"]):
            return {
                "domain": "Honey & Natural Apiculture Sweeteners",
                "standards": [
                    {"code": "FSSAI Reg. 2.8.4", "title": "Honey and Honey Products - FSSAI Regulations", "clause": "Clause 2.8.4 Composition & Adulteration Tests"},
                    {"code": "IS 4941:2020", "title": "Extracted Honey - Specification", "clause": "Clause 4.0 Physical, Chemical & Pollen Count"}
                ],
                "scheme": "FSSAI Food Safety Framework & AGMARK Honey Certification",
                "statutory_bodies": "FSSAI, National Bee Board (NBB), Directorate of Marketing & Inspection (AGMARK), BIS",
                "table_markdown": (
                    "| Quality Parameter | Statutory Requirement (FSSAI / IS 4941) | Test Method / Reference |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Moisture Content | Maximum 20.0% by mass | IS 4941 Clause 4.2 |\n"
                    "| Fructose to Glucose Ratio (F/G) | Not less than 1.0 (Proof of floral honey) | HPLC / IS 4941 |\n"
                    "| Hydroxymethylfurfural (HMF) | Maximum 80.0 mg/kg (Max 40 mg/kg for Grade Special) | Spectrophotometric |\n"
                    "| C4 Sugars (Corn / Cane Sugar Adulteration) | Maximum 7.0% (Zero tolerance for industrial syrups) | EA-IRMS / Stable Isotope |\n"
                    "| C3 Sugars (Rice / Beet Syrup Adulteration) | Negative / SMR & TMR Compliant | LC-IRMS / NMR Profiling |\n"
                    "| Fiehe's Test (Invert Sugar) | Completely NEGATIVE | Resorcinol Color Test |\n"
                    "| Specific Gravity at 27°C | Minimum 1.35 | Hydrometer / Pycnometer |\n"
                    "| Total Ash | Maximum 0.5% by mass | IS 4941 Clause 4.5 |"
                ),
                "qc_requirements": (
                    "- **NMR & Isotope Ratio Mass Spectrometry (IRMS):** Verification against synthetic C4 and C3 commercial sugar syrups imported to mimic floral honey.\n"
                    "- **In-House Lab Equipment:** Refractometer (12–25% moisture scale), spectrophotometer for HMF, and Fiehe's reagent assembly.\n"
                    "- **Thermal Processing Bounds:** Controlled gentle warming (< 45°C) to prevent thermal degradation of natural invertase enzymes and spike of HMF."
                ),
                "licensing_steps": [
                    "Obtain FSSAI Central/State License under Category 11.2 (Other sugars and syrups / Honey) via [FoSCoS](https://foscos.fssai.gov.in).",
                    "Register apiary source with the National Bee Board (NBB) for bee-keeping origin traceability.",
                    "Submit NABL test report verifying C4 sugar (< 7%), HMF (< 80 mg/kg), and negative Fiehe's test.",
                    "Ensure compliant packaging labels with 14-digit FSSAI number and AGMARK grade seal."
                ],
                "consumer_summary": (
                    "Honey in India is frequently adulterated with cheap industrial corn syrup, sugarcane molasses, and Chinese rice syrup designed to beat simple laboratory tests. "
                    "FSSAI and BIS standards mandate nuclear magnetic resonance (NMR) and C4 sugar testing to ensure authentic floral honey."
                ),
                "consumer_checklist": (
                    "1. **Check for AGMARK & FSSAI Number:** Look for the AGMARK Special/Standard grade seal and 14-digit FSSAI number on the jar.\n"
                    "2. **Water Dispersion Test:** Drop a spoonful of honey into a clear glass of room-temperature water. Pure honey drops straight to the bottom in a firm lump; adulterated sugar syrup dissolves immediately and clouds the water.\n"
                    "3. **Crystallization Myth:** Pure raw honey naturally crystallizes in cold temperatures (due to high glucose content). Crystallization is a sign of purity, NOT sugar adulteration!\n"
                    "4. **Thumb Test:** Place a drop of honey on your thumb. Pure honey stays intact as a bead; adulterated syrup spreads or spills immediately."
                ),
                "consumer_red_flags": (
                    "- Liquid honey that never granulates or crystallizes even after months in winter.\n"
                    "- Abnormally thin, watery honey sold loose without moisture certification.\n"
                    "- Jars lacking batch numbering, botanical source, or date of extraction."
                ),
                "bis_care_guide": (
                    "1. Verify honey brand registration on the **FSSAI Food Safety Connect App**.\n"
                    "2. Check packaging integrity and net weight on the **BIS Care App**.\n"
                    "3. Report fake sugar-syrup honey directly to **National Consumer Helpline (NCH)** at **1915**."
                )
            }

        # 2. Construction, Real Estate, Cement & Building Materials
        if concept_key == "construction" or any(k in tokens for k in ["cement", "concrete", "opc", "ppc", "tmt", "steel", "rebar", "brick", "construction", "building", "saria", "loha", "1489", "is1489", "456", "is456", "1786", "is1786", "269", "is269", "స్టీల్", "టిఎంటి", "ఉక్కు", "ஸ்டீல்", "இரும்பு", "सरिया", "स्टील"]):
            return {
                "domain": "Building Materials, Cement & Structural Steel Industry",
                "standards": [
                    {"code": "IS 1786:2008", "title": "High Strength Deformed Steel Bars (TMT Fe 415, Fe 500, Fe 550D) - Specification", "clause": "Clause 8.1 Mechanical & Chemical Bounds"},
                    {"code": "IS 269:2015", "title": "Ordinary Portland Cement (33, 43 and 53 Grade) - Specification", "clause": "Clause 6.1 Physical & Compressive Strength"},
                    {"code": "IS 1489:2015", "title": "Portland Pozzolana Cement (PPC) - Specification", "clause": "Clause 7.0 Compressive Strength & Soundness"},
                    {"code": "IS 456:2000", "title": "Plain and Reinforced Concrete - Code of Practice", "clause": "Clause 5.0 Workability, Durability & Concrete Mix"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark Certification) under Cement & Steel Quality Control Orders",
                "statutory_bodies": "DPIIT, Ministry of Steel, Ministry of Commerce & Industry, Bureau of Indian Standards",
                "table_markdown": (
                    "| Product / Grade | Mandatory Quality Parameter | Permissible Requirement | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- | :--- |\n"
                    "| TMT Rebar (Fe 500D) | 0.2% Proof Stress / Yield Stress | Min 500.0 MPa | IS 1608 (Part 1) |\n"
                    "| TMT Rebar (Fe 500D) | Tensile Strength | Min 565.0 MPa (min 1.10 x YS) | IS 1608 (Part 1) |\n"
                    "| TMT Rebar (Fe 500D) | Elongation at Fracture | Min 16.0% | IS 1608 (Part 1) |\n"
                    "| TMT Rebar (Fe 500D) | Chemical: Carbon (C) | Max 0.25% by mass | IS 228 (Part 1) |\n"
                    "| TMT Rebar (Fe 500D) | Chemical: Sulphur + Phosphorus | Max 0.075% combined | IS 228 (Part 3/9) |\n"
                    "| Cement (OPC 53 Grade) | 28-Day Compressive Strength | Min 53.0 MPa | IS 4031 (Part 6) |\n"
                    "| Cement (OPC 53 Grade) | Initial Setting Time | Min 30 minutes | IS 4031 (Part 5) |\n"
                    "| Cement (OPC 53 Grade) | Final Setting Time | Max 600 minutes | IS 4031 (Part 5) |\n"
                    "| Cement (OPC 53 Grade) | Soundness (Le Chatelier) | Max 10.0 mm | IS 4031 (Part 3) |"
                ),
                "qc_requirements": (
                    "- **In-House Testing Facility:** Fully equipped mechanical and chemical testing laboratory.\n"
                    "- **Key Lab Equipment:** Universal Testing Machine (UTM) for tensile/bend tests, optical emission spectrometer (OES), compression testing machine (2000 kN), Le Chatelier molds, and Blaine air permeability apparatus.\n"
                    "- **Approved Personnel:** Supervised by a qualified Metallurgist / Materials Engineer approved by BIS.\n"
                    "- **Surveillance Records:** Cast/heat-wise chemical analysis records and daily 3, 7, and 28-day cement cube compressive registers."
                ),
                "licensing_steps": [
                    "Establish required in-house metallurgical or cement testing laboratory with calibrated equipment.",
                    "Apply online for Scheme-I Product Certification on [BIS Manakonline](https://www.manakonline.in) under the Steel/Cement QCO.",
                    "Host BIS evaluation officers for factory audit, process verification, and independent witness testing.",
                    "Receive CM/L license number and permanently roll/emboss ISI mark on rebar ribs every meter or print on cement bags."
                ],
                "consumer_summary": (
                    "Structural steel and cement form the backbone of homes and commercial buildings. "
                    "Substandard rebar or expired cement leads to structural cracks, poor earthquake resistance, and catastrophic building collapse. "
                    "BIS certification is mandatory by law under national Quality Control Orders."
                ),
                "consumer_checklist": (
                    "1. **Continuous Rebar Embossing:** On TMT bars, ensure brand name, grade (`Fe 500D`), diameter (`12mm`), and authentic BIS ISI mark are indelibly rolled every meter along the steel rib.\n"
                    "2. **Cement Bag Markings:** Check for authentic ISI logo, 7-digit CM/L number, grade (`53 Grade` or `PPC`), and Week & Year of packing (e.g., `W-38, Y-2026`).\n"
                    "3. **Freshness Verification:** Cement loses up to 20% compressive strength after 90 days. Never accept cement older than 3 months without re-testing.\n"
                    "4. **Manufacturer Test Certificate (MTC):** Ask the dealer for the manufacturer's heat/batch test certificate showing chemical and yield stress values."
                ),
                "consumer_red_flags": (
                    "- Rebars without clear brand and ISI embossing along the bar surface (often cheap re-rolled scrap steel).\n"
                    "- Hardened lumps inside cement bags (indicates moisture absorption and severe strength loss).\n"
                    "- Bags with re-stitched mouths or local names closely mimicking well-known cement brands."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number from the cement bag or steel bundle tag.\n"
                    "3. Verify that the manufacturer name and standard (`IS 1786` or `IS 269`) are currently active.\n"
                    "4. Report counterfeit steel or adulterated cement via the in-app grievance tool or call **1915**."
                )
            }

        # 3. Two-Wheeler Protective Helmets
        if concept_key == "helmets" or any(k in tokens for k in ["helmet", "helmets", "two wheeler helmet", "bike helmet", "protective headgear"]):
            return {
                "domain": "Two-Wheeler Protective Helmets & Rider Safety",
                "standards": [
                    {"code": "IS 4151:2020", "title": "Protective Helmets for Riders of Two-Wheeled Motor Vehicles - Specification", "clause": "Clause 4.0 Construction, Mass & Performance Requirements"},
                    {"code": "IS 9973:2018", "title": "Visors for Two-Wheeler Helmets - Specification", "clause": "Clause 5.0 Light Transmittance & Scratch Resistance"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under MoRTH Protective Helmets Quality Control Order",
                "statutory_bodies": "Ministry of Road Transport and Highways (MoRTH) & Bureau of Indian Standards",
                "table_markdown": (
                    "| Safety Parameter / Test | Statutory Permissible Requirement | Reference Clause (IS 4151) |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Total Mass of Helmet | Maximum 1.2 kg (1200 grams) | Clause 4.2 |\n"
                    "| Impact Attenuation (Flat Anvil) | Peak acceleration shall not exceed 300 g | Clause 9.1 |\n"
                    "| Retention System Dynamic Elongation | Max elongation 25 mm under 1 kN dynamic load | Clause 9.2 |\n"
                    "| Retention Chin Strap Residual Elongation | Shall not exceed 15 mm after test load | Clause 9.2 |\n"
                    "| Chin Strap Width | Minimum 20.0 mm width under tension | Clause 6.8 |\n"
                    "| Visor Light Transmittance | Min 85.0% for clear; min 50.0% for tinted (day use) | IS 9973 Clause 5.1 |\n"
                    "| Peripheral Field of Vision | Horizontal field >= 105° on either side | Clause 5.3 |"
                ),
                "qc_requirements": (
                    "- **In-House Testing Equipment:** Drop-tower impact test rig with triaxial accelerometer, retention system dynamic elongation rig, chin-strap detachment tester, and conditioning chambers (-10°C, +50°C, and water spray).\n"
                    "- **Approved Personnel:** Testing supervised by a qualified mechanical/safety engineer approved by BIS.\n"
                    "- **Routine Sampling:** Destructive batch testing on sample helmets drawn from each production lot."
                ),
                "licensing_steps": [
                    "Set up manufacturing facility with shell molding, EPS liner tooling, and in-house helmet impact testing rig.",
                    "Apply for Scheme-I Product Certification on [BIS Manakonline](https://www.manakonline.in) under MoRTH Helmet QCO.",
                    "Host BIS officers for witness testing (impact attenuation, chin-strap retention, visor optical clarity).",
                    "Receive CM/L license and permanently paint/imprint ISI mark with CM/L number on the outer shell back."
                ],
                "consumer_summary": (
                    "Non-ISI roadside helmets are constructed from cheap brittle plastic and fragile thermocol that shatter on impact, "
                    "offering zero crash protection and causing fatal skull fractures. Under MoRTH regulations, manufacturing, selling, "
                    "or riding with non-ISI helmets is illegal across India."
                ),
                "consumer_checklist": (
                    "1. **Indelible ISI Mark:** The authentic BIS ISI mark and 7-digit CM/L number must be permanently painted on the back exterior of the helmet (not a peelable paper sticker).\n"
                    "2. **Standard Number:** Look for **`IS 4151:2020`** inscribed directly adjacent to the ISI logo.\n"
                    "3. **Weight & Padding:** Total weight must not exceed 1.2 kg. The interior must have dense, high-density Expanded Polystyrene (EPS) foam, not soft cushion foam.\n"
                    "4. **Quick-Release Strap:** Chin strap must be at least 20 mm wide with a secure steel-reinforced buckle that locks firmly."
                ),
                "consumer_red_flags": (
                    "- Roadside stall helmets with paper stickers that peel off with a fingernail.\n"
                    "- Helmets that weigh under 600 grams or flex easily when squeezed with both hands.\n"
                    "- Visors that are distorted, wavy, or scratched brand-new."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit number from the back of the helmet.\n"
                    "3. Verify manufacturer name, brand name, and active license status.\n"
                    "4. Report roadside fake helmet vendors directly in the app or call **1915**."
                )
            }

        # 4. Gold, Silver, Jewellery & Precious Metals
        if concept_key == "gold" or any(k in tokens for k in ["gold", "silver", "jewellery", "jewelry", "hallmark", "huid", "carat", "karat", "ornament", "ahc"]):
            return {
                "domain": "Precious Metals & Jewellery Manufacturing / Retailing",
                "standards": [
                    {"code": "IS 1417:2016", "title": "Gold and Gold Alloys, Jewellery/Artefacts - Fineness and Marking - Specification", "clause": "Clause 4.0 Standard Carat Grades & HUID"},
                    {"code": "IS 2112:2014", "title": "Silver and Silver Alloys, Jewellery/Artefacts - Fineness and Marking - Specification", "clause": "Clause 3.0 Silver Grades (990, 925, 900)"}
                ],
                "scheme": "BIS Hallmarking Scheme under Section 14, BIS Act 2016 (Mandatory across 288+ Districts)",
                "statutory_bodies": "Bureau of Indian Standards & Department of Consumer Affairs",
                "table_markdown": (
                    "| Gold Carat Grade | Fineness (Parts per 1000) | Mandatory Hallmark Inscription | Negative Tolerance Allowed |\n"
                    "| :--- | :--- | :--- | :--- |\n"
                    "| 24 Karat (24K) | 999.0 | 24K999 | 0.0 (Zero negative tolerance) |\n"
                    "| 23 Karat (23K) | 958.0 | 23K958 | 0.0 (Zero negative tolerance) |\n"
                    "| 22 Karat (22K) | 916.0 | 22K916 | 0.0 (Zero negative tolerance) |\n"
                    "| 20 Karat (20K) | 833.0 | 20K833 | 0.0 (Zero negative tolerance) |\n"
                    "| 18 Karat (18K) | 750.0 | 18K750 | 0.0 (Zero negative tolerance) |\n"
                    "| 14 Karat (14K) | 585.0 | 14K585 | 0.0 (Zero negative tolerance) |\n"
                    "| 9 Karat (9K) | 375.0 | 9K375 | 0.0 (Zero negative tolerance) |"
                ),
                "qc_requirements": (
                    "- **Testing Methodology:** Fire Assay cupellation method (IS 1418) or energy-dispersive XRF spectrometry.\n"
                    "- **Assaying Infrastructure:** Batch sampling and testing conducted exclusively at BIS-recognized Assaying & Hallmarking Centres (AHC).\n"
                    "- **Traceability:** Unique 6-digit laser alphanumeric HUID engraved permanently on every piece."
                ),
                "licensing_steps": [
                    "Register as a jeweller on the [BIS Manakonline Portal](https://www.manakonline.in) (zero gov fee for micro-jewellers with turnover < 40 lakhs).",
                    "Dispatch manufactured jewellery batches to a BIS-accredited Assaying & Hallmarking Centre (AHC).",
                    "AHC samples the lot, performs fire assay purity verification, and laser-engraves the 3 mandatory hallmark symbols.",
                    "Sell hallmarked articles with the 6-digit HUID code explicitly itemized on the tax invoice."
                ],
                "consumer_summary": (
                    "BIS Hallmarking guarantees third-party certified purity of precious metals. Without hallmarking, consumers often pay for 22K gold "
                    "while receiving 18K or 14K alloyed metal, losing thousands of rupees. Mandatory hallmarking protects consumers from purity fraud."
                ),
                "consumer_checklist": (
                    "1. **The 3 Mandatory Hallmark Signs:** Every piece of genuine gold jewellery MUST carry:\n"
                    "   - (i) **Official BIS Logo** (triangular emblem)\n"
                    "   - (ii) **Purity & Fineness Mark** (e.g. `22K916` or `18K750`)\n"
                    "   - (iii) **6-Digit Alphanumeric Laser HUID** (e.g. `AB1234`)\n"
                    "2. **Itemized Tax Invoice:** Ensure the jeweller prints the exact 6-digit HUID, weight, and purity on your bill.\n"
                    "3. **Consumer Right to Test:** You can get any hallmarked jewellery piece tested at any BIS-recognized AHC for a nominal fee of ₹45 per article."
                ),
                "consumer_red_flags": (
                    "- Jewellers offering 'cash discounts' if you purchase without a tax bill or without hallmarking.\n"
                    "- Pieces marked only with '916' or 'KDM' without the official BIS triangle logo and 6-digit HUID.\n"
                    "- Jewellers refusing to print the HUID on the tax invoice."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify HUID'**.\n"
                    "3. Enter the unique 6-digit alphanumeric HUID engraved on your jewellery piece.\n"
                    "4. The app reveals jeweller name, AHC centre, article type (ring, bangle, chain), hallmarking date, and certified purity.\n"
                    "5. If purity fails or HUID is invalid, lodge a complaint in the app or call **1915**."
                )
            }

        # 5. Petroleum Retail & BS-VI Automotive Fuels
        if concept_key == "petroleum" or any(k in tokens for k in ["petrol", "fuel", "gasoline", "diesel", "bunk", "pump", "dispenser", "hsd", "peso"]):
            return {
                "domain": "Petroleum Retail & Fuel Dispensing Outlets (Petrol Bunks)",
                "standards": [
                    {"code": "IS 2796:2017", "title": "Motor Gasoline (Petrol) for Automotive Engines - Specification", "clause": "Clause 4.0 BS-VI Requirements"},
                    {"code": "IS 1460:2017", "title": "Automotive Diesel Fuel (High Speed Diesel - HSD) - Specification", "clause": "Clause 5.0 BS-VI Ultra-Low Sulphur Limits"},
                    {"code": "IS 10987:2018", "title": "Storage Tanks for Petroleum Products (Underground & Aboveground Steel Tanks)", "clause": "Clause 3.2 Fabrication & Hydrostatic Test"}
                ],
                "scheme": "Scheme-I (ISI Mark Certification Scheme) & Mandatory Quality Control Order (QCO)",
                "statutory_bodies": "Ministry of Petroleum & Natural Gas (MoPNG), PESO (Petroleum & Explosives Safety Organization), Legal Metrology Dept",
                "table_markdown": (
                    "| Fuel Property / Characteristic | BS-VI Motor Gasoline (IS 2796) | BS-VI High Speed Diesel (IS 1460) | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- | :--- |\n"
                    "| Sulphur Content (Max) | 10.0 mg/kg (ppm) | 10.0 mg/kg (ppm) | ASTM D5453 / ISO 20846 |\n"
                    "| Octane / Cetane Rating | RON Min 91.0 (Regular) / 95.0 (Prem) | Cetane Number Min 51.0 | IS 1448 (P:27 / P:9) |\n"
                    "| Lead Content (Max) | 0.005 g/L | — | IS 1448 (P:38) |\n"
                    "| Benzene Content (Max) | 1.0% by volume | — | IS 1448 (P:104) |\n"
                    "| Flash Point (Abel) | — | Min 35.0°C | IS 1448 (P:20) |\n"
                    "| Density at 15°C | 720.0 to 775.0 kg/m³ | 820.0 to 845.0 kg/m³ | IS 1448 (P:16) |\n"
                    "| Dispenser Delivery Tolerance | ±25 ml per 5 Litres | ±25 ml per 5 Litres | Legal Metrology Rules |"
                ),
                "qc_requirements": (
                    "- **Daily Quality Tests:** Fuel density hydrometer test at 15°C matched to OMC morning delivery invoice.\n"
                    "- **Adulteration Test:** Mandatory Whatman filter paper test (pure petrol evaporates within 2 mins with zero stain).\n"
                    "- **Dispenser Stamping:** Mandatory annual calibration and lead-wire stamping of electronic metering units by the Legal Metrology Inspector."
                ),
                "licensing_steps": [
                    "Procure BS-VI certified fuels strictly from authorized Oil Marketing Companies (IOCL, BPCL, HPCL).",
                    "Install underground storage tanks complying with IS 10987 and obtain PESO site clearance.",
                    "Calibrate fuel dispenser flow meters within statutory ±25 ml per 5 litres tolerance.",
                    "Maintain daily density register, filter paper test kit, and stamped 5-litre brass measure on premises."
                ],
                "consumer_summary": (
                    "Adulterated fuel ruins vehicle fuel injectors, damages catalytic converters, degrades mileage, and causes severe toxic emissions. "
                    "Every citizen has the legal right to free on-the-spot quality and quantity checks at any petrol pump in India."
                ),
                "consumer_checklist": (
                    "1. **Zero-Start on Dispenser:** Ensure the meter displays `0.00` quantity and `0.00` price before fueling begins.\n"
                    "2. **Free Filter Paper Test:** You have the legal right to ask for a filter paper test; 2 drops of petrol must evaporate in 2 minutes without leaving a pink/brown stain.\n"
                    "3. **5-Litre Measure Check:** If you suspect short-delivery, demand a check using the government-stamped 5-litre conical measure (permissible error ±25 ml).\n"
                    "4. **Morning Density Display:** Check the pump's daily density board matched against the delivery challan."
                ),
                "consumer_red_flags": (
                    "- Dispenser meter advancing before the nozzle trigger is squeezed.\n"
                    "- Pump staff refusing your request for a filter paper test or 5-litre measure verification.\n"
                    "- Strong solvent or kerosene odor emanating from the vehicle fuel tank."
                ),
                "bis_care_guide": (
                    "1. Note the petrol pump name, dispensing unit number, and location.\n"
                    "2. File a complaint directly on the OMC customer grievance portal (e.g., IOCL/BPCL/HPCL app) or on PGPortal.\n"
                    "3. Call the **National Consumer Helpline** at **1915** or notify the District Legal Metrology Inspector."
                )
            }

        # 6. IT, Electronics, Gadgets, Mobiles & Hardware
        if concept_key == "electronics" or any(k in tokens for k in ["electronics", "mobile", "phone", "laptop", "computer", "battery", "lithium", "adapter", "charger", "led", "display", "gadget"]):
            return {
                "domain": "Information Technology, Electronics & Consumer Hardware",
                "standards": [
                    {"code": "IS 13252 (Part 1):2010", "title": "Information Technology Equipment - Safety - General Requirements", "clause": "Clause 1.0 Safety & Fire Resistance"},
                    {"code": "IS 16046 (Part 2):2018", "title": "Secondary Lithium-ion Cells & Batteries - Safety Requirements", "clause": "Clause 4.0 Electrical & Thermal Abuse Tests"},
                    {"code": "IS 16102 (Part 1 & 2):2012", "title": "Self-Ballasted LED Lamps for General Lighting - Safety & Performance", "clause": "Clause 6.0 Photometric & Insulation"}
                ],
                "scheme": "Scheme-II (Compulsory Registration Scheme - CRS) mandated by MeitY",
                "statutory_bodies": "Ministry of Electronics & Information Technology (MeitY), Bureau of Indian Standards",
                "table_markdown": (
                    "| Safety Parameter | Statutory Requirement (IS 13252 / IS 16046) | Test Standard |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Enclosure Flammability | UL 94 V-0 or V-1 self-extinguishing grade | IS 13252 Clause 4.7 |\n"
                    "| Insulation Resistance | Minimum 5.0 MΩ at 500 V DC | IS 13252 Clause 5.2 |\n"
                    "| Electric Strength (Dielectric) | No flashover or breakdown at 1500 V AC | IS 13252 Clause 5.2.2 |\n"
                    "| Lithium Battery External Short Circuit | No explosion or fire at 55°C | IS 16046 (Part 2) |\n"
                    "| Lithium Battery Overcharge Test | Cell shall not catch fire or explode | IS 16046 (Part 2) |\n"
                    "| Touch Current / Leakage | Max 0.25 mA for Class II handheld units | IS 13252 Clause 5.1.4 |\n"
                    "| Adapter Temperature Rise | Enclosure surface shall not exceed 75°C | IS 13252 Clause 4.5 |"
                ),
                "qc_requirements": (
                    "- **Testing Laboratory:** Must obtain safety test reports from a BIS-recognized NABL testing laboratory in India.\n"
                    "- **Test Report Validity:** Test reports must be submitted within 90 days of issuance.\n"
                    "- **Quality System:** Factory must maintain an audited quality assurance system with batch burn-in test records."
                ),
                "licensing_steps": [
                    "Submit product samples to a BIS-recognized NABL laboratory in India for safety evaluation.",
                    "Register a manufacturer profile on the BIS CRS portal ([www.crsbis.in](https://www.crsbis.in)).",
                    "Upload test reports along with brand endorsement / authorization letters.",
                    "Receive BIS Registration Number (`R-XXXXXXXX`) and print the standard CRS mark on products and packaging."
                ],
                "consumer_summary": (
                    "Substandard mobile chargers, power banks, and laptops are prone to catastrophic battery explosions, fires, and lethal electric shocks. "
                    "Under MeitY orders, all electronic IT goods must carry the mandatory BIS CRS mark with a registered R-Number."
                ),
                "consumer_checklist": (
                    "1. **BIS CRS Mark:** Look for the standard circular BIS CRS mark with the statement 'Self Declaration - Conforming to IS 13252 (Part 1)' or 'IS 16046'.\n"
                    "2. **Registered R-Number:** Below the CRS logo, verify the authentic 8-digit registration number formatted as `R-XXXXXXXX`.\n"
                    "3. **Official Portal Link:** Check for `www.bis.gov.in` printed on the charger or gadget body.\n"
                    "4. **Pin Stability:** Adapter pins must be sturdy, well-insulated, and fit securely into sockets without sparking."
                ),
                "consumer_red_flags": (
                    "- Ultra-cheap roadside power banks or chargers with fake stickers or lacking an R-Number.\n"
                    "- Chargers that become scorching hot to touch within 10 minutes of charging.\n"
                    "- Gadgets with no brand name, manufacturer address, or country of origin."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify CRS Registration (Verify R-No)'**.\n"
                    "3. Enter the 8-digit R-Number printed on the charger or battery.\n"
                    "4. The app verifies the registered brand, model number, manufacturer, and validity.\n"
                    "5. If unlisted or fake, report the product in the app or call **1915**."
                )
            }

        # 7. Electrical Sockets, Plugs & Household Wiring
        if (concept_key == "electrical" or any(k in tokens for k in ["plug", "plugs", "socket", "sockets", "switch", "switches", "wire", "wires", "cable", "cables", "shutter", "16a", "6a", "is 1293", "is 694", "is1293", "is694"])) and not any(k in tokens for k in ["footwear", "shoes", "shoe", "solar", "feed", "poultry", "iron", "cooker", "cement"]):
            return {
                "domain": "Plugs, Sockets & Electrical Household Safety",
                "standards": [
                    {"code": "IS 1293:2019", "title": "Plugs and Socket-Outlets of Rated Voltage up to and including 250 V - Specification", "clause": "Clause 13.0 Safety Shutters & Temperature Rise"},
                    {"code": "IS 694:2010", "title": "PVC Insulated Cables for Working Voltages up to 1100 V - Specification", "clause": "Clause 5.0 Insulation Resistance & Spark Test"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under Electrical Equipment Quality Control Order",
                "statutory_bodies": "DPIIT, Central Electricity Authority (CEA), Bureau of Indian Standards",
                "table_markdown": (
                    "| Safety Parameter | Mandatory Requirement (IS 1293:2019) | Test Method Ref |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Terminal Temperature Rise | Max 45 K under full continuous rated current | Clause 19.0 |\n"
                    "| Automatic Child Safety Shutters | Mandatory for all sockets rated > 10A | Clause 13.0 |\n"
                    "| Insulation Resistance | Min 5.0 MΩ tested at 500 V DC | Clause 16.0 |\n"
                    "| Mechanical Endurance | 10,000 insertion/withdrawal cycles without failure | Clause 20.0 |\n"
                    "| Recognized Current Ratings | Only 6A (Round pin) and 16A (Round pin) recognized | Clause 6.0 |\n"
                    "| Cable Insulation Spark Test | Withstand high-voltage spark testing without puncture | IS 694 Clause 15.0 |\n"
                    "| Flame Retardancy | Withstand glow-wire test at 850°C without ignition | Clause 28.0 |"
                ),
                "qc_requirements": (
                    "- **In-House Lab Equipment:** Temperature rise test bench, endurance rig (10k cycles), dielectric breakdown tester, glow-wire tester, and spark tester.\n"
                    "- **Supervision:** Supervised by a qualified Electrical Engineer approved by BIS.\n"
                    "- **Marking:** Permanent molding of ISI mark and CM/L into plastic body dies."
                ),
                "licensing_steps": [
                    "Fabricate plastic molding dies with permanent ISI mark and CM/L cavity inserts.",
                    "Set up in-house electrical safety test benches for temperature rise and endurance.",
                    "Apply online for Scheme-I ISI Certification on [BIS Manakonline](https://www.manakonline.in).",
                    "Undergo factory audit, sample witness testing, and obtain CM/L license."
                ],
                "consumer_summary": (
                    "Over 70% of residential fires in India originate from substandard electrical sockets, loose multi-plugs, and cheap uncertified cables. "
                    "BIS certification guarantees that electrical fixtures will not melt, spark, or electrocute users under heavy household loads."
                ),
                "consumer_checklist": (
                    "1. **Molded ISI Mark:** Look for the authentic BIS ISI logo and 7-digit CM/L number permanently molded into the plastic body of the socket or plug.\n"
                    "2. **Child Safety Shutters:** Sockets must feature internal spring shutters that close automatically over live pins when the plug is removed.\n"
                    "3. **Cable Continuous Stamping:** Ensure wiring cables have `IS 694`, manufacturer brand name, and CM/L number embossed every single meter.\n"
                    "4. **Solid 3-Pin Earth:** Earth pin must be longer and thicker to ensure ground contact before current flows."
                ),
                "consumer_red_flags": (
                    "- Loose universal multi-plugs that wobble, spark, or crackle when appliances are switched on.\n"
                    "- Sockets or switch plates that turn yellow or show scorch marks around terminals.\n"
                    "- Thin, unbranded cables lacking continuous embossed markings."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number molded on the socket or printed on the wire box.\n"
                    "3. Confirm manufacturer validity and product scope.\n"
                    "4. File a complaint for fake electrical goods via the app or call **1915**."
                )
            }

        # 8. Toys, Children Goods & Play Equipment
        if concept_key == "toys" or any(k in tokens for k in ["toy", "toys", "doll", "game", "puzzle", "ride-on", "play", "infant", "child"]):
            return {
                "domain": "Toys, Infant Playthings & Childcare Products",
                "standards": [
                    {"code": "IS 9873 (Part 1):2019", "title": "Safety of Toys - Mechanical and Physical Properties", "clause": "Clause 4.0 Small Parts & Choking Hazards"},
                    {"code": "IS 9873 (Part 3):2020", "title": "Safety of Toys - Migration of Certain Elements", "clause": "Clause 4.0 Heavy Metal Limits (Lead, Cadmium, Mercury)"},
                    {"code": "IS 15644:2006", "title": "Safety of Electric Toys", "clause": "Clause 5.0 Electrical Safety & Heat"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under Toys (Quality Control) Order",
                "statutory_bodies": "Ministry of Commerce & Industry, DPIIT, Bureau of Indian Standards",
                "table_markdown": (
                    "| Safety Hazard / Characteristic | Statutory Permissible Limit | Reference Clause |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Small Parts Choking Hazard | Must NOT fit in 31.7 mm test cylinder for age < 36m | IS 9873 Part 1 Clause 4.4 |\n"
                    "| Sharp Edges and Points | Zero accessible sharp glass or metal burrs | IS 9873 Part 1 Clause 4.6 |\n"
                    "| Lead (Pb) Migration Limit | Maximum 90.0 mg/kg | IS 9873 Part 3 Table 1 |\n"
                    "| Cadmium (Cd) Migration Limit | Maximum 75.0 mg/kg | IS 9873 Part 3 Table 1 |\n"
                    "| Mercury (Hg) Migration Limit | Maximum 60.0 mg/kg | IS 9873 Part 3 Table 1 |\n"
                    "| Arsenic (As) Migration Limit | Maximum 25.0 mg/kg | IS 9873 Part 3 Table 1 |\n"
                    "| Phthalate Plasticizers (DEHP, DBP) | Maximum 0.1% by mass combined | IS 9873 Part 6 Clause 4.0 |"
                ),
                "qc_requirements": (
                    "- **In-House QC Equipment:** Small parts test cylinders, drop test platform, torque and tension test gauges, and sharp edge testers.\n"
                    "- **Chemical Testing:** Inductively Coupled Plasma (ICP-OES) or atomic absorption spectrophotometry for heavy metal migration.\n"
                    "- **Mandatory Marking:** Authentic ISI mark with CM/L number on every single toy piece."
                ),
                "licensing_steps": [
                    "Set up manufacturing and assembly facility with required physical safety test gauges.",
                    "Apply for Scheme-I Product Certification on [BIS Manakonline](https://www.manakonline.in) under Toys QCO.",
                    "Submit samples to a BIS-recognized laboratory for heavy metal migration and flammability testing.",
                    "Receive CM/L license number and affix ISI mark with license number on each toy and display box."
                ],
                "consumer_summary": (
                    "Substandard toys pose severe choking hazards from detachable small parts and cause irreversible neurological damage "
                    "from toxic lead and phthalates. Under the Toys (Quality Control) Order, selling non-ISI toys is a punishable criminal offense."
                ),
                "consumer_checklist": (
                    "1. **Authentic ISI Mark:** Check for the official BIS ISI mark and 7-digit CM/L number printed directly on the toy and on the box.\n"
                    "2. **Age Suitability Label:** Look for the clear age advisory (e.g., 'Not suitable for children under 3 years').\n"
                    "3. **No Detachable Small Parts:** For toddlers under 3, ensure eyes, wheels, and buttons cannot be pulled off and swallowed.\n"
                    "4. **Zero Chemical Fumes:** Avoid toys with strong solvent, glue, or petroleum smells indicating toxic plastics."
                ),
                "consumer_red_flags": (
                    "- Plastic toys that smell strongly of chemicals or have sharp unfiled molding seams.\n"
                    "- Toys with easily accessible button battery compartments that children can pry open.\n"
                    "- Roadside unbranded toys sold with cheap printed stickers mimicking the ISI mark without a CM/L number."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number from the toy package.\n"
                    "3. Verify manufacturer name and certified brand.\n"
                    "4. Report shops selling non-ISI toys via the app or call **1915**."
                )
            }

        # 9. Footwear, Leather & Sports Shoes
        if concept_key == "footwear" or any(k in tokens for k in ["footwear", "shoe", "shoes", "leather", "sandal", "chappal", "sports shoe", "boots", "pvc shoe", "15844", "is15844", "3735", "is3735"]):
            return {
                "domain": "Footwear, Leather Shoes, Sports Shoes & PVC Footwear",
                "standards": [
                    {"code": "IS 15844 (Part 1):2021", "title": "Sports Footwear - Specification - General Purpose", "clause": "Clause 4.0 Upper-Sole Adhesion Bond Strength & Abrasion"},
                    {"code": "IS 3735:1996", "title": "Leather Safety Boots and Shoes - Specification", "clause": "Clause 5.0 Toe Impact & Penetration Resistance"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under DPIIT Footwear Quality Control Order (QCO)",
                "statutory_bodies": "DPIIT, Ministry of Commerce & Industry, Bureau of Indian Standards",
                "table_markdown": (
                    "| Physical Property / Test | Statutory Permissible Requirement | Reference Standard |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Upper-to-Sole Adhesion Bond | Min 3.5 N/mm (Leather) / Min 3.0 N/mm (Fabric) | IS 15844 Clause 4.5 |\n"
                    "| Outsole Abrasion Resistance | Relative volume loss max 250 mm³ | IS 3400 (Part 3) |\n"
                    "| Sole Flexing Resistance | Withstand 30,000 flex cycles with cut growth <= 4.0 mm | IS 15298 |\n"
                    "| Safety Toe Impact Resistance | Withstand 200 Joules impact energy without collapse | IS 15298 (Part 2) |\n"
                    "| Sole Penetration Resistance | Withstand 1100 N puncture force | IS 15298 (Part 2) |"
                ),
                "qc_requirements": (
                    "- **In-House QC Equipment:** Bennewart sole flexing tester, upper-sole bond strength tensile tester, and DIN rotary drum abrader.\n"
                    "- **Supervision:** Testing overseen by an approved Footwear Technology / Quality Engineer.\n"
                    "- **Marking:** Indelible embossing of ISI mark and CM/L number on the shoe sole."
                ),
                "licensing_steps": [
                    "Equip factory laboratory with required flexing, tensile, and abrasion test equipment.",
                    "Submit Scheme-I Product Certification application on [BIS Manakonline](https://www.manakonline.in) under Footwear QCO.",
                    "Host BIS officers for factory inspection and sample draw for independent testing.",
                    "Receive CM/L license and imprint authentic ISI mark on shoe soles and retail boxes."
                ],
                "consumer_summary": (
                    "Substandard shoes cause heel pain, ankle instability, posture problems, and rapid sole detachment. "
                    "Under DPIIT Footwear Quality Control Orders, all footwear manufactured or sold in India must meet ISI durability standards."
                ),
                "consumer_checklist": (
                    "1. **Embossed Sole Mark:** Check for the authentic BIS ISI mark and 7-digit CM/L number embossed permanently on the shoe sole.\n"
                    "2. **Natural Flexibility:** The shoe should flex comfortably at the ball of the foot, not in the middle of the arch.\n"
                    "3. **Firm Heel Counter:** Squeeze the back heel cup; it should remain firm to support the ankle.\n"
                    "4. **Box Disclosures:** Check retail box for manufacturer address, size, MRP, and Legal Metrology details."
                ),
                "consumer_red_flags": (
                    "- Strong solvent adhesive odor indicating inferior volatile glues.\n"
                    "- Soles that detach or show peeling seams after minimal walking.\n"
                    "- Counterfeit brand logos sold without an authentic ISI mark on the sole."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit number from the shoe sole or box.\n"
                    "3. Confirm manufacturer validity.\n"
                    "4. Report non-compliant footwear via the app or call **1915**."
                )
            }

        # 10. Poultry, Chicken Centres, Hatcheries & Feeds
        if concept_key == "poultry" or any(k in tokens for k in ["poultry", "chicken", "broiler", "meat", "abattoir", "slaughterhouse", "feed", "hatchery", "egg", "birds", "mutton", "1374", "is1374", "7049", "is7049"]):
            return {
                "domain": "Poultry Farming, Retail Chicken Centres & Meat Processing",
                "standards": [
                    {"code": "IS 1374:2007", "title": "Poultry Feeds - Specification (Broiler Starter, Finisher & Layer Feeds)", "clause": "Clause 4.1 Nutritional & Aflatoxin Limits"},
                    {"code": "IS 7049:1973", "title": "Code for Handling, Processing, Quality Evaluation and Storage of Poultry", "clause": "Clause 5.0 Cold Chain & Hygiene Requirements"},
                    {"code": "IS 2491:2013", "title": "Food Hygiene - General Principles - Code of Practice", "clause": "Clause 4.0 Clean Zone & Sanitization Guidelines"}
                ],
                "scheme": "Scheme-I (ISI Mark) for Feeds & Mandatory FSSAI Category 08 (Meat Products) Certification",
                "statutory_bodies": "Ministry of Fisheries, Animal Husbandry & Dairying, FSSAI, Bureau of Indian Standards",
                "table_markdown": (
                    "| Quality / Safety Parameter | Broiler Starter Feed | Broiler Finisher Feed | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- | :--- |\n"
                    "| Crude Protein (Min) | 21.0% by mass | 19.0% by mass | IS 1374 Clause 4.1 |\n"
                    "| Crude Fibre (Max) | 5.0% by mass | 5.0% by mass | IS 1374 Clause 4.1 |\n"
                    "| Aflatoxin B1 Safety Bound (Max) | 20.0 ppb (0.02 mg/kg) | 20.0 ppb (0.02 mg/kg) | IS 1374 Annex B |\n"
                    "| Meat Chilling Temperature | < 4.0°C within 4 hours | < 4.0°C within 4 hours | IS 7049 Clause 5.0 |\n"
                    "| Frozen Poultry Storage | <= -18.0°C continuously | <= -18.0°C continuously | IS 7049 Clause 5.0 |\n"
                    "| Carcass Washing Water | 100% compliant to IS 10500 | 100% compliant to IS 10500 | IS 10500 Potable Specs |\n"
                    "| Microbiological Pathogens | Salmonella: Absent / 25g | E. Coli: Absent / g | IS 5887 (Part 3) |"
                ),
                "qc_requirements": (
                    "- **Testing Equipment:** Kjeldahl nitrogen apparatus for crude protein, ELISA/HPLC test kit for Aflatoxin B1 screening, and calibrated digital thermometers.\n"
                    "- **Cold Chain Monitoring:** Automated continuous temperature loggers for chillers (0–4°C) and deep freezers (-18°C).\n"
                    "- **Hygiene SOPs:** Carcass wash water tested quarterly against IS 10500 potable standards."
                ),
                "licensing_steps": [
                    "Obtain FSSAI State/Central License under Category 08 (Meat & Meat Products) on [FoSCoS](https://foscos.fssai.gov.in).",
                    "Procure certified poultry feed complying with IS 1374 with verified Aflatoxin test certificates (max 20 ppb).",
                    "Install digital chillers (< 4°C) and deep freezers (<= -18°C) with continuous temperature logging.",
                    "Apply for BIS Scheme-I ISI Mark on [Manakonline](https://www.manakonline.in) for packaged processed poultry."
                ],
                "consumer_summary": (
                    "Unhygienic chicken processing and adulterated poultry feeds cause severe food poisoning from Salmonella, E. coli, "
                    "and carcinogenic Aflatoxin residues in meat and eggs. FSSAI and BIS standards enforce clean food safety across India."
                ),
                "consumer_checklist": (
                    "1. **Chilled Display (< 4°C):** Dressed chicken must be stored in clean glass chillers below 4°C, never exposed to open flies and road dust.\n"
                    "2. **Potable Water Supply:** Verify that the chicken shop washes meat with clean municipal/RO running water, not stagnant bucket water.\n"
                    "3. **FSSAI License Display:** Look for the mandatory 14-digit FSSAI license certificate displayed prominently on the shop wall.\n"
                    "4. **Clean Cutting Blocks:** Cutting boards should be food-grade synthetic plastic or stainless steel, washed regularly."
                ),
                "consumer_red_flags": (
                    "- Open meat counters with flies, dirty wooden tree-stump chopping blocks, and foul odors.\n"
                    "- Chicken meat with a slimy texture, yellowish tint, or discoloration.\n"
                    "- Washing multiple bird carcasses in the same standing bucket of murky water."
                ),
                "bis_care_guide": (
                    "1. Report unhygienic chicken centres or meat shops on the FSSAI FoSCoS portal.\n"
                    "2. Call the **National Consumer Helpline (NCH)** at **1915** or notify the local Municipal Health Officer.\n"
                    "3. For packaged feeds or poultry cuts, verify the CM/L number on the **BIS Care App**."
                )
            }

        # 11. Solar Panels, Photovoltaics & Inverters
        if concept_key == "solar" or any(k in tokens for k in ["solar", "photovoltaic", "pv", "inverter", "renewable", "green energy", "panel", "14286", "is14286", "61730", "16221"]):
            return {
                "domain": "Solar Energy, Photovoltaics & Clean Power Systems",
                "standards": [
                    {"code": "IS 14286:2010", "title": "Crystalline Silicon Terrestrial Photovoltaic (PV) Modules - Design Qualification & Type Approval", "clause": "Clause 10.0 Thermal Cycling & Damp Heat"},
                    {"code": "IS/IEC 61730 (Part 1 & 2):2016", "title": "Photovoltaic (PV) Module Safety Qualification - Construction & Testing", "clause": "Clause 9.0 Electrical Safety & Fire"},
                    {"code": "IS 16221 (Part 2):2015", "title": "Safety of Power Converters for Use in Photovoltaic Power Systems (Inverters)", "clause": "Clause 4.0 Grid Inverter Safety"}
                ],
                "scheme": "Scheme-II (Compulsory Registration Scheme - CRS) mandated by MNRE",
                "statutory_bodies": "Ministry of New and Renewable Energy (MNRE), Bureau of Indian Standards",
                "table_markdown": (
                    "| Quality / Durability Parameter | Mandatory Benchmark | Test Standard |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Damp Heat Test | 85°C / 85% Relative Humidity for 1000 hours | IS 14286 Clause 10.13 |\n"
                    "| Thermal Cycling Test | -40°C to +85°C for 200 cycles | IS 14286 Clause 10.11 |\n"
                    "| Humidity Freeze Test | 85°C/85% RH followed by -40°C freeze (10 cycles) | IS 14286 Clause 10.12 |\n"
                    "| Inverter Total Harmonic Distortion | THD < 3.0% at rated output current | IS 16221 (Part 2) |\n"
                    "| Anti-Islanding Trip Protection | Disconnect from grid within 2.0 seconds of outage | IS 16221 (Part 2) |\n"
                    "| Hail Impact Resistance | Withstand 25 mm ice sphere at 23 m/s | IS 14286 Clause 10.17 |"
                ),
                "qc_requirements": (
                    "- **Testing Infrastructure:** Must obtain Type Approval test reports from the National Institute of Solar Energy (NISE) or BIS-recognized NABL laboratories.\n"
                    "- **Traceability:** Mandatory embedded RFID tag laminated inside the solar module glass with manufacturing serial numbers."
                ),
                "licensing_steps": [
                    "Submit module samples to NISE or a BIS-recognized testing lab for IS 14286 and IS/IEC 61730 testing.",
                    "Submit test reports to the BIS CRS portal ([www.crsbis.in](https://www.crsbis.in)) for grant of R-Number.",
                    "Secure enlistment on the Approved List of Models and Manufacturers (ALMM) maintained by MNRE.",
                    "Affix CRS mark with registered R-Number and embedded internal RFID tracking chip."
                ],
                "consumer_summary": (
                    "Uncertified solar panels degrade rapidly, losing 30–50% power output within 2 years, and can cause rooftop electrical fire hazards. "
                    "MNRE mandates that only BIS-certified and ALMM-enlisted solar modules are eligible for rooftop subsidies."
                ),
                "consumer_checklist": (
                    "1. **BIS CRS Mark & R-Number:** Verify the official CRS logo and registered `R-XXXXXXXX` printed on the panel junction box and datasheet.\n"
                    "2. **Embedded RFID Tag:** Look inside the glass laminate; an authentic solar panel MUST have an internal RFID chip with module serial number.\n"
                    "3. **MNRE ALMM Enlistment:** Check that the specific brand and model are listed on the MNRE Approved List of Models and Manufacturers.\n"
                    "4. **Warranty Card:** Ensure a 25-year linear power warranty guaranteeing at least 80% output at Year 25."
                ),
                "consumer_red_flags": (
                    "- Panels lacking an embedded RFID tag inside the glass.\n"
                    "- Second-hand or B-grade imported panels re-stickered with local brand names.\n"
                    "- Vendors claiming government rooftop solar subsidies without ALMM approval."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify CRS Registration (Verify R-No)'** and enter the 8-digit R-Number.\n"
                    "3. Verify module wattage, model number, and manufacturer validity.\n"
                    "4. Lodge a grievance on the app or call **1915**."
                )
            }

        # 12. Medical Devices, Healthcare & PPE
        if concept_key == "medical" or any(k in tokens for k in ["mask", "medical", "hospital", "ppe", "surgical", "syringe", "thermometer", "pharma", "health"]):
            return {
                "domain": "Medical Devices, Hospital Consumables & Healthcare PPE",
                "standards": [
                    {"code": "IS 16289:2014", "title": "Medical Face Masks - Specification", "clause": "Clause 5.0 Bacterial Filtration Efficiency (BFE)"},
                    {"code": "IS 10258:2002", "title": "Sterile Hypodermic Syringes for Single Use - Specification", "clause": "Clause 4.0 Sterility & Pyrogen Testing"},
                    {"code": "IS 3055:2018", "title": "Clinical Thermometers - Specification", "clause": "Clause 6.0 Accuracy & Response Time"}
                ],
                "scheme": "Scheme-I (ISI Mark) & Medical Devices Rules 2017 (CDSCO Interoperability)",
                "statutory_bodies": "Central Drugs Standard Control Organization (CDSCO) & BIS",
                "table_markdown": (
                    "| Medical Product / Test | Statutory Permissible Requirement | Reference Standard |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Surgical Mask BFE (Class 1) | Bacterial Filtration Efficiency >= 95.0% | IS 16289 Clause 5.1 |\n"
                    "| Surgical Mask BFE (Class 2) | Bacterial Filtration Efficiency >= 98.0% | IS 16289 Clause 5.1 |\n"
                    "| Surgical Mask BFE (Class 3) | BFE >= 98.0% + splash resistance at 120 mmHg | IS 16289 Clause 5.1 |\n"
                    "| Differential Pressure (Breathability) | Delta P < 49.0 Pa/cm² | IS 16289 Clause 5.2 |\n"
                    "| Syringe Sterility Test | Zero biological growth after 14 days incubation | IS 10258 Clause 4.2 |\n"
                    "| Syringe Pyrogenicity | Free from bacterial endotoxins (< 0.5 EU/ml) | IS 10258 Clause 4.3 |\n"
                    "| Clinical Thermometer Accuracy | Maximum permissible error ±0.1°C | IS 3055 Clause 6.0 |"
                ),
                "qc_requirements": (
                    "- **Cleanroom Manufacturing:** ISO Class 7 or Class 8 cleanroom with continuous HEPA particulate monitoring.\n"
                    "- **Sterility QC:** Validated ethylene oxide (EtO) or gamma radiation sterilization with biological indicators."
                ),
                "licensing_steps": [
                    "Obtain CDSCO Manufacturing License (Form MD-5 / MD-9) on the [SUGAM Portal](https://cdsco.gov.in).",
                    "Set up cleanroom production and in-house particulate challenge / sterility test lab.",
                    "Apply for Scheme-I ISI Certification on [BIS Manakonline](https://www.manakonline.in).",
                    "Undergo audit and receive CM/L license for medical packaging."
                ],
                "consumer_summary": (
                    "Substandard face masks and non-sterile syringes fail to block viruses and bacteria, causing fatal bloodstream infections. "
                    "BIS and CDSCO certifications guarantee cleanroom sterility and high-efficiency filtration."
                ),
                "consumer_checklist": (
                    "1. **BIS ISI Mark & CM/L:** Check for the authentic ISI mark and 7-digit CM/L number on the retail box.\n"
                    "2. **CDSCO License Number:** Verify manufacturing license (e.g. `MFG/MD/2026/000123`) printed on packaging.\n"
                    "3. **Blister Seal Integrity:** Syringes must be in 100% sealed, airtight individual blister wrappers.\n"
                    "4. **3-Ply Melt-Blown Middle Layer:** Certified surgical masks must have a real melt-blown filtration layer (melts, does not burn like paper)."
                ),
                "consumer_red_flags": (
                    "- Single-ply or cloth masks falsely sold as 'Surgical Masks'.\n"
                    "- Syringes with unsealed, wrinkled, or yellowed paper wrappers.\n"
                    "- Missing sterilization batch details, date of manufacture, or expiry dates."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number from the box.\n"
                    "3. Confirm manufacturer credentials.\n"
                    "4. Report counterfeit medical consumables via the app or call **1915**."
                )
            }

        # 13. Fertilizers, Agrochemicals & Crop Nutrients
        if concept_key == "fertilizer" or any(k in q for k in ["fertilizer", "urea", "dap", "khad", "pesticide", "insecticide"]):
            return {
                "domain": "Fertilizers, Agrochemicals & Crop Nutrients",
                "standards": [
                    {"code": "IS 540:2019", "title": "Urea, Fertilizer Grade - Specification", "clause": "Clause 3.0 Nitrogen Content & Biuret Bounds"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under Fertilizer Control Order (FCO)",
                "statutory_bodies": "Department of Fertilizers, Ministry of Agriculture, BIS",
                "table_markdown": (
                    "| Quality Parameter (Urea IS 540) | Statutory Requirement | Test Method (IS Code) |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Total Nitrogen Content (Dry Basis) | Minimum 46.0% by mass | IS 540 Clause 3.1 |\n"
                    "| Biuret Bound (Max) | Maximum 1.5% by mass (prevents crop toxicity) | IS 540 Clause 3.2 |\n"
                    "| Moisture Content (Max) | Maximum 1.0% by mass | IS 540 Clause 3.3 |\n"
                    "| Particle Size | Min 90% shall pass through 2.8 mm sieve | IS 540 Clause 3.4 |\n"
                    "| Mandatory Neem Coating | Uniformly coated with neem oil | FCO Mandatory Order |"
                ),
                "qc_requirements": (
                    "- **In-House QC Equipment:** Kjeldahl nitrogen apparatus, spectrophotometer for biuret analysis, and Karl Fischer titrator for moisture.\n"
                    "- **Supervision:** Testing supervised by an approved Agricultural Chemist."
                ),
                "licensing_steps": [
                    "Obtain FCO manufacturing authorization from the State Agriculture Department.",
                    "Equip chemical lab with Kjeldahl nitrogen apparatus and moisture analyzer.",
                    "Apply for Scheme-I ISI Mark on [BIS Manakonline](https://www.manakonline.in).",
                    "Print ISI mark and statutory FCO subsidized MRP details on all bags."
                ],
                "consumer_summary": (
                    "Substandard or adulterated urea with high biuret content burns crop roots and ruins farmer yields. "
                    "BIS and FCO standards protect farmers from counterfeit fertilizers."
                ),
                "consumer_checklist": (
                    "1. **Authentic Stenciled ISI Mark:** Look for the clear BIS ISI logo and 7-digit CM/L number stenciled on the bag.\n"
                    "2. **100% Neem Coated:** Ensure urea has the characteristic mild neem oil aroma and slight yellowish tint.\n"
                    "3. **Rapid Solubility Test:** Dissolve 1 spoonful of urea in a small glass of water; pure urea dissolves rapidly and the water turns noticeably cold to touch.\n"
                    "4. **Subsidized MRP:** Never pay above the government-notified printed MRP on the bag."
                ),
                "consumer_red_flags": (
                    "- Urea bags without neem coating or that fail to produce a cold reaction in water.\n"
                    "- Retailers forcing farmers to purchase unwanted pesticide bottles as a condition to buy urea."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit number from the bag.\n"
                    "3. Verify fertilizer manufacturer validity.\n"
                    "4. Report black-marketing or fake fertilizer via the app or call **1915**."
                )
            }

        # 14. HDPE & PVC Pipes for Potable Water Supply
        if any(k in tokens for k in ["pipe", "pipes", "hdpe", "pvc", "cpvc", "plumbing"]):
            return {
                "domain": "HDPE & PVC Pipes for Potable Water Supply",
                "standards": [
                    {"code": "IS 4984:2016", "title": "Polyethylene Pipes for Water Supply - Specification", "clause": "Clause 6.0 Hydrostatic Pressure & Carbon Black"},
                    {"code": "IS 4985:2021", "title": "Unplasticized PVC Pipes for Potable Water Supplies - Specification", "clause": "Clause 8.0 Hydrostatic Pressure Tests"}
                ],
                "scheme": "Scheme-I (Mandatory ISI Mark) under Pipes Quality Control Order",
                "statutory_bodies": "DPIIT, Ministry of Jal Shakti, Bureau of Indian Standards",
                "table_markdown": (
                    "| Pipe Characteristic | Statutory Requirement (IS 4984 / IS 4985) | Test Method |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Internal Hydrostatic Pressure Test | Withstand test pressure for 165 hours at 80°C without burst | IS 4984 Clause 8.1 |\n"
                    "| Carbon Black Content (HDPE) | 2.0% to 2.5% uniformly dispersed | IS 4984 Clause 6.3 |\n"
                    "| Melt Flow Rate (MFR) Variation | Shall not exceed 20% from raw material | IS 4984 Clause 6.2 |\n"
                    "| Tensile Strength | Minimum 19.0 MPa at break | IS 4984 Clause 8.3 |\n"
                    "| Reversion Test (PVC) | Longitudinal reversion shall not exceed 5% | IS 4985 Clause 8.2 |"
                ),
                "qc_requirements": (
                    "- **In-House Testing Equipment:** Multi-channel hydrostatic pressure test station (80°C water bath), carbon black analyzer, and UTM tensile tester.\n"
                    "- **Marking:** Continuous hot-foil embossing of ISI mark, CM/L, and pressure rating every meter."
                ),
                "licensing_steps": [
                    "Equip pipe laboratory with 80°C hydrostatic burst testing tanks and carbon black furnaces.",
                    "Apply for Scheme-I ISI Mark on [BIS Manakonline](https://www.manakonline.in) under Pipes QCO.",
                    "Host BIS officers for witness burst pressure testing and obtain CM/L license.",
                    "Emboss ISI mark, CM/L number, standard number, and PN rating on pipe every meter."
                ],
                "consumer_summary": (
                    "Substandard pipes crack underground, leak contaminated groundwater into domestic drinking supplies, and cause severe building dampness. "
                    "BIS certification guarantees non-toxic materials and high pressure resilience."
                ),
                "consumer_checklist": (
                    "1. **Continuous Indelible Embossing:** Look for authentic ISI mark, CM/L number, standard number (`IS 4984` or `IS 4985`), pressure rating (e.g. `PN 10`), and diameter stamped every single meter along the pipe.\n"
                    "2. **Concentric Wall Thickness:** Check pipe cross-section for circular concentricity and smooth interior.\n"
                    "3. **Impact Toughness:** Certified pipes do not crack or shatter when dropped on hard concrete."
                ),
                "consumer_red_flags": (
                    "- Brittle, chalky pipes made with excessive calcium carbonate filler.\n"
                    "- Pipes with faint ink markings that rub off easily with a finger.\n"
                    "- Uneven wall thickness that bursts under domestic water pressure."
                ),
                "bis_care_guide": (
                    "1. Open the **BIS Care App**.\n"
                    "2. Tap **'Verify License Details' (Verify CM/L)** and enter the 7-digit CM/L number stamped on the pipe.\n"
                    "3. Confirm manufacturer validity.\n"
                    "4. File a grievance via the app or call **1915**."
                )
            }

        return None

    def _generate_fallback_response(
        self,
        query: str,
        mode: ChatMode,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """High-precision deterministic RAG generator with dual-persona intelligence (Industry vs Consumer)."""
        # 0. Check statutory topics first
        stat_topic = bis_statutory_topics_service.resolve_statutory_topic(query)
        if stat_topic:
            return stat_topic["answer"]

        # 1. Check if query maps to a comprehensive business domain
        business_data = self._resolve_business_domain_standards(query)
        if business_data:
            b_domain = business_data["domain"]
            b_scheme = business_data["scheme"]
            b_bodies = business_data.get("statutory_bodies", "Bureau of Indian Standards")
            
            if mode == ChatMode.CONSUMER:
                lines = [
                    f"### 🛡️ Citizen & Consumer Protection Guide: {b_domain}",
                    f"{business_data.get('consumer_summary', '')}",
                    "",
                    "#### 🔍 What Indian Consumers Must Check (The 4-Point Safety Checklist):",
                    business_data.get('consumer_checklist', ''),
                    "",
                    "#### ⚠️ Consumer Red Flags & Health/Safety Hazards:",
                    business_data.get('consumer_red_flags', ''),
                    "",
                    "#### 📲 How to Verify Authenticity on the BIS Care App & Report Fake Products:",
                    business_data.get('bis_care_guide', '')
                ]
                return "\n".join(lines)
            else:
                is_food_domain = any(k in b_domain.lower() for k in ["food", "juice", "beverage", "restaurant", "catering", "sugarcane"]) or "fssai" in b_scheme.lower()
                scheme_label = "Mandatory Statutory Scheme" if is_food_domain else "Mandatory BIS Certification Scheme"
                scheme_law = "under Food Safety and Standards Act 2006 & BIS Act" if is_food_domain else "under BIS Act 2016"
                if is_food_domain:
                    compliance_status = "Mandatory statutory food business licensing and standards in force across India. Under Section 31 of the Food Safety and Standards Act 2006, operating any food or beverage enterprise without an active FSSAI License/Registration is a cognizable legal offence carrying statutory penalties and closure."
                else:
                    compliance_status = "Mandatory Quality Control Order (QCO) in force across India. Under Section 16 & Section 29 of the BIS Act 2016, manufacturing, importing, stocking, or distributing without an active BIS CM/L license is a cognizable legal violation."
                lines = [
                    f"### 🎯 Business Assessment & Statutory Framework: {b_domain}",
                    f"**{scheme_label}:** `{b_scheme}` {scheme_law}",
                    f"**Enforcing Statutory Authorities:** {b_bodies}",
                    f"**Statutory Compliance Status:** {compliance_status}",
                    "",
                    "#### 📜 Governing Indian Standards (IS Codes):"
                ]
                for std in business_data["standards"]:
                    lines.append(f"- **{std['code']}**: *{std['title']}* (`{std['clause']}`)")
                
                lines.append("")
                lines.append("#### 📊 Mandatory Technical Specifications & Permissible Limits:")
                lines.append(business_data.get("table_markdown", ""))
                
                lines.append("")
                lines.append("#### 🧪 In-House Testing Laboratory & Quality Control Requirements:")
                lines.append(business_data.get("qc_requirements", ""))
                
                lines.append("")
                lines.append("#### 💡 Actionable Next Steps for Certification:")
                for idx, step in enumerate(business_data.get("licensing_steps", []), 1):
                    lines.append(f"{idx}. {step}")
                
                return "\n".join(lines)

        if not retrieved_chunks:
            # Fallback to statutory domain resolvers
            stat_match = bis_statutory_topics_service.resolve_statutory_topic(query)
            if stat_match:
                return stat_match["answer"]
            biz_match = self._resolve_business_domain_standards(query)
            if biz_match:
                return self._generate_fallback_response(query, mode, [])
            fssai_match = fssai_food_safety_service.resolve_fssai_query(query)
            if fssai_match:
                return fssai_match["answer"]
            iso_match = online_standards_resolver.resolve_iso_or_store_licensing(query, mode=mode.value)
            if iso_match:
                return iso_match["answer"]
            return STANDARDIZED_REFUSAL

        # Multi-Domain Negative Firewall between query and retrieved chunks
        q_norm = nlp_query_processor.normalize_text(query).lower()
        q_intent = nlp_query_processor.classify_intent_and_entities(query)
        detected_domain = q_intent.get("detected_domain", "GENERAL")
        
        is_food_query = (detected_domain == "FOOD_AGRICULTURE") or any(w in q_norm for w in ["food", "paneer", "palak", "eating", "eat", "milk", "paala", "doodh", "water", "curry", "diet", "nutrition", "dish", "fssai", "dairy"])
        is_civil_query = (detected_domain == "CONSTRUCTION_CIVIL") or any(w in q_norm for w in ["cement", "simantu", "concrete", "m20", "m25", "slab", "dhalai", "steel", "sariya", "rebar", "inumu", "fe 500", "1786", "269", "456", "pipe", "hdpe", "4984", "brick", "sand"])
        is_gold_query = (detected_domain == "PRECIOUS_METALS") or any(w in q_norm for w in ["gold", "sona", "bangaaram", "thangam", "silver", "chandi", "vendi", "hallmark", "huid", "carat", "karat", "916", "750", "jewell"])
        is_electrical_query = (detected_domain == "ELECTRICAL_ELECTRONICS") or any(w in q_norm for w in ["plug", "socket", "wire", "cable", "theega", "taar", "1293", "694", "battery", "16046", "solar", "14286", "fan", "374"])

        compatible_chunks = []
        for c in retrieved_chunks:
            c_info = (c.get("doc_title", "") + " " + c.get("is_code", "")).lower()
            c_food = any(w in c_info for w in ["water", "food", "milk", "paneer", "14543", "13428", "10500", "11536", "10484"])
            c_civil = any(w in c_info for w in ["steel", "rebar", "cement", "concrete", "pipe", "1786", "269", "456", "4984"])
            c_gold = any(w in c_info for w in ["gold", "silver", "hallmark", "huid", "1417", "1418", "2112"])
            c_elec = any(w in c_info for w in ["plug", "socket", "cable", "wire", "battery", "1293", "694", "16046", "374"])

            if is_food_query and (c_civil or c_elec or c_gold):
                continue
            if is_civil_query and (c_food or c_gold or c_elec):
                continue
            if is_gold_query and (c_food or c_civil or c_elec):
                continue
            if is_electrical_query and (c_food or c_civil or c_gold):
                continue
            compatible_chunks.append(c)

        if compatible_chunks:
            retrieved_chunks = compatible_chunks
        else:
            # Fallback to statutory domain resolvers when chunks violate domain boundary
            stat_match = bis_statutory_topics_service.resolve_statutory_topic(query)
            if stat_match:
                return stat_match["answer"]
            biz_match = self._resolve_business_domain_standards(query)
            if biz_match:
                return self._generate_fallback_response(query, mode, [])
            fssai_match = fssai_food_safety_service.resolve_fssai_query(query)
            if fssai_match:
                return fssai_match["answer"]
            iso_match = online_standards_resolver.resolve_iso_or_store_licensing(query, mode=mode.value)
            if iso_match:
                return iso_match["answer"]
            return STANDARDIZED_REFUSAL

        top_chunk = retrieved_chunks[0]
        is_code = top_chunk.get("is_code", "BIS Standard")
        doc_title = top_chunk.get("doc_title", "Specification")
        clause = top_chunk.get("clause", "Clause")
        page = top_chunk.get("page_number", 1)

        # Enforce semantic grounding between user query and retrieved top_chunk:
        # If query has no relationship to top_chunk and is out-of-scope, do NOT claim this standard applies!
        top_chunk_code = is_code.upper()
        top_chunk_title = doc_title.lower()
        q_clean = query.lower()
        has_chunk_affinity = (
            (top_chunk_code and top_chunk_code in q_clean.upper()) or
            any(w in q_clean for w in top_chunk_title.split() if len(w) > 3) or
            bool(re.search(r'\b(is\s*[:\-]?\s*\d{3,5}|bis|isi|qco|fssai|hallmark|huid|standards?)\b', q_clean)) or
            bool(self._resolve_business_domain_standards(query)) or
            bool(bis_statutory_topics_service.resolve_statutory_topic(query))
        )
        if not has_chunk_affinity:
            return STANDARDIZED_REFUSAL

        # If retrieved chunk is a dynamic government commercial guide, return the authoritative guide directly
        if is_code.startswith("Gov Commercial Code:") or is_code.startswith("Gov Commodity Standard:") or is_code.startswith("Gov Commercial Framework:"):
            dyn_data = online_standards_resolver.resolve_iso_or_store_licensing(query, mode=mode.value)
            if dyn_data:
                return dyn_data["answer"]
            return STANDARDIZED_REFUSAL

        # Filter chunks to only those matching top standard (or related clauses)
        target_is_code = top_chunk.get("is_code", "")
        relevant_chunks = [c for c in retrieved_chunks if c.get("is_code") == target_is_code or not target_is_code]
        if not relevant_chunks:
            relevant_chunks = retrieved_chunks

        # Extract markdown tables and key technical parameters without duplication
        extracted_tables = []
        seen_table_titles = set()
        specific_highlights = []

        q_lower = query.lower()
        target_param_keywords = [w for w in ["lead", "arsenic", "mercury", "cadmium", "chromium", "tds", "ph", "turbidity", "hardness", "yield", "tensile", "elongation", "insulation", "shutter"] if w in q_lower]

        for c in relevant_chunks:
            t = c.get("text", "")
            tbl_data = c.get("table_data") or {}
            table_md = tbl_data.get("markdown", "")

            # Check if table markdown is present in table_data or raw text
            if not table_md and "|" in t and re.search(r'\|\s*[-:]{2,}\s*\|', t):
                table_lines = [l for l in t.split("\n") if "|" in l]
                if len(table_lines) >= 3:
                    table_md = "\n".join(table_lines)

            if table_md:
                # Deduplicate by table title or first row
                tbl_title = c.get("table_title") or c.get("clause") or table_md.split("\n")[0]
                if tbl_title not in seen_table_titles:
                    seen_table_titles.add(tbl_title)
                    extracted_tables.append(table_md)

                    # Check for specific user requested parameters inside table rows
                    if target_param_keywords and tbl_data.get("rows"):
                        for row in tbl_data["rows"]:
                            row_str = " ".join(row).lower()
                            if any(k in row_str for k in target_param_keywords):
                                param_name = row[1] if len(row) > 1 else row[0]
                                param_limit = row[2] if len(row) > 2 else (row[1] if len(row) > 1 else "")
                                test_method = row[3] if len(row) > 3 else ""
                                specific_highlights.append(f"- **{param_name}:** Permissible Limit: **{param_limit}**" + (f" *(Test Method: {test_method})*" if test_method else ""))

        if mode == ChatMode.INDUSTRY:
            is_food_water = any(k in doc_title.lower() or k in is_code.lower() for k in ["water", "food", "beverage", "dairy", "milk", "oil", "spice", "honey", "juice", "14543", "13428", "10500"])
            scheme_name = "Scheme-I (ISI Mark Certification Scheme)" if any(k in doc_title.lower() for k in ["water", "steel", "pipe", "plug", "socket", "cement", "helmet", "fe 500d", "14543", "1786", "4984", "1293", "4151"]) else "Scheme-II (Compulsory Registration Scheme - CRS)" if any(k in doc_title.lower() for k in ["battery", "it equipment", "electronic", "lamp", "led"]) else "BIS Conformity Assessment Scheme"
            
            # HSN and GST mapping
            hsn_code = "2201 (18% GST)" if "water" in doc_title.lower() or "14543" in is_code else "7214 (18% GST)" if "steel" in doc_title.lower() or "1786" in is_code else "8536 (18% GST)" if "plug" in doc_title.lower() or "socket" in doc_title.lower() else "General Industrial Goods (18% GST)"
            
            lines = [
                f"### 🎯 Business Assessment & Applicable Certification Scheme ({is_code})",
                f"**Product / Standard:** *{doc_title}*",
                f"**Mandatory Certification Scheme:** `{scheme_name}` under BIS Act 2016",
                f"**Primary Clause Reference:** `{clause}`, Page {page}",
                "",
                "#### 📊 Mandatory Technical Specifications & Permissible Limits:",
            ]
            
            if specific_highlights:
                lines.append("**Key Requested Parameters & Permissible Limits:**")
                for h in specific_highlights:
                    lines.append(h)
                lines.append("")

            if extracted_tables:
                for tbl in extracted_tables[:2]:
                    lines.append(tbl)
                    lines.append("")
            else:
                for c in relevant_chunks[:2]:
                    lines.append(f"**[{c.get('is_code')} - {c.get('clause')}]**")
                    lines.append(c.get("text", "").strip()[:400] + "...")
                    lines.append("")

            lines.append("#### 🧪 In-House Quality Control & Testing Instructions:")
            lines.append(f"- **Scheme of Testing & Inspection (STI):** Production batches must follow the statistical sampling procedure defined in **{is_code}**.")
            lines.append(f"- **Testing Facilities:** In-house laboratory must be equipped with calibrated instruments traceable to National Physical Laboratory (NPL).")
            lines.append(f"- **Qualified Personnel:** Testing must be carried out by a qualified chemist, microbiologist, or quality engineer approved by BIS.")
            lines.append(f"- **Surveillance Records:** Daily batch test registers and counter-samples must be maintained for BIS factory surveillance audits.")
            lines.append("")
            
            lines.append("#### 🏭 MSME Subsidies & Incentives (Ministry of MSME):")
            lines.append("- **50% Fee Concession:** Micro and Small Enterprises with an active [Udyam Registration](https://udyamregistration.gov.in) receive an official **50% concession on BIS Marking Fees** (plus an additional 20% for women-owned enterprises).")
            lines.append("- **Testing Subsidy:** MSMEs can claim financial reimbursement for testing fees at BIS and NABL laboratories under the MSME Champion Scheme.")
            lines.append("- **Subsidized Credit:** Collateral-free laboratory and machinery financing up to ₹5 Crores under CGTMSE.")
            lines.append("")
            
            lines.append("#### 🧾 GST & Statutory Clearances:")
            lines.append(f"- **GSTIN & HSN Compliance:** Classified under **HSN {hsn_code}**. Mandatory electronic billing with GSTIN registered via [gst.gov.in](https://www.gst.gov.in). E-way bill required for consignments exceeding ₹50,000.")
            if is_food_water:
                lines.append("- **FSSAI Food Business License:** Under Section 31 of the Food Safety & Standards Act 2006 and FSS (Prohibition & Restrictions on Sales) Reg 2.3.14, no manufacturer can sell without **both** an active FSSAI 14-digit license ([FoSCoS](https://foscos.fssai.gov.in)) and a valid BIS ISI CM/L mark.")
            lines.append("")
            
            lines.append("#### 💡 Actionable Next Steps for Certification:")
            lines.append(f"1. **Online Application:** Register and apply via the official [BIS Manakonline Portal](https://www.manakonline.in) under {scheme_name}.")
            lines.append(f"2. **Calibration:** Calibrate all in-house testing equipment with NABL-accredited calibration laboratories.")
            lines.append(f"3. **Factory Audit:** BIS evaluating officers will conduct an on-site factory audit and witness sample testing.")
            lines.append(f"4. **Grant of License:** Upon verification of independent laboratory test reports, receive the official CM/L (Certification Marks / License) number and apply the authentic ISI mark on products.")
            return "\n".join(lines)

        else:  # CONSUMER MODE
            lines = [
                f"### 🛡️ Citizen & Consumer Protection Guide: {is_code} ({doc_title})",
                f"Under the Bureau of Indian Standards **{is_code}**, products manufactured, imported, or sold in India are legally mandated to comply with rigorous national safety and quality benchmarks to protect consumer health, life, and property.",
                "",
                "#### 🔍 What Indian Consumers Must Check (The 4-Point Safety Checklist):",
                f"1. **Authentic BIS Mark:** Check for the official rectangular ISI mark (or CRS logo) embossed or printed clearly on the product body and retail packaging.",
                f"2. **The 7 or 8-Digit CM/L License Number:** Below or above the ISI logo, confirm the presence of an authentic license number formatted as `CM/L-XXXXXXXX`. *Note:* An ISI mark without a valid CM/L number is counterfeit!",
                f"3. **Indian Standard Code:** Confirm that **`{is_code}`** is printed alongside the mark.",
                f"4. **Packaging Integrity & Batch Codes:** Check for unbroken tamper-evident seals, clear batch numbering, date of manufacture, and customer care details per Legal Metrology rules.",
                "",
                "#### ⚠️ Consumer Red Flags & Substandard Warning Signs:",
                f"- Products sold with faint, blurred, or peelable paper ISI stickers without a CM/L license number.",
                f"- Unbranded goods sold with vague verbal claims (e.g. 'Standard Quality', 'Export Quality') lacking official BIS certification.",
                f"- Substandard products that bypass electrical insulation, chemical safety, or structural strength requirements, posing severe fire, toxicity, or injury risks.",
                "",
                "#### 📲 How to Verify Authenticity on the BIS Care App & Report Fake Products:",
                "1. Download the free official **BIS Care Mobile App** from Google Play Store or Apple App Store.",
                "2. Tap **'Verify License Details' (Verify CM/L)** or **'Verify CRS Registration'**.",
                "3. Enter the 7/8-digit CM/L number to view verified manufacturer name, factory address, brand, and validity status.",
                "4. **Lodge Complaint:** If the product is substandard, fake, or the dealer misleads you, tap 'Lodge Complaint' directly in the app or call the **National Consumer Helpline (NCH)** toll-free at **1915**."
            ]
            return "\n".join(lines)


    def _sanitize_input(self, text: str) -> Tuple[str, bool]:
        """Sanitize query against prompt injection attacks, SQL patterns, and anonymize user PII with cartoon aliases."""
        from app.core.security_firewall import pii_shield, security_firewall
        from app.core.security_guard import sanitize_and_shield_input, anonymize_metadata
        cleaned, is_threat = sanitize_and_shield_input(text)
        firewall_threat, _ = security_firewall.inspect_payload(text)
        is_threat = is_threat or firewall_threat
        # Redact any personal identifiers with safe cartoon aliases
        cleaned = pii_shield.redact_and_cartoonize_pii(cleaned)
        # Anonymize device/paths/IPs
        cleaned = anonymize_metadata(cleaned)
        # Neutralize XML context tag injection to prevent breaking out of LLM sandwich defense
        cleaned = cleaned.replace("<", "&lt;").replace(">", "&gt;")
        return cleaned, is_threat

    def _sanitize_output(self, text: str) -> str:
        """Sanitize AI response to eliminate XSS script tags and anonymize device/user metadata with cartoon aliases."""
        if not text:
            return ""
        from app.core.security_firewall import pii_shield
        from app.core.security_guard import anonymize_metadata
        # Neutralize script tags
        cleaned = re.sub(r'(?i)<\s*script[^>]*>.*?<\s*/\s*script\s*>', '', text, flags=re.DOTALL)
        # Neutralize dangerous javascript: and data: URIs in markdown links
        cleaned = re.sub(r'(?i)javascript\s*:', 'blocked:', cleaned)
        cleaned = re.sub(r'(?i)data:\s*text/html', 'blocked:', cleaned)
        # Anonymize real device paths, usernames, hardware specs or IPs with cartoon aliases
        cleaned = anonymize_metadata(cleaned)
        # Redact and cartoonize any personal data in output
        cleaned = pii_shield.redact_and_cartoonize_pii(cleaned)
        return cleaned

    def _is_out_of_domain_query(self, query: str) -> bool:
        """
        Fast-path detector for queries clearly outside the Bureau of Indian Standards,
        Quality Control Orders, and commercial trade licensing domain.
        """
        q = query.lower().strip()
        
        # If explicit IS / ISO standard code is present, it is NEVER out of domain
        if re.search(r'\b(is\s*[:\-]?\s*\d{3,5}|iso\s*[:\-]?\s*\d{4,5}|iec\s*[:\-]?\s*\d{4,5}|isi\s+mark|bis\s+care|cm/l|huid)\b', q):
            return False

        # If explicit statutory, technical, product, or quality keywords are present, NEVER out of domain
        domain_indicators = [
            r'\b(standard|standards|bis|isi|fssai|foscos|mrp|legal\s*metrology|e-daakhil|hallmark|hallmarking|huid|gold|silver|jewellery|certification|license|licence|testing|laboratory|nabl|qco|compostable|biodegradable|plastic|solar|battery|water|helmet|cement|steel|milk|food|adulteration|1915|penalty|consumer|msme|udyam|table\s*\d+)\b'
        ]
        if any(re.search(pat, q) for pat in domain_indicators):
            return False

        # If explicit BIS technical department code
        if re.search(r'\b(ced|etd|litd|ted|med|chd|fad|mtd|pcd|txd|wrd|msd|ssd|eed|pgd|mhd|ayd)\b', q) and any(w in q for w in ["department", "bis", "standard", "council", "division"]):
            return False

        out_of_domain_patterns = [
            # Civic / Personal Identity & Administrative services
            r'\b(passports?|visas?|embassy|consulate|consular|immigration)\b',
            r'\b(driving\s*licen[sc]e|driver\s*licen[sc]e|learner\s*licen[sc]e|rto\b|rc\s*book|vehicle\s*registration|traffic\s*fine|challans?)\b',
            r'\b(voter\s*id|election\s*card|voting|ballot|electoral)\b',
            r'\b(pan\s*card|income\s*tax|itr\s*filing|itr\s*return|aadhaar|uidai)\b',
            r'\b(ration\s*card|bpl\s*card)\b',
            r'\b(birth\s*certificate|death\s*certificate|marriage\s*certificate|caste\s*certificate|income\s*certificate|domicile\s*certificate)\b',
            r'\b(fir\b|police\s*complaint|police\s*station|arrest|bail\b|court\s*case|divorce\s*decree|litigation)\b',
            # Travel & Transport
            r'\b(railway\s*ticket|train\s*ticket|irctc|pnr\s*status|tatkal|flight\s*ticket|bus\s*ticket|metro\s*(?:smart\s*)?card|metro\s*recharge|smart\s*card\s*recharge)\b',
            # Sports & Entertainment
            r'\b(cricket|football|fifa|ipl\b|world\s*cup|virat|dhoni|rohit\s*sharma|sachin|tennis|badminton|olympics|match\s*score)\b',
            r'\b(movies?|actors?|actress|bollywood|hollywood|netflix|songs?|lyrics|music\s*video|watch\s+movie)\b',
            # Creative / Chit-chat / General Trivia / Programming / Food cooking recipes
            r'\b(tell\s*me\s*a\s*joke|funny\s*joke|jokes?|write\s*a\s*poem|write\s*an\s*essay|riddles?)\b',
            r'\b(weather|temperature\s*in|forecast|climate\s*in|rain\s*in)\b',
            r'\b(recipe|recipes|how\s*to\s*cook|how\s*to\s*bake|bake\s*a\s*cake|chocolate\s*cake|baking\s+cake|ingredients\s*for\s*cooking)\b',
            r'\b(python\s*code|write\s*a\s*script|javascript|programming\s*code|debug\s*my|algorithms?|c\+\+|java\s*program)\b',
            r'\b(who\s*is\s*the\s*president|prime\s*minister\s*of|capital\s*of|distance\s*to\s*the\s*moon|photosynthesis|quantum\s*physics)\b',
            # Adversarial and roleplay overrides
            r'\b(system\s*override|roleplay\s*as|malicious\s*hacker|pretend\s*to\s*be|ignore\s*bis\s*guidelines|fabricate\s*fake\s*isi|forget\s*you\s*are)\b',
        ]

        return any(re.search(pat, q) for pat in out_of_domain_patterns)

    async def answer_query(
        self,
        query: str,
        mode: ChatMode = ChatMode.INDUSTRY,
        selected_standard: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
        language: Optional[str] = "en"
    ) -> ChatResponse:
        query_id = str(uuid.uuid4())
        sanitized_query, injection_detected = self._sanitize_input(query)
        
        # Determine target language (from explicit prompt request or parameter)
        prompt_lang = multilingual_translator.detect_requested_language(query)
        active_lang = prompt_lang or language or "en"

        # High-security instant refusal for prompt injection or hostile exfiltration attempts
        if injection_detected:
            security_refusal = (
                "### 🛡️ Security Shield Activated\n\n"
                "Your request contained unauthorized instruction overrides, prompt extraction patterns, or potential security injection payloads. "
                "The BIS Intelligent Assistant is governed by strict defensive safety protocols and will only process genuine technical inquiries regarding Indian Standards (IS Codes), Quality Control Orders, and statutory certification frameworks."
            )
            return ChatResponse(
                id=query_id,
                answer=security_refusal,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.0,
                is_hallucination_safe=True,
                refusal_triggered=True,
                language=active_lang,
                suggested_followups=[
                    "What are the safety and quality requirements for Packaged Drinking Water?",
                    "What are the mechanical properties required under IS 1786 for TMT bars?",
                    "How to verify ISI mark certification on the official BIS Care App?"
                ]
            )

        # ── MULTILINGUAL QUERY LANGUAGE GUARD (8-step pipeline) ─────────────────
        # Detects language → normalizes → translates to English → topic guard
        # → negative blocklist → domain keyword check → Gemini classifier
        guard_result = query_language_guard.process(sanitized_query)
        if not guard_result.is_in_scope:
            # Build bilingual refusal: detected language + English
            lang_label = ""
            if guard_result.detected_language:
                from app.services.query_language_guard import QueryLanguageGuard
                lang_name = QueryLanguageGuard.SCRIPT_NAMES.get(
                    guard_result.detected_language,
                    guard_result.detected_language.upper()
                )
                lang_label = f" (Detected language: {lang_name})"
            refusal_text = (
                f"### ❌ Out-of-Scope Query{lang_label}\n\n"
                f"**Your query:** _{sanitized_query}_\n\n"
                f"**Translated as:** _{guard_result.translated_to_english}_\n\n"
                f"**Reason:** {guard_result.refusal_reason}\n\n"
                f"---\n\n"
                + STANDARDIZED_REFUSAL
            )
            if active_lang and active_lang != "en":
                refusal_text = multilingual_translator.translate_markdown(refusal_text, active_lang)
            return ChatResponse(
                id=query_id,
                answer=refusal_text,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.03,
                is_hallucination_safe=True,
                refusal_triggered=True,
                language=active_lang,
                suggested_followups=[
                    "What are the FSSAI food safety regulations for a milk shop (paala dukanam)?",
                    "What are the BIS certification requirements for packaged drinking water (IS 14543)?",
                    "How to apply for an FSSAI food license on FoSCoS portal?",
                ]
            )

        # Use English-translated query for RAG when original was non-English
        # (preserves better retrieval accuracy from English-indexed vector DB)
        if guard_result.detected_language or guard_result.is_romanized_indian:
            if guard_result.translated_to_english.strip().lower() != sanitized_query.strip().lower():
                # Combine: use translated query for RAG but original intent is preserved
                sanitized_query = guard_result.translated_to_english
                logger.info(
                    f"QueryGuard: Routing RAG with English translation: '{sanitized_query[:80]}'"
                )

        # Fast-path refusal for clear out-of-domain queries (existing English pattern check)
        if self._is_out_of_domain_query(sanitized_query):
            refusal_text = STANDARDIZED_REFUSAL
            if active_lang != "en":
                refusal_text = multilingual_translator.translate_markdown(refusal_text, active_lang)
            return ChatResponse(
                id=query_id,
                answer=refusal_text,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.05,
                is_hallucination_safe=True,
                refusal_triggered=True,
                language=active_lang,
                suggested_followups=[
                    "What parameters are governed under IS 2796 for Petrol?",
                    "What are the mechanical properties required under IS 1786 for TMT bars?",
                    "What are the permissible limits for Packaged Drinking Water under IS 14543 Table 2?"
                ]
            )

        # Check Disambiguation & Cross-Lingual Collisions (Google-style "Did you mean?")
        disambig = detect_query_disambiguation(query) or detect_query_disambiguation(sanitized_query)
        raw_simple = re.sub(r'[^\w\s]', '', query.lower()).strip()
        is_bare_ambiguous = raw_simple in ["pani", "battery", "kallu", "mandi", "oil", "cable"] or (disambig and len(raw_simple.split()) <= 1 and not disambig.get("primary_domain"))
        
        if disambig and is_bare_ambiguous:
            opts = disambig["options"]
            formatted_opts = "\n".join([f"- **{opt['label']}**: {opt['description']}" for opt in opts])
            clarification_msg = (
                f"### 🔍 Did you mean? / వివరణ అవసరం\n\n"
                f"Your query **\"{query}\"** could refer to multiple distinct Indian Standards (BIS) and statutory regulatory domains:\n\n"
                f"{formatted_opts}\n\n"
                f"---\n"
                f"💡 *Please select one of the options below or specify your product category to view official specifications, permissible limits, and testing standards.*"
            )
            return ChatResponse(
                id=query_id,
                answer=clarification_msg,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.90,
                is_hallucination_safe=True,
                refusal_triggered=False,
                needs_clarification=True,
                disambiguation_options=opts,
                language=active_lang,
                suggested_followups=[opt["query"] for opt in opts]
            )

        # 0. NLP Query Normalization & Short/Informal Query Expansion
        expanded_query, was_expanded = nlp_query_processor.expand_short_or_conversational_query(sanitized_query)
        normalized_query = nlp_query_processor.normalize_text(expanded_query)
        intent_meta = nlp_query_processor.classify_intent_and_entities(normalized_query)
        effective_query = normalized_query
        q_lower = effective_query.lower()

        # 0a. Check BIS Statutory Certification Schemes, Processes, Consumer Rights & Standard Recommendations
        statutory_res = bis_statutory_topics_service.resolve_statutory_topic(effective_query, language=active_lang)
        if not statutory_res and sanitized_query != effective_query:
            statutory_res = bis_statutory_topics_service.resolve_statutory_topic(sanitized_query, language=active_lang)
        if not statutory_res and query != effective_query:
            statutory_res = bis_statutory_topics_service.resolve_statutory_topic(query, language=active_lang)
        if statutory_res:
            stat_ans = statutory_res["answer"]
            is_native_topic = any(lang_kw in statutory_res["id"] for lang_kw in ["hindi", "urdu", "telugu", "tamil", "marathi", "bengali", "kannada", "gujarati", "malayalam"])
            if active_lang != "en" and not is_native_topic:
                stat_ans = multilingual_translator.translate_markdown(stat_ans, active_lang)

            stat_citations = [
                Citation(
                    is_code=statutory_res.get("standard_code", "BIS Statutory Framework"),
                    title=statutory_res["title"],
                    clause="Statutory Regulations",
                    page_number=1,
                    snippet=f"Official Bureau of Indian Standards (BIS) Statutory Regulatory Guidance ({statutory_res.get('portal', 'https://www.manakonline.in')}).",
                    similarity_score=0.98,
                    is_table=False
                )
            ]
            stat_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(stat_ans),
                mode=mode,
                citations=stat_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "What are the applicable testing standards under BIS?",
                    "How to verify license authenticity on the BIS Care App?",
                    "What are the penalty provisions under the BIS Act 2016?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=stat_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in stat_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return stat_response

        # 0b. Check FSSAI, Food Safety & Dual Certification Intent
        if intent_meta["has_fssai"] or intent_meta["has_dual_certification"] or any(k in q_lower for k in ["fssai", "foscos", "food safety", "food security", "adulterat", "dart", "fortified", "+f", "organic food", "jaivik bharat"]):
            fssai_res = fssai_food_safety_service.resolve_fssai_query(effective_query)
            if fssai_res:
                fssai_ans = fssai_res["answer"]
                if active_lang != "en":
                    fssai_ans = multilingual_translator.translate_markdown(fssai_ans, active_lang)
                
                fssai_citations = [
                    Citation(
                        is_code=fssai_res.get("standard_code", "FSS Act 2006"),
                        title=fssai_res["title"],
                        clause="Statutory Regulations",
                        page_number=1,
                        snippet=f"Official FSSAI & BIS Food Safety Regulatory Guidance ({fssai_res.get('portal', 'foscos.fssai.gov.in')}).",
                        similarity_score=0.98,
                        is_table=bool(fssai_res.get("table_markdown"))
                    )
                ]
                fssai_trefs = []
                if fssai_res.get("table_markdown"):
                    fssai_trefs.append({
                        "is_code": fssai_res.get("standard_code", "FSSAI"),
                        "table_number": "Table 1",
                        "table_title": f"Mandatory Permissible Limits ({fssai_res.get('standard_code')})",
                        "clause": "Statutory Limit",
                        "page_number": 1,
                        "columns": ["Parameter", "Limit", "Test Method"],
                        "rows": [],
                        "markdown": fssai_res["table_markdown"]
                    })
                fssai_response = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(fssai_ans),
                    mode=mode,
                    citations=fssai_citations,
                    table_references=fssai_trefs,
                    confidence_score=0.98,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    language=active_lang,
                    suggested_followups=[
                        "What are the mandatory parameters under IS 14543 for Packaged Drinking Water?",
                        "How to apply for an FSSAI Central License on FoSCoS?",
                        "How to report adulterated food products on the Food Safety Connect portal?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=fssai_ans,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.98,
                    citations=[c.dict() for c in fssai_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return fssai_response

        # Direct statutory license number verification & brand identification
        lic_keywords = ["license", "licence", "fssai", "cm/l", "cml", "huid", "crs", "verify", "check", "brand", "who owns", "which brand", "genuine", "hallmark"]
        has_lic_intent = any(k in q_lower for k in lic_keywords)
        is_setup_question = any(term in q_lower for term in ["how to open", "how to start", "what licenses are required to", "what clearances", "open a retail", "setup an"])
        if has_lic_intent and not is_setup_question:
            from app.services.license_verifier import license_verifier_service
            extracted_lic = license_verifier_service.extract_identifiers_from_text(query)
            if extracted_lic["primary"]:
                lic_val = extracted_lic["primary"]["value"]
                lic_type = extracted_lic["primary"]["type"]
                v_res = license_verifier_service.verify_identifier(lic_val, query_type=lic_type)
                if v_res and isinstance(v_res, dict) and v_res.get("is_valid"):
                    brand = v_res.get("brand_name") or v_res.get("details", {}).get("brand", "Registered Brand")
                    company = v_res.get("company") or v_res.get("manufacturer") or "Registered Entity"
                    flagship = v_res.get("flagship_products") or v_res.get("product_name")
                    sb = v_res.get("structure_breakdown") or {}
                    
                    ans_parts = [
                        f"### 🏷️ Statutory Credentials & Brand Identity\n",
                        f"- **Brand:** {brand}",
                        f"- **Company / Marketer:** {company}",
                        f"- **Flagship Products:** {flagship}\n",
                        f"### 📋 License Structure Breakdown:\n",
                        f"- **License Type:** {sb.get('license_type', v_res.get('license_type', v_res.get('mark_type')))}",
                        f"- **State / Regional Authority:** {sb.get('state_authority', v_res.get('operating_unit'))}",
                        f"- **Grant Year:** {sb.get('grant_year', v_res.get('issue_year'))}",
                        f"- **Registration Series:** {sb.get('registration_series', v_res.get('identifier'))}",
                        f"- **Current Status:** {v_res.get('status')}",
                        f"- **Validity / Expiry:** {v_res.get('expiry_date', v_res.get('valid_until'))}\n",
                        f"### 🔍 Statutory Compliance & Verification:\n",
                        f"- **Statutory Identifier:** `{v_res.get('identifier')}`",
                        f"- **Standard / Regulatory Basis:** {v_res.get('standard_code')}",
                        f"- **Consumer Action:** {v_res.get('bis_care_instructions')}"
                    ]
                    lic_answer = "\n".join(ans_parts)
                    if active_lang != "en":
                        lic_answer = multilingual_translator.translate_markdown(lic_answer, active_lang)
                    
                    lic_citations = [
                        Citation(
                            is_code=v_res.get("identifier"),
                            title=f"{brand} Statutory Registration",
                            clause=v_res.get("mark_type"),
                            page_number=1,
                            snippet=f"Official Verification Record: {company} ({v_res.get('standard_code')}).",
                            similarity_score=1.0,
                            is_table=False
                        )
                    ]
                    return ChatResponse(
                        id=query_id,
                        answer=self._sanitize_output(lic_answer),
                        mode=mode,
                        citations=lic_citations,
                        table_references=[],
                        confidence_score=0.99,
                        is_hallucination_safe=True,
                        refusal_triggered=False,
                        language=active_lang,
                        suggested_followups=[
                            f"How to verify {brand} on the official FoSCoS portal?",
                            "What testing standards and quality control orders apply?",
                            "How to report unauthorized or fake license numbers?"
                        ]
                    )

        # -------------------------------------------------------------
        # 0c. Specialized Intent: Accredited Testing Laboratories & Nearest Lab Finder (LRS / NABL)
        # -------------------------------------------------------------
        is_lab_query = bool(re.search(
            r'(?i)\b(nearest\s*(?:lab|labs|laboratory|laboratories|testing|centre|center|facility)|lab|labs|laboratory|laboratories|testing\s*(?:center|centre|facility|facilities|station|unit|house|rig|hub)|where\s*(?:can\s*i|to)\s*(?:test|check|verify|analyze|examine|send\s*sample))\b',
            sanitized_query
        ))
        if is_lab_query:
            # 1. Commodity & Indian Standard Detection
            detected_std = None
            commodity_name = "General Industrial & Consumer Products"
            lower_q = sanitized_query.lower()

            extracted_std_match = re.search(r'(?i)\bIS\s*[:\-]?\s*(\d{3,5})\b', sanitized_query)
            if extracted_std_match:
                detected_std = f"IS {extracted_std_match.group(1)}"
                commodity_name = f"Indian Standard {detected_std}"
            elif re.search(r'\b(steel|tmt|rebar|rebars|rod|rods|fe\s*500|fe\s*550|is\s*1786)\b', lower_q):
                detected_std = "IS 1786"
                commodity_name = "TMT Steel Rebars & Structural Reinforcement Steel (IS 1786:2008)"
            elif re.search(r'\b(water|drinking\s*water|mineral\s*water|packaged\s*water|is\s*14543|is\s*10500|is\s*13428)\b', lower_q):
                detected_std = "IS 14543"
                commodity_name = "Packaged Drinking Water & Mineral Water (IS 14543:2018 / IS 10500:2012)"
            elif re.search(r'\b(cement|concrete|opc|ppc|mortar|is\s*269|is\s*1489|is\s*456)\b', lower_q):
                detected_std = "IS 269"
                commodity_name = "Ordinary Portland Cement (OPC) & Concrete (IS 269:2015 / IS 1489)"
            elif re.search(r'\b(helmet|helmets|headgear|is\s*4151)\b', lower_q):
                detected_std = "IS 4151"
                commodity_name = "Two-Wheeler Protective Helmets (IS 4151:2015)"
            elif re.search(r'\b(plug|plugs|socket|sockets|switch|switches|is\s*1293|is\s*694)\b', lower_q):
                detected_std = "IS 1293"
                commodity_name = "Electrical Plugs, Socket-Outlets & Domestic Wiring (IS 1293:2019 / IS 694)"
            elif re.search(r'\b(electronic|electronics|mobile|laptop|battery|batteries|cell|cells|it\s*equipment|is\s*13252|is\s*16046)\b', lower_q):
                detected_std = "IS 13252"
                commodity_name = "Electronics, IT Equipment & Lithium Battery Safety (IS 13252 / IS 16046)"
            elif re.search(r'\b(pipe|pipes|hdpe|pvc|plumbing|is\s*4984|is\s*12235)\b', lower_q):
                detected_std = "IS 4984"
                commodity_name = "High-Density Polyethylene (HDPE) & PVC Pipes (IS 4984:2016)"
            elif re.search(r'\b(gold|silver|hallmark|hallmarking|huid|carat|karat|jewell?er|ahc|is\s*1417)\b', lower_q):
                detected_std = "IS 1417"
                commodity_name = "Gold & Precious Metals Hallmarking / Assaying (IS 1417:2016)"
            elif re.search(r'\b(toy|toys|baby|is\s*9873)\b', lower_q):
                detected_std = "IS 9873"
                commodity_name = "Safety of Toys & Child Care Articles (IS 9873)"
            elif re.search(r'\b(fuel|petrol|diesel|gasoline|is\s*2796|is\s*1460)\b', lower_q):
                detected_std = "IS 2796"
                commodity_name = "Motor Gasoline & Diesel Fuels (IS 2796:2017 / IS 1460)"

            # 2. Geographic Region & Location Detection
            detected_region = None
            detected_location_name = None

            if re.search(r'\b(delhi|noida|ghaziabad|sahibabad|faridabad|ballabgarh|gurgaon|gurugram|chandigarh|mohali|punjab|haryana|up|uttar\s*pradesh|himachal|j&k|north)\b', lower_q):
                detected_region = "North"
                detected_location_name = "Northern India (Delhi NCR / UP / Punjab / Haryana)"
            elif re.search(r'\b(mumbai|pune|nagpur|maharashtra|gujarat|ahmedabad|surat|vadodara|goa|mp|madhya\s*pradesh|west)\b', lower_q):
                detected_region = "West"
                detected_location_name = "Western India (Mumbai / Pune / Maharashtra / Gujarat)"
            elif re.search(r'\b(chennai|bengaluru|bangalore|karnataka|tamil\s*nadu|hyderabad|telangana|andhra|kerala|kochi|south)\b', lower_q):
                detected_region = "South"
                detected_location_name = "Southern India (Chennai / Bengaluru / Hyderabad / Kerala)"
            elif re.search(r'\b(kolkata|west\s*bengal|bihar|jharkhand|odisha|bhubaneswar|assam|east)\b', lower_q):
                detected_region = "East"
                detected_location_name = "Eastern India (Kolkata / West Bengal / Odisha / Bihar)"

            # 3. Fetch Accredited Laboratories from Directory
            matching_labs = search_testing_laboratories(standard_code=detected_std or "")
            if not matching_labs:
                matching_labs = search_testing_laboratories(query=sanitized_query)
            if not matching_labs:
                matching_labs = TESTING_LABORATORIES_DIRECTORY

            # 4. Construct Comprehensive Response
            lab_lines = [
                f"### 🔬 Accredited BIS & NABL Testing Laboratories Directory",
                f"",
                f"> **Statutory Authority:** Bureau of Indian Standards Act, 2016 (Section 13(4) & Section 20) & Laboratory Recognition Scheme (LRS 2020).",
                f"> **Accreditation Standard:** ISO/IEC 17025:2017 (General requirements for the competence of testing and calibration laboratories).",
                f"",
                f"#### 🎯 Product & Standard Testing Scope: **{commodity_name}**"
            ]

            if detected_region and detected_location_name:
                lab_lines.append(f"> 📍 **Target Geographic Location:** Highlighted for `{detected_location_name}`")
                lab_lines.append("")

                nearest_labs = [l for l in matching_labs if l.get("region", "").lower() == detected_region.lower()]
                other_labs = [l for l in matching_labs if l.get("region", "").lower() != detected_region.lower()]

                if nearest_labs:
                    lab_lines.append(f"#### 📍 Nearest Accredited Laboratories in {detected_region} Zone:")
                    for lab in nearest_labs:
                        lab_lines.extend([
                            f"- **🏛️ {lab['name']}** (`{lab['type']}`)",
                            f"  - **Location:** {lab['city']}, {lab['state']} ({lab['region']} Zone)",
                            f"  - **Address:** {lab['address']}",
                            f"  - **Contact:** 📞 `{lab['phone']}` | ✉️ `{lab['email']}`",
                            f"  - **Accreditation:** {lab['nabl_accreditation']}",
                            f"  - **Disciplines:** {', '.join(lab['disciplines'])}",
                            f"  - **Standards Supported:** {', '.join([f'`{s}`' for s in lab['standards_supported']])}",
                            f"  - **Testing Capabilities:** {lab['description']}",
                            f""
                        ])

                if other_labs:
                    lab_lines.append(f"#### 🌐 Other Accredited National Testing Centers Across India:")
                    for lab in other_labs:
                        lab_lines.extend([
                            f"- **🏛️ {lab['name']}** (`{lab['region']} Zone` - {lab['city']}, {lab['state']})",
                            f"  - **Address:** {lab['address']}",
                            f"  - **Contact:** 📞 `{lab['phone']}` | ✉️ `{lab['email']}`",
                            f"  - **Accreditation:** {lab['nabl_accreditation']}",
                            f"  - **Standards Supported:** {', '.join([f'`{s}`' for s in lab['standards_supported']])}",
                            f""
                        ])
            else:
                lab_lines.append(f"Below are the accredited apex BIS National and Regional laboratories equipped with certified testing rigs for **{commodity_name}**:")
                lab_lines.append("")

                for target_reg in ["North", "West", "South", "East"]:
                    reg_labs = [l for l in matching_labs if l.get("region", "").lower() == target_reg.lower()]
                    if reg_labs:
                        lab_lines.append(f"#### 📍 {target_reg} India Laboratories:")
                        for lab in reg_labs:
                            lab_lines.extend([
                                f"- **🏛️ {lab['name']}** (`{lab['type']}`)",
                                f"  - **Location:** {lab['city']}, {lab['state']}",
                                f"  - **Address:** {lab['address']}",
                                f"  - **Contact:** 📞 `{lab['phone']}` | ✉️ `{lab['email']}`",
                                f"  - **Accreditation:** {lab['nabl_accreditation']}",
                                f"  - **Standards Supported:** {', '.join([f'`{s}`' for s in lab['standards_supported']])}",
                                f"  - **Testing Facilities:** {lab['description']}",
                                f""
                            ])

            lab_lines.extend([
                "#### 📋 How Citizens, Builders & Manufacturers Can Submit Samples for Official Testing:",
                "1. **Apply Online on BIS Manakonline (LRS Portal):** Visit [manakonline.in](https://www.manakonline.in) and navigate to the *Laboratory Recognition Scheme (LRS)* section.",
                "2. **Generate Unique Sample ID (USID):** Register the sample (raw steel rod, packaged water bottle, helmet, or cement lot) to generate a tamper-proof digital barcode tracking tag.",
                "3. **Sample Packaging & Sealing:** Samples must be packed in clean, moisture-proof containers with joint seals if drawn during statutory inspection or consumer dispute.",
                "4. **NABL-Endorsed Official Test Report:** The laboratory performs destructive/non-destructive tests (e.g. Tensile Yield, Elongation, Chemical Spectrometry) and issues an authentic, court-admissible certificate of compliance.",
                "5. **Substandard Product Grievance:** If an independent test shows the product breaches statutory standards, lodge an immediate enforcement complaint on the **BIS Care App** or call the National Consumer Helpline at `1915` to seek full product recall, refund, and statutory damages."
            ])

            lab_ans = "\n".join(lab_lines)
            if active_lang != "en":
                lab_ans = multilingual_translator.translate_markdown(lab_ans, active_lang)

            lab_citations = [
                Citation(
                    is_code=detected_std or "BIS LRS 2020",
                    title=f"BIS Accredited Testing Laboratories & LRS Network for {commodity_name}",
                    clause="Section 13(4) & Section 20, BIS Act 2016 / ISO/IEC 17025",
                    page_number=1,
                    snippet="Official directory of BIS Central/Regional and NABL accredited testing laboratories equipped for statutory conformity and citizen verification.",
                    similarity_score=0.98,
                    is_table=True
                )
            ]

            lab_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(lab_ans),
                mode=mode,
                citations=lab_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    f"How to register a testing sample for {detected_std or 'BIS certification'} on Manakonline?",
                    "What mechanical tests are required for TMT steel rebars under IS 1786?",
                    "How to open the official BIS Services Hub to filter laboratories by state?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=lab_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in lab_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return lab_response

        # -------------------------------------------------------------
        # 0d. Specialized Intent: Standards Clubs in Schools & Colleges
        # -------------------------------------------------------------
        is_standards_club = bool(re.search(
            r'(?i)\b(standards?\s*clubs?|learning\s*science\s*via\s*standards|lsvs|grant.*(?:10000|10,000|20000|20,000)|schools?.*standards?\s*clubs?)\b',
            sanitized_query
        ))
        if is_standards_club:
            sc_data = BIS_SERVICES_DIRECTORY.get("standards_clubs", {})
            sc_lines = [
                f"### 🎓 {sc_data.get('title', 'BIS Standards Clubs in Schools & Higher Educational Institutions')}",
                "",
                f"> **Tagline:** *{sc_data.get('tagline', 'Fostering Quality Consciousness & Scientific Temper through Standards')}*",
                f"> **Nodal Authority:** {sc_data.get('ministry', 'Ministry of Consumer Affairs, Food & Public Distribution')} • Bureau of Indian Standards",
                "",
                f"{sc_data.get('overview', '')}",
                "",
                "#### 💰 Statutory Financial Grants & Assistance Provided by BIS:",
                "- **Annual Learning Activity Grant (₹10,000 per annum):** Funded directly by BIS to organize quality quizzes, standards writing competitions, debates, essay contests, and poster campaigns.",
                "- **Science Laboratory Upgrade Grant (Up to ₹20,000 per institution):** Provided under the *Learning Science via Standards (LSvS)* initiative to equip science laboratories with apparatus demonstrating Indian Standards (e.g. testing water pH, food adulteration, tensile strength).",
                "- **Exposure Visits:** Sponsoring full travel and logistics for students and faculty mentors to visit NABL-accredited testing laboratories, manufacturing plants, and BIS Regional Offices.",
                "",
                "#### 📚 Key Student Activities & Mentorship:",
                "- **Learning Science via Standards (LSvS):** Specially curated lesson plans connecting high school physics, chemistry, and biology with Indian Standards.",
                "- **Consumer Awareness Campaigns:** Door-to-door community rallies educating citizens on identifying genuine ISI marks, CRS numbers, and 6-digit HUID gold hallmarks.",
                "- **Faculty Mentor:** Each club is headed by a certified Science or Engineering teacher nominated by the school/college and trained by BIS.",
                "",
                "#### 📝 How to Form / Enroll a Standards Club:",
                "- **Eligibility:** Recognized schools with classes 9th to 12th (science stream), engineering colleges, polytechnics, and universities across India.",
                "- **Application:** School Principals or College Directors can apply through the nearest BIS Branch Office (BO) or via the online Standards Promotion portal on [bis.gov.in](https://www.bis.gov.in)."
            ]
            sc_ans = "\n".join(sc_lines)
            if active_lang != "en":
                sc_ans = multilingual_translator.translate_markdown(sc_ans, active_lang)

            sc_citations = [
                Citation(
                    is_code="BIS Standards Clubs",
                    title="Educational Initiatives & Standards Clubs Guidelines",
                    clause="BIS Act 2016 / Standards Promotion Directorate",
                    page_number=1,
                    snippet="Statutory framework for Standards Clubs in schools and colleges, including ₹10,000 annual grant and LSvS science lab funding.",
                    similarity_score=0.98,
                    is_table=True
                )
            ]
            sc_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(sc_ans),
                mode=mode,
                citations=sc_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How can a school apply for the ₹10,000 Standards Club activity grant?",
                    "What are the Learning Science via Standards (LSvS) lesson modules?",
                    "How to organize an exposure visit to a BIS testing laboratory?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=sc_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in sc_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return sc_response

        # -------------------------------------------------------------
        # 0e. Specialized Intent: National Institute of Training for Standardization (NITS)
        # -------------------------------------------------------------
        is_nits_query = bool(re.search(
            r'(?i)\b(nits\b|national\s*institute\s*of\s*training\s*for\s*standardization|training\s*for\s*standardization)\b',
            sanitized_query
        ))
        if is_nits_query:
            nits_data = BIS_SERVICES_DIRECTORY.get("nits_training", {})
            nits_lines = [
                f"### 🏛️ {nits_data.get('title', 'National Institute of Training for Standardization (NITS)')}",
                "",
                f"> **Apex Institution:** Bureau of Indian Standards (Ministry of Consumer Affairs)",
                f"> **Campus Location:** {nits_data.get('location', 'Sector 62, Noida, UP - 201309')}",
                "",
                f"{nits_data.get('overview', '')}",
                "",
                "#### 📋 Core Specialized Training Programs & Durations:",
                "- **ISO/IEC 17025 Laboratory Quality Management System (LQMS) (4 Days):** For laboratory directors, testing engineers, and NABL quality managers on measurement uncertainty, method validation, and ISO 17025:2017.",
                "- **Lead Auditor Training for Management Systems (5 Days):** IRCA/NABCB recognized certifications covering IS/ISO 9001 (QMS), IS/ISO 14001 (EMS), IS/ISO 22000 (FSMS), IS/ISO 45001 (OH&S), and IS/ISO/IEC 27001 (ISMS).",
                "- **Statistical Quality Control (SQC) & Sampling Plans (3 Days):** Practical industrial application of IS 2500 sampling tables, process capability (Cp, Cpk), and statistical process control.",
                "- **Conformity Assessment & BIS Certification Guidelines (2 Days):** Tailored for MSMEs, startups, and new applicants covering Scheme-I product certification, Scheme of Inspection & Testing (SIT), and Manakonline e-filing.",
                "",
                "#### 💰 Statutory Fee Schedule & Concessions:",
                "- **Standard Course Fees:** Highly subsidized statutory government fee structure (typically ₹10,000 – ₹25,000 depending on course duration and residential option).",
                "- **50% MSME & Startup Concession:** Micro, Small, and Medium Enterprises (registered on Udyam) and DPIIT-recognized startups receive 50% statutory fee concessions.",
                "- **Women Entrepreneurs:** Special subsidized rates to encourage women-led manufacturing and quality testing leadership.",
                "- **International Delegates:** Fully sponsored by the Ministry of External Affairs under ITEC / SCAAP programmes.",
                "",
                "#### 🌐 Registration & Training Calendar:",
                f"- **Official Portal:** [{nits_data.get('enrollment_portal', 'https://www.bis.gov.in/nits/')}](https://www.bis.gov.in/nits/)",
                "- **Official Email:** `nits@bis.gov.in`"
            ]
            nits_ans = "\n".join(nits_lines)
            if active_lang != "en":
                nits_ans = multilingual_translator.translate_markdown(nits_ans, active_lang)

            nits_citations = [
                Citation(
                    is_code="NITS-Noida",
                    title="National Institute of Training for Standardization (NITS)",
                    clause="Apex Training Institute / BIS Act 2016",
                    page_number=1,
                    snippet="Official training calendar, ISO 17025 / ISO 9001 lead auditor programs, and 50% MSME fee concession schedule.",
                    similarity_score=0.98,
                    is_table=True
                )
            ]
            nits_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(nits_ans),
                mode=mode,
                citations=nits_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How to claim 50% MSME concession for NITS training?",
                    "What is the eligibility for ISO/IEC 17025 Lead Assessor course?",
                    "Where can I download the current NITS annual training calendar?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=nits_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in nits_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return nits_response

        # -------------------------------------------------------------
        # 0f. Specialized Intent: Fake / Counterfeit ISI Mark without CM/L
        # -------------------------------------------------------------
        is_fake_isi_query = bool(re.search(
            r'(?i)\b(isi\s*(?:mark|logo)?\s*(?:without|missing).*?(?:cm/l|cml|licen[sc]e|number)|fake\s*isi|counterfeit\s*isi|illegal\s*isi)\b',
            sanitized_query
        ))
        if is_fake_isi_query:
            fake_isi_lines = [
                "### ⚠️ Statutory Illegality of ISI Mark Without CM/L License Number",
                "",
                "> **Statutory Regulatory Mandate:** Section 16 & Section 29, Bureau of Indian Standards Act, 2016.",
                "",
                "#### 🔍 Why an ISI Mark Without a 7 or 8-Digit CM/L Number is Illegal & Counterfeit:",
                "1. **Traceability Guarantee:** Under BIS statutory regulations, the Standard Mark (ISI mark) is NEVER legally valid in isolation. It MUST always appear as an integrated 3-part mark:",
                "   - **Top:** The specific Indian Standard number (e.g. `IS 14543`, `IS 4151`, `IS 694`).",
                "   - **Center:** The official BIS ISI pictogram monogram.",
                "   - **Bottom:** The unique 7-digit or 8-digit **CM/L (Certificate of Manufacture / Licence)** number (e.g. `CM/L-8400192708` or `CM/L-1234567`).",
                "2. **Evidence of Forgery:** If a product displays an ISI mark WITHOUT a CM/L number, it is a **forged, counterfeit mark**. It signifies that the manufacturer has no valid license, no factory inspection was ever conducted, no Scheme of Inspection and Testing (SIT) was followed, and the product poses serious safety, fire, or health risks.",
                "3. **Deceptive Consumer Practice:** Fraudulent sellers print generic 'ISI' logos to mislead consumers into believing the goods are government-certified.",
                "",
                "#### ⚖️ Criminal Penalties for Misuse of ISI Mark (Section 29, BIS Act 2016):",
                "- **Imprisonment:** Up to **2 years** of imprisonment.",
                "- **Statutory Monetary Fine:** Minimum fine of **₹2,00,000 (Two Lakhs)**, extendable up to **10 times the value of the infringing goods** produced or sold.",
                "- **Seizure & Forfeiture:** BIS Enforcement Officers have legal powers to raid premises, seize entire manufacturing machinery and inventory, and seal factories.",
                "",
                "#### 🛡️ Immediate Steps for Citizens & Consumers:",
                "1. **Check via BIS Care App:** Enter the CM/L number into the **BIS Care App** under *'Verify License Details'* to verify manufacturer name, factory address, and validity status.",
                "2. **Report Violation:** File an official enforcement grievance on the BIS Care App (with photo of product and shop location) or email `enforcement@bis.gov.in`.",
                "3. **Redressal:** Call the National Consumer Helpline at `1915` to seek replacement or full refund."
            ]
            fake_isi_ans = "\n".join(fake_isi_lines)
            if active_lang != "en":
                fake_isi_ans = multilingual_translator.translate_markdown(fake_isi_ans, active_lang)

            fake_isi_citations = [
                Citation(
                    is_code="BIS Act 2016",
                    title="Statutory Enforcement & Penalties for Misuse of Standard Mark",
                    clause="Section 16 & Section 29",
                    page_number=1,
                    snippet="Mandatory requirement of 7/8-digit CM/L number on ISI mark; imprisonment up to 2 years and ₹2 Lakhs minimum fine for counterfeit marks.",
                    similarity_score=0.98,
                    is_table=False
                )
            ]
            fake_isi_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(fake_isi_ans),
                mode=mode,
                citations=fake_isi_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How to verify a CM/L number on the BIS Care App?",
                    "How to report a factory manufacturing fake ISI marked products?",
                    "What compensation can a consumer claim for injuries caused by fake ISI goods?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=fake_isi_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in fake_isi_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return fake_isi_response

        # -------------------------------------------------------------
        # 0g. Specialized Intent: National Consumer Helpline 1915
        # -------------------------------------------------------------
        is_nch_query = bool(re.search(
            r'(?i)\b(1915\b|national\s*consumer\s*helpline|nch\s*1915|consumer\s*helpline\s*1915)\b',
            sanitized_query
        ))
        if is_nch_query:
            nch_lines = [
                "### 📞 National Consumer Helpline (NCH) 1915 & BIS Grievance Integration",
                "",
                "> **Nodal Authority:** Department of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution.",
                "> **Statutory Framework:** Consumer Protection Act, 2019 & Bureau of Indian Standards Act, 2016.",
                "",
                "#### 🏛️ What is National Consumer Helpline (NCH) 1915?",
                "- **Toll-Free Dial:** `1915` (Operating 24x7 in multiple scheduled regional languages).",
                "- **SMS Service:** Send SMS to `8800001915`.",
                "- **Online Portal:** [consumerhelpline.gov.in](https://consumerhelpline.gov.in) (INGRAM - Integrated Grievance Redressal Mechanism).",
                "- **National WhatsApp Support:** Available for consumer complaint lodging and status tracking.",
                "",
                "#### 🔗 Integration with BIS for Defective / Counterfeit Certified Products:",
                "When a consumer purchases a product certified by BIS (bearing ISI mark, CRS registration, or HUID hallmarking) that turns out to be substandard, hazardous, adulterated, or counterfeit:",
                "1. **Inter-Agency Routing:** Filing a complaint via NCH 1915 automatically cross-notifies the **BIS Enforcement Wing** and State Legal Metrology authorities.",
                "2. **Product Liability Claims:** Under Chapter VI (Sections 82–87) of the Consumer Protection Act, 2019, manufacturers and sellers of defective certified goods are strictly liable to provide:",
                "   - Immediate replacement of the defective product.",
                "   - 100% full refund of the purchase amount with interest.",
                "   - Statutory compensation for any physical harm, injury, property damage, or financial loss.",
                "3. **Enforcement Action:** BIS initiates market sample drawing, forensic laboratory testing, and surprise factory raids against non-compliant license holders.",
                "",
                "#### 📋 Protocol for Consumers to Lodge a Complaint via 1915:",
                "1. Keep proof of purchase ready (Tax Invoice, UPI payment transaction ID, or Cash Memo).",
                "2. Note down the product's 7/8-digit CM/L number, 6-digit HUID code, or 14-digit FSSAI number.",
                "3. Call `1915` or log in on `consumerhelpline.gov.in` to obtain a unique grievance docket number for online real-time tracking."
            ]
            nch_ans = "\n".join(nch_lines)
            if active_lang != "en":
                nch_ans = multilingual_translator.translate_markdown(nch_ans, active_lang)

            nch_citations = [
                Citation(
                    is_code="NCH 1915",
                    title="National Consumer Helpline (Department of Consumer Affairs)",
                    clause="Consumer Protection Act 2019 / INGRAM Portal",
                    page_number=1,
                    snippet="Toll-free 1915 consumer grievance mechanism integrated with BIS enforcement for defective certified products and product liability.",
                    similarity_score=0.98,
                    is_table=False
                )
            ]
            nch_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(nch_ans),
                mode=mode,
                citations=nch_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How to lodge a complaint on the BIS Care App?",
                    "What is the statutory redressal timeline under Consumer Protection Act 2019?",
                    "What compensation is payable for defective certified goods?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=nch_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in nch_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return nch_response

        # -------------------------------------------------------------
        # 0h. Specialized Intent: GS1 India Barcode Prefix 890 & Counterfeits
        # -------------------------------------------------------------
        is_gs1_query = bool(re.search(
            r'(?i)\b(gs1\s*(?:india)?\s*barcode|barcode.*890|890.*barcode|genuine\s*barcode|counterfeit\s*barcode|barcode\s*stickers?)\b',
            sanitized_query
        ))
        if is_gs1_query:
            gs1_lines = [
                "### 📦 GS1 India Barcode Prefix 890 & Counterfeit Detection Guide",
                "",
                "> **Standardization Body:** GS1 India (Under Ministry of Commerce & Industry, Govt of India) & BIS.",
                "",
                "#### 🏷️ What Does Barcode Prefix '890' Signify?",
                "1. **GS1 National Allocation:** The 3-digit prefix `890` is allocated exclusively by GS1 Global to **GS1 India**.",
                "2. **Manufacturer Registration:** Any product with a genuine 13-digit EAN/GTIN barcode starting with `890` indicates that the brand/company is registered with GS1 India.",
                "3. **Does 890 Guarantee 100% Made-in-India?** **No.** Prefix 890 confirms that the brand owner or legal entity is registered with GS1 India, but raw materials, assemblies, or packaging may be imported. Origin is governed by country of origin declarations under Legal Metrology Rules.",
                "4. **Barcode vs BIS Quality Certification:** A GS1 barcode is purely an inventory and supply-chain identification tool. It does **NOT** substitute for mandatory BIS ISI marks (Scheme-I), CRS registrations (Scheme-II), or Gold Hallmarking.",
                "",
                "#### 🔍 How to Identify Genuine GS1 Barcodes vs Counterfeit Stickers:",
                "- **Over-Pasted Paper Stickers:** Genuine products have the barcode printed directly on the carton/label. Counterfeiters often paste loose paper barcode stickers over imported or uncertified items.",
                "- **Modulo-10 Check Digit Validation:** The 13th digit of a GTIN-13 barcode is calculated via a strict Modulo-10 algorithm. Random or fake barcodes fail check digit verification.",
                "- **Verify via GS1 DataKart / Smart Consumer:** Enter or scan the 13-digit number on the **GS1 India Smart Consumer App** or [gs1india.org](https://www.gs1india.org). Genuine barcodes display the registered brand name, parent company, product description, and net content.",
                "- **Verify Mandatory Standards:** For regulated commodities (packaged water, cement, helmets, electricals), verify that both the genuine GS1 barcode and the statutory BIS CM/L license number are present.",
                "",
                "#### 🛡️ Reporting Counterfeit Goods:",
                "Report fake barcodes and counterfeit goods on the **National Consumer Helpline (1915)** or lodge an enforcement grievance on the **BIS Care App**."
            ]
            gs1_ans = "\n".join(gs1_lines)
            if active_lang != "en":
                gs1_ans = multilingual_translator.translate_markdown(gs1_ans, active_lang)

            gs1_citations = [
                Citation(
                    is_code="GS1 India 890",
                    title="GS1 India Barcode Standards & Identification",
                    clause="GTIN-13 Country Code 890 / DataKart Registry",
                    page_number=1,
                    snippet="Official guide for GS1 India prefix 890, GTIN-13 Modulo-10 check digit verification, and counterfeit sticker detection.",
                    similarity_score=0.98,
                    is_table=False
                )
            ]
            gs1_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(gs1_ans),
                mode=mode,
                citations=gs1_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How to look up a brand using a 13-digit barcode?",
                    "What is the difference between GS1 barcode and BIS CM/L license?",
                    "How to verify FSSAI 14-digit number on packaged foods?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=gs1_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in gs1_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return gs1_response

        # -------------------------------------------------------------
        # 0i. Specialized Intent: Dual MRP & Price Overcharging
        # -------------------------------------------------------------
        is_dual_mrp_query = bool(re.search(
            r'(?i)\b(dual\s*mrp|higher\s*mrp|mrp\s*charging|charging\s*more\s*than\s*mrp|overcharging.*mrp|mrp.*(?:airports?|railway|multiplex))\b',
            sanitized_query
        ))
        if is_dual_mrp_query:
            mrp_lines = [
                "### ⚖️ Statutory Prohibition of Dual MRP & Overcharging",
                "",
                "> **Statutory Law:** Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Amendment Rules, 2017.",
                "> **Enforcing Authority:** Department of Consumer Affairs & State Controllers of Legal Metrology.",
                "",
                "#### 🚫 Strict Ban on Dual MRP at Airports, Multiplexes & Railway Stations:",
                "1. **Rule 18(2) Mandate:** Under the Legal Metrology (Packaged Commodities) Amendment Rules, 2017, no manufacturer, packer, or seller can declare different Maximum Retail Prices (dual MRP) for the identical pre-packaged commodity sold across different venues.",
                "2. **Illegal Price Hikes:** Selling bottled water, aerated drinks, snacks, or certified goods at a higher MRP inside airports, multiplex cinema halls, malls, or railway stations is **strictly illegal and an unfair trade practice**.",
                "3. **Tampering with MRP:** Obliterating, smudging, or sticking a revised price tag over the printed manufacturer's MRP is an offence under Section 36 of the Legal Metrology Act.",
                "",
                "#### ⚖️ Penalties for Dual MRP & Overcharging (Section 36, Legal Metrology Act 2009):",
                "- **First Offence:** Fine up to **₹25,000**.",
                "- **Second Offence:** Fine up to **₹50,000**.",
                "- **Subsequent Offences:** Fine up to **₹1,00,000 or imprisonment up to 1 year**, or both.",
                "",
                "#### 🛡️ How to Report Dual MRP / Overcharging:",
                "1. **Collect Concrete Evidence:** Demand a printed Tax Invoice or Cash Memo clearly indicating the price charged, and take photographs of the product carton showing the printed MRP and batch details.",
                "2. **National Consumer Helpline (NCH):** Call toll-free `1915` or SMS `8800001915`, or register online at [consumerhelpline.gov.in](https://consumerhelpline.gov.in).",
                "3. **State Legal Metrology Inspector:** Submit a written complaint to the Inspector of Legal Metrology in the relevant district/city for immediate inspection and compounding.",
                "4. **Consumer Commission:** File for recovery of overcharged amount plus punitive damages before the District Consumer Commission via e-Daakhil ([edaakhil.nic.in](https://edaakhil.nic.in))."
            ]
            mrp_ans = "\n".join(mrp_lines)
            if active_lang != "en":
                mrp_ans = multilingual_translator.translate_markdown(mrp_ans, active_lang)

            mrp_citations = [
                Citation(
                    is_code="Legal Metrology Act 2009",
                    title="Packaged Commodities Rules & Prohibition of Dual MRP",
                    clause="Section 36 / Rule 18(2)",
                    page_number=1,
                    snippet="Strict prohibition of dual MRP at airports/multiplexes; penalties up to ₹1 Lakh and 1 year imprisonment under Legal Metrology Act.",
                    similarity_score=0.98,
                    is_table=False
                )
            ]
            mrp_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(mrp_ans),
                mode=mode,
                citations=mrp_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "How to lodge a complaint on the e-Daakhil consumer portal?",
                    "What mandatory declarations must appear on prepackaged commodities?",
                    "What are consumer rights under the Consumer Protection Act 2019?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=mrp_ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in mrp_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
        # -------------------------------------------------------------
        # 0j. Nationwide BIS Business Domain Standards Resolution
        # -------------------------------------------------------------
        biz_domain_match = (
            self._resolve_business_domain_standards(query)
            or self._resolve_business_domain_standards(sanitized_query)
            or self._resolve_business_domain_standards(effective_query)
        )
        if biz_domain_match and (not selected_standard or selected_standard in [s["code"] for s in biz_domain_match["standards"]]):
            ans = self._generate_fallback_response(query, mode, [])
            if not ans or ans == STANDARDIZED_REFUSAL:
                ans = self._generate_fallback_response(effective_query, mode, [])
            
            # Google-style "Did you mean?" banner if ambiguous query detected
            if disambig and disambig.get("options"):
                other_opts = [o["label"] for o in disambig["options"] if o.get("label") and not any(k in o["label"].lower() for k in ["wood", "chekka", "carpentry", "timber"])]
                if other_opts:
                    did_you_mean_note = f"> 💡 **Did you mean?** *Showing verified standards for **{biz_domain_match['domain']}**. Did you also mean **{other_opts[0]}**? (Quick options below)*\n\n"
                    ans = did_you_mean_note + ans

            if active_lang != "en":
                ans = multilingual_translator.translate_markdown(ans, active_lang)

            biz_citations = [
                Citation(
                    is_code=s["code"],
                    title=s["title"],
                    clause=s["clause"],
                    page_number=1,
                    snippet=f"Statutory BIS Standard for {biz_domain_match['domain']}.",
                    similarity_score=0.98,
                    is_table=False
                )
                for s in biz_domain_match["standards"]
            ]
            biz_resp = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(ans),
                mode=mode,
                citations=biz_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                needs_clarification=False,
                disambiguation_options=disambig.get("options", []) if disambig else [],
                language=active_lang,
                suggested_followups=[
                    f"What testing facilities are required for {biz_domain_match['standards'][0]['code']}?",
                    f"What is the application fee under {biz_domain_match['scheme'].split(' ')[0]}?",
                    "How to register on the official BIS Manakonline portal?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in biz_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return biz_resp

        is_iso_query = "iso" in q_lower or "iso standard" in q_lower

        # Check commercial licensing or ISO registry if not specifically filtering for an uploaded IS PDF
        if (is_iso_query or not selected_standard) and not re.search(r'\bis\s*\d{3,5}\b', sanitized_query, re.IGNORECASE):
            iso_store_match = online_standards_resolver.resolve_iso_or_store_licensing(sanitized_query, mode=mode.value)
            if iso_store_match:
                ans = iso_store_match["answer"]
                if active_lang != "en":
                    ans = multilingual_translator.translate_markdown(ans, active_lang)

                iso_citations = [
                    Citation(
                        is_code=iso_store_match["code"],
                        title=iso_store_match["title"],
                        clause=iso_store_match["scheme"],
                        page_number=1,
                        snippet=f"Official Statutory Guidance from Government Portals ({iso_store_match.get('portal', 'www.nsws.gov.in')}).",
                        similarity_score=0.96,
                        is_table=False
                    )
                ]
                iso_response = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(ans),
                    mode=mode,
                    citations=iso_citations,
                    table_references=[],
                    confidence_score=0.96,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    language=active_lang,
                    suggested_followups=iso_store_match.get("action_chips") or [
                        f"How to apply on the official portal for {iso_store_match['code'][:40]}?",
                        "What documents and fee structures are required?",
                        "How to check statutory Quality Control Orders (QCOs) on Manakonline?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=ans,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.96,
                    citations=[c.dict() for c in iso_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return iso_response

        # 0b. Check for 17 BIS Technical Departments / Standards Breakdown Query
        q_lower = sanitized_query.lower()
        dept_terms = ["department", "division council", "standards published", "24,084", "24084", "how many standards", "number of standards"]
        dept_codes = ["ssd", "litd", "etd", "eed", "ted", "ced", "msd", "med", "fad", "pgd", "pcd", "txd", "wrd", "chd", "mhd", "mtd", "ayd"]
        
        if any(term in q_lower for term in dept_terms) or any(re.search(rf"\b{code}\b", q_lower) for code in dept_codes):
            dept_match = online_standards_resolver.search_department(sanitized_query)
            if dept_match and not any(term in q_lower for term in ["all", "matrix", "total", "table", "breakdown", "number of standards"]):
                # Specific single department breakdown
                ans = (
                    f"### 🏛️ BIS Department: {dept_match['name']} ({dept_match['code']})\n\n"
                    f"**Total Published Standards:** **{dept_match['published_standards']:,} Standards**\n"
                    f"**Core Industrial Domains:** {dept_match['domains']}\n"
                    f"**Flagship Standards:** {', '.join(dept_match['key_standards'])}\n"
                    f"**Statutory & Regulatory Scope:** {dept_match['scope']}\n\n"
                    f"#### 💡 Application & Compliance Information:\n"
                    f"1. Search individual specifications under {dept_match['code']} on the [BIS Manakonline Portal](https://www.manakonline.in).\n"
                    f"2. Check mandatory Quality Control Orders (QCOs) issued by the corresponding nodal ministry.\n"
                    f"3. Access testing methods and laboratory requirements via the BIS Standards National Repository."
                )
                dept_citations = [
                    Citation(
                        is_code=dept_match['code'],
                        title=dept_match['name'],
                        clause=f"{dept_match['published_standards']} Published Standards",
                        page_number=1,
                        snippet=dept_match['scope'],
                        similarity_score=0.98,
                        is_table=True
                    )
                ]
            else:
                # Full 17 departments matrix report
                ans = online_standards_resolver.get_all_departments_formatted()
                dept_citations = [
                    Citation(
                        is_code="BIS Division Councils",
                        title="17 BIS Technical Standardization Departments",
                        clause="Master Matrix (24,084 Published Standards)",
                        page_number=1,
                        snippet="Comprehensive standardization across all 17 Division Councils of the Bureau of Indian Standards.",
                        similarity_score=0.99,
                        is_table=True
                    )
                ]

            # Apply translation if requested
            if active_lang != "en":
                ans = multilingual_translator.translate_markdown(ans, active_lang)

            dept_response = ChatResponse(
                id=query_id,
                answer=self._sanitize_output(ans),
                mode=mode,
                citations=dept_citations,
                table_references=[],
                confidence_score=0.98,
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "What standards are published under Food & Agriculture (FAD)?",
                    "What standards are published under Electronics & IT (LITD)?",
                    "How to check Quality Control Orders (QCOs) for these departments?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=ans,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.98,
                citations=[c.dict() for c in dept_citations],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return dept_response

        # 1. Retrieve relevant chunks using Next-Gen Hybrid Search (BM25 + Dense + RRF + Reranker)
        lookup_query = effective_query if effective_query else sanitized_query
        target_code_filter = selected_standard
        if not target_code_filter:
            m_code = re.search(r'\b(?:is|iso|iec)\s*[:\-]?\s*(\d{3,5})\b', lookup_query, re.IGNORECASE)
            if m_code:
                digit = m_code.group(1)
                for known_code in ["IS 1786:2008", "IS 14543:2018", "IS 269:2015", "IS 1417:2016", "IS 1293:2019", "IS 4151:2015", "IS 4984:2016", "IS 2796:2017", "IS 1374:2007", "IS 1460:2017", "IS 13252 (Part 1):2010", "IS 7049:1973"]:
                    if digit in known_code:
                        target_code_filter = known_code
                        break

        retrieved = vector_store_service.hybrid_query(
            query_text=lookup_query,
            n_results=5,
            is_code_filter=target_code_filter
        )

        # Multi-Domain Negative Firewall & Semantic Guard
        detected_domain = intent_meta.get("detected_domain", "GENERAL") if intent_meta else "GENERAL"
        q_text_lower = lookup_query.lower()
        
        is_food_query = (detected_domain == "FOOD_AGRICULTURE") or any(w in q_text_lower for w in ["food", "paneer", "palak", "eating", "eat", "milk", "paala", "doodh", "water", "curry", "diet", "nutrition", "dish", "fssai", "dairy"])
        is_civil_query = (detected_domain == "CONSTRUCTION_CIVIL") or any(w in q_text_lower for w in ["cement", "simantu", "concrete", "m20", "m25", "slab", "dhalai", "steel", "sariya", "rebar", "inumu", "fe 500", "1786", "269", "456", "pipe", "hdpe", "4984", "brick", "sand"])
        is_gold_query = (detected_domain == "PRECIOUS_METALS") or any(w in q_text_lower for w in ["gold", "sona", "bangaaram", "thangam", "silver", "chandi", "vendi", "hallmark", "huid", "carat", "karat", "916", "750", "jewell"])
        is_electrical_query = (detected_domain == "ELECTRICAL_ELECTRONICS") or any(w in q_text_lower for w in ["plug", "socket", "wire", "cable", "theega", "taar", "1293", "694", "battery", "16046", "solar", "14286", "fan", "374"])

        if retrieved:
            compatible_retrieved = []
            for c in retrieved:
                c_title_code = (c.get("doc_title", "") + " " + c.get("is_code", "") + " " + c.get("text", "")[:100]).lower()
                c_is_food = any(w in c_title_code for w in ["water", "food", "milk", "paneer", "14543", "13428", "10500", "11536", "10484"])
                c_is_civil = any(w in c_title_code for w in ["steel", "rebar", "cement", "concrete", "pipe", "1786", "269", "456", "4984"])
                c_is_gold = any(w in c_title_code for w in ["gold", "silver", "hallmark", "huid", "1417", "1418", "2112"])
                c_is_electrical = any(w in c_title_code for w in ["plug", "socket", "cable", "wire", "battery", "1293", "694", "16046", "374"])

                if is_food_query and (c_is_civil or c_is_electrical or c_is_gold):
                    continue
                if is_civil_query and (c_is_food or c_is_gold or c_is_electrical):
                    continue
                if is_gold_query and (c_is_food or c_is_civil or c_is_electrical):
                    continue
                if is_electrical_query and (c_is_food or c_is_civil or c_is_gold):
                    continue
                
                compatible_retrieved.append(c)
            retrieved = compatible_retrieved

        # 2. Corrective RAG (CRAG) Evaluation
        crag_score, is_safe, crag_verdict = hybrid_retriever_service.evaluate_crag_confidence(
            query=lookup_query,
            retrieved_chunks=retrieved
        )

        # 2b. Genuine Standards / Regulatory Domain Intent Verification
        has_explicit_code = bool(
            re.search(r'\b(is|iso|iec)\s*[:\-]?\s*\d{3,5}\b', lookup_query, re.IGNORECASE) or 
            re.search(r'\b(is|iso|iec)\s*[:\-]?\s*\d{3,5}\b', sanitized_query, re.IGNORECASE)
        )
        is_statutory = bool(
            bis_statutory_topics_service.resolve_statutory_topic(lookup_query, language=active_lang) or
            bis_statutory_topics_service.resolve_statutory_topic(sanitized_query, language=active_lang)
        )
        is_business_domain = bool(
            self._resolve_business_domain_standards(sanitized_query) or
            self._resolve_business_domain_standards(lookup_query)
        )
        is_fssai = bool(
            fssai_food_safety_service.resolve_fssai_query(lookup_query) or
            fssai_food_safety_service.resolve_fssai_query(sanitized_query)
        )
        is_iso_commercial = bool(
            online_standards_resolver.resolve_iso_or_store_licensing(lookup_query, mode=mode.value) or
            online_standards_resolver.resolve_iso_or_store_licensing(sanitized_query, mode=mode.value)
        )
        domain_keywords_pattern = (
            r'\b('
            r'is\s*[:\-]?\s*\d{3,5}|bis|isi\b|isi\s*mark|qco|fssai|foscos|hallmark|hallmarking|huid|cm/l|cml|crs|'
            r'standards?|clauses?|tables?|permissible|limits?|tolerances?|specifications?|testing|laboratory|lab\b|'
            r'nabl|udyam|msme|gst|hsn|1915|helpline|consumer|grievance|complaint|penalty|mrp|barcode|gs1|'
            r'counterfeit|fake|unauthorized|standards?\s*clubs?|nits|gold|carat|karat|purity|jewell?er|'
            r'packaged\s*water|mineral\s*water|tmt\s*steel|sariya|rebar|cement|concrete|simantu|helmet|'
            r'pressure\s*cooker|gas\s*stove|electric\s*iron|toys?|feeding\s*bottle|chekka\s*pani|rangu\s*pani|'
            r'paints?|distemper|enamel|varnish|woodwork|plywood|flush\s*doors?|fe\s*500d?|is\s*269|is\s*1786|'
            r'is\s*14543|is\s*10500|is\s*4151|is\s*9873|is\s*2347|is\s*4246|is\s*303|is\s*710|is\s*15489|'
            r'application\s*fee|marking\s*fees?|inspection\s*charges?|testing\s*charges?|renewal\s*fee|'
            r'scheme\s*[-–]?\s*(?:iv|4)|certificate\s*of\s*conformity|coc\b|sample\s*submission|counter[- ]sample|'
            r'footwear|shoes?|leather|photovoltaic|pv\s*modules?|poultry\s*feed|electric\s*iron|'
            r'is\s*366|is\s*2347|is\s*14286|is\s*15844|is\s*1489|is\s*456|is\s*1374|is\s*3735|'
            r'milk|paneer|ghee|edible\s*oil|spices|honey|sugarcane\s*juice|poultry|petrol\s*pump|solar|'
            r'plug|socket|wire|cable|battery|batteries|purifier|water'
            r')\b'
        )
        has_keyword_intent = bool(
            re.search(domain_keywords_pattern, lookup_query, re.IGNORECASE) or
            re.search(domain_keywords_pattern, sanitized_query, re.IGNORECASE)
        )
        has_standards_intent = (
            has_explicit_code or
            is_statutory or
            is_business_domain or
            is_fssai or
            is_iso_commercial or
            has_keyword_intent
        )

        # Fail-closed guardrail: if query has zero standards intent, immediately return refusal
        if not has_standards_intent:
            refusal_text = STANDARDIZED_REFUSAL
            if active_lang != "en":
                refusal_text = multilingual_translator.translate_markdown(refusal_text, active_lang)
            refusal_response = ChatResponse(
                id=query_id,
                answer=refusal_text,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.02,
                is_hallucination_safe=True,
                refusal_triggered=True,
                language=active_lang,
                suggested_followups=[
                    "What are the mandatory specifications under IS 14543 for packaged drinking water?",
                    "What are the mechanical properties required under IS 1786 for TMT bars?",
                    "How to verify ISI mark certification on household appliances?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=refusal_text,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.02,
                citations=[],
                is_hallucination_safe=True,
                refusal_triggered=True
            )
            return refusal_response

        MIN_SEMANTIC_SIMILARITY = 0.52
        top_score = retrieved[0].get("rerank_score", retrieved[0].get("similarity", 0.0)) if retrieved else 0.0
        if not retrieved or crag_verdict == "REFUSAL" or top_score < MIN_SEMANTIC_SIMILARITY:
            # Check statutory topic first
            statutory_res = bis_statutory_topics_service.resolve_statutory_topic(lookup_query, language=active_lang)
            if not statutory_res and sanitized_query != lookup_query:
                statutory_res = bis_statutory_topics_service.resolve_statutory_topic(sanitized_query, language=active_lang)
            if statutory_res:
                ans = statutory_res["answer"]
                if active_lang != "en":
                    ans = multilingual_translator.translate_markdown(ans, active_lang)
                stat_citations = [
                    Citation(
                        is_code=statutory_res.get("standard_code", "BIS Statutory Framework"),
                        title=statutory_res["title"],
                        clause="Statutory Regulations",
                        page_number=1,
                        snippet=f"Official Bureau of Indian Standards (BIS) Statutory Guidance ({statutory_res.get('portal', 'https://www.manakonline.in')}).",
                        similarity_score=0.98,
                        is_table=False
                    )
                ]
                stat_resp = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(ans),
                    mode=mode,
                    citations=stat_citations,
                    table_references=[],
                    confidence_score=0.98,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    language=active_lang,
                    suggested_followups=[
                        "What are the applicable testing standards under BIS?",
                        "How to verify license authenticity on the BIS Care App?",
                        "What are the penalty provisions under the BIS Act 2016?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=ans,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.98,
                    citations=[c.dict() for c in stat_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return stat_resp
            # Check if query matches a known nationwide business domain
            business_data = (
                self._resolve_business_domain_standards(lookup_query)
                or self._resolve_business_domain_standards(sanitized_query)
                or self._resolve_business_domain_standards(query)
            )
            if business_data:
                answer = self._generate_fallback_response(lookup_query, mode, [])
                if not answer or answer == STANDARDIZED_REFUSAL:
                    answer = self._generate_fallback_response(sanitized_query, mode, [])

                # If query has cross-lingual or ambiguous options (like chekka pani), add Google-style Did You Mean note
                current_disambig = detect_query_disambiguation(query) or detect_query_disambiguation(sanitized_query)
                if current_disambig and current_disambig.get("options"):
                    other_opts = [o["label"] for o in current_disambig["options"] if o.get("label") and not any(k in o["label"].lower() for k in ["wood", "chekka", "carpentry", "timber"])]
                    if other_opts:
                        did_you_mean_note = f"> 💡 **Did you mean?** *Showing verified standards for **{business_data['domain']}**. Did you also mean **{other_opts[0]}**? (Quick options below)*\n\n"
                        answer = did_you_mean_note + answer

                # Apply translation if target language requested
                if active_lang != "en":
                    answer = multilingual_translator.translate_markdown(answer, active_lang)

                business_citations = [
                    Citation(
                        is_code=s["code"],
                        title=s["title"],
                        clause=s["clause"],
                        page_number=1,
                        snippet=f"Statutory BIS Standard for {business_data['domain']}.",
                        similarity_score=0.92,
                        is_table=False
                    )
                    for s in business_data["standards"]
                ]
                response_obj = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(answer),
                    mode=mode,
                    citations=business_citations,
                    table_references=[],
                    confidence_score=0.92,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    needs_clarification=False,
                    disambiguation_options=current_disambig.get("options", []) if current_disambig else [],
                    language=active_lang,
                    suggested_followups=[
                        f"What testing facilities are required for {business_data['standards'][0]['code']}?",
                        f"What is the application fee under {business_data['scheme'].split(' ')[0]}?",
                        "How to register on the official BIS Manakonline portal?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=answer,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.92,
                    citations=[c.dict() for c in business_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return response_obj

            # Check if query matches ISO standard or store/shop licensing
            iso_data = online_standards_resolver.resolve_iso_or_store_licensing(lookup_query, mode=mode.value)
            if iso_data:
                answer = iso_data["answer"]
                if active_lang != "en":
                    answer = multilingual_translator.translate_markdown(answer, active_lang)

                iso_citations = [
                    Citation(
                        is_code=iso_data["code"],
                        title=iso_data["title"],
                        clause=iso_data["scheme"],
                        page_number=1,
                        snippet=f"Official Statutory Guidance from Government Portals ({iso_data.get('portal', 'www.nsws.gov.in')}).",
                        similarity_score=0.96,
                        is_table=False
                    )
                ]
                response_obj = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(answer),
                    mode=mode,
                    citations=iso_citations,
                    table_references=[],
                    confidence_score=0.96,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    language=active_lang,
                    suggested_followups=[
                        f"How to apply on the official portal for {iso_data['code']}?",
                        "What documents and fee structures are required?",
                        "How to check statutory Quality Control Orders (QCOs) on Manakonline?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=answer,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.96,
                    citations=[c.dict() for c in iso_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return response_obj

            # If user asked an in-domain general standards question, provide informative guidance rather than cold refusal
            if has_standards_intent:
                answer = self._generate_fallback_response(lookup_query, mode, retrieved or [])
                if active_lang != "en":
                    answer = multilingual_translator.translate_markdown(answer, active_lang)
                default_citations = [
                    Citation(
                        is_code="BIS Act 2016",
                        title="Bureau of Indian Standards Statutory Framework",
                        clause="Conformity Assessment Regulations",
                        page_number=1,
                        snippet="National Standards Body of India governing statutory certification, QCO compliance, and laboratory testing.",
                        similarity_score=0.90,
                        is_table=False
                    )
                ]
                gen_response = ChatResponse(
                    id=query_id,
                    answer=self._sanitize_output(answer),
                    mode=mode,
                    citations=default_citations,
                    table_references=[],
                    confidence_score=0.90,
                    is_hallucination_safe=True,
                    refusal_triggered=False,
                    language=active_lang,
                    suggested_followups=[
                        "What are the permissible limits for Packaged Drinking Water under IS 14543?",
                        "What are the mechanical properties required under IS 1786 for TMT bars?",
                        "How to verify ISI mark certification on the official BIS Care App?"
                    ]
                )
                log_query(
                    query_id=query_id,
                    query_text=sanitized_query,
                    response_text=answer,
                    mode=mode.value,
                    standard_filtered=selected_standard,
                    confidence_score=0.90,
                    citations=[c.dict() for c in default_citations],
                    is_hallucination_safe=True,
                    refusal_triggered=False
                )
                return gen_response


            # Unrelated query refusal
            refusal_text = STANDARDIZED_REFUSAL
            if active_lang != "en":
                refusal_text = multilingual_translator.translate_markdown(refusal_text, active_lang)

            refusal_response = ChatResponse(
                id=query_id,
                answer=refusal_text,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=0.1,
                is_hallucination_safe=True,
                refusal_triggered=True,
                language=active_lang,
                suggested_followups=[
                    "What parameters are governed under IS 2796 for Petrol Pumps?",
                    "What are the mechanical properties required under IS 1786 for TMT bars?",
                    "How to verify ISI mark certification on household appliances?"
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=refusal_text,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=0.1,
                citations=[],
                is_hallucination_safe=True,
                refusal_triggered=True
            )
            return refusal_response

        # ── STEP 9: POST-RAG CONFIDENCE GATE ─────────────────────────────────
        # Check top retrieved chunk similarity. If too low and no hardcoded
        # business domain match exists → return honest "not indexed" response
        # instead of letting Gemini hallucinate from an irrelevant chunk.
        POST_RAG_CONFIDENCE_THRESHOLD = 0.40
        business_data_check = self._resolve_business_domain_standards(sanitized_query)
        top_chunk_score = 0.0
        if retrieved:
            top_chunk_score = retrieved[0].get("rerank_score", retrieved[0].get("similarity", 0.0))

        if top_chunk_score < POST_RAG_CONFIDENCE_THRESHOLD and not business_data_check:
            # Build an honest "not found" response with helpful suggestions
            not_found_answer = (
                "### 🔍 No Indexed Standard Found for Your Query\n\n"
                f"**Your query:** _{sanitized_query}_\n\n"
                "The BIS Intelligent Assistant could not find a sufficiently relevant indexed "
                "Bureau of Indian Standards (IS Code) or FSSAI regulation for this specific topic "
                f"(best match score: `{top_chunk_score:.2f}` — below confidence threshold `{POST_RAG_CONFIDENCE_THRESHOLD}`).\n\n"
                "**This does NOT mean your topic is unimportant.** It may mean:\n"
                "- The specific standard for this product/topic has not yet been indexed in our database\n"
                "- The query may need more specific keywords (e.g., add IS code, product name, or FSSAI regulation number)\n\n"
                "---\n\n"
                "**💡 Suggested Actions:**\n"
                "1. Search the official **BIS Standards Portal**: [bis.gov.in](https://www.bis.gov.in)\n"
                "2. Search the official **FSSAI Standards Portal**: [fssai.gov.in](https://www.fssai.gov.in)\n"
                "3. Try rephrasing with specific IS code (e.g., `IS 14543 packaged water`)\n"
                "4. Try related known topics:\n"
                "   - Food safety → `FSSAI food license`, `milk quality`, `food adulteration`\n"
                "   - Construction → `TMT steel IS 1786`, `cement IS 269`\n"
                "   - Consumer → `ISI mark verification`, `hallmarking HUID`\n"
            )
            if active_lang != "en":
                not_found_answer = multilingual_translator.translate_markdown(not_found_answer, active_lang)
            not_found_answer = self._sanitize_output(not_found_answer)
            not_found_response = ChatResponse(
                id=query_id,
                answer=not_found_answer,
                mode=mode,
                citations=[],
                table_references=[],
                confidence_score=round(top_chunk_score, 3),
                is_hallucination_safe=True,
                refusal_triggered=False,
                language=active_lang,
                suggested_followups=[
                    "What are the FSSAI food safety regulations for a milk shop?",
                    "What are the mandatory specifications under IS 14543 for packaged drinking water?",
                    "What are the BIS certification requirements for TMT steel bars under IS 1786?",
                ]
            )
            log_query(
                query_id=query_id,
                query_text=sanitized_query,
                response_text=not_found_answer,
                mode=mode.value,
                standard_filtered=selected_standard,
                confidence_score=top_chunk_score,
                citations=[],
                is_hallucination_safe=True,
                refusal_triggered=False
            )
            return not_found_response
        # ── END STEP 9 ────────────────────────────────────────────────────────

        # 3. Format context, citations, table references, and inject Knowledge Graph connections
        context_str, citations, table_refs = self._format_context(retrieved)
        
        # Check and inject verified business domain standards and tables
        business_data = self._resolve_business_domain_standards(sanitized_query)
        if business_data:
            b_citations = [
                Citation(
                    is_code=s["code"],
                    title=s["title"],
                    clause=s["clause"],
                    page_number=1,
                    snippet=f"Statutory BIS Standard for {business_data['domain']}.",
                    similarity_score=0.96,
                    is_table=True
                )
                for s in business_data["standards"]
            ]
            citations = b_citations

            if business_data.get("table_markdown"):
                table_refs.append({
                    "is_code": business_data["standards"][0]["code"],
                    "table_number": "Table 1",
                    "table_title": f"Mandatory Permissible Limits ({business_data['standards'][0]['code']})",
                    "clause": business_data["standards"][0].get("clause", "Clause 5.0"),
                    "page_number": 1,
                    "columns": ["Parameter / Characteristic", "Permissible Limit", "Test Method / Reference"],
                    "rows": [],
                    "markdown": business_data["table_markdown"]
                })
        
        # Inject Knowledge Graph cross-references
        graph_context = standards_graph_service.format_graph_context(
            f"{sanitized_query} {retrieved[0].get('is_code', '') if retrieved else ''}"
        )
        if graph_context:
            context_str += f"\n\n{graph_context}"
        
        # Determine highest confidence
        top_confidence = retrieved[0].get("rerank_score", retrieved[0].get("similarity", 0.85)) if retrieved else 0.85
        if business_data:
            top_confidence = max(top_confidence, 0.96)

        # 4. Online Dual-Path RAG + LLM Execution & Cross-Verification
        is_connected = dual_verification_engine.check_internet_connectivity()
        is_offline = not is_connected
        system_prompt = INDUSTRY_SYSTEM_PROMPT if mode == ChatMode.INDUSTRY else CONSUMER_SYSTEM_PROMPT

        llm_draft = ""
        if is_connected and GENAI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL or "gemini-3.8-flash",
                    system_instruction=system_prompt
                )
                
                # Encapsulate user prompt securely in XML tags to block prompt injection hijacking
                user_prompt = (
                    f"<retrieved_bis_standard_context>\n"
                    f"{context_str}\n"
                    f"</retrieved_bis_standard_context>\n\n"
                    f"<user_query>\n"
                    f"{effective_query}\n"
                    f"</user_query>\n\n"
                    f"Instruction: Based on verified BIS and FSSAI standard specifications, "
                    f"provide an accurate clause-grounded response for {mode.value.upper()} audience."
                )
                
                response = model.generate_content(user_prompt)
                llm_draft = response.text or ""
            except Exception as e:
                logger.warning(f"Gemini generation call failed, switching to local statutory knowledge engine: {e}")

        if not llm_draft:
            deterministic_draft = self._generate_fallback_response(effective_query, mode, retrieved)
            llm_draft = deterministic_draft

        # Cross-Verify LLM vs RAG ground truth, inject tables, and verify consensus
        verified_answer, verified_citations, verified_tables, confidence_score, is_verified = dual_verification_engine.cross_verify_and_synthesize(
            user_query=sanitized_query,
            llm_response=llm_draft,
            rag_context=context_str,
            rag_citations=citations,
            rag_tables=table_refs,
            mode=mode,
            is_offline=not is_connected
        )

        # Apply translation if requested
        if active_lang != "en":
            verified_answer = multilingual_translator.translate_markdown(verified_answer, active_lang)

        # Sanitize output against XSS/HTML injection
        sanitized_answer = self._sanitize_output(verified_answer)

        # 5. Suggested follow-ups based on the standard
        top_standard = business_data["standards"][0]["code"] if (business_data and business_data.get("standards")) else (retrieved[0]["is_code"] if retrieved else "IS Code")
        followups = [
            f"What are the mandatory testing procedures under {top_standard}?",
            f"What tolerances and permissible limits apply in {top_standard}?",
            f"How is sampling conducted for {top_standard} compliance?"
        ]

        # ── STEP 11: POST-ANSWER GROUNDING VERIFICATION ───────────────────────
        # Verify that the answer actually cites IS codes from the retrieved context.
        # If Gemini answered from hallucinated knowledge (no citation match), flag it.
        is_grounded = True
        grounding_warning = ""

        # Extract IS codes cited in the answer
        cited_codes_in_answer = set(re.findall(r'\bIS\s*[\:\-]?\s*\d{3,5}(?:\s*[\:\-]?\s*\d{4})?\b', sanitized_answer, re.IGNORECASE))
        cited_codes_in_answer.update(re.findall(r'\bFSSAI\b', sanitized_answer, re.IGNORECASE))
        cited_codes_in_answer.update(re.findall(r'\bBIS\b', sanitized_answer, re.IGNORECASE))

        # Extract IS codes present in retrieved context / citations
        context_codes = set()
        for c in (verified_citations or citations):
            code_str = c.is_code if hasattr(c, 'is_code') else c.get('is_code', '')
            if code_str:
                context_codes.add(code_str.upper())
        if business_data:
            for s in business_data.get("standards", []):
                context_codes.add(s["code"].upper())
        # Add any IS codes extracted from retrieved raw chunks
        for chunk in retrieved:
            chunk_code = chunk.get("is_code", "")
            if chunk_code:
                context_codes.add(chunk_code.upper())

        # Grounding check: answer must cite at least one IS/FSSAI code
        # AND the answer should not be about a completely different domain than the query
        if cited_codes_in_answer and context_codes:
            # Check if answer's IS codes have ANY overlap with context codes
            answer_codes_upper = {c.upper() for c in cited_codes_in_answer}
            overlap = answer_codes_upper.intersection(context_codes)
            if not overlap and len(context_codes) > 0:
                # Answer cited codes not in retrieved context — potential cross-domain hallucination
                is_grounded = False
                grounding_warning = (
                    "\n\n---\n> ⚠️ **Grounding Notice:** This answer may cite standards "
                    "not directly retrieved from indexed documents for your query. "
                    "Please verify against official BIS/FSSAI sources."
                )
        elif not cited_codes_in_answer and len(retrieved) > 0:
            # No IS/FSSAI code cited at all despite having retrieved context
            is_grounded = False
            grounding_warning = (
                "\n\n---\n> ⚠️ **Grounding Notice:** This response could not be fully verified "
                "against indexed BIS standards. Please consult official BIS/FSSAI portals for confirmation."
            )

        if not is_grounded and grounding_warning:
            sanitized_answer = sanitized_answer + grounding_warning
        # ── END STEP 11 ───────────────────────────────────────────────────────

        response_obj = ChatResponse(
            id=query_id,
            answer=sanitized_answer,
            mode=mode,
            citations=verified_citations or citations,
            table_references=verified_tables or table_refs,
            confidence_score=round(float(top_confidence), 3),
            is_hallucination_safe=is_grounded,
            refusal_triggered=False,
            language=active_lang,
            suggested_followups=followups
        )

        # 6. Log query telemetry
        log_query(
            query_id=query_id,
            query_text=query,
            response_text=sanitized_answer,
            mode=mode.value,
            standard_filtered=selected_standard,
            confidence_score=float(top_confidence),
            citations=[c.dict() for c in (verified_citations or citations)],
            is_hallucination_safe=is_grounded,
            refusal_triggered=False
        )

        return response_obj



rag_engine = RAGEngine()
