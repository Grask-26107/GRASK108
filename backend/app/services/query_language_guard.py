"""
Query Language Guard & Anti-Hallucination Pipeline (QueryLanguageGuard)
Part of GRASK AI (SIH26107).

Pipeline (in order):
  1. Script Detection  — detect Indic unicode scripts (Telugu, Hindi, Tamil, etc.)
  2. Romanized Indian Language Detection — detect Romanized Indian words phonetically
  3. Normalization — clean and normalize query in original language
  4. Translation to English — translate via GTX / Gemini fallback
  5. Topic Guard (BIS Domain Check) — is translated query BIS/FSSAI related?
  6. Negative Keyword Blocklist — blocks known out-of-scope concepts in all languages
  7. Minimum RAG Score Threshold — enforced externally (threshold=0.30)
  8. Gemini Topic Classifier — lightweight LLM classification for ambiguous cases

Returns:
  QueryGuardResult with:
    - translated_query (English equivalent for RAG)
    - detected_language (ISO code)
    - is_in_scope (bool)
    - refusal_reason (str if out of scope)
    - normalized_original (original query cleaned up)
"""

import re
import logging
import urllib.request
import json
from typing import Optional, Tuple
from dataclasses import dataclass, field

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. OUT-OF-SCOPE NEGATIVE BLOCKLIST
#    All known out-of-scope concepts in English + Romanized Indian languages
# ---------------------------------------------------------------------------
OUT_OF_SCOPE_NEGATIVE_PATTERNS = [
    # Medicine / Pharmacy / Hospital
    r'\b(medical\s*shop|medicine\s*shop|chemist\s*shop|pharmacy|pharmacist|drug\s*store|dispensary)\b',
    r'\b(hospital|clinic|doctor|physician|specialist|surgeon|dentist|veterinar)\b',
    r'\b(mandhula|mandulu|mandulu\s*dukanam|medicine\s*dukan|dawai\s*ki\s*dukan|dawakhana|aushadhi\s*dukan)\b',
    r'\b(maddu\s*dukanam|maddu\s*shop|maddu\s*angadi|marundhu\s*kadai|madu\s*angadi)\b',
    # Travel / Transport / Ticketing / Tourism
    r'\b(railway\s*ticket|train\s*ticket|irctc|pnr\s*status|tatkal|flight\s*ticket|bus\s*ticket|cinema\s*ticket|movie\s*ticket|theatre\s*ticket|film\s*ticket|book\s*tickets?|ticket\s*booking)\b',
    r'\b(movie\s*booking|cinema\s*booking|theatre\s*booking|multiplex\s*booking|box\s*office|ott\s*platform|ott\s*subscription)\b',
    r'\b(metro\s*card|metro\s*recharge|travel\s*card|toll\s*plaza|highway\s*toll)\b',
    r'\b(tourist|tourism|places\s*to\s*visit|sightseeing|travel\s*package|vacation|honeymoon)\b',
    # Civic / Government Identity Services
    r'\b(passport|visa|embassy|consulate|immigration)\b',
    r'\b(driving\s*licen[sc]e|rto\b|rc\s*book|vehicle\s*registration|traffic\s*fine|challan)\b',
    r'\b(voter\s*id|election\s*card|voting|ballot)\b',
    r'\b(pan\s*card|income\s*tax|itr\s*filing|aadhaar|uidai)\b',
    r'\b(ration\s*card|bpl\s*card)\b',
    r'\b(birth\s*certificate|death\s*certificate|marriage\s*certificate|caste\s*certificate)\b',
    r'\b(fir\b|police\s*complaint|police\s*station|arrest|bail\b|court\s*case|divorce)\b',
    # Sports, Music & Entertainment
    r'\b(cricket|football|fifa|ipl\b|world\s*cup|virat|dhoni|rohit\s*sharma|sachin|tennis|badminton|olympics)\b',
    r'\b(movies?|actor|actress|bollywood|hollywood|netflix|songs?\b|lyrics|music\s*video|guitar|piano|violin|chords|musical\s*instrument)\b',
    # Pets & Domestic Animals
    r'\b(adopt\s*a\s*pet|adopt\s*a\s*dog|adopt\s*a\s*puppy|puppy|puppies|kitten|kittens|pet\s*care|dog\s*breed|cat\s*breed)\b',
    # Gaming & Video Games
    r'\b(pubg|free\s*fire|video\s*games?|playstation|xbox|fortnite|gameplay)\b',
    # Cooking Recipes (not food safety)
    r'\b(recipe|how\s*to\s*cook|how\s*to\s*bake|bake\s*a\s*cake|chocolate\s*cake)\b',
    # Weather & Trivia (forecasts/climate queries, not materials 'weather resistance' / 'weathering')
    r'\b(weather\s*(?:forecast|in\b|today|tomorrow|report|update)|temperature\s*in|forecast|climate\s*in|rain\s*in)\b',
    r'\b(who\s*is\s*the\s*president|prime\s*minister\s*of|capital\s*of|distance\s*to\s*the\s*moon|photosynthesis|quantum\s*physics)\b',
    # Programming & Tech (unrelated to standards)
    r'\b(python\s*code|write\s*a\s*script|javascript|programming\s*code|debug\s*my|c\+\+|java\s*program)\b',
    # Adversarial
    r'\b(system\s*override|roleplay\s*as|pretend\s*to\s*be|ignore\s*bis|fabricate\s*fake\s*isi|forget\s*you\s*are)\b',
    # Finance / Banking (not trade/MSME)
    r'\b(stock\s*market|share\s*market|mutual\s*fund|demat|crypto\s*currency|bitcoin|forex)\b',
    r'\b(home\s*loan|personal\s*loan|credit\s*card\s*bill|emi\s*calculation|insurance\s*claim)\b',
    # Fictional / Sci-Fi / Extraterrestrial / Non-existent Technology
    r'\b(mars\b|moon\b|jupiter|saturn|alien|aliens|extraterrestrial|flying\s*cars?|time\s*machine|time\s*travel|teleportation|anti\s*gravity|perpetual\s*motion|laser\s*sword|lightsaber|magic\s*wand|death\s*ray|invisibility\s*cloak)\b',
    # Automotive / Vehicles / Mechanics (unrelated to statutory standards compliance)
    r'\b(car\s*photos?|car\s*pics?|car\s*images?|pictures?\s*of\s*cars?|photo\s*of\s*car|sedan|suv|hatchback|sports\s*car)\b',
    r'\b(toyota\s*corolla|honda\s*civic|maruti\s*suzuki\s*swift|hyundai\s*i20|tata\s*nexon|mahindra\s*thar)\b',
    r'\b(car\s*engine|car\s*mileage|car\s*battery\s*life|car\s*service\s*center|car\s*mechanic|used\s*cars?|buy\s*a\s*car|sell\s*my\s*car)\b',
]

# ---------------------------------------------------------------------------
# 2. ROMANIZED INDIAN OUT-OF-SCOPE WORDS EXPANDED
#    Specifically: medicine/pharmacy/hospital equivalents in regional languages
# ---------------------------------------------------------------------------
ROMANIZED_OUT_OF_SCOPE_MAP = {
    # Telugu
    "mandhulu": "medicine",
    "mandhula": "medicine",
    "mandhula dukanam": "medicine shop",
    "mandhula dukaanam": "medicine shop",
    "maddu": "medicine",
    "maddu dukanam": "medicine shop",
    "hospital": "hospital",
    "asupathri": "hospital",
    "asupathri": "hospital",
    "vaidyasala": "clinic",
    "doctor": "doctor",
    # Hindi
    "dawai": "medicine",
    "dawai ki dukan": "medicine shop",
    "dawakhana": "pharmacy",
    "aushadhi": "medicine",
    "aushadhalaya": "pharmacy",
    "aspatal": "hospital",
    "chikitsalay": "hospital",
    # Tamil
    "marundhu": "medicine",
    "marundhu kadai": "medicine shop",
    "maruttuvam": "medicine",
    "maruttuvamana": "medical",
    # Kannada
    "madu": "medicine",
    "madu angadi": "medicine shop",
    "aushadha": "medicine",
    "chikitsalaya": "hospital",
    # Malayalam
    "maru": "medicine",
    "maru kadai": "medicine shop",
    "chikitsa": "treatment/medical",
    # Generic
    "pharma": "pharmacy",
    "chemist": "pharmacy",
    "dispensary": "pharmacy",
    "clinic": "clinic",
}

# BIS Domain keywords — if any of these are found in translated query, it's in scope
BIS_DOMAIN_KEYWORDS = [
    "standard", "bis", "isi", "fssai", "foscos", "hallmark", "huid", "gold", "silver",
    "certification", "license", "testing", "laboratory", "nabl", "cement", "steel",
    "milk", "food", "water", "helmet", "solar", "battery", "cable", "wire", "socket",
    "plug", "refrigerator", "fan", "pressure cooker", "toy", "consumer", "msme",
    "udyam", "qco", "plastic", "adulterat", "quality", "is code", "iso", "iec",
    "scheme", "manufacturer", "product", "packaging", "label", "mrp", "legal metrology",
    "paneer", "ghee", "butter", "edible oil", "spice", "honey", "mineral water",
    "packaged water", "tmt", "rebar", "concrete", "brick", "pipe", "hdpe", "pvc",
    "shop", "store", "dukanam", "dukan", "kadai", "angadi",  # shops are valid if in BIS context
    "dairy", "paala", "doodh", "paani", "neeru", "bangaaram", "sariya", "simantu",
    "timber", "plywood", "woodwork", "carpentry", "chekka", "lakdi", "wood", "flush door",
    "paint", "paints", "painting", "enamel", "distemper", "emulsion", "varnish", "putty",
    "rangu", "rangupani", "rangu pani", "రంగు", "రంగు పని",
]

# Minimum BIS domain keyword count for a query to be considered in-scope
MIN_DOMAIN_KEYWORD_MATCHES = 1


@dataclass
class QueryGuardResult:
    original_query: str
    normalized_original: str
    detected_language: Optional[str]           # e.g. 'te', 'hi', 'en', None
    is_romanized_indian: bool                  # True if Romanized Telugu/Hindi etc.
    translated_to_english: str                  # English version of query for RAG
    is_in_scope: bool                          # True = pass to RAG, False = refuse
    refusal_reason: Optional[str] = None       # Human-readable reason for refusal
    confidence: float = 1.0                    # Guard confidence score


class QueryLanguageGuard:
    """
    Multilingual Query Guard & Anti-Hallucination Pipeline.
    Called at the entry point of answer_query() before any RAG or LLM call.
    """

    # Indic script unicode ranges
    SCRIPT_RANGES = {
        'te': (0x0C00, 0x0C7F),   # Telugu
        'hi': (0x0900, 0x097F),   # Hindi / Devanagari
        'ta': (0x0B80, 0x0BFF),   # Tamil
        'kn': (0x0C80, 0x0CFF),   # Kannada
        'ml': (0x0D00, 0x0D7F),   # Malayalam
        'bn': (0x0980, 0x09FF),   # Bengali
        'gu': (0x0A80, 0x0AFF),   # Gujarati
        'pa': (0x0A00, 0x0A7F),   # Punjabi (Gurmukhi)
        'ur': (0x0600, 0x06FF),   # Urdu (Arabic)
    }

    SCRIPT_NAMES = {
        'te': 'Telugu', 'hi': 'Hindi', 'ta': 'Tamil',
        'kn': 'Kannada', 'ml': 'Malayalam', 'bn': 'Bengali',
        'gu': 'Gujarati', 'pa': 'Punjabi', 'ur': 'Urdu',
    }

    def semantic_check(self, text: str) -> Tuple[bool, str]:
        """
        Fast, rule-based semantic sanity check — no LLM call.

        Returns (is_meaningful: bool, reason: str).
        Blocks:
          - Text shorter than 2 characters
          - Pure numeric input (e.g. '12345')
          - Keyboard gibberish: 3+ consecutive identical chars ('aaaa'),
            or well-known keyboard-walk sequences ('asdfgh', 'qwerty', 'zxcvbn')
          - Pure symbols / punctuation (no alphanumeric content)
        Allows everything else, including short but real words like 'gold',
        'tmt', 'huid'.
        """
        stripped = text.strip()

        # Too short
        if len(stripped) < 2:
            return False, 'query is too short'

        # Pure numeric
        if re.fullmatch(r'\d+', stripped):
            return False, 'query contains only numbers'

        # Pure symbols / punctuation (no letters or digits)
        if not re.search(r'[A-Za-z0-9\u0900-\u0D7F\u0600-\u06FF]', stripped):
            return False, 'query contains only symbols or punctuation'

        # Keyboard gibberish: 4+ consecutive identical alphabetic/indic characters (exempts numbers like 999 gold purity, 1000 kVA)
        if re.search(r'([a-zA-Z\u0900-\u0D7F])\1{3,}', stripped.lower()):
            return False, 'query appears to be keyboard gibberish (repeated characters)'

        # Keyboard-walk sequences (common gibberish patterns)
        KEYBOARD_WALKS = [
            'asdfgh', 'qwerty', 'zxcvbn', 'qazwsx', 'asdf', 'qwer',
            'zxcv', 'hjkl', 'yuiop', 'bnm',
        ]
        lower = stripped.lower().replace(' ', '')
        for walk in KEYBOARD_WALKS:
            if walk in lower:
                return False, f"query appears to be keyboard gibberish ('{walk}' pattern)"

        return True, 'ok'

    def grammar_fix_in_original_language(self, text: str, detected_lang: Optional[str]) -> str:
        """
        Fix grammar/spelling of the query in its ORIGINAL language using Gemini.

        - If detected_lang is None (English or unknown), return text as-is.
        - Otherwise call Gemini to fix spelling, grammar, and sentence structure
          while keeping the same language.
        - On any error, returns original text unchanged.
        """
        if detected_lang is None or detected_lang == "en":
            try:
                from app.services.domain_relevance_guard import domain_relevance_guard
                clean_res = domain_relevance_guard.clean_and_correct_text(text, feature="chat_standards")
                if clean_res.get("corrected_text"):
                    return clean_res["corrected_text"]
            except Exception as e:
                logger.debug(f"English grammar correction fallback: {e}")
            return text

        try:
            import google.generativeai as genai
            if not settings.GEMINI_API_KEY:
                return text
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(getattr(settings, 'GEMINI_MODEL', 'gemini-3.8-flash'))
            prompt = (
                "Fix spelling, grammar and arrange this sentence properly. "
                "Keep it in the SAME language. "
                "Return ONLY the corrected sentence, nothing else.\n"
                f"Text: {text}"
            )
            response = model.generate_content(prompt)
            corrected = response.text.strip() if response and response.text else None
            if corrected:
                logger.info(
                    f"QueryGuard grammar_fix: '{text[:50]}' → '{corrected[:50]}'"
                )
                return corrected
        except Exception as e:
            logger.debug(f"QueryGuard grammar_fix failed: {e}")

        return text

    def detect_script_language(self, text: str) -> Optional[str]:
        """Detect Indic script language by unicode code point ranges."""
        for lang_code, (start, end) in self.SCRIPT_RANGES.items():
            if re.search(f'[\\u{start:04X}-\\u{end:04X}]', text):
                return lang_code
        return None

    def detect_romanized_language(self, text: str) -> Optional[str]:
        """
        Detect if text is Romanized Indian language by checking known phonetic patterns.
        Returns a guessed language code or 'romanized' for generic.
        """
        q = text.lower()

        # Telugu Romanized indicators
        telugu_markers = [
            "dukanam", "dukaanam", "paaalu", "paala", "neellu", "manchineellu",
            "bangaaram", "simantu", "mandhula", "maddu", "asupathri",
            "inumu", "kambi", "miriyalu", "pasupu", "bellam", "chekka",
            "chekkapani", "panulu", "kottu", "kuragayalu", "kammari", "kummari",
            "rangu", "rangupani", "rangulu",
        ]
        # Hindi Romanized indicators
        hindi_markers = [
            "dukan", "ki dukan", "doodh", "atta", "chaas", "ghee",
            "dawai", "dawakhana", "aspatal", "aushadhi", "sariya",
            "lakdi", "badhai", "tarkhan", "kaam",
        ]
        # Tamil Romanized indicators
        tamil_markers = [
            "kadai", "paal", "thayir", "vellam", "thanneer", "marundhu", "maruttuvam",
            "maram", "maravelai", "velai",
        ]
        # Kannada Romanized indicators
        kannada_markers = ["angadi", "haalu", "mosaru", "kabbina", "madu", "mara", "kelasa"]

        te_count = sum(1 for m in telugu_markers if m in q)
        hi_count = sum(1 for m in hindi_markers if m in q)
        ta_count = sum(1 for m in tamil_markers if m in q)
        kn_count = sum(1 for m in kannada_markers if m in q)

        max_count = max(te_count, hi_count, ta_count, kn_count)
        if max_count == 0:
            return None
        if te_count == max_count:
            return 'te'
        if hi_count == max_count:
            return 'hi'
        if ta_count == max_count:
            return 'ta'
        return 'kn'

    def normalize_query(self, text: str) -> str:
        """Light normalization: strip extra spaces, fix punctuation."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0980-\u09FF\u0A80-\u0AFF\u0D00-\u0D7F\u0A00-\u0A7F\u0600-\u06FF.,!?()\'-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def translate_to_english_gtx(self, text: str) -> Optional[str]:
        """Fast Google GTX translation to English (auto-detect source)."""
        try:
            url = (
                f"https://translate.googleapis.com/translate_a/single"
                f"?client=gtx&sl=auto&tl=en&dt=t&q={urllib.request.quote(text)}"
            )
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and isinstance(data, list) and data[0] and isinstance(data[0], list):
                    translated = "".join(chunk[0] for chunk in data[0] if chunk and chunk[0])
                    if translated and translated.strip():
                        return translated.strip()
        except Exception as e:
            logger.debug(f"GTX translation to English failed: {e}")
        return None

    def translate_to_english_gemini(self, text: str) -> Optional[str]:
        """Gemini-based translation to English — fallback if GTX fails."""
        try:
            import google.generativeai as genai
            from app.core.config import settings
            if not settings.GEMINI_API_KEY:
                return None
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(getattr(settings, 'GEMINI_MODEL', 'gemini-3.8-flash'))
            prompt = (
                f"Translate the following text to English. "
                f"Return ONLY the English translation, nothing else.\n\nText: {text}"
            )
            response = model.generate_content(prompt)
            result = response.text.strip() if response and response.text else None
            return result
        except Exception as e:
            logger.debug(f"Gemini translation to English failed: {e}")
        return None

    def translate_to_english(self, text: str, detected_lang: Optional[str]) -> str:
        """
        Translate query to English using GTX first, Gemini as fallback.
        If both fail, return original text (best-effort).
        """
        # If already English (no Indic chars and no strong Romanized signal)
        if not detected_lang and not re.search(r'[\u0900-\u0D7F\u0600-\u06FF]', text):
            return text  # Already English or Romanized Indian (handled by phonetic map)

        # Try GTX
        gtx = self.translate_to_english_gtx(text)
        if gtx and gtx.strip().lower() != text.strip().lower():
            logger.info(f"QueryGuard: GTX translated '{text[:50]}' → '{gtx[:50]}'")
            return gtx

        # Try Gemini fallback
        gem = self.translate_to_english_gemini(text)
        if gem and gem.strip().lower() != text.strip().lower():
            logger.info(f"QueryGuard: Gemini translated '{text[:50]}' → '{gem[:50]}'")
            return gem

        logger.warning(f"QueryGuard: Translation failed for '{text[:50]}', using original")
        return text

    def check_negative_blocklist(self, text: str) -> Optional[str]:
        """
        Check if query matches known out-of-scope negative patterns.
        Returns refusal reason string if blocked, None if clean.
        """
        q = text.lower().strip()

        has_product_or_procurement = bool(re.search(
            r'\b(cable|cables|wire|wires|steel|rebar|rebars|cement|concrete|pipe|pipes|lighting|lamp|luminaire|'
            r'extinguisher|extinguishers|pump|pumps|transformer|switchgear|tender|procurement|supply|specification|'
            r'specifications|is\s*[:\-]?\s*\d+|isi\b|qco\b|bis\b|standard|standards|gem\b|cppp\b|gfr\b|frls|pvc|hdpe|opc|ppc)\b',
            q
        ))

        # Check Romanized out-of-scope map first (multi-word phrases first)
        for phrase in sorted(ROMANIZED_OUT_OF_SCOPE_MAP.keys(), key=len, reverse=True):
            if phrase in q:
                if has_product_or_procurement and phrase in ["hospital", "asupathri", "dawakhana"]:
                    continue
                meaning = ROMANIZED_OUT_OF_SCOPE_MAP[phrase]
                return (
                    f"Query refers to '{phrase}' ({meaning}) which is outside the "
                    f"BIS Standards, FSSAI Food Safety, and Consumer Quality domain."
                )

        # Check regex negative patterns
        has_statutory_violation = bool(re.search(r'\b(dual\s*mrp|mrp|overcharg\w*|legal\s*metrology|fssai|isi\s*mark|adulterat\w*|e-?daakhil|consumer\s*court|1915)\b', q))
        for pat in OUT_OF_SCOPE_NEGATIVE_PATTERNS:
            m = re.search(pat, q)
            if m:
                # If query is reporting a statutory violation at a venue, allow it
                if has_statutory_violation and any(w in m.group(0).lower() for w in ["cinema", "theatre", "theater", "multiplex", "hotel", "travel"]):
                    continue
                # If query is procuring a standard product for an institution (e.g. cables for hospital, rebars for school), allow it
                if has_product_or_procurement and any(w in m.group(0).lower() for w in ["hospital", "clinic", "doctor", "railway", "hotel", "cinema", "theatre", "travel", "flight", "bus"]):
                    continue
                return (
                    f"Query contains out-of-scope topic '{m.group(0).strip()}' "
                    f"which is not covered by BIS / FSSAI / Consumer Protection standards."
                )

        return None

    def check_bis_domain_keywords(self, english_text: str) -> bool:
        """
        Check if the English-translated query contains any BIS domain keywords.
        Returns True if in scope, False if no domain keyword found.
        """
        q = english_text.lower()
        matches = sum(1 for kw in BIS_DOMAIN_KEYWORDS if kw in q)
        return matches >= MIN_DOMAIN_KEYWORD_MATCHES

    def gemini_topic_classify(self, english_text: str) -> Tuple[bool, float]:
        """
        Use Gemini as a lightweight topic classifier for ambiguous queries.
        Returns (is_in_scope: bool, confidence: float)
        Activated only for queries that pass blocklist but fail keyword check.
        """
        try:
            import google.generativeai as genai
            from app.core.config import settings
            if not settings.GEMINI_API_KEY:
                return True, 0.5  # Default allow if API unavailable

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(getattr(settings, 'GEMINI_MODEL', 'gemini-3.8-flash'))
            prompt = (
                "You are a strict domain classifier for a Bureau of Indian Standards (BIS) assistant.\n"
                "The assistant ONLY handles: BIS Indian Standards (IS codes), FSSAI food safety, "
                "product quality certification, consumer protection for product quality, "
                "food adulteration, hallmarking, MSME certification, lab testing.\n\n"
                f"User query: \"{english_text}\"\n\n"
                "Is this query related to the above domain? Reply with ONLY one of these:\n"
                "IN_SCOPE\nOUT_OF_SCOPE"
            )
            response = model.generate_content(prompt)
            result = response.text.strip().upper() if response and response.text else "IN_SCOPE"
            if "OUT_OF_SCOPE" in result:
                return False, 0.92
            return True, 0.90
        except Exception as e:
            logger.debug(f"Gemini topic classify failed: {e}")
            return True, 0.5  # Default allow on error

    def process(self, raw_query: str) -> QueryGuardResult:
        """
        Full 8-step pipeline. Returns QueryGuardResult.
        
        Steps:
          1. Detect script language (Indic unicode)
          2. Detect Romanized Indian language
          3. Normalize original query
          4. Translate to English
          5. Check negative blocklist on BOTH original + translated
          6. Check BIS domain keywords on translated
          7. Gemini topic classify (only if step 6 fails and not blocked)
          8. Final verdict
        """

        # Step 0: Semantic check
        is_meaningful, semantic_reason = self.semantic_check(raw_query)
        if not is_meaningful:
            return QueryGuardResult(
                original_query=raw_query,
                normalized_original=raw_query,
                detected_language=None,
                is_romanized_indian=False,
                translated_to_english=raw_query,
                is_in_scope=False,
                refusal_reason=f'Query is not meaningful: {semantic_reason}. Please rephrase your question.',
                confidence=0.99,
            )

        # Step 1 & 2: Language Detection
        script_lang = self.detect_script_language(raw_query)
        romanized_lang = self.detect_romanized_language(raw_query) if not script_lang else None
        detected_language = script_lang or romanized_lang
        is_romanized = bool(romanized_lang and not script_lang)

        # Step 3: Normalize
        normalized = self.normalize_query(raw_query)

        # Step 3b: Grammar fix in original language using Gemini
        normalized = self.grammar_fix_in_original_language(normalized, detected_language)

        # Step 4: Translate to English
        # For Romanized queries, also apply phonetic map first
        if is_romanized:
            # Use NLP processor phonetic map for Romanized Indian words
            try:
                from app.services.nlp_query_processor import nlp_query_processor
                phonetic_normalized = nlp_query_processor.normalize_text(normalized)
            except Exception:
                phonetic_normalized = normalized
            english_query = self.translate_to_english(phonetic_normalized, detected_language)
        else:
            english_query = self.translate_to_english(normalized, script_lang)

        # If translation returned same as input for Romanized (i.e., translation didn't help),
        # still use the phonetic-normalized version as English proxy
        if is_romanized and english_query.strip().lower() == normalized.strip().lower():
            try:
                from app.services.nlp_query_processor import nlp_query_processor
                english_query = nlp_query_processor.normalize_text(normalized)
            except Exception:
                pass

        # Step 5: Negative Blocklist Check (on BOTH original + translated)
        # Check original first (catches Romanized patterns)
        block_reason = self.check_negative_blocklist(normalized)
        if not block_reason:
            # Also check English translation
            block_reason = self.check_negative_blocklist(english_query)

        if block_reason:
            logger.info(f"QueryGuard BLOCKED: '{raw_query[:60]}' | Reason: {block_reason}")
            return QueryGuardResult(
                original_query=raw_query,
                normalized_original=normalized,
                detected_language=detected_language,
                is_romanized_indian=is_romanized,
                translated_to_english=english_query,
                is_in_scope=False,
                refusal_reason=block_reason,
                confidence=0.98,
            )

        # Step 6: BIS Domain Keyword Check on translated text
        has_domain_keywords = self.check_bis_domain_keywords(english_query)

        if has_domain_keywords:
            # Clearly in scope
            logger.info(f"QueryGuard ALLOWED (keyword match): '{raw_query[:60]}'")
            return QueryGuardResult(
                original_query=raw_query,
                normalized_original=normalized,
                detected_language=detected_language,
                is_romanized_indian=is_romanized,
                translated_to_english=english_query,
                is_in_scope=True,
                refusal_reason=None,
                confidence=0.95,
            )

        # Step 7: Gemini Topic Classifier for ambiguous queries
        # (only if non-English query or short query that didn't match keywords)
        should_use_gemini = (
            detected_language is not None   # Non-English input
            or is_romanized                  # Romanized Indian
            or len(english_query.split()) <= 5  # Short query
        )

        if should_use_gemini and english_query.strip():
            gemini_in_scope, gemini_conf = self.gemini_topic_classify(english_query)
            if not gemini_in_scope:
                reason = (
                    f"Gemini topic classifier determined this query is outside the "
                    f"BIS Standards / FSSAI / Consumer Quality domain (confidence: {gemini_conf:.0%})."
                )
                logger.info(f"QueryGuard BLOCKED (Gemini): '{raw_query[:60]}'")
                return QueryGuardResult(
                    original_query=raw_query,
                    normalized_original=normalized,
                    detected_language=detected_language,
                    is_romanized_indian=is_romanized,
                    translated_to_english=english_query,
                    is_in_scope=False,
                    refusal_reason=reason,
                    confidence=gemini_conf,
                )
            # Gemini says in scope
            logger.info(f"QueryGuard ALLOWED (Gemini): '{raw_query[:60]}'")
            return QueryGuardResult(
                original_query=raw_query,
                normalized_original=normalized,
                detected_language=detected_language,
                is_romanized_indian=is_romanized,
                translated_to_english=english_query,
                is_in_scope=True,
                refusal_reason=None,
                confidence=gemini_conf,
            )

        # Step 8: Default — if purely English query with no domain keywords, allow
        # (The existing _is_out_of_domain_query will catch the rest)
        logger.info(f"QueryGuard PASSED (default): '{raw_query[:60]}'")
        return QueryGuardResult(
            original_query=raw_query,
            normalized_original=normalized,
            detected_language=detected_language,
            is_romanized_indian=is_romanized,
            translated_to_english=english_query,
            is_in_scope=True,
            refusal_reason=None,
            confidence=0.7,
        )


# Singleton instance
query_language_guard = QueryLanguageGuard()
