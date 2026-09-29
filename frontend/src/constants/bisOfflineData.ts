import { BisServicesDirectoryData, TestingLaboratory } from '../types';

export const OFFLINE_TESTING_LABORATORIES: TestingLaboratory[] = [
  {
    id: "LAB-BIS-CENTRAL",
    name: "BIS Central Laboratory (Sahibabad)",
    type: "BIS Owned & Apex National Laboratory",
    region: "North",
    city: "Ghaziabad",
    state: "Uttar Pradesh",
    address: "Plot No. 20/9, Site IV, Sahibabad Industrial Area, Ghaziabad, UP - 201010",
    phone: "+91-120-4177100",
    email: "cl@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Certificate: TC-5012)",
    disciplines: ["Chemical", "Mechanical", "Electrical", "Microbiology", "Water & Food"],
    standards_supported: ["IS 14543", "IS 10500", "IS 13428", "IS 1786", "IS 269", "IS 1293", "IS 4151", "IS 13252"],
    description: "The apex national testing facility of BIS. Houses comprehensive test facilities for Packaged Drinking Water, TMT steel rebars, Cement, Electrical Plugs, Protective Helmets, and electronics."
  },
  {
    id: "LAB-BIS-WESTERN",
    name: "BIS Western Regional Laboratory (WRL)",
    type: "BIS Regional Testing Laboratory",
    region: "West",
    city: "Mumbai",
    state: "Maharashtra",
    address: "Manakalaya, E-9, MIDC, Behind Marol Telephone Exchange, Andheri (East), Mumbai - 400093",
    phone: "+91-22-28329295",
    email: "wrl@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Accredited)",
    disciplines: ["Chemical", "Metallurgy", "Water & Food", "Civil & Cement", "Plastics"],
    standards_supported: ["IS 14543", "IS 1786", "IS 269", "IS 4984", "IS 1417"],
    description: "Serves industries across Maharashtra, Gujarat, Goa, and MP. Specialized in metallurgical steel analysis, cement compressive strength, drinking water, and polymers."
  },
  {
    id: "LAB-BIS-SOUTHERN",
    name: "BIS Southern Regional Laboratory (SRL)",
    type: "BIS Regional Testing Laboratory",
    region: "South",
    city: "Chennai",
    state: "Tamil Nadu",
    address: "CIT Campus, IV Cross Road, Taramani, Chennai, Tamil Nadu - 600113",
    phone: "+91-44-22541442",
    email: "srl@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Accredited)",
    disciplines: ["Electrical", "Electronics", "Chemical", "Mechanical", "Water & Food"],
    standards_supported: ["IS 14543", "IS 1786", "IS 269", "IS 13252", "IS 16046", "IS 1293"],
    description: "Primary testing hub for Southern India. Accredited for electronics CRS testing, battery safety, packaged drinking water, and electrotechnical appliances."
  },
  {
    id: "LAB-BIS-EASTERN",
    name: "BIS Eastern Regional Laboratory (ERL)",
    type: "BIS Regional Testing Laboratory",
    region: "East",
    city: "Kolkata",
    state: "West Bengal",
    address: "1/14 C.I.T. Scheme VII M, V.I.P. Road, Kankurgachi, Kolkata - 700054",
    phone: "+91-33-23207080",
    email: "erl@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Accredited)",
    disciplines: ["Metallurgy", "Chemical", "Civil", "Mechanical", "Jute & Textiles"],
    standards_supported: ["IS 1786", "IS 2062", "IS 269", "IS 14543", "IS 4984"],
    description: "Eastern India hub specializing in high-grade TMT steel, structural steel sections, Portland cement, mining equipment safety, and drinking water testing."
  },
  {
    id: "LAB-BIS-NORTHERN",
    name: "BIS Northern Regional Laboratory (NRL)",
    type: "BIS Regional Testing Laboratory",
    region: "North",
    city: "Mohali",
    state: "Punjab",
    address: "Plot No. 4-A, Sector 27-B, Madhya Marg, Chandigarh / Mohali - 160019",
    phone: "+91-172-2650206",
    email: "nrl@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Accredited)",
    disciplines: ["Agricultural Equipment", "Chemical", "Civil", "Electrical", "Mechanical"],
    standards_supported: ["IS 14543", "IS 10500", "IS 1786", "IS 269", "IS 4984", "IS 8034"],
    description: "Specialized in agricultural machinery, submersible pump verification, fertilizer testing, drinking water, and construction steel for Punjab, Haryana, and HP."
  },
  {
    id: "LAB-BIS-BANGALORE",
    name: "BIS Branch Laboratory (Bengaluru)",
    type: "BIS Branch Testing Laboratory",
    region: "South",
    city: "Bengaluru",
    state: "Karnataka",
    address: "Peenya Industrial Area, 1st Stage, Tumkur Road, Bengaluru, Karnataka - 560058",
    phone: "+91-80-28394955",
    email: "bnbo-lab@bis.gov.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Accredited)",
    disciplines: ["Electronics", "Information Technology", "Electrical", "Plastics"],
    standards_supported: ["IS 13252", "IS 16046", "IS 616", "IS 1293", "IS 302"],
    description: "Testing facility focused on MeitY CRS electronics: smart devices, lithium batteries, power adapters, and domestic electrical appliances."
  },
  {
    id: "LAB-NABL-SHRIRAM",
    name: "Shriram Institute for Industrial Research (NABL TC-5421)",
    type: "NABL Accredited Partner Laboratory",
    region: "North",
    city: "New Delhi",
    state: "Delhi",
    address: "19, University Road, Block A, Timarpur, Delhi - 110007",
    phone: "+91-11-27667267",
    email: "customercare@shriraminstitute.org",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Certificate: TC-5421)",
    disciplines: ["Chemical", "Biological", "Mechanical", "Toxicology", "Plastics & Polymers"],
    standards_supported: ["IS 14543", "IS 10500", "IS 13428", "IS 4984", "IS 4985", "IS 17088"],
    description: "Premier independent research and testing laboratory recognized under BIS LRS. Apex facilities for pesticides, heavy metals residue, toxicological analysis, and compostable plastics."
  },
  {
    id: "LAB-NABL-NCCBM",
    name: "National Council for Cement and Building Materials (NCCBM)",
    type: "NABL Accredited Partner Laboratory",
    region: "North",
    city: "Ballabgarh",
    state: "Haryana",
    address: "34 Km Stone, Delhi-Mathura Road (NH-2), Ballabgarh, Haryana - 121004",
    phone: "+91-129-4192222",
    email: "nccbm@ncbindia.com",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Certificate: TC-5108)",
    disciplines: ["Civil", "Mechanical", "Chemical"],
    standards_supported: ["IS 269", "IS 1489", "IS 456", "IS 1786", "IS 383", "IS 455"],
    description: "Apex national laboratory for cement, clinker, concrete, aggregates, and structural building materials. Official witness testing for BIS Scheme-I cement licenses."
  },
  {
    id: "LAB-NABL-NEERI",
    name: "CSIR - National Environmental Engineering Research Institute (NEERI)",
    type: "CSIR National Laboratory & BIS Recognized",
    region: "West",
    city: "Nagpur",
    state: "Maharashtra",
    address: "Nehru Marg, Wardha Road, Nagpur, Maharashtra - 440020",
    phone: "+91-712-2249885",
    email: "director@neeri.res.in",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Certificate: TC-6045)",
    disciplines: ["Environmental Testing", "Water & Wastewater", "Chemical", "Microbiology"],
    standards_supported: ["IS 10500", "IS 14543", "IS 13428", "IS 1622", "IS 3025"],
    description: "Premier environmental research institute. Houses state-of-the-art ICP-MS and GC-MS equipment for ultra-trace heavy metals and pesticide residue testing."
  },
  {
    id: "LAB-NABL-TUV-SOUTH",
    name: "TUV Rheinland India Testing Center",
    type: "NABL Accredited Commercial Laboratory",
    region: "South",
    city: "Bengaluru",
    state: "Karnataka",
    address: "Plot No. 27/B, 2nd Phase, Peenya Industrial Area, Bengaluru - 560058",
    phone: "+91-80-46498000",
    email: "info-india@tuv.com",
    nabl_accreditation: "ISO/IEC 17025:2017 (NABL Certificate: TC-6234)",
    disciplines: ["Electrical Safety", "EMC / EMI", "Solar Photovoltaic", "Medical Devices", "Automotive"],
    standards_supported: ["IS 13252", "IS 14286", "IS 16046", "IS 302", "IS 16289"],
    description: "Global testing and certification laboratory recognized under BIS CRS and foreign manufacturer certification scheme (FMCS)."
  }
];

export const OFFLINE_17_TECHNICAL_DEPARTMENTS = [
  {
    code: "CED",
    name: "Civil Engineering Department",
    standards_count: 3120,
    scope: "Cement, Concrete, Structural Steel, Timber, Soil Mechanics, Smart Cities, Earthquake Engineering (NBC 2016, IS 269, IS 456)"
  },
  {
    code: "CHD",
    name: "Chemical Department",
    standards_count: 2840,
    scope: "Paints, Inks, Soaps, Detergents, Explosives, Fertilizers, Leather, Paper, Cosmetics & Industrial Chemicals (IS 540, IS 4707)"
  },
  {
    code: "ETD",
    name: "Electrotechnical Department",
    standards_count: 2450,
    scope: "Switchgear, Power Transformers, Solar PV Cells, Electric Vehicles, Cables, Smart Grids, Batteries (IS 1293, IS 694, IS 2026)"
  },
  {
    code: "FAD",
    name: "Food and Agriculture Department",
    standards_count: 2610,
    scope: "Packaged Water, Dairy, Edible Oils, Agricultural Machinery, Pesticides, Food Hygiene, Organic Products (IS 14543, IS 10500)"
  },
  {
    code: "LITD",
    name: "Electronics and Information Technology Department",
    standards_count: 1980,
    scope: "AI, Cloud Computing, Cybersecurity, Mobile Devices, Displays, IoT, Biometrics, Scheme-II CRS (IS 13252, IS 16046)"
  },
  {
    code: "MED",
    name: "Mechanical Engineering Department",
    standards_count: 3200,
    scope: "Boilers, Pressure Vessels, Pumps, Industrial Valves, Hand Tools, Machine Tools, Robotics, Fire Fighting (IS 2825, IS 1520)"
  },
  {
    code: "MHD",
    name: "Medical Equipment and Hospital Planning Department",
    standards_count: 1420,
    scope: "Surgical Instruments, Implants, Diagnostic Imaging, Syringes, Cleanrooms, Medical Masks (IS 16289, IS/ISO 13485)"
  },
  {
    code: "MTD",
    name: "Metallurgical Engineering Department",
    standards_count: 1850,
    scope: "Wrought Steels, TMT Rebars, Cast Iron, Non-Ferrous Alloys, Gold/Silver Hallmarking HUID (IS 1786, IS 1417, IS 2062)"
  },
  {
    code: "PCD",
    name: "Petroleum, Coal and Related Products Department",
    standards_count: 1640,
    scope: "BS-VI Petrol, Diesel, LPG Cylinders, Lubricants, Bitumen, Petrochemicals, Polymers, HDPE Pipes (IS 2796, IS 4984)"
  },
  {
    code: "PRD",
    name: "Production and General Engineering Department",
    standards_count: 2685,
    scope: "Fasteners (Nuts/Bolts), Bearings, Precision Metrology, Engineering Drawings, Welding Consumables (IS 1363, IS 1367)"
  },
  {
    code: "TED",
    name: "Transport Engineering Department",
    standards_count: 1580,
    scope: "Automotive Components, Two-Wheelers, Helmets, EV Charging, Railway Rolling Stock, Shipbuilding (IS 4151, IS 17017)"
  },
  {
    code: "TXD",
    name: "Textile Department",
    standards_count: 1720,
    scope: "Technical Textiles, Geotextiles, Medical Textiles, Protective Clothing, Cotton, Silk, Yarns (IS 17423, IS 15748)"
  },
  {
    code: "WRD",
    name: "Water Resources Department",
    standards_count: 890,
    scope: "Dams, Canals, Irrigation Micro-Drip/Sprinklers, Flood Management, Hydrology, Hydroelectric (IS 12786, IS 6512)"
  },
  {
    code: "MSD",
    name: "Management and Systems Department",
    standards_count: 780,
    scope: "Management Systems Certification (ISO 9001 QMS, ISO 14001 EMS, ISO 22000 FSMS, ISO 45001 OH&S, ISO 27001)"
  },
  {
    code: "SSD",
    name: "Services Sector Department",
    standards_count: 464,
    scope: "Banking, Financial Services, Education, Tourism, Hospitality, Legal Services, Logistics, E-Commerce"
  },
  {
    code: "EED",
    name: "Environment & Ecology Department",
    standards_count: 140,
    scope: "National Eco-Mark Scheme, Carbon Footprint Verification, Compostable Plastics, E-Waste Management (IS 17088)"
  },
  {
    code: "AYD",
    name: "Ayush Department",
    standards_count: 230,
    scope: "Ayurveda, Yoga, Unani, Siddha, Homoeopathy, Herbal Raw Materials & Ayush Premium Mark Quality (IS 17950, IS 17890)"
  }
];

export const DEFAULT_OFFLINE_BIS_SERVICES_DIRECTORY: BisServicesDirectoryData = {
  standards_clubs: {
    title: "BIS Standards Clubs in Schools & Higher Educational Institutions",
    category: "Educational Initiatives & Youth Sensitization",
    ministry: "Ministry of Consumer Affairs, Food & Public Distribution",
    tagline: "Fostering Quality Consciousness & Scientific Temper through Standards",
    overview: "Standards Clubs are established by BIS in schools (Classes 9th to 12th) and engineering colleges / universities. The objective is to expose young minds to the importance of standards, quality, and safety in daily life.",
    financial_grants: [
      {
        scheme: "Annual Learning Activity Grant",
        amount: "₹10,000 per annum",
        purpose: "Funding standards writing competitions, quiz contests, debates, essay competitions, and poster-making."
      },
      {
        scheme: "Science Laboratory Upgrade Grant (Learning Science via Standards)",
        amount: "Up to ₹20,000 per institution",
        purpose: "Procuring equipment and apparatus to perform practical experiments demonstrating Indian Standards."
      },
      {
        scheme: "Exposure Visits",
        amount: "Full travel & logistics sponsored by BIS",
        purpose: "Sponsoring students and mentors to visit NABL-accredited testing laboratories, manufacturing plants, and BIS Regional Offices."
      }
    ],
    key_activities: [
      "Learning Science via Standards: Curriculum-aligned lesson plans demonstrating physics and chemistry principles through IS specifications.",
      "Quality Quizzes and Standards Writing Competitions at District, State, and National levels.",
      "Consumer Awareness Rallies on identifying ISI marks and HUID gold hallmarks.",
      "Industrial and Laboratory Exposure Visits to witness real destructive/non-destructive testing."
    ],
    mentor_role: "Each club is guided by a trained Science/Engineering Faculty Mentor nominated by the institution and certified by BIS.",
    eligibility: "Government and private recognized schools (Class 9-12), engineering colleges, polytechnics, and universities across India.",
    how_to_enroll: "School Principals/Directors can apply directly through the nearest BIS Branch Office (BO) or online via bis.gov.in."
  },
  nits_training: {
    title: "National Institute of Training for Standardization (NITS)",
    category: "Professional Capacity Building & Standards Training",
    location: "NITS Campus, A-20 & 21, Institutional Area, Sector 62, Noida, UP - 201309",
    overview: "NITS is the apex training institute of BIS. It conducts specialized training programs for industry executives, quality managers, laboratory testing personnel, and academic faculty.",
    core_programs: [
      {
        program: "ISO/IEC 17025 Laboratory Quality Management System (LQMS)",
        duration: "4 Days",
        target_audience: "Laboratory Directors, Testing Engineers, NABL Quality Managers",
        coverage: "Implementation of ISO/IEC 17025:2017, measurement uncertainty, method validation, proficiency testing."
      },
      {
        program: "Lead Auditor Training for Management Systems",
        duration: "5 Days",
        target_audience: "Quality Professionals, Consultants, Auditors",
        coverage: "IRCA/NABCB recognized Lead Auditor certifications for IS/ISO 9001 (QMS), IS/ISO 14001 (EMS), IS/ISO 22000 (FSMS)."
      },
      {
        program: "Statistical Quality Control (SQC) & Sampling Plans",
        duration: "3 Days",
        target_audience: "Manufacturing Plant Managers, Production Engineers",
        coverage: "Application of IS 2500 sampling tables, process capability (Cp, Cpk), control charts (SPC)."
      },
      {
        program: "Conformity Assessment & BIS Certification Guidelines",
        duration: "2 Days",
        target_audience: "New License Applicants, MSMEs, Startup Founders",
        coverage: "Scheme-I Product Certification, Scheme of Inspection and Testing (SIT), Manakonline e-filing."
      }
    ],
    international_outreach: "NITS conducts developing nation standardization training under the Indian Technical and Economic Cooperation (ITEC) programme.",
    enrollment_portal: "https://www.bis.gov.in/nits/ or email nits@bis.gov.in"
  },
  lab_recognition: {
    title: "Laboratory Recognition Scheme (LRS)",
    category: "Testing Infrastructure & Conformity Assessment",
    statutory_basis: "Section 13(4) and Section 20, Bureau of Indian Standards Act, 2016",
    overview: "To support conformity assessment of products under mandatory and voluntary certification, BIS recognizes independent external laboratories across India under the Laboratory Recognition Scheme (LRS) 2020.",
    prerequisites: [
      "Mandatory Accreditation by NABL per ISO/IEC 17025 for the specific Indian Standards applied for.",
      "Demonstrated testing competence, environmental controls, and qualified testing signatories.",
      "Measurement equipment calibrated with unbroken traceability to NPL / BIPM standards.",
      "Participation in Proficiency Testing (PT) and Inter-Laboratory Comparison (ILC) programs."
    ],
    audit_process: [
      "1. Online Application on BIS Manakonline (LRS Portal).",
      "2. Scrutiny of Quality Manual, NABL Scope, and calibration certificates.",
      "3. On-site assessment and witness testing by BIS Technical Officers.",
      "4. Grant of Recognition for a 3-year term with periodic surveillance audits."
    ],
    benefits: [
      "Recognized labs receive samples drawn by BIS officers from manufacturing premises and retail markets for conformity testing.",
      "Listing on the official national BIS directory for industry sample testing referrals."
    ],
    recognized_laboratories: OFFLINE_TESTING_LABORATORIES
  },
  consumer_protection: {
    title: "Consumer Protection & Grievance Redressal Framework",
    category: "Citizen Rights & Enforcement",
    statutory_basis: "Section 29, BIS Act 2016 & Consumer Protection Act 2019",
    helpline: "National Consumer Helpline: 1915 (Toll-Free, 24x7)",
    bis_care_app: {
      name: "BIS Care App (Android & iOS)",
      features: [
        "Verify License Details (CM/L): Check authenticity of any ISI mark by entering 7 or 8-digit number.",
        "Verify HUID: Verify 6-digit laser hallmark on gold jewellery (jeweller name, AHC center, carat purity).",
        "Verify Registration (CRS): Validate electronics R-Number under Scheme-II.",
        "Lodge Grievance: Snap photo of sub-standard product or fake mark and lodge official complaint with geo-location.",
        "Know Your Standard: Search standards applicable to any consumer item."
      ]
    },
    penalties_for_misuse: "Misuse of the Standard Mark (ISI mark), sale of non-certified mandatory items under QCOs, or fraudulent hallmarking is punishable with imprisonment up to 2 years, or a fine not less than ₹2 Lakhs, extendable up to 10 times the value of products."
  },
  departments_17: OFFLINE_17_TECHNICAL_DEPARTMENTS
};

export const FALLBACK_SAMPLE_PROMPTS = {
  industry: [
    {
      standard: "IS 14543:2018",
      title: "Toxic Substance Limits in Packaged Water",
      prompt: "What are the exact permissible limits for Lead, Arsenic, and Mercury under IS 14543 Table 2?"
    },
    {
      standard: "IS 1786:2008",
      title: "TMT Rebars Chemical & Mechanical Tolerances",
      prompt: "What are the minimum 0.2% proof stress and elongation requirements for Fe 500D rebars under IS 1786?"
    },
    {
      standard: "IS 269:2015",
      title: "53 Grade OPC Cement Strength Benchmarks",
      prompt: "What are the mandatory 3-day, 7-day, and 28-day compressive strength limits for 53-grade cement in IS 269?"
    },
    {
      standard: "IS 694:2010",
      title: "Fire Resistant (FRLS) Building Cable Norms",
      prompt: "What are the test methods and halogen acid gas limits for FRLS copper wires under IS 694 and IS 10810?"
    }
  ],
  consumer: [
    {
      standard: "IS 14543",
      title: "How to check if bottled water is safe",
      prompt: "How can I check if the 20-litre water jar delivered to my house has a genuine ISI mark?"
    },
    {
      standard: "IS 1417",
      title: "Verify Gold Jewellery 6-digit HUID",
      prompt: "What is a 6-digit laser HUID on gold jewellery and how can I verify it using the BIS Care app?"
    },
    {
      standard: "IS 4151",
      title: "Motorcycle Helmet ISI Safety Standards",
      prompt: "Why is a roadside helmet illegal in India? How do I verify a genuine IS 4151 ISI certified helmet?"
    },
    {
      standard: "FSSAI Food Safety",
      title: "Identify Hidden Sugars & Palm Oil",
      prompt: "How do I check if my breakfast cereal or biscuit contains hidden sugars like maltodextrin or invert syrup?"
    }
  ]
};
