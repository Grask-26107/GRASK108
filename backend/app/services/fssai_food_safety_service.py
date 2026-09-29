"""
FSSAI, Food Safety & Food Security Statutory Service (FSSAIFoodSafetyService)
Part of GRASK AI (SIH26107).
Provides authoritative statutory guidance on:
- FSSAI Licensing tiers via FoSCoS (Basic Registration, State License, Central License)
- Dual Certification Mandate (Mandatory BIS ISI Mark + FSSAI License for Packaged Water & Infant Food)
- Fortified Foods Standards & the '+F' Logo
- Organic Food Certification & the 'Jaivik Bharat' Logo
- Food Adulteration Detection (FSSAI DART Methods) & Consumer Grievances (Food Safety Connect / 1915)
- Food Security & Grain Storage Infrastructure (IS 6608)
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# FSSAI FoSCoS Licensing Master Framework
FOSCOS_LICENSING_FRAMEWORK = {
    "basic_registration": {
        "title": "FSSAI Basic Registration (Form A)",
        "turnover_limit": "Up to ₹12 Lakh per annum",
        "eligible_entities": "Petty Food Business Operators (FBOs), small hawkers, street food vendors, small temporary stall owners, cottage food processors.",
        "gov_fee": "₹100 per year (Validity 1 to 5 years)",
        "portal_url": "https://foscos.fssai.gov.in",
        "key_documents": ["Photo ID of FBO", "Government photo identity proof (Aadhaar / Voter ID)", "Declaration regarding business turnover < ₹12 Lakh"],
        "approval_timeline": "Within 7 to 14 working days"
    },
    "state_license": {
        "title": "FSSAI State License (Form B)",
        "turnover_limit": "₹12 Lakh to ₹20 Crore per annum",
        "eligible_entities": "Medium food manufacturers, restaurants, mid-sized distributors, caterers, cold storage units, dairy units producing 501 to 50,000 LPD.",
        "gov_fee": "₹2,000 to ₹5,000 per year (based on production capacity)",
        "portal_url": "https://foscos.fssai.gov.in",
        "key_documents": [
            "Blueprint / layout plan of the manufacturing or processing unit",
            "List of machinery and equipment with installed capacity and horsepower",
            "Water testing report from an accredited NABL/FSSAI-notified laboratory (confirming potability as per IS 10500)",
            "NOC / municipal license from local body / panchayat",
            "List of food products planned to be manufactured with flow chart"
        ],
        "approval_timeline": "Within 30 to 45 working days following inspection"
    },
    "central_license": {
        "title": "FSSAI Central License (Form B)",
        "turnover_limit": "Exceeding ₹20 Crore per annum, or Multi-state/Import/E-commerce operations",
        "eligible_entities": (
            "Large-scale food manufacturers, 100% Export Oriented Units (EOUs), food importers, "
            "e-commerce platforms, airline/railway catering, dairy plants > 50,000 LPD, "
            "and all Packaged Drinking Water / Mineral Water plants irrespective of turnover."
        ),
        "gov_fee": "₹7,500 per year",
        "portal_url": "https://foscos.fssai.gov.in",
        "key_documents": [
            "Mandatory BIS Certification / CM/L License copy (Strictly required for Packaged Water & Infant Foods)",
            "DGFT Importer-Exporter Code (IEC) (for importers)",
            "Water testing report from an FSSAI-notified lab complying with IS 10500 / IS 14543",
            "FSMS (Food Safety Management System) plan or ISO 22000 certificate",
            "NOC from Central Ground Water Authority (CGWA) for groundwater extraction (if applicable)"
        ],
        "approval_timeline": "Within 45 to 60 working days"
    }
}

# Dual Certification Matrix (Statutory Requirement for BIS ISI + FSSAI)
DUAL_CERTIFICATION_PRODUCTS = {
    "packaged_drinking_water": {
        "product": "Packaged Drinking Water (Other than Natural Mineral Water)",
        "bis_standard": "IS 14543:2018",
        "bis_scheme": "Scheme-I (Mandatory ISI Mark under Quality Control Order)",
        "fssai_regulation": "Food Safety and Standards (Food Products Standards and Food Additives) Regulations, Section 2.10.8",
        "fssai_license_type": "Mandatory FSSAI Central License via FoSCoS",
        "statutory_rule": (
            "Under Section 31 of the FSS Act, 2006 and the BIS (Conformity Assessment) Regulations, "
            "NO person shall manufacture, sell, or exhibit for sale Packaged Drinking Water except under a valid BIS Certification Mark (ISI) "
            "AND a valid FSSAI Central License. An FSSAI license will NOT be issued or renewed without a valid BIS CM/L license number."
        ),
        "mandatory_parameters": [
            {"parameter": "Total Dissolved Solids (TDS)", "limit": "75 to 500 mg/L", "test_method": "IS 3025 (Part 16)"},
            {"parameter": "Lead (as Pb) [Table 2]", "limit": "Max 0.01 mg/L", "test_method": "IS 3025 (Part 47)"},
            {"parameter": "Arsenic (as As) [Table 2]", "limit": "Max 0.01 mg/L", "test_method": "IS 3025 (Part 37)"},
            {"parameter": "Mercury (as Hg)", "limit": "Max 0.001 mg/L", "test_method": "IS 3025 (Part 48)"},
            {"parameter": "Cadmium (as Cd)", "limit": "Max 0.003 mg/L", "test_method": "IS 3025 (Part 41)"},
            {"parameter": "E. coli & Coliform Bacteria", "limit": "Zero / Absent in 250 ml", "test_method": "IS 15185"}
        ]
    },
    "packaged_mineral_water": {
        "product": "Packaged Natural Mineral Water",
        "bis_standard": "IS 13428:2005",
        "bis_scheme": "Scheme-I (Mandatory ISI Mark)",
        "fssai_regulation": "Food Safety and Standards Regulations, Section 2.10.7",
        "fssai_license_type": "Mandatory FSSAI Central License via FoSCoS",
        "statutory_rule": "Sourced directly from natural underground aquifers or springs. Mandatory dual certification (BIS ISI + FSSAI) is statutory.",
        "mandatory_parameters": [
            {"parameter": "Total Dissolved Solids (TDS)", "limit": "150 to 700 mg/L", "test_method": "IS 3025 (Part 16)"},
            {"parameter": "Nitrate (as NO3)", "limit": "Max 50 mg/L", "test_method": "IS 3025 (Part 34)"},
            {"parameter": "Pesticide Residues (Individual)", "limit": "Max 0.0001 mg/L (0.1 ppb)", "test_method": "GC-MS/MS or LC-MS/MS"}
        ]
    },
    "infant_milk_food": {
        "product": "Infant Milk Substitutes & Infant Formulas",
        "bis_standard": "IS 14433 (Infant Formula) & IS 11536 (Processed Cereal-based Infant Food)",
        "bis_scheme": "Scheme-I (Mandatory ISI Mark under Infant Milk Substitutes Act)",
        "fssai_regulation": "FSS (Foods for Infant Nutrition) Regulations, 2020",
        "fssai_license_type": "Mandatory FSSAI Central License",
        "statutory_rule": "Mandatory compliance with Infant Milk Substitutes (IMS) Act. Both BIS ISI mark and FSSAI Central License are legally compulsory before market sale.",
        "mandatory_parameters": [
            {"parameter": "Milk Fat", "limit": "Min 18% m/m", "test_method": "IS 11721"},
            {"parameter": "Milk Protein", "limit": "10.5% to 15.0% m/m", "test_method": "IS 7219"},
            {"parameter": "Bacterial Count", "limit": "Max 10,000 CFU/g", "test_method": "IS 5402"}
        ]
    }
}

# Fortified Foods Standards (+F Logo)
FORTIFIED_FOOD_STANDARDS = {
    "edible_oil": {
        "food": "Edible Vegetable Oil",
        "nutrients": "Fortified with Vitamin A (25 IU/g) and Vitamin D (4.5 IU/g)",
        "regulation": "FSS (Fortification of Foods) Regulations",
        "logo": "+F Logo (Blue in circle)",
        "statement": "Fortified with Vitamin A & D for healthy vision and bones"
    },
    "milk": {
        "food": "Toned / Double Toned / Standardized / Full Cream Milk",
        "nutrients": "Fortified with Vitamin A (770 IU/L) and Vitamin D (550 IU/L)",
        "regulation": "FSS (Fortification of Foods) Regulations",
        "logo": "+F Logo",
        "statement": "Fortified with Vitamin A & D"
    },
    "salt": {
        "food": "Double Fortified Salt (DFS)",
        "nutrients": "Fortified with Iodine (min 30 ppm at production, 15 ppm at retail) + Iron (850 to 1100 ppm)",
        "regulation": "FSS (Fortification of Foods) Regulations",
        "logo": "+F Logo",
        "statement": "Double Fortified with Iodine & Iron for prevention of goitre and anaemia"
    },
    "rice": {
        "food": "Fortified Rice Kernels (FRK)",
        "nutrients": "Iron (28 to 42.5 mg/kg), Folic Acid (75 to 125 mcg/kg), Vitamin B12 (0.75 to 1.25 mcg/kg)",
        "regulation": "FSSAI Mandatory Fortification for Public Distribution System (PDS)",
        "logo": "+F Logo",
        "statement": "Fortified with Iron, Folic Acid & Vitamin B12"
    }
}

# Organic Food Certification (Jaivik Bharat)
ORGANIC_FOOD_STANDARDS = {
    "title": "Jaivik Bharat: National Organic Food Certification",
    "regulations": "Food Safety and Standards (Organic Foods) Regulations, 2017",
    "certification_systems": [
        {
            "system": "National Programme for Organic Production (NPOP)",
            "governing_body": "APEDA (Ministry of Commerce & Industry)",
            "scope": "Commercial organic food processing, export, and domestic retail",
            "logo": "India Organic Logo + Jaivik Bharat Logo"
        },
        {
            "system": "Participatory Guarantee System (PGS-India)",
            "governing_body": "Ministry of Agriculture & Farmers Welfare",
            "scope": "Small farmer groups and farmer producer organizations (FPOs)",
            "logo": "PGS-India Green / Organic Logo + Jaivik Bharat Logo"
        }
    ],
    "verification_mandate": "Every packaged organic product in India MUST display the Jaivik Bharat logo along with the 14-digit FSSAI License Number and certification authentication code."
}

# Food Adulteration Home Detection (FSSAI DART Methods)
FSSAI_DART_TESTS = [
    {
        "food": "Milk",
        "adulterant": "Detergent / Soap",
        "test_method": "Shake equal amounts of milk and water in a glass tube. If persistent frothy lather forms, detergent is present.",
        "hazard": "Gastrointestinal disorders, mucosal damage, liver toxicity."
    },
    {
        "food": "Milk",
        "adulterant": "Starch",
        "test_method": "Add a few drops of Iodine solution (Tincture Iodine) to 5 ml of milk. Instant blue/purple coloration confirms starch.",
        "hazard": "Nutritional dilution, gastrointestinal distress."
    },
    {
        "food": "Honey",
        "adulterant": "Sugar Syrup / Invert Sugar / Molasses",
        "test_method": "Dip a cotton wick in honey and light with a match. Pure honey burns smoothly without crackling; adulterated honey with water/sugar crackles.",
        "hazard": "Elevated glycemic index, metabolic risk for diabetic patients."
    },
    {
        "food": "Mustard / Cooking Oil",
        "adulterant": "Argemone Oil",
        "test_method": "Add 5 ml of concentrated Nitric Acid (HNO3) to 5 ml of oil sample. Crimson red / orange-red color at lower layer confirms toxic argemone oil.",
        "hazard": "Causes Epidemic Dropsy, cardiac arrest, glaucoma, and bilateral leg swelling."
    },
    {
        "food": "Turmeric Powder (Haldi)",
        "adulterant": "Metanil Yellow (Industrial Dye) or Lead Chromate",
        "test_method": "Add a few drops of concentrated Hydrochloric Acid (HCl) to a water suspension of turmeric. A bright magenta/pink color confirms synthetic Metanil Yellow.",
        "hazard": "Highly carcinogenic, neurotoxic, causes severe digestive damage."
    }
]


class FSSAIFoodSafetyService:
    """Provides authoritative guidance on FSSAI licensing, food standards, and dual certification."""

    @classmethod
    def resolve_fssai_query(cls, query: str) -> Optional[Dict[str, Any]]:
        """Answers any FSSAI, Food Safety, FoSCoS, or Dual Certification query."""
        q = query.lower()
        # 0. Palak Paneer, Paneer & Fresh Culinary Dishes / Food Safety Before Eating
        if any(w in q for w in ["palak", "paneer", "panneer", "panner", "cottage cheese", "spinach", "eating", "eat"]) and any(w in q for w in ["paneer", "panneer", "panner", "palak", "spinach", "food", "curry", "ensure", "check", "before", "safe"]):
            table_md = (
                "| Food Component / Quality Parameter | Statutory Requirement (FSSAI & IS 10484) | Test Method / Verification Protocol |\n"
                "| :--- | :--- | :--- |\n"
                "| **Paneer Moisture Content** | Maximum 60.0% by mass (Paneer) / 70.0% (Chhana) | IS 2785 / Gravimetric Oven Drying |\n"
                "| **Paneer Milk Fat (Dry Basis)** | Not less than 50.0% by mass (Full Fat) / < 15.0% (Low Fat) | IS 1224 (Part 1) / Gerber Method |\n"
                "| **Starch & Flour Adulteration** | Strictly Absent / Zero Tolerance | FSSAI DART (Iodine Test: Blue color = Starch) |\n"
                "| **Detergent & Urea Adulteration** | Strictly Prohibited / Zero Tolerance | DART Froth / Lather Test with Water |\n"
                "| **Palak Pesticide Residues** | Must comply with FSSAI Maximum Residue Limits (MRLs) | Soak in 2% salt water or 1% baking soda for 15 min |\n"
                "| **Palak Artificial Green Dye (Malachite Green)** | Strictly Prohibited / Carcinogenic | FSSAI DART (Damp white cotton rub test) |\n"
                "| **Cooking Core Temperature** | Minimum 75 °C thoroughly boiled | Thermal destruction of vegetative pathogens & E. coli |\n"
                "| **Microbiological Limits** | Coliforms < 90/g, E. coli & Salmonella Absent in 25g | IS 5401 / IS 15185 / IS 5887 |"
            )
            answer = (
                "### 🥗 Citizen Food Safety Guide: What to Ensure Before Eating Palak Paneer\n\n"
                "> **Governing Standards:** **IS 10484:1983** (Specification for Paneer) & **FSSAI Food Safety and Standards (Food Products Standards and Food Additives) Regulations**\n"
                "> **Nodal Authorities:** Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (BIS FAD 19 - Dairy Products)\n\n"
                "When preparing or consuming **Palak Paneer**, consumers must be vigilant regarding two primary ingredients: **Paneer (Cottage Cheese)**, which is prone to synthetic chemical adulteration, and **Palak (Spinach)**, which often carries heavy surface pesticide residues and illicit cosmetic dyes.\n\n"
                "#### 📊 Statutory Quality Parameters & Safety Thresholds:\n\n"
                f"{table_md}\n\n"
                "#### 🔍 What Indian Consumers Must Ensure (The 5-Point Safety Protocol):\n\n"
                "1. **Paneer Authenticity & Starch Check (FSSAI DART Iodine Test):**\n"
                "   - Authentic paneer under **IS 10484** must be soft, spongy, elastic, and have a fresh milky aroma with minimum 50% milk fat on dry matter basis.\n"
                "   - **The Home Iodine Test:** Boil a small sample piece of paneer in water, let it cool to room temperature, and add 2 to 3 drops of Iodine solution (Tincture Iodine). If the paneer turns **intense blue or violet**, it has been adulterated with starch, potato mash, or flour to artificially increase weight.\n"
                "   - **Synthetic Paneer Warning:** Counterfeit paneer made from urea, detergent, and cheap refined palm oil feels unnaturally chewy, rubbery, tastes bitter, or breaks into greasy crumbs when pressed.\n\n"
                "2. **Palak (Spinach) Pesticide Wash & Toxic Dye Check:**\n"
                "   - **Pesticide Removal:** Green leafy vegetables grow close to soil and carry significant pesticide residues. Soak fresh spinach leaves in a **2% saltwater solution** (2 teaspoons salt per liter) or **1% baking soda solution** for 10 to 15 minutes, then rinse thoroughly under cold running water.\n"
                "   - **Malachite Green Dye Test:** Unscrupulous vendors sometimes dye faded spinach with **Malachite Green** (a toxic industrial dye) or copper sulphate. *Test:* Dab a piece of moistened white cotton or clean tissue paper across the wet leaves. If bright green color rubs off onto the cotton, the spinach is artificially dyed and **unfit for human consumption**.\n\n"
                "3. **Cooking Core Temperature & Microbial Safety:**\n"
                "   - Raw spinach frequently harbors soil pathogens (E. coli, Salmonella, and parasite cysts). Spinach puree must be blanched and cooked thoroughly to a core temperature exceeding **75 °C**.\n"
                "   - Paneer cubes should be lightly sautéed or immersed in hot curry for at least 3-5 minutes to eliminate any surface microbial contaminants.\n\n"
                "4. **Freshness & Nitrite Hazards of Reheating:**\n"
                "   - Palak paneer should always be consumed fresh while hot.\n"
                "   - **Never consume spinach curry kept at room temperature for over 2 hours:** Spinach contains naturally high levels of dietary nitrates. When left at room temperature (>25 °C), bacteria convert nitrates into toxic nitrites, which can cause methemoglobinemia and gastrointestinal distress. Store leftovers promptly in the refrigerator (<= 4 °C) and consume within 24 hours.\n\n"
                "5. **Restaurant & Packaged Food Verification:**\n"
                "   - **Packaged Paneer:** Ensure packaging is vacuum-sealed, stored in a refrigerated chiller cabinet (<= 4 °C), and displays the **14-digit FSSAI License Number**, 'Use-By' date, and green vegetarian logo.\n"
                "   - **Dining Out:** If ordering from a restaurant or dhaba, check their displayed **FSSAI Food Hygiene Rating (1 to 5 Stars)** and confirm hygiene standards on the premises.\n\n"
                "#### 📲 Grievance Redressal & Reporting Adulteration:\n"
                "- If you encounter adulterated paneer or contaminated restaurant food, file an immediate complaint with geotagged photo evidence via the **FSSAI Food Safety Connect App** ([foscos.fssai.gov.in](https://foscos.fssai.gov.in)).\n"
                "- You can also dial the **National Consumer Helpline (NCH)** toll-free at **1915** or SMS `8800001915`."
            )
            return {
                "title": "Citizen Food Safety Guide for Palak Paneer & Dairy Specifications (IS 10484)",
                "answer": answer,
                "table_markdown": table_md,
                "standard_code": "IS 10484 / FSSAI Dairy Regs",
                "portal": "https://foscos.fssai.gov.in"
            }

        # 1. Dual Certification (Infant Cereal Food / Baby Food)
        if any(w in q for w in ["baby", "infant", "weaning", "is 11536", "is 14433", "cereal food"]):
            table_md = (
                "| Nutritional Parameter / Requirement | Statutory Bound | Standard Test Method |\n"
                "| :--- | :--- | :--- |\n"
                "| **Protein Content** | Not less than 15.0% by weight (min 12.0% for milk-cereal weaning foods) | IS 7219 / Kjeldahl Method |\n"
                "| **Fat Content** | Minimum 4.0% and Maximum 18.0% by weight | IS 11721 |\n"
                "| **Moisture Content** | Maximum 5.0% by weight | IS 11536 Clause 4.2 |\n"
                "| **Total Bacterial Plate Count** | Maximum 10,000 CFU/g | IS 5402 |\n"
                "| **Hermetic Barrier Packaging** | Nitrogen flushed airtight moisture/oxygen barrier | IMS Act Section 6 |\n"
            )
            answer = (
                "### 👶 Statutory Guidance: Dual Certification for Infant Cereal & Baby Food\n\n"
                "**Governing Standards:** **IS 11536** (Processed Cereal-based Weaning Foods - Specification) & IS 14433 (Infant Formula)\n"
                "**Statutory Act:** Infant Milk Substitutes, Feeding Bottles and Infant Foods Act, 1992 (**IMS Act**) & FSS Act 2006\n"
                "**Mandatory Dual Certification:** Both **BIS ISI Mark** under Scheme-I AND **FSSAI Central License** via FoSCoS are strictly compulsory before manufacturing or marketing.\n\n"
                "#### 📊 Statutory Nutritional & Safety Parameters (IS 11536):\n\n"
                f"{table_md}\n"
                "#### 📦 Mandatory Packaging & Labeling Requirements under IMS Act:\n"
                "1. **Hermetic Nitrogen Flush:** Infant foods must be packed in clean, sound, nitrogen-flushed airtight containers to prevent fat oxidation and rancidity.\n"
                "2. **Nutritional Limits:** Finished product must satisfy statutory bounds for **protein** (minimum 12% to 15%) and **fat** (4% to 18%).\n"
                "3. **Mandatory Statutory Warning:** Every label must prominently carry the notice: *\"Mother's milk is best for your baby\"*.\n"
                "4. **Prohibition of Baby Pictures:** Under Section 6 of the **IMS Act**, labels are strictly prohibited from displaying pictures of mothers, infants, or graphics idealizing formula.\n"
                "5. **License Display:** Labels must display both the authentic BIS ISI Mark with CM/L number and the 14-digit **FSSAI Central License** number."
            )
            return {
                "title": "Dual Certification for Infant & Baby Cereal Foods (IS 11536 & FSSAI Central License)",
                "answer": answer,
                "table_markdown": table_md,
                "standard_code": "IS 11536",
                "portal": "https://foscos.fssai.gov.in"
            }

        # 1b. Dual Certification (Packaged Drinking Water / Mineral Water)
        if any(w in q for w in ["packaged water", "mineral water", "is 14543", "is 13428", "bottle water", "both bis", "both fssai", "dual cert"]):
            data = DUAL_CERTIFICATION_PRODUCTS["packaged_drinking_water"] if "mineral" not in q else DUAL_CERTIFICATION_PRODUCTS["packaged_mineral_water"]
            
            table_md = "| Parameter / Characteristic | Permissible Limit | Statutory Test Method |\n| :--- | :--- | :--- |\n"
            for p in data["mandatory_parameters"]:
                table_md += f"| **{p['parameter']}** | `{p['limit']}` | {p['test_method']} |\n"

            answer = (
                f"### 🇮🇳 Statutory Guidance: Dual Certification (BIS ISI + FSSAI FoSCoS)\n\n"
                f"**Product:** `{data['product']}`\n"
                f"**Mandatory BIS Standard:** `{data['bis_standard']}` ({data['bis_scheme']})\n"
                f"**FSSAI Statutory Regulation:** `{data['fssai_regulation']}`\n"
                f"**Required FSSAI License:** `{data['fssai_license_type']}`\n\n"
                f"> **⚖️ Strict Legal Mandate:** {data['statutory_rule']}\n\n"
                f"#### 📊 Mandatory Permissible Limits & Water Quality Parameters (IS 14543 Table 2)\n\n"
                f"{table_md}\n"
                f"#### 🚀 Step-by-Step Licensing Roadmap for Manufacturers\n"
                f"1. **Obtain BIS ISI Certification First:** Apply on [Manakonline](https://www.manakonline.in) under Scheme-I. Set up in-house laboratory with microbiological and chemical testing benches. Complete preliminary factory audit and sample draw.\n"
                f"2. **Grant of CM/L Number:** Upon satisfactory testing in a BIS laboratory, BIS issues an 7 or 8-digit `CM/L-XXXXXXXX` license number.\n"
                f"3. **Apply for FSSAI Central License on FoSCoS:** Visit [FoSCoS](https://foscos.fssai.gov.in). Select Category `14.1.4 (Water)`. **You MUST enter your valid BIS CM/L number** in the portal.\n"
                f"4. **NOC from CGWA:** If extracting groundwater, obtain No Objection Certificate from Central Ground Water Authority.\n"
                f"5. **Mandatory Labeling:** The bottle label must display the authentic **ISI Mark with CM/L Number**, the **14-digit FSSAI License Number**, batch code, date of manufacture, and best before date."
            )
            return {
                "title": f"Dual Certification for {data['product']}",
                "answer": answer,
                "table_markdown": table_md,
                "standard_code": data["bis_standard"],
                "portal": "https://foscos.fssai.gov.in"
            }

        # 2. FoSCoS Licensing Tiers & Application Procedure
        if any(w in q for w in ["foscos", "fssai license", "food license", "fssai registration", "fees for fssai", "how to apply fssai"]):
            b = FOSCOS_LICENSING_FRAMEWORK["basic_registration"]
            s = FOSCOS_LICENSING_FRAMEWORK["state_license"]
            c = FOSCOS_LICENSING_FRAMEWORK["central_license"]

            answer = (
                "### 🇮🇳 FSSAI FoSCoS Licensing & Registration Framework (FSS Act, 2006)\n\n"
                "All Food Business Operators (FBOs) in India must obtain statutory registration or license via the "
                "official **Food Safety Compliance System (FoSCoS)** portal: [foscos.fssai.gov.in](https://foscos.fssai.gov.in).\n\n"
                "| Licensing Tier | Annual Turnover Threshold | Government Fee | Target Business Categories |\n"
                "| :--- | :--- | :--- | :--- |\n"
                f"| **1. Basic Registration (Form A)** | `{b['turnover_limit']}` | `{b['gov_fee']}` | Petty hawkers, tea stalls, cottage processors |\n"
                f"| **2. State License (Form B)** | `{s['turnover_limit']}` | `{s['gov_fee']}` | Restaurants, mid-sized food processing, caterers |\n"
                f"| **3. Central License (Form B)** | `{c['turnover_limit']}` | `{c['gov_fee']}` | Large plants, importers, e-commerce, packaged water |\n\n"
                "#### 📝 Mandatory Documentation Required on FoSCoS\n"
                "- Photo of Food Business Operator & Government Photo ID (Aadhaar / PAN)\n"
                "- Proof of possession of premises (Electricity bill / Rent agreement / Sale deed)\n"
                "- Complete layout blueprint of food manufacturing area showing installed machinery (State & Central)\n"
                "- Water potability test report from an NABL-accredited laboratory complying with **IS 10500**\n"
                "- Food Safety Management System (FSMS) plan or ISO 22000 certificate (for Central licenses)\n\n"
                "#### 📲 Step-by-Step FoSCoS Application Process\n"
                "1. Open [https://foscos.fssai.gov.in](https://foscos.fssai.gov.in) and click **'Apply for License / Registration'**.\n"
                "2. Select your business state and choose Kind of Business (Manufacturing, Trade, Catering, Food Services).\n"
                "3. Select production capacity or annual turnover to automatically determine eligibility (Basic, State, or Central).\n"
                "4. Upload required documents and pay statutory fee online through the payment gateway.\n"
                "5. A unique 17-digit FoSCoS Application Reference Number is generated for online tracking."
            )
            return {
                "title": "FSSAI FoSCoS Licensing & Registration Guidance",
                "answer": answer,
                "table_markdown": "",
                "standard_code": "FSS Act 2006",
                "portal": "https://foscos.fssai.gov.in"
            }

        # 3. Fortified Food (+F Logo)
        if any(w in q for w in ["fortified", "fortification", "+f", "fortified rice", "fortified oil", "double fortified salt"]):
            table_md = "| Food Commodity | Mandatory Fortification Nutrients | FSSAI Logo Regulation |\n| :--- | :--- | :--- |\n"
            for k, v in FORTIFIED_FOOD_STANDARDS.items():
                table_md += f"| **{v['food']}** | {v['nutrients']} | `{v['logo']}` |\n"

            answer = (
                "### 🇮🇳 FSSAI Fortified Foods Regulations & The '+F' Logo\n\n"
                "Under the **Food Safety and Standards (Fortification of Foods) Regulations**, fortification involves deliberately "
                "increasing the content of essential micronutrients (vitamins and minerals) in staple foods to improve nutritional quality and address hidden hunger.\n\n"
                f"{table_md}\n"
                "#### 🔍 What Indian Consumers Must Check:\n"
                "1. **Authentic '+F' Logo:** Look for the square logo with a plus sign and the letter 'F' in blue.\n"
                "2. **Fortification Statement:** The package must explicitly state the added nutrients, e.g., *'Fortified with Vitamin A & D'*.\n"
                "3. **FSSAI License Number:** Check the 14-digit FSSAI license number on the label.\n"
                "4. **Public Distribution:** Rice distributed through PDS, PM POSHAN, and Anganwadi centers is mandatorily fortified with Iron, Folic Acid, and Vitamin B12."
            )
            return {
                "title": "FSSAI Fortified Foods & +F Logo Standards",
                "answer": answer,
                "table_markdown": table_md,
                "standard_code": "FSS Fortification Regulations",
                "portal": "https://ffrc.fssai.gov.in"
            }

        # 4. Organic Food & Jaivik Bharat
        if any(w in q for w in ["organic", "jaivik bharat", "npop", "pgs-india", "organic certificate", "organic food"]):
            answer = (
                "### 🇮🇳 Organic Food Standards & The 'Jaivik Bharat' Regulatory Framework\n\n"
                "Under the **Food Safety and Standards (Organic Foods) Regulations, 2017**, no person shall manufacture, pack, sell, "
                "or market any food product as 'Organic' unless it strictly complies with statutory national certification systems.\n\n"
                "#### 🛡️ Recognized Organic Certification Pathways:\n"
                "1. **National Programme for Organic Production (NPOP):** Governed by APEDA. Third-party accredited certification for commercial farming, food processing, and exports.\n"
                "2. **Participatory Guarantee System (PGS-India):** Governed by Ministry of Agriculture. Peer-review certification designed for small farmer groups and rural FPOs.\n\n"
                "#### 🏷️ Mandatory Packaging & Labeling Requirements:\n"
                "- Every certified organic package MUST carry the **'Jaivik Bharat' Logo**.\n"
                "- It must display the certification authentication code and the 14-digit FSSAI license number.\n"
                "- Exemption: Small organic producers selling directly to end consumers with annual turnover under ₹12 Lakh are exempt from NPOP/PGS certification, but CANNOT use the Jaivik Bharat logo."
            )
            return {
                "title": "Organic Food & Jaivik Bharat Certification",
                "answer": answer,
                "table_markdown": "",
                "standard_code": "FSS Organic Regulations 2017",
                "portal": "https://jaivikbharat.fssai.gov.in"
            }

        # 5. Food Adulteration Detection & Consumer Testing (DART)
        if any(w in q for w in ["adulteration", "adulterant", "dart", "fake milk", "fake honey", "fake turmeric", "test milk at home", "food safety connect"]):
            table_md = "| Food Commodity | Common Toxic Adulterant | Rapid Home Test Method (FSSAI DART) | Health Hazard |\n| :--- | :--- | :--- | :--- |\n"
            for t in FSSAI_DART_TESTS:
                table_md += f"| **{t['food']}** | {t['adulterant']} | {t['test_method']} | {t['hazard']} |\n"

            answer = (
                "### 🇮🇳 Detecting Food Adulteration: FSSAI DART Rapid Tests & Consumer Protection\n\n"
                "FSSAI's **Detect Adulteration with Rapid Test (DART)** initiative provides simple, scientific tests that citizens can perform at home without laboratory equipment:\n\n"
                f"{table_md}\n"
                "#### 📲 How Citizens Can Report Adulterated Food & File Complaints:\n"
                "1. **Food Safety Connect Portal:** File consumer complaints directly at [https://foodlicensing.fssai.gov.in/cmsweb/](https://foodlicensing.fssai.gov.in/cmsweb/).\n"
                "2. **FSSAI Toll-Free Helpline:** Call `1800-11-2100` to report substandard food or adulteration.\n"
                "3. **National Consumer Helpline:** Call `1915` or send SMS to `8800001915`.\n"
                "4. **Food Safety on Wheels (FSW):** Avail testing at mobile testing vans operated by State Food Safety Authorities in public markets."
            )
            return {
                "title": "FSSAI DART Food Adulteration Detection",
                "answer": answer,
                "table_markdown": table_md,
                "standard_code": "FSS Act 2006 Section 50-65",
                "portal": "https://foodlicensing.fssai.gov.in/cmsweb/"
            }

        # 6. Food Grain Storage & Food Security Infrastructure (IS 6608)
        if any(w in q for w in ["food security", "grain storage", "godown", "silo", "is 6608", "storage of food"]):
            answer = (
                "### 🇮🇳 Food Security & Food Grain Storage Infrastructure (IS 6608 & Warehousing Standards)\n\n"
                "Ensuring national food security requires scientific, pest-proof, and moisture-controlled grain preservation. "
                "The Bureau of Indian Standards governs agricultural warehouse and silo construction:\n\n"
                "- **IS 6608: Specifications for Flat Storage Food Grain Godowns**\n"
                "- **IS 5503: General Requirements for Silos for Food Grain Storage**\n"
                "- **IS 1797: Methods of Sampling and Test for Spices and Condiments**\n\n"
                "#### 🏗️ Mandatory Engineering Specifications for Storage:\n"
                "1. **Plinth Height:** Minimum 60 cm above surrounding ground level to prevent floodwater ingress and rodent entry.\n"
                "2. **Moisture Barriers:** Mandatory polyethylene vapour barrier membrane (minimum 100 microns) beneath concrete flooring.\n"
                "3. **Damp-Proofing:** Plinth walls must include damp-proof course (DPC) complying with IS 2645.\n"
                "4. **Ventilation:** Hermetically sealable ventilators with fine wire mesh (mesh aperture < 1.0 mm) to permit phosphine fumigation while blocking birds and insects.\n"
                "5. **Temperature & Moisture Limits:** Wheat and paddy storage moisture must be maintained strictly below 12% to 14% to prevent Aspergillus flavus fungal growth and aflatoxin contamination."
            )
            return {
                "title": "Food Grain Storage & Food Security Standards",
                "answer": answer,
                "table_markdown": "",
                "standard_code": "IS 6608",
                "portal": "https://www.manakonline.in"
            }

        return None


fssai_food_safety_service = FSSAIFoodSafetyService()
