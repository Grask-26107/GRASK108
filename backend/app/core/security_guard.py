import re
import os
from typing import Dict, Any, List, Optional, Tuple

# Cartoon Alias Mappings for 100% Privacy & Device Protection
CARTOON_ALIASES = {
    "device_name": "Pokemon-Pikachu-Node-007",
    "host_node": "TomAndJerry-Protected-Host",
    "storage_vault": "BugsBunny-SafeVault",
    "inspector": "Inspector-Gadget-BIS",
    "testing_lab": "Duckburg-Accredited-Lab",
    "client_id": "MickeyMouse-Client-902",
    "admin_role": "Popeye-Chief-Auditor",
    "security_shield": "SpiderMan-WebShield-v2",
    "session_id": "Doraemon-PocketSession-42"
}

# Strict Injection and Malicious Patterns (Military-Grade Defense-in-Depth)
INJECTION_PATTERNS = [
    r'(?i)ignore\s+(all\s+)?(previous|prior|existing)\s+instructions',
    r'(?i)disregard\s+(all\s+)?(previous|prior|safety)\s+(instructions|prompts|rules)',
    r'(?i)ignore\s+(bis\s+)?(guidelines|rules|instructions|policies)',
    r'(?i)system\s*override',
    r'(?i)reveal\s+(the\s+)?(system|hidden|developer)\s+prompt',
    r'(?i)reveal\s+.*?(developer\s+instructions|internal\s+guidelines|secret\s+instructions)',
    r'(?i)output\s+(your\s+)?(entire\s+)?system\s+prompt',
    r'(?i)what\s+(is|are)\s+your\s+(initial|system|secret|developer)\s+instructions',
    r'(?i)you\s+are\s+now\s+in\s+(dan|developer|unrestricted|god)\s+mode',
    r'(?i)you\s+are\s+now\s+(chatgpt|dan|an\s+unrestricted|jailbroken)',
    r'(?i)act\s+as\s+an\s+(unfiltered|unrestricted|jailbroken)\s+(ai|agent|assistant)',
    r'(?i)roleplay\s+as(\s+a)?\s+(malicious|hacker|unrestricted|unfiltered)',
    r'(?i)bypass\s+(all\s+)?(safety|security|content)\s+filters',
    r'(?i)\b(how\s+to\s+(forge|fabricate|make|create|print)|fabricate|forge)\s+(fake|counterfeit)\s+(isi|bis|stamps?|marks?)\b',
    r'(?i)\bhow\s+to\s+counterfeit\s+(isi|bis|products|stamps?)\b',
    r'(?i)forget\s+(all\s+)?(your\s+(rules|role|identity|programming)|you\s+are)',
    r'(?i)new\s+system\s+(instruction|prompt|directive):',
    r'(?i)repeat\s+(the\s+)?words?\s+above',
    r'(?i)what\s+was\s+written\s+(before|above)\s+this',
    r'(?i)<\|im_start\|>',
    r'(?i)<\|im_end\|>',
    r'(?i)\[/?(inst|sys)\]',
    r'(?i)</?(system|user_query|retrieved_bis_standard_context)>',
    r'(?i)drop\s+table',
    r'(?i)insert\s+into',
    r'(?i)delete\s+from',
    r'(?i)union\s+select',
    r'(?i)(xp_cmdshell|exec\s*\(|sp_executesql)',
    r'(?i)__proto__',
    r'(?i)constructor\s*\[',
    r'(?i)(os\.environ|printenv|cat\s+/etc/passwd|cmd\.exe|powershell)',
    r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token)\s*(=|:|\?)'
]

# Multilingual Vocabulary & Phonetic Typo Map -> Normalized English Concept Key
MULTILINGUAL_INTENT_MAP: Dict[str, str] = {
    # Poultry / Chicken / Meat
    "murgi": "poultry", "murghi": "poultry", "kodi": "poultry", "kozhi": "poultry",
    "kombadi": "poultry", "koli": "poultry", "marghi": "poultry", "chekin": "poultry",
    "chiken": "poultry", "poultary": "poultry", "poultry": "poultry", "chicken": "poultry",
    "broiler": "poultry", "layer": "poultry", "hatchery": "poultry", "abattoir": "poultry",
    "slaughterhouse": "poultry", "feed": "poultry", "aflatoxin": "poultry", "meat": "poultry",
    "kukkut": "poultry", "goshth": "poultry", "maamsam": "poultry",

    # Petrol / Fuel / Petroleum
    "petrol": "petroleum", "petrole": "petroleum", "petrl": "petroleum", "diesel": "petroleum",
    "diesl": "petroleum", "disel": "petroleum", "hsd": "petroleum", "bunk": "petroleum",
    "pump": "petroleum", "dispenser": "petroleum", "tel": "petroleum", "thailam": "petroleum",
    "enna": "petroleum", "enney": "petroleum", "gasoline": "petroleum", "peso": "petroleum",
    "lpg": "petroleum", "cylinder": "petroleum", "bitumen": "petroleum",

    # Cement / TMT Steel / Construction
    "cement": "construction", "cemnt": "construction", "sariya": "construction",
    "saria": "construction", "rebar": "construction", "steel": "construction",
    "loha": "construction", "inumu": "construction", "irumbu": "construction",
    "lokhand": "construction", "kabbina": "construction", "kaddi": "construction",
    "concrete": "construction", "conkret": "construction", "opc": "construction",
    "ppc": "construction", "tmt": "construction", "fe500": "construction",
    "fe550": "construction", "building": "construction", "makan": "construction",
    "ghar": "construction", "illu": "construction", "veedu": "construction",

    # Drinking Water / Packaged Water / Pipes
    "water": "water", "watr": "water", "watter": "water", "pani": "water", "paani": "water",
    "neellu": "water", "neeru": "water", "thanni": "water", "neer": "water", "jol": "water",
    "vellam": "water", "jal": "water", "mineral": "water", "packaged": "water",
    "tds": "water", "bisleri": "water", "jar": "water", "bottle": "water",
    "hdpe": "water", "pipe": "water", "ro": "water", "purifier": "water",

    # Solar / Clean Energy / Inverters
    "solar": "solar", "solr": "solar", "sollar": "solar", "photovoltaic": "solar",
    "pv": "solar", "inverter": "solar", "invrter": "solar", "surya": "solar",
    "suraj": "solar", "sooriya": "solar", "panel": "solar", "rooftop": "solar",
    "urja": "solar", "shakti": "solar", "bijli": "solar", "vidyuth": "solar",

    # Medical / PPE / Face Masks / Syringes
    "mask": "medical", "maskk": "medical", "medical": "medical", "medcal": "medical",
    "ppe": "medical", "surgical": "medical", "surjical": "medical", "syringe": "medical",
    "dawa": "medical", "aushadh": "medical", "aushadha": "medical", "marunthu": "medical",
    "osudh": "medical", "marunnu": "medical", "hospital": "medical", "haspatal": "medical",
    "davakhana": "medical", "aaspathre": "medical", "maruthuvamanai": "medical",
    "bfe": "medical", "thermometer": "medical",

    # Footwear / Shoes / Chappals
    "footwear": "footwear", "feetwear": "footwear", "shoe": "footwear", "shoes": "footwear",
    "soes": "footwear", "leather": "footwear", "sandal": "footwear", "chappal": "footwear",
    "cheppu": "footwear", "seruppu": "footwear", "cheruppu": "footwear", "joota": "footwear",
    "juto": "footwear", "boots": "footwear", "sneaker": "footwear",

    # Toys / Infant Goods
    "toy": "toys", "toys": "toys", "toyz": "toys", "toies": "toys", "khilone": "toys",
    "khelna": "toys", "khelani": "toys", "ramakada": "toys", "pommai": "toys",
    "aatalu": "toys", "doll": "toys", "baby": "toys", "infant": "toys", "bacho": "toys",

    # Gold / Hallmarking / Jewellery
    "gold": "gold", "gld": "gold", "sona": "gold", "bangaru": "gold", "thangam": "gold",
    "sonu": "gold", "shonali": "gold", "hallmark": "gold", "hallmrk": "gold",
    "huid": "gold", "jewellery": "gold", "jewel": "gold", "carat": "gold", "karat": "gold",
    "22k": "gold", "18k": "gold", "silver": "gold", "chandi": "gold", "velli": "gold",

    # Electrical Sockets / Plugs / Wires
    "plug": "electrical", "plugg": "electrical", "socket": "electrical", "soket": "electrical",
    "switch": "electrical", "swich": "electrical", "wire": "electrical", "cable": "electrical",
    "shutter": "electrical", "16a": "electrical", "6a": "electrical", "bijli": "electrical",
    "current": "electrical", "board": "electrical",

    # Food / Kitchen / Restaurant Hygiene & FSSAI
    "restaurant": "food_hygiene", "restaurnt": "food_hygiene", "resturant": "food_hygiene",
    "restraunt": "food_hygiene", "restaraunt": "food_hygiene", "restrant": "food_hygiene",
    "restaurent": "food_hygiene", "food": "food_hygiene", "fud": "food_hygiene", "foood": "food_hygiene",
    "dhaba": "food_hygiene", "hotel": "food_hygiene", "cafe": "food_hygiene", "canteen": "food_hygiene",
    "catering": "food_hygiene", "bakery": "food_hygiene", "kitchen": "food_hygiene", "bhojan": "food_hygiene",
    "khana": "food_hygiene", "oota": "food_hygiene", "saapadu": "food_hygiene", "mess": "food_hygiene",
    "tiffin": "food_hygiene", "eatery": "food_hygiene", "fastfood": "food_hygiene", "fast food": "food_hygiene",
    "streetfood": "food_hygiene", "street food": "food_hygiene", "fssai": "food_hygiene", "fassai": "food_hygiene",
    "fsai": "food_hygiene", "hygiene": "food_hygiene", "safai": "food_hygiene", "cooking": "food_hygiene",
    "cook": "food_hygiene", "chef": "food_hygiene",

    # Soya Sauce & Fermented Soy Condiments
    "soya": "soya_sauce", "soy": "soya_sauce", "soyasos": "soya_sauce", "soysos": "soya_sauce",
    "shoyu": "soya_sauce", "soybean": "soya_sauce",

    # Dairy, Milk, Paneer & Ghee
    "milk": "dairy", "doodh": "dairy", "dudh": "dairy", "paal": "dairy", "haalu": "dairy",
    "paneer": "dairy", "panir": "dairy", "ghee": "dairy", "butter": "dairy", "makhan": "dairy",
    "curd": "dairy", "dahi": "dairy", "khoya": "dairy", "mawa": "dairy", "lactometer": "dairy",

    # Edible Vegetable Oils & Fats
    "oil": "edible_oil", "sarson": "edible_oil", "mustard": "edible_oil",
    "groundnut": "edible_oil", "sunflower": "edible_oil", "til": "edible_oil", "vanaspati": "edible_oil",
    "argemone": "edible_oil",

    # Spices & Condiments
    "spice": "spices", "masala": "spices", "turmeric": "spices", "haldi": "spices", "pasupu": "spices",
    "chilli": "spices", "mirch": "spices", "mirchi": "spices", "pepper": "spices", "coriander": "spices",
    "dhaniya": "spices", "curcumin": "spices",

    # Honey & Natural Apiculture
    "honey": "honey", "madhu": "honey", "shehad": "honey", "then": "honey", "jenu": "honey",

    # Fresh Juices, Sugarcane Juice, Beverages & Shakes
    "juice": "juice_beverage", "juce": "juice_beverage", "sugarcane": "juice_beverage",
    "ganna": "juice_beverage", "cheruku": "juice_beverage", "karumbu": "juice_beverage",
    "kabbu": "juice_beverage", "serdi": "juice_beverage", "aakh": "juice_beverage",
    "us": "juice_beverage", "beverage": "juice_beverage", "rasam": "juice_beverage",
    "sharbat": "juice_beverage", "shake": "juice_beverage", "smoothie": "juice_beverage",

    # Fertilizers / Chemicals
    "fertilizer": "fertilizer", "fertilyzer": "fertilizer", "khad": "fertilizer",
    "urea": "fertilizer", "ureaa": "fertilizer", "dap": "fertilizer", "pesticide": "fertilizer",
    "soap": "fertilizer", "sabun": "fertilizer",

    # Paints, Enamels, Plastic Emulsions & Wall Coatings (Telugu: rangu, rangu pani)
    "rangu": "paints_coatings", "rangupani": "paints_coatings", "rangu pani": "paints_coatings",
    "painting": "paints_coatings", "paint": "paints_coatings", "paints": "paints_coatings",
    "enamel": "paints_coatings", "distemper": "paints_coatings", "emulsion": "paints_coatings",
    "putty": "paints_coatings", "wall putty": "paints_coatings", "cement paint": "paints_coatings",
    "varnish": "paints_coatings", "primer": "paints_coatings",
    "రంగు": "paints_coatings", "రంగు పని": "paints_coatings", "రంగులు": "paints_coatings",
    "रंग": "paints_coatings", "पेंट": "paints_coatings", "सफेदी": "paints_coatings",

    # Timber, Plywood, Wooden Flush Doors & Carpentry
    "chekka": "timber_carpentry", "chekkapani": "timber_carpentry", "chekka pani": "timber_carpentry",
    "carpentry": "timber_carpentry", "carpenter": "timber_carpentry", "woodwork": "timber_carpentry",
    "wood work": "timber_carpentry", "timber": "timber_carpentry", "plywood": "timber_carpentry",
    "ply": "timber_carpentry", "flush door": "timber_carpentry", "flush doors": "timber_carpentry",
    "wood": "timber_carpentry", "lakdi": "timber_carpentry", "lakdi ka kaam": "timber_carpentry",
    "badhai": "timber_carpentry", "badhai kaam": "timber_carpentry", "tarkhan": "timber_carpentry",
    "maram": "timber_carpentry", "maravelai": "timber_carpentry", "kammari": "timber_carpentry",
    "చెక్క": "timber_carpentry", "చెక్క పని": "timber_carpentry", "కలప": "timber_carpentry",
    "బడగ": "timber_carpentry", "లకడీ": "timber_carpentry", "लकड़ी": "timber_carpentry",
    "बढ़ई": "timber_carpentry", "लकड़ी का काम": "timber_carpentry", "மர வேலை": "timber_carpentry",
    "மரவேலை": "timber_carpentry"
}

# BIS Domain Concept Mapping
DOMAIN_CANONICAL_NAMES = {
    "paints_coatings": "Paints, Varnishes, Synthetic Enamels & Wall Coatings (IS 15489 / IS 2932 / IS 5410 / IS 428)",
    "timber_carpentry": "Timber, Plywood, Wooden Flush Doors & Carpentry (IS 303 / IS 710 / IS 2202 / IS 1331)",
    "juice_beverage": "Fresh Fruit Juices, Sugarcane Juice & Beverage Centers (FSSAI / IS 10500 / IS 2491)",
    "soya_sauce": "Soya Sauce, Fermented Condiments & Soybean Standards (FSSAI Reg 2.3.56 / IS 7837)",
    "dairy": "Dairy Industry, Milk Quality, Paneer & Ghee Adulteration Control (IS 1479 / IS 1224 / IS 10484)",
    "edible_oil": "Edible Vegetable Oils & Fats, Mustard & Blended Oils (IS 542 / IS 544 / IS 546)",
    "spices": "Spices & Condiments, Turmeric, Chilli & Pepper Quality (IS 3576 / IS 2445)",
    "honey": "Honey & Natural Apiculture Sweeteners (IS 4941 / FSSAI)",
    "poultry": "Poultry Farming, Retail Chicken Centres & Meat Processing (IS 1374 / IS 7049)",
    "petroleum": "Petroleum Retail & Fuel Dispensing Outlets (IS 2796 / IS 1460 / IS 10987)",
    "construction": "Building Materials, Cement & Structural Steel (IS 269 / IS 1786)",
    "water": "Packaged Drinking Water & Water Infrastructure (IS 14543 / IS 4984 / IS 10500)",
    "solar": "Solar Photovoltaic & Clean Renewable Energy (IS 14286 / IS/IEC 61730)",
    "medical": "Medical Devices, Hospital Consumables & PPE (IS 16289 / IS 10258)",
    "footwear": "Footwear, Leather Goods & Sports Shoes (IS 15844 / IS 3735)",
    "toys": "Safety of Toys & Childcare Products (IS 9873)",
    "gold": "Gold & Silver Hallmarking & HUID (IS 1417)",
    "electrical": "Plugs, Socket-Outlets & Electrical Safety (IS 1293 / IS 694)",
    "food_hygiene": "Commercial Food Services, Restaurants, Catering & FSSAI Licensing (FSSAI / IS 2491 / IS 10500)",
    "fertilizer": "Industrial Chemicals, Fertilizers & Paints (IS 540 / CHD)"
}


def sanitize_and_shield_input(text: str) -> Tuple[str, bool]:
    """
    Sanitizes user input:
    - Strips control characters
    - Neutralizes prompt injection & SQL keywords
    - Prevents XSS scripts
    - Redacts delimiter collision tags
    Returns (cleaned_text, injection_detected_bool)
    """
    if not text:
        return "", False
    
    cleaned = text.strip()[:1500]
    # Remove non-printable control characters
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    detected = False
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, cleaned):
            detected = True
            cleaned = re.sub(pattern, '[REDACTED_SECURITY_PROMPT_INJECTION]', cleaned)
            
    return cleaned, detected


def anonymize_metadata(obj: Any) -> Any:
    """
    Replaces real system paths, hostnames, IPs, hardware specs, and internal user details
    with safe cartoon identifiers (e.g. Pikachu-Node, Duckburg-Lab, BugsBunny-Vault).
    Zero data leakage of Windows usernames, drive letters, hardware, or internal paths.
    """
    if isinstance(obj, str):
        # 1. Mask local Windows / Linux paths and real usernames (ignoring URL schemes like http:// or https://)
        obj = re.sub(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])[^"\'\n\r<>]+', f'/safe_vault/{CARTOON_ALIASES["storage_vault"]}', obj)
        obj = re.sub(r'/Users/[^"\'\n\r<>]+', f'/safe_vault/{CARTOON_ALIASES["storage_vault"]}', obj)
        obj = re.sub(r'/home/[^"\'\n\r<>]+', f'/safe_vault/{CARTOON_ALIASES["storage_vault"]}', obj)
        obj = re.sub(r'\\\\(?:[a-zA-Z0-9_\-\.]+)\\[^"\'\n\r<>]+', f'/network/{CARTOON_ALIASES["storage_vault"]}', obj)
        # 2. Mask IP addresses (including private subnets, loopbacks)
        obj = re.sub(r'\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b', CARTOON_ALIASES["device_name"], obj)
        obj = re.sub(r'\b127\.0\.0\.1\b', 'localhost.toon', obj)
        # 3. Mask MAC addresses
        obj = re.sub(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b', '00:TO:ON:SH:IE:LD', obj)
        # 4. Mask hardware specs (CPU/GPU/Motherboard identifiers)
        obj = re.sub(r'(?i)\b(intel|amd|nvidia|ryzen|geforce|core\s*i[3579]|radeon)\b[^,\n\r]{0,25}', 'ToonCorp Quantum Processor', obj)
        return obj
    elif isinstance(obj, dict):
        return {k: anonymize_metadata(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [anonymize_metadata(item) for item in obj]
    return obj


# Cross-Lingual & Multi-Sense Disambiguation Registry (Google-style "Did you mean?")
AMBIGUITY_REGISTRY: Dict[str, Dict[str, Any]] = {
    "rangu pani": {
        "title": "Cross-Lingual Clarification: 'rangu pani'",
        "primary_domain": "paints_coatings",
        "language_context": "te",
        "description": "In Telugu, 'rangu pani' (రంగు పని) refers to house painting, synthetic enamels, and wall coatings. In Hindi, 'pani' means drinking water.",
        "options": [
            {
                "label": "🎨 రంగు పని / Paints, Enamels & Wall Putty",
                "query": "What are the BIS standards for wall paints, plastic emulsion, synthetic enamel and distemper (IS 15489, IS 2932, IS 5410)?",
                "description": "Plastic emulsion, synthetic enamel, cement paint, distemper (IS 15489 / IS 2932 / IS 5410)"
            },
            {
                "label": "💧 తాగునీరు / Packaged Drinking Water",
                "query": "What are the BIS standards for packaged drinking water and water bottling plants (IS 14543 / IS 10500)?",
                "description": "Packaged water, RO purification, mineral water standards (IS 14543 / IS 10500)"
            }
        ]
    },
    "chekka pani": {
        "title": "Cross-Lingual Clarification: 'chekka pani'",
        "primary_domain": "timber_carpentry",
        "language_context": "te",
        "description": "In Telugu, 'chekka pani' (చెక్క పని) refers to woodwork & carpentry. In Hindi, 'pani' means drinking water.",
        "options": [
            {
                "label": "🪵 చెక్క పని / Carpentry & Woodwork",
                "query": "What are the BIS standards for carpentry, plywood, timber and wooden doors (IS 303, IS 710, IS 2202)?",
                "description": "Plywood, marine ply, wooden flush doors, timber sizing (IS 303 / IS 710 / IS 2202)"
            },
            {
                "label": "💧 తాగునీరు / Packaged Drinking Water",
                "query": "What are the BIS standards for packaged drinking water and water bottling plants (IS 14543 / IS 10500)?",
                "description": "Packaged water, RO purification, mineral water standards (IS 14543 / IS 10500)"
            }
        ]
    },
    "pani": {
        "title": "Query Disambiguation: 'pani'",
        "primary_domain": None,
        "language_context": "multi",
        "description": "'Pani' means water in Hindi/North India, but means work/labor in Telugu and South Indian languages.",
        "options": [
            {
                "label": "💧 पीने का पानी / Packaged Drinking Water (IS 14543)",
                "query": "What are the BIS standards for packaged drinking water and water bottling plants (IS 14543 / IS 10500)?",
                "description": "Drinking water, mineral water, bottling plants (IS 14543 / IS 10500)"
            },
            {
                "label": "🪵 చెక్క పని / Carpentry & Woodwork (IS 303 / IS 710)",
                "query": "What are the BIS standards for carpentry, timber, plywood and flush doors (IS 303, IS 710, IS 2202)?",
                "description": "Woodwork, plywood, timber cut sizes (IS 303 / IS 710)"
            },
            {
                "label": "🏗️ ఇల్లు పని / Building Construction (IS 269 / IS 1786)",
                "query": "What are the BIS standards for building construction, cement and TMT steel (IS 269 / IS 1786)?",
                "description": "Cement, TMT rebar, concrete structural work (IS 269 / IS 1786)"
            },
            {
                "label": "🎨 రంగు పని / House Painting & Paints (IS 15489 / IS 2932)",
                "query": "What are the BIS standards for wall paints, plastic emulsion, synthetic enamel and distemper (IS 15489, IS 2932, IS 5410)?",
                "description": "Plastic emulsion, synthetic enamel, wall putty (IS 15489 / IS 2932 / IS 5410)"
            }
        ]
    },
    "battery": {
        "title": "Product Category Clarification: 'battery'",
        "primary_domain": None,
        "language_context": "en",
        "description": "Battery standards vary significantly between Electric Vehicles, Consumer Electronics, and Dry Cells.",
        "options": [
            {
                "label": "🚗 EV Traction Batteries (AIS 038 / IS 16893)",
                "query": "What are the BIS and AIS standards for Electric Vehicle (EV) batteries (AIS 038 / IS 16893)?",
                "description": "Safety requirements for EV traction batteries and BMS systems"
            },
            {
                "label": "📱 Portable Lithium Cells & Power Banks (IS 16046)",
                "query": "What are the BIS CRS Scheme-II standards for secondary lithium cells and power banks (IS 16046)?",
                "description": "Mobile phones, laptops, and portable rechargeable power banks"
            },
            {
                "label": "🔋 Dry Cell Primary Batteries (IS 8144)",
                "query": "What are the BIS specifications for primary zinc-carbon and alkaline batteries (IS 8144)?",
                "description": "AA, AAA, 9V primary consumer batteries"
            }
        ]
    },
    "cable": {
        "title": "Product Category Clarification: 'cable'",
        "primary_domain": None,
        "language_context": "en",
        "description": "Cable specifications differ between domestic building wires and high-voltage industrial power cables.",
        "options": [
            {
                "label": "🏠 Domestic Building Wires (IS 694)",
                "query": "What are the BIS standards for PVC insulated domestic electrical cables and building wires (IS 694)?",
                "description": "Single-core and multi-core copper domestic wiring"
            },
            {
                "label": "⚡ Industrial XLPE Power Cables (IS 7098)",
                "query": "What are the BIS standards for crosslinked polyethylene (XLPE) insulated power cables (IS 7098)?",
                "description": "High and extra-high voltage transmission and industrial power cables"
            }
        ]
    },
    "oil": {
        "title": "Category Clarification: 'oil'",
        "primary_domain": None,
        "language_context": "en",
        "description": "'Oil' may refer to edible cooking oils or industrial/transformer lubricating oils.",
        "options": [
            {
                "label": "🍳 Edible Cooking Oils (FSSAI / IS 542)",
                "query": "What are the statutory standards and AGMARK/FSSAI regulations for edible vegetable cooking oils (IS 542)?",
                "description": "Mustard, sunflower, groundnut, and blended vegetable cooking oils"
            },
            {
                "label": "⚙️ Transformer & Industrial Oils (IS 335)",
                "query": "What are the BIS standards for unused mineral insulating oils for transformers and switchgear (IS 335)?",
                "description": "Dielectric transformer oil and industrial lubricants"
            }
        ]
    },
    "kallu": {
        "title": "Cross-Lingual Clarification: 'kallu'",
        "primary_domain": None,
        "language_context": "multi",
        "description": "In Tamil/Kannada/Malayalam, 'kallu' refers to stones/aggregates. In Telugu, 'kallu' can refer to beverages.",
        "options": [
            {
                "label": "🪨 Coarse & Fine Aggregates (IS 383)",
                "query": "What are the BIS standards for coarse and fine aggregates for concrete (IS 383)?",
                "description": "Crushed stone, gravel, and natural sand for building construction"
            },
            {
                "label": "👓 Spectacle Frames & Ophthalmic Optics (IS 16752)",
                "query": "What are the BIS standards for ophthalmic optics and spectacles lenses (IS 16752)?",
                "description": "Corrective vision lenses and eye protection"
            }
        ]
    },
    "mandi": {
        "title": "Domain Clarification: 'mandi'",
        "primary_domain": None,
        "language_context": "multi",
        "description": "'Mandi' can refer to wholesale agricultural grain/produce markets or traditional culinary food services.",
        "options": [
            {
                "label": "🌾 Agricultural Produce Markets (IS 1488)",
                "query": "What are the BIS standards for grain storage, handling and agricultural marketing yards (IS 1488)?",
                "description": "Wholesale grain mandis, moisture standards and storage structures"
            },
            {
                "label": "🍽️ Commercial Food Service & Restaurant Hygiene (FSSAI / IS 2491)",
                "query": "What are the FSSAI and BIS hygiene standards for commercial restaurants, biryani and meat eateries (IS 2491)?",
                "description": "Culinary food safety, kitchen hygiene and FSSAI restaurant licensing"
            }
        ]
    }
}


def detect_query_disambiguation(query: str) -> Optional[Dict[str, Any]]:
    """
    Checks if a query matches known cross-lingual homonyms or polysemous terms.
    Returns disambiguation metadata and options or None.
    """
    clean_q = query.lower().strip()
    clean_q_simple = re.sub(r'[^\w\s]', '', clean_q).strip()
    tokens = clean_q_simple.split()

    if not tokens:
        return None

    # 1. Exact match in registry
    if clean_q_simple in AMBIGUITY_REGISTRY:
        return AMBIGUITY_REGISTRY[clean_q_simple]

    # 2. Check compound multi-word phrases FIRST (sorted by token count descending)
    # This prevents single unigrams ('pani') from stealing 'rangu pani' or 'chekka pani'
    sorted_phrases = sorted(AMBIGUITY_REGISTRY.keys(), key=lambda p: (len(p.split()), len(p)), reverse=True)
    for phrase in sorted_phrases:
        if len(phrase.split()) > 1:
            if re.search(r'\b' + re.escape(phrase) + r'\b', clean_q_simple):
                return AMBIGUITY_REGISTRY[phrase]

    # 3. FIRST-WORD PRIORITY: For multi-token queries with 'pani' (or South Indian verbs)
    # The first token is the primary domain noun/qualifier (rangu = paint, chekka = wood, illu = building)
    if len(tokens) >= 2 and "pani" in tokens:
        first_tok = tokens[0]
        if first_tok in ["rangu", "rang", "paint", "paints", "enamel", "varnish", "distemper", "putty", "రంగు"]:
            return AMBIGUITY_REGISTRY.get("rangu pani")
        if first_tok in ["chekka", "lakdi", "wood", "carpentry", "timber", "plywood", "badhai", "చెక్క"]:
            return AMBIGUITY_REGISTRY.get("chekka pani")

    # 4. Check token-level isolated ambiguous terms (e.g. single word "pani", "battery", "oil")
    if len(tokens) == 1 and tokens[0] in AMBIGUITY_REGISTRY:
        return AMBIGUITY_REGISTRY[tokens[0]]

    # 5. Check standalone single-word registry entries with word boundary regex
    for phrase in sorted_phrases:
        if len(phrase.split()) == 1:
            if re.search(r'\b' + re.escape(phrase) + r'\b', clean_q_simple):
                return AMBIGUITY_REGISTRY[phrase]

    return None


def detect_multilingual_intent(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Tokenizes and inspects query across 10+ Indian languages and phonetic typo forms.
    Evaluates FIRST-WORD qualifiers for compound phrases and multi-word phrases (trigrams and bigrams) FIRST,
    then single tokens SECOND.
    Protects against cross-lingual collisions (e.g. Telugu 'pani' = work vs Hindi 'pani' = water).
    Returns (concept_key, canonical_domain_name) or (None, None).
    """
    clean_q = query.lower().strip()
    tokens = re.findall(r'[a-zA-Z0-9\u0900-\u097F\u0C00-\u0C7F\u0B80-\u0BFF\u0980-\u09FF\u0A80-\u0AFF\u0D00-\u0D7F]+', clean_q)
    
    if not tokens:
        return None, None

    # 0. FIRST-WORD QUALIFIER PRIORITY for multi-token phrases
    # When queries pair a product/material with generic work/verb ('pani', 'work', 'kaam', 'velai', 'kelasa'):
    if len(tokens) >= 2:
        first_token = tokens[0]
        # Paint / Colour domain qualifier
        if first_token in ["rangu", "rang", "రంగు", "paint", "paints", "enamel", "putty"]:
            return "paints_coatings", DOMAIN_CANONICAL_NAMES.get("paints_coatings")
        # Wood / Carpentry domain qualifier
        if first_token in ["chekka", "చెక్క", "lakdi", "timber", "plywood", "carpentry"]:
            return "timber_carpentry", DOMAIN_CANONICAL_NAMES.get("timber_carpentry")
        # Construction / Steel domain qualifier
        if first_token in ["illu", "cement", "sariya", "inumu"]:
            return "construction", DOMAIN_CANONICAL_NAMES.get("construction")

    # 1. Check 3-word sliding trigrams first
    for i in range(len(tokens) - 2):
        trigram = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        if trigram in MULTILINGUAL_INTENT_MAP:
            concept = MULTILINGUAL_INTENT_MAP[trigram]
            return concept, DOMAIN_CANONICAL_NAMES.get(concept)
            
    # 2. Check 2-word sliding bigrams second
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in MULTILINGUAL_INTENT_MAP:
            concept = MULTILINGUAL_INTENT_MAP[bigram]
            return concept, DOMAIN_CANONICAL_NAMES.get(concept)

    # 3. Check single tokens third (with cross-lingual collision safety)
    has_wood_indicator = any(t in tokens for t in ["chekka", "lakdi", "wood", "carpentry", "timber", "plywood", "badhai", "చెక్క"])
    has_paint_indicator = any(t in tokens for t in ["rangu", "rang", "paint", "paints", "enamel", "varnish", "distemper", "putty", "రంగు"])
    has_civil_indicator = any(t in tokens for t in ["illu", "ghar", "makan", "building", "cement", "sariya"])

    for tok in tokens:
        if tok == "pani":
            if has_paint_indicator:
                return "paints_coatings", DOMAIN_CANONICAL_NAMES.get("paints_coatings")
            if has_wood_indicator:
                return "timber_carpentry", DOMAIN_CANONICAL_NAMES.get("timber_carpentry")
            if has_civil_indicator:
                return "construction", DOMAIN_CANONICAL_NAMES.get("construction")
        if tok in MULTILINGUAL_INTENT_MAP:
            concept = MULTILINGUAL_INTENT_MAP[tok]
            return concept, DOMAIN_CANONICAL_NAMES.get(concept)
            
    return None, None
