"""
NLP Query Normalization, Intent & Entity Extraction Engine (NLPQueryProcessor)
Part of GRASK AI (SIH26107).
Handles:
- Informal, ungrammatical, typo-laden, or colloquial user queries
- Short (1-2 word) query expansion (e.g., 'gold', 'huid', 'packaged water', 'fe 500d', 'cement', 'solar', 'fssai')
- Complex mixed questions spanning multiple topics
- Domain intent classification across all 8 BIS + FSSAI pillars
- Multilingual and code-mixed (Hinglish/Tanglish/Telugish) entity recognition
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Common typos and phonetic colloquialisms mapped to standard canonical terms
TYPO_CORRECTION_MAP = {
    # Food & Water
    "watr": "water", "pakaged": "packaged", "packeged": "packaged", "pakage": "package",
    "drnkng": "drinking", "paani": "packaged drinking water",
    "bislari": "packaged drinking water", "bisleri": "packaged drinking water", "aquafina": "packaged drinking water",
    "kinley": "packaged drinking water", "mineral watr": "mineral water",
    # Gold & Hallmarking
    "holmark": "hallmarking", "halmark": "hallmarking", "hallmrak": "hallmarking",
    "huid": "hallmark unique identification huid", "sona": "gold hallmarking",
    "chandi": "silver hallmarking", "jewellery": "gold jewellery hallmarking",
    "jewelery": "gold jewellery hallmarking", "karat": "carat purity", "krt": "carat",
    "22k": "22 karat 916 gold purity", "24k": "24 karat 999 gold purity", "18k": "18 karat 750 gold purity",
    # Steel & Construction
    "tmt": "tmt steel bars is 1786", "sariya": "tmt steel rebars is 1786", "stele": "steel",
    "fe500": "fe 500d tmt steel", "fe500d": "fe 500d tmt steel is 1786", "fe 500": "fe 500d tmt steel",
    "sement": "cement is 269", "cemnt": "cement", "conkreet": "concrete",
    # Electrical & Safety
    "plg": "plugs and sockets is 1293", "soket": "plugs and sockets is 1293", "sokt": "socket",
    "helmit": "two wheeler helmet is 4151", "helmt": "two wheeler helmet is 4151", "hlmet": "helmet",
    # FSSAI & Food
    "fsai": "fssai", "fssi": "fssai", "fssay": "fssai", "foscos": "fssai foscos licensing",
    "foskos": "fssai foscos", "adulterashun": "food adulteration", "adulterat": "adulteration",
    "milkk": "milk", "doodh": "milk safety", "honie": "honey", "tel": "edible cooking oil",
    "panneer": "paneer", "panner": "paneer", "paneeer": "paneer", "subzi": "vegetables",
    "sabzi": "vegetables", "khana": "food safety", "eatting": "eating",
    # Certification & Schemes
    "lisence": "license", "licence": "license", "certficate": "certification", "certificat": "certification",
    "regstr": "registration", "registrashun": "registration", "manak": "manakonline portal",
    "manak online": "manakonline", "crs": "compulsory registration scheme crs",
    "fmcs": "foreign manufacturers certification scheme fmcs", "isi": "isi mark certification",
    # Labs & Testing
    "labratory": "laboratory", "labortory": "laboratory", "nabl": "nabl accredited testing lab",
    "tsting": "testing", "cheking": "testing and verification",
    # Consumer
    "fak": "counterfeit fake", "orignal": "authentic genuine", "cmplaint": "complaint grievance 1915",
    "hepl": "help", "pliz": "please", "plz": "please", "nded": "needed", "wnt": "want", "mke": "make"
}

# Extensive Phonetic Romanized Indian Lexicon (Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali)
ROMANIZED_INDIAN_PHONETIC_MAP = {
    # 1. Food, Dairy & Beverages
    "paala": "milk", "paalu": "milk", "pala": "milk", "paal": "milk", "haalu": "milk",
    "doodh": "milk", "dudh": "milk", "dugdha": "milk", "khoya": "mawa milk solid",
    "perugu": "curd", "thayir": "curd", "dahi": "curd", "mosaru": "curd",
    "majiga": "buttermilk", "chaas": "buttermilk", "lassi": "buttermilk beverage",
    "neyyi": "ghee", "thuppa": "ghee", "nei": "ghee", "venna": "butter", "benne": "butter",
    "nune": "edible oil", "tel": "edible oil", "ennai": "edible oil", "yenne": "edible oil",
    "miriyalu": "black pepper", "pasupu": "turmeric", "haldi": "turmeric", "manjal": "turmeric",
    "mirchi": "red chilli", "milagu": "black pepper", "bellam": "jaggery", "gud": "jaggery",
    "annam": "cooked food", "bhojanam": "meal food", "khana": "food meal", "saapadu": "food meal",
    "mithai": "sweets", "mithayilu": "sweets", "laddu": "sweets", "barfi": "sweets",
    
    # 2. Store, Shop, Trade & Business
    "dukanam": "shop store", "dukan": "shop store", "dukaanam": "shop store",
    "kadai": "shop store", "angadi": "shop store", "kendra": "center shop",
    "vyaparam": "business trade", "vyapar": "business trade", "dhandha": "business enterprise",
    "hotel": "restaurant food eatery", "dhaba": "roadside restaurant food eatery",
    "bhojanalaya": "restaurant food eatery", "mess": "canteen food eatery",
    
    # 3. Water & Potable Quality
    "neeru": "drinking water", "neellu": "drinking water", "manchineellu": "drinking water",
    "paani": "drinking water", "thanneer": "drinking water",
    "kudineer": "drinking water", "vellam": "drinking water", "jal": "drinking water",
    
    # 4. Gold, Silver & Precious Metals
    "bangaaram": "gold jewellery hallmarking", "bangaram": "gold jewellery hallmarking",
    "thangam": "gold jewellery hallmarking", "chinna": "gold jewellery hallmarking",
    "sona": "gold hallmarking", "swarna": "gold hallmarking", "nagalu": "jewellery ornaments",
    "gahne": "jewellery ornaments", "vendi": "silver hallmarking", "chandi": "silver hallmarking",
    "belli": "silver hallmarking", "velli": "silver hallmarking",
    
    # 5. Construction, Steel, Cement & Bricks
    "inumu": "tmt steel rebar", "sariya": "tmt steel rebar is 1786", "loha": "iron steel",
    "irumbu": "iron steel rebar", "kabbina": "iron steel rebar", "kambi": "steel rebar rod",
    "simantu": "cement is 269", "siminti": "cement is 269", "cementu": "cement",
    "isuka": "construction sand", "manal": "construction sand", "ret": "construction sand",
    "baalu": "construction sand", "matti": "soil clay", "mitti": "soil clay",
    "itukalu": "building bricks", "eent": "building bricks", "sengal": "building bricks",
    "dhalai": "concrete slab casting is 456",
    
    # 6. Electrical & Safety
    "theega": "electrical wire is 694", "taar": "electrical wire is 694",
    "poyi": "gas stove is 4246", "chulha": "domestic gas stove is 4246",
    
    # 7. Legal, Administrative & Consumer
    "laisen": "license", "laicence": "license", "parvana": "license permit",
    "darakhastu": "application", "arji": "application", "vinnappam": "application",

    # 8. Timber, Woodwork & Carpentry
    "chekka": "timber wood", "chekkapani": "carpentry woodwork",
    "lakdi": "timber wood", "badhai": "carpentry woodwork", "tarkhan": "carpentry woodwork",
    "maram": "timber wood", "maravelai": "carpentry woodwork", "kammari": "craft work",
    "rangu": "paint wall coating", "rangupani": "house painting enamel", "rangulu": "paints colors",
    "shikayat": "complaint grievance 1915", "pugaar": "complaint grievance 1915",
    "duru": "complaint grievance 1915", "ekkuva": "extra excess above mrp",
    "zyada": "extra excess above mrp", "kooduthal": "extra excess above mrp",

    # 8. Vegetables, Fruits & Fresh Produce (ALL regional languages)
    # Telugu
    "kuragayalu": "vegetables fresh produce", "kuragaya": "vegetables",
    "kuragayala": "vegetables", "kooragayalu": "vegetables fresh produce",
    "aakukoora": "leafy vegetables", "palakura": "spinach leafy vegetable",
    "tomato": "tomato fresh produce", "vankaya": "brinjal eggplant", "bendi": "okra bhindi",
    "carrot": "carrot vegetable", "beerakaya": "ridge gourd vegetable",
    "dosakaya": "cucumber vegetable", "gongura": "sorrel leafy vegetable",
    "munagakaya": "drumstick vegetable", "aratikaya": "raw banana plantain",
    # Hindi / North Indian
    "sabzi": "vegetables fresh produce", "sabji": "vegetables",
    "subzi": "vegetables fresh produce", "hari sabzi": "green vegetables",
    "palak": "spinach leafy vegetable", "methi": "fenugreek leafy vegetable",
    "bhindi": "okra vegetable", "baingan": "brinjal eggplant", "aloo": "potato vegetable",
    "pyaaz": "onion vegetable", "tamatar": "tomato fresh produce",
    "shimla mirch": "capsicum bell pepper", "gobhi": "cauliflower vegetable",
    "matar": "peas vegetable", "mooli": "radish vegetable",
    "fal": "fruits fresh produce", "phal": "fruits fresh produce",
    # Tamil
    "kaaikari": "vegetables", "keerai": "leafy vegetables spinach",
    "thakkali": "tomato", "kathirikkai": "brinjal",
    "vendaikkai": "okra bhindi", "peerkangai": "ridge gourd",
    # Kannada
    "tarkari": "vegetables fresh produce", "soppu": "leafy vegetables",
    "saaru": "curry vegetables", "menasina": "pepper",

    # 9. Market, Stall, Shop types
    "kottu": "market stall shop", "kotta": "market stall",
    "sante": "weekly market bazaar", "shandy": "weekly market bazaar",
    "bazaar": "market bazaar", "bazar": "market bazaar",
    "mandi": "wholesale market bazaar vegetables",
    "rythu bazaar": "farmer market fresh produce vegetables",
    "uzhavar sandhai": "farmer market fresh produce",
    "seema": "area locality market",
    "peta": "locality market area",
}


# Short / 1-2 Word Queries Expansion Map
SHORT_QUERY_EXPANSIONS = {
    # 1-2 Word Terms -> Expanded Canonical Intent Queries
    "packaged water": "What are the mandatory specifications, permissible limits, and testing under IS 14543 for packaged drinking water?",
    "drinking water": "What are the permissible limits and quality parameters under IS 10500 and IS 14543 for drinking water?",
    "water": "What are the Indian Standards for drinking water (IS 10500) and packaged drinking water (IS 14543)?",
    "gold": "What are the mandatory gold hallmarking rules, purity grades (22K, 24K, 18K), and 6-digit HUID verification?",
    "hallmark": "How does BIS Hallmarking work for gold and silver, and how do consumers verify 6-digit HUID on the BIS Care app?",
    "huid": "What is the 6-digit alphanumeric Hallmark Unique Identification (HUID) and how do consumers verify authenticity?",
    "fe 500d": "What are the mechanical properties, yield strength, and chemical limits for Fe 500D TMT bars under IS 1786?",
    "tmt steel": "What are the tensile strength, elongation, and chemical tolerance requirements for TMT rebars under IS 1786?",
    "cement": "What are the mandatory specifications, compressive strength, and fineness for Ordinary Portland Cement under IS 269?",
    "helmets": "What are the mandatory safety impact attenuation and chin strap requirements for protective helmets under IS 4151?",
    "is 1293": "What are the electrical safety, child protection shutters, and insulation requirements for plugs and sockets under IS 1293?",
    "plugs": "What are the mandatory safety requirements and shutter specifications for electrical plugs and sockets under IS 1293?",
    "fssai": "What are the FSSAI licensing categories (Basic, State, Central), FoSCoS portal procedures, and food safety standards?",
    "fssai license": "How to apply for an FSSAI food license on the FoSCoS portal, what are the fees, and eligibility criteria?",
    "solar": "What are the Indian Standards and BIS certification schemes for solar PV modules (IS 14286) and solar water heaters (IS 12933)?",
    "solar water heater": "What is the applicable standard (IS 12933) and certification requirements for solar flat plate collector water heaters?",
    "ev battery": "What are the mandatory safety testing standards for electric vehicle lithium-ion traction batteries under IS 17855 and IS 16046?",
    "testing lab": "How can I find accredited BIS and NABL testing laboratories for product conformity testing across India?",
    "testing lab hyderabad": "Suggest accredited BIS and NABL testing laboratories in and around Hyderabad, Telangana for water, food, and industrial testing.",
    "testing lab mumbai": "Suggest accredited BIS and NABL testing laboratories in Mumbai and Maharashtra for mechanical, chemical, and electrical testing.",
    "testing lab delhi": "Suggest accredited BIS, NTH, and Shriram Institute testing laboratories in Delhi NCR for water, electrical, and materials testing.",
    "scheme 1": "Explain BIS Scheme-I (ISI Mark Scheme) for domestic manufacturers, application process on Manakonline, and grant of CM/L license.",
    "scheme 2": "Explain BIS Scheme-II (Compulsory Registration Scheme - CRS) for electronics and IT goods under MeitY guidelines.",
    "crs": "What products are covered under the Compulsory Registration Scheme (CRS) and how to register on crsbis.in?",
    "fmcs": "Explain the Foreign Manufacturers Certification Scheme (FMCS) for international plants exporting goods to India.",
    "bis license": "Explain the grant of license procedure for BIS CM/L license on Manakonline with factory audit and sample testing.",
    "manakonline": "What is the official BIS Manakonline portal (manakonline.in), how does e-filing work, and how to submit an application for BIS certification?",
    "manak": "What is the official BIS Manakonline portal (manakonline.in), how does e-filing work, and how to submit an application for BIS certification?",
    "bis care": "How do citizens use the BIS Care mobile app to verify ISI license numbers (CM/L), HUID for gold, and file grievances?",
    "complaint": "How can Indian consumers file a complaint against fake ISI marks, substandard goods, or hallmarking fraud on 1915?",
    "food adulteration": "How can consumers detect common food adulterants using FSSAI's DART methods, and where to report food fraud?",
    "fortified food": "What are the FSSAI standards and +F logo regulations for fortified milk, oil, salt, rice, and wheat flour?",
    "organic food": "What are the standards and certification requirements for Organic Food under Jaivik Bharat, NPOP, and PGS-India?",
    
    # MSME & Business Registrations
    "apply for msme how": "How to apply for MSME Udyam Registration on udyamregistration.gov.in, what are the documents, and how does it give a 50% fee concession on BIS certification?",
    "apply msme": "How to apply for MSME Udyam Registration on udyamregistration.gov.in, what are the documents, and how does it give a 50% fee concession on BIS certification?",
    "how to apply msme": "How to apply for MSME Udyam Registration on udyamregistration.gov.in, what are the documents, and how does it give a 50% fee concession on BIS certification?",
    "msme": "How does a business register for MSME on the official Udyam portal (udyamregistration.gov.in) and obtain a 50% concession on BIS certification?",
    "udyam": "How to register on the official free MSME Udyam portal (udyamregistration.gov.in) using Aadhaar and PAN for instant certificate generation?",
    "udyam registration": "How to register on the official free MSME Udyam portal (udyamregistration.gov.in) using Aadhaar and PAN for instant certificate generation?",
    
    # Consumer Rights & Everyday Dilemmas
    "service charge": "Can restaurants automatically add service charge to food bills, is it voluntary, and how can consumers refuse it under CCPA guidelines?",
    "chilling charge": "Can shopkeepers charge extra money above MRP for cold drinks, water, or milk for chilling/refrigeration under the Legal Metrology Act?",
    "cooling charge": "Can shopkeepers charge extra money above MRP for cold drinks, water, or milk for chilling/refrigeration under the Legal Metrology Act?",
    "sell old gold": "Can consumers legally sell or exchange old unhallmarked gold jewellery to jewellers without 6-digit HUID under BIS hallmarking rules?",
    "e-daakhil": "How can citizens file consumer court grievances and product liability claims online on the e-Daakhil portal (edaakhil.nic.in) without a lawyer?",
    "edaakhil": "How can citizens file consumer court grievances and product liability claims online on the e-Daakhil portal (edaakhil.nic.in) without a lawyer?",

    # Technical Formulations & Construction
    "m20": "What is the nominal concrete mix ratio, water-cement ratio, and compressive strength for M20 concrete under IS 456?",
    "m25": "What is the nominal concrete mix ratio, water-cement ratio, and compressive strength for M25 concrete under IS 456?",
    "concrete mix": "What are the standard concrete mix ratios (M15, M20, M25), water-cement ratios, and curing requirements under IS 456?",
    "concrete ratio": "What are the standard concrete mix ratios (M15, M20, M25), water-cement ratios, and curing requirements under IS 456?",
    "rebar tolerance": "What are the permissible rolling tolerances on nominal mass per meter and tensile properties for TMT steel bars under IS 1786 Table 2?",

    # Safety QCOs & Home Products
    "pressure cooker": "What are the mandatory safety requirements, fusible plug specifications, and gasket release tests for domestic pressure cookers under IS 2347?",
    "gas stove": "What are the mandatory thermal efficiency, gas leakage limits, and safety standards for domestic LPG gas stoves under IS 4246?",
    "toys": "What are the mandatory safety testing standards, heavy metal limits, and ISI mark requirements for children's toys under IS 9873?",
    "electric iron": "What are the electrical safety and thermostat cutoff requirements for domestic electric irons under IS 366?",
    "ac wire": "What is the recommended copper wire thickness in sq mm and circuit breaker rating for 1.5-ton air conditioners under IS 694 and NEC?",
    "copper water": "Is drinking water stored in copper vessels safe, what are the permissible copper limits under IS 10500, and what are toxicity risks?",
    "bee": "How does the Bureau of Energy Efficiency (BEE) Star Rating scheme work alongside BIS certification for appliances like ACs and refrigerators?",
    "wpc": "What is the WPC ETA approval requirement for wireless, Bluetooth, and Wi-Fi devices under the Department of Telecommunications?",

    # Multilingual Romanized Queries (Across All Domains)
    # 1. Dairy & Food
    "paala dukanam": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (పాల దుకాణం)?",
    "pala dukanam": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (పాల దుకాణం)?",
    "paalu dukanam": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (పాల దుకాణం)?",
    "doodh ki dukan": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (दूध की दुकान)?",
    "doodh dairy": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (दूध की दुकान)?",
    "paal kadai": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (பால் கடை)?",
    "haalu angadi": "What are the FSSAI food safety regulations, milk quality standards, lactometer testing, and FoSCoS licensing requirements for a milk shop or dairy booth (ಹಾಲು ಅಂಗಡಿ)?",
    "paala vyaparam": "What are the FSSAI licensing and food safety standards for running a milk and dairy business in India?",
    # 2. Construction, Steel & Cement
    "sariya dukanam": "What are the BIS certification standards (IS 1786), quality checks, and testing requirements for a TMT steel rebar shop?",
    "sariya ki dukan": "What are the BIS certification standards (IS 1786), quality checks, and testing requirements for a TMT steel rebar shop?",
    "simantu dukanam": "What are the mandatory BIS certification (IS 269 / IS 1489) and storage requirements for Ordinary Portland Cement (OPC) and PPC in cement retail stores?",
    "cement ki dukan": "What are the mandatory BIS certification (IS 269 / IS 1489) and storage requirements for Ordinary Portland Cement (OPC) and PPC in cement retail stores?",
    "chhat dhalai": "What is the recommended concrete mix ratio (M20 1:1.5:3), water-cement ratio, and curing duration under IS 456 for roof slab casting?",
    "slab casting": "What is the recommended concrete mix ratio (M20 1:1.5:3), water-cement ratio, and curing duration under IS 456 for roof slab casting?",
    # 3. Gold & Hallmarking
    "bangaaram dukanam": "What are the mandatory BIS Gold Hallmarking rules, 6-digit HUID requirement, and registration process for gold jewellery shops?",
    "sona ki dukan": "What are the mandatory BIS Gold Hallmarking rules, 6-digit HUID requirement, and registration process for gold jewellery shops?",
    "thangam kadai": "What are the mandatory BIS Gold Hallmarking rules, 6-digit HUID requirement, and registration process for gold jewellery shops?",
    # 4. Drinking Water
    "paani plant": "What are the mandatory BIS Scheme-I license (IS 14543), FSSAI central license, and CGWA groundwater clearance needed to start a packaged drinking water plant?",
    "neellu plant": "What are the mandatory BIS Scheme-I license (IS 14543), FSSAI central license, and CGWA groundwater clearance needed to start a packaged drinking water plant?",
    # 5. Appliances & Electrical Safety
    "gas poyi": "What are the mandatory safety standards, thermal efficiency (>=68%), and ISI mark requirements for domestic LPG gas stoves under IS 4246?",
    "gas chulha": "What are the mandatory safety standards, thermal efficiency (>=68%), and ISI mark requirements for domestic LPG gas stoves under IS 4246?",
    "current theega": "What are the recommended copper wire sizes in sq mm and safety insulation standards under IS 694 for domestic electrical wiring?",
    "bijli taar": "What are the recommended copper wire sizes in sq mm and safety insulation standards under IS 694 for domestic electrical wiring?",
    # 6. Pricing & Consumer Rights
    "mrp kanna ekkuva": "Is it legal for shopkeepers to charge extra money above MRP for chilling or refrigeration under the Legal Metrology Act?",
    "mrp se zyada": "Is it legal for shopkeepers to charge extra money above MRP for chilling or refrigeration under the Legal Metrology Act?",

    # 7. Timber, Woodwork & Carpentry
    "chekka pani": "What are the BIS standards for carpentry, timber, plywood, and wooden flush doors (IS 303, IS 710, IS 2202, IS 1331)?",
    "chekkapani": "What are the BIS standards for carpentry, timber, plywood, and wooden flush doors (IS 303, IS 710, IS 2202, IS 1331)?",
    "carpentry": "What are the BIS standards for carpentry, timber, plywood, and wooden flush doors (IS 303, IS 710, IS 2202, IS 1331)?",
    "woodwork": "What are the BIS standards for carpentry, timber, plywood, and wooden flush doors (IS 303, IS 710, IS 2202, IS 1331)?",
    "plywood": "What are the BIS standards, glue shear strength, and ISI mark requirements for plywood (IS 303 / IS 710)?",
    "flush doors": "What are the mandatory specifications and testing requirements for wooden flush door shutters under IS 2202 (Part 1)?",
    "timber": "What are the BIS standards for cut sizes of timber and structural timber in building (IS 1331 / IS 3629)?",

    # 8. Paints, Coatings & House Painting
    "rangu pani": "What are the BIS standards for wall paints, plastic emulsion, synthetic enamel and distemper (IS 15489, IS 2932, IS 5410)?",
    "rangupani": "What are the BIS standards for wall paints, plastic emulsion, synthetic enamel and distemper (IS 15489, IS 2932, IS 5410)?",
    "paint": "What are the mandatory BIS standards, ISI mark, and lead restrictions (< 90 ppm) for decorative wall paints and enamels (IS 15489 / IS 2932)?",
    "paints": "What are the mandatory BIS standards, ISI mark, and lead restrictions (< 90 ppm) for decorative wall paints and enamels (IS 15489 / IS 2932)?",
    "wall paint": "What are the BIS standards, washability, and lead restrictions (< 90 ppm) for plastic emulsion wall paints under IS 15489?",

    "सोना हॉलमार्क": "सोने के आभूषणों के लिए अनिवार्य हॉलमार्किंग (Hallmarking), 6-अंकीय HUID और सोने की शुद्धता (Purity 22K 916, 18K 750, 14K) नियम क्या हैं?",
    "پیک شدہ پینے کے پانی کے لیے لیڈ اور آرسینک کی حدود کیا ہیں اور فوڈ لائسنس کیسے حاصل کریں؟": "What are the permissible limits for Lead and Arsenic in Packaged Drinking Water under IS 14543 and how to obtain an FSSAI food license via FoSCoS dual certification?",
    "bottle water lead limit pliz tel table 2": "What are the permissible limits for Lead (0.01 mg/L) in Packaged Drinking Water under IS 14543 Table 2?"
}


class NLPQueryProcessor:
    """Intelligent query normalizer and multi-intent router for Indian Standards & Food Safety."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Fixes punctuation, replaces typos, and expands contractions across Indian dialects."""
        if not text:
            return ""
        
        cleaned = text.strip()
        # Lowercase for analysis
        tokens = re.split(r'(\s+|[.,!?/;:\(\)\[\]{}])', cleaned)
        normalized_tokens = []
        for token in tokens:
            lower_token = token.lower().strip()
            if lower_token in TYPO_CORRECTION_MAP:
                normalized_tokens.append(TYPO_CORRECTION_MAP[lower_token])
            elif lower_token in ROMANIZED_INDIAN_PHONETIC_MAP:
                normalized_tokens.append(ROMANIZED_INDIAN_PHONETIC_MAP[lower_token])
            else:
                normalized_tokens.append(token)
        
        result = "".join(normalized_tokens)
        # Collapse multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    @classmethod
    def expand_short_or_conversational_query(cls, query: str) -> Tuple[str, bool]:
        """
        Detects if query is a short (1-2 word) or cryptic inquiry and expands it
        to a rich canonical question while preserving the original intent.
        Returns: (expanded_query, was_expanded)
        """
        clean_q = query.lower().strip().strip("?.!,")
        clean_norm = cls.normalize_text(clean_q).lower()

        # Direct short query lookup
        if clean_q in SHORT_QUERY_EXPANSIONS:
            return SHORT_QUERY_EXPANSIONS[clean_q], True
        if clean_norm in SHORT_QUERY_EXPANSIONS:
            return SHORT_QUERY_EXPANSIONS[clean_norm], True

        # Check for 1-2 word partial matches
        words = [w for w in re.split(r'\s+', clean_norm) if len(w) > 1]
        if len(words) <= 3:
            two_word = " ".join(words[:2])
            if two_word in SHORT_QUERY_EXPANSIONS:
                return SHORT_QUERY_EXPANSIONS[two_word], True
            if words[0] in SHORT_QUERY_EXPANSIONS:
                return SHORT_QUERY_EXPANSIONS[words[0]], True

        return query, False

    @classmethod
    def classify_intent_and_entities(cls, query: str) -> Dict[str, Any]:
        """
        Identifies primary domain intent, sub-intents, product entities, IS codes,
        and geographic/administrative terms across BIS and FSSAI domains.
        """
        norm = cls.normalize_text(query).lower()
        
        # 1. Detect explicit Standard Codes (IS, ISO, IEC)
        is_codes = re.findall(r'\b(?:is|iso|iec)\s*[:\-]?\s*(\d{3,5}(?:\s*[:\-]?\s*\d{4})?)\b', norm, re.IGNORECASE)
        # also capture standalone numbers if prefixed with IS
        is_numbers = re.findall(r'\bis\s*[:\-]?\s*(\d{3,5})\b', norm, re.IGNORECASE)

        # 2. Check for FSSAI / Food Safety & Culinary keywords
        fssai_match = bool(re.search(
            r'\b(fssai|foscos|food\s*safety|food\s*security|adulterat\w*|dart|fortifi\w*|\+f|organic\s*food|jaivik\s*bharat|'
            r'edible\s*oil|milk|spices|honey|hygiene\s*rating|food\s*license|fbo|'
            r'paneer|panneer|palak|spinach|vegetables?|greens?|dairy|cheese|curd|dahi|butter|ghee|'
            r'eating|eat\b|eaten|consumed?|consume|dish\b|dishes|curry|street\s*food|restaurant|dhaba|'
            r'hotel\s*food|kitchen|cooking|pesticides?|dye\b|malachite|stew|grain|wheat|atta|rice|pulses?|'
            r'sweet|mithai|tea|coffee|juice|snack|momo|biryani|chapat[it]|roti|is\s*10484|is\s*10500|is\s*14543|is\s*1224)\b',
            norm
        ))

        # 3. Check for Hallmarking & Precious Metals keywords
        hallmarking_match = bool(re.search(
            r'\b(hallmark\w*|huid|gold|silver|carat|karat|22k|24k|18k|14k|916|750|585|jewell?er\w*|assaying|ahc)\b',
            norm
        ))

        # 4. Check for Testing Laboratory keywords
        lab_match = bool(re.search(
            r'\b(laboratory|laboratories|lab\b|labs\b|testing\s*facilit\w*|nabl|lrs|central\s*lab|regional\s*lab|test\s*house|shriram|cpri|cipet|arai|nccbm)\b',
            norm
        ))

        # 5. Check for Certification Schemes & Process keywords
        scheme_match = bool(re.search(
            r'\b(scheme\s*[-iIvV1-4]+|isi\s*mark|crs\b|compulsory\s*registration|fmcs\b|foreign\s*manufacturer|eco\s*mark|certificate\s*of\s*conformity|process\w*|procedure|manakonline|grant\s*of\s*license|cm/l|cml|application\s*fee|renewal|inspection|audit|sit\b)\b',
            norm
        ))

        # 6. Check for Consumer Protection & Grievance keywords
        consumer_match = bool(re.search(
            r'\b(consumer|citizen|bis\s*care|verify|fake|counterfeit|1915|helpline|grievance|complaint|rights|fraud|substandard|mrp|cheat\w*)\b',
            norm
        ))

        # 7. Check for Product Recommendation intent
        recommendation_match = bool(re.search(
            r'\b(recommend\w*|suggest\w*|which\s*standard|applicable\s*standard|what\s*standard|standard\s*for|manufacturing\s*new|i\s*make|we\s*produce|product\s*description)\b',
            norm
        ))

        # 8. Check for Dual Certification (BIS + FSSAI) intent
        dual_cert_match = bool(re.search(
            r'\b(packaged\s*water|mineral\s*water|is\s*14543|is\s*13428|infant\s*food|baby\s*food|both\s*bis\s*and\s*fssai|dual\s*cert\w*)\b',
            norm
        ))

        # Check for Procedural & Government Application keywords
        procedure_match = bool(re.search(
            r'\b(apply|how\s*to\s*apply|application|register|registration|portal|e-?filing|udyam|msme|foscos|cgwa|wpc|gs1|barcode|fee\s*structure|renewal|documents?\s*required)\b',
            norm
        ))

        # Check for Consumer Rights & Price Grievance keywords
        consumer_rights_match = bool(re.search(
            r'\b(service\s*charge|chilling|cooling\s*charge|charge\s*extra|extra\s*charge|dual\s*mrp|mrp\s*violation|sell\s*old\s*gold|unhallmarked\s*gold|no\s*refund|refuse\s*return|e-?daakhil|consumer\s*court|poisoning|fake\s*isi|scam)\b',
            norm
        ))

        # Check for Technical Formulations & Ratio keywords
        technical_ratio_match = bool(re.search(
            r'\b(mix\s*ratio|ratio\b|proportion|m20|m25|m15|m10|water\s*cement|slump|curing\s*days|tolerance|nominal\s*mass|elongation|chemical\s*limit|permissible\s*limit|preservative\s*limit|synthetic\s*color|ppm|trans\s*fat|wire\s*size|sq\s*mm|copper\s*limit)\b',
            norm
        ))

        # Check for Home Appliances & Child Safety keywords
        home_safety_match = bool(re.search(
            r'\b(pressure\s*cooker|is\s*2347|gas\s*stove|is\s*4246|electric\s*iron|is\s*366|immersion\s*heater|geyser|is\s*302|toy\w*|is\s*9873|feeding\s*bottle|is\s*14625|baby\s*food|helmet|is\s*4151)\b',
            norm
        ))

        # Check for Construction & Civil Engineering keywords
        construction_match = bool(re.search(
            r'\b(steel|rebar|rebars|tmt|fe\s*500d?|is\s*1786|cement|is\s*269|concrete|is\s*456|pipes?|hdpe|pvc|is\s*4984|sand|bricks?|structural)\b',
            norm
        ))

        # Check for Electrical & Electronics keywords
        electrical_match = bool(re.search(
            r'\b(plug\w*|socket\w*|is\s*1293|switch\w*|wire\w*|cable\w*|is\s*694|battery|batteries|is\s*16046|solar|pv\s*module|is\s*14286|refrigerator|is\s*17550|appliances?|is\s*302)\b',
            norm
        ))

        # Check for Automotive & Mechanical Safety keywords
        automotive_match = bool(re.search(
            r'\b(helmet\w*|is\s*4151|tyre\w*|tires?|is\s*15633|seat\s*belt|lpg\s*cylinder|is\s*3196)\b',
            norm
        ))

        # Extract locations for lab queries
        locations = re.findall(
            r'\b(delhi|mumbai|chennai|kolkata|bengaluru|bangalore|hyderabad|pune|ahmedabad|chandigarh|mohali|faridabad|noida|lucknow|jaipur|patna|bhopal|kochi|coimbatore|nagpur|andhra\s*pradesh|telangana|tamil\s*nadu|karnataka|maharashtra|gujarat|punjab|haryana|west\s*bengal|kerala|uttar\s*pradesh)\b',
            norm
        )

        # Domain classification
        if procedure_match and any(w in norm for w in ["msme", "udyam"]):
            detected_domain = "MSME_UDYAM_GOVERNANCE"
        elif fssai_match or "water" in norm or "food" in norm or "paneer" in norm:
            detected_domain = "FOOD_AGRICULTURE"
        elif hallmarking_match:
            detected_domain = "PRECIOUS_METALS"
        elif construction_match or technical_ratio_match:
            detected_domain = "CONSTRUCTION_CIVIL"
        elif electrical_match:
            detected_domain = "ELECTRICAL_ELECTRONICS"
        elif automotive_match:
            detected_domain = "AUTOMOTIVE_SAFETY"
        elif lab_match:
            detected_domain = "LABORATORY_TESTING"
        elif consumer_rights_match or consumer_match:
            detected_domain = "CONSUMER_PROTECTION"
        else:
            detected_domain = "GENERAL"

        # Primary intent determination
        if dual_cert_match and (fssai_match or "water" in norm or "food" in norm):
            primary_intent = "DUAL_CERTIFICATION"
        elif procedure_match:
            primary_intent = "GOVERNMENT_APPLICATION_PROCESS"
        elif consumer_rights_match:
            primary_intent = "CONSUMER_RIGHTS_PROTECTION"
        elif technical_ratio_match:
            primary_intent = "TECHNICAL_RATIO_SPECIFICATION"
        elif home_safety_match:
            primary_intent = "MANDATORY_SAFETY_QCO"
        elif recommendation_match:
            primary_intent = "PRODUCT_RECOMMENDATION"
        elif lab_match and (locations or "near" in norm or "where" in norm or "lab" in norm):
            primary_intent = "TESTING_LABORATORY"
        elif hallmarking_match:
            primary_intent = "HALLMARKING_HUID"
        elif fssai_match:
            primary_intent = "FSSAI_FOOD_SAFETY"
        elif scheme_match:
            primary_intent = "CERTIFICATION_SCHEME_PROCESS"
        elif consumer_match:
            primary_intent = "CONSUMER_PROTECTION"
        elif is_codes or is_numbers:
            primary_intent = "INDIAN_STANDARDS_SPEC"
        else:
            primary_intent = "GENERAL_STANDARDS_CHAT"

        return {
            "normalized_query": norm,
            "primary_intent": primary_intent,
            "detected_domain": detected_domain,
            "is_codes": is_numbers or is_codes,
            "has_fssai": fssai_match,
            "has_hallmarking": hallmarking_match,
            "has_lab": lab_match,
            "has_scheme": scheme_match,
            "has_consumer": consumer_match,
            "has_consumer_rights": consumer_rights_match,
            "has_procedure": procedure_match,
            "has_technical_ratio": technical_ratio_match,
            "has_home_safety": home_safety_match,
            "has_recommendation": recommendation_match,
            "has_dual_certification": dual_cert_match,
            "detected_locations": locations
        }


nlp_query_processor = NLPQueryProcessor()
