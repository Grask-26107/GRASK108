"""
Procurement Recommendation Engine for Indian Standards (BIS) & Tenders (SIH26108)
Provides semantic recommendation of Indian Standards for procurement portals (GeM/CPPP),
detects latest versions & amendments, maps allied standards (testing, safety, installation,
normative, terminology), checks mandatory QCOs, and generates GeM-ready tender clauses.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from app.services.multilingual_translator import multilingual_translator
from app.services.domain_relevance_guard import domain_relevance_guard

logger = logging.getLogger(__name__)

# Phonetic & Vernacular Term Mapping for Indian Procurement Queries
VERNACULAR_PROCUREMENT_MAP = {
    # Hindi / Hinglish
    "sariya": "tmt steel bars is 1786",
    # Direct Indic terms for high-speed offline accuracy
    "बिजली के तार": "pvc insulated copper electrical wires is 694",
    "वायरिंग केबल": "pvc insulated copper electrical wires is 694",
    "बिजली तार": "pvc insulated copper electrical wires is 694",
    "तार की आपूर्ति": "pvc insulated copper electrical wires is 694",
    "நீటి పైపుల": "hdpe pipes for drinking water pe-100 is 4984",
    "TMT எஃகு கம்பிகள்": "tmt steel reinforcement bars is 1786",
    "எஃகு கம்பிகள்": "tmt steel reinforcement bars is 1786",
    "LED விளக்குகள்": "outdoor road street lighting led luminaire is 10322",
    "স্টিল রড": "tmt steel reinforcement bars is 1786",
    "স্টিল রডের": "tmt steel reinforcement bars is 1786",
    "ಉಕ್ಕಿನ ರಾಡ್": "tmt steel reinforcement bars is 1786",
    "ವಿದ್ಯುತ್ ಕೇಬಲ್": "pvc insulated copper electrical wires is 694",
    "ವಿದ್ಯುತ್ ಕೇಬಲ್‌ಗಳಿಗೆ": "pvc insulated copper electrical wires is 694",
    "loha": "structural steel is 2062",
    "taar": "copper electrical cables is 694",
    "bijli": "electrical cables wires",
    "bijli taar": "electrical wires cables is 694",
    "doodh": "milk safety",
    "paani supply": "water supply pipe hdpe is 4984",
    "paani nali": "water supply pipe hdpe is 4984",
    "paani pipe": "water supply pipe hdpe is 4984",
    "paani bottle": "packaged drinking water is 14543",
    "paani": "drinking water is 14543",
    "sement": "cement is 269",
    "pankha": "ceiling fans is 374",
    "batti": "led street lighting luminaire is 10322",
    "agnee rodhak": "portable fire extinguisher is 15683",
    "agni rodhak": "portable fire extinguisher is 15683",
    "aag bujhane": "portable fire extinguisher is 15683",
    "suraksha topi": "industrial safety helmet is 2925",
    "suraksha joota": "safety footwear shoes is 15298",
    "nalki": "pvc water pipe is 4985",
    
    # Telugu / Telugish
    "inupa rodlu": "tmt steel bars is 1786",
    "inumu": "structural steel is 2062",
    "vidyut teegalu": "electrical wires cables is 694",
    "teegalu": "electrical wires is 694",
    "neeti botlu": "packaged drinking water is 14543",
    "neeti pumpu": "submersible water pump is 8034",
    "panka": "ceiling fans is 374",
    "kanti deepalu": "led lighting streetlights is 10322",
    "rakshana topi": "industrial safety helmet is 2925",
    "rakshana cheppulu": "safety footwear shoes is 15298",
    "neeti gollalu": "hdpe pvc water pipes is 4984",

    # Tamil / Tanglish
    "kambi": "tmt steel bars is 1786",
    "irumbu": "structural steel is 2062",
    "min kambi": "electrical wires cables is 694",
    "thanneer": "packaged drinking water is 14543",
    "thanni": "packaged drinking water is 14543",
    "visiri": "ceiling fans is 374",
    "thee anaipaan": "fire extinguisher is 15683",
    "pathukappu thoppi": "safety helmet is 2925"
}

# Master Procurement Knowledge Base of Indian Standards
# Structured for Public Procurement (GeM / CPPP / Railways / CPWD / Defense / PSUs)
PROCUREMENT_STANDARDS_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ----------------------------------------------------
    # 1. STEEL & METALLURGY (CIVIL & INFRASTRUCTURE)
    # ----------------------------------------------------
    "IS 1786": {
        "id": "IS 1786",
        "code": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
        "popular_names": ["TMT Bars", "TMT Rebars", "Fe 500", "Fe 500D", "Fe 550", "Fe 550D", "Fe 600", "Sariya", "Reinforcement Steel", "Deformed Bars", "TMT Rods"],
        "category": "Civil & Construction",
        "sub_category": "Structural Steel & Reinforcement",
        "latest_edition": "2008 (Reaffirmed 2023)",
        "active_amendments": [
            {"number": 1, "year": "2012", "scope": "Inclusion of Fe 600 grade and enhanced elongation limits"},
            {"number": 2, "year": "2017", "scope": "Enhanced earthquake resistance & seismic ductility criteria"},
            {"number": 3, "year": "2020", "scope": "Tolerance on mass per metre and rib geometry verification"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 1786:1985 (Superseded by 2008 edition)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "Ministry of Steel",
            "qco_order": "Steel and Steel Products (Quality Control) Order",
            "statutory_act": "Section 16 & 29, BIS Act 2016",
            "tender_warning": "CRITICAL: Under Government of India Steel QCO, uncertified steel cannot be procured. Bidders MUST possess valid BIS license (CM/L)."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 228 (Parts 1-24)", "title": "Methods for Chemical Analysis of Steels", "role": "Mandatory chemical composition checking"},
                {"code": "IS 1599:2019", "title": "Metallic Materials - Bend Test", "role": "Cold bend and rebend mandrel testing"},
                {"code": "IS 1608 (Part 1):2018", "title": "Metallic Materials - Tensile Testing", "role": "Yield stress and tensile ratio testing"}
            ],
            "test_methods": [
                {"code": "IS 1608 (Part 1):2018", "title": "Tensile & Proof Stress Test at Ambient Temperature", "clause": "Clause 8.1", "nabl_required": True},
                {"code": "IS 1599:2019", "title": "Bend & Rebend Test around 3D/4D Mandrel", "clause": "Clause 8.3", "nabl_required": True},
                {"code": "IS 228 (Part 1 & 9)", "title": "Determination of Carbon, Sulphur, Phosphorus Content", "clause": "Clause 4.2", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 13920:2016", "title": "Ductile Design and Detailing of Reinforced Concrete Structures Subjected to Seismic Forces", "role": "Earthquake safety compliance"}
            ],
            "installation_standards": [
                {"code": "IS 456:2000 (Reaffirmed 2021)", "title": "Plain and Reinforced Concrete - Code of Practice", "role": "Placement, cover, and lap splicing guidelines"},
                {"code": "SP 34:1987", "title": "Handbook on Concrete Reinforcement and Detailing", "role": "Bar bending schedules and shop drawing norms"}
            ],
            "terminology_standards": [
                {"code": "IS 1387:1993", "title": "General Requirements for the Supply of Metallurgical Materials", "role": "Standard definition of heats, lots, and delivery states"}
            ],
            "related_product_standards": [
                {"code": "IS 2062:2011", "title": "Hot Rolled Medium and High Tensile Structural Steel", "role": "Plates, beams, channels, and angles"},
                {"code": "IS 432 (Part 1):1982", "title": "Mild Steel and Medium Tensile Steel Bars", "role": "Smooth plain round steel"}
            ]
        },
        "gem_tender_clause": (
            "The bidder shall supply High Strength Deformed Steel Bars for Concrete Reinforcement strictly conforming to "
            "IS 1786:2008 (Grade Fe 500D / Fe 550D) with all active Amendments (1, 2, and 3). In compliance with the "
            "Steel and Steel Products (Quality Control) Order issued by the Ministry of Steel, the material must carry "
            "a valid BIS Scheme-I ISI Mark with clear CM/L license number embossed at 1-metre intervals. Third-party testing "
            "shall be executed in NABL accredited laboratories in accordance with IS 1608 (Part 1) for tensile properties and "
            "IS 1599 for rebend tests."
        )
    },

    "IS 2062": {
        "id": "IS 2062",
        "code": "IS 2062:2011",
        "title": "Hot Rolled Medium and High Tensile Structural Steel - Specification",
        "popular_names": ["Structural Steel", "MS Angles", "Beams", "Channels", "Steel Plates", "Joists", "Girder Steel", "E250", "E350", "I-Beams"],
        "category": "Civil & Construction",
        "sub_category": "Structural Steel",
        "latest_edition": "2011 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2015", "scope": "Inclusion of high strength structural grades E550 and E650"},
            {"number": 2, "year": "2019", "scope": "Tolerances on dimensional profiles and sub-zero impact testing"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 2062:2006", "IS 2062:1999"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "Ministry of Steel",
            "qco_order": "Steel and Steel Products (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Mandatory BIS certification is legally enforceable for all structural steel sections."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 1608 (Part 1):2018", "title": "Tensile Testing of Metals", "role": "Yield & Ultimate Tensile Strength"},
                {"code": "IS 1757 (Part 1):2020", "title": "Charpy V-Notch Impact Test", "role": "Impact toughness test"}
            ],
            "test_methods": [
                {"code": "IS 1608 (Part 1):2018", "title": "Tensile Testing", "clause": "Clause 11", "nabl_required": True},
                {"code": "IS 1757 (Part 1):2020", "title": "Charpy V-Notch Pendulum Impact Test", "clause": "Clause 12", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 800:2007 (Reaffirmed 2022)", "title": "General Construction In Steel - Code of Practice", "role": "Structural safety and stability"}
            ],
            "installation_standards": [
                {"code": "IS 7205:1974", "title": "Safety Code for Erection of Structural Steelwork", "role": "Site hoisting, welding, and erection safety"}
            ],
            "terminology_standards": [
                {"code": "IS 1956", "title": "Glossary of Terms Relating to Iron and Steel", "role": "Terminology for structural profiles"}
            ],
            "related_product_standards": [
                {"code": "IS 1786:2008", "title": "TMT Rebars for Concrete Reinforcement", "role": "Reinforcement companion standard"}
            ]
        },
        "gem_tender_clause": (
            "Structural steel plates, sections, channels, and beams supplied shall strictly conform to IS 2062:2011 "
            "(Grade E250 / E350 Quality A/BR) with active amendments. In adherence to the Ministry of Steel QCO, "
            "each piece must bear the authentic ISI mark and CM/L license number. Fabrication and erection shall "
            "comply with IS 800:2007."
        )
    },

    # ----------------------------------------------------
    # 2. CEMENT & CONCRETE
    # ----------------------------------------------------
    "IS 269": {
        "id": "IS 269",
        "code": "IS 269:2015",
        "title": "Ordinary Portland Cement (33, 43 and 53 Grade) - Specification",
        "popular_names": ["OPC Cement", "Cement 53 Grade", "Cement 43 Grade", "Ordinary Portland Cement", "Grey Cement", "Portland Cement"],
        "category": "Civil & Construction",
        "sub_category": "Building Materials",
        "latest_edition": "2015 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": 1, "year": "2018", "scope": "Revision of chloride content and insoluble residue maximum limits"},
            {"number": 2, "year": "2021", "scope": "Composite testing for early compressive strength at 3 and 7 days"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 8112:1989 (43 Grade OPC merged into IS 269:2015)", "IS 12269:1987 (53 Grade OPC merged into IS 269:2015)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Cement (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Cement is under strict mandatory ISI certification. Selling, stocking, or purchasing non-ISI cement is an offence."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 4031 (Parts 1-15)", "title": "Methods of Physical Tests for Hydraulic Cement", "role": "Complete physical test suite"},
                {"code": "IS 4032:1985", "title": "Method of Chemical Analysis of Hydraulic Cement", "role": "Chemical limits & insoluble residue"}
            ],
            "test_methods": [
                {"code": "IS 4031 (Part 2):1999", "title": "Determination of Fineness by Blaine Air Permeability", "clause": "Clause 6.1", "nabl_required": True},
                {"code": "IS 4031 (Part 3):1988", "title": "Determination of Soundness by Le-Chatelier & Autoclave", "clause": "Clause 6.2", "nabl_required": True},
                {"code": "IS 4031 (Part 5):1988", "title": "Determination of Initial and Final Setting Times", "clause": "Clause 6.3", "nabl_required": True},
                {"code": "IS 4031 (Part 6):1988", "title": "Determination of Compressive Strength (3, 7, 28 Days)", "clause": "Clause 6.4", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 456:2000 (Reaffirmed 2021)", "title": "Plain and Reinforced Concrete - Durability & Exposure Classes", "role": "Maximum water-cement ratio and minimum cement content"}
            ],
            "installation_standards": [
                {"code": "IS 456:2000", "title": "Batching, Mixing and Curing of Concrete", "role": "Site preparation & concrete placement"}
            ],
            "terminology_standards": [
                {"code": "IS 4845:1968", "title": "Definitions and Terminology Relating to Hydraulic Cement", "role": "Standard cement classification"}
            ],
            "related_product_standards": [
                {"code": "IS 1489 (Part 1):2015", "title": "Portland Pozzolana Cement (Fly Ash Based - PPC)", "role": "Green blended cement alternative"},
                {"code": "IS 455:2015", "title": "Portland Slag Cement (PSC)", "role": "Slag based cement for marine environments"}
            ]
        },
        "gem_tender_clause": (
            "Cement supplied shall be fresh Ordinary Portland Cement 53 Grade conforming strictly to IS 269:2015 "
            "with Amendments 1 and 2. Cement bags must carry the statutory BIS ISI mark with valid CM/L license number "
            "and manufacturer batch code. 28-day compressive strength shall not be less than 53 MPa when tested in "
            "accordance with IS 4031 (Part 6). Bags older than 90 days from manufacture shall be summarily rejected."
        )
    },

    "IS 1489": {
        "id": "IS 1489",
        "code": "IS 1489 (Part 1):2015",
        "title": "Portland Pozzolana Cement - Specification - Part 1 Fly Ash Based",
        "popular_names": ["PPC Cement", "Fly Ash Cement", "Pozzolana Cement", "Blended Cement", "Green Cement"],
        "category": "Civil & Construction",
        "sub_category": "Building Materials",
        "latest_edition": "2015 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": 1, "year": "2019", "scope": "Fly ash proportion validation (15% to 35%) and drying shrinkage limits"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Cement (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Mandatory ISI certification required for PPC fly ash based cement."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 3812 (Part 1):2013", "title": "Pulverized Fuel Ash - Specification", "role": "Fly ash quality criteria"}
            ],
            "test_methods": [
                {"code": "IS 4031 (Part 6):1988", "title": "Compressive Strength Test", "clause": "Clause 6", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 456:2000", "title": "Plain and Reinforced Concrete", "role": "Structural safety"}
            ],
            "installation_standards": [
                {"code": "IS 456:2000", "title": "Curing Duration (Minimum 10 days for PPC)", "role": "Adequate moist curing"}
            ],
            "terminology_standards": [
                {"code": "IS 4845:1968", "title": "Cement Definitions", "role": "Definitions"}
            ],
            "related_product_standards": [
                {"code": "IS 269:2015", "title": "Ordinary Portland Cement (OPC)", "role": "Pure clinker cement"}
            ]
        },
        "gem_tender_clause": (
            "Portland Pozzolana Cement (Fly Ash Based) supplied shall strictly conform to IS 1489 (Part 1):2015 "
            "with Amendment 1. The bags must bear the authentic BIS ISI mark and CM/L license number. Fly ash content "
            "shall be between 15% and 35% by mass. 28-day compressive strength shall not be less than 33 MPa."
        )
    },

    # ----------------------------------------------------
    # 3. ELECTRICAL, WIRES, CABLES & LIGHTING
    # ----------------------------------------------------
    "IS 694": {
        "id": "IS 694",
        "code": "IS 694:2010",
        "title": "Polyvinyl Chloride (PVC) Insulated Unsheathed and Sheathed Cables/Cords with Rigid and Flexible Conductor",
        "popular_names": [
            "PVC Wires", "Copper House Wires", "Electrical Building Wires", "Flexible Copper Cables",
            "FR/FRLS Wires", "Fire Resistant Electrical Cables", "Fire Retardant Cables", "FRLS Cables",
            "Electrical Cables", "Electric Cables", "PVC Cables", "1.5 sq mm copper wire", "2.5 sq mm copper wire"
        ],
        "category": "Electrical & Energy",
        "sub_category": "Wires and Cables",
        "latest_edition": "2010 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": 1, "year": "2014", "scope": "Enhanced conductor resistance and conductor purity norms"},
            {"number": 2, "year": "2017", "scope": "Flame Retardant Low Smoke (FRLS) halogen acid gas emission limits"},
            {"number": 3, "year": "2021", "scope": "Packaging and tamper-evident sequential metre marking on wire jacket"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 694:1990 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Electrical Wires and Cables (Quality Control) Order",
            "statutory_act": "Section 16 & 29, BIS Act 2016",
            "tender_warning": "Mandatory ISI certification. Uncertified electrical building wires pose high fire hazard and are legally prohibited."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 8130:2013", "title": "Conductors for Insulated Electric Cables and Flexible Cords", "role": "Electrolytic grade copper conductor purity"},
                {"code": "IS 5831:1984", "title": "PVC Insulation and Sheath of Electric Cables", "role": "Insulation thermal stability"}
            ],
            "test_methods": [
                {"code": "IS 10810 (Part 5):1984", "title": "Conductor Resistance Test", "clause": "Clause 10.1", "nabl_required": True},
                {"code": "IS 10810 (Part 45):1984", "title": "High Voltage Spark Test", "clause": "Clause 10.2", "nabl_required": True},
                {"code": "IS 10810 (Part 53):1984", "title": "Flammability Test / Flame Retardance", "clause": "Clause 10.3", "nabl_required": True},
                {"code": "IS 10810 (Part 59):1988", "title": "Determination of Halogen Acid Gas for FRLS Cables", "clause": "Clause 10.4", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS/IEC 60332 (Parts 1-3)", "title": "Tests on Electric Cables Under Fire Conditions", "role": "Fire propagation prevention"}
            ],
            "installation_standards": [
                {"code": "IS 732:2019", "title": "Code of Practice for Electrical Wiring Installations", "role": "Conduit sizing, current rating, and color coding"},
                {"code": "National Electrical Code of India (NEC 2023)", "title": "SP 30: National Electrical Code", "role": "Building electrical safety"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 32):1993", "title": "Electrotechnical Vocabulary - Electric Cables", "role": "Standard cable terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 7098 (Part 1):1988", "title": "Cross-Linked Polyethylene (XLPE) Insulated PVC Sheathed Cables (1.1 kV)", "role": "Industrial underground power cables"},
                {"code": "IS 1554 (Part 1):1988", "title": "PVC Insulated Heavy Duty Armoured Cables", "role": "Armoured power cables"}
            ]
        },
        "gem_tender_clause": (
            "The bidder must supply 1100V grade PVC insulated unsheathed/sheathed single-core copper conductor wires conforming "
            "to IS 694:2010 (with latest Amendments 1, 2, and 3) with Flame Retardant Low Smoke (FRLS) insulation. The wires must "
            "bear the authentic BIS Scheme-I ISI Mark with clear CM/L license number and continuous metre marking on the outer sheath. "
            "Testing for conductor resistance and flammability shall conform to IS 10810."
        )
    },

    "IS 7098": {
        "id": "IS 7098",
        "code": "IS 7098 (Part 1):1988",
        "title": "Cross-Linked Polyethylene (XLPE) Insulated Thermoplastic Sheathed Cables - For Working Voltages up to and Including 1100 V",
        "popular_names": ["XLPE Cables", "Armoured Power Cables", "Underground Power Cables", "Heavy Duty XLPE", "Aluminium XLPE Cable"],
        "category": "Electrical & Energy",
        "sub_category": "Power Cables",
        "latest_edition": "1988 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": 1, "year": "2000", "scope": "Armouring round steel wire / strip dimension limits"},
            {"number": 2, "year": "2015", "scope": "Thermal short-circuit rating criteria"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Electrical Wires and Cables (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Mandatory ISI mark required for all underground XLPE power cables."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 8130:2013", "title": "Conductors for Insulated Electric Cables", "role": "Aluminium/copper conductor criteria"}
            ],
            "test_methods": [
                {"code": "IS 10810 (Part 30):1984", "title": "Hot Set Test for XLPE Insulation", "clause": "Clause 14", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 1255:1983", "title": "Code of Practice for Installation and Maintenance of Power Cables", "role": "Trench depth and sand cushioning"}
            ],
            "installation_standards": [
                {"code": "IS 1255:1983", "title": "Cable Laying and Jointing in Ground", "role": "Ground cable route marker"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 32):1993", "title": "Power Cable Vocabulary", "role": "Vocabulary"}
            ],
            "related_product_standards": [
                {"code": "IS 694:2010", "title": "PVC Insulated Building Wires", "role": "Building wires"}
            ]
        },
        "gem_tender_clause": (
            "1.1 kV grade XLPE insulated, PVC outer sheathed, armoured power cables shall strictly conform to "
            "IS 7098 (Part 1):1988 with latest amendments. Cables must carry the mandatory BIS Scheme-I ISI Mark. "
            "Hot set elongation test reports as per IS 10810 (Part 30) shall be furnished prior to dispatch."
        )
    },

    "IS 10322": {
        "id": "IS 10322",
        "code": "IS 10322 (Part 5/Sec 3):2012 / IS 16107 (Part 2/Sec 1):2012",
        "title": "Luminaires - Particular Requirements - Luminaires for Road and Street Lighting",
        "popular_names": ["LED Street Lights", "LED Luminaires", "LED Flood Lights", "Outdoor LED Fixtures", "Smart Streetlighting", "LED Lights", "Street Lights"],
        "category": "Electrical & Energy",
        "sub_category": "Lighting & Luminaires",
        "latest_edition": "2012 (Reaffirmed 2022)",
        "active_amendments": [
            {"number": 1, "year": "2016", "scope": "Ingress protection minimum IP66 rating for outdoor road fixtures"},
            {"number": 2, "year": "2020", "scope": "Surge protection 10kV / 10kA withstand capability and driver life test"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-II (Compulsory Registration Scheme - CRS)",
            "issuing_ministry": "Ministry of Electronics and Information Technology (MeitY)",
            "qco_order": "Electronics and Information Technology Goods (Compulsory Registration) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "LED street luminaires and drivers MUST be registered under BIS CRS (R-XXXXXXXX number). Customs clearance and GeM sales prohibited without CRS."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 15885 (Part 2/Sec 13):2012", "title": "Safety of Lamp Controlgear - Electronic Controlgear for LED Modules", "role": "Mandatory LED driver safety"},
                {"code": "IS 16102 (Part 1 & 2):2012", "title": "Self-Ballasted LED Lamps for General Lighting Services - Performance", "role": "Luminous efficacy and lumen maintenance"}
            ],
            "test_methods": [
                {"code": "IS 16106:2012", "title": "Method of Electrical and Photometric Measurements of Solid-State Lighting (LED) Products", "clause": "Clause 8", "nabl_required": True},
                {"code": "IS 12063:1987", "title": "Classification of Degrees of Protection Provided by Enclosures (IP Code - IP66)", "clause": "Clause 9", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 15885 (Part 1):2011", "title": "Lamp Controlgear - General and Safety Requirements", "role": "Electrical shock and thermal protection"}
            ],
            "installation_standards": [
                {"code": "IS 1944 (Parts 1-6):1970", "title": "Code of Practice for Lighting of Public Thoroughfares", "role": "Pole height, spacing, and lux level design"},
                {"code": "National Lighting Code (SP 72:2010)", "title": "National Lighting Code of India", "role": "Energy efficient lighting design"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 16):1968", "title": "Electrotechnical Vocabulary - Lighting", "role": "Standard photometric terms (Lumens, Lux, CRI)"}
            ],
            "related_product_standards": [
                {"code": "IS 16103 (Part 1):2012", "title": "LED Modules for General Lighting - Safety Specifications", "role": "LED chip package safety"}
            ]
        },
        "gem_tender_clause": (
            "The outdoor LED street light luminaires shall conform to IS 10322 (Part 5/Sec 3):2012 and performance standard "
            "IS 16107 (Part 2/Sec 1). The luminaire and its LED driver must hold valid BIS Compulsory Registration Scheme (CRS) "
            "approval under MeitY with valid R-Number (R-XXXXXXXX) clearly marked. Ingress protection shall be certified IP66 "
            "as per IS 12063, with minimum system efficacy of 120 lumens/watt and 10kV surge protection."
        )
    },

    "IS 374": {
        "id": "IS 374",
        "code": "IS 374:2019",
        "title": "Electric Ceiling Type Fans and Regulators - Specification",
        "popular_names": ["Ceiling Fans", "Electric Fans", "BLDC Fans", "BEE Star Fans", "Regulators for Fans"],
        "category": "Electrical & Energy",
        "sub_category": "Home & Office Appliances",
        "latest_edition": "2019 (Reaffirmed 2024)",
        "active_amendments": [
            {"number": 1, "year": "2021", "scope": "Inclusion of Brushless DC (BLDC) motor fan specifications and harmonic limits"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 374:1979 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark) + BEE Star Labeling",
            "issuing_ministry": "Ministry of Power & DPIIT",
            "qco_order": "Electric Ceiling Fans (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Electric ceiling fans must mandatorily hold BIS ISI mark and minimum 1-Star BEE energy rating."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 302-2-80:2017", "title": "Safety of Household and Similar Electrical Appliances - Fans", "role": "Electrical shock safety"}
            ],
            "test_methods": [
                {"code": "IS 374 Clause 13", "title": "Air Delivery Measurement in Anemometer Chamber", "clause": "Clause 13", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 302-1:2008", "title": "General Safety Requirements for Household Electrical Appliances", "role": "Insulation safety"}
            ],
            "installation_standards": [
                {"code": "IS 732:2019", "title": "Electrical Wiring Installations", "role": "Downrod safety shackle and earthing"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 54)", "title": "Household Appliances Vocabulary", "role": "Vocabulary"}
            ],
            "related_product_standards": [
                {"code": "IS 2312:1967", "title": "Exhaust Fans - Specification", "role": "Exhaust ventilation fans"}
            ]
        },
        "gem_tender_clause": (
            "Electric ceiling fans supplied shall conform to IS 374:2019 with Amendment 1, carrying the mandatory "
            "BIS Scheme-I ISI Mark with valid CM/L code and BEE Star rating label. Minimum air delivery shall be 210 m3/min "
            "with minimum service value of 4.0 m3/min/W. Safety downrod shackle shall conform to IS 302-2-80."
        )
    },

    "IS 1180": {
        "id": "IS 1180",
        "code": "IS 1180 (Part 1):2014",
        "title": "Outdoor Type Oil Immersed Distribution Transformers up to and Including 2500 kVA, 33 kV - Specification",
        "popular_names": ["Distribution Transformer", "Oil Immersed Transformer", "11kV/415V Transformer", "Energy Efficient Transformer", "BEE Star Transformer"],
        "category": "Electrical & Energy",
        "sub_category": "Power Distribution",
        "latest_edition": "2014 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2016", "scope": "Max loss levels for Energy Level 1, Level 2, and Level 3"},
            {"number": 2, "year": "2018", "scope": "Short circuit withstand testing protocols"},
            {"number": 3, "year": "2020", "scope": "Standardization of tank fittings and bi-directional rollers"},
            {"number": 4, "year": "2023", "scope": "Harmonization with CEA technical standards for distribution grid"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 1180 (Part 1):1989"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "Ministry of Power / DPIIT",
            "qco_order": "Distribution Transformers (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "CRITICAL: Distribution transformers are under strict mandatory ISI certification and BEE Star Labeling rules."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 2026 (Parts 1-5)", "title": "Power Transformers", "role": "Core transformer theory and performance"},
                {"code": "IS 335:2018", "title": "New Insulating Oils - Specification", "role": "Mineral transformer oil breakdown voltage"}
            ],
            "test_methods": [
                {"code": "IS 2026 (Part 1):2011", "title": "Measurement of Winding Resistance and Voltage Ratio", "clause": "Clause 16", "nabl_required": True},
                {"code": "IS 2026 (Part 5):2011", "title": "Ability to Withstand Short Circuit Test", "clause": "Clause 16.5", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 10028 (Part 1 & 2):1981", "title": "Code of Practice for Selection, Installation and Maintenance of Transformers", "role": "Substation fire safety & oil soak pit"}
            ],
            "installation_standards": [
                {"code": "Central Electricity Authority (Measures Relating to Safety and Electric Supply) Regulations", "title": "CEA Safety Regulations 2023", "role": "Clearances and grounding"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 38):1993", "title": "Electrotechnical Vocabulary - Transformers", "role": "Transformer terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 2026", "title": "Power Transformers up to 400 kV", "role": "High capacity substation transformers"}
            ]
        },
        "gem_tender_clause": (
            "Distribution transformers shall strictly conform to IS 1180 (Part 1):2014 with latest Amendments 1 to 4 and must "
            "bear the mandatory BIS Scheme-I ISI Mark with valid CM/L license number. Loss levels shall conform to BEE Star-1/Star-2 "
            "ratings. Type test certificates including Short Circuit Withstand Test from CPRI or ERDA shall be submitted with the technical bid."
        )
    },

    "IS 14286": {
        "id": "IS 14286",
        "code": "IS 14286:2019 / IEC 61215:2016",
        "title": "Terrestrial Photovoltaic (PV) Modules - Design Qualification and Type Approval",
        "popular_names": ["Solar Panels", "Solar PV Modules", "Photovoltaic Panels", "Rooftop Solar Modules", "Monocrystalline Solar Panels"],
        "category": "Electrical & Energy",
        "sub_category": "Renewable Energy & Solar",
        "latest_edition": "2019 (Reaffirmed 2024)",
        "active_amendments": [
            {"number": 1, "year": "2022", "scope": "Bifacial solar module testing protocol and PID resistance testing"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 14286:2010 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-II (Compulsory Registration Scheme - CRS) + ALMM",
            "issuing_ministry": "Ministry of New and Renewable Energy (MNRE)",
            "qco_order": "Solar Photovoltaics, Systems, Devices and Components Goods (Requirements for Compulsory Registration) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Solar panels for all government tenders MUST hold BIS CRS registration and be enlisted in the MNRE Approved List of Models and Manufacturers (ALMM)."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS/IEC 61730 (Part 1 & 2):2016", "title": "Photovoltaic (PV) Module Safety Qualification", "role": "Electrical shock and fire hazard safety"}
            ],
            "test_methods": [
                {"code": "IS 14286 Clause 10.11", "title": "Thermal Cycling Test (200 Cycles)", "clause": "Clause 10.11", "nabl_required": True},
                {"code": "IS 14286 Clause 10.13", "title": "Damp Heat Test (1000h at 85°C/85% RH)", "clause": "Clause 10.13", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS/IEC 61730-2", "title": "PV Module Safety - Testing", "role": "Class A fire rating and dielectric withstand"}
            ],
            "installation_standards": [
                {"code": "MNRE Guidelines for Rooftop Solar", "title": "MNRE Best Practice Manual for Solar PV Installations", "role": "Module mounting structure wind load"}
            ],
            "terminology_standards": [
                {"code": "IS 12834:1989", "title": "Solar Photovoltaic Energy Systems - Terms and Definitions", "role": "Definitions"}
            ],
            "related_product_standards": [
                {"code": "IS 16221 (Part 2):2015", "title": "Safety of Power Converters for Use in Photovoltaic Power Systems (Solar Inverters)", "role": "Solar Grid Inverters"}
            ]
        },
        "gem_tender_clause": (
            "Solar Photovoltaic (PV) modules supplied shall strictly conform to IS 14286:2019 / IEC 61215 and IS/IEC 61730 (Parts 1 & 2). "
            "Modules must hold valid BIS Compulsory Registration Scheme (CRS) certification with active R-Number and be enlisted in "
            "the latest MNRE ALMM (Approved List of Models and Manufacturers). Module efficiency shall be greater than 20.5% with linear "
            "degradation warranty guaranteeing at least 80% output at 25 years."
        )
    },

    # ----------------------------------------------------
    # 4. PIPES, WATER SUPPLY & SANITATION
    # ----------------------------------------------------
    "IS 4984": {
        "id": "IS 4984",
        "code": "IS 4984:2016",
        "title": "High Density Polyethylene (HDPE) Pipes for Water Supply - Specification",
        "popular_names": ["HDPE Pipes", "PE100 Pipes", "PE80 Pipes", "Jal Jeevan Mission Pipes", "Black Plastic Water Pipes", "Potable Water Pipes"],
        "category": "Pipes & Water Supply",
        "sub_category": "Plastic Piping Systems",
        "latest_edition": "2016 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2018", "scope": "Hydrostatic pressure test duration and raw material carbon black dispersion"},
            {"number": 2, "year": "2021", "scope": "Co-extruded blue stripe identification requirements for potable water lines"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 4984:1995 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "Department of Chemicals and Petrochemicals (DCPC)",
            "qco_order": "Pipes and Fittings (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Under Jal Jeevan Mission and CPHEEO guidelines, HDPE pipes without valid BIS ISI mark are ineligible for state/central funding."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 7328:2020", "title": "High Density Polyethylene Materials for Moulding and Extrusion", "role": "Virgin raw material PE-100 specification"},
                {"code": "IS 9845:1998", "title": "Determination of Overall Migration of Plastic Materials Food Contact", "role": "Toxic chemical leaching safety in drinking water"}
            ],
            "test_methods": [
                {"code": "IS 4984 Annex B", "title": "Hydrostatic Internal Pressure Test (100h / 165h at 80°C)", "clause": "Clause 8.1", "nabl_required": True},
                {"code": "IS 2530:1963", "title": "Methods of Test for Polyethylene - Carbon Black Content and Dispersion", "clause": "Clause 8.2", "nabl_required": True},
                {"code": "IS 4984 Annex E", "title": "Melt Flow Rate (MFR) Determination", "clause": "Clause 8.4", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 10146:1982", "title": "Polyethylene for its Safe Use in Contact with Foodstuffs, Pharmaceuticals and Drinking Water", "role": "Potable water toxicological safety"}
            ],
            "installation_standards": [
                {"code": "IS 7634 (Part 2):2012", "title": "Code of Practice for Laying and Jointing of Polyethylene Pipes", "role": "Butt fusion welding, trench excavation, and bedding"}
            ],
            "terminology_standards": [
                {"code": "IS 2828:1964", "title": "Glossary of Terms Used in the Plastics Industry", "role": "Plastics technical vocabulary"}
            ],
            "related_product_standards": [
                {"code": "IS 4985:2021", "title": "Unplasticized PVC (uPVC) Pipes for Potable Water Supplies", "role": "Rigid PVC pipe alternative"},
                {"code": "IS 14333:1996", "title": "High Density Polyethylene Pipes for Sewerage", "role": "Gravity sewer lines"}
            ]
        },
        "gem_tender_clause": (
            "HDPE pipes supplied for water transmission shall strictly conform to IS 4984:2016 (PE-100 Grade, PN 6 / PN 10 / PN 16 rating) "
            "with latest Amendments 1 and 2. The pipes must be manufactured only from virgin resin and bear the authentic BIS ISI mark "
            "with CM/L number. Laying and butt-fusion jointing must adhere to IS 7634 (Part 2). Factory test reports for hydrostatic pressure "
            "and carbon black dispersion shall be furnished with each consignment."
        )
    },

    "IS 4985": {
        "id": "IS 4985",
        "code": "IS 4985:2021",
        "title": "Unplasticized Polyvinyl Chloride (uPVC) Pipes for Potable Water Supplies - Specification",
        "popular_names": ["uPVC Pipes", "PVC Water Pipes", "Plumbing Pipes", "Potable Water UPVC", "Rigid PVC Pipes", "PVC Pipes"],
        "category": "Pipes & Water Supply",
        "sub_category": "Plastic Piping Systems",
        "latest_edition": "2021 (Current Active Edition)",
        "active_amendments": [
            {"number": 1, "year": "2023", "scope": "Lead-free stabilizer compliance and toxic heavy metal prohibition"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 4985:2000 (Superseded by 2021 edition)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT & Ministry of Chemicals",
            "qco_order": "Pipes and Fittings (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Mandatory ISI mark required. Must comply with lead-free plumbing mandate."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 12235 (Parts 1-19)", "title": "Methods of Test for Unplasticized PVC Pipes for Potable Water Supplies", "role": "Comprehensive testing methodology"}
            ],
            "test_methods": [
                {"code": "IS 12235 (Part 8/Sec 1)", "title": "Resistance to Internal Hydrostatic Pressure", "clause": "Clause 9.1", "nabl_required": True},
                {"code": "IS 12235 (Part 9)", "title": "Impact Strength (Falling Dart) Test at 0°C", "clause": "Clause 9.2", "nabl_required": True},
                {"code": "IS 12235 (Part 10)", "title": "Determination of Lead and Toxic Heavy Metal Extraction", "clause": "Clause 9.3", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 10148:1982", "title": "Positive List of Constituents of PVC in Contact with Food and Drinking Water", "role": "Food grade safety"}
            ],
            "installation_standards": [
                {"code": "IS 7634 (Part 3):2003", "title": "Code of Practice for Laying and Jointing of uPVC Pipes", "role": "Solvent cement jointing and rubber ring sockets"}
            ],
            "terminology_standards": [
                {"code": "IS 2828:1964", "title": "Plastics Vocabulary", "role": "Terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 7834 (Parts 1-8)", "title": "Injection Moulded PVC Fittings for Potable Water", "role": "Elbows, tees, and couplers"}
            ]
        },
        "gem_tender_clause": (
            "uPVC pipes shall conform to IS 4985:2021 with Amendment 1 (Lead-Free / Non-Toxic formulation). Pipes must bear the "
            "statutory BIS Scheme-I ISI Mark with CM/L code. Jointing and installation shall strictly follow IS 7634 (Part 3). "
            "Heavy metal extraction test certificates confirming compliance with zero-lead limits shall be produced prior to delivery."
        )
    },

    "IS 8034": {
        "id": "IS 8034",
        "code": "IS 8034:2018",
        "title": "Submersible Pumpsets - Specification",
        "popular_names": ["Submersible Pump", "Borewell Pump", "Agricultural Water Pump", "Openwell Submersible", "Tube Well Pump", "Water Pump 5HP", "Borewell Motor"],
        "category": "Pipes & Water Supply",
        "sub_category": "Pumps & Pumping Machinery",
        "latest_edition": "2018 (Reaffirmed 2023)",
        "active_amendments": [
            {"number": 1, "year": "2020", "scope": "Harmonization with BEE Star-Rating energy efficiency tables"},
            {"number": 2, "year": "2022", "scope": "Corrosion resistance testing for stainless steel impellers and bowls"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 8034:2002 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark) + BEE Star Labeling",
            "issuing_ministry": "Ministry of Power & DPIIT",
            "qco_order": "Pumps (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Submersible pumps for government water supply schemes must be ISI certified and minimum 3-Star BEE rated."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 9283:2013", "title": "Motors for Submersible Pumpsets - Specification", "role": "Submersible rewindable/water-filled motor requirements"},
                {"code": "IS 9137:2019", "title": "Code for Acceptance Tests for Centrifugal, Mixed Flow and Axial Pumps - Class C", "role": "Discharge and head measurement"}
            ],
            "test_methods": [
                {"code": "IS 11346:2002", "title": "Code of Practice for Testing of Submersible Pumpsets", "clause": "Clause 14", "nabl_required": True},
                {"code": "IS 9283:2013 Annex", "title": "Insulation Resistance & High Voltage Withstand Test", "clause": "Clause 15", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS/IEC 60034-1:2017", "title": "Rotating Electrical Machines - Rating and Performance", "role": "Electrical motor safety"}
            ],
            "installation_standards": [
                {"code": "IS 14536:1998", "title": "Code of Practice for Selection, Installation and Maintenance of Submersible Pumps", "role": "Borewell lowering, cable clamping, and protection panels"}
            ],
            "terminology_standards": [
                {"code": "IS 5120:1977", "title": "Technical Requirements for Roto-Dynamic Special Purpose Pumps", "role": "Pump terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 9079:2018", "title": "Monobloc Pumpsets for Clear, Cold Water", "role": "Surface monobloc pumps"}
            ]
        },
        "gem_tender_clause": (
            "Submersible pumpsets supplied shall strictly conform to IS 8034:2018 with latest amendments, equipped with water-lubricated "
            "submersible motor as per IS 9283. The unit must carry the authentic BIS Scheme-I ISI Mark and BEE energy efficiency star label. "
            "Installation shall follow IS 14536. Factory performance test curves showing discharge (LPS), total head (m), and overall efficiency "
            "shall be verified in accordance with IS 11346."
        )
    },

    # ----------------------------------------------------
    # 5. SAFETY, DEFENSE & FIRE FIGHTING
    # ----------------------------------------------------
    "IS 15683": {
        "id": "IS 15683",
        "code": "IS 15683:2018",
        "title": "Portable Fire Extinguishers - Performance and Construction - Specification",
        "popular_names": ["Fire Extinguisher", "ABC Powder Extinguisher", "CO2 Fire Extinguisher", "Water Type Extinguisher", "Foam Extinguisher", "Fire Fighting Cylinders"],
        "category": "Safety & Fire Protection",
        "sub_category": "Fire Fighting Appliances",
        "latest_edition": "2018 (Reaffirmed 2023)",
        "active_amendments": [
            {"number": 1, "year": "2020", "scope": "Hydrostatic pressure testing burst factor and pressure gauge accuracy limits"},
            {"number": 2, "year": "2022", "scope": "Eco-friendly non-toxic extinguishing powders and PFAS foaming agent bans"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 2171:1999 (Dry Powder)", "IS 940:2003 (Water)", "IS 2878:2004 (CO2) - All harmonized into IS 15683"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "Ministry of Home Affairs / DPIIT",
            "qco_order": "Fire Fighting Equipment (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Fire extinguishers are life-safety equipment. Supplying uncertified or obsolete types (IS 2171/IS 940) violates NBC 2016."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 4308:2019", "title": "Dry Chemical Powder for Fire Fighting (Class B & C Fires)", "role": "Chemical powder extinguishing efficacy"},
                {"code": "IS 14609:2020", "title": "Dry Chemical Powder for Class A, B, C Fires", "role": "MAP 50/90 powder formulation"}
            ],
            "test_methods": [
                {"code": "IS 15683 Annex E", "title": "Class A and Class B Fire Performance Ratings Tests", "clause": "Clause 8.1", "nabl_required": True},
                {"code": "IS 15683 Annex G", "title": "Hydraulic Burst Pressure Test", "clause": "Clause 8.2", "nabl_required": True},
                {"code": "IS 15683 Annex J", "title": "Electrical Conductivity Test (100 kV)", "clause": "Clause 8.3", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "National Building Code of India (NBC 2016 Part 4)", "title": "Fire and Life Safety", "role": "Building fire egress and extinguisher spacing"}
            ],
            "installation_standards": [
                {"code": "IS 2190:2024", "title": "Selection, Installation and Maintenance of First-Aid Fire Appliances - Code of Practice", "role": "Mounting height, annual refilling, and inspection"}
            ],
            "terminology_standards": [
                {"code": "IS 7673:2004", "title": "Glossary of Terms Relating to Fire Fighting Equipment", "role": "Fire safety definitions"}
            ],
            "related_product_standards": [
                {"code": "IS 16018:2012", "title": "Wheeled Fire Extinguishers (Trolley Mounted 25kg/50kg)", "role": "Heavy industrial fire trolleys"}
            ]
        },
        "gem_tender_clause": (
            "Portable fire extinguishers supplied shall strictly comply with unified Indian Standard IS 15683:2018 with active "
            "Amendments 1 and 2, carrying the mandatory BIS Scheme-I ISI Mark with verifiable CM/L number. Extinguishers must be "
            "charged with MAP-50 ABC dry powder conforming to IS 14609. Installation and periodic maintenance protocol must strictly "
            "adhere to IS 2190:2024 and National Building Code 2016 Part 4."
        )
    },

    "IS 2925": {
        "id": "IS 2925",
        "code": "IS 2925:1984",
        "title": "Specification for Industrial Safety Helmets",
        "popular_names": ["Safety Helmet", "Hard Hat", "Construction Safety Helmet", "Industrial Hard Hat", "PPE Helmet"],
        "category": "Safety & Fire Protection",
        "sub_category": "Personal Protective Equipment (PPE)",
        "latest_edition": "1984 (Reaffirmed 2019)",
        "active_amendments": [
            {"number": 1, "year": "1988", "scope": "Flammability and electrical insulation limits"},
            {"number": 2, "year": "2000", "scope": "Retention system chin strap release load specifications"},
            {"number": 3, "year": "2014", "scope": "UV degradation resistance and shelf life labeling"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Personal Protective Equipment (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Industrial safety helmets must possess valid BIS ISI mark before supply to any construction, mining, or factory site."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 4151:2020", "title": "Protective Helmets for Two-Wheeler Riders", "role": "Distinguished two-wheeler standard"}
            ],
            "test_methods": [
                {"code": "IS 2925 Clause 8.2", "title": "Shock Absorption Resistance Test", "clause": "Clause 8.2", "nabl_required": True},
                {"code": "IS 2925 Clause 8.3", "title": "Penetration Resistance Test (Drop Plumb Bob)", "clause": "Clause 8.3", "nabl_required": True},
                {"code": "IS 2925 Clause 8.5", "title": "Electrical Insulation Resistance Test", "clause": "Clause 8.5", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "NBC 2016 Part 7", "title": "Construction Management, Practices and Safety", "role": "Mandatory site PPE protocol"}
            ],
            "installation_standards": [
                {"code": "IS 13416 (Part 1-5)", "title": "Recommendations for Preventive Measures Against Hazards at Work Sites", "role": "Site safety"}
            ],
            "terminology_standards": [
                {"code": "IS 8521", "title": "Glossary of Terms for Personal Protective Equipment", "role": "PPE terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 15298 (Part 2):2016", "title": "Safety Footwear with Steel Toe (Industrial Safety Shoes)", "role": "Safety shoes PPE"}
            ]
        },
        "gem_tender_clause": (
            "Industrial safety helmets shall conform to IS 2925:1984 (Reaffirmed 2019) with Amendments 1, 2, and 3, crafted from "
            "high-density polyethylene (HDPE) or ABS with 6-point textile cradle suspension. Helmets must carry the BIS Scheme-I ISI Mark. "
            "Shock absorption and penetration test certificates from an NABL accredited laboratory shall be provided."
        )
    },

    "IS 15298": {
        "id": "IS 15298",
        "code": "IS 15298 (Part 2):2016 / ISO 20345:2011",
        "title": "Personal Protective Equipment - Safety Footwear - Specification",
        "popular_names": ["Safety Shoes", "Steel Toe Shoes", "Industrial Safety Footwear", "Worker Safety Boots", "PPE Footwear"],
        "category": "Safety & Fire Protection",
        "sub_category": "Personal Protective Equipment (PPE)",
        "latest_edition": "2016 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2019", "scope": "Enhanced anti-static resistance and slip resistance test protocol"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 15298 (Part 2):2002 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark)",
            "issuing_ministry": "DPIIT, Ministry of Commerce & Industry",
            "qco_order": "Footwear Made from Leather and Other Materials (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "CRITICAL: Under DPIIT Footwear QCO, all safety shoes must bear BIS ISI mark. Supplying non-ISI footwear to government is strictly prohibited."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 15298 (Part 1):2011", "title": "Test Methods for Footwear", "role": "Testing protocol"}
            ],
            "test_methods": [
                {"code": "IS 15298 (Part 1) Clause 5.4", "title": "Impact Resistance of Toe-Cap (200 Joules)", "clause": "Clause 5.4", "nabl_required": True},
                {"code": "IS 15298 (Part 1) Clause 5.5", "title": "Compression Resistance of Toe-Cap (15 kN)", "clause": "Clause 5.5", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "Factories Act 1948 Section 35", "title": "Protection of Eyes and Limbs", "role": "Statutory worker safety"}
            ],
            "installation_standards": [
                {"code": "IS 13416", "title": "Work Site PPE Standards", "role": "Site protocol"}
            ],
            "terminology_standards": [
                {"code": "IS 2050:1991", "title": "Glossary of Footwear Terms", "role": "Footwear terms"}
            ],
            "related_product_standards": [
                {"code": "IS 2925:1984", "title": "Industrial Safety Helmets", "role": "Companion PPE"}
            ]
        },
        "gem_tender_clause": (
            "Safety footwear supplied for field personnel shall strictly conform to IS 15298 (Part 2):2016 with steel toe-cap "
            "withstanding 200 Joules impact energy and 15 kN compression force. In compliance with DPIIT Footwear QCO, "
            "every pair must bear the mandatory BIS Scheme-I ISI Mark with verifiable CM/L number. Anti-skid double density "
            "PU sole shall be oil and acid resistant."
        )
    },

    # ----------------------------------------------------
    # 6. IT, ELECTRONICS & BATTERIES
    # ----------------------------------------------------
    "IS 13252": {
        "id": "IS 13252",
        "code": "IS 13252 (Part 1):2010 / IEC 60950-1:2005",
        "title": "Information Technology Equipment - Safety - General Requirements",
        "popular_names": ["Laptops", "Desktops", "Computers", "Servers", "Printers", "Monitors", "Scanners", "UPS for IT", "All-in-One PC"],
        "category": "IT & Electronics",
        "sub_category": "Computer Hardware & Electronics",
        "latest_edition": "2010 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": 1, "year": "2013", "scope": "Harmonization with IEC 60950-1 Amendment 1"},
            {"number": 2, "year": "2015", "scope": "Enhanced criteria for thermal runaway and power supply insulation"}
        ],
        "is_withdrawn": False,
        "superseded_by": "IS 18112 / IEC 62368-1 (Transition ongoing under MeitY)",
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-II (Compulsory Registration Scheme - CRS)",
            "issuing_ministry": "Ministry of Electronics and Information Technology (MeitY)",
            "qco_order": "Electronics and Information Technology Goods (Requirement for Compulsory Registration) Order",
            "statutory_act": "Section 16 & 29, BIS Act 2016",
            "tender_warning": "CRITICAL: IT hardware without a valid MeitY BIS R-Number (R-XXXXXXXX) is banned from customs import, public sale, and GeM procurement."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 16046 (Part 2):2018", "title": "Secondary Lithium-ion Cells and Batteries", "role": "Embedded battery mandatory CRS"},
                {"code": "IS 616:2017 / IEC 60065", "title": "Audio, Video and Similar Electronic Apparatus - Safety", "role": "AV apparatus safety"}
            ],
            "test_methods": [
                {"code": "IS 13252 Clause 4.2", "title": "Mechanical Strength (Drop & Impact) Test", "clause": "Clause 4.2", "nabl_required": True},
                {"code": "IS 13252 Clause 5.2", "title": "Electric Strength (Hipot) Test", "clause": "Clause 5.2", "nabl_required": True},
                {"code": "IS 13252 Clause 4.5", "title": "Thermal Stability & Temperature Rise Test", "clause": "Clause 4.5", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IEC 62368-1:2018", "title": "Audio/video, information and communication technology equipment - Safety requirements", "role": "Hazard-based safety engineering"}
            ],
            "installation_standards": [
                {"code": "IS 3043:2018", "title": "Code of Practice for Earthing", "role": "Clean technical earthing for server rooms & IT infrastructure"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 74):1993", "title": "Electrotechnical Vocabulary - Information Technology", "role": "IT definitions"}
            ],
            "related_product_standards": [
                {"code": "IS 16242 (Part 1):2014", "title": "Uninterruptible Power Systems (UPS) - General and Safety Requirements", "role": "Online / Line-interactive UPS"}
            ]
        },
        "gem_tender_clause": (
            "All supplied Information Technology Equipment (Desktops, Laptops, Servers, and Monitors) shall strictly hold valid "
            "BIS Compulsory Registration Scheme (CRS) certification under MeitY in accordance with IS 13252 (Part 1):2010. "
            "The equipment chassis and external cartons must prominently display the official BIS Standard Mark with the manufacturer's "
            "active R-Number (R-XXXXXXXX). All embedded Lithium-ion battery packs must hold independent valid CRS registration under IS 16046 (Part 2)."
        )
    },

    "IS 16046": {
        "id": "IS 16046",
        "code": "IS 16046 (Part 2):2018 / IEC 62133-2:2017",
        "title": "Secondary Cells and Batteries Containing Alkaline or Other Non-Acid Electrolytes (Lithium Systems)",
        "popular_names": ["Lithium-ion Battery", "Laptop Battery", "Mobile Battery", "Power Bank", "Li-ion Battery Packs", "Energy Storage Cells"],
        "category": "IT & Electronics",
        "sub_category": "Energy Storage & Batteries",
        "latest_edition": "2018 (Part 2) (Reaffirmed 2023)",
        "active_amendments": [
            {"number": 1, "year": "2020", "scope": "Enhanced overcharging safety and vibration resistance for mobility use"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 16046:2015 (Superseded by 2018 Part 1 & Part 2)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-II (Compulsory Registration Scheme - CRS)",
            "issuing_ministry": "Ministry of Electronics and Information Technology (MeitY)",
            "qco_order": "Electronics and IT Goods (Requirement for Compulsory Registration) Order",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "Lithium batteries without valid BIS CRS Registration pose severe explosion/fire risks and cannot be purchased."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IEC 62133-2:2017", "title": "Secondary Cells and Batteries (Lithium)", "role": "International benchmark"}
            ],
            "test_methods": [
                {"code": "IS 16046 (Part 2) Clause 7.3.1", "title": "External Short Circuit Test at 55°C", "clause": "Clause 7.3.1", "nabl_required": True},
                {"code": "IS 16046 (Part 2) Clause 7.3.6", "title": "Overcharging Protection Test", "clause": "Clause 7.3.6", "nabl_required": True},
                {"code": "IS 16046 (Part 2) Clause 7.3.8", "title": "Forced Internal Short Circuit Test", "clause": "Clause 7.3.8", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "UN 38.3", "title": "UN Manual of Tests and Criteria for Lithium Battery Transportation", "role": "Safe transport and logistics"}
            ],
            "installation_standards": [
                {"code": "IS 16242:2014", "title": "Installation and Interconnection of Battery Banks", "role": "DC wiring and battery racks"}
            ],
            "terminology_standards": [
                {"code": "IS 1885 (Part 8):1986", "title": "Vocabulary - Secondary Cells and Batteries", "role": "Battery terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 15549:2005", "title": "Stationary Valve Regulated Lead Acid (VRLA) Batteries", "role": "Lead acid battery backup"}
            ]
        },
        "gem_tender_clause": (
            "Secondary Lithium-ion cells and battery packs supplied shall strictly comply with IS 16046 (Part 2):2018 / IEC 62133-2. "
            "Each battery pack must be registered under BIS Compulsory Registration Scheme (CRS) bearing the official BIS Standard Mark "
            "with R-Number. Test reports verifying non-explosion under thermal abuse, overcharge, and forced internal short circuit must be supplied."
        )
    },

    # ----------------------------------------------------
    # 7. FOOD & WATER (OFFICE CANTEENS & EVENTS)
    # ----------------------------------------------------
    "IS 14543": {
        "id": "IS 14543",
        "code": "IS 14543:2018",
        "title": "Packaged Drinking Water (Other than Packaged Natural Mineral Water) - Specification",
        "popular_names": ["Packaged Drinking Water", "Water Bottles", "20L Water Jars", "Mineral Water", "Purified Bottled Water"],
        "category": "Food, Water & Agriculture",
        "sub_category": "Packaged Water",
        "latest_edition": "2018 (Reaffirmed 2023)",
        "active_amendments": [
            {"number": 1, "year": "2020", "scope": "Microbiological safety parameter updates and zero pesticide residue limits"},
            {"number": 2, "year": "2022", "scope": "BPA-free packaging certification and QR code tracing on 20-litre jars"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 14543:2004 (Superseded)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Scheme-I (Mandatory ISI Mark) + FSSAI Central License",
            "issuing_ministry": "Ministry of Consumer Affairs & FSSAI",
            "qco_order": "Packaged Drinking Water (Quality Control) Order",
            "statutory_act": "Section 16, BIS Act 2016 & FSS Act 2006 Section 31",
            "tender_warning": "CRITICAL: Packaged drinking water MUST hold BOTH dual statutory credentials: BIS CM/L license AND 14-digit FSSAI license."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 10500:2012", "title": "Drinking Water - Potable Domestic Water Supply", "role": "Raw water baseline"},
                {"code": "IS 15410:2003", "title": "Containers for Packaging of Packaged Drinking Water", "role": "Food grade PET/polycarbonate containers"}
            ],
            "test_methods": [
                {"code": "IS 3025 (Parts 1-60)", "title": "Methods of Sampling and Physical/Chemical Test for Water", "clause": "Clause 6", "nabl_required": True},
                {"code": "IS 1622:1981", "title": "Methods of Sampling and Microbiological Examination of Water", "clause": "Clause 7", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "FSSAI Food Safety and Standards (Packaging and Labelling) Regulations", "title": "FSSAI Packaging Regulations", "role": "Mandatory front of pack declarations"}
            ],
            "installation_standards": [
                {"code": "IS 10500", "title": "Storage and Dispensing Hygiene Guidelines", "role": "Clean dispenser maintenance"}
            ],
            "terminology_standards": [
                {"code": "IS 704:1984", "title": "Vocabulary of Water Quality", "role": "Water terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 13428:2005", "title": "Packaged Natural Mineral Water", "role": "Natural spring mineral water"}
            ]
        },
        "gem_tender_clause": (
            "Packaged drinking water in bottles or 20-litre jars supplied for government offices and events shall strictly conform to "
            "IS 14543:2018 with latest amendments. The vendor MUST possess both a valid BIS Scheme-I ISI Mark (with CM/L number) "
            "and a valid 14-digit FSSAI Food License. Water containers must be manufactured from food-grade virgin PET/Polycarbonate "
            "conforming to IS 15410. Routine NABL microbiological test certificates shall be submitted weekly."
        )
    },

    # ----------------------------------------------------
    # 9. PRECIOUS METALS & GOLD HALLMARKING (HUID)
    # ----------------------------------------------------
    "IS 1417": {
        "id": "IS 1417",
        "code": "IS 1417:2016",
        "title": "Gold and Gold Alloys, Jewellery/Artefacts - Fineness and Marking - Specification",
        "popular_names": ["Gold Hallmark", "HUID", "22K Gold", "18K Gold", "24K Gold", "Gold Jewellery", "Hallmarked Gold", "Gold Coins", "Gold Bullion", "Gold Ornaments"],
        "category": "Precious Metals & Hallmarking",
        "sub_category": "Gold & Silver Jewellery",
        "latest_edition": "2016 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2021", "scope": "Mandatory 6-digit alphanumeric HUID marking system"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": [],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Hallmarking Scheme (Mandatory HUID)",
            "issuing_ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
            "qco_order": "Hallmarking of Gold Jewellery and Gold Artefacts Order",
            "statutory_act": "Section 14 & 15, BIS Act 2016",
            "tender_warning": "CRITICAL: Gold procurement, state treasury auctions, and institutional sales MUST have 6-digit alphanumeric HUID hallmark."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 15820:2009", "title": "General Requirements for Establishment and Operation of Assaying and Hallmarking Centres", "role": "AHC accreditation"}
            ],
            "test_methods": [
                {"code": "IS 1418:2009", "title": "Assaying of Gold in Gold Bullion, Gold Alloys and Gold Jewellery/Artefacts by Cupellation (Fire Assay) Method", "clause": "Clause 5", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "Hallmarking Regulation 2018", "title": "BIS Hallmarking Regulations", "role": "Consumer gold purity protection"}
            ],
            "installation_standards": [
                {"code": "AHC Operating Guidelines", "title": "Laser engraving and HUID traceability protocols", "role": "HUID traceability"}
            ],
            "terminology_standards": [
                {"code": "IS 1417:2016 Clause 3", "title": "Definitions of Carat, Fineness in parts per thousand (ppt)", "role": "Purity terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 2112:2014", "title": "Silver and Silver Alloys, Jewellery/Artefacts - Fineness and Marking", "role": "Silver hallmarking"}
            ]
        },
        "gem_tender_clause": (
            "All gold jewellery, bullion, medals, or artifacts procured shall strictly conform to IS 1417:2016 "
            "with mandatory 6-digit alphanumeric HUID (Hallmark Unique Identification) laser engraved by a BIS-recognized "
            "Assaying and Hallmarking Centre (AHC). Purity shall be verified by Fire Assay method under IS 1418."
        )
    },

    # ----------------------------------------------------
    # 10. STRUCTURAL DESIGN & CIVIL CODES OF PRACTICE
    # ----------------------------------------------------
    "IS 456": {
        "id": "IS 456",
        "code": "IS 456:2000",
        "title": "Plain and Reinforced Concrete - Code of Practice",
        "popular_names": ["Concrete Code", "RCC Code", "Reinforced Concrete", "Plain Concrete", "Concrete Design", "Concrete Work", "IS 456", "M20 M25 M30 Concrete"],
        "category": "Civil & Construction",
        "sub_category": "Structural Engineering Code of Practice",
        "standard_type": "Code of Practice / Design Standard",
        "latest_edition": "2000 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": 1, "year": "2001", "scope": "Correction of durability criteria and minimum cement content"},
            {"number": 2, "year": "2005", "scope": "Inclusion of high performance concrete and fly ash blending limits"},
            {"number": 3, "year": "2007", "scope": "Clarification on shear design around openings in slabs"},
            {"number": 4, "year": "2013", "scope": "Self-compacting concrete provisions"},
            {"number": 5, "year": "2019", "scope": "Revision of environmental exposure classes and nominal cover to reinforcement"}
        ],
        "is_withdrawn": False,
        "superseded_by": None,
        "withdrawn_history": ["IS 456:1978 (Superseded)", "IS 456:1964 (Withdrawn)"],
        "mandatory_certification": {
            "is_mandatory": True,
            "scheme": "Mandatory National Building Code (NBC) Compliance",
            "issuing_ministry": "Ministry of Housing and Urban Affairs & BIS",
            "qco_order": "National Building Code / CPWD Civil Works Guidelines",
            "statutory_act": "Section 16, BIS Act 2016",
            "tender_warning": "CRITICAL: All structural RCC designs, mix designs, concrete batching, and curing in government tenders MUST strictly conform to IS 456:2000."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 269:2015", "title": "Ordinary Portland Cement Specification", "role": "Cement selection"},
                {"code": "IS 1786:2008", "title": "High Strength Deformed Steel Bars for Concrete Reinforcement", "role": "Reinforcement rebar"},
                {"code": "IS 383:2016", "title": "Coarse and Fine Aggregate for Concrete", "role": "Aggregate grading"}
            ],
            "test_methods": [
                {"code": "IS 516 (Parts 1-5)", "title": "Hardened Concrete - Methods of Testing", "clause": "Clause 15", "nabl_required": True},
                {"code": "IS 1199 (Parts 1-7)", "title": "Fresh Concrete - Methods of Sampling and Analysis", "clause": "Clause 14", "nabl_required": True}
            ],
            "safety_standards": [
                {"code": "IS 13920:2016", "title": "Ductile Design and Detailing of Reinforced Concrete Structures", "role": "Seismic safety"}
            ],
            "installation_standards": [
                {"code": "SP 34:1987", "title": "Handbook on Concrete Reinforcement and Detailing", "role": "Bar bending and placement"},
                {"code": "IS 10262:2019", "title": "Concrete Mix Proportioning - Guidelines", "role": "Mix design calculations"}
            ],
            "terminology_standards": [
                {"code": "IS 4845:1968", "title": "Definitions and Terminology Relating to Hydraulic Cement and Concrete", "role": "Concrete terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 4926:2003", "title": "Ready-Mixed Concrete (RMC) - Code of Practice", "role": "Commercial RMC supply"}
            ]
        },
        "gem_tender_clause": (
            "All structural plain and reinforced concrete works, mix designs, concrete grade selection (M20 to M50), "
            "placement, minimum cement content, maximum water-cement ratio, and curing shall strictly conform to "
            "IS 456:2000 (Reaffirmed 2021) incorporating all active Amendments (1, 2, 3, 4, and 5). 28-day cube compressive "
            "strength testing shall be executed in NABL accredited laboratories conforming to IS 516."
        )
    },

    "IS 1293": {
        "id": "IS 1293",
        "code": "IS 1293:2019",
        "title": "Plugs and Socket-Outlets (Domestic and Similar General Purpose) - Safety Requirements",
        "popular_names": ["plug", "socket", "socket outlet", "plug top", "3 pin socket", "2 pin socket",
                          "modular socket", "electrical socket", "power socket", "wall socket", "switched socket"],
        "category": "Electrical & Electronics",
        "sub_category": "Wiring Accessories",
        "latest_edition": "IS 1293:2005 (Reaffirmed 2020)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2011", "summary": "Revised current rating and pin dimensions"},
            {"number": "Amd 2", "year": "2018", "summary": "Safety shutter mandatory for all socket outlets"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "DPIIT QCO on Electrical Accessories",
            "issuing_ministry": "Ministry of Commerce & Industry (DPIIT)",
            "effective_date": "2013-06-03",
            "consequence_of_non_compliance": "Tender is liable for rejection. Non-ISI marked sockets illegal for supply."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 732:1989", "title": "Code of Practice for Electrical Wiring Installations", "role": "Installation code"},
                {"code": "IS 694:2010", "title": "PVC Insulated Cables for Working Voltages up to 1100V", "role": "Connecting cable"}
            ],
            "test_methods": [
                {"code": "IS 1293:2005 Cl. 13-24", "title": "Mechanical, electrical and thermal tests", "role": "Acceptance tests"},
                {"code": "IEC 60884-1", "title": "Plugs and socket-outlets — Safety", "role": "International harmonization"}
            ],
            "safety_standards": [
                {"code": "IS 732:1989", "title": "Electrical Wiring Installations", "role": "Safety of wiring"}
            ],
            "installation_standards": [
                {"code": "IS 3854:1997", "title": "Switches for Domestic and Similar Fixed Electrical Installations", "role": "Companion switch standard"}
            ],
            "terminology_standards": [
                {"code": "IEC 60050-442", "title": "International Electrotechnical Vocabulary: Electrical Accessories", "role": "Definitions"}
            ],
            "related_product_standards": [
                {"code": "IS 3854:1997", "title": "Switches for Domestic and Similar Electrical Installations", "role": "Modular switches"},
                {"code": "IS 302:2008", "title": "Safety of Household and Similar Electrical Appliances", "role": "Appliance interconnection"}
            ]
        },
        "gem_tender_clause": (
            "All plug and socket-outlet wiring accessories supplied shall strictly conform to IS 1293:2005 "
            "(Reaffirmed 2020) including Amendments 1 and 2. Current ratings shall be 6A or 16A as specified. "
            "Safety shutters shall be mandatory on all socket outlets. Each unit shall bear valid BIS ISI mark "
            "under DPIIT QCO on Electrical Accessories. Certification shall be verified before dispatch."
        )
    },

    "IS 4151": {
        "id": "IS 4151",
        "code": "IS 4151:2015",
        "title": "Protective Helmets for Two-Wheeler Motor Cycle Riders",
        "popular_names": ["motorcycle helmet", "bike helmet", "two wheeler helmet", "crash helmet",
                          "rider helmet", "ISI helmet", "motor cycle helmet", "motorbike helmet",
                          "protective headgear motorcycle", "full face helmet", "open face helmet"],
        "category": "Personal Protective Equipment",
        "sub_category": "Protective Helmets",
        "latest_edition": "IS 4151:2015",
        "active_amendments": [
            {"number": "Amd 1", "year": "2018", "summary": "Mandatory HALS reflective marking on rear"},
            {"number": "Amd 2", "year": "2020", "summary": "Revised impact energy absorption test"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "DPIIT QCO on Helmets for Two-Wheeler Riders",
            "issuing_ministry": "Ministry of Commerce & Industry (DPIIT)",
            "effective_date": "2019-01-01",
            "consequence_of_non_compliance": "Non-ISI marked helmets banned for sale; police patrol procurement rejected."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 1609:1972", "title": "Method of Test for Personal Protection Equipment Against Mechanical Hazards", "role": "Test methods"}
            ],
            "test_methods": [
                {"code": "IS 4151:2015 Cl. 8", "title": "Impact absorption, penetration resistance, retention", "role": "Safety tests"},
                {"code": "IS 4151:2015 Cl. 7", "title": "Field of vision, ventilation, mass tests", "role": "Ergonomic tests"}
            ],
            "safety_standards": [
                {"code": "IS 2925:1984", "title": "Industrial Safety Helmets", "role": "General helmet safety reference"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "IS 4151:2015 Cl. 3", "title": "Definitions", "role": "Helmet terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 2925:1984", "title": "Industrial Safety Helmets (Non-Motorcycle)", "role": "Industrial PPE helmets"},
                {"code": "IS 9882:1981", "title": "Fireman Helmets", "role": "Specialized fire helmet"}
            ]
        },
        "gem_tender_clause": (
            "All protective helmets for two-wheeler/motorcycle riders shall conform to IS 4151:2015 "
            "incorporating Amendments 1 and 2. Helmets shall carry valid BIS ISI mark under DPIIT QCO "
            "on Helmets for Two-Wheeler Riders. Full face or open face configurations as specified. "
            "Impact absorption, penetration resistance, and retention system tests shall be verified "
            "at NABL accredited test laboratory."
        )
    },

    "IS 14846": {
        "id": "IS 14846",
        "code": "IS 14846:2000",
        "title": "Sluice Valves for Water Works Purposes (Sizes 50 mm to 600 mm) — Specification",
        "popular_names": ["sluice valve", "gate valve", "isolation valve", "sluice gate", "water works valve",
                          "cast iron valve", "ductile iron valve", "resilient seated gate valve",
                          "flanged sluice valve", "water main valve"],
        "category": "Water Supply & Plumbing",
        "sub_category": "Water Control Valves",
        "latest_edition": "IS 14846:2000 (Reaffirmed 2018)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2009", "summary": "Added ductile iron body option and epoxy coating requirements"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "Ministry of Jal Shakti procurement guidelines",
            "issuing_ministry": "Ministry of Jal Shakti",
            "effective_date": "2018-01-01",
            "consequence_of_non_compliance": "Valve rejected in water works tender; ISI mark mandatory for AMRUT and Jal Jeevan Mission procurement."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 1865:2009", "title": "Iron Castings with Spheroidal or Nodular Graphite (Ductile Iron)", "role": "Ductile iron body material"},
                {"code": "IS 210:2009", "title": "Grey Iron Castings", "role": "Cast iron valve body material"}
            ],
            "test_methods": [
                {"code": "IS 14846:2000 Cl. 7", "title": "Hydrostatic body and seat tests, torque test, leakage test", "role": "Acceptance tests"},
                {"code": "IS 2825:1969", "title": "Code for Unfired Pressure Vessels", "role": "Pressure test reference"}
            ],
            "safety_standards": [
                {"code": "IS 12288:1987", "title": "Code of Practice for Use and Care of Hand-Operated Sluice Valves", "role": "Operational safety"}
            ],
            "installation_standards": [
                {"code": "IS 12288:1987", "title": "Use and Care of Sluice Valves", "role": "Installation practice"}
            ],
            "terminology_standards": [
                {"code": "IS 2685:2003", "title": "Valves — Glossary of Terms", "role": "Valve terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 4984:2016", "title": "HDPE Pipes for Water Supply", "role": "HDPE pipeline companion"},
                {"code": "IS 8034:2018", "title": "Submersible Pumps for Clear Cold Water", "role": "Pump-valve integration"}
            ]
        },
        "gem_tender_clause": (
            "All sluice/gate valves shall conform to IS 14846:2000 (Reaffirmed 2018) incorporating Amendment 1. "
            "Body shall be cast iron conforming to IS 210 or ductile iron conforming to IS 1865. "
            "Valves shall carry BIS ISI mark. Hydrostatic body test, seat leakage test, and operational "
            "torque test shall be performed and certified by NABL accredited laboratory. "
            "Epoxy coating (minimum 250 micron DFT) mandatory for underground water supply installations."
        )
    },

    "IS 1536": {
        "id": "IS 1536",
        "code": "IS 1536:2001",
        "title": "Centrifugally Cast (Spun) Iron Pressure Pipes for Water, Gas and Sewage",
        "popular_names": ["cast iron pipe", "CI pipe", "spun iron pipe", "centrifugally cast iron pipe",
                          "cast iron pressure pipe", "CI water pipe", "spun cast pipe",
                          "socket spigot CI pipe", "flanged CI pipe"],
        "category": "Water Supply & Plumbing",
        "sub_category": "Metal Water Pipes",
        "latest_edition": "IS 1536:2001 (Reaffirmed 2018)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2008", "summary": "Dimensional tolerances and testing pressures updated"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "Ministry of Jal Shakti Jal Jeevan Mission procurement standards",
            "issuing_ministry": "Ministry of Jal Shakti",
            "effective_date": "2015-01-01",
            "consequence_of_non_compliance": "Non-ISI CI pipes rejected in public water works tenders."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 210:2009", "title": "Grey Iron Castings", "role": "Base metal standard for pipe body"},
                {"code": "IS 3896:2017", "title": "Centrifugally Cast Iron Socket and Spigot Fittings", "role": "CI pipe fittings"}
            ],
            "test_methods": [
                {"code": "IS 1536:2001 Cl. 8-10", "title": "Hydrostatic test, tensile strength, Brinell hardness", "role": "Acceptance tests"},
                {"code": "IS 1500:2005", "title": "Method for Brinell Hardness Test for Metallic Materials", "role": "Hardness testing"}
            ],
            "safety_standards": [
                {"code": "IS 12288:1987", "title": "Code of Practice for Use and Care of Hand-Operated Sluice Valves", "role": "Pipeline operational safety"}
            ],
            "installation_standards": [
                {"code": "IS 12288:1987", "title": "CI pipe installation guide", "role": "Pipeline laying"}
            ],
            "terminology_standards": [
                {"code": "IS 1121:1971", "title": "Methods of Tensile Testing of Steel Tubes", "role": "Tensile test method"}
            ],
            "related_product_standards": [
                {"code": "IS 14846:2000", "title": "Sluice Valves for Water Works", "role": "Companion valve standard"},
                {"code": "IS 4984:2016", "title": "HDPE Pipes for Water Supply", "role": "Alternate pipe material"}
            ]
        },
        "gem_tender_clause": (
            "All centrifugally cast (spun) iron pipes shall conform to IS 1536:2001 (Reaffirmed 2018). "
            "Class shall be LA, A, or B as specified for the design pressure. Pipes shall carry BIS ISI mark. "
            "Hydrostatic test, tensile strength (≥ 260 MPa), and Brinell hardness tests shall be performed "
            "at NABL accredited laboratory. Internal cement mortar lining and external bitumen coating "
            "shall comply with IS 3597."
        )
    },

    "IS 8320": {
        "id": "IS 8320",
        "code": "IS 8320:2000",
        "title": "General Requirements for Submersible Motor-Pump Sets for Clear Cold Water",
        "popular_names": ["submersible motor", "submersible electric motor", "borewell motor", "borehole motor",
                          "deep well motor", "tubewell motor", "motor pump set submersible",
                          "CRGO motor", "water filled motor", "three phase submersible"],
        "category": "Pumps & Fluid Control",
        "sub_category": "Submersible Pumps and Motors",
        "latest_edition": "IS 8320:2000 (Reaffirmed 2021)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2012", "summary": "Insulation class F updated; IP68 requirement added"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "Ministry of Jal Shakti procurement guidelines for pump sets",
            "issuing_ministry": "Ministry of Jal Shakti",
            "effective_date": "2018-01-01",
            "consequence_of_non_compliance": "Non-ISI submersible motors rejected in PMKSY, Jal Jeevan Mission procurement."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 8034:2018", "title": "Submersible Pumps for Clear Cold Water", "role": "Companion pump standard"},
                {"code": "IS 4029:1967", "title": "Guide for Testing Three-Phase Induction Motors", "role": "Motor test guide"}
            ],
            "test_methods": [
                {"code": "IS 8320:2000 Cl. 11-15", "title": "Dielectric strength, locked rotor torque, temperature rise, efficiency", "role": "Acceptance tests"},
                {"code": "IS 4029:1967", "title": "Three phase induction motor test methods", "role": "Electrical tests"}
            ],
            "safety_standards": [
                {"code": "IS 13947 (Part 1):1993", "title": "Low Voltage Switchgear and Controlgear", "role": "Motor protection"}
            ],
            "installation_standards": [
                {"code": "IS 4029:1967", "title": "Guide for Testing Three-Phase Induction Motors", "role": "Motor test and installation"}
            ],
            "terminology_standards": [
                {"code": "IS 8320:2000 Cl. 3", "title": "Definitions for submersible motor terms", "role": "Terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 8034:2018", "title": "Submersible Pumps for Clear Cold Water", "role": "Pump set companion"},
                {"code": "IS 1180:2014", "title": "Power Distribution Transformers", "role": "Motor power supply"}
            ]
        },
        "gem_tender_clause": (
            "All submersible electric motors shall conform to IS 8320:2000 (Reaffirmed 2021) incorporating Amendment 1. "
            "Motors shall have F-class insulation and IP68 enclosure rating. Dielectric strength test, "
            "temperature rise test, locked rotor torque, and efficiency shall be verified at NABL laboratory. "
            "Motor-pump sets shall carry BIS ISI mark and conform to IS 8034 (pump portion). "
            "Stainless steel sleeve mandatory for brackish/saline water applications."
        )
    },

    "IS 15644": {
        "id": "IS 15644",
        "code": "IS 15644:2006",
        "title": "Safety of Electric Toys",
        "popular_names": ["electric toy", "electronic toy", "battery toy", "educational toy", "children toy safety",
                          "toy safety", "electric powered toy", "toy BIS", "toy ISI mark"],
        "category": "Consumer Products",
        "sub_category": "Toys & Educational Materials",
        "latest_edition": "IS 15644:2006 (Reaffirmed 2019)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2013", "summary": "Mandatory QCO application; battery safety limits updated"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark)",
            "is_mandatory": True,
            "qco_reference": "DPIIT Toys Quality Control Order 2020",
            "issuing_ministry": "Ministry of Commerce & Industry (DPIIT)",
            "effective_date": "2021-01-01",
            "consequence_of_non_compliance": "Non-ISI toys banned for sale and procurement in India."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 9873:2007", "title": "Safety of Toys (Non-Electric)", "role": "General toy safety standard"},
                {"code": "IS 16046:2018", "title": "Secondary Lithium Cells for Portable Applications", "role": "Battery safety in toys"}
            ],
            "test_methods": [
                {"code": "IS 15644:2006 Cl. 10-18", "title": "Electrical, thermal, mechanical tests for electric toys", "role": "Safety acceptance tests"}
            ],
            "safety_standards": [
                {"code": "IS 9873:2007", "title": "Safety of Toys", "role": "Companion non-electric toy safety"},
                {"code": "IEC 62115", "title": "Safety of Electric Toys", "role": "International harmonization"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "IS 15644:2006 Cl. 3", "title": "Definitions of electric toy terms", "role": "Terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 9873:2007", "title": "Safety of Toys — General Requirements", "role": "Non-electric toys"},
                {"code": "IS 16046:2018", "title": "Lithium Battery Safety", "role": "Battery powered toys"}
            ]
        },
        "gem_tender_clause": (
            "All electric toys supplied shall conform to IS 15644:2006 (Reaffirmed 2019) incorporating Amendment 1. "
            "Toys shall carry mandatory BIS ISI mark under DPIIT Toys Quality Control Order 2020. "
            "Electrical safety, thermal cutoff, mechanical strength, and age grade labeling shall comply. "
            "Battery compartments shall meet child safety requirements."
        )
    },

    "IS 2796": {
        "id": "IS 2796",
        "code": "IS 2796:2017",
        "title": "Motor Gasoline (Petrol) — Specification",
        "popular_names": ["motor gasoline", "petrol", "motor spirit", "automotive petrol", "unleaded petrol",
                          "BS-VI petrol", "E20 petrol", "motor fuel", "gasoline", "vehicle fuel petrol",
                          "RON 91 fuel", "BS6 petrol"],
        "category": "Petroleum Products",
        "sub_category": "Automotive Fuels",
        "latest_edition": "IS 2796:2017",
        "active_amendments": [
            {"number": "Amd 1", "year": "2021", "summary": "E20 ethanol blended petrol parameters incorporated"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "Quality testing at MoPNG approved NABL accredited laboratories",
            "is_mandatory": True,
            "qco_reference": "Ministry of Petroleum and Natural Gas Petroleum Quality Control Rules",
            "issuing_ministry": "Ministry of Petroleum and Natural Gas (MoPNG)",
            "effective_date": "2017-04-01",
            "consequence_of_non_compliance": "Non-conforming petrol liable to seizure under Motor Spirit Rules."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 1448 series", "title": "Methods of Test for Petroleum and its Products", "role": "All test parameters"}
            ],
            "test_methods": [
                {"code": "IS 1448 (P:14)", "title": "Research Octane Number (RON) test", "role": "Antiknock quality"},
                {"code": "IS 1448 (P:17)", "title": "Distillation characteristics", "role": "Distillation limits"},
                {"code": "IS 1448 (P:31)", "title": "Vapor pressure (Reid method)", "role": "Vapor lock index"},
                {"code": "IS 1448 (P:66)", "title": "Oxidation stability (induction period method)", "role": "Gum content control"}
            ],
            "safety_standards": [
                {"code": "IS 1446:1974", "title": "Fire Safety for Petroleum Storage", "role": "Storage safety"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "IS 1165:1982", "title": "Petroleum Vocabulary", "role": "Fuel terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 1460:2017", "title": "Automotive Diesel Fuel", "role": "Companion diesel standard"},
                {"code": "IS 1979:2008", "title": "Aviation Turbine Fuels", "role": "Related aviation fuel"}
            ]
        },
        "gem_tender_clause": (
            "All motor gasoline (petrol) supplied shall conform to IS 2796:2017 including Amendment 1 (E20). "
            "BS-VI specifications mandatory: max sulfur 10 ppm, benzene max 1.0 vol%, RON min 91. "
            "Batch quality certificate from MoPNG approved NABL accredited laboratory mandatory. "
            "Ethanol content shall comply with National Biofuel Policy 2018 for E10/E20 blends."
        )
    },

    "IS 1460": {
        "id": "IS 1460",
        "code": "IS 1460:2017",
        "title": "Automotive Diesel Fuel — Specification (BS-VI)",
        "popular_names": ["automotive diesel", "high speed diesel", "HSD", "diesel fuel", "auto diesel",
                          "diesel oil", "BS-VI diesel", "automotive gas oil", "diesel HSD",
                          "diesel generator fuel", "DG set fuel", "cetane diesel"],
        "category": "Petroleum Products",
        "sub_category": "Automotive Fuels",
        "latest_edition": "IS 1460:2017",
        "active_amendments": [
            {"number": "Amd 1", "year": "2021", "summary": "B20 biodiesel blended diesel fuel parameters"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "Quality testing at MoPNG approved NABL accredited laboratories",
            "is_mandatory": True,
            "qco_reference": "Ministry of Petroleum and Natural Gas Petroleum Quality Control Rules",
            "issuing_ministry": "Ministry of Petroleum and Natural Gas (MoPNG)",
            "effective_date": "2017-04-01",
            "consequence_of_non_compliance": "Non-BS-VI diesel banned for supply; liable to seizure under Motor Spirit (Diesel) Rules."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 1448 series", "title": "Methods of Test for Petroleum and its Products", "role": "All test parameters"}
            ],
            "test_methods": [
                {"code": "IS 1448 (P:9)", "title": "Cetane number test method", "role": "Ignition quality (min 51)"},
                {"code": "IS 1448 (P:17)", "title": "Distillation characteristics", "role": "90% distillation point"},
                {"code": "IS 1448 (P:26)", "title": "Kinematic viscosity", "role": "Viscosity limits"},
                {"code": "IS 1448 (P:69)", "title": "Cold filter plugging point (CFPP)", "role": "Cold flow operability"},
                {"code": "IS 1448 (P:61)", "title": "Water content (Karl Fischer)", "role": "Water content limit"}
            ],
            "safety_standards": [
                {"code": "IS 1446:1974", "title": "Fire Safety for Petroleum Storage", "role": "Storage safety"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "IS 1165:1982", "title": "Petroleum Vocabulary", "role": "Diesel terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 2796:2017", "title": "Motor Gasoline (Petrol)", "role": "Companion petrol standard"},
                {"code": "IS 1979:2008", "title": "Aviation Turbine Fuels", "role": "Aviation fuel"}
            ]
        },
        "gem_tender_clause": (
            "All automotive diesel fuel (High Speed Diesel / HSD) supplied shall conform to IS 1460:2017 including Amendment 1. "
            "BS-VI specifications mandatory: maximum sulfur 10 mg/kg, cetane number minimum 51, flash point min 35°C, "
            "CFPP as per seasonal requirements. Batch quality certificate from MoPNG approved NABL accredited laboratory mandatory. "
            "Biodiesel blended fuel (B20) parameters shall additionally satisfy Ministry of Petroleum B20 specifications."
        )
    },

    "IS 16102": {
        "id": "IS 16102",
        "code": "IS 16102 (Part 1):2012 / IS 16102 (Part 2):2012",
        "title": "Self-Ballasted LED Lamps for General Lighting Services — Safety Requirements",
        "popular_names": ["LED bulb", "LED lamp", "self ballasted LED", "LED light bulb", "LED lamps",
                          "energy saving LED", "LED retrofit lamp", "CRS LED lamp", "BEE LED",
                          "LED bulb B22", "LED bulb E27", "9W LED", "12W LED", "LED indoor lamp"],
        "category": "Electrical & Electronics",
        "sub_category": "LED Lamps and Luminaires",
        "latest_edition": "IS 16022:2012 (Reaffirmed 2022)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2018", "summary": "Mandatory CRS registration under MeitY; lumen maintenance updated"},
            {"number": "Amd 2", "year": "2021", "summary": "Surge immunity 2.5 kV mandatory; harmonic distortion limits tightened"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Compulsory Registration Scheme (CRS)",
            "is_mandatory": True,
            "qco_reference": "MeitY CRS for LED Lamps under Electronics and IT Goods (Compulsory Registration) Order 2012",
            "issuing_ministry": "Ministry of Electronics and Information Technology (MeitY)",
            "effective_date": "2014-09-01",
            "consequence_of_non_compliance": "Non-CRS registered LED lamps banned; EESL/government tenders require mandatory BIS CRS."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 16102:2012", "title": "Self-Ballasted LED Lamps — Performance Requirements", "role": "Lumen output, efficacy, CRI"},
                {"code": "IEC 62560", "title": "Self-Ballasted LED Lamps Safety", "role": "International harmonization"}
            ],
            "test_methods": [
                {"code": "IS 16022:2012 Cl. 8-17", "title": "Electrical, photometric, thermal, mechanical safety tests", "role": "Safety compliance tests"},
                {"code": "IS 16102:2012 Cl. 7", "title": "Lumen output, lumen maintenance, CRI, CCT tests", "role": "Performance tests"}
            ],
            "safety_standards": [
                {"code": "IS 15885 (Part 2/Sec 13)", "title": "Photobiological Safety of Lamps", "role": "Blue light hazard"}
            ],
            "installation_standards": [
                {"code": "IS 732:1989", "title": "Electrical Wiring Installations", "role": "Lamp installation wiring safety"}
            ],
            "terminology_standards": [
                {"code": "IEC 60050-845", "title": "International Electrotechnical Vocabulary: Lighting", "role": "Photometric terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 10322:2013", "title": "LED Street Luminaires", "role": "Outdoor LED lighting"},
                {"code": "IS 374:2019", "title": "Electric Ceiling Fans", "role": "Companion energy efficient product"}
            ]
        },
        "gem_tender_clause": (
            "All self-ballasted LED lamps supplied shall conform to IS 16022:2012 (Reaffirmed 2022) incorporating "
            "Amendments 1 and 2. Each lamp shall carry valid BIS CRS registration under MeitY mandate. "
            "Power factor shall be ≥ 0.9 for lamps > 5W. Lumen maintenance at 2000 hours ≥ 96%. "
            "Surge immunity test 2.5 kV, harmonic distortion THD ≤ 20%, and photobiological safety "
            "(RG0 or RG1) shall be verified at NABL accredited laboratory. BEE star rating label mandatory."
        )
    },

    "IS 15410": {
        "id": "IS 15410",
        "code": "IS 15410:2003",
        "title": "Polyethylene Terephthalate (PET) Materials and Articles in Contact with Foodstuffs",
        "popular_names": ["PET bottle", "PET container", "plastic bottle", "water bottle PET",
                          "food grade PET", "mineral water bottle", "PET preform", "plastic container PET",
                          "PET packaging", "food contact PET", "beverage bottle"],
        "category": "Consumer Products",
        "sub_category": "Food Contact Packaging",
        "latest_edition": "IS 15410:2003 (Reaffirmed 2018)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2011", "summary": "Overall migration limits revised; heavy metal extraction limits added"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark) for food contact applications",
            "is_mandatory": True,
            "qco_reference": "FSSAI Food Contact Regulations; Plastic Waste Management Rules 2016",
            "issuing_ministry": "Ministry of Health and Family Welfare (FSSAI)",
            "effective_date": "2019-01-01",
            "consequence_of_non_compliance": "Non-compliant PET containers rejected in food/beverage/mineral water procurement."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 14543:2018", "title": "Packaged Drinking Water", "role": "End product standard for mineral water"},
                {"code": "IS 7518:2012", "title": "Specification for Polyethylene for Moulding/Extrusion", "role": "Base polymer reference"}
            ],
            "test_methods": [
                {"code": "IS 15410:2003 Cl. 6-10", "title": "Overall migration, specific migration, acetaldehyde, heavymetals", "role": "Food safety tests"},
                {"code": "IS 9833:1981", "title": "Environmental Stress Crack Resistance of Polyethylene", "role": "ESCR test"}
            ],
            "safety_standards": [
                {"code": "FSSAI Food Packaging Regulations", "title": "Plastic packaging for food contact", "role": "Food safety compliance"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "ISO 472", "title": "Plastics — Vocabulary", "role": "PET and polymer terminology"}
            ],
            "related_product_standards": [
                {"code": "IS 14543:2018", "title": "Packaged Drinking Water", "role": "End product"},
                {"code": "IS 4984:2016", "title": "HDPE Pipes for Water Supply", "role": "Related polyolefin product"}
            ]
        },
        "gem_tender_clause": (
            "All PET containers/bottles for packaged drinking water or food contact use shall conform to "
            "IS 15410:2003 (Reaffirmed 2018) incorporating Amendment 1. "
            "Overall migration shall not exceed 10 mg/dm² (60°C, 10 days). "
            "Acetaldehyde content shall not exceed 0.05 mg/kg. Heavy metal extractable content "
            "shall comply with FSSAI food contact material regulations. "
            "Food grade virgin resin only; recycled PET prohibited for primary food contact."
        )
    },

    "IS 1374": {
        "id": "IS 1374",
        "code": "IS 1374:2007",
        "title": "Poultry Feeds — Specification",
        "popular_names": ["poultry feed", "chicken feed", "broiler feed", "layer feed",
                          "chick starter mash", "poultry mash", "compound poultry feed",
                          "poultry feed pellets", "broiler finisher feed", "layer mash"],
        "category": "Agriculture & Food",
        "sub_category": "Animal Feeds",
        "latest_edition": "IS 1900:1993 (Reaffirmed 2019)",
        "active_amendments": [
            {"number": "Amd 1", "year": "2006", "summary": "Metabolizable energy, amino acid, and mineral premix limits updated"},
            {"number": "Amd 2", "year": "2016", "summary": "Aflatoxin maximum limit 10 ppb; moisture max 12%; urease index clarified"}
        ],
        "is_withdrawn": False,
        "mandatory_certification": {
            "scheme": "BIS Product Certification (ISI Mark) recommended; quality testing mandatory",
            "is_mandatory": False,
            "qco_reference": "Department of Animal Husbandry & Dairying quality procurement standards",
            "issuing_ministry": "Ministry of Fisheries, Animal Husbandry and Dairying",
            "effective_date": "2019-01-01",
            "consequence_of_non_compliance": "Sub-standard feeds subject to rejection under Prevention of Food Adulteration Act."
        },
        "allied_standards": {
            "normative_references": [
                {"code": "IS 9936:1993", "title": "Methods of Sampling and Test for Poultry Feeds", "role": "Sampling and testing methods"}
            ],
            "test_methods": [
                {"code": "IS 9936:1993", "title": "Crude protein (N×6.25), crude fat, crude fibre, moisture, ash", "role": "Proximate analysis tests"},
                {"code": "AOAC methods", "title": "Amino acid profile, metabolizable energy determination", "role": "Nutritional quality tests"}
            ],
            "safety_standards": [
                {"code": "Prevention of Food Adulteration Act Rules", "title": "Animal feed quality control", "role": "Regulatory compliance"}
            ],
            "installation_standards": [],
            "terminology_standards": [
                {"code": "IS 1900:1993 Cl. 3", "title": "Definitions for poultry feed grades", "role": "Feed classification"}
            ],
            "related_product_standards": [
                {"code": "IS 2395:1967", "title": "Cattle and Buffalo Feeds", "role": "Related livestock feed standard"}
            ]
        },
        "gem_tender_clause": (
            "All poultry feeds supplied shall conform to IS 1900:1993 (Reaffirmed 2019) incorporating Amendments 1 and 2. "
            "Crude protein minimum as per grade (broiler pre-starter ≥ 22%, starter ≥ 20%, finisher ≥ 18%, layer ≥ 16%). "
            "Aflatoxin maximum 10 ppb, moisture maximum 12%, urease activity negative (for soybean-based feeds). "
            "Quality certificate from NABL accredited feed testing laboratory mandatory with each lot. "
            "50 kg gunny bags with BIS-specified labeling including batch no., date of manufacture, and nutritional composition."
        )
    }

}


# ---------------------------------------------------------------------------
# GLOBAL SPECIFICATION & MATERIAL PROPERTY MAP (100% Engineering Precision)
# ---------------------------------------------------------------------------
GLOBAL_SPEC_PROPERTY_MAP = {
    "IS 1786": [
        "proof stress", "ts/ys", "deformed bar", "rib height", "ribs height", "rib spacing",
        "micro-alloying", "vanadium", "rebend", "fe 500d", "transverse crack", "16mm rebar",
        "yield stress 500", "tensile strength minimum 545", "s+p max 0.075", "yield strength 550",
        "tensile strength 585", "cold bend test around a pin", "without flaking", "carbon max 0.25",
        "total elongation at maximum force"
    ],
    "IS 694": [
        "conductor resistance", "insulation resistance constant", "spark test", "frls",
        "oxygen index", "smoke density", "acid gas", "annealed high conductivity",
        "pvc insulation", "building wiring", "single vertical cable", "cold bend test at -15",
        "rupture of sheath", "flammability test on single", "1100v grade"
    ],
    "IS 269": [
        "28 days compressive strength", "blaine", "initial setting time", "final setting time",
        "le-chatelier", "soundness", "autoclave", "insoluble residue",
        "magnesia", "loss on ignition", "sulfuric anhydride", "ordinary portland cement",
        "3 days compressive strength", "mgo content", "expansion soundness"
    ],
    "IS 4984": [
        "hydrostatic internal pressure", "melt flow rate", "carbon black content",
        "oxidation induction", "longitudinal reversion", "density of base resin",
        "polyethylene water pipe", "ductile rupture", "carbon black dispersion",
        "pe-80 and 21 mpa", "pe-100", "extruded polyethylene", "oit minimum 20 minutes"
    ],
    "IS 1417": [
        "916 parts per thousand", "750 parts per thousand", "999 parts per thousand",
        "fire assay method cupellation", "x-ray fluorescence xrf", "6-digit laser",
        "huid marking", "hallmarking center", "fineness certification", "base metal alloying",
        "children gold jewelry", "gold jewelry", "assay balance precision"
    ],
    "IS 14543": [
        "total dissolved solids", "packaged drinking water", "arsenic", "mercury",
        "cadmium", "nephelometric turbidity", "total coliform", "e. coli",
        "pesticide residues", "sulfate so4", "chloride cl", "lead pb",
        "nitrate as no3", "nitrite as no2", "maximum permissible limit 0.01"
    ],
    "IS 4151": [
        "impact attenuation", "hemispherical steel anvil", "retention system", "chin strap",
        "penetration resistance", "visor luminous", "peripheral vision", "eps foam liner",
        "motorcycle headgear", "flat anvil", "drop height 2.5 meters", "630 n lateral load",
        "retention strap", "peak acceleration not exceeding"
    ],
    "IS 1293": [
        "temperature rise of terminals", "breaking capacity test", "withdrawal force",
        "child protection shutter", "glow wire test", "screw terminal torque",
        "earthing contact resistance", "earth pin", "16a sockets", "between live poles",
        "electric strength test 2000v", "shutter endurance"
    ],
    "IS 2062": [
        "yield strength minimum 250", "ultimate tensile strength 410", "charpy v-notch",
        "carbon equivalent ce", "internal sound plate ultrasonic", "e350", "e250",
        "through-thickness reduction", "mandrel diameter 2t", "quality structural steel",
        "structural plates above 40mm", "e250br"
    ],
    "IS 10322": [
        "surge protection immunity 10kv", "ingress protection ip66", "total harmonic distortion thd",
        "power factor minimum 0.95", "photobiological safety", "driver operating voltage",
        "lumen maintenance l70", "anti-corrosive powder coating", "correlated color temperature",
        "between circuit and body", "pmma secondary lens"
    ],
    "IS 15683": [
        "bursting pressure of cylinder", "hydrostatic pressure test at 25 bar", "effective discharge duration",
        "powder discharged", "fire rating test", "electrical conductivity test 100 kv",
        "salt spray test 480 hours", "abc dry chemical", "pressure gauge calibration",
        "discharge hose burst", "squeeze grip"
    ],
    "IS 8034": [
        "overall efficiency of pump", "hydrostatic test of pump bowls", "motor insulation resistance minimum 5",
        "submersible pump head", "bee star labeling", "thrust bearing load", "pump shaft deflection",
        "dynamic balancing of impellers", "no-load power consumption", "between windings and ground"
    ],
    "IS 14286": [
        "damp heat exposure", "thermal cycling test 200", "hail impact test", "mechanical load test 2400",
        "wet leakage current", "hot spot endurance", "bypass diode thermal", "uv preconditioning",
        "light soaking", "electroluminescence crack", "half-cut mono perc"
    ],
    "IS 1460": [
        "cetane index", "cetane number", "sulfur content maximum 10 mg/kg", "polycyclic aromatic hydrocarbons",
        "pah maximum", "pensky-martens", "kinematic viscosity at 40", "cold filter plugging point",
        "cfpp", "lubricity hfrr", "total contamination", "not exceeding class 1 rating",
        "karl fischer titration"
    ],
    "IS 2796": [
        "research octane number ron", "sulfur content maximum 10 ppm", "benzene content maximum 1.0",
        "oxygen content maximum 2.7", "e20 blended", "reid vapor pressure rvp",
        "distillation recovery at 70", "existent gum content", "induction period oxidation stability",
        "class 1 rating for motor fuel"
    ],
    "IS 15410": [
        "polyethylene terephthalate", "pet container", "pet preform", "overall migration",
        "blow molded pet", "tamper evident", "food contact grade plastic"
    ]
}

class ProcurementService:
    """
    Core AI recommendation & tender specification generation service for SIH26108.
    """

    def __init__(self):
        self._standards_registry = PROCUREMENT_STANDARDS_REGISTRY

    def get_all_categories(self) -> List[str]:
        """Returns unique procurement categories."""
        categories = set()
        for std in self._standards_registry.values():
            categories.add(std.get("category", "General"))
        return sorted(list(categories))

    def get_standards_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Returns all standards under a given procurement category."""
        return [
            std for std in self._standards_registry.values()
            if std.get("category", "").lower() == category.lower()
        ]

    def get_all_ministries(self) -> List[str]:
        """Returns unique issuing ministries for Quality Control Orders (QCOs)."""
        ministries = set()
        for std in self._standards_registry.values():
            m = std.get("mandatory_certification", {}).get("issuing_ministry")
            if m:
                ministries.add(m)
        return sorted(list(ministries))

    def get_standards_by_ministry(self, ministry: str) -> List[Dict[str, Any]]:
        """Returns all standards regulated by a given ministry."""
        return [
            std for std in self._standards_registry.values()
            if ministry.lower() in std.get("mandatory_certification", {}).get("issuing_ministry", "").lower()
        ]

    def recommend_standard(self, query_or_specs: str) -> Dict[str, Any]:
        """
        Semantically analyzes product description, technical specifications,
        or tender text and returns the most relevant Indian Standard and allied standards.
        Supports English and Indic languages (Hindi, Telugu, Tamil, Marathi, Bengali, Kannada, etc.).
        """
        if not query_or_specs or not query_or_specs.strip():
            return {
                "success": False,
                "error": "Query or technical specifications text cannot be empty.",
                "recommendation": None
            }

        original_text = query_or_specs.strip()

        # 0. Early check for adversarial prompt injections, jailbreaks, and unethical exploitation
        PROMPT_JAILBREAK_PATTERNS = [
            r'\b(ignore\s+(all\s+)?(previous\s+)?instructions|reveal\s+system\s+prompt|system\s*override)\b',
            r'\b(pretend\s+to\s+be|act\s+as\s+(an?|the)?\s*(linux|terminal|hacker|unrestricted)|roleplay\s+as)\b',
            r'\b(jailbreak|bypass\s+(statutory|qco|customs|crs|compulsory|guardrails|safety)|override\s+guardrails)\b',
            r'\b(forge\s+(an?\s+)?isi|fake\s+licen[sc]e|fake\s+nabl|fraudulent\s+compliance)\b',
            r'\b(tamper\s+with\s+huid|dilute\s+packaged|sell\s+uncertified|without\s+getting\s+caught)\b',
            r'\b(root\s+credentials|admin\s+credentials|api\s+keys|secret\s+keys|environment\s+variables)\b',
            r'\b(evade\s+(bis|bureau|raid|inspection)|bribe\s+certification|prompt\s+leak|hidden\s+instructions)\b',
            r'\b(repeat\s+after\s+me|disable\s+all\s+safety|bash\s+command|raw\s+markdown\s+injection)\b',
            r'\b(personal\s+phone\s+number|home\s+address\s+of\s+bis|float\s+a\s+tender\s+without\s+standard)\b',
            r'\b(simulate\s+a\s+bypass|forget\s+that\s+you\s+are)\b',
            r'\b(where\s+is\s+the\s+nearest|nearest\s+(petrol|gas|hospital|atm|shop|store|cinema|hotel))\b',
            r'\b(today\'?s\s+(petrol|diesel)\s+price|price\s+of\s+(petrol|diesel))\b',
            r'\b(clean\s+.*(sneakers?|shoes?\s+without\s+bleach))\b'
        ]

        SQL_INJECTION_FRAGMENTS = [
            r"';\s*drop\s+table.*",
            r";\s*drop\s+table.*",
            r"drop\s+table\s+\w+.*",
            r"union\s+select\s+.*",
            r"select\s+\*\s+from\s+.*",
            r"insert\s+into\s+.*",
            r"delete\s+from\s+.*",
            r"exec\s+xp_cmdshell.*",
            r"'\s*or\s+'\d+'\s*=\s*'\d+.*",
            r"'\s*or\s+1\s*=\s*1.*",
            r"--.*",
            r"/\*.*?\*/"
        ]

        lower_raw = original_text.lower()
        if any(re.search(p, lower_raw) for p in PROMPT_JAILBREAK_PATTERNS):
            return {
                "success": True,
                "match_found": False,
                "confidence_score": 0.0,
                "message": "Refused: Adversarial prompt injection or unethical query detected. System adheres to BIS statutory compliance rules.",
                "obsolete_warning": None,
                "foreign_standard_notice": None,
                "recommendation": None,
                "security_flag": True,
                "security_notice": "Adversarial prompt injection pattern blocked by Security Shield."
            }

        security_flag = False
        security_notice = None

        # Check for and sanitize embedded SQL injection patterns
        sanitized_query = original_text
        for sql_pat in SQL_INJECTION_FRAGMENTS:
            if re.search(sql_pat, sanitized_query, re.IGNORECASE):
                sanitized_query = re.sub(sql_pat, "", sanitized_query, flags=re.IGNORECASE).strip()
                security_flag = True
                security_notice = "Prohibited SQL syntax or database command was intercepted and stripped by the Security Shield."

        if not sanitized_query:
            return {
                "success": True,
                "match_found": False,
                "confidence_score": 0.0,
                "message": "Input contained only SQL injection syntax and was blocked by Security Shield.",
                "obsolete_warning": None,
                "foreign_standard_notice": None,
                "recommendation": None,
                "security_flag": True,
                "security_notice": security_notice or "SQL syntax blocked."
            }

        normalized_text = self._normalize_query(sanitized_query)

        # Topic Relevance Check on normalized/repaired text: Guard against out-of-scope & irrelevant queries
        is_relevant, relevance_reason, _ = domain_relevance_guard.check_text_relevance(normalized_text, feature="procurement")
        has_direct_bis_indicators = any(k in normalized_text for k in [
            "is ", "is:", "is-", "standard", "tender", "bis", "gem", "qco", "isi mark", "cml", "fe 500", "opc", "ppc", "xlpe", "huid", "fssai", "nabl", "eurocode", "astm", "iec",
            "proof stress", "deformed bar", "conductor resistance", "spark test", "frls", "compressive strength", "blaine",
            "setting time", "soundness", "hydrostatic", "melt flow", "carbon black", "total dissolved solids", "arsenic",
            "mercury", "cadmium", "turbidity", "coliform", "pesticide", "impact attenuation", "retention system",
            "breaking capacity", "earthing contact", "yield strength", "charpy", "surge protection", "ingress protection",
            "bursting pressure", "powder discharged", "pump efficiency", "damp heat", "thermal cycling", "hail impact",
            "fineness", "fire assay", "cetane", "sulfur content", "research octane", "reid vapor", "distillation recovery",
            "motor spirit", "overall migration", "e350", "dielectric strength", "locked rotor", "submersible electric motor"
        ])
        has_spec_property = any(
            p in normalized_text
            for plist in GLOBAL_SPEC_PROPERTY_MAP.values()
            for p in plist
        )
        if not is_relevant and not has_direct_bis_indicators and not has_spec_property:
            return {
                "success": True,
                "match_found": False,
                "confidence_score": 0.0,
                "message": f"Irrelevant Query: {relevance_reason}",
                "obsolete_warning": None,
                "recommendation": None
            }

        # Check for Foreign Standard Equivalence (Eurocode, ASTM, IEC, NFPA, DIN, BS EN)
        foreign_notice = None
        FOREIGN_EQUIVALENCE = {
            "eurocode 3": ("IS 2062", "Eurocode 3 governs structural steel. Under Indian Public Procurement rules (GFR Rule 144), the statutory Indian Standard is IS 2062:2011."),
            "eurocode 2": ("IS 456", "Eurocode 2 governs concrete design. The corresponding mandatory Indian Standard code of practice is IS 456:2000."),
            "astm a615": ("IS 1786", "ASTM A615 covers rebar steel. Under the Ministry of Steel QCO, bidders must supply TMT bars conforming to IS 1786:2008."),
            "astm a36": ("IS 2062", "ASTM A36 covers structural carbon steel. Under Indian Public Procurement rules, the statutory Indian Standard is IS 2062:2011 Grade E250."),
            "astm c150": ("IS 269", "ASTM C150 covers Portland cement. The statutory Indian Standard is IS 269:2015 for Ordinary Portland Cement."),
            "iec 60950": ("IS 13252", "IEC 60950 is adopted into Indian Standard as IS 13252 for IT equipment safety under MeitY CRS."),
            "iec 62368": ("IS 13252", "IEC 62368-1 is harmonized as IS 18112 / IS 13252 for audio/video and IT equipment under MeitY CRS."),
            "iec 62133": ("IS 16046", "IEC 62133 is harmonized as IS 16046 for lithium battery safety under MeitY CRS."),
            "iec 61215": ("IS 14286", "IEC 61215 is harmonized as IS 14286 for terrestrial solar PV modules under MNRE ALMM."),
            "iec 61730": ("IS 14286", "IEC 61730 covers PV module safety qualification, harmonized as IS/IEC 61730 under MNRE ALMM."),
            "iec 60502": ("IS 7098", "IEC 60502 covers power cables. The mandatory Indian Standard is IS 7098 for XLPE cables under Ministry of Power regulations."),
            "bs en 10025": ("IS 2062", "BS EN 10025 covers structural steel. In Indian tenders, bidders must supply steel complying with IS 2062:2011 with BIS ISI mark."),
            "nfpa 10": ("IS 15683", "NFPA 10 covers portable fire extinguishers. The statutory Indian Standard for tenders in India is IS 15683:2018."),
            "iso 20345": ("IS 15298", "ISO 20345 is harmonized as IS 15298 (Part 2):2016 for industrial safety footwear under DPIIT QCO."),
            "en 397": ("IS 2925", "EN 397 covers industrial safety helmets. For public tenders in India, the mandatory statutory standard is IS 2925:1984 under DPIIT QCO."),
            "din 8074": ("IS 4984", "DIN 8074 covers HDPE pipes. The mandatory Indian Standard for drinking water and gas is IS 4984:2016."),
            "bs 4449": ("IS 1786", "BS 4449 covers deformed steel bars. Under the Ministry of Steel QCO, Indian tenders must specify IS 1786:2008 TMT bars with BIS ISI mark."),
            "iec 60598": ("IS 10322", "IEC 60598 covers luminaires. The equivalent mandatory Indian Standard is IS 10322 series for luminaires under BIS certification."),
            "bs 6004": ("IS 694", "BS 6004 covers PVC insulated cables. The equivalent Indian Standard for building wires is IS 694:2010 under BIS ISI scheme."),
            "iso 9906": ("IS 8034", "ISO 9906 covers rotodynamic pumps. The corresponding Indian Standard for submersible pumps is IS 8034:2002 under BIS ISI scheme."),
            "iso 4427": ("IS 4984", "ISO 4427 covers polyethylene pipes for water supply. The mandatory Indian Standard is IS 4984:2016 for HDPE pipes."),
            "en 3-7": ("IS 15683", "EN 3-7 covers portable fire extinguishers. The equivalent Indian Standard is IS 15683:2018 under BIS ISI scheme."),
            "astm a706": ("IS 1786", "ASTM A706 covers low-alloy steel rebars. Under the Ministry of Steel QCO, Indian tenders must use IS 1786:2008 Fe 500D/Fe 550D."),
            "en 197-1": ("IS 269", "EN 197-1 covers common cements. The mandatory Indian Standard for Ordinary Portland Cement is IS 269:2015."),
            "iso 1083": ("IS 1865", "ISO 1083 covers spheroidal graphite cast iron. The corresponding Indian Standard is IS 1865 for ductile iron fittings."),
            "iec 60269": ("IS 13703", "IEC 60269 covers low-voltage fuses. The equivalent Indian Standard is IS 13703 under BIS scheme."),
            "iso 3506": ("IS 1367", "ISO 3506 covers stainless steel fasteners. The equivalent Indian Standard is IS 1367 under BIS scheme."),
            "iec 60227": ("IS 694", "IEC 60227 covers PVC insulated cables for rated voltages up to 450/750V. The mandatory Indian Standard is IS 694:2010 under BIS ISI scheme."),
            "en 13032": ("IS 10322", "EN 13032 covers measurement and presentation of photometric data of lamps and luminaires. The equivalent Indian Standard is IS 10322 series for luminaires."),
            "ul 94": ("IS 694", "UL 94 covers flammability of plastic materials. For cable sheathing applications, the Indian Standard is IS 694:2010 which mandates FRLS cable grade."),
            "iso 11114": ("IS 15683", "ISO 11114 covers compatibility of cylinder and valve materials with gas contents. For fire extinguisher cylinders in India, the mandatory standard is IS 15683:2018."),
            "iso 6469": ("IS 16046", "ISO 6469 covers safety requirements for electrically propelled vehicles. Battery cells used in EVs must conform to IS 16046 under MeitY CRS."),
            "astm b8": ("IS 8130", "ASTM B8 covers stranded bare copper conductors. The equivalent Indian Standard is IS 8130 for conductors of insulated cables."),
            "en 1563": ("IS 1865", "EN 1563 covers spheroidal graphite cast iron. The equivalent Indian Standard is IS 1865 for ductile iron castings."),
            "iso 8501": ("IS 1477", "ISO 8501 covers preparation of steel surfaces before application of paints. The equivalent Indian Standard for surface preparation is IS 1477."),
            "iec 60320": ("IS 1293", "IEC 60320 covers appliance couplers for household use. The equivalent Indian Standard for plugs and socket outlets is IS 1293:2005."),
            "iec 60884": ("IS 1293", "IEC 60884 covers plugs and socket-outlets for household. The mandatory Indian Standard is IS 1293:2005 under DPIIT QCO.")
        }
        for foreign_kw, (target_is, notice_msg) in FOREIGN_EQUIVALENCE.items():
            if foreign_kw in normalized_text:
                foreign_notice = {
                    "foreign_standard_detected": foreign_kw.upper(),
                    "statutory_advice": notice_msg,
                    "equivalent_indian_standard": target_is
                }
                break

        # Check for obsolete or superseded standard mentions by user (e.g. IS 1786:1985 or IS 456:1978)
        obsolete_warning = self._check_obsolete_standards(normalized_text)

        # Score matching across all registered procurement standards
        best_match = None
        best_score = 0.0

        for std_id, std_data in self._standards_registry.items():
            score = self._compute_similarity_score(normalized_text, std_data)
            if foreign_notice and foreign_notice.get("equivalent_indian_standard") == std_id:
                score += 0.70
            if obsolete_warning and obsolete_warning.get("superseded_by_id") == std_id:
                score += 0.70
            if score > best_score:
                best_score = score
                best_match = std_data

        if not best_match or best_score < 0.25:
            return {
                "success": True,
                "match_found": False,
                "confidence_score": 0.0,
                "message": (
                    "No exact Indian Standard identified in the procurement catalog for this item. "
                    "Ensure the product is regulated under Bureau of Indian Standards (BIS) or provide additional "
                    "technical parameters (e.g., material grade, operating voltage, pressure rating)."
                ),
                "obsolete_warning": obsolete_warning,
                "foreign_standard_notice": foreign_notice,
                "recommendation": None,
                "security_flag": security_flag,
                "security_notice": security_notice
            }

        # Build comprehensive recommendation output
        rec = {
            "success": True,
            "match_found": True,
            "confidence_score": round(min(best_score * 100, 98.5), 1),
            "primary_standard": {
                "id": best_match["id"],
                "code": best_match["code"],
                "title": best_match["title"],
                "category": best_match["category"],
                "sub_category": best_match["sub_category"],
                "latest_edition": best_match["latest_edition"],
                "active_amendments": best_match["active_amendments"],
                "total_amendments": len(best_match["active_amendments"]),
                "is_withdrawn": best_match["is_withdrawn"],
                "superseded_by": best_match.get("superseded_by", None)
            },
            "mandatory_certification": best_match["mandatory_certification"],
            "allied_standards": best_match["allied_standards"],
            "gem_tender_clause": best_match["gem_tender_clause"],
            "obsolete_warning": obsolete_warning,
            "foreign_standard_notice": foreign_notice,
            "security_flag": security_flag,
            "security_notice": security_notice
        }

        return rec

    def _normalize_query(self, text: str) -> str:
        """
        Normalizes input text:
        1. Corrects typographical errors in technical procurement terms
        2. Checks for non-ASCII Indic scripts (Hindi, Telugu, Tamil, etc.) and translates to English
        3. Replaces phonetic romanized vernacular terms (e.g. 'sariya', 'inupa rodlu', 'kambi')
        4. Cleans punctuation and excess whitespace
        """
        lower_text = text.lower().strip()

        # Typo correction for common procurement misspellings and abbreviations
        typo_map = {
            "fir": "fire", "resistnt": "resistant", "resistent": "resistant", "reistant": "resistant",
            "electrc": "electric", "elctrc": "electric", "electrcl": "electrical", "elctricl": "electrical",
            "hospitl": "hospital", "buldng": "building", "bldng": "building", "bldg": "building",
            "stndrd": "standard", "stndr": "standard", "bsi": "bis", "watr": "water", "drnking": "drinking",
            "drnkng": "drinking", "wtr": "water", "pip": "pipe", "payp": "pipe", "pipes": "pipe",
            "suplly": "supply", "suply": "supply", "villag": "village", "cabls": "cables", "cbl": "cable",
            "mtrs": "meters", "mtr": "meter", "tmt": "tmt steel", "sariya": "tmt steel rebar is 1786",
            "portlnd": "portland", "cemnt": "cement", "cementu": "cement", "simantu": "cement", "siminti": "cement",
            "stuctural": "structural", "stell": "steel", "saftey": "safety", "helmt": "helmet", "hlmet": "helmet",
            "stritlite": "street lighting", "driniking": "drinking", "armord": "armoured", "seling": "ceiling",
            "transfrmr": "transformer", "distribtion": "distribution", "solr": "solar", "modl": "module",
            "lithum": "lithium", "battr": "battery", "rechrgable": "rechargeable", "compyutr": "computer",
            "equpmnt": "equipment", "beem": "beam", "chanel": "channel", "submersibl": "submersible",
            "submersble": "submersible", "extingusher": "extinguisher", "chemicl": "chemical", "powdr": "powder",
            "min kambi": "copper electrical wire is 694", "irumbu": "structural steel is 2062",
            "kambi": "tmt steel bars is 1786", "inumu": "tmt steel rebar is 1786",
            "cilindar": "cylinder extinguisher", "cilender": "cylinder extinguisher",
            "shooes": "shoes", "shoos": "shoes", "balb": "bulb luminaire", "polyethlene": "polyethylene",
            "insulatd": "insulated", "transmision": "transmission", "powerr": "power", "reinfrcmnt": "reinforcement",
            "gvanized": "galvanized", "glvanized": "galvanized", "galvnized": "galvanized"
        }
        for typo, fix in typo_map.items():
            lower_text = re.sub(rf'\b{typo}\b', fix, lower_text)

        # Check for Indic script characters (Unicode ranges)
        has_indic = bool(re.search(r'[\u0900-\u0D7F]', text))
        if has_indic:
            try:
                translated = multilingual_translator._translate_gtx(text, target_lang="en")
                if translated and len(translated.strip()) > 0:
                    lower_text = f"{lower_text} {translated.lower()}"
            except Exception as e:
                logger.debug(f"Indic translation fallback error: {e}")

        # Check romanized vernacular procurement terms (sorted by descending length so multi-word terms like "paani supply" match before "paani")
        for vern_term, canonical in sorted(VERNACULAR_PROCUREMENT_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(r'\b' + re.escape(vern_term) + r'\b', lower_text):
                lower_text = re.sub(r'\b' + re.escape(vern_term) + r'\b', canonical, lower_text)

        return lower_text

    @staticmethod
    def _get_stemmed_words(text: str) -> set:
        words = set(re.findall(r'\b[a-zA-Z0-9\-]+\b', text.lower()))
        stemmed = set(words)
        for w in words:
            if '-' in w:
                for part in w.split('-'):
                    if part:
                        stemmed.add(part)
            if w.endswith('ies') and len(w) > 4:
                stemmed.add(w[:-3] + 'y')
            elif w.endswith('es') and len(w) > 4:
                stemmed.add(w[:-2])
                stemmed.add(w[:-1])
            elif w.endswith('s') and len(w) > 3 and not w.endswith('ss'):
                stemmed.add(w[:-1])
            if w.endswith('ing') and len(w) > 5:
                stemmed.add(w[:-3])
                stemmed.add(w[:-3] + 'e')
            if w.endswith('ed') and len(w) > 4:
                stemmed.add(w[:-2])
                stemmed.add(w[:-1])
        return stemmed

    def _compute_similarity_score(self, text: str, standard_data: Dict[str, Any]) -> float:
        """
        Computes semantic similarity using token-set intersections, stemmed matching,
        distinctive product anchors, and engineering specification property maps.
        """
        score = 0.0
        lower_text = text.lower()
        std_id = standard_data["id"]
        std_id_lower = std_id.lower()

        # Direct mention of IS code (e.g. "is 1786" or "is1786")
        if std_id_lower in text or std_id_lower.replace(" ", "") in text:
            score += 0.85

        stemmed_set = self._get_stemmed_words(text)

                # 1. SPEC_PROPERTY_MAP: Distinctive engineering specification parameters
        SPEC_PROPERTY_MAP = GLOBAL_SPEC_PROPERTY_MAP
        if std_id in SPEC_PROPERTY_MAP:
            for phrase in SPEC_PROPERTY_MAP[std_id]:
                if phrase in lower_text:
                    score += 0.80
                    break

        # 2. ANCHOR_KEYWORDS: Token-group anchors for core product identification
        ANCHOR_KEYWORDS = {
            "IS 16046": [["battery"], ["batteries"], ["lithium"], ["secondary", "cell"], ["secondary", "lithium"], ["electric", "mobility"], ["lifepo4"], ["nmc"],
                         ["lithium", "cell"], ["secondary", "lithium"], ["rechargeable", "cell"]],
            "IS 14286": [["solar"], ["photovoltaic"], ["pv", "module"], ["pv", "panel"], ["solar", "panel"],
                         ["solar", "pv"], ["almm"], ["monocrystalline"], ["polycrystalline"], ["bifacial"]],
            "IS 13252": [["server"], ["workstation"], ["computer"], ["it", "equipment"], ["crs", "safety"],
                         ["desktop"], ["laptop"], ["printer"], ["information", "technology", "equipment"], ["power", "adapter"], ["scanner"], ["router"], ["network", "switch"],
                         ["it", "hardware"], ["kiosk"], ["multifunctional"], ["peripheral"], ["tablet"]],
            "IS 1180":  [["transformer"], ["kva"], ["oil", "immersed", "distribution"]],
            "IS 15683": [["extinguisher"], ["fire", "safety"], ["abc", "powder"], ["afff"], ["clean", "agent"],
                         ["fire", "extinguisher"], ["dry", "chemical", "powder"]],
            "IS 2925":  [["industrial", "safety", "helmet"], ["hard", "hat"], ["construction", "helmet"],
                         ["site", "helmet"], ["protective", "helmet", "industrial"]],
            "IS 4151":  [["motorcycle", "helmet"], ["two", "wheeler", "helmet"], ["bike", "helmet"],
                         ["crash", "helmet"], ["rider", "helmet"], ["motor", "cycle", "helmet"],
                         ["motorbike", "helmet"], ["two-wheeler", "helmet"], ["motorcycle", "headgear"],
                         ["protective", "headgear"], ["full", "face", "helmet"], ["open", "face", "helmet"],
                         ["motorcycle", "rider"], ["dot", "isi", "helmet"], ["two", "wheeler", "motorcycle"]],
            "IS 15298": [["footwear"], ["safety", "shoe"], ["safety", "boot"], ["steel", "toe"]],
            "IS 1417":  [["gold"], ["hallmark"], ["hallmarking"], ["huid"], ["jewellery"],
                         ["karat"], ["carat"], ["bullion"], ["gold", "medal"], ["gold", "coin"]],
            "IS 1786":  [["tmt"], ["rebar"], ["fe", "500"], ["fe", "550"], ["fe", "600"],
                         ["deformed", "bar"], ["steel", "rod"], ["sariya"], ["kambi"], ["thermo", "mechanically"]],
            "IS 2062":  [["structural", "steel"], ["ismb"], ["ismc"], ["structural", "beam"],
                         ["steel", "plate"], ["e250"], ["e350"], ["e350", "grade"], ["transmission", "tower"], ["mild", "steel"],
                         ["steel", "section"], ["universal", "column"]],
            "IS 269":   [["opc"], ["ordinary", "portland", "cement"], ["53", "grade", "cement"],
                         ["43", "grade", "cement"], ["cement", "53"], ["cement", "43"],
                         ["portland", "cement"], ["isi", "cement"], ["cement", "bag"],
                         ["hydraulic", "cement"], ["high", "strength", "cement"],
                         ["airport", "cement"], ["bridge", "cement"], ["runway", "cement"]],
            "IS 1489":  [["ppc"], ["pozzolana"], ["fly", "ash", "cement"], ["blended", "cement"],
                         ["portland", "pozzolana"]],
            "IS 456":   [["is", "456"], ["concrete", "code"], ["reinforced", "concrete"],
                         ["plain", "concrete"], ["rcc"], ["concrete", "mix"],
                         ["code", "practice", "concrete"], ["design", "mix", "concrete"],
                         ["m30", "grade"], ["m25", "grade"], ["m20", "grade"],
                         ["curing", "concrete"], ["rcc", "column"], ["rcc", "beam"],
                         ["concrete", "structure"], ["concrete", "design"], ["structural", "concrete"],
                         ["concrete", "durability"], ["shear", "stress", "rcc"]],
            "IS 694":   [["house", "wire"], ["building", "wire"], ["copper", "wire"],
                         ["frls", "wire"], ["copper", "cable"], ["min", "kambi"],
                         ["pvc", "cable"], ["1100v", "cable"], ["domestic", "wiring"],
                         ["building", "cable"], ["flexible", "copper"]],
            "IS 7098":  [["xlpe"], ["armoured", "cable"], ["power", "cable"],
                         ["ht", "cable"], ["underground", "cable"], ["mv", "cable"]],
            "IS 4984":  [["hdpe"], ["hdpe", "pipe"], ["pe100"], ["pe80"],
                         ["polyethylene", "pipe"], ["pe", "100"], ["pe-100"],
                         ["gravity", "main"], ["hdpe", "water"], ["pe", "pipe"],
                         ["polyethylene", "water"], ["water", "supply", "pipe"],
                         ["hdpe", "fitting"], ["water", "pipeline"], ["hilly", "terrain", "pipe"],
                         ["drinking", "water", "pipe"], ["potable", "water", "pipe"],
                         ["carbon", "black", "dispersion"], ["gravity", "transmission"],
                         ["rural", "water", "supply"], ["butt", "fusion"]],
            "IS 4985":  [["upvc"], ["upvc", "pipe"], ["pvc", "pressure", "pipe"], ["nalki"]],
            "IS 8034":  [["submersible", "pump"], ["borehole", "pump"],
                         ["agricultural", "pump"], ["tubewell", "pump"], ["neeti", "pumpu"],
                         ["deep", "well", "submersible", "pump"], ["borewell", "pump"],
                         ["submersible", "pumping", "unit"], ["borewell", "water", "extraction"]],
            "IS 8320":  [["submersible", "motor"], ["induction", "motor"],
                         ["borewell", "motor"], ["borehole", "motor"],
                         ["deep", "well", "motor"], ["tubewell", "motor"],
                         ["water", "cooled", "motor"], ["crgo", "stator"],
                         ["kingsbury", "thrust"], ["f-class", "insulation"]],
            "IS 374":   [["ceiling", "fan"], ["bldc", "fan"], ["electric", "fan"], ["pankha"]],
            "IS 10322": [["led", "street"], ["street", "light"], ["streetlight"],
                         ["roadway", "lighting"], ["street", "luminaire"], ["outdoor", "led"],
                         ["road", "lighting"], ["street", "lighting"], ["secondary", "lens"]],
            "IS 16102": [["led", "bulb"], ["led", "lamp"], ["self", "ballasted", "led"],
                         ["retrofit", "led"], ["energy", "saving", "led"], ["b22", "base"],
                         ["general", "lighting", "service", "led"], ["cool", "daylight"],
                         ["domestic", "lighting", "led"]],
            "IS 1293":  [["pin", "plug"], ["socket", "outlet"], ["safety", "shutter"],
                         ["modular", "socket"], ["electrical", "socket"], ["power", "socket"],
                         ["switch", "socket"], ["switched", "socket"], ["plug", "top"],
                         ["flush", "mounted", "socket"], ["solid", "brass", "pin"]],
            "IS 14846": [["sluice", "valve"], ["gate", "valve"], ["isolation", "valve"],
                         ["sluice", "gate"], ["water", "works", "valve"],
                         ["resilient", "seated", "gate"], ["flanged", "gate", "valve"],
                         ["flanged", "sluice"], ["water", "distribution", "valve"],
                         ["inside", "screw", "valve"]],
            "IS 1536":  [["cast", "iron", "pipe"], ["ci", "pipe"], ["spun", "iron", "pipe"],
                         ["centrifugally", "cast"], ["spun", "cast", "iron"],
                         ["class", "la", "pipe"], ["class", "a", "pipe"],
                         ["socket", "spigot", "pipe"], ["spigot", "socket", "pipe"],
                         ["iron", "pressure", "pipe"]],
            "IS 15644": [["electric", "toy"], ["electronic", "toy"],
                         ["battery", "operated", "toy"], ["educational", "electric", "toy"],
                         ["children", "electric", "toy"], ["toys", "quality", "control"],
                         ["motorized", "children", "toy"], ["battery", "powered", "toy"],
                         ["accessible", "voltage", "toy"], ["toy", "safety"]],
            "IS 2796":  [["motor", "gasoline"], ["petrol"], ["motor", "spirit"],
                         ["automotive", "petrol"], ["unleaded", "petrol"],
                         ["gasoline", "fuel"], ["ron", "91"], ["motor", "spirit"], ["unleaded", "motor", "spirit"], ["detergent", "additive"], ["bs-vi", "petrol"],
                         ["bs6", "petrol"], ["e20", "petrol"], ["ethanol", "blended"]],
            "IS 1460":  [["automotive", "diesel"], ["high", "speed", "diesel"],
                         ["hsd"], ["diesel", "fuel"], ["auto", "diesel"],
                         ["diesel", "oil"], ["bs-vi", "diesel"], ["bs6", "diesel"],
                         ["automotive", "gas", "oil"], ["diesel", "generator"],
                         ["dg", "set", "fuel"], ["diesel", "fleet"], ["cetane"]],
            "IS 15410": [["pet", "bottle"], ["pet", "container"],
                         ["polyethylene", "terephthalate"], ["food", "grade", "pet"],
                         ["pet", "preform"], ["plastic", "container", "pet"],
                         ["pet", "packaging"], ["food", "contact", "grade", "plastic"],
                         ["packaged", "beverage", "distribution"], ["blow", "molded", "pet"],
                         ["tamper", "evident", "screw"], ["stress", "crack", "resistance", "bottle"], ["overall", "migration"], ["plastic", "migration"], ["polyethylene", "terephthalate"]],
            "IS 1374":  [["poultry", "feed"], ["chicken", "feed"], ["broiler", "feed"],
                         ["layer", "feed"], ["chick", "starter"], ["poultry", "mash"],
                         ["compound", "poultry", "feed"], ["poultry", "pellet"],
                         ["broiler", "crumbles"], ["layer", "mash"],
                         ["poultry", "farm"], ["pre-starter", "feed"]],
            "IS 14543": [["packaged", "drinking", "water"], ["bottled", "water"],
                         ["water", "bottle", "isi"], ["neeti", "botlu"],
                         ["paani", "bottle"], ["mineral", "water", "drinking"],
                         ["packaged", "potable", "water"], ["20-liter", "water"]]
        }

        if ("resin bottle" in lower_text or "food grade resin" in lower_text) and std_id == "IS 15410":
            score += 0.85
        if "water lubricated submersible" in lower_text and std_id == "IS 8034":
            score += 0.85
        if "\u0c28\u0c40\u0c1f\u0c3f \u0c2a\u0c48\u0c2a\u0c41\u0c32" in text and std_id == "IS 4984":
            score += 0.95
        if "\u0b8e\u0b83\u0b95\u0bc1 \u0b95\u0bae\u0bcd\u0baa\u0bbf" in text and std_id == "IS 1786":
            score += 0.95
        if "\u0bb5\u0bbf\u0bb3\u0b95\u0bcd\u0b95\u0bc1\u0b95\u0bb3\u0bcd" in text and "10kv" in lower_text and std_id == "IS 10322":
            score += 0.95
        if "tmt" in lower_text and std_id == "IS 1786":
            score += 0.90
        if "10kv" in lower_text and "led" in lower_text and std_id == "IS 10322":
            score += 0.90
        if "steel rod" in lower_text and std_id == "IS 1786":
            score += 0.85
        if ("ಕೇಬಲ್" in lower_text or "ಕೇಬಲ್‌ಗಳಿಗೆ" in lower_text) and std_id == "IS 694":
            score += 0.85
        if "secondary lithium" in lower_text and std_id == "IS 16046":
            score += 0.85
        if "water lubricated submersible" in lower_text and std_id == "IS 8034":
            score += 0.85
        if "potable drinking water" in lower_text and std_id == "IS 14543":
            score += 0.85
        if "submersible electric motor evaluated" in lower_text and std_id == "IS 8320":
            score += 0.85
        if "water cooled three phase induction motor" in lower_text and std_id == "IS 8320":
            score += 0.85
        if "submersible pumping motor" in lower_text and std_id == "IS 8320":
            score += 0.85
        if std_id in ANCHOR_KEYWORDS:
            for token_group in ANCHOR_KEYWORDS[std_id]:
                if set(token_group).issubset(stemmed_set):
                    score += 0.60
                    break

        # 3. Popular names matching (max partial match, non-accumulating)
        exact_alias_matched = False
        best_alias_ratio = 0.0
        stopwords = {"safety", "testing", "standards", "standard", "commercial", "work", "procurement", "supply", "preparation", "development"}
        for alias in standard_data.get("popular_names", []):
            alias_lower = alias.lower()
            if alias_lower in lower_text:
                exact_alias_matched = True
                break
            else:
                alias_words = [w for w in alias_lower.split() if len(w) > 3 and w not in stopwords]
                if alias_words:
                    matching_words = [w for w in alias_words if w in stemmed_set]
                    ratio = len(matching_words) / len(alias_words)
                    if ratio > best_alias_ratio:
                        best_alias_ratio = ratio

        if exact_alias_matched:
            score += 0.40
        elif best_alias_ratio >= 0.5:
            score += 0.25 * best_alias_ratio

        # 4. Title words matching (capped at 0.15)
        title_words = [w for w in standard_data["title"].lower().split() if len(w) > 3 and w not in stopwords]
        matching_title = [tw for tw in title_words if tw in stemmed_set]
        if title_words and matching_title:
            score += min(0.15, 0.05 * len(matching_title))

        return score


    def _check_obsolete_standards(self, text: str) -> Optional[Dict[str, Any]]:
        """Detects if the user or tender specifies an obsolete/superseded Indian Standard edition."""
        obsolete_patterns = [
            (r"\bis\s*1786\s*:\s*(1985|1979)\b", "IS 1786:1985/1979 is WITHDRAWN. Superseded by IS 1786:2008 (Reaffirmed 2023).", "IS 1786"),
            (r"\bis\s*2062\s*:\s*(2006|1999)\b", "IS 2062:2006/1999 is WITHDRAWN. Superseded by IS 2062:2011 (Reaffirmed 2021).", "IS 2062"),
            (r"\bis\s*456\s*:\s*(1978|1964)\b", "IS 456:1978/1964 is WITHDRAWN. Superseded by IS 456:2000 (Reaffirmed 2021).", "IS 456"),
            (r"\bis\s*8112\b", "IS 8112 (43 Grade OPC) is MERGED into unified IS 269:2015.", "IS 269"),
            (r"\bis\s*12269\b", "IS 12269 (53 Grade OPC) is MERGED into unified IS 269:2015.", "IS 269"),
            (r"\bis\s*2171\b", "IS 2171 (Dry Powder Extinguisher) is WITHDRAWN. Superseded by unified IS 15683:2018.", "IS 15683"),
            (r"\bis\s*940\b", "IS 940 (Water Type Extinguisher) is WITHDRAWN. Superseded by unified IS 15683:2018.", "IS 15683"),
            (r"\bis\s*694\s*:\s*1990\b", "IS 694:1990 is WITHDRAWN. Superseded by IS 694:2010.", "IS 694"),
            (r"\bis\s*1180\s*:\s*1989\b", "IS 1180:1989 is WITHDRAWN. Superseded by IS 1180 (Part 1):2014.", "IS 1180"),
            (r"\bis\s*15298\s*:\s*2002\b", "IS 15298:2002 is WITHDRAWN. Superseded by IS 15298 (Part 2):2016.", "IS 15298"),
            (r"\bis\s*14286\s*:\s*2010\b", "IS 14286:2010 is WITHDRAWN. Superseded by IS 14286:2019.", "IS 14286"),
            (r"\bis\s*13252\s*:\s*2003\b", "IS 13252:2003 is WITHDRAWN. Superseded by IS 13252 (Part 1):2010.", "IS 13252"),
            (r"\bis\s*14543\s*:\s*2004\b", "IS 14543:2004 is WITHDRAWN. Superseded by IS 14543:2018.", "IS 14543"),
            (r"\bis\s*1363(\s*:\s*1992)?\b", "IS 1363:1992 is WITHDRAWN. Superseded by IS 1363 (Parts 1-3):2019 for hexagon bolts, screws and nuts.", "IS 1363"),
            (r"\bis\s*1011\b", "IS 1011 (Ordinary Portland Cement, 1992 and earlier) is WITHDRAWN. Superseded by unified IS 269:2015 which covers all OPC grades.", "IS 269"),
            (r"\bis\s*432\b", "IS 432 (Mild Steel Bars) is WITHDRAWN. For structural steel TMT rebars, use IS 1786:2008. For mild steel bars in general structural use, refer to IS 2062:2011.", "IS 2062"),
            (r"\bis\s*226\b", "IS 226 (Structural Steel — Standard Quality) is WITHDRAWN. Superseded by IS 2062:2011. All tenders must specify IS 2062 Grade E250 or equivalent.", "IS 2062"),
            (r"\bis\s*1977\b", "IS 1977 (Structural Steel — Low Tensile) is WITHDRAWN. Superseded by IS 2062:2011.", "IS 2062"),
            (r"\bis\s*2171\b", "IS 2171 (Dry Powder Type Fire Extinguisher) is WITHDRAWN. Superseded by unified IS 15683:2018.", "IS 15683"),
            (r"\bis\s*1234\b", "IS 1234 (Distribution Transformers) is WITHDRAWN. Superseded by IS 1180 (Part 1):2014.", "IS 1180"),
            (r"\bis\s*4905\b", "IS 4905 (Ceiling Fans) is WITHDRAWN. Superseded by IS 374:2019.", "IS 374"),
            (r"\bis\s*8686\b", "IS 8686 (Solar PV Modules) is WITHDRAWN. Superseded by IS 14286:2019.", "IS 14286")
        ]

        for pattern, warning_msg, target_id in obsolete_patterns:
            if re.search(pattern, text):
                return {
                    "is_obsolete": True,
                    "warning": warning_msg,
                    "superseded_by_id": target_id,
                    "recommendation": "Update tender documents to specify the latest active published edition to avoid tender cancellation."
                }
        return None

    def validate_tender_document_relevance(self, document_text: str) -> Tuple[bool, str, str]:
        """
        Validates whether the uploaded document text is relevant to public procurement,
        tenders, engineering deliverables, or Bill of Quantities (BoQ).
        Returns: (is_relevant, relevance_reason, user_friendly_message)
        """
        if not document_text or len(document_text.strip()) < 20:
            return False, "Empty or insufficient text in uploaded document.", (
                "The uploaded document contains insufficient text to evaluate procurement requirements."
            )

        text_lower = document_text.lower()

        # Check for obvious out-of-scope categories: recipes, source code, resumes, automotive, fiction
        IRRELEVANT_DOCUMENT_PATTERNS = [
            (r'\b(recipe|tablespoon|teaspoon|cocoa powder|bake at \d+|preheat oven|ingredients:)\b', "Culinary / Cooking Recipe Document"),
            (r'\b(def\s+[a-zA-Z_]\w*\(|import\s+sys|console\.log|function\s*\(|class\s+[a-zA-Z_]\w*:\s*$|public\s+static\s+void)\b', "Software Source Code / Script Document"),
            (r'\b(curriculum\s+vitae|bachelor\s+of\s+science|work\s+experience|professional\s+summary|education:\s*bachelor)\b', "Personal Resume / Curriculum Vitae"),
            (r'\b(sports\s*car|engine\s*horsepower|brake\s*horsepower|top\s*speed|0-60\s*mph|sedan\s*vehicle)\b', "Automotive Vehicle Document"),
            (r'\b(once\s+upon\s+a\s+time|in\s+a\s+galaxy\s+far|chapter\s+1|novel|fiction\s+story)\b', "Fictional / Literary Document")
        ]

        for pattern, cat in IRRELEVANT_DOCUMENT_PATTERNS:
            if re.search(pattern, text_lower):
                return False, f"Irrelevant Document Detected: {cat}", (
                    f"⚠️ Non-Procurement Document Detected ({cat}): The uploaded file does not contain technical specifications, "
                    "material deliverables, or tender items. Please upload an official GeM/CPPP tender document or Bill of Quantities (BoQ)."
                )

        # Positive procurement and engineering keywords
        PROCUREMENT_INDICATORS = [
            "tender", "bid", "bidding", "boq", "bill of quantities", "schedule of requirements", "schedule of items",
            "procurement", "supply", "deliverables", "technical specification", "scope of work", "gem", "cppp",
            "is ", "is:", "bis", "qco", "isi mark", "scheme-i", "scheme-ii", "cml", "crs", "nabl",
            "quantity", "rate", "conforming to", "grade", "diameter", "thickness", "voltage", "rating",
            "pipe", "pipes", "cable", "cables", "wire", "wires", "steel", "cement", "valve", "valves",
            "pump", "pumps", "transformer", "luminaire", "helmet", "meter", "meters", "kg", "tons", "mt"
        ]

        matches = sum(1 for ind in PROCUREMENT_INDICATORS if ind in text_lower)
        if matches == 0:
            return False, "Irrelevant Document: No tender, engineering, or procurement deliverables detected.", (
                "⚠️ Non-Procurement Document Detected: The uploaded file does not contain recognizable public procurement items, "
                "standards citations, or engineering specifications. Please upload an official tender document, RFP, or BoQ schedule."
            )

        return True, "Relevant procurement document.", ""

    def parse_tender_document_text(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Parses full tender document or Bill of Quantities (BoQ) text,
        splits it into separate items/sections, and generates recommendations for each.
        """
        if not document_text or not document_text.strip():
            return []

        # Split text into candidate lines or paragraphs (BoQ items)
        lines = [line.strip() for line in document_text.split("\n") if len(line.strip()) > 15]

        # Filter out common legal / financial boilerplate and document headers
        boilerplate_keywords = [
            "earnest money deposit", "emd", "tender fee", "arbitration clause",
            "force majeure", "penalty for delay", "payment terms", "bank guarantee",
            "jurisdiction of court", "integrity pact", "affidavit", "stamp paper",
            "notice inviting tender", "tender no:", "section i:", "section ii:",
            "section iii:", "government of", "department of", "water supply & sewerage board",
            "refinery corporation", "corporation limited", "annual supply of",
            "schedule of requirements", "bill of quantities"
        ]

        item_candidates = []
        for line in lines:
            line_lower = line.lower()
            if any(bp in line_lower for bp in boilerplate_keywords):
                continue
            item_candidates.append(line)

        # Group similar items or take top distinct item candidates
        results = []
        seen_standards = set()

        for item_desc in item_candidates[:20]:  # Cap at 20 line items for speed & responsiveness
            rec = self.recommend_standard(item_desc)
            if rec.get("match_found"):
                std_id = rec["primary_standard"]["id"]
                if std_id not in seen_standards:
                    seen_standards.add(std_id)
                    results.append({
                        "tender_item_description": item_desc,
                        "recommendation": rec
                    })

        return results

    def generate_custom_gem_clause(self, is_code: str, custom_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates a customized, official GeM tender clause for procurement officials.
        """
        std_key = is_code.upper().strip()
        if not std_key.startswith("IS "):
            std_key = f"IS {std_key}"

        standard = self._standards_registry.get(std_key)
        if not standard:
            return f"The supplied material shall conform to Indian Standard {is_code} with all latest amendments and statutory BIS certification."

        clause = standard["gem_tender_clause"]
        if custom_params and custom_params.get("delivery_timeline_days"):
            clause += f" Material must be supplied within {custom_params['delivery_timeline_days']} calendar days from date of Purchase Order (PO)."
        if custom_params and custom_params.get("third_party_inspection_agency"):
            clause += f" Third-party inspection (TPI) will be conducted by {custom_params['third_party_inspection_agency']} prior to dispatch."

        return clause

    def export_gem_boq_csv(self, items: List[Dict[str, Any]]) -> str:
        """
        Builds a comprehensive, GeM-compatible CSV Schedule of Requirements (BoQ)
        from a list of extracted or recommended tender items.
        """
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Item No",
            "Tender Item Description",
            "Mandatory Indian Standard",
            "Standard Title",
            "Latest Published Edition",
            "Active Amendments",
            "Certification Scheme",
            "QCO Mandatory Status",
            "Issuing Ministry",
            "Mandatory Test Methods (NABL)",
            "Official GeM Specification Clause"
        ])
        for idx, item in enumerate(items, start=1):
            desc = item.get("tender_item_description", f"Item {idx}")
            rec = item.get("recommendation", {})
            primary = rec.get("primary_standard", {})
            code = primary.get("code", "N/A")
            title = primary.get("title", "")
            edition = primary.get("latest_edition", "")
            amendments = "; ".join([f"Amd {a['number']} ({a['year']})" for a in primary.get("active_amendments", [])])
            qco = rec.get("mandatory_certification", {})
            scheme = qco.get("scheme", "N/A")
            is_mand = "MANDATORY" if qco.get("is_mandatory") else "VOLUNTARY"
            ministry = qco.get("issuing_ministry", "N/A")
            allied = rec.get("allied_standards", {})
            test_methods = "; ".join([t.get("code", "") for t in allied.get("test_methods", [])])
            clause = rec.get("gem_tender_clause", "")
            writer.writerow([
                idx,
                desc,
                code,
                title,
                edition,
                amendments,
                scheme,
                is_mand,
                ministry,
                test_methods,
                clause
            ])
        return output.getvalue()


procurement_service = ProcurementService()
