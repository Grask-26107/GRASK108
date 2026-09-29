"""
Statutory Certificate & Licensing Master Registry (SIH26107)
Comprehensive statutory metadata for:
  - BIS Product Certification (ISI Mark Scheme-I)
  - BIS Compulsory Registration Scheme (CRS Scheme-II)
  - FSSAI Food Licensing (Basic Registration, State License, Central License)
  - MSME / Udyam Registration (50% Fee Concessions)
  - BEE Star Rating Certification (Energy Conservation)
  - EPR (Extended Producer Responsibility - CPCB)
  - BIS Gold Hallmarking (6-digit HUID)
  - AGMARK Agricultural Grading
"""

from typing import Dict, Any, List

CERTIFICATE_REGISTRY: Dict[str, Any] = {
    "BIS_ISI": {
        "id": "BIS_ISI",
        "name": "BIS ISI Mark (Product Certification Scheme-I)",
        "authority": "Bureau of Indian Standards (Ministry of Consumer Affairs)",
        "mandatory": True,
        "governing_law": "Bureau of Indian Standards Act, 2016 & Mandatory QCOs",
        "portal_name": "Manakonline",
        "portal_url": "https://www.manakonline.in",
        "statutory_form": "Form V (Application for Grant of Licence to use Standard Mark)",
        "base_application_fee": 1000,
        "inspection_fee_per_day": 7000,
        "concessions": {
            "micro_enterprise": 0.50,   # 50% discount on application & inspection
            "small_enterprise": 0.20,   # 20% discount
            "women_entrepreneur": 0.50, # 50% discount
            "dpiit_startup": 0.50       # 50% discount
        },
        "estimated_timeline": "30 to 60 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "Company PAN & Proof of Business Identity",
                "description": "Proprietorship PAN / Partnership Deed / Certificate of Incorporation (CIN).",
                "category": "legal",
                "weight": 10
            },
            {
                "id": "doc_factory_address",
                "name": "Factory Premises Ownership / Registered Lease",
                "description": "Valid sale deed, rent agreement with minimum 1-year validity, or industrial estate allotment letter.",
                "category": "legal",
                "weight": 10
            },
            {
                "id": "doc_electricity_bill",
                "name": "Industrial Electricity Bill & Sanctioned Load",
                "description": "Proof of active commercial/industrial 3-phase power connection supporting manufacturing machinery.",
                "category": "legal",
                "weight": 10
            },
            {
                "id": "doc_machinery_list",
                "name": "Manufacturing Machinery & Process Flow Chart",
                "description": "Complete inventory of installed machinery, manufacturer names, capacity, and production flow sheet.",
                "category": "technical",
                "weight": 15
            },
            {
                "id": "doc_inhouse_lab",
                "name": "In-House Testing Laboratory Equipment List",
                "description": "Mandatory testing apparatus required by the specific Indian Standard installed inside factory premises.",
                "category": "technical",
                "weight": 25,
                "is_critical_blocker": True
            },
            {
                "id": "doc_calib_certs",
                "name": "Calibration Certificates of Testing Instruments",
                "description": "Valid calibration from NABL-accredited external calibration laboratories for all in-house gauges and meters.",
                "category": "technical",
                "weight": 15
            },
            {
                "id": "doc_quality_personnel",
                "name": "Qualified Quality Control Chemist / Engineer",
                "description": "Appointment letter and degree certificates of full-time technical personnel managing quality control.",
                "category": "personnel",
                "weight": 15
            }
        ]
    },
    "BIS_CRS": {
        "id": "BIS_CRS",
        "name": "BIS Compulsory Registration Scheme (CRS - Scheme-II)",
        "authority": "BIS & Ministry of Electronics and Information Technology (MeitY)",
        "mandatory": True,
        "governing_law": "Electronics & IT Goods (Requirements for Compulsory Registration) Order",
        "portal_name": "BIS CRS Portal",
        "portal_url": "https://www.crsbis.in",
        "statutory_form": "Form VI (Self Declaration of Conformity - SDoC)",
        "base_application_fee": 53100,  # ₹45,000 + 18% GST
        "inspection_fee_per_day": 0,    # CRS requires no factory inspection upfront
        "concessions": {
            "micro_enterprise": 0.0,
            "small_enterprise": 0.0,
            "women_entrepreneur": 0.0,
            "dpiit_startup": 0.0
        },
        "estimated_timeline": "15 to 25 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "Company PAN & Proof of Business Identity",
                "description": "CIN, GSTIN, and Authorized Signatory Letter.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_factory_address",
                "name": "Manufacturing Facility Registration Proof",
                "description": "Factory license or registration in the country of origin.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_nabl_test_report",
                "name": "NABL Accredited In-Country Test Report",
                "description": "Test report from a BIS-recognized Indian laboratory issued within the last 90 days.",
                "category": "technical",
                "weight": 40,
                "is_critical_blocker": True
            },
            {
                "id": "doc_brand_trademark",
                "name": "Trademark Registration Certificate / Authorization",
                "description": "Proof of brand ownership or legal Brand Owner Authorization Letter.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_air_nomination",
                "name": "Authorized Indian Representative (AIR) Undertaking",
                "description": "Mandatory for foreign manufacturers appointing a local Indian entity.",
                "category": "legal",
                "weight": 15
            }
        ]
    },
    "FSSAI_STATE": {
        "id": "FSSAI_STATE",
        "name": "FSSAI State Food License",
        "authority": "Food Safety and Standards Authority of India (FSSAI)",
        "mandatory": True,
        "governing_law": "Food Safety and Standards Act, 2006 (Licensing & Registration Regulations)",
        "portal_name": "FoSCoS (Food Safety Compliance System)",
        "portal_url": "https://foscos.fssai.gov.in",
        "statutory_form": "Form B (Application for License under FSS Act)",
        "base_application_fee": 3000,
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "15 to 30 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "Photo ID and Address Proof of Proprietor/Partners",
                "description": "Aadhaar Card, Voter ID, or Passport.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_factory_address",
                "name": "Premises Proof (Rent Agreement / Electricity Bill)",
                "description": "Proof of possession of premises with NOC from landlord.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_fsms_plan",
                "name": "Food Safety Management System (FSMS) Plan",
                "description": "FSMS plan or certificate detailing hygiene, sanitization, and hazard control.",
                "category": "technical",
                "weight": 20
            },
            {
                "id": "doc_water_test",
                "name": "Water Potability Test Report (as per IS 10500)",
                "description": "Chemical and microbiological testing of source water used in food production.",
                "category": "technical",
                "weight": 25,
                "is_critical_blocker": True
            },
            {
                "id": "doc_machinery_list",
                "name": "List of Food Processing Equipment & Layout",
                "description": "Floor plan showing processing sections, equipment capacity, and horsepower.",
                "category": "technical",
                "weight": 15
            },
            {
                "id": "doc_fostac_cert",
                "name": "FoSTaC Certified Food Safety Supervisor",
                "description": "At least one trained Food Safety Supervisor certified under FSSAI FoSTaC scheme.",
                "category": "personnel",
                "weight": 10
            }
        ]
    },
    "FSSAI_BASIC": {
        "id": "FSSAI_BASIC",
        "name": "FSSAI Basic Registration",
        "authority": "Food Safety and Standards Authority of India (FSSAI)",
        "mandatory": True,
        "governing_law": "Food Safety and Standards Act, 2006",
        "portal_name": "FoSCoS",
        "portal_url": "https://foscos.fssai.gov.in",
        "statutory_form": "Form A (Application for Registration under FSS Act)",
        "base_application_fee": 100,
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "7 to 14 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "Photo ID and Passport Photo of Applicant",
                "description": "Aadhaar Card, PAN card, or Voter ID.",
                "category": "legal",
                "weight": 40
            },
            {
                "id": "doc_factory_address",
                "name": "Business Address Proof",
                "description": "Electricity bill, shop lease, or municipal trade license.",
                "category": "legal",
                "weight": 35
            },
            {
                "id": "doc_declaration",
                "name": "Basic Hygiene & Sanitation Declaration",
                "description": "Signed declaration confirming clean water, covered food bins, and pest control.",
                "category": "technical",
                "weight": 25
            }
        ]
    },
    "FSSAI_CENTRAL": {
        "id": "FSSAI_CENTRAL",
        "name": "FSSAI Central Food License",
        "authority": "FSSAI Central Licensing Authority",
        "mandatory": True,
        "governing_law": "Food Safety and Standards Act, 2006",
        "portal_name": "FoSCoS",
        "portal_url": "https://foscos.fssai.gov.in",
        "statutory_form": "Form B (Central License Application)",
        "base_application_fee": 7500,
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "30 to 45 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "CIN, GSTIN, and IE Code (for Importers/Exporters)",
                "description": "Central corporate and tax credentials.",
                "category": "legal",
                "weight": 15
            },
            {
                "id": "doc_water_test",
                "name": "Comprehensive IS 10500 Potability Report",
                "description": "Testing by NABL accredited lab for all 42 physicochemical and microbiological parameters.",
                "category": "technical",
                "weight": 25,
                "is_critical_blocker": True
            },
            {
                "id": "doc_fsms_plan",
                "name": "ISO 22000 / HACCP / Advanced FSMS Documentation",
                "description": "Formal food safety certification or audited risk assessment.",
                "category": "technical",
                "weight": 20
            },
            {
                "id": "doc_machinery_list",
                "name": "Engineered Plant Layout & Equipment Specifications",
                "description": "Production flow, installed horsepower, hygiene barrier zoning.",
                "category": "technical",
                "weight": 20
            },
            {
                "id": "doc_quality_personnel",
                "name": "Designated Technical Officer / Food Technologist",
                "description": "Full-time degree holder in Food Technology / Dairy Science / Chemistry.",
                "category": "personnel",
                "weight": 20
            }
        ]
    },
    "UDYAM": {
        "id": "UDYAM",
        "name": "Udyam MSME Registration Certificate",
        "authority": "Ministry of Micro, Small and Medium Enterprises",
        "mandatory": False,
        "is_enabler": True,
        "governing_law": "Micro, Small and Medium Enterprises Development Act, 2006",
        "portal_name": "Udyam Registration Portal",
        "portal_url": "https://udyamregistration.gov.in",
        "statutory_form": "Online Paperless Self-Declaration Form",
        "base_application_fee": 0,  # 100% FREE OFFICIAL GOVT SERVICE
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "1 to 3 Days (Instant QR e-Certificate)",
        "mandatory_prerequisites": [
            {
                "id": "doc_aadhaar",
                "name": "Applicant Aadhaar Number linked with Mobile OTP",
                "description": "Proprietor / Managing Partner / Director Aadhaar.",
                "category": "legal",
                "weight": 40
            },
            {
                "id": "doc_pan",
                "name": "Enterprise / Proprietor PAN",
                "description": "Validated automatically against Income Tax CBDT database.",
                "category": "legal",
                "weight": 30
            },
            {
                "id": "doc_gstin",
                "name": "GSTIN (Exempt for micro enterprises with turnover < ₹20L/₹40L)",
                "description": "Goods and Services Tax Identification Number if registered.",
                "category": "legal",
                "weight": 30
            }
        ]
    },
    "BEE_STAR": {
        "id": "BEE_STAR",
        "name": "BEE Star Labeling Certification (Energy Conservation)",
        "authority": "Bureau of Energy Efficiency (Ministry of Power)",
        "mandatory": True,
        "governing_law": "Energy Conservation Act, 2001 (Mandatory Star Labeling Regulations)",
        "portal_name": "BEE Star Labeling Portal",
        "portal_url": "https://www.beestarlabel.com",
        "statutory_form": "Schedule Registration & Model Approval Form",
        "base_application_fee": 20000,
        "inspection_fee_per_day": 0,
        "concessions": {
            "micro_enterprise": 0.50,
            "small_enterprise": 0.50
        },
        "estimated_timeline": "20 to 40 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_bis_license",
                "name": "Valid BIS ISI License / CRS Registration",
                "description": "Prerequisite electrical safety license under Bureau of Indian Standards.",
                "category": "legal",
                "weight": 30,
                "is_critical_blocker": True
            },
            {
                "id": "doc_energy_test_report",
                "name": "NABL Energy Consumption Test Report",
                "description": "Independent laboratory testing verifying Star Rating kWh energy efficiency bounds.",
                "category": "technical",
                "weight": 40,
                "is_critical_blocker": True
            },
            {
                "id": "doc_label_sample",
                "name": "Sample Star Label Artwork & Color Specimen",
                "description": "Proof of label complying with BEE graphic guidelines and dimensions.",
                "category": "technical",
                "weight": 15
            },
            {
                "id": "doc_company_auth",
                "name": "Board Resolution & Authorized Signatory ID",
                "description": "Authorization letter for BEE portal nodal officer.",
                "category": "legal",
                "weight": 15
            }
        ]
    },
    "EPR_CPCB": {
        "id": "EPR_CPCB",
        "name": "Extended Producer Responsibility (EPR) Registration",
        "authority": "Central Pollution Control Board (CPCB) & SPCB",
        "mandatory": True,
        "governing_law": "Plastic Waste Management Rules / E-Waste Management Rules",
        "portal_name": "CPCB EPR Portal",
        "portal_url": "https://eprplastic.cpcb.gov.in",
        "statutory_form": "Form I (Producer / Importer / Brand Owner Registration)",
        "base_application_fee": 10000,
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "15 to 30 Days",
        "mandatory_prerequisites": [
            {
                "id": "doc_spcb_cto",
                "name": "State Pollution Control Board Consent to Operate (CTO)",
                "description": "Valid CTO under Air & Water Pollution Control Acts.",
                "category": "legal",
                "weight": 35,
                "is_critical_blocker": True
            },
            {
                "id": "doc_plastic_data",
                "name": "Annual Plastic / E-Waste Packaging Quantification",
                "description": "Audited quantity of Cat-I, Cat-II, Cat-III plastics introduced into the market.",
                "category": "technical",
                "weight": 35
            },
            {
                "id": "doc_recycler_agreement",
                "name": "Agreement with Registered Recycler / PRO",
                "description": "Memorandum of Understanding with certified waste processing partners.",
                "category": "technical",
                "weight": 30
            }
        ]
    },
    "BIS_HALLMARK": {
        "id": "BIS_HALLMARK",
        "name": "BIS Gold & Silver Hallmarking Registration (HUID)",
        "authority": "Bureau of Indian Standards (Hallmarking Directorate)",
        "mandatory": True,
        "governing_law": "Hallmarking of Gold & Silver Artefacts Order, 2020",
        "portal_name": "Manakonline",
        "portal_url": "https://www.manakonline.in",
        "statutory_form": "Online Application for Grant of Registration to Jewellers",
        "base_application_fee": 0,  # Zero fee for micro jewelers in rural districts under MSME
        "inspection_fee_per_day": 0,
        "concessions": {},
        "estimated_timeline": "1 to 5 Days (Instant Online Grant)",
        "mandatory_prerequisites": [
            {
                "id": "doc_identity_pan",
                "name": "Jeweller PAN & Proof of Business Formation",
                "description": "Proprietorship PAN, GST registration, or Trade License.",
                "category": "legal",
                "weight": 35
            },
            {
                "id": "doc_factory_address",
                "name": "Jewellery Showroom / Workshop Address Proof",
                "description": "Electricity bill, lease agreement, or municipality license.",
                "category": "legal",
                "weight": 35
            },
            {
                "id": "doc_turnover_proof",
                "name": "CA Certificate of Annual Turnover / GST Return",
                "description": "Determines fee slab waiver.",
                "category": "legal",
                "weight": 30
            }
        ]
    }
}


# Pre-mapped standard product profiles with specific testing equipment and required certificates
PRODUCT_PROFILES: Dict[str, Any] = {
    "packaged_drinking_water": {
        "id": "packaged_drinking_water",
        "title": "Packaged Drinking Water (Other than Natural Mineral Water)",
        "is_code": "IS 14543:2018",
        "department": "Food & Agriculture (FAD)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "FSSAI_STATE", "UDYAM"],
        "aliases": [
            "packaged drinking water", "ro water", "bislery", "bisleri", "ro watur",
            "drinking water", "water bottle", "water can", "20 litre jar", "20l water",
            "water plant", "pani plant", "bottled water", "water treatment plant",
            "ro mineral water", "jar water", "drinking water plant"
        ],
        "inhouse_lab_equipment": [
            "pH Meter (Accuracy ±0.01 pH with buffer calibration)",
            "Conductivity / Total Dissolved Solids (TDS) Meter",
            "Turbidity Meter (Nephelometric Turbidity Unit - NTU)",
            "Autoclave (Vertical steam sterilizer for microbiological media, 121°C)",
            "Bacteriological Incubator (37°C ± 0.5°C for coliform/E. coli detection)",
            "Laminar Air Flow Clean Bench (Class 100 for sterile microbial inoculation)",
            "Membrane Filtration Apparatus (with 0.45 micron sterile cellulose grid filters)",
            "Colony Counter (Digital with illuminated magnifying viewer)",
            "Spectrophotometer / Colorimeter (for Nitrate, Sulphate, Fluoride testing)"
        ],
        "crucial_warnings": [
            "Raw source water must be tested for toxic heavy metals (Lead, Arsenic, Cadmium) before commencing commercial bottling.",
            "IS 14543 strictly mandates an in-house microbiological laboratory inside the plant boundary. External lab contracts are NOT permitted for daily batch release.",
            "Bottling line must have automated filling and capping inside a positive-pressure HEPA filtered clean room."
        ]
    },
    "natural_mineral_water": {
        "id": "natural_mineral_water",
        "title": "Natural Mineral Water (Spring / Artesian Source)",
        "is_code": "IS 13428:2017",
        "department": "Food & Agriculture (FAD)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "FSSAI_CENTRAL", "UDYAM"],
        "aliases": [
            "natural mineral water", "spring water", "mountain water", "artesian water",
            "himalayan water", "natural spring"
        ],
        "inhouse_lab_equipment": [
            "High Precision Inductively Coupled Plasma (ICP) or AAS for trace minerals",
            "Microbiological Testing Suite (Aerobic microbial count, Pseudomonas aeruginosa)",
            "Total Organic Carbon (TOC) Analyzer",
            "Conductivity Meter and Digital pH Station",
            "Class 100 Laminar Clean Air Cabinet"
        ],
        "crucial_warnings": [
            "Natural Mineral Water cannot undergo RO demineralization or chemical addition. It must be packaged directly at source.",
            "Requires central FSSAI license irrespective of turnover if marketed inter-state."
        ]
    },
    "tmt_steel_bars": {
        "id": "tmt_steel_bars",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement (TMT)",
        "is_code": "IS 1786:2008",
        "department": "Metallurgical Engineering (MED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "EPR_CPCB", "UDYAM"],
        "aliases": [
            "tmt steel", "tmt bar", "tmt sariya", "sariya", "steel rod", "reinforcement steel",
            "fe 500", "fe 500d", "fe 550", "steel rebar", "tata tiscon", "jindal steel",
            "construction rod", "concrete steel"
        ],
        "inhouse_lab_equipment": [
            "Universal Testing Machine (UTM - minimum 1000 kN capacity with electronic extensometer)",
            "Mandrel Cold Bend and Rebend Testing Apparatus (Mandrel diameters as per Clause 9.4)",
            "Optical Emission Spectrometer (OES for Carbon, Sulphur, Phosphorus, CE calculation)",
            "Weight per Metre Balance (Analytical balance with ±0.5% resolution)",
            "Surface Rib Geometry Measuring Caliper & Depth Micrometer"
        ],
        "crucial_warnings": [
            "QCO mandates that no steel rolling mill can produce or dispatch TMT rebars without an active ISI CM/L license.",
            "Yield strength (0.2% proof stress), Ultimate Tensile Strength (UTS), and elongation must be tested on every individual cast/heat."
        ]
    },
    "protective_helmets": {
        "id": "protective_helmets",
        "title": "Protective Helmets for Two-Wheeler Riders",
        "is_code": "IS 4151:2015",
        "department": "Transport Engineering (TED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "UDYAM"],
        "aliases": [
            "protective helmet", "helmet", "two wheeler helmet", "bike helmet", "motorcycle helmet",
            "healmet", "helment", "studds", "vega", "steelbird", "riding helmet"
        ],
        "inhouse_lab_equipment": [
            "Impact Absorption Test Rig with Triaxial Accelerometer and Guided Drop Carriage",
            "Dynamic Retention System Test Apparatus (Chin strap stretch and release)",
            "Audibility Test Chamber and Acoustic Measuring Apparatus",
            "Peripheral Vision Aperture Protractor Rig",
            "Climatic Conditioning Chambers (-10°C cold, +50°C heat, water immersion)"
        ],
        "crucial_warnings": [
            "Sale of non-ISI certified two-wheeler helmets is a punishable criminal offense under the Motor Vehicles Act & BIS Act.",
            "Maximum weight of motorcycle helmet cannot exceed 1.5 kg under IS 4151:2015."
        ]
    },
    "portland_cement": {
        "id": "portland_cement",
        "title": "Ordinary Portland Cement (33, 43, and 53 Grade) & PPC",
        "is_code": "IS 269:2015 / IS 1489:2015",
        "department": "Civil Engineering (CED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "EPR_CPCB", "UDYAM"],
        "aliases": [
            "cement", "opc", "ppc", "portland cement", "opc 53", "opc 43",
            "ultratech cement", "ambuja cement", "cement plant", "clinker"
        ],
        "inhouse_lab_equipment": [
            "Compression Testing Machine (CTM - 2000 kN with pacing rate controller)",
            "Vicat Apparatus with needles and plunger for Consistency and Setting Time",
            "Le-Chatelier Flask and Water Bath for Soundness by Expansion",
            "Blaine's Air Permeability Apparatus for Specific Surface (Fineness)",
            "Standard Vibration Machine with Mortar Cube Moulds (70.6 mm)"
        ],
        "crucial_warnings": [
            "Cement is under strict 100% mandatory QCO. Mandatory sampling from clinker blending silo to final packed bags."
        ]
    },
    "led_lighting": {
        "id": "led_lighting",
        "title": "Self-Ballasted LED Lamps & Controlgear for General Lighting Services",
        "is_code": "IS 16102 (Part 1 & 2):2012",
        "department": "Electronics & Information Technology (LITD)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_CRS", "BEE_STAR", "EPR_CPCB", "UDYAM"],
        "aliases": [
            "led lamp", "led bulb", "led bulp", "led lighting", "downlight", "led light",
            "9w led", "syska", "philips led", "emergency led", "street light led"
        ],
        "inhouse_lab_equipment": [
            "Integrating Sphere with Photometer / Spectroradiometer for Lumens and CCT",
            "High Voltage Insulation Tester (Dielectric Breakdown / Hipot)",
            "Digital Power Analyzer (Measuring Watts, Power Factor, THD)",
            "Endurance and Accelerated Ageing Test Rack",
            "Glow Wire Testing Apparatus"
        ],
        "crucial_warnings": [
            "Must register under BIS CRS (Compulsory Registration Scheme) via MeitY.",
            "Energy Star labeling is mandatory under BEE for self-ballasted lamps."
        ]
    },
    "domestic_gas_stoves": {
        "id": "domestic_gas_stoves",
        "title": "Domestic Gas Stoves for use with Liquefied Petroleum Gases (LPG)",
        "is_code": "IS 4246:2002",
        "department": "Mechanical Engineering (MED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "UDYAM"],
        "aliases": [
            "gas stove", "lpg stove", "chulha", "gas chulha", "domestic gas stove",
            "prestige stove", "burner stove", "glass top stove"
        ],
        "inhouse_lab_equipment": [
            "Gas Leakage Testing Rig with Digital Pressure Gauge (150 mbar proof)",
            "Thermal Efficiency Test Rig with Calibrated Vessels and Thermocouples",
            "Flame Stability and Flashback Testing Apparatus",
            "Carbon Monoxide / Carbon Dioxide Ratio Emission Hood",
            "Surface Temperature Probes for Knobs and Body Panels"
        ],
        "crucial_warnings": [
            "Thermal efficiency must be minimum 68% as per Bureau of Indian Standards statutory regulations."
        ]
    },
    "hdpe_pipes": {
        "id": "hdpe_pipes",
        "title": "Polyethylene Pipes for Water Supply (HDPE Pipes)",
        "is_code": "IS 4984:2016",
        "department": "Civil Engineering (CED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "EPR_CPCB", "UDYAM"],
        "aliases": [
            "hdpe pipe", "hdpe pipes", "plastic pipe", "plasstic pip", "borewell pipe",
            "submersible pipe", "irrigation pipe", "drip pipe", "polyethylene pipe", "pe 100"
        ],
        "inhouse_lab_equipment": [
            "Hydrostatic Pressure Testing Tank with Multi-Station End Caps (80°C & 27°C)",
            "Melt Flow Index (MFI) Apparatus with Automatic Extrusion Cutter",
            "Carbon Black Content Apparatus (Muffle Furnace with Nitrogen purge)",
            "Carbon Black Dispersion Microscope with Photomicrography Rig",
            "Digital Wall Thickness Ultrasonic Gauge and Vernier Calipers"
        ],
        "crucial_warnings": [
            "Use of recycled / reground plastic scraps is strictly prohibited for drinking water grade PE pipes under IS 4984."
        ]
    },
    "food_processing_bakery": {
        "id": "food_processing_bakery",
        "title": "Packaged Bakery, Snacks, Grain Milling & Processed Foods",
        "is_code": "FSSAI Regulations / IS 1483 / IS 1008",
        "department": "Food Safety & Standards (FSSAI)",
        "mandatory_qco": True,
        "required_certificates": ["FSSAI_STATE", "UDYAM"],
        "aliases": [
            "bakery", "bread", "biscuits", "namkeen", "snack manufacturing", "flour mill",
            "atta chakki", "atta chaki", "chawal mill", "rice mill", "spice mill",
            "packaged food", "food processing", "chips manufacturing"
        ],
        "inhouse_lab_equipment": [
            "Moisture Balance / Halogen Moisture Analyzer",
            "Digital Weighing Balance (0.001g precision)",
            "pH & Total Acidity Titration Bench",
            "Oil Rancidity / Peroxide Value Testing Kit (for fried snacks)",
            "Pest and Foreign Matter Inspection Light Box"
        ],
        "crucial_warnings": [
            "Mandatory FSSAI FoSCoS state or central license required depending on production capacity (over 1 MT/day requires State License).",
            "Nutritional panel and allergen warnings must comply with FSSAI (Labeling and Display) Regulations 2020."
        ]
    },
    "dairy_milk_processing": {
        "id": "dairy_milk_processing",
        "title": "Dairy Processing, Milk Chilling, Paneer, Curd & Ghee",
        "is_code": "FSSAI Dairy Standards / IS 13688 / IS 1165",
        "department": "Food Safety & Standards (FSSAI)",
        "mandatory_qco": True,
        "required_certificates": ["FSSAI_STATE", "UDYAM"],
        "aliases": [
            "dairy", "milk dairy", "doodh", "paneer", "curd", "ghee", "paala dukanam",
            "milk processing", "dairy plant", "butter", "ice cream"
        ],
        "inhouse_lab_equipment": [
            "Milk Analyzer (Ultrasonic fat, SNF, protein, added water detection)",
            "Lactometer and Temperature-Controlled Water Bath",
            "Methylene Blue Reduction Test (MBRT) Apparatus for Microbial Quality",
            "Adulteration Chemical Test Kits (Detergent, Urea, Starch, Neutralizer detection)",
            "Autoclave and Bacteriological Incubator"
        ],
        "crucial_warnings": [
            "Milk collection centers handling over 500 liters/day require mandatory FoSCoS registration/license.",
            "Raw milk chilling must achieve below 4°C within 3 hours of collection."
        ]
    },
    "gold_jewellery": {
        "id": "gold_jewellery",
        "title": "Gold & Silver Jewellery Hallmarking (6-Digit HUID)",
        "is_code": "IS 1417:2016",
        "department": "Hallmarking Directorate (BIS)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_HALLMARK", "UDYAM"],
        "aliases": [
            "gold shop", "jeweller", "jewellery", "sona chandi", "gold ornaments",
            "huid", "hallmark shop", "silver jewellery", "gold retailer"
        ],
        "inhouse_lab_equipment": [
            "Electronic High Precision Carat Balance (0.001g resolution)",
            "Optical Magnifier / Stereo Microscope (minimum 10X for HUID laser mark reading)",
            "Assaying touchstone with certified testing nitric acids",
            "Secure Computer with BIS Manakonline HUID Integration Portal"
        ],
        "crucial_warnings": [
            "Selling un-hallmarked gold jewellery of 14k, 18k, 20k, 22k, 23k, 24k is illegal in designated districts.",
            "Registration is 100% online with lifetime validity and zero inspection fee for micro MSMEs."
        ]
    },
    "paper_industry": {
        "id": "paper_industry",
        "title": "Writing and Printing Paper, Kraft Paper & Packaging Board",
        "is_code": "IS 1848:2018 / IS 1397:2020",
        "department": "Chemical & Forest Products (CHD)",
        "mandatory_qco": False,
        "required_certificates": ["BIS_ISI", "EPR_CPCB", "UDYAM"],
        "aliases": [
            "paper industry", "paper", "paper mill", "paper manufacturing", "kraft paper",
            "copier paper", "a4 paper", "kaghaz", "packaging board", "corrugated box",
            "cardboard", "paper plant", "tissue paper", "paper plate raw material"
        ],
        "inhouse_lab_equipment": [
            "Grammage (GSM) Electronic Balance (0.01g resolution with standard round template cutter)",
            "Bursting Strength Tester (Mullen hydraulic diaphragm tester)",
            "Cobb Sizing Tester (Water absorption measurement for 60 seconds)",
            "Paper Tensile Strength Tester (Electronic with elongation sensor)",
            "Smoothness and Porosity Tester (Bendtsen or Sheffield standard method)",
            "Rapid Halogen Moisture Analyzer / Air Circulating Drying Oven",
            "Tearing Resistance Tester (Elmendorf pendulum apparatus)",
            "Digital Thickness Caliper / Micrometer (0.001 mm resolution)"
        ],
        "crucial_warnings": [
            "Effluent discharge must strictly adhere to State Pollution Control Board (SPCB) Consent to Operate (CTO).",
            "Corrugated paper and kraft packaging require EPR registration for post-consumer waste recovery under CPCB rules."
        ]
    },
    "books_and_stationery": {
        "id": "books_and_stationery",
        "title": "Exercise Books, Note Books, Student Stationery & Educational Printing",
        "is_code": "IS 11015:2018 / IS 1848:2018",
        "department": "Paper, Stationery & Forest Products (CHD)",
        "mandatory_qco": False,
        "required_certificates": ["EPR_CPCB", "UDYAM"],
        "aliases": [
            "books or notes industry", "notes industry", "books industry", "notebooks",
            "notebook", "exercise books", "note book", "books", "notes", "stationery",
            "school notebooks", "pustakalu", "kithaben", "printing and publishing",
            "book binding", "register notebooks", "office stationery", "ruled paper"
        ],
        "inhouse_lab_equipment": [
            "Paper Grammage (GSM) Electronic Precision Scale",
            "Digital Thickness Micrometer for Sheet & Board Caliper",
            "Binding Page Pull and Spine Flexibility Tester",
            "Ruling Alignment and Margin Spacing Optical Gauge",
            "Cover Board Rigidity & Folding Endurance Tester"
        ],
        "crucial_warnings": [
            "Educational student notebooks must use chlorine-free or elemental chlorine-free (ECF) paper meeting IS 1848 brightness bounds.",
            "Plastic lamination on book covers introduces plastic waste obligations under CPCB Extended Producer Responsibility (EPR)."
        ]
    },
    "footwear_industry": {
        "id": "footwear_industry",
        "title": "Footwear, Leather Shoes & Industrial Protective Safety Shoes",
        "is_code": "IS 15844:2010 / IS 15298:2016",
        "department": "Chemical & Leather Engineering (CHD)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "UDYAM"],
        "aliases": [
            "footwear", "shoes", "leather shoes", "safety shoes", "chappal", "sandals",
            "joota", "footwear factory", "shoe manufacturing"
        ],
        "inhouse_lab_equipment": [
            "Impact Resistance Testing Machine for Safety Toe-Caps (200 Joules drop)",
            "Upper Sole Adhesion and Bond Peel Strength Tester",
            "Flexing Endurance Tester (Ross flexing / Bally flexometer for leather)",
            "Abrasion Resistance Tester for Soles (DIN or Rotary drum method)",
            "Electrical Resistance Testing Rig for Anti-Static / Conducting Footwear"
        ],
        "crucial_warnings": [
            "Footwear is under 100% Mandatory QCO by DPIIT. Non-ISI footwear cannot be sold in Indian retail.",
            "Must pass 200J steel toe impact test for industrial safety category."
        ]
    },
    "electric_cables_wires": {
        "id": "electric_cables_wires",
        "title": "PVC Insulated Electrical Cables & Flexible Wires for Working Voltages up to 1100V",
        "is_code": "IS 694:2010",
        "department": "Electrotechnical (ETD)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "UDYAM"],
        "aliases": [
            "electric wire", "cables", "copper wire", "pvc cable", "wiring", "havells wire",
            "electrical wire", "flexible wire", "house wiring"
        ],
        "inhouse_lab_equipment": [
            "Kelvin Double Bridge / Digital Micro-Ohmmeter for Conductor Resistance",
            "High Voltage Spark Tester (Inline for continuous insulation testing)",
            "Insulation Resistance Water Bath with Megohmmeter (at 60°C)",
            "Tensile & Elongation Testing Rig with Dumbbell Cutting Dies",
            "Flammability and Oxygen Index Testing Chamber"
        ],
        "crucial_warnings": [
            "Mandatory QCO in force. Copper purity must be minimum 99.9% electrolytic grade (ETP).",
            "Must pass spark test at 6kV to prevent electrical fire hazards in buildings."
        ]
    },
    "safety_toys": {
        "id": "safety_toys",
        "title": "Safety of Toys (Mechanical, Physical & Chemical Safety)",
        "is_code": "IS 9873 (Part 1-9):2019",
        "department": "Mechanical & Consumer Products (MED)",
        "mandatory_qco": True,
        "required_certificates": ["BIS_ISI", "UDYAM"],
        "aliases": [
            "toys", "plastic toys", "kids toys", "electronic toys", "toy factory",
            "khilone", "wooden toys", "plush toys"
        ],
        "inhouse_lab_equipment": [
            "Small Parts Cylinder (for choking hazard detection under 3 years)",
            "Sharp Edge and Sharp Point Testing Rig",
            "Tension, Compression, and Torsion Force Gauges for Component Pull",
            "Drop Impact Test Rig on Standard Steel Plate",
            "XRF Spectrometer for Phthalates and Toxic Heavy Metals (Lead, Cadmium)"
        ],
        "crucial_warnings": [
            "DPIIT Quality Control Order: Zero toys can be manufactured or imported without valid BIS ISI certification.",
            "Strict zero-tolerance on toxic phthalates, sharp burrs, and detachable small parts."
        ]
    }
}
