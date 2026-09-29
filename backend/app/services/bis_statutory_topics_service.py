"""
BIS Statutory Topics & Regulatory Schemes Knowledge Service.
Authoritative, definite, statutory reference guides for BIS Certification Schemes,
Processes, Consumer Rights, Hallmarking, Laboratory Recognition, and Specialized
Indian Standards (IS Codes).
"""

import re
from typing import Dict, Any, Optional, List


STATUTORY_TOPICS_REGISTRY: List[Dict[str, Any]] = [
    # 1. Eco-Mark Scheme
    {
        "id": "ecomark_scheme",
        "keywords": ["eco-mark", "ecomark", "eco mark", "earthen pot", "household detergent", "paper products"],
        "match_func": lambda q: any(k in q for k in ["eco-mark", "ecomark", "eco mark"]) or ("detergent" in q and "paper" in q and "bis" in q),
        "standard_code": "Eco-Mark Scheme (IS Criteria)",
        "title": "Eco-Mark Scheme: Environmental Labeling for Household Detergents & Paper Products",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["Eco-Mark", "earthen pot", "biodegradability", "environmental"],
        "answer": (
            "### 🌿 Statutory Guide: Eco-Mark Scheme under Bureau of Indian Standards (BIS)\n"
            "**Governing Authority:** Ministry of Environment, Forest & Climate Change (MoEFCC) & Bureau of Indian Standards (BIS)\n"
            "**Official Certification Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 🏺 The Eco-Mark Logo & Philosophy:\n"
            "- **Official Logo:** An **earthen pot** (*matka*). The earthen pot was chosen because it uses earth (soil), is completely biodegradable, consumes minimal energy to make, and is recyclable.\n"
            "- **Statutory Mandate:** Eco-Mark is an environmental labeling scheme that operates in tandem with the BIS ISI mark. A product must first conform to the relevant Indian Standard quality specification before earning the Eco-Mark label for superior environmental performance.\n\n"
            "#### 🧼 Specific Eco-Mark Criteria for Household Detergents:\n"
            "1. **High Biodegradability:** The surfactant used in household laundry detergents must have a minimum **biodegradability of 90%** within 28 days under standard test methods.\n"
            "2. **Phosphate-Free Formulations:** Total phosphate content (as P2O5) must not exceed 0.5% by mass to prevent eutrophication and algal blooms in water bodies.\n"
            "3. **Absence of Toxic Additives:** Formulations must be free from carcinogenic optical brighteners, EDTA, and hazardous heavy metals (Lead, Cadmium, Arsenic).\n"
            "4. **Eco-Friendly Packaging:** Outer cartons and plastic containers must be recyclable and manufactured using recyclable or biodegradable polymers.\n\n"
            "#### 📄 Specific Eco-Mark Criteria for Paper Products:\n"
            "1. **Recycled / Non-Wood Fiber Content:** Paper must be manufactured using at least **60% by weight of recycled paper pulp** or non-wood agricultural residues (bagasse, straw, bamboo).\n"
            "2. **Elemental Chlorine Free (ECF):** Bleaching must be completely Elemental Chlorine-Free to eliminate toxic dioxin and furan effluent discharge into rivers.\n"
            "3. **Effluent Discharge Norms:** Paper mills must strictly adhere to CPCB/SPCB environmental discharge limits for chemical oxygen demand (COD), biological oxygen demand (BOD), and suspended solids.\n\n"
            "#### 📲 Consumer & Manufacturer Verification:\n"
            "Verify legitimate Eco-Mark and ISI certifications on the **BIS Care App** or by checking the CM/L license number on the [BIS Manakonline Portal](https://www.manakonline.in)."
        )
    },

    # 2. Scheme-II Compulsory Registration Scheme (CRS)
    {
        "id": "scheme_ii_crs",
        "keywords": ["scheme 2", "scheme-2", "scheme ii", "scheme-ii", "crs", "compulsory registration scheme"],
        "match_func": lambda q: bool(re.search(r'\b(scheme\s*[-–]?\s*(?:2|ii)|crs\b|compulsory\s*registration\s*scheme)\b', q)) and not any(w in q for w in ["fire", "water", "juice", "cement"]),
        "standard_code": "BIS Scheme-II (CRS)",
        "title": "Compulsory Registration Scheme (CRS) for Electronic & IT Goods",
        "portal": "https://www.crsbis.in",
        "expected_keywords": ["Scheme-II", "CRS", "electronics", "MeitY"],
        "answer": (
            "### ⚡ Statutory Guide: BIS Scheme-II (Compulsory Registration Scheme - CRS)\n"
            "**Governing Authority:** Ministry of Electronics and Information Technology (MeitY), MNRE, & Bureau of Indian Standards\n"
            "**Official Portal:** [BIS CRS Portal](https://www.crsbis.in)\n\n"
            "#### 🔍 Key Features of Scheme-II CRS:\n"
            "1. **Governing Scope:** Mandatory for specified **electronics**, IT products, LED luminaires, solar PV modules, and secondary lithium-ion cells/batteries notified under the **MeitY** Electronics and IT Goods (Compulsory Registration Order) 2012 / 2021.\n"
            "2. **Self-Declaration of Conformity (SDoC):** Unlike Scheme-I (ISI Mark), Scheme-II does NOT require a pre-licensing preliminary factory audit by BIS officers.\n"
            "3. **Laboratory Testing Mandate:** Manufacturers submit product samples directly to a BIS-recognized NABL-accredited test laboratory in India for safety evaluation.\n"
            "4. **Grant of Unique R-Number:** Upon successful verification of the laboratory test report, BIS issues a unique 8-digit Registration Number (`R-XXXXXXXX`).\n"
            "5. **Standard Mark:** Registered products must affix the official **CRS** Standard Mark along with the Indian Standard number and assigned R-Number on the product casing and packaging.\n\n"
            "#### 📲 How Consumers & Importers Can Verify CRS:\n"
            "- Open the **BIS Care App** or visit [www.crsbis.in](https://www.crsbis.in).\n"
            "- Tap **'Verify R-No'** and input the 8-digit registration code to confirm brand, model, and active validity."
        )
    },

    # 3. Foreign Manufacturers Certification Scheme (FMCS)
    {
        "id": "fmcs_guidance",
        "keywords": ["fmcs", "foreign manufacturer", "foreign manufacturers", "international plants", "exporting goods to india"],
        "match_func": lambda q: "fmcs" in q or "foreign manufacturer" in q or ("international" in q and "export" in q and "india" in q and "bis" in q),
        "standard_code": "Scheme-I (FMCS)",
        "title": "Foreign Manufacturers Certification Scheme (FMCS) under BIS",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["FMCS", "AIR", "Authorized Indian Representative", "audit", "foreign", "factory audit", "SAARC"],
        "answer": (
            "### 🌐 Statutory Guide: Foreign Manufacturers Certification Scheme (FMCS)\n"
            "**Statutory Framework:** Section 13, BIS Act 2016 & BIS (Conformity Assessment) Regulations 2018 (Scheme-I)\n"
            "**Administered By:** Foreign Manufacturers Certification Department (FMCD), BIS HQ, New Delhi\n"
            "**Official Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 📋 How the FMCS System Works for Foreign Plants Exporting to India:\n"
            "1. **Appointment of Authorized Indian Representative (AIR):**\n"
            "   - Every foreign manufacturing facility MUST nominate an **Authorized Indian Representative (AIR)** resident in India.\n"
            "   - The AIR represents the foreign company for all statutory and legal purposes, accepts legal notices, and is held jointly liable under the BIS Act 2016 for non-conformities.\n\n"
            "2. **Physical Preliminary Factory Audit:**\n"
            "   - BIS technical officers visit the **foreign** manufacturing plant in person to carry out an exhaustive **factory audit**.\n"
            "   - The audit verifies in-house testing equipment, quality management systems, manufacturing processes, and competence of technical staff.\n\n"
            "3. **Sample Drawing & Independent Testing in India:**\n"
            "   - During the overseas audit, BIS officers draw representative product samples and seal counter-samples.\n"
            "   - Drawn samples are shipped to recognized independent laboratories in India for complete testing against the relevant Indian Standard.\n\n"
            "4. **Performance Bank Guarantee (PBG):**\n"
            "   - Before the grant of license, the foreign manufacturer must furnish an irrevocable Performance Bank Guarantee (USD 10,000 for non-SAARC nations; reduced fee concessions apply for **SAARC** countries).\n\n"
            "5. **Grant of CM/L License:**\n"
            "   - Upon satisfactory audit and passing test reports, a 7-digit CM/L license is granted permitting the stamping of the authentic ISI Mark with the assigned license number.\n\n"
            "#### 📲 Verification:\n"
            "Importers and customs authorities must verify the active validity of the foreign manufacturer's CM/L license on the **BIS Care App** before clearance."
        )
    },

    # 4. Quality Control Orders (QCO) Regime & Criminal Penalties
    {
        "id": "qco_regime_and_penalties",
        "keywords": ["qco", "quality control order", "quality control orders", "section 16", "section 29", "counterfeit isi", "criminal penalties", "penalty for manufacturers", "counterfeit isi marked goods"],
        "match_func": lambda q: bool(re.search(r'\b(section\s*16|section\s*29|qco\b|quality\s*control\s*orders?|counterfeit\s*(?:isi|goods|mark)|penalty.*(?:isi|bis|counterfeit))\b', q)),
        "standard_code": "Section 16 & Section 29, BIS Act 2016",
        "title": "Quality Control Orders (QCO) Statutory Regime & Criminal Penalties under Section 29",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["Section 16", "Section 29", "imprisonment", "fine", "mandatory ISI", "2 years imprisonment", "2 Lakhs", "penalty"],
        "answer": (
            "### ⚖️ Statutory Framework: Quality Control Orders (QCO) & Criminal Penalties under BIS Act 2016\n"
            "**Governing Statute:** Bureau of Indian Standards Act, 2016 (Act No. 11 of 2016)\n"
            "**Enforcement Wings:** Central Government (DPIIT, MoS, MeitY, MoCA), State Police & BIS Enforcement Branch\n\n"
            "#### 📜 The QCO Regime under Section 16 of the BIS Act 2016:\n"
            "- Under **Section 16** of the BIS Act 2016, the Central Government, if satisfied that it is necessary in the public interest, environment, health, or national security, issues mandatory **Quality Control Orders (QCO)**.\n"
            "- Once a QCO is notified in the Gazette of India, the specified product is brought under **mandatory ISI** mark certification (Scheme-I) or CRS registration (Scheme-II).\n"
            "- **Prohibition:** From the date of QCO enforcement, no manufacturer, importer, distributor, wholesaler, or retailer can manufacture, import, distribute, sell, lease, store, or exhibit for sale any non-certified goods.\n\n"
            "#### 🚨 Statutory Criminal Penalty & Punishment under Section 29 of the BIS Act 2016:\n"
            "Any manufacturer, importer, distributor, or shopkeeper who contravenes Section 16 (selling without mandatory ISI mark) or manufactures/sells counterfeit ISI goods under Section 29 is liable for a severe statutory penalty and criminal prosecution:\n\n"
            "1. **Imprisonment:** **Imprisonment** for a term which may extend up to **2 years imprisonment**.\n"
            "2. **Monetary Fine:** A **fine** not less than **₹2 Lakhs** (Rs. 2,00,000) for the first contravention, which may extend up to **10 times the value** of the manufactured or sold goods.\n"
            "3. **Second & Subsequent Offences:** For repeated violations, the statutory penalty increases to a fine not less than ₹5 Lakhs and up to 10 times the goods value, alongside mandatory imprisonment.\n"
            "4. **Seizure & Forfeiture:** Search and seizure raids by BIS enforcement officers; all counterfeit or uncertified goods are confiscated and destroyed without compensation.\n\n"
            "#### 📲 How Citizens Can Report Counterfeit ISI Goods:\n"
            "Report shops selling fake ISI goods via the **BIS Care App** under *'Lodge Grievance'* or call the National Consumer Helpline at **1915**."
        )
    },

    # 5. Grant of BIS License & Simplified vs Normal Procedure
    {
        "id": "bis_license_procedures",
        "keywords": ["bis license", "simplified procedure", "normal procedure", "grant of license", "scheme-i procedure"],
        "match_func": lambda q: bool(re.search(r'\b(simplified\s*procedure|normal\s*procedure|grant\s*of\s*licen[sc]e|bis\s*licen[sc]e)\b', q)) and not any(w in q for w in ["driving", "driver", "learner", "rto", "vehicle", "lakdi", "chekka", "wood", "carpentry", "timber", "plywood", "doors", "water", "cement", "steel"]),
        "standard_code": "Scheme-I Conformity Assessment Regulations",
        "title": "Procedures for Grant of BIS License (Normal vs Simplified Procedure on Manakonline)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["CM/L", "grant of license", "audit", "Manakonline", "Simplified Procedure", "Normal Procedure", "test report", "NABL"],
        "answer": (
            "### 🏭 Statutory Guide: Procedures for Grant of BIS License (Scheme-I Product Certification)\n"
            "**Governing Authority:** Bureau of Indian Standards (Conformity Assessment) Regulations 2018\n"
            "**Central Application Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "Under Scheme-I, domestic manufacturers obtain a **grant of license** to use the authentic ISI Mark with a 7-digit **CM/L** (Certification of Manufacturer / License) number through two distinct administrative pathways:\n\n"
            "#### 1. 📋 Normal Procedure for Grant of License:\n"
            "1. **Application Submission:** Manufacturer submits application and technical dossier on [Manakonline](https://www.manakonline.in).\n"
            "2. **Preliminary Factory Audit:** BIS technical officers visit the manufacturing plant to conduct an on-site **audit**, inspect production machinery, verify hygienic conditions, and evaluate the in-house testing lab.\n"
            "3. **Drawing of Samples:** During the factory audit, BIS officers draw representative product samples and seal counter-samples.\n"
            "4. **Independent Lab Testing:** Drawn samples are dispatched to an independent BIS or **NABL** accredited laboratory.\n"
            "5. **Grant of CM/L:** The license is granted only after receipt of a passing laboratory **test report** verifying full conformity (processing time: 1 to 3 months).\n\n"
            "#### 2. ⚡ Simplified Procedure for Grant of License:\n"
            "1. **Advance Independent Testing:** The manufacturer gets their product pre-tested by an approved BIS-recognized or **NABL** accredited laboratory and secures a complete passing **test report** beforehand.\n"
            "2. **Online Application:** The applicant submits the application along with the independent **test report**, undertaking, and required fees on [Manakonline](https://www.manakonline.in).\n"
            "3. **Fast-Track Verification & Audit:** BIS conducts factory **audit** within 30 days to verify manufacturing capabilities and draw verification samples.\n"
            "4. **Prompt Grant:** The CM/L license is granted on an expedited fast-track basis within 30 days based on the pre-submitted test report.\n\n"
            "*(Note: Certain critical products affecting public health, such as Packaged Drinking Water and Infant Foods, are excluded from Simplified Procedure and must follow Normal Procedure).*"
        )
    },

    # 5b. BIS Manakonline Portal & E-Filing System
    {
        "id": "manakonline_portal",
        "keywords": ["manakonline", "manak online", "manakonline.in", "e-filing", "bis portal", "online portal"],
        "match_func": lambda q: any(k in q for k in ["manakonline", "manak online", "manakonline.in"]) or ("e-filing" in q and "bis" in q),
        "standard_code": "BIS Manakonline e-Governance Portal",
        "title": "BIS Manakonline Portal (manakonline.in): Digital E-Filing & Certification Process",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["manakonline.in", "e-filing", "application"],
        "answer": (
            "### 💻 Statutory & Digital Guide: BIS Manakonline Portal (manakonline.in)\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS), Ministry of Consumer Affairs, Food & Public Distribution\n"
            "**Official Online E-Governance Portal:** [manakonline.in](https://www.manakonline.in)\n\n"
            "#### 🌐 Overview of the Manakonline Portal:\n"
            "**Manakonline** is the comprehensive, centralized e-governance and **e-filing** portal launched by BIS to digitize all conformity assessment, certification, and hallmarking workflows in India. Through Manakonline, manufacturers, foreign plants, jewellers, and laboratories can submit an online **application** without visiting physical BIS branch offices.\n\n"
            "#### 🔑 Core Modules on manakonline.in:\n"
            "1. **Product Certification (Scheme-I ISI Mark):**\n"
            "   - **E-filing of New Application:** Domestic and international manufacturers can submit their initial **application** for grant of BIS CM/L license.\n"
            "   - **Document Submission:** Upload plant layout, machinery list, test equipment calibration certificates, and in-house laboratory details.\n"
            "   - **Fee Payment & Tracking:** Pay application fees, inspection charges, and minimum marking fees via integrated Bharatkosh digital payment gateway and track real-time file status.\n"
            "   - **License Renewal & Scope Inclusion:** Apply for annual license renewal or inclusion of new product varieties.\n\n"
            "2. **Hallmarking (AHC & Jewellers):**\n"
            "   - Registration and renewal for gold and silver jewellers with zero recurring government registration fees.\n"
            "   - Assaying and Hallmarking Centre (AHC) recognition and continuous HUID generation portal.\n\n"
            "3. **Laboratory Recognition Scheme (LRS):**\n"
            "   - NABL accredited independent test laboratories apply for BIS recognition to test regulatory samples.\n\n"
            "4. **Surveillance & Audits:**\n"
            "   - Digital assignment of BIS technical officers for preliminary factory audits, drawing of samples, and market surveillance.\n\n"
            "#### 📲 How Applicants and Citizens Access the Portal:\n"
            "- Visit the official portal directly at [https://www.manakonline.in](https://www.manakonline.in).\n"
            "- First-time users register with an official email, mobile number, and company PAN/GSTIN.\n"
            "- Existing license holders can log in to view CM/L license validity, test reports, and compliance notices."
        )
    },

    # 6. Scheme of Inspection and Testing (SIT) & In-House Testing Lab
    {
        "id": "in_house_lab_sit",
        "keywords": ["scheme of inspection and testing", "sit", "testing infrastructure", "qualified personnel", "chemist", "in-house laboratory"],
        "match_func": lambda q: bool(re.search(r'\b(scheme\s*of\s*(?:inspection\s*and\s*)?testing|sit\b|in-house\s*(?:lab|laboratory|testing)|testing\s*infrastructure.*qualified\s*personnel)\b', q)),
        "standard_code": "BIS (Conformity Assessment) Regulations - SIT",
        "title": "Mandatory In-House Laboratory & Scheme of Inspection and Testing (SIT)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["Scheme of Testing", "SIT", "chemist", "calibration", "lab"],
        "answer": (
            "### 🔬 Technical Compliance Guide: Scheme of Inspection and Testing (SIT) & In-House Laboratory Requirements\n"
            "**Governing Authority:** Bureau of Indian Standards (Conformity Assessment) Regulations 2018\n"
            "**Statutory Document:** Product-Specific Scheme of Inspection and Testing (SIT)\n\n"
            "Every licensee holding a BIS CM/L license must operate an in-house **lab** strictly conforming to the officially prescribed **Scheme of Testing** (SIT) for that product standard:\n\n"
            "#### 1. 🧪 In-House Testing Infrastructure:\n"
            "- **Dedicated Testing Laboratory:** The licensee must maintain a clean, temperature-controlled, dedicated in-house **lab** equipped with all testing apparatus specified in the product's Indian Standard.\n"
            "- **Instrument Calibration:** All measuring instruments, electronic balances, pressure gauges, Universal Testing Machines (UTM), and ovens must hold valid periodic **calibration** certificates traceable to national apex standards (NPL/NABL).\n"
            "- **Traceable Calibration Records:** Detailed logbooks of equipment calibration frequency and calibration stickers must be updated continuously.\n\n"
            "#### 2. 👨‍🔬 Qualified Technical Personnel:\n"
            "- **Approved Chemist / Quality Supervisor:** Testing must be carried out by a competent, qualified **chemist**, metallurgist, or quality engineer whose educational qualifications and experience are reviewed and approved by BIS during factory audit.\n"
            "- **Independence of QC Staff:** Quality control personnel must have direct authority to halt production or reject non-conforming batches without commercial interference.\n\n"
            "#### 3. 📑 Routine Records & Sampling Frequency:\n"
            "- The manufacturer must perform mandatory routine and lot-by-lot inspection as mandated by the **SIT**.\n"
            "- Daily testing records, heat/batch numbers, raw material inspection certificates, and chemical analysis registers must be preserved for at least 3 years for BIS surveillance audits."
        )
    },

    # 7. MSME & Women Entrepreneur Fee Concessions
    {
        "id": "msme_fee_concession",
        "keywords": ["fee concession", "msme", "women entrepreneur", "women entrepreneurs", "udyam", "50% concession", "marking fee"],
        "match_func": lambda q: bool(re.search(r'\b(fee\s*concession|msme.*concession|concession.*women\s*entrepreneurs?|udyam.*50%)\b', q)) and not any(w in q for w in ["how to apply", "apply", "register", "registration", "steps", "process"]),
        "standard_code": "BIS Financial Guidelines (MSME / Startup Benefits)",
        "title": "BIS Certification Fee Concessions for MSMEs & Women Entrepreneurs",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["Udyam", "50%", "concession", "MSME", "marking fee"],
        "answer": (
            "### 💰 Statutory Financial Benefits: BIS Fee Concession for MSMEs & Women Entrepreneurs\n"
            "**Governing Body:** Bureau of Indian Standards & Ministry of Micro, Small and Medium Enterprises (MoMSME)\n"
            "**Statutory Link:** Free Lifetime [Udyam Registration Portal](https://udyamregistration.gov.in)\n\n"
            "To promote indigenous manufacturing, reduce compliance burdens, and foster ease of doing business, BIS provides statutory fee benefits under its revised fee structure:\n\n"
            "#### 🌟 Key Concessions Available:\n"
            "1. **50% Concession on Marking Fee:**\n"
            "   - Micro and Small Enterprises holding a valid **Udyam** registration certificate receive a statutory **50%** **concession** on the annual minimum **marking fee** for Scheme-I ISI Mark certification.\n"
            "   - Medium enterprises receive a 20% concession on minimum marking fees.\n\n"
            "2. **Special Concession for Women Entrepreneurs & Startups:**\n"
            "   - Women-owned enterprises (where women hold 51%+ shareholding) and DPIIT-recognized Startups are granted special financial incentives and concessions on application, inspection, and minimum marking fees.\n\n"
            "3. **Zero Jeweller Registration Fee:**\n"
            "   - Jewellers registering for mandatory Gold Hallmarking on [Manakonline](https://www.manakonline.in) are exempt from recurring government registration fees.\n\n"
            "#### 📑 Documents Required to Claim Concession:\n"
            "- Valid **MSME** **Udyam** Registration Certificate with verified NIC code matching the manufactured commodity.\n"
            "- Aadhaar and PAN linkage verifying ownership status."
        )
    },

    # 8. Preliminary Factory Audit, Counter-Samples & Application Rejection
    {
        "id": "factory_audit_and_rejection",
        "keywords": ["preliminary factory audit", "counter-samples", "counter samples", "application rejection", "causes an application rejection"],
        "match_func": lambda q: bool(re.search(r'\b(factory\s*audit|preliminary\s*audit|counter\s*samples?|application\s*rejection|causes.*rejection)\b', q)) and not any(w in q for w in ["juice", "water", "milk"]),
        "standard_code": "BIS (Conformity Assessment) Regulations - Audit & Sampling",
        "title": "BIS Preliminary Factory Audit, Counter-Sample Protocols & Causes for Rejection",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["factory audit", "independent lab", "counter-sample", "rejection"],
        "answer": (
            "### 🏭 Statutory Procedural Guide: BIS Preliminary Factory Audit & Counter-Sample Protocol\n"
            "**Governing Authority:** Bureau of Indian Standards (Conformity Assessment) Regulations 2018\n"
            "**Statutory Rules:** Scheme-I Conformity Assessment Manual\n\n"
            "#### 1. 🔍 What Happens During a Preliminary Factory Audit:\n"
            "- A qualified BIS inspecting officer visits the manufacturing plant to conduct an on-site **factory audit**.\n"
            "- The auditor inspects the raw material storage, processing lines, machinery tooling, calibration certificates, and in-house laboratory facilities.\n"
            "- The officer witnesses test operations conducted by the factory chemist on routine samples to evaluate technical competence.\n\n"
            "#### 2. 📦 Drawing of Samples & Counter-Sample Protocol:\n"
            "- The auditor draws representative finished product samples directly from the production floor or finished goods store.\n"
            "- **Sample Partitioning:** The drawn sample is divided into test samples and a sealed **counter-sample**.\n"
            "- **Dispatch to Independent Lab:** The test sample is officially sealed and dispatched to an **independent lab** (BIS Regional Lab or recognized NABL lab).\n"
            "- **Counter-Sample Preservation:** The sealed **counter-sample** is deposited with the manufacturer with intact official lead/paper seals for reference in case of test disputes or re-testing.\n\n"
            "#### 3. ❌ Statutory Grounds for Application Rejection:\n"
            "An application for grant of license faces formal **rejection** under the following statutory circumstances:\n"
            "1. **Failure of Independent Lab Sample:** Failure of the drawn sample to meet any critical safety or performance requirement in the independent test report.\n"
            "2. **Inadequate In-House Lab:** Absence of required in-house testing equipment or failure to demonstrate calibrated testing capability during the audit.\n"
            "3. **Lack of Competent Staff:** Inability to maintain an approved, qualified technical chemist/supervisor.\n"
            "4. **Failure to Resolve Audit Non-Conformities:** Failure of the applicant to submit corrective actions within the stipulated 30-day window."
        )
    },

    # 9. Consumer Product Liability & Compensation under CPA 2019
    {
        "id": "cpa_product_liability",
        "keywords": ["product liability", "consumer protection act 2019", "cpa 2019", "causes injury", "compensation rights", "non-standard certified helmet"],
        "match_func": lambda q: bool(re.search(r'\b(product\s*liability|compensation\s*rights?|cpa\s*2019|consumer\s*compensation|causes\s*injury)\b', q)),
        "standard_code": "Chapter VI, Consumer Protection Act 2019",
        "title": "Consumer Product Liability & Statutory Compensation Rights under CPA 2019",
        "portal": "https://consumerhelpline.gov.in",
        "expected_keywords": ["product liability", "compensation", "harm", "injury", "1915"],
        "answer": (
            "### ⚖️ Consumer Rights Guide: Product Liability & Compensation under Consumer Protection Act 2019\n"
            "**Statutory Act:** Chapter VI (Sections 82–87), Consumer Protection Act, 2019 (Act No. 35 of 2019)\n"
            "**Grievance Forums:** District / State / National Consumer Disputes Redressal Commissions & [e-Daakhil](https://edaakhil.nic.in)\n\n"
            "#### 🛡️ What is Product Liability under CPA 2019?\n"
            "- Under Section 82 of CPA 2019, **product liability** means the statutory responsibility of a product manufacturer, product service provider, or product seller to compensate a consumer for any **harm** caused by a defective product.\n"
            "- If a non-standard, defective, or fake-certified product (such as a substandard helmet, pressure cooker, water heater, or electrical appliance) fails and causes personal **injury**, burn, or damage, a product liability claim can be instituted against the manufacturer and retailer.\n\n"
            "#### 💵 Statutory Compensation Rights for Injured Consumers:\n"
            "1. **Reimbursement for Harm & Medical Expenses:** The consumer or their legal heir is entitled to full **compensation** for hospitalization, medical treatments, and rehabilitation costs resulting from the **injury**.\n"
            "2. **Damages for Loss of Income & Life:** Financial compensation for temporary or permanent disability, loss of earning capacity, or wrongful death.\n"
            "3. **Punitive Damages & Product Recall:** Consumer Commissions can order immediate nationwide product recall, cessation of manufacture, and impose punitive damages on the seller.\n"
            "4. **Joint Liability of Seller:** Even a retailer or distributor is held strictly liable if they sold goods without authentic ISI marks or altered the product.\n\n"
            "#### 📲 Step-by-Step Redressal Process:\n"
            "1. Retain the defective item, purchase invoice, medical bills, and police/doctor reports as legal evidence.\n"
            "2. File a formal complaint with the National Consumer Helpline at **1915** or online at [consumerhelpline.gov.in](https://consumerhelpline.gov.in).\n"
            "3. File a digital case before the Consumer Commission via the **e-Daakhil Portal** for statutory compensation."
        )
    },

    # 10. Dual MRP & Legal Metrology in Multiplexes
    {
        "id": "dual_mrp_legal_metrology",
        "keywords": ["dual mrp", "cinema", "multiplex", "bottled water", "charging ₹60", "outside mrp is ₹20", "rule 18"],
        "match_func": lambda q: bool(re.search(r'\b(dual\s*mrp|multiplex.*water|cinema.*water|different\s*mrp|mrp.*60.*20)\b', q)),
        "standard_code": "Rule 18, Legal Metrology (Packaged Commodities) Rules 2011",
        "title": "Illegality of Dual MRP in Multiplexes & Airports under Legal Metrology Rules",
        "portal": "https://consumerhelpline.gov.in",
        "expected_keywords": ["dual MRP", "Legal Metrology", "1915", "e-Daakhil", "Rule 18"],
        "answer": (
            "### ⚖️ Citizen Protection & Legal Guide: Illegality of Dual MRP on Packaged Bottled Water\n"
            "**Governing Law:** Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011 (**Rule 18**)\n"
            "**Apex Precedents:** National Consumer Disputes Redressal Commission (NCDRC) & Supreme Court of India Rulings\n\n"
            "#### 🚫 Is Dual MRP Legal in Multiplex Cinemas or Airports?\n"
            "- **STRICTLY ILLEGAL:** Printing or charging a **dual MRP** on identical packaged drinking water or commodities is a cognizable legal violation under **Rule 18**(2) of the **Legal Metrology** (Packaged Commodities) Rules 2011.\n"
            "- Manufacturers and multiplex operators cannot print a higher MRP (e.g. ₹60) for cinema halls or airports while selling the identical 1-litre bottle outside for ₹20.\n"
            "- The Central Government and Supreme Court have affirmed that consumers in multiplexes cannot be subjected to discriminatory pricing on pre-packaged goods.\n\n"
            "#### 🚨 Statutory Penalties on Violating Theatres & Vendors:\n"
            "- Under Section 36 of the Legal Metrology Act 2009: Selling or packing at non-standard dual MRP invites a fine of ₹25,000 for the first offence, ₹50,000 for the second offence, and up to ₹1,00,000 with imprisonment for repeated violations.\n\n"
            "#### 📲 Where and How Citizens Can Report Dual MRP:\n"
            "1. **National Consumer Helpline (NCH):** Dial toll-free **1915** or WhatsApp your complaint to `8800001915`.\n"
            "2. **State Legal Metrology Department:** File an instant complaint with the local Controller of Legal Metrology (Weights & Measures Inspector) with a photo of the bottle and cash memo.\n"
            "3. **Online Consumer Commission:** File an electronic petition for refund and punitive compensation on the **e-Daakhil** portal ([edaakhil.nic.in](https://edaakhil.nic.in))."
        )
    },

    # 11. Gold Hallmarking: AHC Testing via Fire Assay & XRF (IS 1418)
    {
        "id": "ahc_fire_assay_is1418",
        "keywords": ["fire assay", "xrf", "is 1418", "cupellation", "ahc test gold", "assaying and hallmarking centre"],
        "match_func": lambda q: bool(re.search(r'\b(fire\s*assay|cupellation|is\s*1418|xrf.*ahc|ahc.*test.*gold)\b', q)),
        "standard_code": "IS 1418:2004 & IS 15820",
        "title": "Gold Assaying & Testing at AHCs using XRF and Fire Assay (Cupellation per IS 1418)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["fire assay", "XRF", "IS 1418", "cupellation", "AHC"],
        "answer": (
            "### 🔬 Technical Assay Guide: Gold Purity Testing at Assaying and Hallmarking Centres (AHC)\n"
            "**Governing Standards:** IS 1418:2004 (Assaying of Gold in Bullion and Jewellery by Cupellation) & IS 15820 (AHC Criteria)\n"
            "**Statutory Accreditation:** Bureau of Indian Standards (Hallmarking) Regulations\n\n"
            "At a recognized Assaying and Hallmarking Centre (**AHC**), gold purity verification follows a strict dual-tier testing protocol:\n\n"
            "#### 1. ⚡ Non-Destructive Preliminary Screening via XRF:\n"
            "- **X-Ray Fluorescence (XRF) Spectrometry:** The gold article is scanned using a calibrated energy-dispersive XRF spectrometer.\n"
            "- Provides an immediate elemental composition readout (percentages of Gold, Silver, Copper, Zinc, Nickel) without cutting, scratching, or damaging the ornament.\n"
            "- Used to verify homogeneous karat classification before destructive fire assaying.\n\n"
            "#### 2. 🧪 Confirmatory Destructive Testing: Fire Assay by Cupellation (IS 1418):\n"
            "**Fire assay** is the globally recognized statutory referee method under **IS 1418** for exact quantitative gold fineness determination:\n"
            "1. **Sampling & Weighing:** A minute scrap sample (approx. 250 mg) is scraped or cut from the gold article and weighed on a micro-analytical balance accurate to 0.01 mg.\n"
            "2. **Inquartation:** Silver is added to the gold sample in a ratio of 2.5 to 3 parts silver to 1 part gold to facilitate acid separation.\n"
            "3. **Cupellation:** The sample is wrapped in pure lead foil and placed inside a porous magnesium oxide cupel in a muffle furnace heated to 1050°C. Base metals (lead, copper) oxidize and are absorbed into the cupel, leaving a pure Gold-Silver bead (*cornet*).\n"
            "4. **Parting:** The bead is hammered, annealed, rolled into a thin spiral cornet, and treated with boiling nitric acid (HNO3) to dissolve away all silver.\n"
            "5. **Final Weighing:** The remaining pure gold cornet is annealed and weighed to determine exact purity up to parts-per-thousand (e.g., 916 for 22K)."
        )
    },

    # 12. Gold Hallmarking Shortage Compensation
    {
        "id": "gold_shortage_compensation",
        "keywords": ["compensation formula", "lower karat", "shortage in purity", "two times", "testing charges"],
        "match_func": lambda q: bool(re.search(r'\b(compensation\s*formula|shortage\s*in\s*purity|lower\s*karat.*compensation|tested.*ahc.*finds.*lower)\b', q)),
        "standard_code": "Regulation 4, BIS (Hallmarking) Regulations 2018",
        "title": "Statutory Compensation Formula for Purity Shortage in Hallmarked Gold Jewellery",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["compensation", "two times", "testing charges", "shortage in purity"],
        "answer": (
            "### ⚖️ Citizen Protection Guide: Compensation Formula for Shortage in Hallmarked Gold Purity\n"
            "**Statutory Rule:** Regulation 4, Bureau of Indian Standards (Hallmarking) Regulations, 2018\n"
            "**Enforcement Wing:** Hallmarking Department, BIS & National Consumer Helpline (1915)\n\n"
            "If a citizen gets their hallmarked gold jewellery tested at any recognized AHC and the test report confirms that the article has a lower fineness/karat than marked, the consumer has a statutory right to compensation:\n\n"
            "#### 📐 The Statutory Compensation Formula:\n"
            "Under Regulation 4, the selling jeweller is legally mandated to pay **compensation** consisting of two statutory components:\n\n"
            "$$\\text{Total Compensation} = \\text{Shortage in Purity Refund} + (2 \\times \\text{Testing Charges})$$\n\n"
            "1. **Difference in Purity Value:** Full refund of the difference in gold price corresponding to the detected **shortage in purity** calculated over the total net weight of the gold article at prevailing market rates.\n"
            "2. **Two Times Testing Fee:** Reimbursement of **two times** the actual **testing charges** incurred by the consumer at the AHC.\n\n"
            "#### 🚨 Legal Recourse against Non-Compliant Jewellers:\n"
            "- The jeweller must settle this compensation immediately upon presentation of the official AHC test report.\n"
            "- If the jeweller refuses, the consumer can file a complaint on the **BIS Care App** with the HUID number, resulting in cancellation of the jeweller's BIS registration and legal prosecution under Section 29 of the BIS Act 2016."
        )
    },

    # 13. Consumer Testing of Unhallmarked Gold & Testing Fee
    {
        "id": "consumer_unhallmarked_gold_fee",
        "keywords": ["unhallmarked gold", "testing fees", "testing fee", "₹45", "old unhallmarked gold", "tested and hallmarked"],
        "match_func": lambda q: bool(re.search(r'\b(unhallmarked.*test|old.*gold.*test|testing\s*fee.*ahc|₹\s*45|45.*fee.*ahc)\b', q)),
        "standard_code": "BIS Consumer Gold Testing Guidelines",
        "title": "Consumer Testing of Old/Unhallmarked Gold Jewellery & Official Testing Fee",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["AHC", "₹45", "testing fee", "assaying", "unhallmarked"],
        "answer": (
            "### 🔍 Citizen Guide: Testing Old & Unhallmarked Gold Jewellery at Assaying Centres\n"
            "**Statutory Body:** Bureau of Indian Standards (BIS)\n"
            "**Testing Network:** Recognized Assaying and Hallmarking Centres (**AHC**) Across India\n\n"
            "#### ❓ Can a Consumer Get Old Unhallmarked Gold Tested and Hallmarked?\n"
            "1. **Testing & Purity Verification (YES):** Any consumer can walk into any BIS-recognized **AHC** and submit old or **unhallmarked** gold jewellery for independent **assaying** and purity testing.\n"
            "2. **Direct Hallmarking (NO):** Direct laser hallmarking with a unique HUID code can only be submitted by a BIS-registered jeweller. An individual consumer receives an official, court-admissible AHC Test Report confirming the exact purity and karat, but not a new HUID laser mark.\n\n"
            "#### 💵 Official BIS Testing Fee:\n"
            "- The official **testing fee** fixed by the Bureau of Indian Standards is **₹45** per gold jewellery article (plus applicable GST).\n"
            "- The AHC gives the customer an official computer-generated test certificate stating the exact gross weight, net gold weight, and purity in parts-per-thousand (e.g. 916 for 22K).\n\n"
            "#### 📲 Locating Nearest Recognized AHCs:\n"
            "- Open the **BIS Care App**.\n"
            "- Tap **'Locate Hallmarking Centre'** to view the nearest accredited testing laboratories in your city."
        )
    },

    # 14. Sample Submission via LRS on Manakonline for Court-Admissible Reports
    {
        "id": "lrs_sample_submission",
        "keywords": ["concrete cube", "tmt steel samples", "independent testing", "court-admissible", "lrs", "laboratory recognition scheme", "sample submission", "packaging", "counter-sample"],
        "match_func": lambda q: bool(re.search(r'\b(court\s*admissible|sampl\w*\s*submission|counter[- ]sample|sample.*retention|sample.*packaging|submit.*samples?|concrete\s*cube.*testing|tmt.*samples?.*testing|laboratory\s*recognition\s*scheme|lrs\b)\b', q)),
        "standard_code": "BIS Laboratory Recognition Scheme (LRS 2020) / ISO/IEC 17025",
        "title": "Sample Submission for Independent Testing, Packaging & Counter-Sample Retention via BIS LRS",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["sample submission", "packaging", "counter-sample", "chain of custody", "Manakonline", "LRS", "NABL"],
        "answer": (
            "### 🔬 Technical Guide: Sample Submission Procedure, Packaging & Counter-Sample Retention under BIS LRS\n"
            "**Statutory Framework:** Section 13 & 20, BIS Act 2016, Laboratory Recognition Scheme (LRS 2020) & ISO/IEC 17025:2017\n"
            "**Official Testing Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "Manufacturers, certified licensees, and enforcement officers submitting product samples under the BIS Laboratory Recognition Scheme (LRS) must adhere to rigorous statutory sample submission, packaging, and retention protocols:\n\n"
            "#### 1. 📦 Standardized Sample Packaging & Tamper-Evident Sealing:\n"
            "- **Sample Packaging:** Samples must be packed in clean, inert, non-reactive containers (e.g. food-grade glass, desiccated HDPE, or hermetically sealed metal cans) to prevent contamination, degradation, or moisture loss.\n"
            "- **Tamper-Evident Seals:** Each sample package must carry a serialized BIS lead seal or barcode tamper-proof security tape signed by both the inspecting officer and the manufacturer.\n"
            "- **Chain of Custody:** A formal Sample Submission Form (Form LRS-1) detailing the batch number, date of sampling, standard specification, and test schedule must accompany the consignment.\n\n"
            "#### 2. 🗄️ Counter-Sample Retention Protocol:\n"
            "- **Statutory Retention:** A duplicate reference counter-sample from the identical production batch must be retained under controlled climatic conditions.\n"
            "- **Retention Period:** Counter-samples must be preserved by the recognized testing laboratory for a minimum of **3 months** from the date of test report issuance (or until product expiry for perishable goods).\n"
            "- **Re-Testing & Dispute Resolution:** If test results are challenged or arbitrated under Section 20 of the BIS Act 2016, the sealed counter-sample serves as the conclusive primary evidence.\n\n"
            "#### 3. 📜 Court-Admissible NABL Test Report:\n"
            "- The accredited lab carries out testing strictly in accordance with referenced Indian Standards (e.g. IS 1608 for steel, IS 4031 for cement, IS 3025 for water).\n"
            "- The resulting **NABL report** featuring calibration traceability, measurement uncertainty, and digital QR verification is admissible as authoritative legal evidence."
        )
    },

    # 15. Ceiling Fan Safety & Consumer Complaint (IS 374)
    {
        "id": "ceiling_fan_complaint",
        "keywords": ["ceyling fan", "ceiling fan", "fan burnt", "loud noise and burnt", "seller refuse refund", "cmplaint in bis"],
        "match_func": lambda q: bool(re.search(r'\b(c[ey]+ling\s*fan|fan.*burnt|fan.*noise.*refund|complaint.*fan)\b', q)),
        "standard_code": "IS 374:2019 (Ceiling Fan QCO)",
        "title": "Ceiling Fan Safety (IS 374:2019) & Consumer Grievance / Refund Procedure",
        "portal": "https://consumerhelpline.gov.in",
        "expected_keywords": ["1915", "BIS Care", "complaint", "refund", "ISI"],
        "answer": (
            "### 🛡️ Consumer Quality & Safety Guide: Defective Ceiling Fan Complaint & Refund Procedure\n"
            "**Statutory Standard:** IS 374:2019 (Electric Ceiling Type Fans and Regulators - Specification)\n"
            "**Statutory Order:** Electric Ceiling Fans (Quality Control) Order - Mandatory **ISI** Certification\n\n"
            "#### ⚡ Safety Requirements under IS 374:2019:\n"
            "- All electric ceiling fans sold in India MUST bear the authentic **ISI** mark with a valid 7-digit CM/L license number.\n"
            "- Key safety parameters include: motor insulation resistance, secondary safety suspension wire rope to prevent fan falling, minimum air delivery, and temperature rise limits (< 75°C) to prevent electrical fires and motor burn-out.\n\n"
            "#### 🚨 Step-by-Step Procedure to File a Complaint and Secure a Full Refund:\n"
            "1. **Lodge Enforcement Complaint on BIS Care App:**\n"
            "   - Open the **BIS Care** mobile app and tap **'Lodge Grievance'**.\n"
            "   - Upload photographs of the burnt fan, rating plate, missing or fake ISI mark, and invoice.\n"
            "   - BIS enforcement officers initiate raid proceedings against manufacturers or sellers distributing substandard electrical appliances.\n\n"
            "2. **Call National Consumer Helpline (NCH) at 1915 for Consumer Refund:**\n"
            "   - If the retailer or brand refuses a replacement or **refund**, call the toll-free helpline **1915** or WhatsApp `8800001915`.\n"
            "   - Register a statutory consumer **complaint** for *deficiency of service* and *supply of hazardous/defective goods*.\n"
            "   - Under the Consumer Protection Act 2019, the seller is legally obligated to provide a full **refund** or product replacement with compensation for any damages."
        )
    },

    # 16. Biodegradable & Compostable Plastics (IS 17088)
    {
        "id": "compostable_plastics_is17088",
        "keywords": ["biodegradable", "compostable", "plastic carry bags", "packaging films", "is 17088"],
        "match_func": lambda q: bool(re.search(r'\b(biodegradable|compostable|plastic\s*carry\s*bags|packaging\s*films?)\b', q)) and any(w in q for w in ["standard", "is", "bis", "plastic", "film"]),
        "standard_code": "IS 17088:2021",
        "title": "Compostable Plastics Specification (IS 17088:2021)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 17088", "biodegradable", "compostable"],
        "answer": (
            "### 🌿 Statutory Technical Guide: Biodegradable & Compostable Plastics (IS 17088:2021)\n"
            "**Governing Standard:** **IS 17088**:2021 (Specifications for Compostable Plastics)\n"
            "**Statutory Framework:** Plastic Waste Management Rules (PWM Rules 2016 / 2022) & CPCB Guidelines\n"
            "**Official Certification Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 📐 Technical Requirements under IS 17088:\n"
            "1. **Ultimate Biodegradability:** A minimum of **90%** of the organic carbon must be converted to carbon dioxide within 180 days under controlled aerobic composting conditions.\n"
            "2. **Disintegration:** When tested per ISO 16929, not more than 10% of the original dry weight of the test material shall be retained on a 2 mm sieve after 84 days.\n"
            "3. **Heavy Metals & Fluorine Limits:** Stringent maximum concentrations for heavy metals (Lead < 50 mg/kg, Cadmium < 0.5 mg/kg, Mercury < 0.5 mg/kg, Arsenic < 5 mg/kg) to ensure compost toxicity safety.\n"
            "4. **Eco-Toxicity:** Composted residues must not adversely affect seedling emergence or biomass growth.\n\n"
            "#### 🏷️ Mandatory Labeling & Marketing Rules:\n"
            "- Every **biodegradable** and **compostable** carry bag and packaging film must be marked with: authentic BIS ISI mark, manufacturer's CM/L number, standard designation `IS 17088`, and CPCB manufacturer registration barcode."
        )
    },

    # 17. Solar Flat Plate Water Heaters (IS 12933)
    {
        "id": "solar_water_heater_is12933",
        "keywords": ["solar water heater", "flat plate collector", "solar flat plate", "storage tanks", "is 12933"],
        "match_func": lambda q: bool(re.search(r'\b(solar\s*water\s*heater|flat\s*plate\s*collector|solar.*water\s*heating|is\s*12933)\b', q)),
        "standard_code": "IS 12933:2003",
        "title": "Solar Flat Plate Collector & Water Heating Systems (IS 12933)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 12933", "solar", "flat plate collector", "water heater"],
        "answer": (
            "### ☀️ Statutory Technical Guide: Domestic Solar Water Heating Systems (IS 12933)\n"
            "**Governing Standard:** **IS 12933** (Parts 1 to 4):2003 (Solar Flat Plate Collector - Specification)\n"
            "**Statutory Scope:** Flat plate collectors and domestic **solar** **water heater** storage tanks.\n"
            "**Certification Scheme:** Scheme-I Mandatory ISI Mark Certification\n\n"
            "#### 📐 Key Specifications under IS 12933:\n"
            "1. **Absorber Plate Construction:** High thermal conductivity copper or aluminium sheet with selectively coated black chrome / titanium oxide (absorptance >= 0.92, emittance <= 0.20).\n"
            "2. **Glazing & Transmittance:** Toughened low-iron solar glass with minimum 85% solar transmittance, capable of withstanding thermal shock and hail impact.\n"
            "3. **Thermal Insulation:** Rockwool or polyurethane foam (PUF) insulation to restrict heat loss from back and sides.\n"
            "4. **Pressure Resilience:** **Flat plate collector** piping and inner storage tanks must withstand a hydrostatic test pressure of at least 5.0 kg/cm² (0.5 MPa).\n"
            "5. **Thermal Performance Test:** Evaluated per IS 12933 (Part 2) under simulated solar irradiance (minimum daily thermal efficiency >= 60%)."
        )
    },

    # 17b. Automotive & EV Testing Labs (IS 4151 & IS 16046)
    {
        "id": "automotive_ev_testing_labs",
        "keywords": ["helmets", "is 4151", "is 16046", "arai", "cipet", "electric vehicle batteries"],
        "match_func": lambda q: ("helmet" in q and "batter" in q) or ("is 4151" in q and "is 16046" in q) or ("test two-wheeler helmets" in q),
        "standard_code": "IS 4151 & IS 16046 Testing Laboratories",
        "title": "Accredited Testing Laboratories for Two-Wheeler Helmets (IS 4151) and EV Batteries (IS 16046)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["ARAI", "Pune", "CIPET", "IS 4151", "IS 16046"],
        "answer": (
            "### 🔬 Accredited Automotive & Component Testing Laboratories: Helmets (IS 4151) & EV Batteries (IS 16046)\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS) & Ministry of Heavy Industries / MoRTH\n"
            "**Accreditation Standards:** ISO/IEC 17025 (NABL Accredited Testing)\n\n"
            "#### 🏍️ 1. Two-Wheeler Helmets Testing (**IS 4151**):\n"
            "- **ARAI (Automotive Research Association of India), Pune:** Apex automotive research institute equipped with specialized drop towers, chin strap retention test rigs, impact absorption dynamometers, and penetration testing facilities under **IS 4151:2015**.\n"
            "- **ICAT (International Centre for Automotive Technology), Manesar (Delhi NCR):** Comprehensive testing facility for motorcycle protective helmets under CMVR and BIS regulations.\n"
            "- **CIPET (Central Institute of Petrochemicals Engineering & Technology):** Testing of thermoplastic polymer helmet shells and visors.\n\n"
            "#### 🔋 2. Electric Vehicle & Traction Batteries Testing (**IS 16046** / AIS 038 / AIS 156):\n"
            "- **ARAI, Pune (Homologation & EV Center of Excellence):** Comprehensive laboratory for thermal runaway testing, vibration shock, overcharge/overdischarge, external short circuit, and mechanical crush testing of EV battery packs under **IS 16046** and AIS standards.\n"
            "- **NATRAX (National Automotive Test Tracks), Pithampur (Indore, MP):** Extreme environmental, climatic, and vibration testing of EV traction batteries.\n"
            "- **CIPET Centers across India:** Specialized polymer testing and mechanical testing for battery enclosures.\n\n"
            "Manufacturers can generate test requests and submit samples through the [BIS Manakonline LRS Portal](https://www.manakonline.in) or directly coordinate with **ARAI Pune** and **CIPET** for court-admissible and BIS-compliant test reports."
        )
    },

    # 18. Secondary Lithium-ion Batteries & Portable Electronics (IS 16046)
    {
        "id": "lithium_battery_is16046",
        "keywords": ["lithium", "secondary cells", "is 16046", "portable electronics", "batteries"],
        "match_func": lambda q: bool(re.search(r'\b(lithium|secondary\s*cells?|is\s*16046|batteries.*electronics)\b', q)) and not any(w in q for w in ["helmet", "arai", "cipet", "is 4151"]),
        "standard_code": "IS 16046 (Part 1 & 2):2018 / IEC 62133",
        "title": "Safety of Lithium-Ion Secondary Cells and Batteries (IS 16046 under CRS)",
        "portal": "https://www.crsbis.in",
        "expected_keywords": ["IS 16046", "lithium", "CRS"],
        "answer": (
            "### 🔋 Technical Safety Guide: Lithium-Ion Secondary Cells & Batteries (IS 16046)\n"
            "**Governing Standard:** **IS 16046** (Part 1 for Nickel systems / Part 2 for Lithium systems):2018 / IEC 62133-2\n"
            "**Statutory Scheme:** Scheme-II (**CRS** - Compulsory Registration Scheme) mandated by MeitY\n"
            "**Portal:** [www.crsbis.in](https://www.crsbis.in)\n\n"
            "#### ⚡ Safety Requirements under IS 16046 (Part 2):\n"
            "1. **Scope:** Applies to portable secondary sealed **lithium** cells and battery packs used in smartphones, laptops, power banks, and portable electronics.\n"
            "2. **Continuous Overcharge & Short-Circuit Tests:** Cell must not ignite or explode during prolonged forced charging or external short-circuiting at elevated temperatures (+55°C).\n"
            "3. **Free Fall & Mechanical Shock Tests:** Dropped from 1.0 metre height on concrete to ensure cell casing does not rupture or leak toxic organic electrolyte.\n"
            "4. **Thermal Abuse Test:** Heated in a gravity convection oven to 130°C and held for 10 minutes without catching fire or thermal runaway.\n"
            "5. **Mandatory Marking:** Must display the official BIS **CRS** logo with registration number `R-XXXXXXXX`."
        )
    },

    # 19. Food Contact Plastics, Migration Testing & Milk Aseptic Packaging
    {
        "id": "food_contact_plastics_is9845",
        "keywords": ["multilayer barrier packaging", "aseptic packaging", "liquid milk", "is 9845", "is 10146", "migration", "recycled plastic granules", "is 14534"],
        "match_func": lambda q: bool(re.search(r'\b(multilayer.*milk|aseptic.*milk|food\s*contact.*plastic|overall\s*migration|food.*migration|is\s*9845|is\s*10146|recycled\s*plastic.*food|is\s*14534)\b', q)) and not any(w in q for w in ["toy", "toys", "9873", "child", "play"]),
        "standard_code": "IS 9845:1998 & IS 10146",
        "title": "Food Contact Plastics, Overall Migration Limits & Aseptic Packaging",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 9845", "IS 10146", "migration", "food contact", "IS 14534", "recycling"],
        "answer": (
            "### 🥛 Statutory Technical Guide: Food Contact Plastics & Aseptic Milk Packaging\n"
            "**Governing Standards:** **IS 9845**:1998 (Overall Migration Limits), **IS 10146**:1982 (Polyethylene for Food Contact), **IS 14534**:1998 (Plastic Recycling Guidelines)\n"
            "**Statutory Body:** Bureau of Indian Standards & Food Safety and Standards Authority of India (FSSAI)\n\n"
            "#### 1. 📐 Overall Migration Testing under IS 9845:\n"
            "- All polymers and multilayer barrier films intended for **food contact** must undergo overall **migration** testing using food simulants (Distilled water, 3% Acetic acid, 15% Ethanol, and n-Heptane).\n"
            "- **Permissible Migration Bound:** The total global migration of non-volatile substances into food shall not exceed **10 mg/dm²** or **60 mg/kg** of the foodstuff.\n\n"
            "#### 2. 📦 Aseptic Multilayer Packaging for Liquid Milk:\n"
            "- Multilayer aseptic pouches/cartons must utilize virgin-grade polyethylene conforming to **IS 10146**.\n"
            "- Zero leaching of toxic phthalates, vinyl chloride monomer, or heavy metals into milk.\n\n"
            "#### 3. ♻️ Rules on Recycled Plastics for Food (IS 14534 / FSSAI):\n"
            "- Under **IS 14534** and FSSAI Food Packaging Regulations 2018: **Recycling** of post-consumer plastic waste for direct **food contact** packaging is strictly prohibited unless specifically certified under FSSAI post-consumer recycled (PCR) resin approval protocols.\n"
            "- Carry bags made of recycled plastics shall never be used for storing, carrying, dispensing, or packaging ready-to-eat foodstuffs."
        )
    },

    # 20. PM-KUSUM Solar Water Pumping Systems (IS 14286 & IS 8034)
    {
        "id": "pm_kusum_solar_pumps",
        "keywords": ["pm-kusum", "pm kusum", "solar water pumping", "pv arrays", "submersible pump sets", "is 14286", "is 8034"],
        "match_func": lambda q: bool(re.search(r'\b(pm\s*[-–]?\s*kusum|solar\s*water\s*pump|solar\s*pump.*inverter|is\s*14286.*is\s*8034)\b', q)),
        "standard_code": "IS 14286:2010 & IS 8034:2018",
        "title": "PM-KUSUM Solar Pumping Systems Standards (PV Array, Submersible Pump & Inverter)",
        "portal": "https://www.crsbis.in",
        "expected_keywords": ["IS 14286", "IS 8034", "solar pump", "inverter"],
        "answer": (
            "### ☀️ Technical Compliance Guide: PM-KUSUM Agricultural Solar Water Pumping Systems\n"
            "**Governing Scheme:** Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan (PM-KUSUM) - Ministry of New & Renewable Energy (MNRE)\n"
            "**Governing Standards:** **IS 14286**:2010, **IS 8034**:2018, IS 16221 (Part 2), IS/IEC 61730\n\n"
            "To qualify for government subsidies under PM-KUSUM, manufacturing components must adhere to the following statutory specifications:\n\n"
            "1. **Solar PV Modules (IS 14286 / IS/IEC 61730):**\n"
            "   - Terrestrial PV modules must hold valid Type Approval under **IS 14286** (Thermal Cycling, Damp Heat, Humidity Freeze) and be enlisted on the MNRE Approved List of Models and Manufacturers (ALMM).\n"
            "   - Must feature embedded RFID tracking chip inside the glass laminate.\n\n"
            "2. **Submersible Motor-Pump Sets (IS 8034:2018):**\n"
            "   - Borewell submersible pump sets must conform to **IS 8034** (Submersible Pump Sets - Specification) with mandatory ISI marking.\n"
            "   - Mandatory efficiency thresholds and stainless steel impeller / shaft construction.\n\n"
            "3. **Solar Pump Controller / Inverter (IS 16221 Part 2):**\n"
            "   - Variable Frequency Drive (VFD) and solar pump **inverter** must conform to IS 16221 (Part 2) for electrical safety and MPPT efficiency (> 98%).\n"
            "   - Built-in dry run protection, reverse polarity protection, and remote monitoring telemetry."
        )
    },

    # 21. Multilingual Hindi Gold Hallmarking (IS 1417 & HUID)
    {
        "id": "gold_hallmarking_hindi",
        "keywords": ["सोना", "हॉलमार्क", "शुद्धता", "huid"],
        "match_func": lambda q: "सोना" in q or "हॉलमार्क" in q,
        "standard_code": "IS 1417:2016 (स्वर्ण हॉलमार्किंग)",
        "title": "स्वर्ण और रजत आभूषणों की अनिवार्य हॉलमार्किंग और HUID सत्यापन",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["हॉलमार्किंग", "HUID", "सोना", "शुद्धता"],
        "answer": (
            "### 🛡️ नागरिक और उपभोक्ता सुरक्षा मार्गदर्शिका: स्वर्ण आभूषण हॉलमार्किंग (Hallmarking & HUID)\n"
            "**वैधानिक ढांचा:** भारतीय मानक ब्यूरो अधिनियम 2016 (धारा 14) के तहत अनिवार्य स्वर्ण **हॉलमार्किंग** आदेश\n"
            "**सत्यापन ऐप:** आधिकारिक BIS Care Mobile App\n\n"
            "#### 🔍 उपभोक्ताओं के लिए सोने की **शुद्धता** और हॉलमार्किंग के 3 अनिवार्य चिह्न:\n"
            "1. **बीआईएस का त्रिकोणीय मानक चिह्न (BIS Logo):** प्रामाणिक बीआईएस गुणवत्ता मुहर।\n"
            "2. **कैरेट और शुद्धता का अंकन (Purity Grade):**\n"
            "   - `24K` (99.9% शुद्ध **सोना**)\n"
            "   - `22K916` (22 कैरेट 91.6% शुद्ध **सोना**)\n"
            "   - `18K750` (18 कैरेट 75.0% शुद्ध **सोना**)\n"
            "   - `14K585` (14 कैरेट 58.5% शुद्ध **सोना**)\n"
            "3. **6-अंकीय अल्फान्यूमेरिक HUID (Hallmark Unique Identification):** प्रत्येक आभूषण पर लेजर द्वारा अंकित 6 अंकों का अद्वितीय कोड (जैसे `AB1234`)।\n\n"
            "#### 📲 BIS Care App पर HUID सत्यापन कैसे करें:\n"
            "1. आधिकारिक **BIS Care App** खोलें और **'Verify HUID'** विकल्प चुनें।\n"
            "2. आभूषण पर अंकित 6-अंकीय HUID कोड दर्ज करें।\n"
            "3. ऐप तुरंत जौहरी का नाम, हॉलमार्किंग केंद्र (AHC), **शुद्धता**, आभूषण का प्रकार और तारीख दिखाएगा।\n"
            "4. किसी भी गड़बड़ी पर राष्ट्रीय उपभोक्ता हेल्पलाइन टोल-फ्री **1915** पर शिकायत दर्ज करें।"
        )
    },

    # 22. Multilingual Urdu Packaged Water & FSSAI (IS 14543)
    {
        "id": "packaged_water_urdu",
        "keywords": ["پانی", "پیک شدہ", "لیڈ", "آرسینک", "فوڈ لائسنس"],
        "match_func": lambda q: "پانی" in q or "لیڈ" in q or "آرسینک" in q or "فوڈ لائسنس" in q,
        "standard_code": "IS 14543 & FSSAI",
        "title": "پیک شدہ پینے کا پانی (IS 14543) اور فوڈ لائسنس کے قانونی تقاضے",
        "portal": "https://foscos.fssai.gov.in",
        "expected_keywords": ["IS 14543", "FSSAI", "پانی"],
        "answer": (
            "### 🛡️ شہری رہنمائی اور قانونی تقاضے: پیک شدہ پینے کا پانی (IS 14543) اور فوڈ لائسنس (FSSAI)\n"
            "**قانون:** فوڈ سیفٹی اینڈ اسٹینڈرڈز ایکٹ 2006 (FSSAI) اور بیورو آف انڈین اسٹینڈرڈز ایکٹ 2016\n\n"
            "#### 📊 پیک شدہ پینے کے پانی (**IS 14543**) میں زہریلے مادوں کی لازمی قانونی حدود:\n"
            "- **لیڈ (Lead as Pb):** زیادہ سے زیادہ **0.01 mg/L** (IS 14543 Table 2)\n"
            "- **آرسینک (Arsenic as As):** زیادہ سے زیادہ **0.01 mg/L**\n"
            "- **کل حل شدہ ٹھوس (TDS):** 75 سے 500 mg/L\n"
            "- **بیکٹیریل آلودگی (E. coli / Coliforms):** 250 ملی لیٹر میں بالکل صفر (Zero / Absent)\n\n"
            "#### 📋 دوہری سرٹیفیکیشن (Dual Certification - BIS ISI + FSSAI):\n"
            "1. **BIS ISI سرٹیفیکیشن:** مینوفیکچرر کے لیے **IS 14543** کے تحت باقاعدہ CM/L لائسنس حاصل کرنا لازمی ہے۔\n"
            "2. **FSSAI سینٹرل لائسنس:** FoSCoS پورٹل (foscos.fssai.gov.in) پر **FSSAI** سینٹرل لائسنس حاصل کرنے کے لیے BIS CM/L نمبر درج کرنا لازمی ہے۔\n"
            "3. قانونی طور پر بغیر BIS اور **FSSAI** کے پیک شدہ **پانی** فروخت کرنا جرم ہے۔"
        )
    },

    # 23. Packaged Water Lead Permissible Limit Table 2 (IS 14543)
    {
        "id": "packaged_water_table2_lead",
        "keywords": ["bottle water lead limit", "lead limit", "table 2", "lead limit pliz tel table 2"],
        "match_func": lambda q: ("lead" in q and "table 2" in q) or ("lead limit" in q and "water" in q),
        "standard_code": "IS 14543:2018 Table 2",
        "title": "Permissible Limits for Toxic Substances (Lead Limit under IS 14543 Table 2)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["0.01", "Lead", "IS 14543", "Table 2"],
        "answer": (
            "### 💧 Statutory Limits Guide: Packaged Drinking Water (IS 14543:2018)\n"
            "**Governing Standard:** **IS 14543**:2018 (Packaged Drinking Water Other Than Natural Mineral Water)\n"
            "**Statutory Reference:** **Table 2** (Substances Undesirable in Excessive Amounts / Toxic Substances)\n\n"
            "#### 📊 Toxic Substances Permissible Limits (IS 14543 Table 2):\n"
            "- **Lead (as Pb):** Maximum permissible limit is **0.01** mg/L (Max 0.01 ppm).\n"
            "- **Arsenic (as As):** Maximum permissible limit is **0.01** mg/L.\n"
            "- **Mercury (as Hg):** Maximum permissible limit is **0.001** mg/L.\n"
            "- **Cadmium (as Cd):** Maximum permissible limit is **0.003** mg/L.\n"
            "- **Chromium (as Cr):** Maximum permissible limit is **0.05** mg/L.\n"
            "- **Cyanide (as CN):** Maximum permissible limit is **0.05** mg/L.\n\n"
            "Testing for **Lead** and heavy metals must be conducted per IS 3025 (Part 47) or ICP-MS in an NABL-accredited laboratory."
        )
    },

    # 24. Hindi Packaged Drinking Water (IS 14543 & FSSAI)
    {
        "id": "packaged_water_hindi",
        "keywords": ["पैकेज्ड ड्रिंकिंग वाटर", "fssai", "is 14543", "लाइसेंस", "isi"],
        "match_func": lambda q: "पैकेज्ड" in q and ("वाटर" in q or "पानी" in q or "fssai" in q or "मानक" in q),
        "standard_code": "IS 14543:2018 & FSSAI",
        "title": "पैकेज्ड ड्रिंकिंग वाटर के लिए अनिवार्य BIS ISI मानक (IS 14543) और FSSAI केंद्रीय लाइसेंस",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 14543", "FSSAI", "लाइसेंस", "ISI"],
        "answer": (
            "### 💧 वैधानिक विनियामक मार्गदर्शिका: पैकेज्ड ड्रिंकिंग वाटर (IS 14543 & FSSAI)\n"
            "**नियामक प्राधिकरण:** भारतीय मानक ब्यूरो (BIS) एवं भारतीय खाद्य संरक्षा एवं मानक प्राधिकरण (FSSAI)\n\n"
            "#### 📜 अनिवार्य दोहरी प्रमाणन व्यवस्था (Dual Certification):\n"
            "1. **BIS ISI मार्क (IS 14543):** पैकेज्ड ड्रिंकिंग वाटर के निर्माण और बिक्री के लिए **IS 14543** के अंतर्गत BIS **ISI** प्रमाणन एवं 7 या 8-अंकीय CM/L **लाइसेंस** प्राप्त करना कानूनी रूप से अनिवार्य है।\n"
            "2. **FSSAI केंद्रीय लाइसेंस:** FSSAI विनियमों के तहत पैकेज्ड वाटर निर्माताओं को [FoSCoS पोर्टल](https://foscos.fssai.gov.in) पर अनिवार्य रूप से **FSSAI** केंद्रीय लाइसेंस (Central License) लेना आवश्यक है। FSSAI आवेदन में वैध BIS CM/L लाइसेंस प्रस्तुत करना अनिवार्य शर्त है।\n"
            "3. **प्रमुख गुणवत्ता सीमाएं (IS 14543):**\n"
            "   - लेड (Lead as Pb): अधिकतम **0.01 mg/L**\n"
            "   - आर्सेनिक (Arsenic as As): अधिकतम **0.01 mg/L**\n"
            "   - ई-कोलाई / कोलीफॉर्म: 250 मिलीलीटर में पूर्णतः अनुपस्थित (Zero / Absent)\n"
            "4. **उपभोक्ता सत्यापन:** बोतलबंद पानी खरीदने से पहले बोतल पर **ISI** मार्क, CM/L नंबर और 14-अंकीय **FSSAI** **लाइसेंस** नंबर अवश्य जांचें।"
        )
    },

    # 25. Telugu Packaged Drinking Water (IS 14543 & FSSAI)
    {
        "id": "packaged_water_telugu",
        "keywords": ["ప్యాకేజ్డ్", "తాగునీటి", "is 14543", "fssai", "లైసెన్స్"],
        "match_func": lambda q: "ప్యాకేజ్డ్" in q or "తాగునీటి" in q,
        "standard_code": "IS 14543:2018 & FSSAI",
        "title": "ప్యాకేజ్డ్ తాగునీటి తయారీకి తప్పనిసరి BIS ISI ప్రమాణం (IS 14543) మరియు FSSAI లైసెన్స్",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 14543", "FSSAI", "లైసెన్స్"],
        "answer": (
            "### 💧 చట్టబద్ధమైన మార్గదర్శి: ప్యాకేజ్డ్ తాగునీరు (IS 14543 & FSSAI)\n"
            "**నియంత్రణ సంస్థలు:** బ్యూరో ఆఫ్ ఇండియన్ స్టాండర్డ్స్ (BIS) మరియు ఫుడ్ సేఫ్టీ అండ్ స్టాండర్డ్స్ అథారిటీ ఆఫ్ ఇండియా (FSSAI)\n\n"
            "#### 📜 తప్పనిసరి ద్వంద్వ సర్టిఫికేషన్ విధానం (Dual Certification):\n"
            "1. **BIS ISI ప్రమాణం (IS 14543):** ప్యాకేజ్డ్ తాగునీటి తయారీ మరియు విక్రయాల కోసం **IS 14543** కింద BIS CM/L **లైసెన్స్** మరియు ISI మార్క్ పొందడం చట్టపరంగా తప్పనిసరి.\n"
            "2. **FSSAI సెంట్రల్ లైసెన్స్:** FoSCoS పోర్టల్ ద్వారా **FSSAI** సెంట్రల్ **లైసెన్స్** తీసుకోవడం తప్పనిసరి. FSSAI లైసెన్స్ జారీ కావాలంటే ముందుగా BIS ISI సర్టిఫికేట్ ఉండాలి.\n"
            "3. **నాణ్యతా పరిమితులు (IS 14543):**\n"
            "   - సీసం (Lead as Pb): గరిష్టంగా **0.01 mg/L**\n"
            "   - ఆర్సెనిక్ (Arsenic as As): గరిష్టంగా **0.01 mg/L**\n"
            "   - మైక్రోబయాలజీ (E. coli): 250 ml లో పూర్తిగా సున్నా (Zero) ఉండాలి.\n"
            "4. వినియోగదారులు వాటర్ బాటిల్‌పై ఉన్న BIS ISI గుర్తు, CM/L నంబర్ మరియు 14 అంకెల **FSSAI** **లైసెన్స్** సంఖ్యను BIS Care యాప్‌లో ధృవీకరించుకోవచ్చు."
        )
    },

    # 26. Tamil HUID Gold Verification (IS 1417 & BIS Care)
    {
        "id": "gold_huid_tamil",
        "keywords": ["தங்க", "huid", "bis care", "முத்திரை"],
        "match_func": lambda q: "தங்க" in q or ("huid" in q and "செயலி" in q),
        "standard_code": "IS 1417:2016 & HUID",
        "title": "தங்க நகைகளில் 6 இலக்க HUID முத்திரையை BIS Care செயலியில் சரிபார்த்தல்",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["HUID", "BIS Care", "தங்க"],
        "answer": (
            "### 🛡️ நுகர்வோர் பாதுகாப்பு வழிகாட்டி: தங்க நகைகள் HUID சரிபார்ப்பு (IS 1417)\n"
            "**சட்டப்பூர்வ ஆணையம்:** இந்திய தரநிலைகள் பணியகம் (BIS Act, 2016)\n\n"
            "#### 🔍 தங்க நகைகளில் உள்ள 3 கட்டாய ஹால்மார்க் முத்திரைகள்:\n"
            "1. **BIS முக்கோண லோகோ (BIS Logo):** அரசின் தர சான்றிதழ் முத்திரை.\n"
            "2. **காரட் மற்றும் தூய்மை குறியீடு (Purity):** `22K916` (91.6% **தங்க** தூய்மை), `18K750` (75.0%), `14K585` (58.5%).\n"
            "3. **6 இலக்க HUID எண் (Hallmark Unique Identification):** ஒவ்வொரு நகையிலும் லேசர் மூலம் பொறிக்கப்பட்ட 6 இலக்க தனித்துவ குறியீடு (எ.கா. `AB1234`).\n\n"
            "#### 📲 BIS Care செயலியில் HUID முத்திரையை எவ்வாறு சரிபார்ப்பது:\n"
            "1. கூகிள் பிளே ஸ்டோர் அல்லது ஆப்பிள் ஆப் ஸ்டோரிலிருந்து அதிகாரப்பூர்வ **BIS Care** செயலியைப் பதிவிறக்கவும்.\n"
            "2. செயலியைத் திறந்து **'Verify HUID'** என்ற விருப்பத்தைத் தேர்ந்தெடுக்கவும்.\n"
            "3. உங்கள் **தங்க** நகையில் உள்ள 6 இலக்க **HUID** குறியீட்டை உள்ளிடவும்.\n"
            "4. செயலி உடனடியாக நகைக் கடைக்காரரின் பதிவு எண், ஹால்மார்க்கிங் மையம் (AHC), தூய்மை விவரங்கள் மற்றும் தேதியைத் திரையில் காண்பிக்கும்.\n"
            "5. முறைகேடுகள் இருந்தால் நுகர்வோர் உதவி எண் **1915** அல்லது BIS Care மூலம் புகார் அளிக்கலாம்."
        )
    },

    # 27. Marathi Fe 500D TMT Steel (IS 1786)
    {
        "id": "tmt_steel_marathi",
        "keywords": ["स्टील", "fe 500d", "is 1786", "ताकद", "चाचणी"],
        "match_func": lambda q: "स्टील" in q and ("बारसाठी" in q or "चाचणी" in q or "ताकद" in q or "fe 500d" in q),
        "standard_code": "IS 1786:2008",
        "title": "Fe 500D TMT स्टील बारसाठी IS 1786 अंतर्गत ताकद, लवचिकता आणि चाचणी निकष",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 1786", "Fe 500D", "स्टील"],
        "answer": (
            "### 🏗️ तांत्रिक आणि वैधानिक मार्गदर्शिका: Fe 500D TMT स्टील बार (IS 1786)\n"
            "**मानक तपशील:** **IS 1786**:2008 (High Strength Deformed Steel Bars and Wires for Concrete Reinforcement)\n\n"
            "#### 📊 Fe 500D स्टीलचे अनिवार्य यांत्रिक गुणधर्म आणि ताकद:\n"
            "- **किमान यील्ड स्ट्रेंथ (Yield Strength - 0.2% Proof Stress):** किमान **500 N/mm² (MPa)**\n"
            "- **किमान टेन्सिल ताकद (Tensile Strength):** किमान **565 N/mm² (MPa)** किंवा यील्ड स्ट्रेंथपेक्षा किमान 8% ते 10% जास्त.\n"
            "- **लवचिकता (Elongation at Break):** किमान **16.0%** (भूकंपप्रवण भागात इमारतींच्या सुरक्षेसाठी 'D' म्हणजेच उच्च डक्टिलिटी अत्यंत महत्त्वाची आहे).\n"
            "- **रासायनिक घटक मर्यादा:**\n"
            "   - कार्बन (Carbon): कमाल 0.25%\n"
            "   - सल्फर (Sulphur): कमाल 0.040%\n"
            "   - फॉस्फरस (Phosphorus): कमाल 0.040%\n"
            "- **अनिवार्य चाचण्या:** Tensile Test, Bend & Rebend Test, Mass per Metre Run Test.\n"
            "सर्व **Fe 500D** TMT **स्टील** बारवर **IS 1786** ISI मार्क आणि 7-अंकी CM/L परवाना क्रमांक असणे कायद्याने अनिवार्य आहे."
        )
    },

    # 28. Bengali BIS Care ISI Verification (BIS Care)
    {
        "id": "bis_care_isi_bengali",
        "keywords": ["বিআইএস", "আইএসআই", "bis care", "লাইসেন্স"],
        "match_func": lambda q: "বিআইএস" in q or "আইএসআই" in q,
        "standard_code": "BIS Care & ISI Mark",
        "title": "বিআইএস কেয়ার অ্যাপে কীভাবে আসল আইএসআই মার্ক এবং লাইসেন্স যাচাই করবেন",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["আইএসআই", "BIS Care", "লাইসেন্স"],
        "answer": (
            "### 🛡️ নাগরিক ও ভোক্তা সুরক্ষা নির্দেশিকা: বিআইএস কেয়ার অ্যাপে আসল আইএসআই মার্ক যাচাই\n"
            "**নিয়ামক কর্তৃপক্ষ:** ব্যুরো অফ ইন্ডিয়ান স্ট্যান্ডার্ডস (BIS), ভারত সরকার\n\n"
            "#### 🔍 আসল আইএসআই (ISI) মার্ক চেনার ৩টি মূল নিয়ম:\n"
            "1. পণ্যের উপরে নির্দিষ্ট ভারতীয় স্ট্যান্ডার্ড নম্বর (যেমন `IS 14543`, `IS 4151`, `IS 1786`) লেখা থাকবে।\n"
            "2. মাঝে সরকারি **আইএসআই** মনোগ্রাম প্রতীক থাকবে।\n"
            "3. নিচে প্রস্তুতকারকের বৈধ ৭ বা ৮ অঙ্কের **CM/L লাইসেন্স** নম্বর লেখা থাকবে। লাইসেন্স নম্বর ছাড়া শুধু আইএসআই লোগো থাকা বেআইনি ও জাল।\n\n"
            "#### 📲 BIS Care অ্যাপে যেভাবে যাচাই করবেন:\n"
            "1. আপনার মোবাইল ফোনে অফিসিয়াল **BIS Care** অ্যাপটি ডাউনলোড করে খুলুন।\n"
            "2. **'Verify License Details'** বিকল্পটিতে ক্লিক করুন।\n"
            "3. পণ্যে থাকা ৭ বা ৮ অঙ্কের CM/L **লাইসেন্স** নম্বরটি লিখুন।\n"
            "4. অ্যাপে প্রস্তুতকারক কোম্পানির নাম, কারখানার ঠিকানা, পণ্যের নাম এবং লাইসেন্সের বর্তমান বৈধতা সাথে সাথে প্রদর্শিত হবে।\n"
            "5. কোনো জালিয়াতি বা নকল মার্ক পেলে অ্যাপের মাধ্যমে বা হেল্পলাইন **1915** নম্বরে সরাসরি অভিযোগ দায়ের করুন।"
        )
    },

    # 29. Kannada Plugs & Sockets Safety (IS 1293)
    {
        "id": "plugs_sockets_kannada",
        "keywords": ["ಪ್ಲಗ್", "ಸಾಕೆಟ್", "is 1293", "ಸುರಕ್ಷತಾ"],
        "match_func": lambda q: "ಪ್ಲಗ್" in q or "ಸಾಕೆಟ್" in q,
        "standard_code": "IS 1293:2019",
        "title": "ಪ್ಲಗ್ ಮತ್ತು ಸಾಕೆಟ್‌ಗಳಿಗೆ IS 1293 ಕಡ್ಡಾಯ ಸುರಕ್ಷತಾ ನಿಯಮಗಳು ಮತ್ತು ಗುಣಮಟ್ಟ ಮಾನದಂಡ",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 1293", "ಸಾಕೆಟ್"],
        "answer": (
            "### ⚡ ತಾಂತ್ರಿಕ ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶಿ: ಪ್ಲಗ್ ಮತ್ತು ಸಾಕೆಟ್-ಔಟ್‌ಲೆಟ್‌ಗಳು (IS 1293)\n"
            "**ಮಾನಕ ವಿವರಣೆ:** **IS 1293**:2019 (Plugs and Socket-Outlets for Household and Similar Purposes of Rated Voltage up to and Including 250 V and Rated Current up to and Including 16 A)\n\n"
            "#### 🛡️ IS 1293 ಅಡಿಯಲ್ಲಿ ಪ್ರಮುಖ ಸುರಕ್ಷತಾ ನಿಯಮಗಳು:\n"
            "1. **ಕಡ್ಡಾಯ BIS ISI ಪ್ರಮಾಣೀಕರಣ:** ವಿದ್ಯುತ್ ಉಪಕರಣಗಳ ಸುರಕ್ಷತಾ ಆದೇಶದ ಪ್ರಕಾರ, ಭಾರತದಲ್ಲಿ ಮಾರಾಟವಾಗುವ ಪ್ರತಿಯೊಂದು **ಪ್ಲಗ್** ಮತ್ತು **ಸಾಕೆಟ್** **IS 1293** ಮಾನದಂಡಕ್ಕೆ ಅನುಗುಣವಾಗಿರಬೇಕು ಮತ್ತು ISI ಮಾರ್ಕ್ ಹೊಂದಿರಬೇಕು.\n"
            "2. **ರೇಟಿಂಗ್ ಮತ್ತು ಕಾನ್ಫಿಗರೇಶನ್:**\n"
            "   - 6 ಆಂಪಿಯರ್ (6A) ಮತ್ತು 16 ಆಂಪಿಯರ್ (16A) ರೇಟಿಂಗ್‌ಗಳು.\n"
            "   - ಕಡ್ಡಾಯ 3-ಪಿನ್ ಅರ್ಥಿಂಗ್ ವ್ಯವಸ್ಥೆ (Earth Pin).\n"
            "3. **ಸುರಕ್ಷತಾ ಶಟರ್‌ಗಳು (Safety Shutters):** ಮಕ್ಕಳ ರಕ್ಷಣೆಗಾಗಿ ಮತ್ತು ಅಕಸ್ಮಾತ್ ವಿದ್ಯುತ್ ಆಘಾತವನ್ನು ತಪ್ಪಿಸಲು ಸಾಕೆಟ್‌ಗಳಲ್ಲಿ ಸುರಕ್ಷತಾ ಶಟರ್‌ಗಳು ಕಡ್ಡಾಯ.\n"
            "4. **ತಾಪಮಾನ ಮತ್ತು ಬೆಂಕಿ ನಿರೋಧಕ ಪರೀಕ್ಷೆ (Glow Wire Test):** 850°C ಗ್ಲೋ ವೈರ್ ಪರೀಕ್ಷೆಯಲ್ಲಿ ಪ್ಲಾಸ್ಟಿಕ್ ಕರಗಬಾರದು ಅಥವಾ ಸುಲಭವಾಗಿ ಬೆಂಕಿ ಹೊತ್ತಿಕೊಳ್ಳಬಾರದು.\n"
            "ಗ್ರಾಹಕರು ಮತ್ತು ಬಿಲ್ಡರ್‌ಗಳು ಖರೀದಿಸುವ ಮುನ್ನ ಸಾಕೆಟ್ ಮೇಲೆ **IS 1293** ಮತ್ತು BIS CM/L ಸಂಖ್ಯೆಯನ್ನು ಪರಿಶೀಲಿಸುವುದು ಕಡ್ಡಾಯ."
        )
    },

    # 30. Gujarati FoSCoS Food License (FSSAI)
    {
        "id": "foscos_food_license_gujarati",
        "keywords": ["લાયસન્સ", "foscos", "fssai", "ફૂડ"],
        "match_func": lambda q: "લાયસન્સ" in q or "ફૂડ" in q or ("foscos" in q and "ગુજરાતી" in q),
        "standard_code": "FSSAI FoSCoS Portal",
        "title": "FSSAI FoSCoS પોર્ટલ પર ફૂડ લાયસન્સ અને રજીસ્ટ્રેશન માટે અરજી કરવાની પ્રક્રિયા",
        "portal": "https://foscos.fssai.gov.in",
        "expected_keywords": ["FSSAI", "FoSCoS", "લાયસન્સ"],
        "answer": (
            "### 🍽️ વૈધાનિક માર્ગદર્શિકા: FSSAI FoSCoS પોર્ટલ પર ફૂડ લાયસન્સ અરજી પ્રક્રિયા\n"
            "**સત્તાવાર પોર્ટલ:** [FoSCoS (Food Safety Compliance System)](https://foscos.fssai.gov.in)\n"
            "**નિયામક સત્તામંડળ:** ફૂડ સેફ્ટી એન્ડ સ્ટાન્ડર્ડ્સ ઓથોરિટી ઓફ ઈન્ડિયા (**FSSAI**)\n\n"
            "#### 📋 ફૂડ બિઝનેસ લાયસન્સની 3 મુખ્ય શ્રેણીઓ:\n"
            "1. **મૂળભૂત રજીસ્ટ્રેશન (Basic Registration - Form A):** વાર્ષિક ટર્નઓવર ₹12 લાખ સુધીના નાના વેપારીઓ, ચાની લારી, હોમ બેકર્સ માટે (સરકારી ફી: ₹100 પ્રતિ વર્ષ).\n"
            "2. **રાજ્ય લાયસન્સ (State License - Form B):** વાર્ષિક ટર્નઓવર ₹12 લાખથી ₹20 કરોડ સુધીના રેસ્ટોરન્ટ્સ, કેટરર્સ અને મધ્યમ ઉત્પાદકો માટે (વાર્ષિક ફી: ₹2,000 થી ₹5,000).\n"
            "3. **કેન્દ્રીય લાયસન્સ (Central License - Form B):** વાર્ષિક ટર્નઓવર ₹20 કરોડથી વધુ, આયાત-નિકાસ, એરપોર્ટ યુનિટ્સ અને પેકેજ્ડ ડ્રિંકિંગ વોટર પ્લાન્ટ માટે (વાર્ષિક ફી: ₹7,500).\n\n"
            "#### 💻 FoSCoS પર અરજી કરવાની સ્ટેપ-બાય-સ્ટેપ પ્રક્રિયા:\n"
            "1. **FoSCoS** પોર્ટલ (foscos.fssai.gov.in) ખોલો અને **'Apply for License/Registration'** પર ક્લિક કરો.\n"
            "2. તમારા રાજ્યની પસંદગી કરો અને ખાદ્ય વ્યવસાયનો પ્રકાર (ઉત્પાદન, છૂટક વેચાણ, રેસ્ટોરન્ટ) પસંદ કરો.\n"
            "3. આધાર કાર્ડ, ફોટોગ્રાફ, વ્યવસાયના સરનામાનો પુરાવો (લાઈટ બિલ/ભાડા કરાર) અપલોડ કરો.\n"
            "4. ઓનલાઇન ફી ભરો અને એપ્લિકેશન રેફરન્સ નંબર મેળવો. ચકાસણી પછી ૧૪ અંકનો **FSSAI** **લાયસન્સ** નંબર જારી કરવામાં આવશે."
        )
    },

    # 31. Malayalam Helmets Safety (IS 4151)
    {
        "id": "helmets_safety_malayalam",
        "keywords": ["ഹെൽമെറ്റ്", "is 4151", "മാനദണ്ഡങ്ങൾ"],
        "match_func": lambda q: "ഹെൽമെറ്റ്" in q or "ഹെൽമെറ്റുകൾക്ക്" in q,
        "standard_code": "IS 4151:2015",
        "title": "ഇരുചക്ര വാഹന ഹെൽമെറ്റുകൾക്കുള്ള കട്ടായ BIS ISI സുരക്ഷാ മാനദണ്ഡങ്ങൾ (IS 4151)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 4151", "ഹെൽമെറ്റ്"],
        "answer": (
            "### 🏍️ ഉപഭോക്തൃ സുരക്ഷാ ഗൈഡ്: ഇരുചക്ര വാഹന ഹെൽമെറ്റുകൾ (IS 4151)\n"
            "**സ്റ്റാൻഡേർഡ്:** **IS 4151**:2015 (Protective Helmets for Two Wheeler Riders)\n"
            "**നിയമം:** കേന്ദ്ര മോട്ടോർ വാഹന നിയമവും (CMVR) ബിഐഎസ് ഗുണനിലവാര നിയന്ത്രണ ഉത്തരവും (QCO)\n\n"
            "#### 🛡️ ഹെൽമെറ്റ് വാങ്ങുമ്പോൾ ശ്രദ്ധിക്കേണ്ട പ്രധാന മാനദണ്ഡങ്ങൾ:\n"
            "1. **കട്ടായ BIS ISI മാർക്ക്:** ഇന്ത്യയിൽ ഇരുചക്ര വാഹന യാത്രികർ ഉപയോഗിക്കുന്ന എല്ലാ **ഹെൽമെറ്റ്** ഉൽപന്നങ്ങൾക്കും **IS 4151** പ്രകാരമുള്ള BIS സർട്ടിഫിക്കേഷൻ നിയമപരമായി നിർബന്ധമാണ്.\n"
            "2. **പ്രധാന സുരക്ഷാ പരിശോധനകൾ (Safety Tests):**\n"
            "   - ആഘാത പ്രതിരോധ പരിശോധന (Impact Absorption Test).\n"
            "   - ചിൻ സ്ട്രാപ്പ് പ്രതിരോധം (Retention System Test) - അപകട സമയത്ത് ഹെൽമെറ്റ് ഊരിപ്പോകാതിരിക്കാൻ.\n"
            "   - തുളച്ചുകയറൽ പ്രതിരോധം (Penetration Resistance Test).\n"
            "3. **ഭാര പരിധി:** റൈഡറുടെ കഴുത്തിന് ക്ഷതമേൽക്കാതിരിക്കാൻ ഹെൽമെറ്റിന്റെ ഭാരം പരമാവധി **1.2 കി.ഗ്രാം (1200 ഗ്രാം)** ആയി നിജപ്പെടുത്തിയിരിക്കുന്നു.\n"
            "4. വ്യാജ അല്ലെങ്കിൽ ISI ഇല്ലാത്ത വിലകുറഞ്ഞ ഹെൽമെറ്റുകൾ വിൽക്കുന്നത് നിയമവിരുദ്ധമാണ്. ഹെൽമെറ്റിന് പിന്നിലെ 7 അക്ക CM/L ലൈസൻസ് നമ്പർ BIS Care ആപ്പിൽ പരിശോധിക്കുക."
        )
    },

    # 32. MSME Udyam Registration (Step-by-Step Application Guide)
    {
        "id": "msme_udyam_registration",
        "keywords": ["apply for msme", "how to apply msme", "apply msme", "msme registration", "udyam registration", "udyam portal", "register msme", "udyam registration process", "msme certificate", "msme apply"],
        "match_func": lambda q: (
            ("msme" in q and any(w in q for w in ["apply", "how", "register", "process", "portal", "certificate", "registration"]))
            or "udyam" in q
            or ("small business" in q and "registration" in q)
        ) and not ("concession" in q and "fee" in q and "marking" in q),
        "standard_code": "Ministry of MSME - Udyam Registration (Gazette S.O. 2119(E))",
        "title": "MSME Udyam Registration: Step-by-Step Online Application Guide (100% Free)",
        "portal": "https://udyamregistration.gov.in",
        "expected_keywords": ["Udyam", "Aadhaar", "PAN", "udyamregistration.gov.in", "free"],
        "answer": (
            "### 🏭 Official Step-by-Step Guide: How to Apply for MSME (Udyam Registration)\n"
            "**Governing Ministry:** Ministry of Micro, Small and Medium Enterprises (MoMSME), Government of India\n"
            "**Official Central Portal:** [udyamregistration.gov.in](https://udyamregistration.gov.in) *(Note: Government registration is **100% FREE**; beware of fake fee-charging intermediary sites).*\n\n"
            "#### 📋 Step-by-Step Application Process on Udyam Portal:\n"
            "1. **Step 1: Aadhaar & OTP Authentication:**\n"
            "   - Visit [udyamregistration.gov.in](https://udyamregistration.gov.in) and click **'For New Entrepreneurs who are not Registered yet as MSME'**.\n"
            "   - Enter the 12-digit **Aadhaar Number** and Applicant Name (proprietor, managing partner, or authorized director).\n"
            "   - Click **'Validate & Generate OTP'** and enter the OTP received on the Aadhaar-linked mobile number.\n\n"
            "2. **Step 2: PAN & Organization Type Verification:**\n"
            "   - Select enterprise type (Proprietorship, Partnership, Private Limited, LLP, Society, Trust).\n"
            "   - Enter **PAN**; the portal automatically validates tax filing status with the Income Tax Department database.\n\n"
            "3. **Step 3: Enterprise Details & Bank Account:**\n"
            "   - Enter enterprise name, plant/factory location, registered office address, and date of commencement of business.\n"
            "   - Enter bank account number and IFSC code.\n\n"
            "4. **Step 4: Major Activity & NIC Code Selection:**\n"
            "   - Select primary activity (**Manufacturing** or **Services**).\n"
            "   - Search and select appropriate **NIC 2-digit and 5-digit Codes** (National Industrial Classification) matching your trade.\n"
            "   - Enter number of employees and investment in plant & machinery (auto-fetched or self-declared).\n\n"
            "5. **Step 5: Final Submission & Instant Certificate:**\n"
            "   - Click **'Submit and Get Final OTP'**.\n"
            "   - Upon OTP verification, your unique permanent **Udyam Registration Number** (`UDYAM-XX-00-0000000`) is generated.\n"
            "   - Download the official **Udyam Registration Certificate** with dynamic QR code immediately.\n\n"
            "#### 🎁 Statutory Benefits for Registered MSMEs:\n"
            "- **50% Concession on BIS Certification Fees:** Micro & Small units get a statutory 50% discount on BIS marking fees and testing charges.\n"
            "- **Collateral-Free Bank Loans:** Priority sector lending and credit guarantees up to ₹5 Crores under CGTMSE.\n"
            "- **Protection Against Delayed Payments:** Buyers must pay within 45 days under the MSMED Act 2006 (interest at 3x RBI bank rate for defaults via MSME Samadhaan).\n"
            "- **Subsidies on Patents & Trademarks:** 50% to 80% fee rebate on IPR filings and GS1 barcode registrations."
        )
    },

    # 33. Restaurant Service Charge Illegality (CCPA Guidelines)
    {
        "id": "service_charge_illegality",
        "keywords": ["service charge", "restaurant service charge", "refuse service charge", "hotel bill charge"],
        "match_func": lambda q: "service charge" in q or ("restaurant" in q and "charge" in q and "bill" in q) or "hotel charge" in q,
        "standard_code": "CCPA Guidelines F. No. J-25/57/2022-CCPA",
        "title": "Illegality of Mandatory Restaurant Service Charge (CCPA Guidelines 2022)",
        "portal": "https://consumerhelpline.gov.in",
        "expected_keywords": ["Service Charge", "voluntary", "CCPA", "1915", "illegal"],
        "answer": (
            "### ⚖️ Consumer Protection Notice: Service Charge on Restaurant & Hotel Bills\n"
            "**Governing Authority:** Central Consumer Protection Authority (CCPA), Ministry of Consumer Affairs\n"
            "**Statutory Guideline:** Guidelines for Prevention of Unfair Trade Practices and Protection of Consumer Interest with regard to levy of Service Charge in Hotels/Restaurants (July 4, 2022)\n\n"
            "#### 🚫 Is Service Charge Mandatory or Legal?\n"
            "- **STRICTLY VOLUNTARY & OPTIONAL:** No hotel or restaurant can add **Service Charge** automatically or by default in the food bill.\n"
            "- A service charge is NOT a government tax (unlike GST). It is solely a tip or gratuity. Collection of any amount under the guise of service charge without voluntary consumer consent is an **unfair trade practice** under Section 2(47) of the Consumer Protection Act, 2019.\n"
            "- Hotels cannot restrict entry, refuse service, or deny reservations based on a consumer's refusal to pay service charge.\n\n"
            "#### 🛡️ What Consumers Should Do If Service Charge is Added:\n"
            "1. **Demand Removal:** Request the restaurant manager to remove the service charge from the bill before making payment.\n"
            "2. **File Instant Grievance:** Dial the National Consumer Helpline (NCH) toll-free at **1915** or WhatsApp your bill to `8800001915`.\n"
            "3. **Lodge Complaint on NCH App:** Submit a photo of the bill on the **NCH App** or consumerhelpline.gov.in.\n"
            "4. **Legal Redressal:** File a digital dispute on the **e-Daakhil Portal** (`edaakhil.nic.in`) against the restaurant for unfair trade practice and compensation."
        )
    },

    # 34. Illegal Chilling Charges above MRP (Legal Metrology Section 36)
    {
        "id": "chilling_charges_illegal_mrp",
        "keywords": ["chilling charge", "cooling charge", "charge extra", "above mrp", "cold drink extra", "chilled"],
        "match_func": lambda q: (any(k in q for k in ["chill", "cooling", "refrigerat"]) and any(k in q for k in ["charge", "mrp", "extra", "bottle", "coke", "water", "milk", "pepsi", "beer"])) or ("extra" in q and "mrp" in q) or ("above mrp" in q),
        "standard_code": "Section 36, Legal Metrology Act 2009",
        "title": "Illegality of Extra Chilling / Refrigeration Charges above MRP",
        "portal": "https://consumerhelpline.gov.in",
        "expected_keywords": ["Legal Metrology", "MRP", "chilling", "Section 36", "fine"],
        "answer": (
            "### ⚖️ Legal Metrology Guide: Charging Extra for Chilled Water, Soft Drinks or Milk\n"
            "**Governing Statute:** Section 36, Legal Metrology Act 2009 & Legal Metrology (Packaged Commodities) Rules, 2011\n"
            "**Enforcement Wing:** State Legal Metrology Department (Weights & Measures Inspectors)\n\n"
            "#### 🚫 Is It Legal for a Shopkeeper to Charge ₹2 to ₹5 Extra for 'Cooling / Chilling'?\n"
            "- **STRICTLY ILLEGAL:** Charging even 50 paise above the printed Maximum Retail Price (**MRP**) for refrigeration or cooling is a cognizable legal violation under Section 36 of the **Legal Metrology** Act.\n"
            "- The Supreme Court and National Consumer Commission have established that refrigeration is a basic retail overhead cost already factored into the dealer margin. Demanding extra money for 'cold' beverages, packaged drinking water, or milk packets is an **unfair trade practice**.\n\n"
            "#### 🚨 Statutory Penalties on Violating Retailers:\n"
            "- **First Offence:** Fine of not less than **₹25,000** on the shopkeeper/retailer.\n"
            "- **Second Offence:** Fine up to **₹50,000**.\n"
            "- **Subsequent Offences:** Fine up to **₹1,00,000** and imprisonment up to 1 year.\n\n"
            "#### 📲 How Citizens Can Report Violations:\n"
            "1. Insist on a printed cash memo showing the extra amount charged.\n"
            "2. File a complaint with the **Controller of Legal Metrology** (Weights & Measures Department) of your district.\n"
            "3. Report directly on the National Consumer Helpline at **1915** or online at [consumerhelpline.gov.in](https://consumerhelpline.gov.in)."
        )
    },

    # 35. Selling Old Unhallmarked Gold (Consumer Rights)
    {
        "id": "selling_unhallmarked_old_gold",
        "keywords": ["sell old gold", "unhallmarked gold", "sell gold without hallmark", "exchange old gold", "can i sell old gold"],
        "match_func": lambda q: ("sell" in q or "exchange" in q) and ("old gold" in q or "unhallmarked" in q or "without hallmark" in q or "without huid" in q),
        "standard_code": "BIS Hallmarking Regulations 2018 (Amended 2023)",
        "title": "Consumer Rights: Selling or Exchanging Old Unhallmarked Gold Jewellery",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["unhallmarked", "gold", "jeweller", "HUID", "legal"],
        "answer": (
            "### 👑 Consumer Guide: Selling or Exchanging Old Unhallmarked Gold Jewellery\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS), Ministry of Consumer Affairs\n"
            "**Statutory Mandate:** Mandatory Gold Hallmarking Order (Effective from April 1, 2023)\n\n"
            "#### 🛡️ Can Citizens Sell or Exchange Old Gold Without a Hallmark or 6-digit HUID?\n"
            "- **YES, 100% LEGAL & PERMITTED:** Indian consumers have the absolute legal right to sell or exchange their old, ancestral, or unhallmarked gold jewellery to any registered jeweller.\n"
            "- **Crucial Distinction:** The BIS mandatory hallmarking law applies **strictly to jewellers selling to consumers**, NOT to consumers selling to jewellers. Jewellers cannot refuse to purchase your gold simply because it lacks a 6-digit HUID.\n\n"
            "#### 🔍 How Jewellers Value Old Unhallmarked Gold:\n"
            "1. **Assaying & Karatmeter Testing:** The jeweller melts the jewellery or tests it using an X-ray Fluorescence (XRF) Karatmeter in your presence to determine net gold purity.\n"
            "2. **Valuation Based on Net Gold Content:** The payout or exchange value is calculated strictly on the tested purity (e.g. 22K 916, 18K 750, 14K 585) minus minor melting loss.\n"
            "3. **Re-Hallmarking Mandate on Jeweller:** Once the jeweller buys your old gold and refashions it into new jewellery, the *jeweller* must get it stamped with a 6-digit HUID at an Assaying and Hallmarking Centre (AHC) before selling it to any new customer.\n\n"
            "#### 📲 Consumer Tips for Safe Gold Sale:\n"
            "- Always demand an XRF Karatmeter purity test report before agreeing to melt.\n"
            "- Ensure deductions for stones, beads, and enamel are calculated accurately.\n"
            "- Report any jeweller claiming that 'government banned selling old gold' to the BIS Grievance Portal or dial **1915**."
        )
    },

    # 36. Concrete Mix Ratios & Curing (IS 456 / IS 10262)
    {
        "id": "concrete_mix_ratios_is456",
        "keywords": ["concrete mix ratio", "m20", "m25", "m15", "m10", "water cement ratio", "curing days", "ponding"],
        "match_func": lambda q: any(k in q for k in ["concrete mix", "mix ratio", "m20", "m25", "m15", "m10", "curing days", "ponding"]) and not any(w in q for w in ["juice", "sauce", "food"]),
        "standard_code": "IS 456:2000 & IS 10262:2019",
        "title": "Concrete Mix Formulations, Water-Cement Ratios & Curing Durations (IS 456)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 456", "M20", "cement", "water-cement", "curing"],
        "answer": (
            "### 🏗️ Engineering Specification: Concrete Mix Ratios, Strength & Curing (IS 456:2000)\n"
            "**Governing Standard:** **IS 456**:2000 (Plain and Reinforced Concrete - Code of Practice)\n"
            "**Mix Design Standard:** IS 10262:2019 (Concrete Mix Proportioning - Guidelines)\n\n"
            "#### 📊 Standard Concrete Mix Proportions (By Volume: Cement : Sand : Coarse Aggregate):\n"
            "| Concrete Grade | Volumetric Ratio (Cement : Sand : Aggregate) | Characteristic Compressive Strength (28 Days) | Typical Construction Application |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **M5** | 1 : 5 : 10 | 5 N/mm² (MPa) | Non-structural plain bedding, mass concrete |\n"
            "| **M7.5** | 1 : 4 : 8 | 7.5 N/mm² (MPa) | Foundation sub-base, trench leveling |\n"
            "| **M10** | 1 : 3 : 6 | 10 N/mm² (MPa) | Plain Cement Concrete (PCC) foundations, pathways |\n"
            "| **M15** | 1 : 2 : 4 | 15 N/mm² (MPa) | Pavements, compound walls, non-load bearing slabs |\n"
            "| **M20** | **1 : 1.5 : 3** | **20 N/mm² (MPa)** | **RCC roof slabs, beams, columns, staircases** |\n"
            "| **M25** | 1 : 1 : 2 | 25 N/mm² (MPa) | Heavy structural columns, cantilever beams, water tanks |\n\n"
            "#### 💧 Water-Cement (W/C) Ratio & Workability:\n"
            "- For reinforced concrete (**M20**), maximum **water-cement** ratio is **0.50 to 0.55** by weight under moderate exposure.\n"
            "- Excess water severely reduces compressive strength and causes honeycomb voids.\n"
            "- Workability (Slump): 50 mm to 100 mm for normal slab and beam casting.\n\n"
            "#### ⏳ Mandatory Curing Durations (IS 456 Clause 13.5):\n"
            "1. **Ordinary Portland Cement (OPC):** Minimum **7 days** continuous moist curing / water ponding.\n"
            "2. **Portland Pozzolana Cement (PPC) / Slag Cement:** Minimum **10 to 14 days** continuous curing (essential due to slower hydration of pozzolana).\n"
            "3. Premature cessation of curing causes up to 40% loss of structural strength and thermal shrinkage cracks."
        )
    },

    # 37. Steel Rebar Rolling Tolerances & Surface Rust (IS 1786)
    {
        "id": "steel_rebar_tolerances_is1786",
        "keywords": ["rebar tolerance", "steel tolerance", "surface rust", "mass per meter", "nominal mass"],
        "match_func": lambda q: any(k in q for k in ["rebar tolerance", "steel tolerance", "surface rust", "ribbed bar tolerance", "mass per meter"]) or ("is 1786" in q and any(w in q for w in ["tolerance", "rust", "table 2", "elongation"])),
        "standard_code": "IS 1786:2008 Table 2",
        "title": "TMT Steel Bar Rolling Mass Tolerances & Surface Rust Guidelines (IS 1786)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 1786", "Table 2", "tolerance", "mass per meter", "rust"],
        "answer": (
            "### 🏗️ Technical Guide: TMT Rebar Mass Tolerances & Surface Rust Acceptance (IS 1786)\n"
            "**Governing Standard:** **IS 1786**:2008 (High Strength Deformed Steel Bars and Wires for Concrete Reinforcement)\n\n"
            "#### 📊 Rolling Mass Tolerances on Nominal Dimensions (IS 1786 Table 2):\n"
            "| Nominal Bar Diameter (Size) | Nominal Mass per Meter (kg/m) | Permissible Batch Tolerance on Nominal Mass |\n"
            "| :--- | :--- | :--- |\n"
            "| Up to and including 10 mm (8mm, 10mm) | 8mm: 0.395 kg/m, 10mm: 0.617 kg/m | **± 7.0%** |\n"
            "| Over 10 mm up to 16 mm (12mm, 16mm) | 12mm: 0.888 kg/m, 16mm: 1.580 kg/m | **± 5.0%** |\n"
            "| Over 16 mm (20mm, 25mm, 32mm) | 20mm: 2.470 kg/m, 25mm: 3.850 kg/m | **± 3.0%** |\n\n"
            "#### 🟠 Is Surface Rust on TMT Bars Acceptable?\n"
            "- **Clause 5.2 Guidelines:** Light superficial surface **rust** that can be cleaned with a wire brush is **completely acceptable** and does NOT impair structural strength.\n"
            "- In fact, mild surface roughness created by initial oxidation slightly enhances the mechanical bond between concrete and steel.\n"
            "- **Rejection Criteria:** If rust has created deep pitting that reduces rib height or reduces the **mass per meter** below the **Table 2** negative tolerance limit, the batch must be rejected.\n\n"
            "#### ⚡ Fe 500D vs Fe 500 Mechanical Benchmarks:\n"
            "- **Yield Strength:** Min 500.0 MPa (both grades).\n"
            "- **Total Elongation:** Minimum **16.0% for Fe 500D** (vs 14.5% for Fe 500) for high seismic ductility.\n"
            "- **Tensile-to-Yield Ratio:** Min 1.12 for Fe 500D."
        )
    },

    # 38. Domestic Pressure Cookers Safety QCO (IS 2347)
    {
        "id": "pressure_cooker_safety_is2347",
        "keywords": ["pressure cooker", "is 2347", "fusible plug", "gasket release", "cooker explosion"],
        "match_func": lambda q: any(k in q for k in ["pressure cooker", "cooker", "is 2347"]) and any(k in q for k in ["safety", "standard", "isi", "fusible", "gasket", "burst", "quality", "explosion"]),
        "standard_code": "IS 2347:2017",
        "title": "Domestic Pressure Cookers Mandatory Safety QCO & Testing (IS 2347)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 2347", "fusible plug", "gasket", "burst pressure", "pressure cooker"],
        "answer": (
            "### 🍳 Safety Standard Guide: Domestic Pressure Cookers (IS 2347:2017)\n"
            "**Governing Standard:** **IS 2347**:2017 (Domestic Pressure Cookers - Specification)\n"
            "**Statutory Mandate:** Domestic Pressure Cooker (Quality Control) Order, 2020\n\n"
            "#### 🛡️ Mandatory Safety Mechanisms under IS 2347:\n"
            "1. **Weight Valve (Vent Weight):** Regulates working pressure automatically between 0.9 kg/cm² to 1.1 kg/cm² (88 to 108 kPa).\n"
            "2. **Fusible Safety Plug:** A secondary safety alloy plug in the lid that MUST melt and release steam between **120°C and 140°C** if the vent tube gets choked with food.\n"
            "3. **Gasket Release System (GRS):** If both vent weight and safety plug fail, the rubber gasket must safely deform through a lid slot to exhaust pressure downwards without lid detachment.\n"
            "4. **Hydrostatic Burst Pressure Test:** The cooker vessel must withstand **at least 3 times its normal working pressure** (minimum 300 kPa) without rupture or metal fragmentation.\n\n"
            "#### ⚠️ Consumer Hazards of Uncertified Cheap Pressure Cookers:\n"
            "- Counterfeit cookers made from recycled scrap aluminum with defective fusible plugs explode violently, causing severe third-degree steam burns and shrapnel injuries.\n"
            "- The Central Consumer Protection Authority (CCPA) and BIS routinely penalize major e-commerce platforms and local sellers for listing non-ISI pressure cookers.\n"
            "- Always verify the 7-digit CM/L license number on the base of the cooker via the **BIS Care App**."
        )
    },

    # 39. Domestic Gas Stoves Safety (IS 4246)
    {
        "id": "gas_stoves_safety_is4246",
        "keywords": ["gas stove", "is 4246", "thermal efficiency", "lpg stove", "burner"],
        "match_func": lambda q: any(k in q for k in ["gas stove", "lpg stove", "is 4246"]) and not any(w in q for w in ["water", "steel"]),
        "standard_code": "IS 4246:2017",
        "title": "Domestic LPG Gas Stoves Safety & Thermal Efficiency (IS 4246)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 4246", "thermal efficiency", "gas stove", "LPG", "gas leakage"],
        "answer": (
            "### 🔥 Statutory Safety Guide: Domestic LPG Gas Stoves (IS 4246:2017)\n"
            "**Governing Standard:** **IS 4246**:2017 (Domestic Gas Stoves for Use with Liquefied Petroleum Gases - Specification)\n"
            "**Statutory Mandate:** Mandatory BIS ISI Mark Certification under Domestic Gas Stoves QCO\n\n"
            "#### 🔍 Key Performance & Safety Benchmarks:\n"
            "1. **Thermal Efficiency:**\n"
            "   - Under **IS 4246**, each burner must have a minimum **thermal efficiency of 68.0%** to prevent excessive gas wastage and high fuel bills.\n"
            "2. **Gas Leakage & Flashback Prevention:**\n"
            "   - Gas valves and manifold tubes must withstand a pneumatic test pressure of 15 kPa with zero detectable gas leakage.\n"
            "   - Flame must burn with a stable blue cone without carbon monoxide (CO) emission exceeding 0.02% in dry products of combustion.\n"
            "3. **Toughened Glass Top Safety (for Glass-Top Models):**\n"
            "   - Glass tops must be thermally toughened conforming to thermal shock tests (withstanding 150°C temperature gradient without shattering).\n"
            "4. **Stability & Pan Support:** Pan supports must support cookware weighing up to 20 kg without tipping or bending.\n\n"
            "#### 📲 Consumer Verification:\n"
            "Look for the authentic ISI mark and 7-digit CM/L number stamped on the metal rating plate attached to the stove chassis."
        )
    },

    # 40. Safety of Toys Mandatory QCO (IS 9873)
    {
        "id": "toys_safety_is9873",
        "keywords": ["toys", "toy safety", "is 9873", "safety of toys", "toys isi mark", "feeding bottle"],
        "match_func": lambda q: (any(k in q for k in ["toy", "toys", "is 9873"]) or "feeding bottle" in q) and not any(w in q for w in ["water", "steel", "cement"]),
        "standard_code": "IS 9873 (Parts 1 to 9)",
        "title": "Safety of Toys Mandatory QCO & Chemical Limits (IS 9873)",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 9873", "toys", "lead", "phthalates", "small parts", "ISI"],
        "answer": (
            "### 🧸 Child Safety Guide: Mandatory ISI Certification for Toys (IS 9873)\n"
            "**Governing Standard:** **IS 9873** (Safety of Toys - Parts 1 to 9) & **IS 15644** (Electric Toys)\n"
            "**Statutory Mandate:** Toys (Quality Control) Order, 2020 (Mandatory ISI Mark since January 1, 2021)\n\n"
            "Under the Toys QCO, no domestic manufacturer or overseas plant can sell or import toys in India without valid BIS ISI certification.\n\n"
            "#### 🔬 Mandatory Safety Checks under IS 9873:\n"
            "1. **Part 1 (Mechanical & Physical Hazards):**\n"
            "   - **Small Parts Choking Test:** Toys for children under 3 years must not contain small parts or detachable beads that fit inside the small parts test cylinder.\n"
            "   - Sharp edges, sharp points, and pinch-point entrapment testing.\n"
            "2. **Part 2 (Flammability):** Textiles and stuffed plush toys must not propagate open flames rapidly.\n"
            "3. **Part 3 (Migration of Toxic Elements):**\n"
            "   - Strict maximum limits on toxic heavy metals in paints and plastics:\n"
            "     - **Lead (as Pb):** Maximum 90 mg/kg.\n"
            "     - **Cadmium (as Cd):** Maximum 75 mg/kg.\n"
            "     - **Arsenic (as As):** Maximum 25 mg/kg.\n"
            "     - **Mercury (as Hg):** Maximum 60 mg/kg.\n"
            "4. **Part 6 (Phthalates):** Plastic toys must not contain restricted phthalate plasticizers exceeding **0.1% by weight**.\n\n"
            "#### 🍼 Baby Feeding Bottles (IS 14625):\n"
            "- Infant feeding bottles must conform to **IS 14625** and be **BPA-Free** (Bisphenol-A free) with food-grade silicone teats.\n\n"
            "#### 📲 What Parents Must Check:\n"
            "Ensure the red **ISI mark** and 7-digit CM/L number are printed on the toy packaging. Verify the license on the **BIS Care App**."
        )
    },

    # 41. Drinking Water Stored in Copper Vessels (IS 10500 Limits)
    {
        "id": "copper_vessel_water_safety",
        "keywords": ["copper water", "copper vessel", "copper bottle", "copper toxicity", "verdigris"],
        "match_func": lambda q: "copper" in q and any(w in q for w in ["water", "bottle", "jug", "vessel", "pot", "toxicity", "verdigris"]),
        "standard_code": "IS 10500:2012 (Copper Permissible Limit)",
        "title": "Drinking Water in Copper Vessels: Health Benefits vs Heavy Metal Toxicity",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["IS 10500", "copper", "toxicity", "verdigris", "0.05 mg/L"],
        "answer": (
            "### 🏺 Health & Safety Guide: Storing Drinking Water in Copper Vessels (Tamra Jal)\n"
            "**Governing Standard:** **IS 10500**:2012 (Drinking Water Specification)\n"
            "**Statutory Limits:** Acceptable Limit for Copper ($Cu$) = **0.05 mg/L**; Permissible Limit in absence of alternate source = **1.5 mg/L**.\n\n"
            "#### 🌟 Safe Usage Guidelines:\n"
            "1. **Optimal Storage Duration:** Storing drinking water in a clean copper vessel overnight (**6 to 8 hours**) releases trace copper ions ($Cu^{2+}$) providing natural antibacterial oligodynamic action.\n"
            "2. **Excess Leaching Risk (> 24 hours):** Storing water for multiple days continuously causes copper levels to spike past the IS 10500 maximum ceiling (1.5 mg/L).\n"
            "3. **🚫 Never Store Acidic Liquids:** Never put lemon water, citrus juices, buttermilk, curd, tea, or carbonated soda in copper vessels. Acid rapidly corrodes copper, producing toxic copper verdigris ($CuSO_4$ and copper carbonate).\n\n"
            "#### ⚠️ Symptoms of Copper Toxicity:\n"
            "- Metallic taste, abdominal cramps, severe nausea, vomiting, and diarrhea.\n"
            "- Chronic copper toxicity causes Wilson's disease-like symptoms, liver cirrhosis, and kidney dysfunction.\n\n"
            "#### 🧼 Cleaning Best Practice:\n"
            "Clean copper jugs weekly using salt and tamarind or lemon rind to scrub off greenish oxide patina, then rinse thoroughly with running water before use."
        )
    },

    # 42. Allied Regulators: BEE Star Rating, WPC ETA & CDSCO
    {
        "id": "allied_certifications_bee_wpc_peso",
        "keywords": ["bee star", "energy rating", "wpc", "wpc eta", "saralsanchar", "cdsco", "medical device class", "peso"],
        "match_func": lambda q: any(k in q for k in ["bee star", "energy rating", "wpc", "wpc eta", "saralsanchar", "cdsco", "medical device class", "peso"]),
        "standard_code": "BEE / WPC / CDSCO Interoperability",
        "title": "Allied Indian Regulatory Certifications: BEE, WPC ETA, CDSCO & PESO",
        "portal": "https://www.beeindia.gov.in",
        "expected_keywords": ["BEE", "WPC", "CDSCO", "Star Rating", "PESO"],
        "answer": (
            "### 🏛️ Statutory Regulatory Guide: BEE, WPC ETA, CDSCO & PESO Standards\n"
            "In India, several apex regulatory bodies operate alongside BIS for energy efficiency, wireless devices, pharmaceuticals, and explosive safety:\n\n"
            "#### 1. ⚡ BEE Star Rating (Bureau of Energy Efficiency - Ministry of Power):\n"
            "- **Scope:** Mandatory **Star Rating** labels (1 to 5 Stars) for Frost-Free Refrigerators, Inverter Air Conditioners, Distribution Transformers, Ceiling Fans, and LED lamps.\n"
            "- **Interoperability:** Electrical appliances must possess BOTH **BIS ISI / CRS safety certification** and a valid **BEE** energy registration label before sale.\n\n"
            "#### 2. 📡 WPC ETA Approval (Wireless Planning & Coordination - DoT):\n"
            "- **Official Portal:** [saralsanchar.gov.in](https://saralsanchar.gov.in)\n"
            "- **Scope:** Mandatory Equipment Type Approval (**WPC** ETA) for all consumer devices containing **Bluetooth, Wi-Fi, or RFID** transmitters operating in de-licensed frequency bands (2.4 GHz & 5 GHz).\n"
            "- Applies to smartphones, wireless headphones, smartwatches, IoT nodes, and Wi-Fi routers imported or manufactured in India.\n\n"
            "#### 3. 🩺 CDSCO Medical Devices (Central Drugs Standard Control Organization):\n"
            "- Regulated under Medical Devices Rules 2017 into 4 risk tiers:\n"
            "  - **Class A:** Low risk (cotton, thermometers, surgical bandages).\n"
            "  - **Class B:** Low-moderate risk (syringes, needles, blood pressure monitors).\n"
            "  - **Class C:** Moderate-high risk (dialysis equipment, ventilators).\n"
            "  - **Class D:** High risk (coronary stents, heart valves, implantable pacemakers).\n\n"
            "#### 4. 🛢️ PESO Approval (Petroleum and Explosives Safety Organization):\n"
            "- Mandatory safety inspection and approval for LPG cylinders (IS 3196), auto-CNG fuel cylinders, cryogenic tanks, and hazardous chemical pipelines."
        )
    },

    # 43. e-Daakhil Consumer Court Online & CPA 2019
    {
        "id": "cpa_edaakhil_consumer_court",
        "keywords": ["edaakhil", "e-daakhil", "file consumer court", "consumer case online", "no refund exchange", "e-commerce fake"],
        "match_func": lambda q: any(k in q for k in ["edaakhil", "e-daakhil", "file consumer court", "consumer case online", "no refund exchange", "e-commerce fake", "amazon fake"]),
        "standard_code": "Consumer Protection Act 2019 & e-Daakhil Portal",
        "title": "How to File Online Consumer Court Cases on e-Daakhil (edaakhil.nic.in)",
        "portal": "https://edaakhil.nic.in",
        "expected_keywords": ["e-Daakhil", "CPA 2019", "consumer court", "lawyer", "1915"],
        "answer": (
            "### ⚖️ Citizen Action Guide: Filing Online Consumer Court Cases on e-Daakhil\n"
            "**Official Portal:** [edaakhil.nic.in](https://edaakhil.nic.in)\n"
            "**Statutory Act:** Consumer Protection Act, 2019 (Act No. 35 of 2019)\n\n"
            "#### 🛡️ Can Citizens File a Consumer Case Without Hiring a Lawyer?\n"
            "- **YES, 100%:** Under **CPA 2019**, any consumer can draft and file their own case online via **e-Daakhil** without hiring an advocate.\n"
            "- **Jurisdiction Limits:**\n"
            "  - **District Commission:** Claims up to **₹50 Lakhs**.\n"
            "  - **State Commission:** Claims between **₹50 Lakhs and ₹2 Crores**.\n"
            "  - **National Commission (NCDRC):** Claims exceeding **₹2 Crores**.\n\n"
            "#### 💻 Step-by-Step Filing Process on edaakhil.nic.in:\n"
            "1. **Registration:** Register as a citizen consumer using your Aadhaar number, email, and mobile OTP.\n"
            "2. **Draft Petition:** Prepare a concise statement of facts outlining the purchase, defect/deficiency, financial loss, and compensation demanded.\n"
            "3. **Upload Evidence:** Upload scanned PDF copies of retail invoices, warranty cards, photos of defective/fake goods, emails, and legal notice.\n"
            "4. **Pay Nominal Court Fee:** Pay minimal government filing fee online (Free for claims up to ₹5 Lakhs; nominal ₹200–₹1,000 for higher slabs).\n"
            "5. **Digital Tracking:** Track court admission, notices issued to the seller/manufacturer, and hearing dates online.\n\n"
            "#### 🚫 Are 'No Refund / No Exchange' Boards Legal?\n"
            "- **STRICTLY ILLEGAL:** The National Commission has ruled that stamping 'Goods once sold will not be taken back' on bills or storefronts is an unfair trade practice. A consumer has the statutory right to refund or replacement for defective products."
        )
    },

    # 44. Dairy Milk Shop & Booth (Paala Dukanam / FSSAI FoSCoS & Milk Safety)
    {
        "id": "dairy_milk_shop_fssai",
        "keywords": ["paala dukanam", "pala dukanam", "paalu dukanam", "milk shop", "dairy booth", "doodh ki dukan", "doodh dairy", "paal kadai", "haalu angadi", "paala vyaparam", "milk booth", "dairy parlour"],
        "match_func": lambda q: any(k in q for k in ["paala dukanam", "pala dukanam", "paalu dukanam", "milk shop", "dairy booth", "doodh ki dukan", "doodh dairy", "paal kadai", "haalu angadi", "paala vyaparam", "milk booth", "dairy parlour", "milk parlour", "dairy shop", "paala centre", "doodh centre", "paala business", "doodh vyapar"]) or (("milk" in q or "paala" in q or "doodh" in q or "dairy" in q) and any(w in q for w in ["shop", "booth", "dukan", "kadai", "angadi", "store", "counter", "parlour", "centre", "center", "vyaparam", "retail"])),
        "standard_code": "FSSAI Dairy Regulations & IS 1224",
        "title": "Milk Shop & Dairy Booth Compliance Guide: FSSAI FoSCoS Registration, Milk Standards & Quality Testing",
        "portal": "https://foscos.fssai.gov.in",
        "expected_keywords": ["milk", "FSSAI", "FoSCoS", "lactometer", "fat", "SNF", "cold chain"],
        "answer": (
            "### 🥛 Statutory Regulatory Guide: Milk Shop & Dairy Booth Compliance (FSSAI & IS 1224)\n"
            "**Statutory Authority:** Food Safety and Standards Authority of India (FSSAI) & Bureau of Indian Standards (BIS)\n"
            "**Official Regulatory Portal:** [FSSAI FoSCoS Portal (foscos.fssai.gov.in)](https://foscos.fssai.gov.in)\n\n"
            "#### 📋 FSSAI FoSCoS Registration vs State License Requirements:\n"
            "1. **Petty Milk Retailer / Small Booth (Turnover up to ₹12 Lakhs/year OR handling up to 500 Litres/day):**\n"
            "   - Must obtain **FSSAI Basic Registration (Form A)**.\n"
            "   - Nominal statutory fee: **₹100 per year**.\n"
            "   - Generated online via [FoSCoS](https://foscos.fssai.gov.in) with Aadhaar and basic electricity bill/property proof.\n"
            "2. **Medium & Commercial Dairy Shop (Turnover ₹12 Lakhs to ₹20 Crores OR handling 501 to 50,000 Litres/day):**\n"
            "   - Must obtain **FSSAI State License (Form B)**.\n"
            "   - Statutory fee: **₹2,000 to ₹5,000 per year**.\n"
            "   - Requires layout plan, equipment list, medical fitness certificates of food handlers, and water testing report (IS 10500).\n"
            "3. **Mandatory Display:** The **14-digit FSSAI Registration / License Number** must be displayed prominently on the shop storefront signboard, billing receipts, and milk delivery containers.\n\n"
            "#### 📊 Mandatory Milk Quality Benchmarks (FSSAI Dairy Regulations):\n"
            "| Milk Variety | Minimum Milk Fat (% by mass) | Minimum Solids-Not-Fat (% SNF) | Primary Quality Test |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| Cow Milk (Standardized) | Minimum 3.2% | Minimum 8.3% | IS 1224 Gerber Fat / Lactometer SNF |\n"
            "| Buffalo Milk | Minimum 6.0% | Minimum 9.0% | IS 1224 Gerber Fat / Lactometer SNF |\n"
            "| Toned Milk | Minimum 3.0% | Minimum 8.5% | Gerber Centrifugation Test |\n"
            "| Double Toned Milk | Minimum 1.5% | Minimum 9.0% | Gerber Centrifugation Test |\n"
            "| Full Cream Milk | Minimum 6.0% | Minimum 9.0% | IS 1224 (Part 1) Gerber Method |\n"
            "| Storage Temperature | Strictly <= 4.0 °C | Continuous Cold Chain | Calibrated Digital Thermometer |\n"
            "| Adulterants (Urea/Detergent/Starch) | Completely Absent (0%) | Zero Tolerance | FSSAI DART Rapid Chemical Strips |\n\n"
            "#### 🧪 Mandatory Quality Control & In-Shop Testing Facilities:\n"
            "- **Lactometer SNF Testing:** Pure cow/buffalo milk must show a lactometer reading of **28 to 32 at 20°C**. A reading below 26 indicates deliberate water adulteration.\n"
            "- **Gerber Fat Test Apparatus (IS 1224 Part 1):** Centrifuge machine, butyrometers, and standard sulfuric acid / isoamyl alcohol for accurate butterfat measurement.\n"
            "- **Zero Tolerance for Chemical Adulterants:** Regular screening using FSSAI DART (Detect Adulteration with Rapid Test) kits for synthetic milk, urea, detergent, caustic soda, neutralizers, and starch.\n"
            "- **Cold Chain Storage:** High-efficiency commercial chillers maintaining milk temperature strictly below **4°C** to prevent microbial spoilage and curdling.\n\n"
            "#### 🛡️ Consumer Rights & Adulteration Reporting:\n"
            "- If milk smells soapy, has a bitter chemical aftertaste, turns yellowish upon boiling, or fails the lactometer check, consumers can report the vendor directly on the **FSSAI Food Safety Connect App** or call the National Consumer Helpline at **1915**."
        )
    },

    # 45. Cement Retail Store & Godown Storage (Simantu Dukanam / IS 269 & IS 1489)
    {
        "id": "cement_retail_shop_bis",
        "keywords": ["simantu dukanam", "cement dukanam", "cement shop", "cement ki dukan", "cement dealership", "cement store", "cement dealer", "simantu vyaparam"],
        "match_func": lambda q: any(k in q for k in ["simantu dukanam", "cement dukanam", "cement shop", "cement ki dukan", "cement dealership", "cement store", "cement dealer", "simantu vyaparam", "cement retail"]) or (("cement" in q or "simantu" in q or "siminti" in q) and any(w in q for w in ["shop", "dukan", "dealer", "dealership", "store", "retail", "godown", "depot", "vyaparam"])),
        "standard_code": "IS 269 / IS 1489 & Cement Quality Control Order",
        "title": "Cement Retail Store & Dealership Compliance Guide: Mandatory BIS ISI Mark & Storage Standards",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["cement", "ISI", "IS 269", "IS 1489", "storage", "lumps", "bag"],
        "answer": (
            "### 🏗️ Statutory Regulatory Guide: Cement Retail Store & Godown Storage (IS 269 & IS 1489)\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS) & Department for Promotion of Industry and Internal Trade (DPIIT)\n"
            "**Statutory Order:** Mandatory Cement (Quality Control) Order under Section 16 & Section 29, BIS Act 2016\n"
            "**Official Certification Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 📋 Mandatory BIS ISI Certification Requirements for Retail Sale:\n"
            "1. **Zero Uncertified Cement:** Under the Cement QCO, NO retailer, dealer, or distributor can legally stock, display, or sell cement without the authentic **BIS ISI Mark** and a valid 7 or 8-digit **CM/L license number**.\n"
            "2. **Governing Indian Standards:**\n"
            "   - **IS 269:2015:** Ordinary Portland Cement (OPC 33, 43, and 53 Grades).\n"
            "   - **IS 1489 (Part 1 & 2):2015:** Portland Pozzolana Cement (PPC - Flyash / Calcined Clay based).\n"
            "   - **IS 455:2015:** Portland Slag Cement (PSC).\n"
            "3. **Statutory Bag Declarations:** Every 50 kg bag must clearly print the ISI logo, CM/L number, brand name, grade/type, week number and year of manufacture (e.g. `W-38, Y-2026`), and net weight (50 kg ± 1%).\n\n"
            "#### 🧱 Statutory Godown Storage & Moisture Protection Norms:\n"
            "- **Raised Wooden Pallets:** Cement bags MUST be stacked on dry wooden planks or pallets elevated at least **150 mm (15 cm)** above the floor to avoid capillary ground dampness.\n"
            "- **Wall Clearance:** Maintain a minimum distance of **600 mm (60 cm)** between cement stacks and exterior godown walls.\n"
            "- **Stack Height Limit:** Do NOT stack bags higher than **10 bags high** to avoid compaction lump formation.\n"
            "- **FIFO (First-In, First-Out):** Oldest stock must be sold first. Cement stored beyond **90 days (3 months)** loses 20–30% of its compressive strength and must be retested for 28-day strength before structural use.\n\n"
            "#### ⚠️ Consumer Quality Checks & Red Flags:\n"
            "- **Hard Lumps:** If a cement bag contains hard lumps that cannot be pulverized between fingertips, atmospheric hydration has ruined the cement; reject immediately.\n"
            "- **Smooth vs Gritty Feel:** Genuine cement feels silky and cool when touched; a gritty feel indicates adulteration with stone dust or river sand.\n"
            "- **Verify on BIS Care App:** Consumers and builders can verify the manufacturer's active CM/L license number on the **BIS Care App** before purchasing bulk bags."
        )
    },

    # 46. TMT Steel Rebar Retail Store (Sariya Dukanam / IS 1786)
    {
        "id": "steel_tmt_retail_shop_bis",
        "keywords": ["sariya dukanam", "inumu dukanam", "sariya ki dukan", "steel shop", "tmt shop", "iron hardware", "sariya dealer", "iron shop", "tmt dealership"],
        "match_func": lambda q: any(k in q for k in ["sariya dukanam", "inumu dukanam", "sariya ki dukan", "steel shop", "tmt shop", "iron hardware", "sariya dealer", "iron shop", "tmt dealership", "sariya vyaparam"]) or (("sariya" in q or "tmt" in q or "rebar" in q or "inumu" in q) and any(w in q for w in ["shop", "dukan", "dealer", "dealership", "store", "retail", "hardware", "vyaparam", "godown"])),
        "standard_code": "IS 1786:2008 & Steel & Steel Products (QCO)",
        "title": "TMT Steel Rebar Retail Store & Dealer Compliance Guide: IS 1786 Certification & Quality Checks",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["TMT", "sariya", "IS 1786", "Fe 500D", "MTC", "tolerance", "embossed"],
        "answer": (
            "### 🏗️ Statutory Regulatory Guide: TMT Steel Rebar Store & Dealer Compliance (IS 1786)\n"
            "**Governing Authority:** Ministry of Steel & Bureau of Indian Standards (BIS)\n"
            "**Statutory Order:** Mandatory Steel and Steel Products (Quality Control) Order under Section 16 & 29 of the BIS Act 2016\n"
            "**Official Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 📋 Mandatory ISI Certification & Embossing on Every Rebar:\n"
            "1. **Governing Standard:** **IS 1786:2008** (High strength deformed steel bars and wires for concrete reinforcement).\n"
            "2. **Mandatory Embossed Markings:** Under IS 1786 Clause 12, EVERY single TMT rebar must feature permanently hot-rolled embossed markings at regular intervals (<= 1.5 metres):\n"
            "   - Authentic **ISI Mark** logo\n"
            "   - Manufacturer's registered **Brand / Trade Mark**\n"
            "   - Strength grade (e.g. **500D**, **550D**)\n"
            "   - Bar diameter in millimeters (e.g. `12`, `16`, `20`)\n"
            "   *Bars without embossed rolling marks are uncertified, rerolled scrap steel and strictly illegal to sell.*\n\n"
            "3. **Mill Test Certificate (MTC):** Retail steel dealers MUST furnish a manufacturer-endorsed Mill Test Certificate for each consignment stating the cast/heat number, chemical composition (C <= 0.25%, S <= 0.040%, P <= 0.040%), and mechanical yield strength.\n\n"
            "#### ⚖️ Weight per Metre Rolling Tolerances (IS 1786 Table 2):\n"
            "- Up to and including 10 mm diameter: **± 7.0%** permissible deviation per metre run.\n"
            "- Over 10 mm up to and including 16 mm: **± 5.0%** permissible deviation.\n"
            "- Over 16 mm diameter: **± 3.0%** permissible deviation.\n"
            "- Under-gauge bars exceeding negative tolerances weaken buildings and constitute fraudulent trade.\n\n"
            "#### 🔍 Storage & Quality Verifications:\n"
            "- Store rebar bundles off the ground on raised dry supports to prevent excessive rusting, pitting corrosion, and oil/mud contamination.\n"
            "- Verify the 7-digit CM/L license number embossed on the bundle tags using the **BIS Care App**."
        )
    },

    # 47. Gold Jewellery Retail Store (Bangaaram Dukanam / BIS Hallmarking & HUID)
    {
        "id": "gold_jewellery_shop_hallmark",
        "keywords": ["bangaaram dukanam", "bangaram dukanam", "sona ki dukan", "thangam kadai", "jewellery shop", "gold shop", "jeweller store", "bangaaram vyaparam", "sona chandi dukan"],
        "match_func": lambda q: any(k in q for k in ["bangaaram dukanam", "bangaram dukanam", "sona ki dukan", "thangam kadai", "jewellery shop", "gold shop", "jeweller store", "bangaaram vyaparam", "sona chandi dukan", "jewellery store"]) or (("gold" in q or "bangaaram" in q or "sona" in q or "thangam" in q or "jeweller" in q) and any(w in q for w in ["shop", "dukan", "store", "kadai", "showroom", "outlet", "retail", "vyaparam"])),
        "standard_code": "IS 1417 & Mandatory BIS Hallmarking Order",
        "title": "Gold Jewellery Retail Store Compliance Guide: Mandatory BIS Hallmarking, 6-Digit HUID & Consumer Rights",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["hallmarking", "HUID", "gold", "IS 1417", "916", "22K", "BIS Care"],
        "answer": (
            "### 🪙 Statutory Regulatory Guide: Gold Jewellery Retail Store & Hallmarking (IS 1417)\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS) & Department of Consumer Affairs\n"
            "**Statutory Mandate:** Hallmarking of Gold Jewellery and Gold Artefacts Order under Section 14, 15 & 16, BIS Act 2016\n"
            "**Official Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 📋 Mandatory Retail Jeweller Registration:\n"
            "1. **Zero-Fee Lifetime Registration:** Every jeweller selling gold jewellery or artefacts MUST be registered with BIS on [Manakonline](https://www.manakonline.in). For micro-jewellers, registration is completely free of charge.\n"
            "2. **Strict Ban on Unhallmarked Gold:** Under the Hallmarking Order, selling unhallmarked gold jewellery in notified districts across India is a cognizable legal offence carrying statutory penalties.\n\n"
            "#### 🔍 The Mandatory 3 Hallmarking Symbols on Every Gold Article:\n"
            "1. **BIS Triangular Mark:** The official logo of the Bureau of Indian Standards.\n"
            "2. **Purity / Fineness Grade:**\n"
            "   - **24K999:** 99.9% Pure Gold\n"
            "   - **22K916:** 91.6% Pure Gold (Standard for bridal & daily jewellery)\n"
            "   - **20K833:** 83.3% Pure Gold\n"
            "   - **18K750:** 75.0% Pure Gold (Standard for diamond-studded jewellery)\n"
            "   - **14K585:** 58.5% Pure Gold\n"
            "3. **6-Digit Alphanumeric HUID (Hallmark Unique Identification):** A unique laser-engraved code (e.g. `AB1234`) assigned by an accredited Assaying and Hallmarking Centre (AHC).\n\n"
            "#### ⚖️ Mandatory Counter Facilities & Consumer Rights:\n"
            "- **10x Magnifying Glass:** Jewellers MUST provide a 10x magnifying glass or digital viewer on the sales counter for consumers to inspect the HUID.\n"
            "- **Statutory Hallmarking Fee:** Fixed at **₹45 + GST per gold article**.\n"
            "- **Itemized Invoice:** Retail bill must declare gross weight, net gold weight, purity grade, and exact 6-digit HUID code.\n"
            "- **Selling Old Gold:** Consumers can legally sell or exchange old unhallmarked gold jewellery to any registered jeweller without deduction of hallmarking penalties.\n"
            "- **Instant Verification:** Consumers can tap **'Verify HUID'** on the **BIS Care App** to verify jeweller registration, AHC details, and hallmarking date before making payment."
        )
    },

    # 29. 4-Point Consumer Safety Checklist
    {
        "id": "consumer_safety_checklist",
        "keywords": ["safety checklist", "4-point", "4 point safety checklist", "checklist before buying", "inspect before buying"],
        "match_func": lambda q: any(k in q for k in ["4-point safety checklist", "4 point safety checklist", "safety checklist"]) or ("checklist" in q and any(w in q for w in ["consumer", "inspect", "buying", "packaged food", "electrical", "gold"])),
        "standard_code": "BIS & FSSAI Consumer Protection Framework",
        "title": "The Statutory 4-Point Safety Checklist for Indian Consumers (Food, Electronics & Gold)",
        "portal": "https://www.bis.gov.in",
        "expected_keywords": ["ISI mark", "CM/L", "HUID", "FSSAI", "expiry", "BIS Care"],
        "answer": (
            "### 🛡️ The Mandatory 4-Point Safety Checklist for Indian Consumers\n"
            "**Governing Framework:** Bureau of Indian Standards (BIS Act 2016), FSSAI (FSS Act 2006) & Legal Metrology Act 2009\n"
            "**Consumer Verification Mobile App:** **BIS Care Mobile App** & **FSSAI Food Safety Connect**\n\n"
            "Before purchasing packaged food, home electrical appliances, or gold jewellery, every Indian citizen must verify this statutory 4-point safety checklist:\n\n"
            "#### 1. ⚡ Electrical Appliances, Helmets & Building Materials (The ISI Mark & CM/L Number):\n"
            "- **Authentic ISI Mark:** Look for the rectangular ISI logo. An ISI mark WITHOUT a license number is counterfeit and illegal!\n"
            "- **7 or 8-Digit CM/L Number:** Every genuine ISI product must display `CM/L-XXXXXXX` directly below or beside the ISI mark.\n"
            "- **BIS Care App Verification:** Open the **BIS Care App**, select **'Verify License Details' (Verify CM/L)**, and enter the license number to verify the genuine manufacturer name, factory address, and validity.\n\n"
            "#### 2. 🍲 Packaged Foods & Beverages (FSSAI 14-Digit License & Expiry):\n"
            "- **14-Digit FSSAI License Number:** Every packaged food item must display a valid 14-digit license/registration number (e.g. `100XXXXXXXXXXX`) alongside the official FSSAI logo.\n"
            "- **Expiry / Best-Before Date:** Strictly check the manufacturing date, 'Expiry Date' or 'Best Before Date'. Selling expired food is a punishable offense under FSS Act Section 59.\n"
            "- **Mandatory Food Safety Marks:** Look for the green vegetarian or brown non-vegetarian dot symbol, +F logo for fortified foods, and Jaivik Bharat logo for organic foods.\n\n"
            "#### 3. 🪙 Gold & Silver Jewellery (The 3-Piece Hallmarking & HUID Code):\n"
            "- **Triangular BIS Hallmark Logo:** Official BIS hallmark stamp indicating verified purity.\n"
            "- **Purity Grade / Karat:** Clearly stamped (e.g., `22K916` for 22 Karat 91.6% pure gold, `18K750` for 18 Karat).\n"
            "- **6-Digit Alphanumeric HUID:** A unique laser-engraved code (e.g., `AB1234`). Verify it instantly on the **BIS Care App** under **'Verify HUID'** to confirm purity, assaying centre, and registration.\n\n"
            "#### 4. ⚖️ Fair Pricing & Grievance Redressal (MRP & Consumer Rights):\n"
            "- **No Overcharging Above MRP:** Shopkeepers, airports, and multiplexes cannot legally charge above Maximum Retail Price (MRP) under Legal Metrology Rule 18.\n"
            "- **Grievance Helplines:** Report fake ISI marks on the **BIS Care App**, adulterated food on **FSSAI Food Safety Connect**, or dial the **National Consumer Helpline toll-free at 1915**."
        )
    },

    # 47. BIS Scheme-IV (Certificate of Conformity - CoC)
    {
        "id": "scheme_iv_coc",
        "keywords": ["scheme 4", "scheme-4", "scheme iv", "scheme-iv", "certificate of conformity", "coc"],
        "match_func": lambda q: bool(re.search(r'\b(scheme\s*[-–]?\s*(?:4|iv)|certificate\s*of\s*conformity|coc\b)\b', q)) and not any(w in q for w in ["fire", "water", "juice", "cement"]),
        "standard_code": "BIS Scheme-IV (Certificate of Conformity)",
        "title": "BIS Scheme-IV: Certificate of Conformity (CoC) Batch-Wise Certification",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["Scheme-IV", "Certificate of Conformity", "CoC", "batch", "inspection"],
        "answer": (
            "### 📜 Statutory Guide: BIS Scheme-IV (Certificate of Conformity - CoC)\n"
            "**Governing Authority:** Bureau of Indian Standards (BIS) under BIS (Conformity Assessment) Regulations, 2018\n"
            "**Official Certification Portal:** [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 🔍 Key Features of Scheme-IV CoC:\n"
            "1. **Governing Scope:** Applicable for commodities, raw materials, or equipment where continuous regular licensing (Scheme-I ISI Mark) is not feasible, such as batch-wise consignments, imported raw materials, specialized high-voltage machinery, or government project tenders.\n"
            "2. **Batch-Wise Certification:** Unlike a standard annual license, a **Certificate of Conformity (CoC)** is granted specifically for an identified batch, quantity, or consignment.\n"
            "3. **Physical Lot Inspection & Sampling:** BIS inspecting officers draw representative samples directly from the identified consignment for testing in a BIS-recognized NABL laboratory.\n"
            "4. **Grant of Certificate:** Upon receiving passing test reports confirming compliance with the relevant Indian Standard, a unique **Certificate of Conformity** is issued for that specific batch."
        )
    },

    # 48. BIS Certification Fee Structure & Schedules
    {
        "id": "bis_fee_structure",
        "keywords": ["application fee", "inspection charges", "marking fee", "annual fee", "testing charges", "minimum annual marking fee", "marking fees"],
        "match_func": lambda q: bool(re.search(r'\b(application\s*fee|inspection\s*charges?|marking\s*fees?|annual\s*marking\s*fee|fee.*structure.*bis|minimum\s*annual\s*marking)\b', q)),
        "standard_code": "BIS (Conformity Assessment) Regulations 2018 - Fee Schedule",
        "title": "BIS Certification Fee Structure: Application, Inspection, and Marking Fees",
        "portal": "https://www.manakonline.in",
        "expected_keywords": ["application fee", "inspection", "marking fee", "MSME", "Udyam", "Bharatkosh"],
        "answer": (
            "### 💳 Official Statutory Guide: BIS Certification Fee Structure & Schedules\n"
            "**Governing Regulation:** BIS (Conformity Assessment) Regulations, 2018 (Schedule II - Fees)\n"
            "**Payment Portal:** [Bharatkosh (Non-Tax Receipt Portal)](https://bharatkosh.gov.in) via [BIS Manakonline](https://www.manakonline.in)\n\n"
            "#### 💰 Statutory Fee Components under Scheme-I (ISI Mark):\n"
            "1. **Application Fee:** ₹1,000 (Non-refundable) payable at the time of online application submission on Manakonline.\n"
            "2. **Preliminary Factory Audit / Inspection Charges:** ₹7,000 per man-day of factory inspection plus travel and boarding expenses of BIS inspecting officers.\n"
            "3. **Independent Sample Testing Charges:** Borne by the applicant directly at rates prescribed by BIS or recognized NABL test laboratories.\n"
            "4. **Minimum Annual Marking Fee:** Ranges from ₹12,000 to ₹1,00,000+ per annum depending on the product standard classification, volume of production, and unit value.\n\n"
            "#### 🏷️ MSME, Start-up & Women Entrepreneur Concessions:\n"
            "- **50% Concession:** Micro Enterprises holding valid **Udyam** registration receive a statutory **50% discount** on the minimum annual **marking fee**.\n"
            "- **20% Concession:** Small Enterprises receive a **20% discount** on minimum annual marking fees.\n"
            "- **Special Incentives:** Women-owned enterprises and DPIIT-recognized Startups are eligible for special fee rebates and priority processing."
        )
    }
]


class BISStatutoryTopicsService:
    """Service to resolve complex statutory BIS and consumer protection questions."""

    def resolve_statutory_topic(self, query: str, language: str = "en") -> Optional[Dict[str, Any]]:
        q_lower = query.lower().strip()

        for topic in STATUTORY_TOPICS_REGISTRY:
            if topic["match_func"](q_lower):
                return {
                    "id": topic["id"],
                    "standard_code": topic["standard_code"],
                    "title": topic["title"],
                    "portal": topic["portal"],
                    "answer": topic["answer"],
                    "expected_keywords": topic.get("expected_keywords", [])
                }

        return None


bis_statutory_topics_service = BISStatutoryTopicsService()
