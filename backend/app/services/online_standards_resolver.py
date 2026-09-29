import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from app.services.pdf_table_parser import ParsedChunk
from app.services.vector_store import vector_store_service
from app.core.database import register_standard_db, get_standard_by_code_db

logger = logging.getLogger(__name__)

# Master Official Government Portals Registry
OFFICIAL_GOV_PORTALS = {
    "NSWS": {
        "name": "National Single Window System (NSWS)",
        "url": "https://www.nsws.gov.in",
        "description": "Government of India's single digital platform for all central and state business approvals, clearances, and licenses."
    },
    "BIS_MANAKONLINE": {
        "name": "BIS Manakonline Portal",
        "url": "https://www.manakonline.in",
        "description": "Official portal for Product Certification (ISI Mark), Management Systems (ISO 9001/14001/22000), Hallmarking, and Standards lookup."
    },
    "BIS_CRS": {
        "name": "BIS Compulsory Registration Scheme (CRS)",
        "url": "https://www.crsbis.in",
        "description": "MeitY/BIS mandatory registration portal for electronics, IT goods, and secondary lithium-ion cells/batteries."
    },
    "FSSAI_FOSCOS": {
        "name": "Food Safety Compliance System (FoSCoS - FSSAI)",
        "url": "https://foscos.fssai.gov.in",
        "description": "Statutory portal for Food Business Operator (FBO) Registration, State License, Central License, and annual returns."
    },
    "MSME_UDYAM": {
        "name": "Udyam Registration Portal (Ministry of MSME)",
        "url": "https://udyamregistration.gov.in",
        "description": "Official, free-of-cost, zero-paperwork government portal for Micro, Small & Medium Enterprise (MSME) registration."
    },
    "GST_PORTAL": {
        "name": "Goods and Services Tax (GST) Portal (CBIC)",
        "url": "https://www.gst.gov.in",
        "description": "Mandatory tax registration for businesses exceeding turnover thresholds (Rs. 20/40 Lakhs) or interstate trade."
    },
    "CDSCO_SUGAM": {
        "name": "CDSCO SUGAM Online Licensing (Drugs & Cosmetics)",
        "url": "https://cdsco.gov.in",
        "description": "Central Drugs Standard Control Organization portal for Pharmacy Drug Licenses, Medical Devices, and Cosmetics import/manufacture."
    },
    "PESO": {
        "name": "Petroleum and Explosives Safety Organization (PESO)",
        "url": "https://peso.gov.in",
        "description": "Statutory approvals for Petrol Bunks, CNG Stations, LPG Storage, Explosives, and Pressure Vessels."
    },
    "LEGAL_METROLOGY": {
        "name": "e-Measure Portal (Department of Consumer Affairs)",
        "url": "https://e-measure.gov.in",
        "description": "Mandatory verification and stamping of electronic weighing scales, fuel dispensers, and packaged commodity labeling."
    },
    "DGFT": {
        "name": "Directorate General of Foreign Trade (DGFT)",
        "url": "https://www.dgft.gov.in",
        "description": "Issuance of 10-digit Importer-Exporter Code (IEC) for international trade."
    },
    "SPCB_CPCB": {
        "name": "Central & State Pollution Control Board (CPCB / SPCB)",
        "url": "https://cpcb.nic.in",
        "description": "Consent to Establish (CTE) and Consent to Operate (CTO) under Water and Air Pollution Prevention Acts."
    },
    "NCH_CONSUMER": {
        "name": "National Consumer Helpline (Department of Consumer Affairs)",
        "url": "https://consumerhelpline.gov.in",
        "description": "Official citizen grievance portal and toll-free helpline (1915) for substandard goods, weight fraud, and consumer disputes."
    }
}

# Master ISO to Harmonized Indian Standards (IS/ISO) Knowledge Base
ISO_STANDARDS_GOV_REGISTRY: Dict[str, Dict[str, Any]] = {
    "9001": {
        "iso_code": "ISO 9001:2015",
        "is_code": "IS/ISO 9001:2015",
        "title": "Quality Management Systems (QMS) - Requirements",
        "domains": ["quality", "qms", "iso 9001", "iso9001", "process control", "customer satisfaction", "iso certificate"],
        "department": "Management & Systems Department (MSD 02)",
        "cert_scheme": "BIS Management Systems Certification Scheme (MSCD) under Section 13, BIS Act 2016",
        "portal_url": "https://www.manakonline.in",
        "statutory_act": "Bureau of Indian Standards (Conformity Assessment) Regulations",
        "summary": "International and National standard specifying requirements for a Quality Management System based on Plan-Do-Check-Act (PDCA) and risk-based thinking.",
        "key_clauses": [
            "Clause 4.0: Context of the Organization (Internal & External issues, Scope of QMS)",
            "Clause 5.0: Leadership & Customer Focus (Quality Policy & Responsibilities)",
            "Clause 6.0: Planning (Actions to address risks and opportunities, Quality Objectives)",
            "Clause 7.0: Support (Resources, Competence, Awareness, Documented Information)",
            "Clause 8.0: Operation (Operational Planning, Control of Externally Provided Processes)",
            "Clause 9.0: Performance Evaluation (Internal Audit, Management Review)",
            "Clause 10.0: Improvement (Nonconformity and Corrective Action)"
        ],
        "steps": [
            "1. Conduct Gap Analysis against IS/ISO 9001:2015 requirements.",
            "2. Establish Quality Manual, Standard Operating Procedures (SOPs), and Quality Objectives.",
            "3. Conduct at least one complete cycle of Internal Audits and Management Review.",
            "4. Apply online on the [BIS Manakonline Portal](https://www.manakonline.in) under Management System Certification.",
            "5. Undergo Stage 1 (Documentation Audit) and Stage 2 (Implementation Audit) by BIS / NABCB-accredited Auditors.",
            "6. Receive 3-Year ISO 9001 Certificate with annual surveillance audits."
        ]
    },
    "14001": {
        "iso_code": "ISO 14001:2015",
        "is_code": "IS/ISO 14001:2015",
        "title": "Environmental Management Systems (EMS) - Requirements with Guidance for Use",
        "domains": ["environment", "ems", "iso 14001", "iso14001", "carbon", "waste management", "pollution control"],
        "department": "Environment & Ecology Department (EED / MSD 04)",
        "cert_scheme": "BIS EMS Certification Scheme & State Pollution Control Board Green Credit Alignment",
        "portal_url": "https://www.manakonline.in",
        "statutory_act": "Environment (Protection) Act 1986 & BIS Act 2016",
        "summary": "Establishes environmental aspects, legal compliance evaluation, waste minimization, carbon reduction, and emergency preparedness.",
        "key_clauses": [
            "Clause 6.1.2: Environmental Aspects & Impacts Identification",
            "Clause 6.1.3: Compliance Obligations (Water Act, Air Act, Hazardous Waste Rules)",
            "Clause 8.2: Emergency Preparedness and Response",
            "Clause 9.1.2: Evaluation of Environmental Compliance"
        ],
        "steps": [
            "1. Identify environmental aspects, emissions, and hazardous waste streams in operations.",
            "2. Ensure zero statutory non-compliance under SPCB Consent to Operate (CTO).",
            "3. Apply on [BIS Manakonline](https://www.manakonline.in) for IS/ISO 14001 certification.",
            "4. Complete Stage 1 & Stage 2 audits for grant of 3-year EMS license."
        ]
    },
    "22000": {
        "iso_code": "ISO 22000:2018",
        "is_code": "IS/ISO 22000:2018",
        "title": "Food Safety Management Systems (FSMS) - Requirements for Any Organization in the Food Chain",
        "domains": ["fsms", "iso 22000", "iso22000", "haccp", "iso food safety", "is/iso 22000", "iso 22000 certification"],
        "department": "Food & Agriculture Department (FAD 15 / MSD)",
        "cert_scheme": "BIS FSMS Certification Scheme & FSSAI Category Harmonization",
        "portal_url": "https://foscos.fssai.gov.in",
        "statutory_act": "Food Safety and Standards Act 2006 (FSSAI) & BIS Act 2016",
        "summary": "Combines ISO 9001 management principles with HACCP (Hazard Analysis and Critical Control Points) and prerequisite programmes (PRPs) to guarantee safe food across the entire supply chain.",
        "key_clauses": [
            "Clause 8.2: Prerequisite Programmes (PRPs) per ISO/TS 22002 series",
            "Clause 8.5: Hazard Control Plan (HACCP / OPRP determination)",
            "Clause 8.7: Control of Monitoring and Measuring Devices (Temperature, pH)",
            "Clause 8.9: Control of Product and Process Non-conformities (Recall & Traceability)"
        ],
        "steps": [
            "1. Obtain valid FSSAI Central/State License on [FoSCoS Portal](https://foscos.fssai.gov.in).",
            "2. Implement Prerequisite Programmes (cleanroom zoning, pest control, potable water per IS 10500).",
            "3. Conduct Hazard Analysis and establish Critical Control Points (CCPs).",
            "4. Apply on [BIS Manakonline](https://www.manakonline.in) or NABCB-accredited certification bodies for FSMS audit."
        ]
    },
    "27001": {
        "iso_code": "ISO/IEC 27001:2022",
        "is_code": "IS/ISO/IEC 27001:2022",
        "title": "Information Security, Cybersecurity and Privacy Protection - Information Security Management Systems (ISMS)",
        "domains": ["cybersecurity", "infosec", "iso 27001", "iso27001", "data privacy", "cloud security", "it security", "dpdp act"],
        "department": "Electronics & IT Department (LITD 07 / MSD)",
        "cert_scheme": "BIS ISMS Scheme & CERT-In / MeitY Cybersecurity Directives",
        "portal_url": "https://www.manakonline.in",
        "statutory_act": "Information Technology Act 2000 & Digital Personal Data Protection (DPDP) Act 2023",
        "summary": "Comprehensive framework of 93 information security controls covering Organizational, People, Physical, and Technological safeguards for digital assets and customer data.",
        "key_clauses": [
            "Clause 6.1.3: Information Security Risk Treatment & Statement of Applicability (SoA)",
            "Annex A.5: Organizational Controls (Policies, Access Control, Threat Intelligence)",
            "Annex A.8: Technological Controls (Data Masking, Encryption, Vulnerability Management)"
        ],
        "steps": [
            "1. Define ISMS Scope and construct Asset-Threat-Vulnerability Risk Register.",
            "2. Formulate Statement of Applicability (SoA) for Annex A controls.",
            "3. Enforce access control, endpoint security, and DPDP compliance data encryption.",
            "4. Undergo Stage 1 and Stage 2 third-party certification audits."
        ]
    },
    "45001": {
        "iso_code": "ISO 45001:2018",
        "is_code": "IS/ISO 45001:2018",
        "title": "Occupational Health and Safety Management Systems (OH&S) - Requirements",
        "domains": ["occupational health", "workplace safety", "occupational safety", "iso 45001", "iso45001", "factory safety", "workplace hazard", "ppe safety", "oh&s", "ohsas 18001"],
        "department": "Management & Systems Department (MSD 07)",
        "cert_scheme": "BIS OH&SMS Certification Scheme",
        "portal_url": "https://www.manakonline.in",
        "statutory_act": "Factories Act 1948 & Occupational Safety, Health and Working Conditions Code 2020",
        "summary": "Aims to eliminate workplace hazards, prevent fatal and minor industrial injuries, ensure worker health surveillance, and establish PPE protocols.",
        "key_clauses": [
            "Clause 5.4: Consultation and Participation of Workers",
            "Clause 6.1.2: Hazard Identification and Assessment of OH&S Risks",
            "Clause 8.1.2: Eliminating Hazards and Reducing OH&S Risks (Hierarchy of Controls)"
        ],
        "steps": [
            "1. Perform Hazard Identification and Risk Assessment (HIRA) across all plant workstations.",
            "2. Provide certified personal protective equipment (PPE) conforming to BIS standards.",
            "3. Form safety committees and execute emergency fire and evacuation drills.",
            "4. Apply on [BIS Manakonline](https://www.manakonline.in) for formal OH&S certification."
        ]
    },
    "13485": {
        "iso_code": "ISO 13485:2016",
        "is_code": "IS/ISO 13485:2016",
        "title": "Medical Devices - Quality Management Systems - Requirements for Regulatory Purposes",
        "domains": ["medical device", "iso 13485", "iso13485", "implants", "diagnostic", "cdsco", "cleanroom", "biocompatibility"],
        "department": "Medical Equipment & Hospital Planning (MHD 04 / MSD)",
        "cert_scheme": "CDSCO Medical Device Rules 2017 & BIS Medical Device QMS Scheme",
        "portal_url": "https://cdsco.gov.in",
        "statutory_act": "Drugs and Cosmetics Act 1940 & Medical Device Rules 2017",
        "summary": "Mandatory quality management standard for medical device manufacturers, ensuring cleanroom sterility, biocompatibility validation, and clinical risk management.",
        "key_clauses": [
            "Clause 6.4.2: Contamination Control and Cleanroom Environments (ISO Class 7/8)",
            "Clause 7.3: Design & Development Controls, Verification and Clinical Validation",
            "Clause 7.5.9: Traceability of Implantable and Critical Medical Devices"
        ],
        "steps": [
            "1. Classify device under CDSCO Class A/B/C/D risk tier on [SUGAM Portal](https://cdsco.gov.in).",
            "2. Implement ISO 13485 QMS documentation, Device Master Record (DMR), and Device History Record (DHR).",
            "3. Undergo audit by CDSCO-notified Notified Bodies / BIS.",
            "4. Obtain Manufacturing License (MD-5 / MD-9) from State/Central Licensing Authority."
        ]
    },
    "17025": {
        "iso_code": "ISO/IEC 17025:2017",
        "is_code": "IS/ISO/IEC 17025:2017",
        "title": "General Requirements for the Competence of Testing and Calibration Laboratories",
        "domains": ["nabl", "lab", "laboratory", "calibration", "testing lab", "iso 17025", "iso17025", "measurement uncertainty"],
        "department": "National Accreditation Board for Testing and Calibration Laboratories (NABL) / BIS",
        "cert_scheme": "NABL Accreditation under Quality Council of India (QCI)",
        "portal_url": "https://nabl-india.org",
        "statutory_act": "National Accreditation Rules & BIS Recognized Laboratory Scheme",
        "summary": "International benchmark demonstrating that testing laboratories operate competently, produce valid and impartial results, and maintain measurement traceability to National Physical Laboratory (NPL).",
        "key_clauses": [
            "Clause 6.4 & 6.5: Equipment Calibration and Metrological Traceability to SI units",
            "Clause 7.2: Method Selection, Verification and Validation of Test Procedures",
            "Clause 7.6: Evaluation of Measurement Uncertainty (GUM principles)",
            "Clause 7.7: Ensuring Validity of Results (Proficiency Testing / Inter-lab comparisons)"
        ],
        "steps": [
            "1. Setup laboratory with calibrated test equipment traceable to NPL / BIPM standards.",
            "2. Participate in accredited Proficiency Testing (PT) programs.",
            "3. Calculate Measurement Uncertainty (MU) for all accredited test parameters.",
            "4. Apply on the [NABL Portal](https://nabl-india.org) for formal ISO/IEC 17025 accreditation."
        ]
    }
}

# Master Vernacular & Typo Normalization Mapping
VERNACULAR_AND_TYPO_MAP: Dict[str, str] = {
    "bsi": "bis",
    "cokonut": "coconut", "nariyal": "coconut", "kobbari": "coconut", "thengai": "coconut", "elaneer": "coconut",
    "doodh": "milk_dairy", "dahi": "milk_dairy", "paneer": "milk_dairy", "ghee": "milk_dairy", "pal": "milk_dairy",
    "paani": "packaged_water", "bisleri": "packaged_water", "water bottle": "packaged_water", "drinking water": "packaged_water",
    "saria": "tmt_steel", "loha": "tmt_steel", "iron rod": "tmt_steel", "rebar": "tmt_steel", "steel bar": "tmt_steel",
    "khad": "fertilizer", "khat": "fertilizer", "urea": "fertilizer", "dap": "fertilizer",
    "sona": "gold_jewellery", "chandi": "gold_jewellery", "gehna": "gold_jewellery", "thangam": "gold_jewellery", "bangar": "gold_jewellery",
    "chappal": "footwear", "joota": "footwear", "sandals": "footwear", "shoes": "footwear", "sneakers": "footwear",
    "khilona": "toys", "gudia": "toys", "doll": "toys", "toy": "toys",
    "tel": "edible_oil", "cooking oil": "edible_oil", "mustard oil": "edible_oil", "sarson tel": "edible_oil",
    "chai": "tea_coffee", "kaapi": "tea_coffee", "coffee": "tea_coffee",
    "masala": "spices", "mirchi": "spices", "haldi": "spices", "dhaniya": "spices", "jeera": "spices",
    "dava": "pharmacy_medical", "dawai": "pharmacy_medical", "dawakhana": "pharmacy_medical", "medicine": "pharmacy_medical",
    "murga": "meat_fish", "gosht": "meat_fish", "machli": "meat_fish", "chicken": "meat_fish", "mutton": "meat_fish",
    "mithai": "sweet_mithai_dairy", "halwai": "sweet_mithai_dairy",
    "bijli wire": "electrical_wiring", "taar": "electrical_wiring",
    "concreete": "cement", "cement": "cement",
    "helmet": "helmets", "gas cylinder": "lpg_cylinders", "cylinder": "lpg_cylinders",
    # Common Food, Restaurant & Licensing typos
    "restaurnt": "restaurant", "resturant": "restaurant", "restraunt": "restaurant",
    "restaraunt": "restaurant", "restrant": "restaurant", "restaurent": "restaurant",
    "fud": "food", "foood": "food", "fod": "food",
    "juce": "juice", "jucie": "juice", "juicee": "juice",
    "sugercane": "sugarcane", "shugarcane": "sugarcane",
    "licentce": "license", "licence": "license", "lisence": "license", "lisense": "license",
    "requirment": "requirement", "requrment": "requirement", "requirments": "requirement",
    "fssai": "fssai", "fsai": "fssai", "fassai": "fssai", "fssi": "fssai",
    "bakry": "bakery", "bekary": "bakery",
    "medicl": "medical", "farma": "pharmacy",
    "petroll": "petrol", "disel": "diesel", "deisel": "diesel",
    "solar": "solar_energy", "solar panel": "solar_energy"
}

# Master Commodities & Everyday Products 360 Knowledge Graph
MASTER_COMMODITIES_STANDARDS_GRAPH: Dict[str, Dict[str, Any]] = {
    "coconut": {
        "title": "Coconut (Fresh Tender Coconut, Bottled Coconut Water, Coconut Oil & Byproducts)",
        "keywords": ["coconut", "tender coconut", "coconut water", "nariyal", "kobbari", "thengai", "elaneer", "copra", "coconut oil", "desiccated coconut", "coir", "cocopeat", "coconut stall"],
        "standards": [
            "IS 15271:2003 (Packaged Natural Tender Coconut Water - pH 4.8-5.5, Brix 5.0-6.5%, Zero Pathogens)",
            "IS 547:1968 (Edible Coconut Oil - Moisture max 0.25%, Polenske value min 13.0, Zero mineral oil)",
            "IS 966:1999 (Desiccated Coconut Powder - Oil min 65%, Moisture max 3%, FFA max 0.3%)",
            "IS 15827:2009 (Coir Pith / Cocopeat Organic Soil Conditioner)",
            "FSSAI Food Safety Category 04 (Fruits & Vegetables) & Category 02 (Edible Oils)"
        ],
        "consumer_guide": [
            "Tender Coconut Water: Check for clean cut husk; bottled water must carry 14-digit FSSAI logo, pH 4.8-5.5, and Best Before date.",
            "Edible Coconut Oil: Look for Agmark Grade I/II seal or FSSAI registration. Pure unadulterated coconut oil solidifies completely below 24°C.",
            "Desiccated Powder: Must be snow-white, free from yellow oxidation, rancidity, and foreign odors."
        ],
        "business_guide": [
            {"license": "FSSAI Basic Registration (< ₹12L) or State License (> ₹12L)", "authority": "FSSAI (FoSCoS)", "portal": "foscos.fssai.gov.in"},
            {"license": "Municipal Street Vending / Health Trade Clearance", "authority": "Local Urban Local Body (ULB)", "portal": "Municipal Citizen Portal"},
            {"license": "Shops and Commercial Establishments Registration (Gumasta)", "authority": "State Labour Department", "portal": "www.nsws.gov.in"},
            {"license": "Coconut Development Board (CDB) Registration", "authority": "Ministry of Agriculture & Farmers Welfare", "portal": "coconutboard.gov.in"},
            {"license": "MSME Udyam Registration (Free Lifetime Certificate)", "authority": "Ministry of MSME", "portal": "udyamregistration.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Obtain Shop Act Certificate and Municipal Vending / Trade permit.",
            "Step 2: Register on FSSAI FoSCoS portal under Category 04 / Category 14 (Beverages).",
            "Step 3: If setting up an oil mill or bottling plant, secure CDB technology subsidy and SPCB consent.",
            "Step 4: Register free on Udyam portal (udyamregistration.gov.in) for PM SVANidhi or Mudra collateral-free loan eligibility."
        ],
        "action_chips": [
            "🌴 How to start a Fresh Tender Coconut Stall?",
            "🥤 Setup a Packaged Tender Coconut Water bottling plant",
            "🛢️ Start a Coconut Oil manufacturing mill under IS 547",
            "🧶 Open a Coir & Cocopeat manufacturing unit"
        ]
    },
    "milk_dairy": {
        "title": "Milk, Dairy Products, Paneer, Ghee, Curd & Butter",
        "keywords": ["milk", "dairy", "doodh", "paneer", "ghee", "curd", "dahi", "butter", "milk powder", "khoya", "lassi", "milk parlour", "dairy farm"],
        "standards": [
            "IS 1374:2007 (Cattle Feed for Lactating Cows - Protein & Mineral Specs)",
            "IS 2785 (Cheese & Paneer - Moisture max 60%, Milk fat min 50% on dry basis)",
            "IS 1165 (Milk Powder - Microbial limits)",
            "FSSAI Category 01 (Dairy Products and Analogues) - Zero synthetic adulterants (neutralizers, urea, starch)"
        ],
        "consumer_guide": [
            "Check for official FSSAI logo, License number, Milk Fat % (Toned: 3%, Standardized: 4.5%, Full Cream: 6%) and SNF % on milk packets.",
            "Mithai & Paneer: Confirm Best Before display on trays; reject items showing blue/yellow starch adulteration under iodine drop test.",
            "Ghee: Verify authentic aroma, graininess (granules), and Agmark Special Grade seal."
        ],
        "business_guide": [
            {"license": "FSSAI Food Business License (Category 01 - Dairy)", "authority": "FSSAI", "portal": "foscos.fssai.gov.in"},
            {"license": "Municipal Health Trade License (Commercial Chillers 0-4°C)", "authority": "Municipal Corporation", "portal": "Municipal Portal"},
            {"license": "Legal Metrology Stamping of Weighing Scales / Dispensing Cans", "authority": "Legal Metrology Dept", "portal": "e-measure.gov.in"},
            {"license": "MSME Udyam Registration (Free Lifetime)", "authority": "Ministry of MSME", "portal": "udyamregistration.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Install commercial deep-freezers and milk chillers maintaining 0°C to 4°C cold chain.",
            "Step 2: Obtain FSSAI State License on FoSCoS portal with daily fat and SNF testing logs.",
            "Step 3: Get electronic scales stamped by Legal Metrology inspector (deducting box tare weight).",
            "Step 4: Register for free Udyam MSME certificate on udyamregistration.gov.in."
        ],
        "action_chips": [
            "🥛 How to open a Milk Parlour & Dairy Store?",
            "🧀 Setup a Paneer & Ghee manufacturing unit",
            "🧪 How to test milk purity and adulteration at home?",
            "📜 FSSAI registration process for dairy farmers"
        ]
    },
    "packaged_water": {
        "title": "Packaged Drinking Water & Natural Mineral Water",
        "keywords": ["water", "drinking water", "packaged water", "mineral water", "paani", "bisleri", "water plant", "ro water", "water bottle"],
        "standards": [
            "IS 14543:2018 (Packaged Drinking Water Other Than Natural Mineral Water - Mandatory ISI Mark Scheme-I)",
            "IS 13428:2005 (Packaged Natural Mineral Water - Mandatory Scheme-I)",
            "IS 10500:2012 (Drinking Water - Baseline Potability Parameters)"
        ],
        "consumer_guide": [
            "Check for mandatory authentic BIS ISI Mark with 7/8-digit CM/L license number on bottle label or jar cap.",
            "Verify tamper-evident neck sleeve seal, 14-digit FSSAI license number, and clear batch coding.",
            "Verify the CM/L license number on the official **BIS Care Mobile App** to ensure genuine manufacturer status."
        ],
        "business_guide": [
            {"license": "BIS Scheme-I Product Certification (Mandatory ISI Mark)", "authority": "Bureau of Indian Standards", "portal": "www.manakonline.in"},
            {"license": "FSSAI Central / State Food License", "authority": "FSSAI", "portal": "foscos.fssai.gov.in"},
            {"license": "Central Ground Water Authority (CGWA) Borewell NOC", "authority": "Ministry of Jal Shakti", "portal": "cgwa-noc.gov.in"},
            {"license": "Consent to Establish & Operate (CTE/CTO)", "authority": "State Pollution Control Board", "portal": "cpcb.nic.in"}
        ],
        "setup_steps": [
            "Step 1: Secure CGWA Borewell NOC and SPCB environmental consent.",
            "Step 2: Install complete RO filtration, ozonation, UV treatment, and in-house microbiological laboratory.",
            "Step 3: Apply on BIS Manakonline for Scheme-I ISI Mark Certification (Section 16, BIS Act 2016).",
            "Step 4: Undergo factory audit and product sample draw by BIS inspecting officers."
        ],
        "action_chips": [
            "💧 How to setup a Packaged Drinking Water bottling plant?",
            "🔬 In-house testing laboratory requirements under IS 14543",
            "📲 How to verify ISI mark on water bottle with BIS Care app",
            "📜 Central Ground Water Authority (CGWA) NOC rules"
        ]
    },
    "cement": {
        "title": "Cement (Portland Pozzolana Cement - PPC, Ordinary Portland Cement - OPC)",
        "keywords": ["cement", "ppc", "opc", "concreete", "concrete", "cement shop", "rmc", "cement dealership"],
        "standards": [
            "IS 1489 (Part 1 & 2): Portland Pozzolana Cement (Fly Ash / Calcined Clay Based)",
            "IS 269:2015 (Ordinary Portland Cement - 33, 43 & 53 Grade)",
            "IS 4926 (Ready Mixed Concrete - Production & Quality Control)"
        ],
        "consumer_guide": [
            "Verify authentic BIS ISI Mark and 7-digit CM/L number printed on all HDPE/paper cement bags.",
            "Check Week Number & Year of packing (Cement loses up to 20% compressive strength after 90 days).",
            "Ensure stitched bag weight is 50 kg ± 1% with no lumps or moisture hardening inside."
        ],
        "business_guide": [
            {"license": "BIS Scheme-I Product Certification (Mandatory for Manufacturers)", "authority": "BIS", "portal": "www.manakonline.in"},
            {"license": "Shops and Commercial Establishments Registration (for Retail Dealers)", "authority": "State Labour Dept", "portal": "www.nsws.gov.in"},
            {"license": "GST Registration (28% Cement GST Slab)", "authority": "CBIC", "portal": "www.gst.gov.in"},
            {"license": "Legal Metrology Packaged Commodities Compliance", "authority": "Legal Metrology Dept", "portal": "e-measure.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Secure dry, leak-proof godown with wooden pallets to keep cement bags 15 cm off floor.",
            "Step 2: Obtain Dealership LOI from cement manufacturer (UltraTech, ACC, Ambuja, Dalmia, Shree).",
            "Step 3: Register for GSTIN on gst.gov.in and Shop Act License from State Labour portal.",
            "Step 4: Provide manufacturer's test certificate (MTC) with compressive strength values to buyers."
        ],
        "action_chips": [
            "🏗️ How to start a Cement Dealership & Retail shop?",
            "⚖️ Compressive strength & setting time testing under IS 269",
            "📦 Legal Metrology 50kg bag weight stamping rules",
            "🏭 Setup an RMC (Ready Mix Concrete) batching plant"
        ]
    },
    "tmt_steel": {
        "title": "TMT Steel Rebars, Structural Steel & Construction Rods",
        "keywords": ["steel", "tmt", "saria", "loha", "rebar", "iron rod", "structural steel", "tmt bar", "tmt rod", "steel dealership"],
        "standards": [
            "IS 1786:2008 (High Strength Deformed Steel Bars and Wires for Concrete Reinforcement - Fe 500, Fe 550D, Fe 600)",
            "DPIIT Steel & Steel Products (Quality Control) Order"
        ],
        "consumer_guide": [
            "Look for embossed ISI mark, Grade designation (e.g. `Fe 550D`), Brand name, and CM/L number repeated along every single meter of the rebar.",
            "`D` grade (e.g., Fe 500D) indicates superior earthquake resistance and minimum 16% elongation.",
            "Reject rusted or plain non-ribbed rebars lacking mandatory manufacturer embossing."
        ],
        "business_guide": [
            {"license": "BIS Scheme-I ISI Mark Certification (Mandatory for Re-Rolling Mills)", "authority": "BIS", "portal": "www.manakonline.in"},
            {"license": "Manufacturer Mill Test Certificate (MTC)", "authority": "Primary/Secondary Steel Producer", "portal": "Ministry of Steel"},
            {"license": "GST Registration (18% Steel Slab) & Trade License", "authority": "CBIC & Municipal Body", "portal": "www.gst.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Establish authorized retail dealership with primary (SAIL, TATA, JSW, Jindal) or certified secondary producers.",
            "Step 2: Secure commercial yard with heavy vehicle crane loading facilities and weighing bridge.",
            "Step 3: Register for GSTIN and Shop Act License.",
            "Step 4: Maintain Mill Test Certificates (MTC) proving chemical (Carbon, Sulphur, Phosphorus) and mechanical strength."
        ],
        "action_chips": [
            "🏢 How to start a TMT Steel & Hardware Dealership?",
            "📐 Yield strength & elongation specs for Fe 500D rebars",
            "🔍 How to detect counterfeit non-ISI steel bars",
            "🏭 Setup a Steel Re-Rolling Mill under IS 1786"
        ]
    },
    "fertilizer": {
        "title": "Fertilizers, Agrochemicals, Urea, DAP & Pesticides",
        "keywords": ["fertilizer", "khad", "khat", "urea", "dap", "pesticide", "insecticide", "agrochemicals", "krishi kendra", "agri store"],
        "standards": [
            "IS 540:2019 (Urea, Fertilizer Grade - Nitrogen min 46.0%, Biuret max 1.5%)",
            "IS 824 (Di-ammonium Phosphate - Total Nitrogen min 18.0%, Water soluble P2O5 min 41.0%)",
            "Fertilizer (Control) Order (FCO) 1985 & Insecticides Act 1968"
        ],
        "consumer_guide": [
            "Check mandatory neem-coated urea tag and subsidized Maximum Retail Price (MRP) printed on bag.",
            "Purchase only through Government biometric POS machines with Aadhaar authentication to claim official subsidies.",
            "Never purchase unsealed or loose fertilizer bags."
        ],
        "business_guide": [
            {"license": "Fertilizer Dealer Authorization (Form A2 under FCO 1985)", "authority": "District Agriculture Officer (DAO)", "portal": "State Agriculture Portal"},
            {"license": "Insecticides & Pesticides Sale License", "authority": "Joint Director of Agriculture", "portal": "State Agriculture Single Window"},
            {"license": "e-Urvarak Biometric POS Machine Integration", "authority": "Department of Fertilizers", "portal": "urvarak.nic.in"},
            {"license": "GST Registration (5% Fertilizer Slab)", "authority": "CBIC", "portal": "www.gst.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Verify mandatory qualification (B.Sc Agriculture / Chemistry graduate or diploma in agri-inputs).",
            "Step 2: Obtain Principal Certificate from fertilizer manufacturers (IFFCO, KRIBHCO, Coromandel, NFL).",
            "Step 3: Apply for Fertilizer (FCO) and Pesticide dealer license at District Agriculture Office.",
            "Step 4: Install Government DBT POS machine connected to e-Urvarak portal for biometric farmer sales."
        ],
        "action_chips": [
            "🌾 How to open a Fertilizer & Pesticides shop?",
            "📑 Documents required for Fertilizer Control Order (FCO) license",
            "💻 How to integrate e-Urvarak biometric POS machine",
            "🧪 Nitrogen and Biuret limits in Urea per IS 540"
        ]
    },
    "gold_jewellery": {
        "title": "Gold & Silver Jewellery, Precious Ornaments & Bullion",
        "keywords": ["gold", "jewellery", "sona", "chandi", "hallmark", "huid", "silver", "diamond", "gold shop", "jeweller"],
        "standards": [
            "IS 1417:2016 (Gold and Gold Alloys, Jewellery/Artefacts - Fineness & 6-digit HUID Hallmarking)",
            "IS 2112:2014 (Silver and Silver Alloys - Fineness & Hallmarking)",
            "Section 14, BIS Act 2016 (Mandatory Hallmarking of Gold Jewellery in India)"
        ],
        "consumer_guide": [
            "Look for the 3 mandatory hallmarks: 1. BIS Triangular Logo, 2. Purity Grade (e.g. `22K916` for 91.6% pure gold, `18K750`, `14K585`), and 3. Six-digit laser-engraved alphanumeric HUID.",
            "Verify the 6-digit HUID code instantly on the **BIS Care Mobile App** using the 'Verify HUID' feature to see article type, jeweller registration, and assaying center.",
            "Demand formal retail invoice with breakdown of gross weight, net gold weight, purity karat, and making charges."
        ],
        "business_guide": [
            {"license": "Mandatory BIS Jeweller Registration on Manakonline", "authority": "Bureau of Indian Standards", "portal": "www.manakonline.in"},
            {"license": "Legal Metrology Stamping of High-Precision Class-II Electronic Balances", "authority": "Legal Metrology Dept", "portal": "e-measure.gov.in"},
            {"license": "GST Registration (3% Precious Metals Slab)", "authority": "CBIC", "portal": "www.gst.gov.in"},
            {"license": "PMLA Compliance (Prevention of Money Laundering Act KYC)", "authority": "FIU-India", "portal": "fiuindia.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Install high-security vaults, 24x7 CCTV backup, and Legal Metrology certified Class-II electronic balances.",
            "Step 2: Apply online on BIS Manakonline portal (www.manakonline.in) for Gold Jeweller Registration (zero fee for small turnover jewellers).",
            "Step 3: Send all gold jewellery lots exclusively to BIS-Recognized Assaying & Hallmarking Centres (AHC) to laser-engrave HUID.",
            "Step 4: Display official BIS Consumer Information Board and 10X magnifying glass at the customer counter."
        ],
        "action_chips": [
            "💍 How to get BIS Hallmarking registration for jewellery showroom?",
            "🔍 How to verify 6-digit HUID code on BIS Care App",
            "⚖️ Legal Metrology stamping for carat precision scales",
            "🪙 Hallmarking fee structure for gold ornaments"
        ]
    },
    "footwear": {
        "title": "Footwear, Leather Shoes, Sports Shoes, Chappals & Sandals",
        "keywords": ["footwear", "shoes", "shoe", "chappal", "joota", "sandals", "sneakers", "boots", "slippers", "shoe shop"],
        "standards": [
            "IS 15844 (Sports Footwear - Upper adhesion & sole abrasion resistance)",
            "IS 17043 (All Rubber & Polymeric Boots and Slippers)",
            "DPIIT Footwear (Quality Control) Order"
        ],
        "consumer_guide": [
            "Check embossed authentic BIS ISI Mark with 7/8-digit CM/L number on shoe outsoles or insole heel pads.",
            "Verify box packaging contains Legal Metrology label stating Size (in Indian/UK units), MRP, Net Quantity, and Manufacturer Address.",
            "Ensure sole flexing withstands 30,000 continuous flex cycles without cracking."
        ],
        "business_guide": [
            {"license": "DPIIT Footwear QCO Compliance (Illegal to stock non-ISI shoes)", "authority": "DPIIT & BIS", "portal": "www.manakonline.in"},
            {"license": "Shops and Commercial Establishments Registration (Gumasta)", "authority": "State Labour Department", "portal": "www.nsws.gov.in"},
            {"license": "GST Registration (5% / 12% Footwear Slabs)", "authority": "CBIC", "portal": "www.gst.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Obtain Shop Act Certificate and Municipal Trade License.",
            "Step 2: Obtain GSTIN on gst.gov.in.",
            "Step 3: Ensure all footwear sourced from wholesalers/manufacturers carries authentic BIS ISI mark under Footwear QCO.",
            "Step 4: Register for free Udyam MSME certificate on udyamregistration.gov.in."
        ],
        "action_chips": [
            "👟 How to open a Footwear Showroom & Shoe Store?",
            "📐 DPIIT Footwear QCO compliance requirements",
            "🔍 How to verify ISI mark on shoe soles",
            "🏭 Setup a Footwear manufacturing unit under IS 15844"
        ]
    },
    "toys": {
        "title": "Toys, Children Play Equipment, Dolls & Electronic Games",
        "keywords": ["toys", "toy", "khilona", "doll", "dolls", "games", "puzzles", "ride-on", "toy store", "infant toys"],
        "standards": [
            "IS 9873 (Parts 1 to 9: Safety of Toys - Mechanical, Physical, Flammability & Heavy Metal Migration)",
            "IS 15644 (Safety of Electric Toys)",
            "DPIIT Toys (Quality Control) Order 2020 (Mandatory Scheme-I ISI Mark)"
        ],
        "consumer_guide": [
            "Check authentic BIS ISI Mark with CM/L number printed directly on toy body and packaging.",
            "Never buy toys with small detachable parts (smaller than 31.7 mm diameter) for children under 3 years to prevent choking hazards.",
            "Check for non-toxic paint certification (Lead < 90 mg/kg, Cadmium < 75 mg/kg, Phthalates < 0.1%)."
        ],
        "business_guide": [
            {"license": "BIS Scheme-I Product Certification (Mandatory for Manufacturers)", "authority": "BIS", "portal": "www.manakonline.in"},
            {"license": "Shops and Commercial Establishments Registration (for Retailers)", "authority": "State Labour Dept", "portal": "www.nsws.gov.in"},
            {"license": "Legal Metrology Packaged Commodities Registration", "authority": "Legal Metrology Dept", "portal": "e-measure.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Secure Shop Act License and Municipal Trade permit.",
            "Step 2: Verify that 100% of toy stock carries authentic BIS ISI marks (Selling non-ISI toys is a criminal offense under Section 29, BIS Act 2016).",
            "Step 3: Register for GSTIN (HSN 9503) on gst.gov.in.",
            "Step 4: Register for free Udyam MSME certificate on udyamregistration.gov.in."
        ],
        "action_chips": [
            "🧸 How to start a Toy Store & Gift Article Shop?",
            "👶 BIS Child safety & choking hazard standards under IS 9873",
            "🔋 Electric toy safety testing under IS 15644",
            "🏭 Setup a Toy manufacturing unit under Toys QCO"
        ]
    },
    "helmets": {
        "title": "Two-Wheeler Helmets & Protective Headgear",
        "keywords": ["helmet", "helmets", "two wheeler helmet", "bike helmet", "protective headgear", "rider helmet"],
        "standards": [
            "IS 4151:2020 (Protective Helmets for Riders of Two-Wheeled Motor Vehicles - Mandatory Scheme-I ISI Mark)",
            "Ministry of Road Transport and Highways (MoRTH) Protective Helmets QCO"
        ],
        "consumer_guide": [
            "Never buy roadside non-ISI helmets; check authentic BIS ISI mark and 7-digit CM/L number permanently painted on back of helmet.",
            "Ensure helmet weight is <= 1.2 kg with impact-attenuation EPS foam liner and quick-release chin strap.",
            "Verify visor conforms to IS 9973 for scratch resistance and optical clarity."
        ],
        "business_guide": [
            {"license": "MoRTH Mandatory Helmet QCO Compliance", "authority": "MoRTH & BIS", "portal": "www.manakonline.in"},
            {"license": "Shops & Establishments Registration", "authority": "State Labour Dept", "portal": "www.nsws.gov.in"},
            {"license": "GST Registration (18% Helmet Slab)", "authority": "CBIC", "portal": "www.gst.gov.in"}
        ],
        "setup_steps": [
            "Step 1: Secure retail premise and obtain Shop Act certificate.",
            "Step 2: Obtain GSTIN on gst.gov.in.",
            "Step 3: Stock only BIS-certified IS 4151 helmets from authorized manufacturers.",
            "Step 4: Verify helmet CM/L numbers on BIS Care mobile app."
        ],
        "action_chips": [
            "🛵 BIS Safety standards for Two-Wheeler Helmets (IS 4151)",
            "🔍 How to identify fake non-ISI helmets",
            "🏪 How to open a Motorcycle Accessories & Helmet shop",
            "🏭 In-house testing laboratory requirements for Helmets"
        ]
    }
}

# Master Commercial Business, Retail Shop & Store Licensing Knowledge Base
COMMERCIAL_STORES_LICENSING_REGISTRY: Dict[str, Dict[str, Any]] = {
    "kirana_grocery": {
        "business_type": "Grocery Store, Retail Supermarket, Kirana Shop & Provision Store",
        "keywords": ["grocery", "kirana", "supermarket", "provision store", "general store", "retail shop", "open a store", "retail store", "shop license"],
        "mandatory_licenses": [
            {
                "license": "Shops and Commercial Establishments Act Registration",
                "authority": "State Labour Department",
                "purpose": "Statutory registration for operating a commercial establishment, working hours, and employee benefits.",
                "portal": "State Labour Single Window / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "FSSAI Registration / State Food License",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "purpose": "Mandatory for all food, grains, edible oils, and packaged foods. Basic registration (< 12 Lakh turnover) or State License (> 12 Lakhs).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "Municipal Trade License / Health Trade License",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB)",
                "purpose": "Permit to conduct commercial trade within municipality limits.",
                "portal": "Municipal Citizen Services Portal"
            },
            {
                "license": "Legal Metrology (Weights & Measures) Verification Certificate",
                "authority": "Department of Legal Metrology",
                "purpose": "Annual mandatory stamping of electronic weighing scales and verification of Maximum Retail Price (MRP) packaged commodity rules.",
                "portal": "e-Measure Portal (e-measure.gov.in)"
            },
            {
                "license": "GST Registration (Goods and Services Tax)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory for turnover > Rs. 40 Lakhs (goods) or inter-state trade.",
                "portal": "GST Portal (www.gst.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free & Lifetime)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Priority sector lending, collateral-free bank loans, and MSME subsidy eligibility.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            }
        ],
        "key_standards": [
            "IS 10500:2012 (Drinking Water for store premises)",
            "Legal Metrology (Packaged Commodities) Rules 2011 (Mandatory MRP, Net Quantity, Batch, Expiry, Customer Care labeling)",
            "FSSAI Packaging and Labelling Regulations"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Shop & Establishment Certificate from State Labour portal within 30 days of opening.",
            "Step 2: Apply for FSSAI Basic Registration (Rs. 100/yr) on FoSCoS portal (foscos.fssai.gov.in).",
            "Step 3: Register MSME Udyam online for free with Aadhaar & PAN on udyamregistration.gov.in.",
            "Step 4: Get commercial electronic weighing scale stamped and certified by the local Legal Metrology Inspector.",
            "Step 5: Apply for Municipal Trade License and GSTIN if turnover exceeds threshold."
        ]
    },
    "pharmacy_medical": {
        "business_type": "Retail Pharmacy, Chemist Shop & Medical Store",
        "keywords": ["medical store", "pharmacy", "chemist", "drug store", "medicine shop", "drug license", "open medical store"],
        "mandatory_licenses": [
            {
                "license": "Retail Drug License (Form 20 & Form 21)",
                "authority": "State Drugs Control Administration / CDSCO",
                "purpose": "Statutory permit under Drugs & Cosmetics Act 1940 to sell allopathic drugs and biologicals.",
                "portal": "State Drug Control Portal / CDSCO SUGAM (cdsco.gov.in)"
            },
            {
                "license": "Registered Pharmacist Certificate & Employment Contract",
                "authority": "State Pharmacy Council (under Pharmacy Council of India)",
                "purpose": "Mandatory presence of registered B.Pharm / D.Pharm pharmacist on premises during working hours.",
                "portal": "State Pharmacy Council"
            },
            {
                "license": "Shops and Commercial Establishments Registration",
                "authority": "State Labour Department",
                "purpose": "Commercial operations permit.",
                "portal": "State Labour Portal"
            },
            {
                "license": "GST Registration (Goods & Services Tax)",
                "authority": "CBIC",
                "purpose": "Mandatory tax registration for pharmaceutical retailing (0%, 5%, 12% drug GST slabs).",
                "portal": "www.gst.gov.in"
            },
            {
                "license": "MSME Udyam Registration (Free & Lifetime)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Priority sector credit, collateral-free bank loans, and statutory government MSME benefits.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            }
        ],
        "key_standards": [
            "Drugs & Cosmetics Rules 1945 (Schedule H, H1 & X Prescription Registers)",
            "Cold Chain Temperature: 2°C to 8°C refrigerator with continuous temperature monitoring",
            "Minimum Carpet Area: 10 square metres for retail; 15 sq metres for wholesale + retail combined"
        ],
        "step_by_step_setup": [
            "Step 1: Lease or own premises with minimum 10 sq. metres carpet area and install dedicated drug refrigerator.",
            "Step 2: Appoint a full-time Registered Pharmacist with valid State Pharmacy Council registration.",
            "Step 3: Apply online on State Drug Control portal for Form 20 (General Drugs) and Form 21 (Schedule C/C1).",
            "Step 4: Drug Inspector conducts physical premise inspection (verifying area, refrigerator, and pharmacist credentials).",
            "Step 5: Grant of 5-year Retail Drug License."
        ]
    },
    "fssai_food_licensing": {
        "business_type": "FSSAI Food Business License, FoSCoS Registration & Food Safety Standards",
        "keywords": [
            "fssai", "foscos", "fssai license", "fssai licence", "fssai licentce", "fssai registration",
            "fssai requirement", "fssai requirements", "fssai rules", "fssai certificate", "fssai standard",
            "fssai standards", "food license", "food licence", "food licentce", "food safety license",
            "food safety certificate", "food registration", "fassai", "fsai", "how to get fssai license",
            "fssai basic registration", "fssai state license", "fssai central license", "fssai permit",
            "fssai apply", "apply for fssai", "food business license", "food safety authority",
            "fssai guidelines", "fssai compliance", "food safety"
        ],
        "mandatory_licenses": [
            {
                "license": "FSSAI Basic Registration (Turnover up to ₹12 Lakhs / Year)",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "purpose": "Mandatory Form A registration for petty food manufacturers, hawkers, small vendors, mobile food carts, juice stalls, and small retail shops (Statutory Govt fee: ₹100/year).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "FSSAI State License (Turnover ₹12 Lakhs to ₹20 Crores / Year)",
                "authority": "State Food Safety Department / Commissioner of Food Safety",
                "purpose": "Mandatory Form B license for mid-sized restaurants, cafes, cloud kitchens, bakeries, food caterers, dairy units, and wholesale distributors (Statutory Govt fee: ₹2,000 to ₹5,000/year).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "FSSAI Central License (Turnover > ₹20 Crores / Year or Multi-State)",
                "authority": "FSSAI Central Licensing Authority",
                "purpose": "Mandatory Form B central license for large food manufacturers, 100% Export-Oriented Units (EOUs), multi-state chains (Head Office), seaports, airports, and railway catering (Statutory Govt fee: ₹7,500/year).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "Municipal Health Trade License / Sanitary Trade Permit",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB)",
                "purpose": "Public health clearance for commercial food preparation, clean potable water connection, and wet waste disposal.",
                "portal": "Municipal Citizen Services Portal"
            },
            {
                "license": "Shops and Commercial Establishments Act Registration (Gumasta)",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial premises, working hours, and employee welfare.",
                "portal": "State Labour Portal / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free Lifetime Certificate)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Statutory priority sector lending, collateral-free credit, 50% government fee concessions, and government subsidy benefits.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            },
            {
                "license": "GST Registration (Goods and Services Tax)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory tax registration for all food business operators crossing threshold limits or listing on e-commerce platforms (Zomato/Swiggy).",
                "portal": "GST Portal (www.gst.gov.in)"
            }
        ],
        "key_standards": [
            "Food Safety and Standards Act 2006 (Section 31) - Mandatory 14-digit FSSAI license/registration number to be prominently displayed on all premises, packaging, bill receipts, and digital delivery apps",
            "FSSAI Schedule 4 (General Hygienic and Sanitary Practices) - Mandatory hygiene conditions for all FBOs (pest exclusion, hot holding > 65°C, cold storage < 5°C, handwash stations)",
            "IS 10500:2012 / IS 14543:2018 (Drinking Water & Ice Potability) - All water used for cooking, food washing, juice blending, and ice preparation MUST test zero for E. coli & Coliforms (quarterly NABL lab testing required)",
            "IS 2491:2013 (Food Hygiene - General Principles - Code of Practice) - National standard specifying hygienic layout, SS 304 food-grade contact surfaces, pest exclusion, and waste segregation",
            "IS/ISO 22000:2018 (Food Safety Management Systems) - International HACCP benchmark for Hazard Analysis and Critical Control Points across commercial food chains",
            "FSSAI RUCO Regulations (Repurpose Used Cooking Oil) - Reheated cooking oil must NOT exceed 25% Total Polar Compounds (TPC); disposal to authorized biodiesel aggregators mandatory for kitchens using > 50 L/day",
            "Form VII Medical Fitness Certification - Mandatory annual health checkup (skin, enteric pathogens, tuberculosis, typhoid) for all food handlers",
            "Food Safety Display Board (FSDB) - Mandatory color-coded display board (Green for Fruit/Veg, Purple for Restaurant, Blue for Milk) with 14-digit FSSAI license number prominently hung at billing counter"
        ],
        "step_by_step_setup": [
            "Step 1: Determine Licensing Tier based on annual turnover (< ₹12 Lakhs = Basic Registration; ₹12L to ₹20Cr = State License; > ₹20Cr = Central License) or production/handling capacity.",
            "Step 2: Assemble Mandatory Documentation: Proof of premises (Rent Agreement / Electricity bill), Layout Blueprint with equipment list, NABL Water Testing Report (IS 10500), Form VII Medical Fitness Certificates for all handlers, and Photo ID / Aadhaar / PAN.",
            "Step 3: Submit Online Application on FoSCoS Portal (foscos.fssai.gov.in): Select Kind of Business (KoB), fill Form A (Registration) or Form B (License), upload documents, and pay the statutory fee via digital payment gateway.",
            "Step 4: Scrutiny & Inspection: The assigned Food Safety Officer (FSO) reviews documentation and conducts physical inspection of premise hygiene and water safety under Schedule 4 within 15–30 days.",
            "Step 5: Grant of 14-Digit FSSAI License: FSSAI issues the digital certificate with QR code and unique 14-digit number. Download and display prominently along with the Food Safety Display Board (FSDB)."
        ]
    },
    "restaurant_food": {
        "business_type": "Restaurant, Hotel, Cloud Kitchen, Cafe, Bakery & Eating House",
        "keywords": [
            "restaurant", "restaurnt", "resturant", "restraunt", "restaraunt", "restrant", "restaurent",
            "cafe", "cloud kitchen", "bakery", "hotel", "food outlet", "dhaba", "canteen", "open a restaurant",
            "food license", "food business", "eating house", "food", "fud", "foood", "food court", "catering",
            "mess", "tiffin", "bhojanalaya", "eatery", "dining", "kitchen", "food stall"
        ],
        "mandatory_licenses": [
            {
                "license": "FSSAI Food Business License (State / Central)",
                "authority": "FSSAI",
                "purpose": "Mandatory food hygiene and safety permit under Food Safety & Standards Act.",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "Health Trade License",
                "authority": "Municipal Corporation (ULB)",
                "purpose": "Public health clearance for food preparation and commercial dining.",
                "portal": "Municipal Single Window"
            },
            {
                "license": "Eating House License",
                "authority": "State Police Licensing Department / Municipal Body",
                "purpose": "Public safety and zoning clearance for dine-in seating.",
                "portal": "State Police Portal / National Single Window System (NSWS)"
            },
            {
                "license": "Fire Safety NOC",
                "authority": "State Fire Services Department",
                "purpose": "Mandatory fire safety inspection for restaurants having seating > 50 persons or multistoried premises.",
                "portal": "State Fire Services Portal"
            },
            {
                "license": "Consent to Establish & Operate (CTE/CTO)",
                "authority": "State Pollution Control Board (SPCB)",
                "purpose": "Effluent treatment (oil and grease trap) and kitchen exhaust chimney height compliance.",
                "portal": "State PCB Portal"
            },
            {
                "license": "Liquor / Bar License (if applicable)",
                "authority": "State Excise Department",
                "purpose": "Permit to serve alcoholic beverages on premises.",
                "portal": "State Excise Portal"
            },
            {
                "license": "Shops and Commercial Establishments Act Registration (Gumasta)",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial premises, employee welfare, and working hours.",
                "portal": "State Labour Portal / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "GST Registration (5% Restaurant Slab)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory tax registration for restaurants, cafes, and eateries.",
                "portal": "GST Portal (www.gst.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free & Lifetime)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Statutory priority sector lending, collateral-free trade loans, and government MSME restaurant subsidies.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            }
        ],
        "key_standards": [
            "IS 2491:2013 (Food Hygiene - General Principles - Code of Practice)",
            "IS 10500:2012 (Drinking & Cooking Water Potability - Strict Zero E.coli & Coliform Limits)",
            "IS/ISO 22000:2018 (Food Safety Management Systems)",
            "FSSAI RUCO Regulations (Repurpose Used Cooking Oil - Total Polar Compounds max 25%)",
            "NBC 2016 Part 4 (Fire and Life Safety for Commercial Assembly Buildings)"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Municipal Health Trade License and SPCB clearance for kitchen exhaust & oil-grease trap.",
            "Step 2: Secure Fire Safety NOC from Fire Services Department.",
            "Step 3: Apply for FSSAI State License on FoSCoS (foscos.fssai.gov.in) with layout plan & water test report.",
            "Step 4: Apply for Eating House License on State Police single window portal.",
            "Step 5: Register for GST and Shop Act before commencing commercial dining operations."
        ]
    },
    "fast_food_street_stall": {
        "business_type": "Fast Food Center, Fried Rice & Noodles Stall, Chinese Corner, Street Food Kiosk, Biryani Point & Eatery",
        "keywords": [
            "fast food", "fast food center", "fast food shop", "fast food stall", "fried rice", "fried rice center",
            "fried rice stall", "fried rice shop", "noodles", "chowmein", "chinese fast food", "chinese corner",
            "chinese stall", "biryani", "biryani center", "biryani point", "biryani stall", "momos", "momos shop",
            "dosa", "idli", "tiffin center", "tiffin shop", "mess", "food truck", "food stall", "food cart",
            "chaat", "pani puri", "shawarma", "burger", "pizza", "samosa", "paratha", "street food", "eatery",
            "snack center", "caterer", "eating point", "bsi of fried rice", "bis of fried rice", "bsi of fast food",
            "bis of fast food", "open fast food", "open fried rice shop", "rice shop", "egg rice"
        ],
        "mandatory_licenses": [
            {
                "license": "FSSAI Food Business Registration / State License (Category 16.0 - Prepared Foods / Street Food)",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "purpose": "Mandatory statutory food safety registration under Food Safety and Standards Act 2006 (Rs. 100/yr for Basic turnover < 12L; Rs. 2000/yr for State License).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "Municipal Health Trade License / Street Vending Clearance",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB) Town Vending Committee",
                "purpose": "Sanitary permit for commercial food preparation, cooking gas stove safety, clean water connection, and municipal waste disposal.",
                "portal": "Municipal Citizen Portal / State Single Window"
            },
            {
                "license": "Shops and Commercial Establishments Act Registration (Gumasta)",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial food premises, employee welfare, and working hours.",
                "portal": "State Labour Portal / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "Fire Safety Clearance & Commercial LPG Approval",
                "authority": "State Fire Services & Authorized Oil Marketing Company (IOCL/BPCL/HPCL)",
                "purpose": "Mandatory use of commercial 19 kg blue LPG cylinders (domestic cylinders are illegal for commercial fast food cooking) and ABC fire extinguisher.",
                "portal": "State Fire Services Portal"
            },
            {
                "license": "GST Registration & MSME Udyam Registration (Free Lifetime)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC) & Ministry of MSME",
                "purpose": "5% restaurant/fast food GST compliance and collateral-free PM SVANidhi street vendor loans / Mudra loan subsidies.",
                "portal": "Udyam Registration (udyamregistration.gov.in) / GST (www.gst.gov.in)"
            }
        ],
        "key_standards": [
            "IS 10500:2012 (Drinking Water for Cooking & Washing) - Strict Zero-E.coli/Coliform potability for boiling rice, making curries, washing utensils, and customer drinking water",
            "IS 2491:2013 (Food Hygiene - General Principles - Code of Practice) - Food-grade SS 304 cooking woks, stainless steel counter surfaces, fly-proof wire mesh, and covered waste bins",
            "FSSAI Repurpose Used Cooking Oil (RUCO) Regulations - Cooking oil (IS 544 / IS 542) Total Polar Compounds (TPC) must NOT exceed 25%; repeated overheating/blackening of oil is strictly prohibited by law",
            "FSSAI Food Additives & Food Colors Regulations - Zero use of toxic industrial dyes (e.g., Rhodamine B, Metanil Yellow). Monosodium Glutamate (MSG / Ajinomoto) strictly within GMP limits and prohibited for infants",
            "FSSAI Schedule 4 Sanitary Hygiene & Form VII Medical Fitness - All fast food cooks and helpers must wear clean aprons, hairnets, and hold valid annual medical fitness certificates"
        ],
        "step_by_step_setup": [
            "Step 1: Secure commercial kitchen or kiosk space with running IS 10500 potable water, grease-trap drainage, and dedicated commercial 19kg LPG cylinder connection.",
            "Step 2: Apply for FSSAI Registration or State License on FoSCoS portal (foscos.fssai.gov.in) under Kind of Business: Food Services -> Fast Food / Street Food Vendor.",
            "Step 3: Obtain Shop & Establishment Certificate (Gumasta) and Municipal Health Trade permit from local ULB.",
            "Step 4: Equip the cooking station with food-grade SS 304 woks, digital oil quality/thermometer test, and ABC type fire extinguisher.",
            "Step 5: Register for free Udyam MSME certificate (or PM SVANidhi street vendor scheme) on udyamregistration.gov.in for government loan access.",
            "Step 6: Display the 14-digit FSSAI Registration number and 'Food Safety Display Board (FSDB)' prominently at the front counter."
        ]
    },
    "juice_beverage_center": {
        "business_type": "Fresh Fruit Juice Center, Juice Bar, Beverage Stall, Shake & Mocktail Shop, Sugarcane Juice Unit",
        "keywords": [
            "juice", "juce", "jucie", "juicee", "sugarcane", "sugarcane juice", "sugercane", "shugarcane",
            "ganna", "cheruku", "karumbu", "kabbu", "serdi", "aakh", "ऊस", "juice center", "fruit juice",
            "juice bar", "fresh juice", "beverage stall", "smoothie bar", "open a juice center", "juice shop",
            "shake shop", "bsi of juice center", "bis for juice shop", "juice stall", "open juice shop",
            "beverage shop", "smoothie", "sharbat", "shake", "beverage"
        ],
        "mandatory_licenses": [
            {
                "license": "FSSAI Food Safety Registration / State License (Category 14.1.2 - Fruit Juices)",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "purpose": "Mandatory statutory food hygiene & safety registration under FSS Act 2006 (Rs. 100/yr for Basic, Rs. 2000/yr for State License).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            },
            {
                "license": "Municipal Health Trade License / Sanitary Trade Permit",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB)",
                "purpose": "Public health clearance for commercial beverage preparation, clean potable water connection, and wet waste disposal.",
                "portal": "Municipal Citizen Services Portal"
            },
            {
                "license": "Shops and Commercial Establishments Act Registration (Gumasta)",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial premises, working hours, and employee welfare.",
                "portal": "State Labour Portal / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "Legal Metrology Verification Certificate (Weights & Measures)",
                "authority": "Department of Legal Metrology",
                "purpose": "Annual stamping and calibration of commercial electronic weighing scales (for fruit procurement) and volume dispensing jugs.",
                "portal": "e-Measure Portal (e-measure.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free & Lifetime)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Government collateral-free trade loans, food processing subsidies, and priority MSME benefits.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            },
            {
                "license": "GST Registration (Goods and Services Tax)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory if annual aggregate turnover exceeds Rs. 20/40 Lakhs or for input tax credit on commercial blenders & chillers.",
                "portal": "GST Portal (www.gst.gov.in)"
            }
        ],
        "key_standards": [
            "IS 10500:2012 / IS 14543:2018 (Drinking Water & Ice Potability) - All water used for fruit washing, juice blending, and ice preparation MUST strictly comply with IS 10500 potable limits (Coliforms/E.coli = 0, TDS < 500 mg/L)",
            "IS 2491:2013 (Food Hygiene - General Principles) - Mandatory pest control, covered waste bins, fly-catchers, and food-grade stainless steel (SS 304) extractor blades",
            "IS 3881 / IS 5101 (Fruit Beverages & Preserved Juices) - Guidelines on natural fruit brix content, acidity levels, and complete prohibition of non-permitted coal-tar chemical dyes",
            "FSSAI Schedule 4 Sanitary Guidelines - Mandatory medical fitness certification (Form VII) for juice handlers (free from skin infections, tuberculosis, typhoid)",
            "FSSAI Packaging & Labelling Regulations - Mandatory 14-digit FSSAI number, Batch No, Best Before date, and allergen declarations on packaged takeaway bottles"
        ],
        "step_by_step_setup": [
            "Step 1: Secure a commercial premise with direct access to certified potable running water (complying with IS 10500) and adequate drainage.",
            "Step 2: Apply for FSSAI Basic Registration (turnover < Rs. 12 Lakhs) or State License (turnover > Rs. 12 Lakhs) on the FoSCoS portal (foscos.fssai.gov.in) under Kind of Business: Food Services / Beverage Stall.",
            "Step 3: Obtain Shop & Establishment Certificate (Gumasta) from the State Labour Department within 30 days of opening.",
            "Step 4: Secure Municipal Health Trade License and get all commercial weighing scales stamped by the Legal Metrology Inspector.",
            "Step 5: Procure food-grade SS 304 extractors and dedicated refrigeration equipment (0°C to 4°C for cut fruits). Ensure zero use of unauthorized artificial sweeteners (e.g., Saccharin) or unpermitted food coloring chemicals.",
            "Step 6: Register for free Udyam MSME certification online on udyamregistration.gov.in with Aadhaar & PAN."
        ]
    },
    "clothing_textile": {
        "business_type": "Clothing Store, Garment Showroom, Textile Boutique & Footwear Retail",
        "keywords": ["clothing", "clothes", "garment", "textile", "boutique", "apparel", "cloth store", "open clothing shop", "shoe store"],
        "mandatory_licenses": [
            {
                "license": "Shops and Commercial Establishments Act Registration",
                "authority": "State Labour Department",
                "purpose": "Commercial retail shop license.",
                "portal": "State Labour Portal"
            },
            {
                "license": "Municipal Trade License",
                "authority": "Urban Local Body (ULB)",
                "purpose": "Commercial trading clearance.",
                "portal": "Municipal Portal"
            },
            {
                "license": "GST Registration",
                "authority": "CBIC",
                "purpose": "Mandatory for textiles and apparel (5% / 12% GST slabs).",
                "portal": "www.gst.gov.in"
            },
            {
                "license": "MSME Udyam Registration",
                "authority": "Ministry of MSME",
                "purpose": "Free government registration for retail traders.",
                "portal": "udyamregistration.gov.in"
            }
        ],
        "key_standards": [
            "Legal Metrology (Packaged Commodities) Rules - Garment Size, Fiber Composition %, MRP, Month/Year of Manufacture",
            "DPIIT Footwear Quality Control Order (Mandatory ISI mark on all retail shoes per IS 15844)",
            "IS 15748 (Fire Retardant Fabrics for commercial interior curtains)"
        ],
        "step_by_step_setup": [
            "Step 1: Complete Shop & Establishment registration within 30 days.",
            "Step 2: Obtain GSTIN on gst.gov.in (essential for input tax credit on wholesale garment purchases).",
            "Step 3: Register for free Udyam MSME certificate.",
            "Step 4: Ensure all retail footwear and apparel carry statutory BIS Quality Control compliance tags."
        ]
    },
    "hardware_electrical": {
        "business_type": "Hardware Shop, Electrical Goods Retailer, Sanitaryware & Building Materials Store",
        "keywords": ["hardware", "electrical", "electric shop", "sanitaryware", "paint store", "tools", "plumbing", "open hardware store"],
        "mandatory_licenses": [
            {
                "license": "Shops and Commercial Establishments Registration",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment license.",
                "portal": "State Labour Portal"
            },
            {
                "license": "Municipal Trade License",
                "authority": "Municipal Corporation",
                "purpose": "Commercial trade permit.",
                "portal": "Municipal Services"
            },
            {
                "license": "GST Registration",
                "authority": "CBIC",
                "purpose": "Mandatory tax registration (18% / 28% hardware slabs).",
                "portal": "www.gst.gov.in"
            },
            {
                "license": "MSME Udyam Certificate",
                "authority": "Ministry of MSME",
                "purpose": "Credit guarantee and trade support.",
                "portal": "udyamregistration.gov.in"
            }
        ],
        "key_standards": [
            "IS 1293:2019 (Plugs and Socket-Outlets - Mandatory ISI Mark Scheme-I)",
            "IS 694 (PVC Insulated Cables for Electric Supply)",
            "IS 15489 (Lead-safe Paints Quality Control Order)",
            "IS 1786 (TMT Rebars Statutory QCO)"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Shop Act Certificate and Municipal Trade License.",
            "Step 2: Register for GSTIN on gst.gov.in.",
            "Step 3: Verify all electrical goods and cables stocked hold genuine BIS ISI mark and 7/8-digit CM/L numbers.",
            "Step 4: Maintain test certificates for structural steel and cement lots sold from the store."
        ]
    },
    "electronics_mobile": {
        "business_type": "Mobile Phone Store, Computer & Laptop Showroom, Electronics Retailer",
        "keywords": ["mobile", "phone store", "electronics shop", "computer", "laptop", "gadget", "open mobile shop", "mobile accessories"],
        "mandatory_licenses": [
            {
                "license": "Shops and Commercial Establishments Registration",
                "authority": "State Labour Department",
                "purpose": "Commercial retail license.",
                "portal": "State Labour Portal"
            },
            {
                "license": "Municipal Trade License",
                "authority": "Urban Local Body",
                "purpose": "Local trade permit.",
                "portal": "Municipal Citizen Portal"
            },
            {
                "license": "GST Registration",
                "authority": "CBIC",
                "purpose": "Mandatory tax registration (18% electronic GST slab).",
                "portal": "www.gst.gov.in"
            },
            {
                "license": "MSME Udyam Certificate",
                "authority": "Ministry of MSME",
                "purpose": "Government MSME benefits.",
                "portal": "udyamregistration.gov.in"
            }
        ],
        "key_standards": [
            "IS 13252 (Part 1):2010 (IT Equipment Safety - Mandatory BIS CRS R-Number)",
            "IS 16046 (Part 2):2018 (Lithium-ion Battery Safety CRS Scheme)",
            "E-Waste (Management) Rules 2022 (Extended Producer Responsibility - EPR compliance)"
        ],
        "step_by_step_setup": [
            "Step 1: Secure Shop Act License and Municipal Trade permit.",
            "Step 2: Obtain GSTIN on gst.gov.in for buying from authorized distributors (Apple, Samsung, etc.).",
            "Step 3: Verify that all electronics, power banks, and chargers display the statutory BIS CRS logo with valid R-Number (`R-XXXXXXXX`).",
            "Step 4: Register as an authorized e-waste collection point under E-Waste Rules."
        ]
    },
    "gift_toys_handicrafts": {
        "business_type": "Gift Article Shop, Toy Store, Fancy Store, Novelty & Handicrafts Showroom",
        "keywords": ["gift", "gift article", "gift shop", "gift article shop", "gift store", "toy", "toys", "toy store", "fancy store", "novelty", "handicraft", "handicrafts", "souvenir", "stationery", "open gift shop", "gift items", "present shop", "decorative shop"],
        "mandatory_licenses": [
            {
                "license": "Shops and Commercial Establishments Act Registration",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial premises, employee welfare and working hours.",
                "portal": "State Labour Portal / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "Municipal Trade License / Gumasta License",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB)",
                "purpose": "Permit to operate retail trade within municipal urban jurisdiction.",
                "portal": "Municipal Citizen Portal"
            },
            {
                "license": "GST Registration (Goods & Services Tax)",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory tax registration for input tax credit on wholesale giftware, toys, and fancy goods.",
                "portal": "GST Portal (www.gst.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free & Lifetime)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Collateral-free trade loans, 50% patent/trademark discount, and government MSME trade benefits.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            },
            {
                "license": "Legal Metrology Packaged Commodities Registration",
                "authority": "Department of Consumer Affairs (Legal Metrology Division)",
                "purpose": "Mandatory consumer disclosures (MRP, Net Quantity, Manufacturer Address, Customer Care Contact on gift packaging).",
                "portal": "e-Measure Portal (e-measure.gov.in)"
            }
        ],
        "key_standards": [
            "IS 9873 (Parts 1 to 9): Safety of Toys - Mechanical, Physical & Flammability Requirements (Mandatory Toys Quality Control Order QCO 2020 under Scheme-I ISI Mark)",
            "IS 15644: Safety of Electric Toys",
            "Legal Metrology (Packaged Commodities) Rules 2011 (Mandatory MRP, Net Quantity, Country of Origin, Customer Care contact on all boxed gift items)",
            "IS 1417:2016 (Gold and Silver Artefacts Hallmarking) - if selling silver/gold gift articles or mementos"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Shop & Establishment Certificate from State Labour portal within 30 days of opening premises.",
            "Step 2: Apply for Municipal Trade License from the local Urban Local Body.",
            "Step 3: Register for GSTIN on gst.gov.in (HSN 9503 for toys, HSN 4820/4909 for cards/stationery, HSN 7117 for fancy jewellery).",
            "Step 4: Register for free Udyam MSME certificate with Aadhaar & PAN on udyamregistration.gov.in.",
            "Step 5: CRITICAL STATUTORY REQUIREMENT: Ensure all toys, electric toys, and child gift items stocked in the store carry the mandatory authentic BIS ISI Mark with valid 7/8-digit CM/L license number under the Toys (Quality Control) Order 2020 (Selling non-ISI toys is a criminal offense under Section 29, BIS Act 2016).",
            "Step 6: Ensure all gift sets and decorative boxes carry mandatory Legal Metrology packaged commodity stickers."
        ]
    },
    "bakery_confectionery": {
        "business_type": "Bakery, Cake Shop, Pastry Studio & Confectionery Unit",
        "keywords": ["bakery", "cake shop", "pastry", "biscuits", "bread", "baking", "cookies", "muffins", "open a bakery", "bake shop"],
        "mandatory_licenses": [
            {"license": "FSSAI Food Business License / Registration", "authority": "FSSAI", "purpose": "Mandatory hygiene compliance for baking and food preparation under FoSCoS Category 07.", "portal": "foscos.fssai.gov.in"},
            {"license": "Municipal Health Trade License", "authority": "Urban Local Body", "purpose": "Commercial oven installation and food preparation hygiene clearance.", "portal": "Municipal Citizen Services"},
            {"license": "Shops and Commercial Establishments Registration (Gumasta)", "authority": "State Labour Department", "purpose": "Retail establishment permit.", "portal": "State Labour Portal"},
            {"license": "GST Registration & MSME Udyam", "authority": "CBIC & Ministry of MSME", "purpose": "Input tax credit on bakery machinery and commercial flour.", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "IS 1483:1988 (White Bread - Specifications and Moisture limits)",
            "IS 1011:2002 (Biscuits - Moisture, Acidity & Ash Content)",
            "IS 10500:2012 (Drinking Water for bakery dough kneading & washing)",
            "FSSAI Schedule 4 (Cleanroom baking hygiene, pest control & Form VII Medical Fitness)"
        ],
        "step_by_step_setup": [
            "Step 1: Secure commercial premises with IS 10500 potable water line and proper exhaust chimney for baking ovens.",
            "Step 2: Apply for FSSAI State/Basic License on FoSCoS portal (foscos.fssai.gov.in).",
            "Step 3: Register for Shop Act License and Municipal Health Trade permit.",
            "Step 4: Ensure all pre-packaged cakes and artisan breads carry FSSAI label, Nutritional info, Veg/Non-Veg logo, and Best Before date."
        ]
    },
    "sweet_mithai_dairy": {
        "business_type": "Sweet Shop, Halwai, Mithai Mart, Milk Parlour & Paneer/Ghee Unit",
        "keywords": ["sweet shop", "mithai", "halwai", "sweets", "milk parlour", "dairy shop", "paneer", "ghee", "khoya", "curd", "lassi", "open sweet shop"],
        "mandatory_licenses": [
            {"license": "FSSAI Food Business License (Category 01 - Dairy & Category 05 - Confectionery)", "authority": "FSSAI", "purpose": "Statutory food license with strict milk adulteration monitoring.", "portal": "foscos.fssai.gov.in"},
            {"license": "Municipal Health Trade License", "authority": "Municipal Corporation", "purpose": "Commercial dairy refrigeration & public health permit.", "portal": "Municipal Portal"},
            {"license": "Legal Metrology Stamping Certificate", "authority": "Legal Metrology Dept", "purpose": "Mandatory annual stamping of electronic weighing scale (tare weight exclusion).", "portal": "e-measure.gov.in"},
            {"license": "GST & MSME Udyam Registration", "authority": "CBIC & MSME", "purpose": "Statutory tax and MSME credit benefits.", "portal": "udyamregistration.gov.in"}
        ],
        "key_standards": [
            "IS 10500:2012 (Potable Water for syrup preparation)",
            "IS 2785 (Cheese and Paneer Specifications)",
            "IS 1165 (Milk Powder Specifications)",
            "FSSAI Prohibition of Synthetic Dyes (Only permitted food colors per FSSAI regulations, zero Metanil Yellow)"
        ],
        "step_by_step_setup": [
            "Step 1: Setup commercial deep-freezers and milk chillers (0°C to 4°C).",
            "Step 2: Obtain FSSAI State License on FoSCoS and maintain milk batch testing logs (fat % and SNF).",
            "Step 3: Ensure weighing scale is inspected and stamped by Legal Metrology inspector (deducting box weight from sweet weight).",
            "Step 4: Comply with FSSAI display board rule indicating 'Best Before Date' on open mithai trays."
        ]
    },
    "beauty_salon_spa": {
        "business_type": "Beauty Parlour, Unisex Hair Salon, Makeup Studio & Wellness Spa",
        "keywords": ["beauty parlour", "salon", "hair salon", "barber", "spa", "beauty salon", "makeup studio", "unisex salon", "haircut shop", "parlor", "open a salon"],
        "mandatory_licenses": [
            {"license": "Shops and Commercial Establishments Act Registration (Gumasta)", "authority": "State Labour Department", "purpose": "Statutory retail establishment registration.", "portal": "State Labour Portal"},
            {"license": "Municipal Health Trade License", "authority": "Local Municipal Corporation", "purpose": "Public health clearance, clean sterilization equipment, and linen hygiene.", "portal": "Municipal Citizen Services"},
            {"license": "Bio-Medical Waste Management Authorization (for blades & sharps)", "authority": "State Pollution Control Board (SPCB)", "purpose": "Safe disposal of disposable razor blades and chemical salon waste.", "portal": "State PCB Portal"},
            {"license": "GST Registration & MSME Udyam Certificate", "authority": "CBIC & MSME", "purpose": "18% salon services GST compliance and priority trade loans.", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "Cosmetics Rules 2020 (Only CDSCO-approved and BIS-compliant skin/hair dyes and cosmetics)",
            "IS 4707 (Part 1 & 2): Raw materials for cosmetics & permissible dye concentrations",
            "UV Sterilizer & Autoclave Standards for salon scissors, clippers, and comb disinfection"
        ],
        "step_by_step_setup": [
            "Step 1: Secure commercial salon space with dedicated water connection, shampoo station drainage, and UV sterilizers.",
            "Step 2: Obtain Shop & Establishment Certificate and Municipal Health Trade permit.",
            "Step 3: Register for free Udyam MSME certificate and GSTIN.",
            "Step 4: Use only single-use disposable blades for shaving and dispose of sharps in puncture-proof bio-hazard bins."
        ]
    },
    "gym_fitness_centre": {
        "business_type": "Commercial Gym, Fitness Center, CrossFit Studio & Yoga Center",
        "keywords": ["gym", "fitness", "fitness centre", "fitness center", "crossfit", "yoga studio", "bodybuilding", "open a gym", "health club", "gymnasium"],
        "mandatory_licenses": [
            {"license": "Shops and Commercial Establishments Act Registration", "authority": "State Labour Department", "purpose": "Commercial sports and fitness establishment permit.", "portal": "State Labour Portal"},
            {"license": "Municipal Trade License & Structural Safety Clearance", "authority": "Municipal Corporation", "purpose": "Floor load capacity clearance for heavy weights and dumbbells.", "portal": "Municipal Citizen Portal"},
            {"license": "Police Public Performance / Noise NOC (for gym music)", "authority": "State Police Licensing / PPL", "purpose": "Permit for playing background workout music within permissible decibel limits.", "portal": "State Police Portal"},
            {"license": "Fire Safety NOC", "authority": "State Fire Services", "purpose": "Life safety and fire extinguishers (NBC 2016 Part 4).", "portal": "State Fire Services Portal"},
            {"license": "GST Registration (18% Fitness Center Slab)", "authority": "CBIC", "purpose": "Mandatory tax registration for gym memberships and fitness training fees.", "portal": "www.gst.gov.in"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Collateral-free equipment financing loans, power tariff concessions, and government MSME benefits.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "NBC 2016 Part 4 (Life Safety & Emergency Exit Doors for Assembly Buildings)",
            "IS 10500:2012 (Drinking Water for gym members & shower facilities)",
            "FSSAI Retail License (if selling protein powders and health supplements on premises)"
        ],
        "step_by_step_setup": [
            "Step 1: Secure premise with reinforced commercial flooring capable of sustaining heavy barbell/dumbbell drops.",
            "Step 2: Obtain Shop Act License and Municipal Trade License.",
            "Step 3: Install heavy-duty ventilation/AC and certified fire extinguishers near cardio and weight zones.",
            "Step 4: If selling protein whey or pre-workouts, obtain FSSAI Basic Registration."
        ]
    },
    "dental_medical_clinic": {
        "business_type": "Dental Clinic, Polyclinic, Doctor Consultation & Nursing Room",
        "keywords": ["dental clinic", "clinic", "dentist", "doctor clinic", "polyclinic", "consultation room", "medical clinic", "open a clinic", "dental hospital"],
        "mandatory_licenses": [
            {"license": "Clinical Establishments (Registration and Regulation) Act Registration", "authority": "District Health Administration / State Health Dept", "purpose": "Mandatory statutory registration for medical and dental diagnostic facilities.", "portal": "State Health Services"},
            {"license": "State Dental / Medical Council Registration Certificate", "authority": "Dental Council of India (DCI) / NMC", "purpose": "Mandatory valid registration of practicing BDS/MDS or MBBS doctors.", "portal": "State Medical Council"},
            {"license": "Bio-Medical Waste (Management) Rules Authorization", "authority": "State Pollution Control Board (SPCB)", "purpose": "Mandatory tie-up with Common Bio-Medical Waste Treatment Facility (CBWTF).", "portal": "State PCB Portal"},
            {"license": "AERB Approval (Atomic Energy Regulatory Board)", "authority": "AERB (e-LORA Portal)", "purpose": "Mandatory registration for dental X-ray machines (IOPA / OPG / CBCT).", "portal": "elora.aerb.gov.in"},
            {"license": "Shops and Commercial Establishments Registration", "authority": "State Labour Department", "purpose": "Commercial premise permit for clinic staff and nurses.", "portal": "State Labour Portal"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Healthcare enterprise priority lending, medical equipment financing subsidies, and MSME benefits.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "Bio-Medical Waste Management Rules 2016 (Yellow, Red, White, Blue color-coded segregation)",
            "AERB Safety Code for Medical Diagnostic X-ray Equipment",
            "IS/ISO 13485 (Medical Device & Sterilization Systems)"
        ],
        "step_by_step_setup": [
            "Step 1: Establish clinic with dedicated autoclave room, lead-lined X-ray enclosure, and bio-medical waste bins.",
            "Step 2: Apply for Clinical Establishment registration with District Chief Medical Officer (CMO).",
            "Step 3: Register dental X-ray equipment on AERB e-LORA portal.",
            "Step 4: Execute agreement with authorized Bio-Medical Waste management facility (CBWTF)."
        ]
    },
    "diagnostics_pathology_lab": {
        "business_type": "Pathology Laboratory, Blood Testing Diagnostic Center & Imaging Center",
        "keywords": ["pathology", "diagnostic center", "blood test", "lab", "pathology lab", "medical lab", "testing lab", "x-ray center", "ultrasound", "open pathology lab"],
        "mandatory_licenses": [
            {"license": "Clinical Establishments Act Registration", "authority": "District Health Department", "purpose": "Statutory registration for diagnostic testing laboratories.", "portal": "State Health Single Window"},
            {"license": "NABL Accreditation (ISO 15189:2022) / Quality Council of India", "authority": "NABL India", "purpose": "Benchmark laboratory competence and diagnostic validity.", "portal": "nabl-india.org"},
            {"license": "Bio-Medical Waste Management Authorization", "authority": "State Pollution Control Board", "purpose": "Safe disposal of blood samples, vacutainers, and reagents.", "portal": "State PCB Portal"},
            {"license": "PNDT Act Registration (Pre-Conception & Pre-Natal Diagnostic Techniques)", "authority": "District Health Authority", "purpose": "Mandatory registration for Ultrasound and Sonography machines.", "portal": "District Health Portal"},
            {"license": "GST Registration (Commercial Diagnostics / B2B)", "authority": "CBIC", "purpose": "Tax registration for commercial laboratory testing and reagents.", "portal": "www.gst.gov.in"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Diagnostic laboratory technology upgradation subsidies and priority credit.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "IS/ISO 15189:2022 (Medical laboratories - Requirements for quality and competence)",
            "IS/ISO/IEC 17025 (Calibration and Testing Laboratory standards)",
            "Bio-Medical Waste Management Rules 2016"
        ],
        "step_by_step_setup": [
            "Step 1: Employ full-time MD Pathologist / Qualified Lab Technician with valid State Council registration.",
            "Step 2: Setup calibrated biochemistry and hematology analyzers with daily internal Quality Controls (IQC).",
            "Step 3: Obtain Clinical Establishment License and Bio-Medical Waste authorization.",
            "Step 4: Apply for NABL accreditation on nabl-india.org for national diagnostic certification."
        ]
    },
    "pet_care_aquarium_shop": {
        "business_type": "Pet Shop, Aquarium Store, Dog Food & Animal Supplies Mart",
        "keywords": ["pet shop", "aquarium", "dog food", "pet store", "bird shop", "fish store", "pet care", "veterinary supplies", "cat food", "open pet shop"],
        "mandatory_licenses": [
            {"license": "State Animal Welfare Board Registration", "authority": "State Animal Welfare Board (SAWB)", "purpose": "Mandatory registration under Prevention of Cruelty to Animals (Pet Shop) Rules 2018.", "portal": "State Animal Husbandry Dept"},
            {"license": "Municipal Trade License / Pet Trade Permit", "authority": "Local Municipal Corporation", "purpose": "Sanitary permit and animal accommodation inspection.", "portal": "Municipal Citizen Portal"},
            {"license": "Shops and Commercial Establishments Registration (Gumasta)", "authority": "State Labour Department", "purpose": "Commercial retail license.", "portal": "State Labour Portal"},
            {"license": "GST & MSME Udyam Registration", "authority": "CBIC & MSME", "purpose": "Tax compliance on pet accessories and pet feed.", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "Prevention of Cruelty to Animals (Pet Shop) Rules, 2018 (Minimum cage dimensions, ventilation, veterinary checkups)",
            "Prevention of Cruelty to Animals (Dog Breeding and Marketing) Rules, 2017",
            "IS 9761 (Poultry & Pet Cage Safety specifications)",
            "Legal Metrology (Packaged Commodities) Rules for imported pet food"
        ],
        "step_by_step_setup": [
            "Step 1: Setup climate-controlled housing with adequate air changes and clean quarantine cages for pets.",
            "Step 2: Apply for mandatory license with the State Animal Welfare Board (SAWB) with layout blueprint.",
            "Step 3: Retain an authorized registered Veterinary Doctor (BVSc) for routine health certification.",
            "Step 4: Maintain statutory register of animal pedigree, microchip IDs, and vaccination certificates."
        ]
    },
    "jewellery_gold_silver": {
        "business_type": "Gold & Silver Jewellery Showroom, Hallmarking Centre & Precious Stones Retailer",
        "keywords": ["jewellery", "gold shop", "jeweller", "silver shop", "hallmark", "huid", "gold showroom", "diamond store", "open jewellery shop"],
        "mandatory_licenses": [
            {"license": "Mandatory BIS Gold Hallmarking Jeweller Registration", "authority": "Bureau of Indian Standards (BIS)", "purpose": "Mandatory statutory registration on Manakonline under Section 14, BIS Act 2016 for selling hallmarked gold/silver.", "portal": "www.manakonline.in"},
            {"license": "Shops and Commercial Establishments Registration", "authority": "State Labour Department", "purpose": "Retail establishment permit.", "portal": "State Labour Portal"},
            {"license": "Legal Metrology Stamping of High-Precision Weighing Scales (Class II / Class I)", "authority": "Department of Legal Metrology", "purpose": "Mandatory annual stamping of 3-decimal carat/gram analytical electronic balances.", "portal": "e-measure.gov.in"},
            {"license": "GST Registration (3% Precious Metals Slab) & PMLA KYC Compliance", "authority": "CBIC & FIU-India", "purpose": "Mandatory KYC and PAN collection for jewellery transactions exceeding statutory limits.", "portal": "www.gst.gov.in"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Statutory trade credit guarantees, export assistance, and zero government registration fees.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "IS 1417:2016 (Gold and Gold Alloys, Jewellery/Artefacts - Fineness & 6-digit HUID Marking)",
            "IS 2112:2014 (Silver and Silver Alloys - Fineness & Marking)",
            "IS 15820 (General Requirements for Assaying and Hallmarking Centres)"
        ],
        "step_by_step_setup": [
            "Step 1: Install high-security vaults, 24x7 CCTV backup, and Legal Metrology certified Class-II electronic balances.",
            "Step 2: Apply online on BIS Manakonline portal (www.manakonline.in) for Gold Jeweller Registration (instant grant under zero-fee automated workflow for small jewellers).",
            "Step 3: Send gold jewellery lots only to BIS-Recognized Assaying & Hallmarking Centres (AHC) to laser-imprint the 3 mandatory marks: BIS Logo, Purity Mark (e.g. 22K916), and 6-digit alphanumeric HUID.",
            "Step 4: Display the official BIS Consumer Information Board and magnifying glass (10X) at the counter."
        ]
    },
    "footwear_leather_store": {
        "business_type": "Footwear Showroom, Shoe Retail Shop, Leather Goods & Chappal Mart",
        "keywords": ["footwear", "shoe shop", "shoes", "leather goods", "chappal", "sandals", "sneakers", "boots", "open shoe store"],
        "mandatory_licenses": [
            {"license": "Shops and Commercial Establishments Act Registration", "authority": "State Labour Department", "purpose": "Commercial retail license.", "portal": "State Labour Portal"},
            {"license": "Municipal Trade License", "authority": "Urban Local Body", "purpose": "Local trade permit.", "portal": "Municipal Citizen Portal"},
            {"license": "GST Registration & MSME Udyam", "authority": "CBIC & MSME", "purpose": "Mandatory tax registration (5% / 12% footwear slabs).", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "DPIIT Footwear Quality Control Order (Mandatory authentic BIS ISI mark on all retail shoes)",
            "IS 15844 (Sports Footwear)",
            "IS 17043 (All Rubber & Polymeric Boots)",
            "IS 1988 (Leather Sandals and Slippers)",
            "Legal Metrology (Packaged Commodities) Rules (Mandatory Size in Indian/UK system, MRP, Net Quantity, Manufacturer details)"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Shop Act Certificate and Municipal Trade License.",
            "Step 2: Obtain GSTIN on gst.gov.in.",
            "Step 3: CRITICAL COMPLIANCE: Ensure every footwear article stocked holds genuine BIS ISI mark and 7/8-digit CM/L number per the Footwear QCO (Selling non-ISI footwear is illegal in India).",
            "Step 4: Ensure boxes display the mandatory Legal Metrology packaged commodity label."
        ]
    },
    "furniture_modular_wood": {
        "business_type": "Furniture Showroom, Modular Kitchen Studio & Woodcraft Mart",
        "keywords": ["furniture", "sofa", "bed", "modular kitchen", "wood shop", "timber", "plywood", "carpentry", "open furniture store"],
        "mandatory_licenses": [
            {"license": "Shops and Commercial Establishments Registration", "authority": "State Labour Department", "purpose": "Retail establishment permit.", "portal": "State Labour Portal"},
            {"license": "Municipal Trade License", "authority": "Municipal Corporation", "purpose": "Commercial showroom trade clearance.", "portal": "Municipal Portal"},
            {"license": "Fire Safety Clearance", "authority": "State Fire Services", "purpose": "Fire safety protocols for combustible timber/foam inventories.", "portal": "State Fire Services Portal"},
            {"license": "GST & MSME Udyam Registration", "authority": "CBIC & MSME", "purpose": "Tax registration (12% / 18% furniture slabs).", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "IS 710 (Marine Plywood - Water Resistance)",
            "IS 3087 (Particle Boards - Density and Formaldehyde Emissions)",
            "IS 15748 (Fire Retardant Fabrics for commercial sofa upholstery)",
            "DPIIT Wood Based Panels Quality Control Order (QCO)"
        ],
        "step_by_step_setup": [
            "Step 1: Secure showroom with certified smoke detectors and ABC dry chemical fire extinguishers.",
            "Step 2: Obtain Shop Act License, Municipal Trade License, and GSTIN.",
            "Step 3: Verify all plywood and particle boards carry authentic BIS ISI marks under the Wood Panels QCO.",
            "Step 4: Provide formal warranty cards stating timber species and termite treatment specifications."
        ]
    },
    "stationery_printing_press": {
        "business_type": "Printing Press, Digital Flex Printing, Stationery & Xerox Center",
        "keywords": ["printing press", "stationery", "xerox", "flex printing", "photocopy", "book binding", "offset printing", "open printing press"],
        "mandatory_licenses": [
            {"license": "Press and Registration of Books Act (PRB Act) Declaration", "authority": "District Magistrate (DM / DC Office)", "purpose": "Mandatory declaration for operating printing presses publishing books/periodicals.", "portal": "District Collectorate"},
            {"license": "Shops & Establishments Act / Factories Act", "authority": "State Labour / DISH", "purpose": "Registration as commercial establishment or factory (if > 10 workers with electric power).", "portal": "State Single Window"},
            {"license": "Consent to Operate (CTO)", "authority": "State Pollution Control Board", "purpose": "Safe disposal of chemical solvent inks and plate-making effluent.", "portal": "State PCB Portal"},
            {"license": "GST & MSME Udyam Registration", "authority": "CBIC & MSME", "purpose": "Input tax credit on printing machinery, paper, and inks.", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "IS 1397 (Kraft Paper specifications)",
            "IS 1848 (Writing and Printing Paper - GSM and Brightness limits)",
            "Noise Pollution (Regulation and Control) Rules 2000 (Decibel limits for offset printing machinery)"
        ],
        "step_by_step_setup": [
            "Step 1: Install printing machinery on vibration-dampened foundation and provide sound dampeners.",
            "Step 2: File PRB Act press declaration with the District Magistrate.",
            "Step 3: Secure SPCB consent for solvent ink handling.",
            "Step 4: Register for GST and MSME Udyam on udyamregistration.gov.in."
        ]
    },
    "petrol_fuel_bunk": {
        "business_type": "Petrol Bunk, Diesel Retail Outlet, CNG Station & Fuel Pump",
        "keywords": ["petrol bunk", "petrol pump", "fuel station", "diesel pump", "cng station", "open petrol pump", "retail fuel outlet", "fuel bunk"],
        "mandatory_licenses": [
            {"license": "PESO Petroleum Storage & Dispensing License (Form XII)", "authority": "Petroleum and Explosives Safety Organization (PESO)", "purpose": "Mandatory hazardous fuel storage license under Petroleum Rules 2002.", "portal": "peso.gov.in"},
            {"license": "District Magistrate No Objection Certificate (DM / DC NOC)", "authority": "District Magistrate / Collector Office", "purpose": "Zoning, law and order, and local public safety clearance.", "portal": "District Single Window"},
            {"license": "National Highway / State PWD Access Permission", "authority": "NHAI / State PWD", "purpose": "Highway deceleration/acceleration lane and frontage approval.", "portal": "morth.nic.in"},
            {"license": "Consent to Establish & Operate (CTE/CTO)", "authority": "State Pollution Control Board", "purpose": "Vapour Recovery System (VRS) and storm water oil separator compliance.", "portal": "State SPCB Portal"},
            {"license": "Legal Metrology Verification Certificate (Nozzle Stamping)", "authority": "Department of Legal Metrology", "purpose": "Mandatory periodic stamping and calibration of fuel dispensing meter nozzles to guarantee zero fuel delivery cheating.", "portal": "e-Measure Portal (e-measure.gov.in)"},
            {"license": "GST Registration (Goods and Services Tax)", "authority": "CBIC", "purpose": "Mandatory tax registration for retail fuel sales and convenience lubricants.", "portal": "GST Portal (www.gst.gov.in)"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Statutory retail trade credit guarantee and government MSME benefits.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "IS 2796:2017 (Automotive Gasoline - BS VI Specification)",
            "IS 1460:2017 (Automotive Diesel Fuel - BS VI Specification)",
            "Legal Metrology (Weights & Measures) Verification (Monthly stamping of dispensing nozzle meter accuracy)",
            "OISD-STD-141 / OISD-GDN-169 (Design & Safety Requirements for Retail Fuel Outlets)"
        ],
        "step_by_step_setup": [
            "Step 1: Obtain Letter of Intent (LOI) from Oil Marketing Company (IOCL, BPCL, HPCL, Reliance, Nayara).",
            "Step 2: Secure DM/DC NOC and NHAI access clearance.",
            "Step 3: Construct underground tanks and dispensing forecourt adhering to PESO and OISD standards.",
            "Step 4: Complete calibration inspection by Legal Metrology and receive PESO final Form XII license."
        ]
    },
    "ev_charging_station": {
        "business_type": "EV Charging Station (Electric Vehicle Public Charging Infrastructure)",
        "keywords": ["ev charging", "electric vehicle charging", "ev station", "charging point", "open ev charging", "ev charger", "public charging station"],
        "mandatory_licenses": [
            {"license": "Central Electricity Authority (CEA) Technical Compliance Clearance", "authority": "Central Electricity Authority (CEA) / State Discom", "purpose": "Grid connectivity approval and dedicated EV tariff transformer setup.", "portal": "State Discom Portal"},
            {"license": "Municipal Commercial NOC / Trade Permit", "authority": "Urban Local Body", "purpose": "Parking bay allocation and commercial vehicle accessibility.", "portal": "Municipal Portal"},
            {"license": "Fire Safety NOC", "authority": "State Fire Services", "purpose": "Electrical short-circuit suppression and fire safety inspection.", "portal": "State Fire Services Portal"},
            {"license": "GST Registration (18% EV Charging Services Slab)", "authority": "CBIC", "purpose": "Mandatory tax registration for billing commercial charging services.", "portal": "www.gst.gov.in"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Eligibility for FAME-II government subsidies and priority electrical infrastructure financing.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "IS 17017 (Part 1, 21, 23, 24): Electric Vehicle Conductive AC/DC Charging Systems",
            "CEA (Measures relating to Safety and Electric Supply) Regulations",
            "MoP Guidelines and Standards for Public Charging Infrastructure (Open Access Protocol)"
        ],
        "step_by_step_setup": [
            "Step 1: Secure dedicated parking space with minimum 3.5m clearance and apply to State Discom for high-tension (HT/LT) EV connection.",
            "Step 2: Install ARAI/ICAT certified CCS-2, CHAdeMO, or Type-2 AC chargers conforming to IS 17017.",
            "Step 3: Integrate with national EV Charging Network app using Open Charge Point Protocol (OCPP 1.6/2.0.1).",
            "Step 4: Undergo Electrical Inspectorate inspection before commercial energization."
        ]
    },
    "auto_service_garage_wash": {
        "business_type": "Automobile Service Garage, Mechanic Workshop & Car Washing Center",
        "keywords": ["car wash", "auto garage", "car service", "bike mechanic", "car repair", "automobile workshop", "detailing", "water wash", "open car wash"],
        "mandatory_licenses": [
            {"license": "Consent to Establish & Operate (CTE/CTO)", "authority": "State Pollution Control Board (SPCB)", "purpose": "Mandatory effluent treatment plant (ETP) for oil-grease separation and water recycling.", "portal": "State PCB Portal"},
            {"license": "Municipal Trade License", "authority": "Local Municipal Corporation", "purpose": "Commercial auto service trade clearance.", "portal": "Municipal Citizen Services"},
            {"license": "Shops & Establishments Act Registration", "authority": "State Labour Department", "purpose": "Commercial premise permit.", "portal": "State Labour Portal"},
            {"license": "GST & MSME Udyam Registration", "authority": "CBIC & MSME", "purpose": "Input tax credit on hydraulic lifts, compressors, and lubricants.", "portal": "www.gst.gov.in"}
        ],
        "key_standards": [
            "Water (Prevention and Control of Pollution) Act 1974 (Zero untreated oil/sludge discharge)",
            "IS 10500:2012 (Groundwater extraction rules and mandatory rain-water harvesting for commercial washers)",
            "Hazardous and Other Wastes Rules 2016 (Authorized recycler disposal of used engine oil)"
        ],
        "step_by_step_setup": [
            "Step 1: Install three-chambered oil-water separator / ETP with sludge drying bed.",
            "Step 2: Obtain SPCB Consent and Municipal Trade License.",
            "Step 3: Execute contract with CPCB-authorized re-refiner for collecting waste engine oil.",
            "Step 4: Register MSME Udyam for subsidized equipment financing."
        ]
    },
    "fertilizer_pesticide_seed": {
        "business_type": "Agrochemicals, Fertilizer Dealer, Pesticides & Certified Seeds Store",
        "keywords": ["fertilizer", "pesticide", "seeds", "urea", "dap", "khad", "agrochemicals", "agri store", "krishi kendra", "open fertilizer shop"],
        "mandatory_licenses": [
            {"license": "Fertilizer Dealer License (Form A2 / FCO)", "authority": "District Agriculture Department (District Agriculture Officer - DAO)", "purpose": "Mandatory authorization under Fertilizer (Control) Order 1985.", "portal": "State Agriculture Portal / NSWS"},
            {"license": "Insecticide / Pesticide Sale License", "authority": "Licensing Officer / Joint Director of Agriculture", "purpose": "Statutory permit under Insecticides Act 1968 (Mandatory B.Sc Agriculture or Chemistry qualification).", "portal": "State Agriculture Portal"},
            {"license": "Seed Dealer License", "authority": "District Seed Licensing Authority", "purpose": "Statutory permit under Seeds (Control) Order 1983 / Seeds Act 1966.", "portal": "State Agriculture Single Window"},
            {"license": "GST Registration (5% Agri Input Slab)", "authority": "CBIC", "purpose": "Direct Benefit Transfer (DBT) POS machine integration.", "portal": "www.gst.gov.in"},
            {"license": "MSME Udyam Registration (Free & Lifetime)", "authority": "Ministry of Micro, Small and Medium Enterprises", "purpose": "Collateral-free agricultural trade loans, subsidized POS terminals, and priority MSME sector benefits.", "portal": "Udyam Registration Portal (udyamregistration.gov.in)"}
        ],
        "key_standards": [
            "IS 540 (Urea, Fertilizer Grade Specifications)",
            "IS 824 (Di-ammonium Phosphate - DAP Specifications)",
            "Fertilizer Control Order (Mandatory maximum retail price - MRP compliance & POS machine biometric billing)",
            "Insecticides Rules 1971 (Poison and antidote first aid display requirements)"
        ],
        "step_by_step_setup": [
            "Step 1: Verify educational qualification (B.Sc Agriculture / Chemistry graduate or diploma in agri-inputs).",
            "Step 2: Obtain Principal Certificate from manufacturing companies (IFFCO, KRIBHCO, Coromandel, etc.).",
            "Step 3: Apply for Fertilizer (FCO) and Pesticide license at the District Agriculture Office.",
            "Step 4: Install Government DBT POS machine connected to the e-Urvarak portal for biometric farmer authentication."
        ]
    },
    "hotel_resort_lodge": {
        "business_type": "Hotel, Commercial Lodge, Resort, Guest House & Homestay",
        "keywords": ["hotel", "lodge", "resort", "guest house", "homestay", "boarding", "motel", "open a hotel", "pg", "lodging"],
        "mandatory_licenses": [
            {"license": "State Police Lodging License / Sarai Act Registration", "authority": "District Police Commissioner / DM Office", "purpose": "Public safety, guest identity verification (Form C for foreign guests).", "portal": "State Police Portal"},
            {"license": "Fire Safety No Objection Certificate (NOC)", "authority": "State Fire Services Department", "purpose": "Mandatory fire safety inspection (NBC 2016 Part 4).", "portal": "State Fire Services Portal"},
            {"license": "FSSAI Food Business License (State / Central)", "authority": "FSSAI", "purpose": "Mandatory hygiene license for hotel restaurant, banquet, and room service.", "portal": "foscos.fssai.gov.in"},
            {"license": "Consent to Establish & Operate (CTE/CTO)", "authority": "State Pollution Control Board", "purpose": "Sewage Treatment Plant (STP) and diesel generator noise limits.", "portal": "State PCB Portal"},
            {"license": "Municipal Health Trade License & Star Classification", "authority": "Urban Local Body & Ministry of Tourism (HRACC)", "purpose": "Commercial lodging permit and star categorization.", "portal": "hotelcloud.nic.in"}
        ],
        "key_standards": [
            "IS 10500:2012 (Drinking Water for all guest rooms and banquet facilities)",
            "IS 2491:2013 (Food Hygiene for commercial hospitality dining)",
            "NBC 2016 Part 4 (Fire & Life Safety for Commercial Residential Buildings)"
        ],
        "step_by_step_setup": [
            "Step 1: Construct building complying with National Building Code (NBC 2016) with dual fire staircases and hydrants.",
            "Step 2: Secure Fire Safety NOC and SPCB Consent to Operate.",
            "Step 3: Obtain Police Lodging License and FSSAI Hotel License on FoSCoS.",
            "Step 4: Apply for voluntary Star Classification on Ministry of Tourism HRACC portal."
        ]
    },
    "drone_uav_enterprise": {
        "business_type": "Drone Manufacturing, UAV Technology Assembly, Drone Pilot Training & Rental",
        "keywords": ["drone", "uav", "quadcopter", "drone manufacturing", "drone rental", "aerial survey", "open drone company", "drone business"],
        "mandatory_licenses": [
            {"license": "DGCA Type Certificate & Drone Registration (UIN)", "authority": "Directorate General of Civil Aviation (DGCA)", "purpose": "Mandatory airworthiness certificate and Unique Identification Number on DigitalSky portal.", "portal": "digitalsky.dgca.gov.in"},
            {"license": "BIS Compulsory Registration Scheme (CRS) for Drone Batteries", "authority": "Bureau of Indian Standards (BIS)", "purpose": "Mandatory R-Number verification for Lithium-ion propulsion batteries under IS 16046.", "portal": "www.crsbis.in"},
            {"license": "Wireless Planning & Coordination (WPC) ETA Clearance", "authority": "Department of Telecommunications (DoT)", "purpose": "Equipment Type Approval (ETA) for radio frequency transmitter controllers.", "portal": "saralsanchar.gov.in"},
            {"license": "Factories Act / MSME Udyam Registration", "authority": "State DISH & Ministry of MSME", "purpose": "Manufacturing assembly unit registration and PLI Drone Scheme benefits.", "portal": "udyamregistration.gov.in"}
        ],
        "key_standards": [
            "Drone Rules 2021 (DGCA Safety & No-Permission No-Takeoff - NPNT compliance)",
            "IS 16046 (Secondary Cells and Batteries Containing Alkaline or Other Non-Acid Electrolytes)",
            "IS/ISO 9001:2015 (Aerospace and UAV Quality Management)"
        ],
        "step_by_step_setup": [
            "Step 1: Prototype drone and obtain WPC radio frequency approval for 2.4 GHz / 5.8 GHz telemetry links.",
            "Step 2: Submit drone prototype to designated testing laboratory for DGCA Type Certification on DigitalSky.",
            "Step 3: Ensure all lithium propulsion battery packs hold authentic BIS CRS R-Numbers.",
            "Step 4: Apply for Ministry of Civil Aviation PLI (Production Linked Incentive) scheme for drone manufacturers."
        ]
    }
}


class OnlineStandardsResolver:
    """
    Intelligent Dynamic Standards & Government Licensing Resolver.
    Searches, synthesizes, and auto-indexes authoritative Indian Standards (IS Codes),
    ISO Harmonized Standards, and Commercial Store/Shop Licensing profiles from official Government of India portals.
    """

    def __init__(self):
        pass

    def resolve_iso_or_store_licensing(self, query: str, mode: str = "industry") -> Optional[Dict[str, Any]]:
        """
        Dynamically resolves ISO standards or Commercial Store/Shop setup inquiries
        with official Government of India licensing frameworks, acts, and portal URLs.
        Auto-indexes the structured data into ChromaDB and BM25.
        """
        q = query.lower().strip()
        is_consumer = (mode.lower() == "consumer")
        
        # Check if query is explicitly non-commercial, civic, or out of domain
        non_commercial_exclusions = [
            "passport", "driving license", "driving licence", "driver license", "driver licence",
            "learner license", "learner licence", "rto", "rc book", "vehicle registration",
            "pan card", "voter id", "election card", "aadhaar", "uidai", "ration card",
            "birth certificate", "death certificate", "marriage certificate", "caste certificate",
            "income certificate", "domicile certificate", "residence certificate",
            "visa", "citizenship", "police verification", "fir", "police complaint",
            "court case", "divorce", "bail", "challan", "traffic fine",
            "railway ticket", "train ticket", "irctc", "flight ticket", "bus ticket", "metro card",
            "cricket", "football", "sports", "world cup", "olympics", "match", "movie", "cinema",
            "weather", "climate", "temperature", "rain", "joke", "comedy", "recipe", "how to cook",
            "coding", "programming", "python", "javascript", "algorithm",
            "who is", "who was", "who won", "president of", "prime minister of", "capital of"
        ]
        if any(re.search(rf'\b{re.escape(ex)}\b', q) for ex in non_commercial_exclusions):
            return None

        # 0. Normalize vernacular, regional slang and common typos
        normalized_q = q
        for typo, standard_term in VERNACULAR_AND_TYPO_MAP.items():
            if re.search(rf'\b{re.escape(typo)}\b', normalized_q, re.IGNORECASE):
                normalized_q = re.sub(rf'\b{re.escape(typo)}\b', standard_term, normalized_q, flags=re.IGNORECASE)

        # 1. Check Master Everyday Commodities & Products 360 Knowledge Graph
        for comm_key, comm_data in MASTER_COMMODITIES_STANDARDS_GRAPH.items():
            if comm_key in normalized_q or any(k in q or k in normalized_q for k in comm_data["keywords"]):
                if is_consumer:
                    lines = [
                        f"### 🛡️ Citizen Quality & Safety Guide: {comm_data['title']}",
                        f"**Statutory Protection:** Mandatory Bureau of Indian Standards (BIS Act 2016) & FSSAI Standards",
                        f"**Enforcing Authorities:** BIS, FSSAI & Ministry of Consumer Affairs",
                        "",
                        "#### 🔍 What Consumers Must Check Before Purchasing (Safety Checklist):",
                    ]
                    for cg in comm_data["consumer_guide"]:
                        lines.append(f"- **Safety Rule:** {cg}")
                    
                    lines.append("")
                    lines.append("#### 📲 How to Verify on Official BIS Care Mobile App & Report Substandard Goods:")
                    lines.append("1. Download the official **BIS Care Mobile App** from Google Play Store or Apple App Store.")
                    lines.append("2. Tap **'Verify License Details' (Verify CM/L)** or **'Verify HUID'**.")
                    lines.append("3. Enter the 7/8-digit CM/L license number from the package to view genuine manufacturer details, brand name, and validity.")
                    lines.append("4. If the product is substandard, lacks an authentic CM/L number, or the ISI mark is forged, tap **'Lodge Complaint'** in the app or call **1915** (National Consumer Helpline).")
                else:
                    lines = [
                        f"### 🏢 Business Compliance & Manufacturing Guide: {comm_data['title']}",
                        f"**Statutory Framework:** Bureau of Indian Standards (BIS Act 2016), FSSAI & Ministry of MSME",
                        f"**Central Digital Application Portal:** [{OFFICIAL_GOV_PORTALS['NSWS']['name']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})",
                        "",
                        "#### 🏪 Mandatory Statutory Licenses for Selling / Manufacturing:",
                    ]
                    for idx, bg in enumerate(comm_data["business_guide"], 1):
                        lines.append(f"{idx}. **{bg['license']}**")
                        lines.append(f"   - **Issuing Authority:** `{bg['authority']}`")
                        lines.append(f"   - **Official Application Portal:** [{bg['portal']}](https://{bg['portal']})")
                    
                    lines.append("")
                    lines.append("#### 📐 Applicable Indian Standards (IS Codes) & Quality Orders:")
                    for std in comm_data["standards"]:
                        lines.append(f"- {std}")
                    
                    lines.append("")
                    lines.append("#### 🚀 Step-by-Step Government Setup & Verification Roadmap:")
                    for step in comm_data["setup_steps"]:
                        lines.append(step)
                    
                    lines.append("")
                    lines.append("#### 🔗 Direct Official Government Portal Links:")
                    lines.append(f"- **National Single Window System (NSWS):** [{OFFICIAL_GOV_PORTALS['NSWS']['url']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})")
                    lines.append(f"- **Udyam MSME Registration (Free):** [{OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']}]({OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']})")
                    lines.append(f"- **BIS Manakonline Portal:** [{OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']}]({OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']})")
                    lines.append(f"- **FSSAI FoSCoS Portal:** [{OFFICIAL_GOV_PORTALS['FSSAI_FOSCOS']['url']}]({OFFICIAL_GOV_PORTALS['FSSAI_FOSCOS']['url']})")
                
                formatted_text = "\n".join(lines)
                
                # Auto-index single chunk safely without duplication
                self._auto_index_single_chunk(
                    is_code=f"Gov Commodity Standard: {comm_key.upper()}",
                    title=comm_data["title"],
                    clause="360° Citizen Quality & Statutory Licensing Guide",
                    text=formatted_text
                )
                
                return {
                    "type": "COMMODITY_360",
                    "code": comm_data["title"][:50],
                    "title": comm_data["title"][:200],
                    "answer": formatted_text,
                    "portal": OFFICIAL_GOV_PORTALS["NSWS"]["url"],
                    "scheme": "360° Dual Quality & Commercial Standards",
                    "action_chips": comm_data.get("action_chips", [])
                }

        # 2. Check for ISO Standards
        for iso_key, iso_data in ISO_STANDARDS_GOV_REGISTRY.items():
            if any(k in q for k in iso_data["domains"]) or f"iso {iso_key}" in q or f"iso{iso_key}" in q:
                if is_consumer:
                    lines = [
                        f"### 🛡️ Citizen Guide: Understanding {iso_data['is_code']} ({iso_data['iso_code']})",
                        f"**Full Specification Title:** *{iso_data['title']}*",
                        f"**Governing Authority:** {iso_data['department']} / Bureau of Indian Standards",
                        "",
                        "#### 📖 What This Standard Guarantees to Indian Consumers:",
                        f"{iso_data['summary']}",
                        "",
                        "#### 🔍 Key Consumer Takeaways:",
                        "- Organizations certified under this standard have passed independent third-party audits verifying strict quality control, continuous monitoring, and accountability.",
                        "- It ensures that consumer grievances are formally logged, tracked, and remediated under standard operating procedures (SOPs).",
                        "",
                        "#### 📲 How to Verify Certificate Authenticity:",
                        "- Ask the supplier for their accreditation certificate.",
                        "- Verify the accreditation body is recognized by the **National Accreditation Board for Certification Bodies (NABCB - Quality Council of India)** at [qcin.org/nabcb](https://qcin.org/nabcb)."
                    ]
                else:
                    lines = [
                        f"### 🌐 Official Statutory Standard: {iso_data['is_code']} ({iso_data['iso_code']})",
                        f"**Full Specification Title:** *{iso_data['title']}*",
                        f"**BIS Standardization Department:** `{iso_data['department']}`",
                        f"**Statutory Certification Scheme:** `{iso_data['cert_scheme']}`",
                        f"**Governing Statutory Act:** {iso_data['statutory_act']}",
                        f"**Official Government Portal:** [{OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['name']}]({iso_data['portal_url']})",
                        "",
                        f"#### 📖 Standard Scope & Objectives:",
                        f"{iso_data['summary']}",
                        "",
                        "#### 📊 Key Clauses & Auditing Requirements:",
                    ]
                    for clause in iso_data["key_clauses"]:
                        lines.append(f"- **{clause}**")
                    
                    lines.append("")
                    lines.append("#### 🏛️ Step-by-Step Government Certification Procedure:")
                    for step in iso_data["steps"]:
                        lines.append(step)
                    
                    lines.append("")
                    lines.append("#### 🔗 Official Government & Accreditation Resources:")
                    lines.append(f"- **BIS Manakonline Portal:** [{OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']}]({OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']})")
                    lines.append(f"- **National Single Window System (NSWS):** [{OFFICIAL_GOV_PORTALS['NSWS']['url']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})")
                    lines.append(f"- **NABCB (Quality Council of India):** [https://qcin.org/nabcb](https://qcin.org/nabcb)")
                
                formatted_text = "\n".join(lines)
                
                self._auto_index_single_chunk(
                    is_code=iso_data["is_code"],
                    title=iso_data["title"],
                    clause="Clause 4.0 to 10.0 (Master Management Framework)",
                    text=formatted_text
                )
                
                return {
                    "type": "ISO_STANDARD",
                    "code": iso_data["is_code"],
                    "title": iso_data["title"],
                    "answer": formatted_text,
                    "portal": iso_data["portal_url"],
                    "scheme": iso_data["cert_scheme"]
                }

        # 3. Check for Store / Shop / Commercial Business Licensing
        for store_key, store_data in COMMERCIAL_STORES_LICENSING_REGISTRY.items():
            matched_kws = [
                k for k in store_data["keywords"]
                if re.search(rf'(?<!\w){re.escape(k)}(?!\w)', q) or re.search(rf'(?<!\w){re.escape(k)}(?!\w)', normalized_q)
            ]
            if matched_kws:
                if is_consumer:
                    if store_key == "juice_beverage_center":
                        lines = [
                            f"### 🛡️ Citizen Protection & Safety Guide: Fresh Fruit Juices, Sugarcane Juice & Beverage Centers",
                            "**Statutory Framework:** Food Safety and Standards Act 2006 (FSSAI Schedule 4), Consumer Protection Act 2019 & IS 10500 Potable Water Standards",
                            "",
                            "#### 🔍 What Citizens Must Check When Buying Juices (The 4-Point Safety Checklist):",
                            "1. **Potable Ice & Water Quality:** Ensure ice is made from certified potable water (IS 10500 compliant). Beware of large industrial cooling ice blocks transported on bare vehicle beds or burlap sacks — they frequently carry severe bacterial contaminants (E. coli / Coliforms).",
                            "2. **Food-Grade Extraction Machinery (SS 304):** Sugarcane crusher rollers and fruit extractor blades must be food-grade stainless steel (SS 304). Verify that black machine motor oil or bearing grease is NOT leaking onto the sugarcane stalks or into the juice collection tray.",
                            "3. **Zero Artificial Sweeteners & Toxic Dyes:** Natural juice must be extracted without illegal artificial sweeteners (e.g. Saccharin, which leaves a metallic chemical aftertaste) or unpermitted synthetic coal-tar food dyes.",
                            "4. **FSSAI License & Stalk Cleanliness:** The 14-digit FSSAI Registration number must be displayed. Sugarcane stalks must have outer muddy nodes washed and peeled, stored off the ground away from street dust.",
                            "",
                            "#### ⚠️ Consumer Red Flags & Health Hazards:",
                            "- Crushed ice stored in murky water or in direct contact with dirt/sawdust.",
                            "- Black machine grease dripping near roller gears into the juice cup.",
                            "- Swarms of houseflies settling on unpeeled cane piles or sliced fruits.",
                            "- Glasses washed by dipping in a single bucket of dirty standing water.",
                            "- Artificially neon bright juice with a chemical aftertaste (Saccharin or non-permitted dyes).",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- Report unhygienic juice stalls or adulterated beverages to the **FSSAI Food Safety Connect App** or notify your local Municipal Food Safety Officer.",
                            "- Call the **National Consumer Helpline (NCH)** toll-free at **1915**."
                        ]
                    elif store_key == "fssai_food_licensing":
                        lines = [
                            f"### 🛡️ Citizen Protection & Safety Guide: FSSAI Food Safety Licensing & Standards",
                            "**Statutory Framework:** Food Safety and Standards Act 2006 (FSSAI Schedule 4), Consumer Protection Act 2019 & IS 10500 Drinking Water Standards",
                            "",
                            "#### 🔍 What Citizens Must Check (Food Safety & FSSAI Verification Checklist):",
                            "1. **Verify 14-Digit FSSAI License Number:** Look for the 14-digit FSSAI number printed on bill receipts, food delivery packages, and displayed prominently on entrance counters. You can verify validity instantly using the **FSSAI Food Safety Connect App** or by entering the number on the **FoSCoS Consumer Portal** (foscos.fssai.gov.in).",
                            "2. **Food Safety Display Board (FSDB):** Every legitimate restaurant, cafe, sweet shop, food cart, and juice bar must display a color-coded FSDB board at the front counter displaying their 14-digit license, basic hygiene do's and don'ts, and the Food Safety Officer's contact details.",
                            "3. **Water, Ice & Hygiene Standards (IS 10500 & IS 2491):** Verify that drinking water and ice used in food/beverage preparation are prepared from potable water (IS 10500 compliant with zero E. coli). Check for food-grade stainless steel (SS 304) utensils and clean, covered storage.",
                            "4. **Packaging & Allergen Disclosures:** Packaged and takeaway foods must display the Green/Brown Veg/Non-Veg logo, Manufacturing & Expiry/Best Before date, complete ingredient list, nutritional information, batch number, and allergen declarations.",
                            "",
                            "#### ⚠️ Consumer Red Flags & Adulteration Hazards:",
                            "- Absence of 14-digit FSSAI number on bill, board, or takeaway packaging.",
                            "- Dark, murky, repeatedly reheated cooking oil (RUCO violation - high carcinogenic Total Polar Compounds > 25%).",
                            "- Use of unpermitted synthetic coal-tar dyes (e.g., Rhodamine B, Metanil Yellow, Malachite Green) or prohibited chemical sweeteners (Saccharin in fresh juice).",
                            "- Roadside ice stored in burlap/sawdust bags made from contaminated non-potable water.",
                            "- Sick food handlers with visible skin rashes or coughing without aprons/hairnets.",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- Report adulteration, stale food, foreign objects, or unlicensed eateries on the official **FSSAI Food Safety Connect App** (available on Android & iOS).",
                            "- Lodge statutory grievances on the **National Consumer Helpline (NCH)** by calling toll-free **1915** or visiting [consumerhelpline.gov.in](https://consumerhelpline.gov.in).",
                            "- Contact the District Designated Officer (DO) or Food Safety Officer (FSO) at your local Municipal Health Office."
                        ]
                    elif store_key in ["restaurant_food", "bakery_confectionery", "fast_food_chinese_stall"]:
                        lines = [
                            f"### 🛡️ Citizen Protection & Safety Guide: {store_data['business_type']}",
                            "**Statutory Framework:** Food Safety and Standards Act 2006 (FSSAI Schedule 4), Consumer Protection Act 2019 & IS 2491 Food Hygiene Standards",
                            "",
                            "#### 🔍 What Citizens Must Check (Food Safety & Hygiene Checklist):",
                            "1. **FSSAI Food Safety Display Board (FSDB):** Look for the green FSSAI Food Safety Display Board prominently hung at the counter showing the 14-digit FSSAI license/registration number.",
                            "2. **Potable Cooking & Drinking Water:** Verify that drinking water and food preparation water conforms to IS 10500 potable standards.",
                            "3. **Cooking Oil Quality:** Commercial kitchens must not reuse cooking oil repeatedly until it turns black or forms toxic Total Polar Compounds (TPC > 25%).",
                            "4. **Food Handler Cleanliness:** Kitchen and service staff must wear clean aprons, hairnets, and exhibit clean personal hygiene (Form VII medical fitness).",
                            "",
                            "#### ⚠️ Consumer Red Flags:",
                            "- Open, uncovered cooked food swarmed by flies or left near open drains.",
                            "- Foul-smelling, dark foaming cooking oil being reused repeatedly.",
                            "- Refusal to provide an itemized bill or absence of the 14-digit FSSAI number.",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- Lodge complaints regarding food poisoning or unhygienic restaurants on the **FSSAI FoSCoS / Food Safety Connect App**.",
                            "- Call the **National Consumer Helpline (NCH)** at **1915**."
                        ]
                    elif store_key == "petrol_fuel_bunk":
                        lines = [
                            f"### 🛡️ Citizen Protection & Consumer Rights: {store_data['business_type']}",
                            "**Statutory Framework:** Legal Metrology Act 2009, Petroleum Act 1934 & Consumer Protection Act 2019",
                            "",
                            "#### 🔍 What Consumers Have the Statutory Right to Check (Free of Cost at Every Petrol Pump):",
                            "1. **Zero Reset on Dispenser:** Always verify that the fuel dispensing screen displays exactly `0.00` Litres and `₹ 0.00` before fueling begins.",
                            "2. **5-Litre Quantity Check (Legal Metrology):** Every fuel pump is legally required to provide an authentic, stamped 5-litre conical measure upon customer request to verify delivery accuracy.",
                            "3. **Filter Paper Quality Test (Free):** For petrol, request a sheet of Whatman filter paper. Put a drop of petrol on it; if it evaporates in 2 minutes leaving no stain or ring, fuel is 100% pure. A colored ring indicates kerosene adulteration.",
                            "4. **Hydrometer Density Test:** Consumers can ask the fuel pump manager to verify density against the morning reference density register (IS 2796 for Petrol: 720–775 kg/m³; IS 1460 for Diesel: 820–860 kg/m³).",
                            "",
                            "#### ⚠️ Consumer Red Flags:",
                            "- Nozzle meter jumping straight from 0 to 5 or 10 rupees without continuous smooth flow.",
                            "- Dispenser nozzle lacking the mandatory stamped inspection seal of the Legal Metrology officer.",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- Note the Pump Name, OMC (IOCL/BPCL/HPCL), Nozzle Number, and report immediately on the OMC grievance toll-free helpline.",
                            "- File an e-complaint on the **National Consumer Helpline (NCH)** via **1915** or Legal Metrology Department portal."
                        ]
                    elif store_key == "jewellery_gold_silver":
                        lines = [
                            f"### 🛡️ Citizen Protection & Buying Guide: {store_data['business_type']}",
                            "**Statutory Framework:** Section 14, BIS Act 2016 (Mandatory Gold Hallmarking) & Consumer Protection Act 2019",
                            "",
                            "#### 🔍 What Citizens Must Check (The 3 Mandatory BIS Hallmarks on Gold):",
                            "1. **BIS Triangular Logo:** Official hallmark symbol of the Bureau of Indian Standards.",
                            "2. **Purity / Fineness Mark:** Clearly indicating gold purity (e.g. `22K916` for 22 Karat 91.6% pure gold, `18K750` for 18 Karat 75.0% pure gold, or `14K585`).",
                            "3. **6-Digit Alphanumeric HUID:** Unique Hallmark Unique Identification code laser-engraved on every single jewellery piece (e.g. `AB1234`).",
                            "4. **10X Magnifying Glass & Scale:** The jeweller is legally required to provide a 10X magnifying glass for you to read the HUID and a Legal Metrology certified Class-II scale.",
                            "",
                            "#### 📲 How to Verify HUID on the BIS Care Mobile App:",
                            "1. Open the official **BIS Care App** and select **'Verify HUID'**.",
                            "2. Enter the 6-digit alphanumeric code engraved on your gold article.",
                            "3. The app instantly displays: Jeweller Name, Assaying & Hallmarking Centre (AHC), Date of Hallmarking, Purity, and Article Type.",
                            "4. If unhallmarked or HUID doesn't match, report instantly via the app or call **1915**."
                        ]
                    elif store_key == "pharmacy_medical":
                        lines = [
                            f"### 🛡️ Citizen Protection & Safety Guide: {store_data['business_type']}",
                            "**Statutory Framework:** Drugs and Cosmetics Act 1940, Pharmacy Act 1948 & Consumer Protection Act 2019",
                            "",
                            "#### 🔍 What Citizens Must Check When Purchasing Medicines:",
                            "1. **Registered Pharmacist on Duty:** A qualified registered pharmacist (holding D.Pharm/B.Pharm registration) must dispense medicines personally.",
                            "2. **Batch Number & Expiry Date:** Check the blister foil or vial for clear batch printing and ensure the medicine has not crossed its Expiry Date.",
                            "3. **Tamper-Evident Packaging:** Confirm that foil blister seals, bottle caps, or insulin vials are completely intact without punctures or discoloration.",
                            "4. **Itemized Tax Invoice:** Always demand a valid cash memo / tax invoice detailing drug name, batch number, expiry date, MRP, and the pharmacy's Drug License Number.",
                            "",
                            "#### ⚠️ Consumer Red Flags:",
                            "- Loose individual pills dispensed without foil packaging or visible expiry date.",
                            "- Faint or blurred batch printing or re-stickered expiry dates.",
                            "- Antibiotics or Schedule H/H1/X drugs offered without a valid doctor's prescription.",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- Report counterfeit or expired drugs to the **State Drugs Control Department** or CDSCO.",
                            "- File a complaint on the **National Consumer Helpline (NCH)** via **1915**."
                        ]
                    else:
                        lines = [
                            f"### 🛡️ Citizen Protection & Safety Guide: {store_data['business_type']}",
                            "**Statutory Framework:** Consumer Protection Act 2019, Legal Metrology Rules & BIS Act 2016",
                            "",
                            "#### 🔍 What Citizens Must Check When Purchasing from This Store:",
                            "1. **Statutory Licenses on Display:** Look for the municipal trade license, Shop Act certificate, and relevant sectoral approvals displayed on premises.",
                            "2. **Authentic Certified Products:** Ensure packaged goods, electrical items, toys, and packaged water sold on shelves carry genuine BIS ISI marks with valid 7/8-digit CM/L numbers.",
                            "3. **Legal Metrology Weights & Measures:** Check that electronic weighing scales carry a valid annual verification stamp from the Legal Metrology inspector (tare weight of packaging excluded).",
                            "4. **Tax Receipt:** Always demand an itemized bill or tax invoice displaying the store's registered GSTIN for consumer grievance protection.",
                            "",
                            "#### 📲 Consumer Grievance & Reporting:",
                            "- If a shop sells counterfeit non-ISI products or manipulates weights, file a grievance directly on the **National Consumer Helpline (NCH)** by calling **1915** or using the **BIS Care Mobile App**."
                        ]
                else:
                    lines = [
                        f"### 🏪 Official Government Licensing & Setup Guide: {store_data['business_type']}",
                        f"**Governing Authority:** Ministry of Micro, Small and Medium Enterprises & State Governments",
                        f"**Central Digital Application Portal:** [{OFFICIAL_GOV_PORTALS['NSWS']['name']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})",
                        "",
                        "#### 📑 Mandatory Statutory Licenses & Registrations Required:",
                    ]
                    
                    for idx, lic in enumerate(store_data["mandatory_licenses"], 1):
                        lines.append(f"{idx}. **{lic['license']}**")
                        lines.append(f"   - **Issuing Authority:** `{lic['authority']}`")
                        lines.append(f"   - **Statutory Purpose:** {lic['purpose']}")
                        lines.append(f"   - **Official Application Portal:** `{lic['portal']}`")
                        lines.append("")
                    
                    lines.append("#### 📐 Applicable Indian Standards (IS Codes) & Quality Orders:")
                    for std in store_data["key_standards"]:
                        lines.append(f"- {std}")
                    
                    lines.append("")
                    lines.append("#### 🚀 Step-by-Step Government Registration Procedure:")
                    for step in store_data["step_by_step_setup"]:
                        lines.append(f"{step}")
                    
                    lines.append("")
                    lines.append("#### 🔗 Direct Official Government Portal Links:")
                    lines.append(f"- **National Single Window System (NSWS):** [{OFFICIAL_GOV_PORTALS['NSWS']['url']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})")
                    lines.append(f"- **Udyam MSME Registration (Free):** [{OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']}]({OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']})")
                    lines.append(f"- **GST Portal (CBIC):** [{OFFICIAL_GOV_PORTALS['GST_PORTAL']['url']}]({OFFICIAL_GOV_PORTALS['GST_PORTAL']['url']})")
                    lines.append(f"- **BIS Manakonline Portal:** [{OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']}]({OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']})")
                    if any(k in store_key for k in ["juice", "food", "restaurant", "bakery"]):
                        lines.append(f"- **FSSAI FoSCoS Portal:** [{OFFICIAL_GOV_PORTALS['FSSAI_FOSCOS']['url']}]({OFFICIAL_GOV_PORTALS['FSSAI_FOSCOS']['url']})")
                
                formatted_text = "\n".join(lines)
                
                # Auto-index into ChromaDB and BM25
                self._auto_index_single_chunk(
                    is_code=f"Gov Commercial Code: {store_key.upper()}",
                    title=store_data["business_type"],
                    clause="Statutory Clearances & Licences",
                    text=formatted_text
                )
                
                return {
                    "type": "STORE_LICENSING",
                    "code": store_data["business_type"],
                    "title": f"Statutory Commercial Licensing for {store_data['business_type']}",
                    "answer": formatted_text,
                    "portal": OFFICIAL_GOV_PORTALS["NSWS"]["url"],
                    "scheme": "Commercial Establishment Clearances under State & Central Acts"
                }

        # 3. Universal Autonomous Fallback: Dynamically synthesize ANY Indian business, store, manufacturing unit or trade
        dynamic_synthesis = self.dynamically_synthesize_any_business(query, mode=mode)
        if dynamic_synthesis:
            return dynamic_synthesis

        return None

    def dynamically_synthesize_any_business(self, query: str, mode: str = "industry") -> Optional[Dict[str, Any]]:
        """
        Universal Autonomous Government & Commercial Licensing Synthesizer.
        Dynamically analyzes ANY business, industry, retail shop, manufacturing unit,
        or commercial trade query, maps it to the applicable Central & State Acts,
        mandatory BIS/FSSAI/Pollution/Fire/Labour standards, and generates an official
        Government of India statutory compliance roadmap with live portal links.
        """
        q = query.lower()
        is_consumer = (mode.lower() == "consumer")
        
        # Check non-commercial exclusions
        non_commercial_exclusions = [
            "passport", "driving license", "driving licence", "driver license", "driver licence",
            "learner license", "learner licence", "rto", "rc book", "vehicle registration",
            "pan card", "voter id", "election card", "aadhaar", "uidai", "ration card",
            "birth certificate", "death certificate", "marriage certificate", "caste certificate",
            "income certificate", "domicile certificate", "residence certificate",
            "visa", "citizenship", "police verification", "fir", "police complaint",
            "court case", "divorce", "bail", "challan", "traffic fine",
            "railway ticket", "train ticket", "irctc", "flight ticket", "bus ticket", "metro card",
            "cricket", "football", "sports", "world cup", "olympics", "match", "movie", "cinema",
            "weather", "climate", "temperature", "rain", "joke", "comedy", "recipe", "how to cook",
            "coding", "programming", "python", "javascript", "algorithm",
            "who is", "who was", "who won", "president of", "prime minister of", "capital of"
        ]
        if any(re.search(rf'\b{re.escape(ex)}\b', q) for ex in non_commercial_exclusions):
            return None

        # Exclude technical, statutory, procedural, and testing inquiries (handled by BIS statutory services)
        technical_statutory_exclusions = [
            "testing infrastructure", "qualified personnel", "scheme of inspection", "sit",
            "simplified procedure", "normal procedure", "preliminary factory audit", "counter-sample",
            "counter-samples", "causes an application rejection", "application rejection",
            "fee concession", "women entrepreneur", "fmcs", "foreign manufacturer", "eco-mark", "ecomark",
            "section 16", "section 29", "quality control order", "qco", "counterfeit isi", "penalty for",
            "compensation rights", "product liability", "causes injury", "dual mrp", "multiplex",
            "fire assay", "cupellation", "compensation formula", "unhallmarked", "court-admissible",
            "concrete cube", "burnt", "loud noise and burnt", "ceyling fan", "ceiling fan", "is 12933",
            "solar water heater", "is 17088", "compostable", "is 16046", "lithium", "pm-kusum"
        ]
        if any(ex in q for ex in technical_statutory_exclusions):
            return None

        # Check if query is about starting, operating, licensing, or standardizing a commercial business or product
        commercial_triggers = [
            "open", "start", "setup", "license", "licence", "licentce", "licensing", "store", "shop", "center", "centre",
            "bunk", "factory", "unit", "business", "permit", "clearance", "scheme", "gumasta", "fssai", "foscos", "fassai", "fsai", "iso",
            "bsi", "bis", "retail", "showroom", "plant", "agency", "dealer", "distributor", "stall", "parlour",
            "salon", "bakery", "dairy", "clinic", "gym", "press", "car", "service", "farm", "mill", "workshop",
            "enterprise", "venture", "industry", "manufacturing", "franchise", "commercial", "trade", "selling",
            "sell", "requirements for", "how to make", "production", "guidelines for", "compliance for", "stall",
            "fast food", "fried rice", "biryani", "noodles", "chowmein", "momos", "pizza", "burger", "dosa", "idli",
            "street food", "chaat", "pani puri", "shawarma", "kiosk", "cart", "vendor", "eatery", "tiffin"
        ]
        
        if not any(t in q for t in commercial_triggers):
            return None

        # Clean query to extract entity name
        cleaned_name = re.sub(
            r'(?i)\b(how to open|how to start|how to setup|licenses? required for|licences? required for|steps to open|bis of|bsi of|bis for|bsi for|what is the process to open|what are the requirements for|guide for|clearances for|mandatory licenses for|open a|start a|setup a|in india)\b',
            '',
            query
        ).strip(' ?.,!:')
        
        # Apply typo correction on cleaned_name
        for typo_pat, repl in [
            (r'(?i)\blicentce\b', 'License'),
            (r'(?i)\blicence\b', 'License'),
            (r'(?i)\brestaurnt\b', 'Restaurant'),
            (r'(?i)\bresturant\b', 'Restaurant'),
            (r'(?i)\bjuce\b', 'Juice'),
            (r'(?i)\bfud\b', 'Food'),
            (r'(?i)\bfoood\b', 'Food'),
            (r'(?i)\bfassai\b', 'FSSAI'),
            (r'(?i)\bfsai\b', 'FSSAI'),
            (r'(?i)\bfssai\b', 'FSSAI')
        ]:
            cleaned_name = re.sub(typo_pat, repl, cleaned_name)

        if cleaned_name.lower().strip() in [
            "driving license", "driving licence", "driver license", "driver licence",
            "license", "licence", "licensing", "permit", "how to get driving license",
            "commercial business enterprise", "passport", "visa", "ticket", "cricket"
        ]:
            return None

        if len(cleaned_name) < 2:
            cleaned_name = "Commercial Business Enterprise"
        elif cleaned_name.lower().strip() in ["fssai", "fssai license", "fssai licence", "foscos"]:
            cleaned_name = "FSSAI Food Business Enterprise"
        else:
            cleaned_name = cleaned_name.title()

        # Classify business domain
        is_food = any(w in q for w in [
            "food", "fssai", "foscos", "fassai", "fsai", "food license", "food licence", "food licentce", "food safety",
            "cafe", "tea", "coffee", "snack", "sweet", "mithai", "dairy", "milk", "meat", "fish", "chicken",
            "poultry", "bakery", "ice cream", "juice", "juce", "restaurant", "restaurnt", "resturant", "catering", "dhaba", "canteen", "beverage",
            "sugarcane", "shake", "eatery", "rice", "fried rice", "biryani", "noodles", "chowmein", "chinese",
            "momos", "pizza", "burger", "sandwich", "shawarma", "dosa", "idli", "vada", "samosa", "chaat",
            "pani puri", "tiffin", "mess", "curry", "roti", "paratha", "kabab", "tandoor", "grill", "bbq",
            "pulao", "meals", "thali", "bhojanalaya", "street food", "stall", "cart", "kiosk", "fast food",
            "edible", "cooking", "oil", "spice", "masala", "grain", "flour", "atta", "wheat", "dal", "pulse",
            "egg rice", "veg rice", "non veg", "prawns", "pasta", "snack"
        ])
        is_health = any(w in q for w in ["drug", "chemist", "pharma", "clinic", "hospital", "ayurved", "homeo", "diagnostic", "pathology", "cosmetic", "beauty", "salon", "parlour", "spa", "wellness", "doctor", "dentist", "medicine", "nursing", "massage", "hair"])
        is_tech = any(w in q for w in ["electric", "computer", "mobile", "gadget", "battery", "inverter", "solar", "appliance", "wiring", "led", "electronics", "laptop", "software", "drone", "cctv", "camera", "charger"])
        is_hazardous = any(w in q for w in ["petrol", "diesel", "fuel", "gas", "lpg", "cng", "chemical", "paint", "solvent", "fertilizer", "pesticide", "welding", "firecracker", "explosive", "fuel station", "bunk"])
        is_manufacturing = any(w in q for w in ["factory", "manufacturing", "plant", "mill", "steel", "cement", "plastic", "pipe", "metal", "casting", "textile", "brick", "fabrication", "assembly", "production", "tannery"])

        if is_consumer:
            lines = [
                f"### 🛡️ Citizen Protection & Safety Guide: {cleaned_name}",
                "**Statutory Framework:** Consumer Protection Act 2019, Legal Metrology Rules & National Safety Standards",
                "",
                "#### 🔍 What Citizens Must Check (Consumer Safety Checklist):",
            ]
            if is_food:
                lines.extend([
                    "1. **FSSAI License Display:** Look for the 14-digit FSSAI registration/license number displayed on the premises or food cart.",
                    "2. **Potable Water & Hygiene:** Ensure water used in food/drink preparation complies with IS 10500 potable water standards.",
                    "3. **Freshness & Storage:** Verify proper hygiene, clean utensils, covered food containers, and absence of houseflies or road dust.",
                    "4. **No Adulteration:** Be alert to artificial chemical colors, prohibited synthetic sweeteners, or adulterated cooking oils."
                ])
            elif is_health:
                lines.extend([
                    "1. **Professional Qualification & Registration:** Verify that practitioners or pharmacists hold active council registrations.",
                    "2. **Product Expiry & Sealing:** Check expiry dates, intact tamper-evident packaging, and legitimate CDSCO batch details.",
                    "3. **Hygiene & Sterilization:** Ensure sterile equipment, disposable items where mandated, and safe bio-medical disposal.",
                    "4. **Valid Cash Memo:** Always obtain an itemized invoice stating batch numbers and license details."
                ])
            elif is_tech:
                lines.extend([
                    "1. **BIS CRS Registration (R-Number):** Check electronic products, power adapters, and batteries for the authentic BIS CRS mark and valid `R-XXXXXXXX` number.",
                    "2. **Authentic Accessories:** Avoid uncertified cheap chargers that pose severe battery explosion or electrical fire hazards.",
                    "3. **Warranty & Tax Invoice:** Demand a GST bill with product serial numbers for manufacturer warranty coverage.",
                    "4. **E-Waste Disposal:** Dispose of obsolete gadgets through authorized recycling collection points."
                ])
            elif is_hazardous:
                lines.extend([
                    "1. **Safety Clearances & Fire NOC:** Check that hazardous materials or fuels are stored under PESO and Fire Safety certified conditions.",
                    "2. **Legal Metrology Calibration:** Verify valid inspection stamps on fuel nozzles, measuring meters, or commercial scales.",
                    "3. **Statutory Warnings:** Confirm appropriate hazard symbols, emergency contact numbers, and caution boards are displayed.",
                    "4. **Billing & Receipts:** Insist on computer-generated tax bills with recorded meter readings or batch lots."
                ])
            elif is_manufacturing:
                lines.extend([
                    "1. **Authentic BIS ISI Mark:** Check for genuine ISI mark with verified 7/8-digit CM/L license number on products.",
                    "2. **Legal Metrology Disclosures:** Verify complete packaged commodity labels (MRP, Net Quantity, Mfg Date, Customer Care).",
                    "3. **Standard Quality:** Ensure items conform to mandatory Quality Control Orders (QCOs) issued by the Government.",
                    "4. **Consumer Recourse:** Retain warranty cards and tax invoices for grievance redressal under CPA 2019."
                ])
            else:
                lines.extend([
                    "1. **Statutory Licenses on Display:** Look for the Municipal Trade License, Shop Act (Gumasta) certificate, and GSTIN.",
                    "2. **Authentic Certified Products:** Ensure certified goods on shelves carry authentic BIS ISI marks with verified CM/L numbers.",
                    "3. **Accurate Weights & Measures:** Check that electronic weighing scales bear the annual Legal Metrology verification stamp.",
                    "4. **Itemized Tax Invoice:** Always demand a valid cash memo or tax invoice for consumer rights protection."
                ])
            lines.extend([
                "",
                "#### 📲 Consumer Grievance & Reporting:",
                "- If you encounter counterfeit products, weight manipulation, or unhygienic practices, file a grievance directly on the **National Consumer Helpline (NCH)** by calling **1915** or using the **BIS Care Mobile App**."
            ])
            if is_food:
                lines.append("- For food adulteration or unhygienic eateries, file a complaint on the **FSSAI Food Safety Connect App**.")

            formatted_text = "\n".join(lines)
            return {
                "type": "STORE_LICENSING",
                "code": cleaned_name,
                "title": f"Citizen Safety Guide for {cleaned_name}",
                "answer": formatted_text,
                "portal": OFFICIAL_GOV_PORTALS["NCH_CONSUMER"]["url"],
                "scheme": "Citizen Safety & Consumer Protection Act 2019"
            }

        mandatory_licenses = [
            {
                "license": "Shops and Commercial Establishments Act Registration (Gumasta)",
                "authority": "State Labour Department",
                "purpose": "Statutory retail establishment registration for operating commercial premises, employee rights, working hours, and local police verification.",
                "portal": "State Labour Single Window / NSWS (www.nsws.gov.in)"
            },
            {
                "license": "Municipal Trade License / Sanitary Trade Clearance",
                "authority": "Local Municipal Corporation / Urban Local Body (ULB)",
                "purpose": "Statutory permit to conduct commercial trade within local municipal jurisdiction and adhere to zoning regulations.",
                "portal": "Municipal Citizen Services Portal"
            },
            {
                "license": "Goods and Services Tax (GSTIN) Registration",
                "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
                "purpose": "Mandatory tax registration for inter-state business, input tax credit, and entities exceeding statutory turnover limits.",
                "portal": "GST Portal (www.gst.gov.in)"
            },
            {
                "license": "MSME Udyam Registration (Free Lifetime Certificate)",
                "authority": "Ministry of Micro, Small and Medium Enterprises",
                "purpose": "Statutory priority sector lending, collateral-free trade loans, 50% government fee concessions, and government subsidy benefits.",
                "portal": "Udyam Registration Portal (udyamregistration.gov.in)"
            }
        ]

        key_standards = [
            "Legal Metrology (Packaged Commodities) Rules 2011 (Mandatory MRP, Net Weight, Manufacturer Details & Customer Care labeling on all packaged goods)",
            "IS 10500:2012 (Drinking Water for commercial establishment premises and staff welfare)"
        ]

        if is_food:
            mandatory_licenses.insert(0, {
                "license": "FSSAI Food Safety License / Registration (FoSCoS)",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "purpose": "Mandatory food hygiene and safety certification under Food Safety & Standards Act 2006 (Basic < Rs. 12L; State License > Rs. 12L).",
                "portal": "FoSCoS Portal (foscos.fssai.gov.in)"
            })
            key_standards.extend([
                "IS 2491:2013 (Food Hygiene - General Principles - Code of Practice)",
                "IS 10500:2012 (Strict Zero-E.coli Potable Water Requirement for Food/Drink preparation)",
                "FSSAI Schedule 4 Sanitary Guidelines (Mandatory Form VII Medical Fitness for Food Handlers)"
            ])

        if is_health:
            mandatory_licenses.append({
                "license": "State Health Department & Bio-Medical Waste Management Authorization",
                "authority": "State Health Services & State Pollution Control Board (SPCB)",
                "purpose": "Clearance under Bio-Medical Waste Management Rules 2016 and Drugs/Cosmetics statutory provisions.",
                "portal": "State PCB Portal / CDSCO SUGAM (cdsco.gov.in)"
            })
            key_standards.append("IS/ISO 13485 (Medical Devices & Healthcare Quality Systems)")

        if is_tech:
            mandatory_licenses.append({
                "license": "BIS Compulsory Registration Scheme (CRS) & Extended Producer Responsibility (EPR)",
                "authority": "Bureau of Indian Standards & Central Pollution Control Board (CPCB)",
                "purpose": "Mandatory safety verification (R-Number) under BIS Scheme-II and E-Waste Management Rules 2022.",
                "portal": "BIS CRS Portal (www.crsbis.in) / CPCB EPR Portal"
            })
            key_standards.extend([
                "IS 13252 (Part 1):2010 (Information Technology Equipment - Safety)",
                "IS 16046 (Lithium-ion Battery Safety Standard)"
            ])

        if is_hazardous:
            mandatory_licenses.insert(0, {
                "license": "PESO Petroleum / Explosives License & Fire Safety NOC",
                "authority": "Petroleum & Explosives Safety Organization (PESO) & State Fire Services",
                "purpose": "Statutory hazardous storage permit and life safety inspection under Petroleum Rules 2002 / Explosives Act.",
                "portal": "PESO Portal (peso.gov.in)"
            })
            mandatory_licenses.append({
                "license": "Consent to Establish (CTE) and Consent to Operate (CTO)",
                "authority": "State Pollution Control Board (SPCB)",
                "purpose": "Statutory environmental clearance under Water Act 1974 and Air Act 1981.",
                "portal": "State SPCB Online Consent Management System (OCMMS)"
            })
            key_standards.extend([
                "IS 2796 (Automotive Gasoline Specs) / IS 1460 (Automotive Diesel Specs)",
                "NBC 2016 Part 4 (Fire and Life Safety Regulations)"
            ])

        if is_manufacturing:
            mandatory_licenses.insert(0, {
                "license": "Factories Act Factory License & SPCB CTE/CTO",
                "authority": "State Directorate of Industrial Safety & Health (DISH) & SPCB",
                "purpose": "Statutory industrial manufacturing license, machinery safety, and environmental emissions consent.",
                "portal": "State Single Window / NSWS (www.nsws.gov.in)"
            })
            mandatory_licenses.append({
                "license": "BIS Scheme-I Product Certification (ISI Mark License)",
                "authority": "Bureau of Indian Standards (BIS)",
                "purpose": "Grant of CM/L license number for imprinting authentic ISI mark under mandatory Quality Control Orders (QCOs).",
                "portal": "BIS Manakonline Portal (www.manakonline.in)"
            })
            key_standards.append("IS/ISO 9001:2015 (Quality Management Systems)")

        lines = [
            f"### 🏪 Official Government Licensing & Setup Guide: {cleaned_name}",
            f"**Governing Authority:** Ministry of Micro, Small and Medium Enterprises, BIS & State Governments",
            f"**Central Digital Application Portal:** [{OFFICIAL_GOV_PORTALS['NSWS']['name']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})",
            "",
            "#### 📑 Mandatory Statutory Licenses & Registrations Required:",
        ]

        for idx, lic in enumerate(mandatory_licenses, 1):
            lines.append(f"{idx}. **{lic['license']}**")
            lines.append(f"   - **Issuing Authority:** `{lic['authority']}`")
            lines.append(f"   - **Statutory Purpose:** {lic['purpose']}")
            lines.append(f"   - **Official Application Portal:** `{lic['portal']}`")
            lines.append("")

        lines.append("#### 📐 Applicable Indian Standards (IS Codes) & Quality Orders:")
        for std in key_standards:
            lines.append(f"- {std}")

        lines.append("")
        lines.append("#### 🚀 Step-by-Step Government Setup & Approval Roadmap:")
        lines.append(f"1. **Commercial Premise Registration:** Obtain Shop & Establishment Certificate (Gumasta) or Factory License on the State Single Window portal within 30 days of setup.")
        lines.append(f"2. **MSME Registration (Free):** Register your enterprise on the [Udyam Portal](https://udyamregistration.gov.in) with Aadhaar and PAN for priority trade benefits and collateral-free loan access.")
        lines.append(f"3. **Tax & Municipal Clearances:** Obtain GSTIN on [gst.gov.in](https://www.gst.gov.in) and secure Municipal Trade / Health License from the local Urban Local Body.")
        if is_food:
            lines.append(f"4. **Food Safety License:** Apply on the [FoSCoS Portal](https://foscos.fssai.gov.in) for FSSAI registration and ensure water potability complies with IS 10500.")
        elif is_hazardous:
            lines.append(f"4. **PESO & Environmental Approvals:** Apply on the [PESO Portal](https://peso.gov.in) and secure SPCB Consent to Operate (CTO).")
        elif is_manufacturing:
            lines.append(f"4. **BIS Product Certification:** Apply on [BIS Manakonline](https://www.manakonline.in) for Scheme-I ISI mark certification under the applicable Quality Control Order.")
        else:
            lines.append(f"4. **Weights & Measures Compliance:** Get all commercial weighing and measuring instruments verified and stamped by the local Legal Metrology Inspector on e-measure.")
        lines.append(f"5. **National Single Window Gateway:** Track all state and central approvals seamlessly via the unified [National Single Window System (NSWS)](https://www.nsws.gov.in).")

        lines.append("")
        lines.append("#### 🔗 Direct Official Government Portal Links:")
        lines.append(f"- **National Single Window System (NSWS):** [{OFFICIAL_GOV_PORTALS['NSWS']['url']}]({OFFICIAL_GOV_PORTALS['NSWS']['url']})")
        lines.append(f"- **Udyam MSME Registration (Free):** [{OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']}]({OFFICIAL_GOV_PORTALS['MSME_UDYAM']['url']})")
        lines.append(f"- **GST Portal (CBIC):** [{OFFICIAL_GOV_PORTALS['GST_PORTAL']['url']}]({OFFICIAL_GOV_PORTALS['GST_PORTAL']['url']})")
        lines.append(f"- **BIS Manakonline Portal:** [{OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']}]({OFFICIAL_GOV_PORTALS['BIS_MANAKONLINE']['url']})")
        if is_food:
            lines.append(f"- **FSSAI FoSCoS Portal:** [https://foscos.fssai.gov.in](https://foscos.fssai.gov.in)")

        formatted_text = "\n".join(lines)

        # Auto-index into ChromaDB and BM25 for dynamic learning
        self._auto_index_single_chunk(
            is_code=f"Gov Commercial Framework: {cleaned_name[:40].upper()}",
            title=f"Statutory Commercial Setup Guide for {cleaned_name}",
            clause="Statutory Clearances, Licences & Quality Standards",
            text=formatted_text
        )

        return {
            "type": "STORE_LICENSING",
            "code": cleaned_name,
            "title": f"Statutory Commercial Licensing for {cleaned_name}",
            "answer": formatted_text,
            "portal": OFFICIAL_GOV_PORTALS["NSWS"]["url"],
            "scheme": "Commercial Establishment Clearances under State & Central Acts"
        }

    def _auto_index_single_chunk(self, is_code: str, title: str, clause: str, text: str):
        """Helper to safely register and index dynamic synthesized government content."""
        # Intentionally disabled to preserve vector database purity and prevent false-positive leakage across unrelated queries
        return

    def search_and_index_business_standards(self, query: str) -> Optional[Dict[str, Any]]:
        """Legacy resolver hook for general industrial sectors."""
        return self.resolve_iso_or_store_licensing(query)

    def get_department_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Returns the full dictionary of all 17 BIS Technical Departments."""
        return BIS_17_TECHNICAL_DEPARTMENTS

    def get_total_standards_count(self) -> int:
        """Returns total published standards across all 17 departments (24,084)."""
        return sum(dept["published_standards"] for dept in BIS_17_TECHNICAL_DEPARTMENTS.values())

    def search_department(self, query: str) -> Optional[Dict[str, Any]]:
        """Searches for a specific department by code (e.g. SSD, LITD, ETD, FAD) or name/domain."""
        q = query.lower()
        for code, data in BIS_17_TECHNICAL_DEPARTMENTS.items():
            if code.lower() == q or f"({code.lower()})" in q or f" {code.lower()} " in f" {q} ":
                return {"code": code, **data}
            if data["name"].lower() in q or any(domain.strip().lower() in q for domain in data["domains"].split(",")):
                return {"code": code, **data}
        return None

    def get_all_departments_formatted(self) -> str:
        """Generates comprehensive markdown report for all 17 BIS Technical Departments."""
        total = self.get_total_standards_count()
        lines = [
            "### 🏛️ Bureau of Indian Standards (BIS) - 17 Technical Departments (Division Councils)",
            f"**Total Published Standards in Force:** **{total:,} Standards**",
            "",
            "| # | Department Code | Department Name | Number of Standards Published | Core Industry Scope |",
            "|---|---|---|---|---|"
        ]
        
        idx = 1
        for code, data in BIS_17_TECHNICAL_DEPARTMENTS.items():
            lines.append(
                f"| {idx} | **{code}** | {data['name']} | **{data['published_standards']:,}** | {data['domains'][:60]}... |"
            )
            idx += 1
            
        lines.append(f"| **TOTAL** | **17 DEPARTMENTS** | **Nationwide Standards Ecosystem** | **{total:,}** | **All Industrial & Consumer Sectors in India** |")
        lines.append("")
        lines.append("#### 📑 Department Breakdown & Key Highlights:")
        for code, data in BIS_17_TECHNICAL_DEPARTMENTS.items():
            lines.append(f"##### 🔹 {data['name']} ({code}) - **{data['published_standards']:,} Standards**")
            lines.append(f"- **Key Domains:** {data['domains']}")
            lines.append(f"- **Flagship Standards:** {', '.join(data['key_standards'])}")
            lines.append(f"- **Regulatory Scope:** {data['scope']}")
            lines.append("")
            
        return "\n".join(lines)


# Master Matrix of the 17 Technical Departments (Division Councils) of BIS (Total: 24,084 Standards)
BIS_17_TECHNICAL_DEPARTMENTS: Dict[str, Dict[str, Any]] = {
    "SSD": {
        "name": "Service Sector Department (SSD)",
        "published_standards": 199,
        "domains": "Banking, Financial Services, Education, Tourism, Hospitality, Legal Services, Logistics, IT-Enabled Services",
        "key_standards": ["IS 15000 (Series)", "IS 16001 (Educational Org Management)", "IS 17000 (Conformity Assessment)"],
        "scope": "Formulates standards for services quality, customer satisfaction benchmarks, service level agreements, and ethical operations."
    },
    "LITD": {
        "name": "Electronics & Information Technology Department (LITD)",
        "published_standards": 1634,
        "domains": "IT Equipment, Cyber Security, Cloud Computing, Artificial Intelligence, Smart Cards, Biometrics, Audio/Video",
        "key_standards": ["IS 13252 (IT Safety)", "IS/ISO/IEC 27001 (InfoSec)", "IS 16046 (Li-ion Batteries)", "IS 16333 (Indian Language Mobile Support)"],
        "scope": "Manages Scheme-II Compulsory Registration Scheme (CRS) in coordination with MeitY for electronics, gadgets, and cyber resilience."
    },
    "ETD": {
        "name": "Electrotechnical Department (ETD)",
        "published_standards": 1963,
        "domains": "Power Generation, Transmission, Transformers, Switchgears, Electric Motors, Inverters, Plugs & Sockets, Smart Grids",
        "key_standards": ["IS 1293 (Plugs and Sockets)", "IS 2026 (Power Transformers)", "IS 1180 (Outdoor Distribution Transformers)", "IS 694 (PVC Cables)"],
        "scope": "Governs electrical safety, energy efficiency standards, star rating interoperability with BEE, and mandatory Scheme-I ISI Mark orders."
    },
    "EED": {
        "name": "Environment & Ecology Department (EED)",
        "published_standards": 140,
        "domains": "Eco-Mark Certification, Environmental Management Systems (EMS), Carbon Footprint Verification, Wastewater Reuse, E-Waste",
        "key_standards": ["IS/ISO 14001 (EMS)", "IS/ISO 14064 (Greenhouse Gas)", "IS 17088 (Compostable Plastics)", "Eco-Mark Scheme Guidelines"],
        "scope": "Administers India's national Eco-Mark labeling scheme and environmental sustainability frameworks."
    },
    "TED": {
        "name": "Transport Engineering Department (TED)",
        "published_standards": 1343,
        "domains": "Automotive Systems, Electric Vehicles (EV), Two-Wheeler Helmets, Rail Transport, Aerospace, Shipbuilding & Marine",
        "key_standards": ["IS 4151 (Two-Wheeler Helmets)", "IS 17017 (EV Charging)", "IS 15633 (Passenger Car Tyres)", "IS/ISO 9001 TED Automotive Guides"],
        "scope": "Works with MoRTH and AISC (Automotive Industry Standards Committee) for CMVR homologation and passenger safety."
    },
    "CED": {
        "name": "Civil Engineering Department (CED)",
        "published_standards": 1951,
        "domains": "National Building Code (NBC 2016), Cement, Concrete, Ready-Mix, Earthquake Engineering, Structural Safety, Plumbing",
        "key_standards": ["IS 269 (OPC Cement)", "IS 456 (Plain & Reinforced Concrete)", "IS 1893 (Earthquake Resistant Design)", "NBC 2016 (National Building Code)"],
        "scope": "Maintains the National Building Code of India and mandatory Quality Control Orders for cement, aggregates, and structural safety."
    },
    "MSD": {
        "name": "Management & Systems Department (MSD)",
        "published_standards": 584,
        "domains": "Quality Management (QMS), Food Safety (FSMS), Occupational Health & Safety (OH&S), Anti-Bribery, Energy Management",
        "key_standards": ["IS/ISO 9001 (QMS)", "IS/ISO 22000 (Food Safety)", "IS/ISO 45001 (Occupational Health)", "IS/ISO 50001 (Energy Management)"],
        "scope": "Certifies management systems across government departments, private enterprises, and multinational organizations."
    },
    "MED": {
        "name": "Mechanical Engineering Department (MED)",
        "published_standards": 1464,
        "domains": "Industrial Boilers, Pressure Vessels, Pumps, Compressors, Material Handling, Refrigeration, Machine Tools, Fire Fighting",
        "key_standards": ["IS 2825 (Unfired Pressure Vessels)", "IS 1520 (Centrifugal Pumps)", "IS 2190 (Fire Extinguisher Selection)", "IS 800 (General Steel Construction)"],
        "scope": "Ensures industrial machinery integrity, pressure equipment safety, and workplace mechanical hazard mitigation."
    },
    "FAD": {
        "name": "Food & Agriculture Department (FAD)",
        "published_standards": 2369,
        "domains": "Packaged Drinking Water, Mineral Water, Poultry Feeds, Dairy, Infant Formula, Agricultural Equipment, Edible Oils, Spices",
        "key_standards": ["IS 14543 (Packaged Water)", "IS 13428 (Mineral Water)", "IS 1374 (Poultry Feeds)", "IS 7049 (Poultry Processing)", "IS 10500 (Potable Water)"],
        "scope": "Enforces mandatory Scheme-I ISI marks in convergence with FSSAI regulations to guarantee food safety for 1.4 billion citizens."
    },
    "PGD": {
        "name": "Production & General Engineering Department (PGD)",
        "published_standards": 2685,
        "domains": "Industrial Fasteners (Nuts/Bolts), Bearings, Precision Metrology, Engineering Drawings, Welding Consumables, Ergonomics",
        "key_standards": ["IS 1363 (Hexagon Head Bolts)", "IS 1367 (Technical Supply Conditions for Fasteners)", "IS 962 (Architectural Drawings)", "IS 814 (Welding Electrodes)"],
        "scope": "India's largest standardization department by published count (2,685 standards), underpinning all manufacturing sectors."
    },
    "PCD": {
        "name": "Petroleum, Coal & Related Products Department (PCD)",
        "published_standards": 1656,
        "domains": "BS-VI Motor Gasoline (Petrol), High Speed Diesel (HSD), LPG Cylinders, Lubricants, Bitumen, Petrochemicals, Polymers & Pipes",
        "key_standards": ["IS 2796 (Motor Gasoline Petrol)", "IS 1460 (Automotive Diesel HSD)", "IS 4984 (HDPE Pipes)", "IS 3196 (LPG Cylinders)"],
        "scope": "Standardizes clean automotive fuels, hazardous gas cylinders, and advanced polymers in collaboration with MoPNG & PESO."
    },
    "TXD": {
        "name": "Textiles Department (TXD)",
        "published_standards": 1635,
        "domains": "Technical Textiles, Geotextiles, Medical Textiles, Protective Fire-Retardant Clothing, Cotton Yarns, Silk, Jute, Man-Made Fibres",
        "key_standards": ["IS 17423 (Medical Textiles)", "IS 15748 (Protective Clothing for Firefighters)", "IS 16391 (Geotextiles)", "IS 17354 (Agrotex)"],
        "scope": "Leads India's Technical Textiles Mission and mandatory Quality Control Orders for geotextiles and medical protective wear."
    },
    "WRD": {
        "name": "Water Resources Department (WRD)",
        "published_standards": 483,
        "domains": "Irrigation Systems, Micro-Irrigation Drip/Sprinklers, Hydro-Electric Power Stations, Dam Safety, Canal Lining, Flood Control",
        "key_standards": ["IS 12786 (Irrigation Drip Lateral Pipes)", "IS 12232 (Rotary Sprinklers)", "IS 6512 (Design of Gravity Dams)", "IS 11485 (Canal Lining)"],
        "scope": "Supports the Jal Jeevan Mission and National Water Mission through precision water conservation and dam engineering standards."
    },
    "CHD": {
        "name": "Chemical Department (CHD)",
        "published_standards": 2138,
        "domains": "Industrial Chemicals, Soaps & Detergents, Paints & Coatings, Fertilizers (Urea/DAP), Pesticides, Cosmetics, Paper & Packaging",
        "key_standards": ["IS 540 (Urea)", "IS 4707 (Cosmetics Colourants & Safety)", "IS 15489 (Emulsion Paints)", "IS 2888 (Toilet Soaps)"],
        "scope": "Regulates chemical purity, limits heavy metals/lead in paints, enforces fertilizer quality under FCO, and cosmetic consumer safety."
    },
    "MHD": {
        "name": "Medical Equipment & Hospital Planning Department (MHD)",
        "published_standards": 1894,
        "domains": "Surgical Instruments, Orthopedic Implants, Diagnostic Equipment, Hospital Architecture & Cleanrooms, Syringes, Medical Face Masks",
        "key_standards": ["IS 16289 (Medical Face Masks)", "IS 10258 (Hypodermic Syringes)", "IS/ISO 13485 (Medical Device QMS)", "IS 10905 (Hospital Cleanrooms)"],
        "scope": "Aligns with CDSCO Medical Device Rules 2017 to guarantee patient safety, biocompatibility, and hospital sterility."
    },
    "MTD": {
        "name": "Metallurgical Engineering Department (MTD)",
        "published_standards": 1716,
        "domains": "TMT Rebars, Structural Steel Plates, Gold & Silver Hallmarking, Non-Ferrous Alloys (Aluminium, Copper), Foundry, Heat Treatment",
        "key_standards": ["IS 1786 (High Strength Deformed TMT Steel)", "IS 1417 (Gold Hallmarking & HUID)", "IS 2062 (Hot Rolled Structural Steel)", "IS 2112 (Silver Hallmarking)"],
        "scope": "Executes India's National Steel Policy mandates and nationwide mandatory Gold Hallmarking across all consumer jewellery."
    },
    "AYD": {
        "name": "Ayush Department (AYD)",
        "published_standards": 230,
        "domains": "Ayurveda, Yoga & Naturopathy, Unani, Siddha, Sowa-Rigpa and Homoeopathy ingredients, single herbs, polyherbal formulations",
        "key_standards": ["IS 17950 (Good Agricultural and Collection Practices for Medicinal Plants)", "IS 17890 (Single Ayurvedic Herbs)", "Ayush Premium Mark Standards"],
        "scope": "India's newest Division Council established to standardize traditional medicine purity, active markers, and global Ayush export quality."
    }
}

online_standards_resolver = OnlineStandardsResolver()
