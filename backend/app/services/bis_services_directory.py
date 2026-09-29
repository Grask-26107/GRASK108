"""
BIS Services & Initiatives Master Directory (SIH26107)
Provides comprehensive statutory data for:
  - Standards Clubs in Educational Institutions (Schools & Colleges)
  - National Institute of Training for Standardization (NITS)
  - Laboratory Recognition Scheme (LRS / NABL Accreditation)
  - Product Certification (ISI Mark, FMCS, Eco-Mark)
  - Compulsory Registration Scheme (CRS - MeitY)
  - Hallmarking Scheme (6-Digit HUID)
  - Consumer Affairs & Grievance Redressal (BIS Care App, NCH 1915)
  - 17 BIS Technical Departments & Standards Formulation
"""

import re
from typing import Dict, Any, List

BIS_SERVICES_DIRECTORY: Dict[str, Any] = {
    "standards_clubs": {
        "title": "BIS Standards Clubs in Schools & Higher Educational Institutions",
        "category": "Educational Initiatives & Youth Sensitization",
        "ministry": "Ministry of Consumer Affairs, Food & Public Distribution",
        "tagline": "Fostering Quality Consciousness & Scientific Temper through Standards",
        "overview": (
            "Standards Clubs are established by BIS in schools (Classes 9th to 12th) and engineering colleges / universities. "
            "The objective is to expose young minds to the importance of standards, quality, and safety in daily life, "
            "bridging theoretical science textbooks with practical industrial quality testing."
        ),
        "financial_grants": [
            {
                "scheme": "Annual Learning Activity Grant",
                "amount": "₹10,000 per annum",
                "purpose": "Funding standards writing competitions, quiz contests, debates, essay competitions, and poster-making."
            },
            {
                "scheme": "Science Laboratory Upgrade Grant (Learning Science via Standards)",
                "amount": "Up to ₹20,000 per institution",
                "purpose": "Procuring equipment and apparatus to perform practical experiments demonstrating Indian Standards (e.g. testing water pH, food adulteration, tensile strength)."
            },
            {
                "scheme": "Exposure Visits",
                "amount": "Full travel & logistics sponsored by BIS",
                "purpose": "Sponsoring students and mentors to visit NABL-accredited testing laboratories, manufacturing plants, and BIS Regional Offices."
            }
        ],
        "key_activities": [
            "Learning Science via Standards: Curriculum-aligned lesson plans demonstrating physics and chemistry principles through IS specifications.",
            "Quality Quizzes and Standards Writing Competitions at District, State, and National levels.",
            "Consumer Awareness Rallies and Door-to-Door citizen campaigns on identifying ISI marks and HUID gold hallmarks.",
            "Industrial and Laboratory Exposure Visits to witness real destructive/non-destructive testing."
        ],
        "mentor_role": "Each club is guided by a trained Science/Engineering Faculty Mentor nominated by the institution and certified by BIS.",
        "eligibility": "Government and private recognized schools with science streams (Class 9-12), engineering colleges, polytechnics, and universities across all Indian states.",
        "how_to_enroll": "School Principals/Directors can apply directly through the nearest BIS Branch Office (BO) or online via the Standards Promotion portal on bis.gov.in."
    },
    "nits_training": {
        "title": "National Institute of Training for Standardization (NITS)",
        "category": "Professional Capacity Building & Standards Training",
        "location": "NITS Campus, A-20 & 21, Institutional Area, Sector 62, Noida, UP - 201309",
        "overview": (
            "NITS is the apex training institute of BIS. It conducts specialized training programs for industry executives, "
            "quality managers, laboratory testing personnel, academic faculty, and international delegates under ITEC/SCAAP."
        ),
        "core_programs": [
            {
                "program": "ISO/IEC 17025 Laboratory Quality Management System (LQMS)",
                "duration": "4 Days",
                "target_audience": "Laboratory Directors, Testing Engineers, NABL Quality Managers",
                "coverage": "Implementation of ISO/IEC 17025:2017, measurement uncertainty, method validation, proficiency testing."
            },
            {
                "program": "Lead Auditor Training for Management Systems",
                "duration": "5 Days",
                "target_audience": "Quality Professionals, Consultants, Auditors",
                "coverage": "IRCA/NABCB recognized Lead Auditor certifications for IS/ISO 9001 (QMS), IS/ISO 14001 (EMS), IS/ISO 22000 (FSMS), IS/ISO 45001 (OH&S), and IS/ISO/IEC 27001 (ISMS)."
            },
            {
                "program": "Statistical Quality Control (SQC) & Sampling Plans",
                "duration": "3 Days",
                "target_audience": "Manufacturing Plant Managers, Production Engineers",
                "coverage": "Application of IS 2500 sampling tables, process capability (Cp, Cpk), control charts (SPC)."
            },
            {
                "program": "Conformity Assessment & BIS Certification Guidelines",
                "duration": "2 Days",
                "target_audience": "New License Applicants, MSMEs, Startup Founders",
                "coverage": "Scheme-I Product Certification, Scheme of Inspection and Testing (SIT), Manakonline e-filing."
            }
        ],
        "international_outreach": "NITS conducts developing nation standardization training under the Indian Technical and Economic Cooperation (ITEC) programme of Ministry of External Affairs.",
        "enrollment_portal": "https://www.bis.gov.in/nits/ or email nits@bis.gov.in"
    },
    "lab_recognition": {
        "title": "Laboratory Recognition Scheme (LRS)",
        "category": "Testing Infrastructure & Conformity Assessment",
        "statutory_basis": "Section 13(4) and Section 20, Bureau of Indian Standards Act, 2016",
        "overview": (
            "To support conformity assessment of products under mandatory and voluntary certification, BIS recognizes "
            "independent external laboratories across India under the Laboratory Recognition Scheme (LRS) 2020."
        ),
        "prerequisites": [
            "Mandatory Accreditation by NABL (National Accreditation Board for Testing and Calibration Laboratories) per ISO/IEC 17025 for the specific Indian Standards applied for.",
            "Demonstrated testing competence, environmental controls (temperature/humidity conditioning), and qualified testing signatories.",
            "Measurement equipment calibrated with unbroken traceability to National Physical Laboratory (NPL) or international BIPM standards.",
            "Participation in Proficiency Testing (PT) and Inter-Laboratory Comparison (ILC) programs."
        ],
        "audit_process": [
            "1. Online Application on BIS Manakonline (LRS Portal).",
            "2. Scrutiny of Quality Manual, NABL Scope, and calibration certificates.",
            "3. On-site assessment and witness testing by BIS Technical Officers.",
            "4. Grant of Recognition for a 3-year term with periodic surveillance audits."
        ],
        "benefits": "Recognized labs receive samples drawn by BIS officers from manufacturing premises and open retail markets for official conformity testing."
    },
    "consumer_protection": {
        "title": "Consumer Protection & Grievance Redressal Framework",
        "category": "Citizen Rights & Enforcement",
        "statutory_basis": "Section 29, BIS Act 2016 & Consumer Protection Act 2019",
        "helpline": "National Consumer Helpline: 1915 (Toll-Free, 24x7)",
        "bis_care_app": {
            "name": "BIS Care App (Android & iOS)",
            "features": [
                "Verify License Details (CM/L): Check authenticity of any ISI mark by entering 7 or 8-digit number.",
                "Verify HUID: Verify 6-digit laser hallmark on gold jewellery (jeweller name, AHC center, carat purity).",
                "Verify Registration (CRS): Validate electronics R-Number under Scheme-II.",
                "Lodge Grievance: Snap photo of sub-standard product or fake mark and lodge official complaint with geo-location.",
                "Know Your Standard: Search standards applicable to any consumer item."
            ]
        },
        "penalties_for_misuse": (
            "Misuse of the Standard Mark (ISI mark), sale of non-certified mandatory items under QCOs, or fraudulent hallmarking "
            "is punishable with imprisonment up to 2 years, or a fine not less than ₹2 Lakhs, extendable up to 10 times the value of products (Section 29, BIS Act 2016)."
        )
    },
    "departments_17": [
        {"code": "CED", "name": "Civil Engineering Department", "standards_count": 3120, "scope": "Cement, Concrete, Structural Steel, Timber, Soil Mechanics, Smart Cities, Earthquake Engineering (NBC 2016, IS 269, IS 456)"},
        {"code": "CHD", "name": "Chemical Department", "standards_count": 2840, "scope": "Paints, Inks, Soaps, Detergents, Explosives, Fertilizers, Leather, Paper, Cosmetics & Industrial Chemicals (IS 540, IS 4707)"},
        {"code": "ETD", "name": "Electrotechnical Department", "standards_count": 2450, "scope": "Switchgear, Power Transformers, Solar PV Cells, Electric Vehicles, Cables, Smart Grids, Batteries (IS 1293, IS 694, IS 2026)"},
        {"code": "FAD", "name": "Food and Agriculture Department", "standards_count": 2610, "scope": "Packaged Water, Dairy, Edible Oils, Agricultural Machinery, Pesticides, Food Hygiene, Organic Products (IS 14543, IS 10500)"},
        {"code": "LITD", "name": "Electronics and Information Technology Department", "standards_count": 1980, "scope": "AI, Cloud Computing, Cybersecurity, Mobile Devices, Displays, IoT, Biometrics, Scheme-II CRS (IS 13252, IS 16046)"},
        {"code": "MED", "name": "Mechanical Engineering Department", "standards_count": 3200, "scope": "Boilers, Pressure Vessels, Pumps, Industrial Valves, Hand Tools, Machine Tools, Robotics, Fire Fighting (IS 2825, IS 1520)"},
        {"code": "MHD", "name": "Medical Equipment and Hospital Planning Department", "standards_count": 1420, "scope": "Surgical Instruments, Implants, Diagnostic Imaging, Syringes, Cleanrooms, Medical Masks (IS 16289, IS/ISO 13485)"},
        {"code": "MTD", "name": "Metallurgical Engineering Department", "standards_count": 1850, "scope": "Wrought Steels, TMT Rebars, Cast Iron, Non-Ferrous Alloys, Gold/Silver Hallmarking HUID (IS 1786, IS 1417, IS 2062)"},
        {"code": "PCD", "name": "Petroleum, Coal and Related Products Department", "standards_count": 1640, "scope": "BS-VI Petrol, Diesel, LPG Cylinders, Lubricants, Bitumen, Petrochemicals, Polymers, HDPE Pipes (IS 2796, IS 4984)"},
        {"code": "PRD", "name": "Production and General Engineering Department", "standards_count": 2685, "scope": "Fasteners (Nuts/Bolts), Bearings, Precision Metrology, Engineering Drawings, Welding Consumables (IS 1363, IS 1367)"},
        {"code": "TED", "name": "Transport Engineering Department", "standards_count": 1580, "scope": "Automotive Components, Two-Wheeler Helmets, EV Charging, Railway Rolling Stock, Shipbuilding (IS 4151, IS 17017)"},
        {"code": "TXD", "name": "Textile Department", "standards_count": 1720, "scope": "Technical Textiles, Geotextiles, Medical Textiles, Protective Clothing, Cotton, Silk, Yarns (IS 17423, IS 15748)"},
        {"code": "WRD", "name": "Water Resources Department", "standards_count": 890, "scope": "Dams, Canals, Irrigation Micro-Drip/Sprinklers, Flood Management, Hydrology, Hydroelectric (IS 12786, IS 6512)"},
        {"code": "MSD", "name": "Management and Systems Department", "standards_count": 780, "scope": "Management Systems Certification (ISO 9001 QMS, ISO 14001 EMS, ISO 22000 FSMS, ISO 45001 OH&S, ISO 27001)"},
        {"code": "SSD", "name": "Services Sector Department", "standards_count": 464, "scope": "Banking, Financial Services, Education, Tourism, Hospitality, Legal Services, Logistics, E-Commerce"},
        {"code": "EED", "name": "Environment & Ecology Department", "standards_count": 140, "scope": "National Eco-Mark Scheme, Carbon Footprint Verification, Compostable Plastics, E-Waste Management (IS 17088)"},
        {"code": "AYD", "name": "Ayush Department", "standards_count": 230, "scope": "Ayurveda, Yoga, Unani, Siddha, Homoeopathy, Herbal Raw Materials & Ayush Premium Mark Quality (IS 17950, IS 17890)"}
    ]
}

# =========================================================================
# AUTHORITATIVE TESTING LABORATORIES DIRECTORY (LRS & NABL ACCREDITED)
# =========================================================================
TESTING_LABORATORIES_DIRECTORY: List[Dict[str, Any]] = [
    {
        "id": "LAB-BIS-CENTRAL",
        "name": "BIS Central Laboratory (Sahibabad)",
        "type": "BIS Owned & Apex National Laboratory",
        "region": "North",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "address": "Plot No. 20/9, Site IV, Sahibabad Industrial Area, Ghaziabad, UP - 201010",
        "phone": "+91-120-4177100",
        "email": "cl@bis.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Certificate: TC-5012)",
        "disciplines": ["Chemical", "Mechanical", "Electrical", "Microbiology", "Water & Food"],
        "standards_supported": ["IS 14543", "IS 10500", "IS 13428", "IS 1786", "IS 269", "IS 1293", "IS 4151", "IS 13252"],
        "description": "The apex national testing facility of BIS. Houses comprehensive test facilities for Packaged Drinking Water, TMT steel rebars, Cement, Electrical Plugs, Protective Helmets, and electronics."
    },
    {
        "id": "LAB-BIS-WESTERN",
        "name": "BIS Western Regional Laboratory (WRL)",
        "type": "BIS Regional Testing Laboratory",
        "region": "West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "address": "Manakalaya, E-9, MIDC, Behind Marol Telephone Exchange, Andheri (East), Mumbai - 400093",
        "phone": "+91-22-28329295",
        "email": "wrl@bis.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited)",
        "disciplines": ["Chemical", "Metallurgy", "Water & Food", "Civil & Cement", "Plastics"],
        "standards_supported": ["IS 14543", "IS 1786", "IS 269", "IS 4984", "IS 1417"],
        "description": "Serves industries across Maharashtra, Gujarat, Goa, and MP. Specialized in metallurgical steel analysis, cement compressive strength, drinking water, and polymers."
    },
    {
        "id": "LAB-BIS-SOUTHERN",
        "name": "BIS Southern Regional Laboratory (SRL)",
        "type": "BIS Regional Testing Laboratory",
        "region": "South",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "address": "CIT Campus, IV Cross Road, Taramani, Chennai, Tamil Nadu - 600113",
        "phone": "+91-44-22541442",
        "email": "srl@bis.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited)",
        "disciplines": ["Electrical", "Electronics", "Chemical", "Mechanical", "Water & Food"],
        "standards_supported": ["IS 14543", "IS 1786", "IS 269", "IS 13252", "IS 16046", "IS 1293"],
        "description": "Primary testing hub for Southern India. Accredited for electronics CRS testing, battery safety, packaged drinking water, and electrotechnical appliances."
    },
    {
        "id": "LAB-BIS-EASTERN",
        "name": "BIS Eastern Regional Laboratory (ERL)",
        "type": "BIS Regional Testing Laboratory",
        "region": "East",
        "city": "Kolkata",
        "state": "West Bengal",
        "address": "1/14, C.I.T. Scheme VII M, V.I.P. Road, Kankurgachi, Kolkata, West Bengal - 700054",
        "phone": "+91-33-23207080",
        "email": "erl@bis.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited)",
        "disciplines": ["Metallurgy", "Civil & Cement", "Chemical", "Water & Food"],
        "standards_supported": ["IS 1786", "IS 269", "IS 14543", "IS 10500", "IS 228"],
        "description": "Apex eastern testing center specializing in primary & secondary steel rolling mills (TMT bars), cement, structural concrete, and mineral water."
    },
    {
        "id": "LAB-BIS-NORTHERN",
        "name": "BIS Northern Regional Laboratory (NRL)",
        "type": "BIS Regional Testing Laboratory",
        "region": "North",
        "city": "Mohali / Chandigarh",
        "state": "Punjab",
        "address": "Plot No. 4-A, Sector 27-B, Madhya Marg, Chandigarh / Phase VII, Industrial Area, Mohali - 160019",
        "phone": "+91-172-2650206",
        "email": "nrl@bis.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited)",
        "disciplines": ["Chemical", "Mechanical", "Water & Food", "Petroleum"],
        "standards_supported": ["IS 14543", "IS 1786", "IS 269", "IS 1460", "IS 2796"],
        "description": "Serves Punjab, Haryana, Himachal Pradesh, and J&K. Full facilities for fuels, lubricants, water filtration, and civil construction materials."
    },
    {
        "id": "LAB-NTH-ALIPORE",
        "name": "National Test House (NTH - Eastern HQ)",
        "type": "Apex Government Testing House (DoCA Recognized)",
        "region": "East",
        "city": "Kolkata",
        "state": "West Bengal",
        "address": "Block CP, Sector V, Salt Lake City, Kolkata - 700091 / Alipore, Kolkata - 700027",
        "phone": "+91-33-23673869",
        "email": "director.nth-wb@gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS LRS Recognized)",
        "disciplines": ["Civil & Cement", "Chemical", "High-Voltage Electrical", "Non-Destructive Testing (NDT)"],
        "standards_supported": ["IS 269", "IS 1786", "IS 4984", "IS 1293", "IS 14543"],
        "description": "Over 100 years of national testing heritage under the Department of Consumer Affairs. Testing partner for major infrastructure, BIS certification, and government procurements."
    },
    {
        "id": "LAB-NTH-MUMBAI",
        "name": "National Test House (NTH - Western Region)",
        "type": "Apex Government Testing House",
        "region": "West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "address": "Saki Naka, Kurla-Andheri Road, Mumbai, Maharashtra - 400072",
        "phone": "+91-22-28573574",
        "email": "director.nth-wr@gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Recognized)",
        "disciplines": ["Mechanical", "Chemical", "Polymers", "Electrical"],
        "standards_supported": ["IS 1786", "IS 4984", "IS 1293", "IS 14543"],
        "description": "Equipped with advanced universal tensile machines (UTM), spectrometry, burst testing rigs, and electrical safety benches."
    },
    {
        "id": "LAB-SHRIRAM-DELHI",
        "name": "Shriram Institute for Industrial Research (SIIR)",
        "type": "Independent NABL & BIS Recognized Research Institute",
        "region": "North",
        "city": "New Delhi",
        "state": "Delhi NCR",
        "address": "19, University Road, Delhi - 110007",
        "phone": "+91-11-27667267",
        "email": "customercare@shriraminstitute.org",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited & BIS Approved)",
        "disciplines": ["Chemical", "Trace Contaminants", "Toxic Heavy Metals", "Food & Water", "Polymers & Toys"],
        "standards_supported": ["IS 14543", "IS 10500", "IS 4984", "IS 9873", "IS 14625"],
        "description": "Leading research & testing institute for ultra-trace heavy metal detection (ICP-MS, AAS) in packaged water, food contact plastics, baby feeding bottles, and toy safety."
    },
    {
        "id": "LAB-CPRI-BLR",
        "name": "Central Power Research Institute (CPRI)",
        "type": "Apex National Power & Electrotechnical Lab",
        "region": "South",
        "city": "Bengaluru",
        "state": "Karnataka",
        "address": "Prof. Sir C.V. Raman Road, Sadashivanagar, Bengaluru, Karnataka - 560080",
        "phone": "+91-80-22072222",
        "email": "cpri@nic.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Recognized)",
        "disciplines": ["Electrical", "Electronics", "High Voltage", "Switchgear"],
        "standards_supported": ["IS 1293", "IS 13252", "IS 16046", "IS 2026", "IS 694"],
        "description": "India's premier testing facility for power transformers, switchgear, electric vehicle batteries, solar inverters, and electrical wiring accessories."
    },
    {
        "id": "LAB-CIPET-HQ",
        "name": "Central Institute of Petrochemicals Engineering & Technology (CIPET)",
        "type": "National Polymer & Petrochemical Testing Center",
        "region": "South",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "address": "CIPET Head Office, TVK Industrial Estate, Guindy, Chennai, Tamil Nadu - 600032",
        "phone": "+91-44-22254780",
        "email": "cipetho@cipet.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Recognized)",
        "disciplines": ["Polymers", "Plastics", "Pipes", "Automotive Helmets"],
        "standards_supported": ["IS 4984", "IS 4151", "IS 12235", "IS 13592"],
        "description": "Apex testing agency for HDPE pipes, PVC conduits, plastic packaging, and impact attenuation & chin strap testing for two-wheeler protective helmets (IS 4151)."
    },
    {
        "id": "LAB-NCCBM-BALLABGARH",
        "name": "National Council for Cement and Building Materials (NCCBM)",
        "type": "Apex Civil & Cement Research Institute",
        "region": "North",
        "city": "Ballabgarh / Faridabad",
        "state": "Haryana",
        "address": "34 Km Stone, Delhi-Mathura Road (NH-2), Ballabgarh, Faridabad, Haryana - 121004",
        "phone": "+91-129-4192222",
        "email": "nccbm@ncbindia.com",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Recognized)",
        "disciplines": ["Civil & Cement", "Structural Metallurgy", "Concrete"],
        "standards_supported": ["IS 269", "IS 1489", "IS 456", "IS 1786"],
        "description": "The apex research and testing body for the cement and concrete industry in India. Equipped for 28-day compressive strength, soundness (Le Chatelier/Autoclave), and chemical fineness."
    },
    {
        "id": "LAB-ARAI-PUNE",
        "name": "Automotive Research Association of India (ARAI)",
        "type": "Apex Automotive & Safety Testing Institute",
        "region": "West",
        "city": "Pune",
        "state": "Maharashtra",
        "address": "Survey No. 102, Vetal Hill, Off Paud Road, Kothrud, Pune, Maharashtra - 411038",
        "phone": "+91-20-30231111",
        "email": "director@araiindia.com",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Approved)",
        "disciplines": ["Automotive Components", "Helmets", "EV Batteries", "Safety Glazing"],
        "standards_supported": ["IS 4151", "IS 16046", "IS 2553"],
        "description": "The nation's foremost automotive testing authority. Tests two-wheeler helmets for dynamic impact absorption and retention systems, plus EV lithium battery packs."
    },
    {
        "id": "LAB-VIMTA-HYD",
        "name": "Vimta Labs Limited",
        "type": "NABL, BIS LRS Recognized & FSSAI National Referral Laboratory",
        "region": "South",
        "city": "Hyderabad",
        "state": "Telangana",
        "address": "Plot No. 142, IDA Phase-II, Cherlapally, Hyderabad, Telangana - 500051",
        "phone": "+91-40-67404040",
        "email": "mktg@vimta.com",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & FSSAI Notified & BIS Recognized)",
        "disciplines": ["Water & Food", "Chemical", "Toxicology", "Trace Heavy Metals", "Environmental"],
        "standards_supported": ["IS 14543", "IS 10500", "IS 13428", "IS 14433", "IS 1786"],
        "description": "Leading laboratory hub in Hyderabad serving Telangana and Andhra Pradesh. Premier testing for packaged water, pesticide residues, food safety, and metals."
    },
    {
        "id": "LAB-CFTRI-MYS",
        "name": "CSIR - Central Food Technological Research Institute (CFTRI)",
        "type": "Apex National Food Referral Laboratory (FSSAI & BIS Approved)",
        "region": "South",
        "city": "Mysuru / Bengaluru",
        "state": "Karnataka",
        "address": "Cheluvamba Mansion, Opp. Railway Station, Mysuru, Karnataka - 570020",
        "phone": "+91-821-2515910",
        "email": "director@cftri.res.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited & FSSAI Referral)",
        "disciplines": ["Food Safety", "Water & Food", "Microbiology", "Pesticide Residues", "Nutritional Profiling"],
        "standards_supported": ["IS 14543", "IS 13428", "IS 11536", "IS 14433", "IS 1797"],
        "description": "The nation's apex food research institute. Referral laboratory for food adulteration disputes, infant nutrition safety, pesticide residues, and packaged water."
    },
    {
        "id": "LAB-ERDA-VADODARA",
        "name": "Electrical Research and Development Association (ERDA)",
        "type": "Apex National Electrotechnical Testing Laboratory",
        "region": "West",
        "city": "Vadodara / Ahmedabad",
        "state": "Gujarat",
        "address": "ERDA Road, GIDC, Makarpura, Vadodara, Gujarat - 390010",
        "phone": "+91-265-3043129",
        "email": "erda@erda.org",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL & BIS Recognized)",
        "disciplines": ["Electrical", "Electronics", "High Voltage", "Switchgear", "EV Battery"],
        "standards_supported": ["IS 1293", "IS 694", "IS 2026", "IS 13252", "IS 16046"],
        "description": "Western India's premier electrical testing organization. Tests plugs, sockets, switches, cables, transformers, and electric vehicle batteries under BIS CRS."
    },
    {
        "id": "LAB-NFL-GHAZIABAD",
        "name": "National Food Laboratory (NFL Ghaziabad - FSSAI)",
        "type": "FSSAI Apex Referral Laboratory",
        "region": "North",
        "city": "Ghaziabad / Delhi NCR",
        "state": "Uttar Pradesh",
        "address": "Ahinsa Khand II, Indirapuram, Ghaziabad, Uttar Pradesh - 201014",
        "phone": "+91-120-2601103",
        "email": "nfl.ghaziabad@fssai.gov.in",
        "nabl_accreditation": "ISO/IEC 17025:2017 (NABL Accredited & FSSAI Apex)",
        "disciplines": ["Food Safety", "Water & Food", "Heavy Metals", "Adulteration Testing"],
        "standards_supported": ["IS 14543", "IS 10500", "IS 13428", "IS 14433"],
        "description": "FSSAI apex referral laboratory for Northern India. Equipped with high-resolution mass spectrometers for food adulterants, packaged water, and imported food consignments."
    }
]


def search_testing_laboratories(
    query: str = "",
    standard_code: str = "",
    region: str = "",
    discipline: str = ""
) -> List[Dict[str, Any]]:
    """
    Finds accredited BIS and NABL testing laboratories matching product standards, region, or disciplines.
    """
    clean_q = query.lower().strip() if query else ""
    clean_std = standard_code.upper().replace(" ", "").strip() if standard_code else ""
    clean_reg = region.lower().strip() if region else ""
    clean_disc = discipline.lower().strip() if discipline else ""

    results = []
    for lab in TESTING_LABORATORIES_DIRECTORY:
        score = 0

        # Check standard code match
        if clean_std:
            for std in lab["standards_supported"]:
                if clean_std in std.replace(" ", ""):
                    score += 5

        # Check region match
        if clean_reg:
            if clean_reg in lab["region"].lower() or clean_reg in lab["state"].lower():
                score += 3

        # Check discipline match
        if clean_disc:
            for d in lab["disciplines"]:
                if clean_disc in d.lower():
                    score += 4

        # Check general text query match
        if clean_q:
            combined = (
                f"{lab['name']} {lab['city']} {lab['state']} {lab['description']} "
                f"{' '.join(lab['disciplines'])} {' '.join(lab['standards_supported'])}"
            ).lower()
            if clean_q in combined:
                score += 3
            # check individual query tokens
            tokens = [t for t in re.split(r'\s+', clean_q) if len(t) > 2]
            for token in tokens:
                if token in combined:
                    score += 1

        # If no filters provided, return all
        if not clean_q and not clean_std and not clean_reg and not clean_disc:
            results.append(lab)
        elif score > 0:
            results.append(lab)

    return results


# Attach testing laboratories directly to LRS service directory
BIS_SERVICES_DIRECTORY["lab_recognition"]["recognized_laboratories"] = TESTING_LABORATORIES_DIRECTORY
