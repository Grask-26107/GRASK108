import re
import logging
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, Tuple, List
from app.core.config import settings

logger = logging.getLogger(__name__)

# Supported Languages in India
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧", "voice_code": "en-IN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳", "voice_code": "hi-IN"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳", "voice_code": "te-IN"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳", "voice_code": "ta-IN"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳", "voice_code": "mr-IN"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳", "voice_code": "bn-IN"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳", "voice_code": "kn-IN"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳", "voice_code": "gu-IN"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳", "voice_code": "ml-IN"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "voice_code": "pa-IN"},
    "ur": {"name": "Urdu", "native": "اردو", "flag": "🇮🇳", "voice_code": "ur-IN"}
}

# Explicit Language Triggers in Prompts (e.g. "in hindi", "telugu lo cheppu", "tamil me", "translate to marathi")
LANGUAGE_TRIGGER_REGEX = [
    (r'(?i)\b(in\s+hindi|hindi\s+mein|hindi\s+me|हिन्दी|हिंदी)\b', 'hi'),
    (r'(?i)\b(in\s+telugu|telugu\s+lo|telugulo|తెలుగు)\b', 'te'),
    (r'(?i)\b(in\s+tamil|tamil\s+la|tamilil|தமிழ்)\b', 'ta'),
    (r'(?i)\b(in\s+marathi|marathi\s+madhye|मराठी)\b', 'mr'),
    (r'(?i)\b(in\s+bengali|bangla\s+te|বাংলা|বাঙালি)\b', 'bn'),
    (r'(?i)\b(in\s+kannada|kannadadalli|ಕನ್ನಡ)\b', 'kn'),
    (r'(?i)\b(in\s+gujarati|gujarati\s+ma|ગુજરાતી)\b', 'gu'),
    (r'(?i)\b(in\s+malayalam|malayalam\s+il|മലയാളം)\b', 'ml'),
    (r'(?i)\b(in\s+punjabi|punjabi\s+vich|ਪੰਜਾਬੀ)\b', 'pa'),
    (r'(?i)\b(in\s+urdu|urdu\s+mein|اردو)\b', 'ur'),
    (r'(?i)\b(in\s+english|english\s+mein)\b', 'en')
]

# Core Dictionary Translations for Instant Deterministic Offline Rendering
PHRASE_DICTIONARY: Dict[str, Dict[str, str]] = {
    "hi": {
        "Business Compliance & Certification Assessment": "व्यावसायिक अनुपालन और प्रमाणन मूल्यांकन",
        "Citizen & Consumer Protection Guide": "नागरिक और उपभोक्ता सुरक्षा मार्गदर्शिका",
        "Citizen Protection Guide": "नागरिक सुरक्षा मार्गदर्शिका",
        "Mandatory BIS Scheme": "अनिवार्य बीआईएस प्रमाणन योजना",
        "Enforcing Statutory Authorities": "लागू करने वाले वैधानिक प्राधिकरण",
        "Key Applicable Indian Standards (IS Codes)": "प्रमुख लागू भारतीय मानक (IS कोड)",
        "Mandatory Technical Specifications & Quality Thresholds": "अनिवार्य तकनीकी विनिर्देश और गुणवत्ता सीमाएं",
        "Actionable Next Steps for Your Business": "आपके व्यवसाय के लिए आवश्यक अगले कदम",
        "What Indian Consumers Must Check Before Purchasing": "भारतीय उपभोक्ताओं को खरीदारी से पहले क्या जांचना चाहिए",
        "How to Verify on Official BIS Care Mobile App": "आधिकारिक BIS Care मोबाइल ऐप पर प्रामाणिकता कैसे सत्यापित करें",
        "Open the BIS Care App": "BIS Care ऐप खोलें (Android और iOS पर उपलब्ध)",
        "Tap 'Verify License Details' or 'Verify HUID'": "'लाइसेंस विवरण सत्यापित करें' या 'HUID सत्यापित करें' पर टैप करें",
        "Authentic ISI / BIS Quality Mark": "प्रामाणिक ISI / BIS गुणवत्ता चिह्न",
        "License Number": "लाइसेंस संख्या (CM/L संख्या या 6-अंकीय HUID)",
        "Bureau of Indian Standards": "भारतीय मानक ब्यूरो (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "स्कीम-I (ISI मार्क प्रमाणन योजना)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "स्कीम-II (अनिवार्य पंजीकरण योजना - CRS)",
        "Total Published Standards in Force": "लागू कुल प्रकाशित मानक",
        "Official Notice from BIS Intelligent Assistant": "बीआईएस इंटेलिजेंट असिस्टेंट से आधिकारिक सूचना"
    },
    "te": {
        "Business Compliance & Certification Assessment": "వ్యాపార సమ్మతి మరియు ధృవీకరణ అంచనా",
        "Citizen & Consumer Protection Guide": "పౌర మరియు వినియోగదారుల రక్షణ మార్గదర్శి",
        "Citizen Protection Guide": "పౌర భద్రతా మార్గదర్శి",
        "Mandatory BIS Scheme": "తప్పనిసరి BIS సర్టిఫికేషన్ స్కీమ్",
        "Enforcing Statutory Authorities": "అమలుపరిచే చట్టబద్ధమైన అధికార సంస్థలు",
        "Key Applicable Indian Standards (IS Codes)": "ముఖ్యమైన వర్తించే భారతీయ ప్రమాణాలు (IS కోడ్‌లు)",
        "Mandatory Technical Specifications & Quality Thresholds": "తప్పనిసరి సాంకేతిక నిర్దేశాలు మరియు నాణ్యత పరిమితులు",
        "Actionable Next Steps for Your Business": "మీ వ్యాపారం కోసం తదుపరి అవసరమైన చర్యలు",
        "What Indian Consumers Must Check Before Purchasing": "భారతీయ వినియోగదారులు కొనుగోలు చేయడానికి ముందు ఏమి తనిఖీ చేయాలి",
        "How to Verify on Official BIS Care Mobile App": "అధికారిక BIS Care మొబైల్ యాప్‌లో ఎలా ధృవీకరించాలి",
        "Open the BIS Care App": "BIS Care యాప్‌ను తెరవండి (Android & iOS లో అందుబాటులో ఉంది)",
        "Tap 'Verify License Details' or 'Verify HUID'": "'లైసెన్స్ వివరాలను ధృవీకరించండి' లేదా 'HUIDని ధృవీకరించండి' పై నొక్కండి",
        "Authentic ISI / BIS Quality Mark": "ప్రామాణికమైన ISI / BIS నాణ్యత గుర్తు",
        "License Number": "లైసెన్స్ నంబర్ (CM/L సంఖ్య లేదా 6-అంకెల HUID)",
        "Bureau of Indian Standards": "బ్యూరో ఆఫ్ ఇండియన్ స్టాండర్డ్స్ (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "స్కీమ్-I (ISI మార్క్ సర్టిఫికేషన్ స్కీమ్)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "స్కీమ్-II (తప్పనిసరి రిజిస్ట్రేషన్ స్కీమ్ - CRS)",
        "Total Published Standards in Force": "ప్రస్తుతం అమల్లో ఉన్న మొత్తం ప్రమాణాలు",
        "Official Notice from BIS Intelligent Assistant": "BIS ఇంటెలిజెంట్ అసిస్టెంట్ నుండి అధికారిక నోటీసు"
    },
    "ta": {
        "Business Compliance & Certification Assessment": "வணிக இணக்கம் மற்றும் சான்றிதழ் மதிப்பீடு",
        "Citizen & Consumer Protection Guide": "குடிமக்கள் மற்றும் நுகர்வோர் பாதுகாப்பு வழிகாட்டி",
        "Citizen Protection Guide": "குடிமக்கள் பாதுகாப்பு வழிகாட்டி",
        "Mandatory BIS Scheme": "கட்டாய BIS சான்றிதழ் திட்டம்",
        "Enforcing Statutory Authorities": "அமல்படுத்தும் சட்டப்பூர்வ அதிகார அமைப்புகள்",
        "Key Applicable Indian Standards (IS Codes)": "முக்கியமான பொருந்தக்கூடிய இந்திய தரநிலைகள் (IS குறியீடுகள்)",
        "Mandatory Technical Specifications & Quality Thresholds": "கட்டாய தொழில்நுட்ப விவரக்குறிப்புகள் மற்றும் தர வரம்புகள்",
        "Actionable Next Steps for Your Business": "உங்கள் வணிகத்திற்கான அடுத்தடுத்த படிகள்",
        "What Indian Consumers Must Check Before Purchasing": "இந்திய நுகர்வோர் வாங்குவதற்கு முன் என்ன சரிபார்க்க வேண்டும்",
        "How to Verify on Official BIS Care Mobile App": "அதிகாரப்பூர்வ BIS Care மொபைல் செயலியில் எவ்வாறு சரிபார்ப்பது",
        "Open the BIS Care App": "BIS Care செயலியைத் திறக்கவும்",
        "Tap 'Verify License Details' or 'Verify HUID'": "'உரிம விவரங்களைச் சரிபார்க்கவும்' அல்லது 'HUID சரிபார்க்கவும்' என்பதைத் தட்டவும்",
        "Authentic ISI / BIS Quality Mark": "உண்மையான ISI / BIS தர முத்திரை",
        "License Number": "உரிம எண் (CM/L எண் அல்லது 6 இலக்க HUID)",
        "Bureau of Indian Standards": "இந்திய தரநிலைகள் பணியகம் (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "திட்டம்-I (ISI முத்திரை சான்றிதழ் திட்டம்)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "திட்டம்-II (கட்டாயப் பதிவுத் திட்டம் - CRS)",
        "Total Published Standards in Force": "நடைமுறையில் உள்ள மொத்த வெளியிடப்பட்ட தரநிலைகள்",
        "Official Notice from BIS Intelligent Assistant": "BIS நுண்ணறிவு உதவியாளரிடமிருந்து அதிகாரப்பூர்வ அறிவிப்பு"
    },
    "mr": {
        "Business Compliance & Certification Assessment": "व्यवसाय अनुपालन आणि प्रमाणन मूल्यांकन",
        "Citizen & Consumer Protection Guide": "नागरिक आणि ग्राहक संरक्षण मार्गदर्शक",
        "Citizen Protection Guide": "नागरिक संरक्षण मार्गदर्शक",
        "Mandatory BIS Scheme": "अनिवार्य बीआयएस योजना",
        "Enforcing Statutory Authorities": "अंमलबजावणी करणारे वैधानिक प्राधिकरण",
        "Key Applicable Indian Standards (IS Codes)": "प्रमुख लागू भारतीय मानके (IS कोड)",
        "Mandatory Technical Specifications & Quality Thresholds": "अनिवार्य तांत्रिक वैशिष्ट्ये आणि गुणवत्ता मर्यादा",
        "Actionable Next Steps for Your Business": "तुमच्या व्यवसायासाठी पुढील आवश्यक पावले",
        "What Indian Consumers Must Check Before Purchasing": "भारतीय ग्राहकांनी खरेदी करण्यापूर्वी काय तपासले पाहिजे",
        "How to Verify on Official BIS Care Mobile App": "अधिकृत BIS Care मोबाइल अॅपवर पडताळणी कशी करावी",
        "Open the BIS Care App": "BIS Care अॅप उघडा",
        "Tap 'Verify License Details' or 'Verify HUID'": "'परवाना तपशील पडताळा' किंवा 'HUID पडताळा' वर टॅप करा",
        "Authentic ISI / BIS Quality Mark": "अस्सल ISI / BIS गुणवत्ता चिन्ह",
        "License Number": "परवाना क्रमांक (CM/L किंवा 6-अंकी HUID)",
        "Bureau of Indian Standards": "भारतीय मानक ब्युरो (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "योजना-I (ISI मार्क प्रमाणन योजना)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "योजना-II (अनिवार्य नोंदणी योजना - CRS)",
        "Total Published Standards in Force": "लागू असलेली एकूण प्रकाशित मानके",
        "Official Notice from BIS Intelligent Assistant": "BIS इंटेलिजंट असिस्टंटकडून अधिकृत सूचना"
    },
    "bn": {
        "Business Compliance & Certification Assessment": "ব্যবসায়িক সম্মতি এবং সার্টিফিকেশন মূল্যায়ন",
        "Citizen & Consumer Protection Guide": "নাগরিক ও ভোক্তা সুরক্ষা নির্দেশিকা",
        "Citizen Protection Guide": "নাগরিক সুরক্ষা নির্দেশিকা",
        "Mandatory BIS Scheme": "বাধ্যতামূলক BIS সার্টিফিকেশন স্কিম",
        "Enforcing Statutory Authorities": "বাস্তবায়নকারী সংবিধিবদ্ধ কর্তৃপক্ষ",
        "Key Applicable Indian Standards (IS Codes)": "প্রধান প্রযোজ্য ভারতীয় মান (IS কোড)",
        "Mandatory Technical Specifications & Quality Thresholds": "বাধ্যতামূলক প্রযুক্তিগত বৈশিষ্ট্য এবং গুণমান সীমা",
        "Actionable Next Steps for Your Business": "আপনার ব্যবসার জন্য পরবর্তী কার্যকর পদক্ষেপ",
        "What Indian Consumers Must Check Before Purchasing": "ভারতীয় ভোক্তাদের কেনার আগে কী পরীক্ষা করা উচিত",
        "How to Verify on Official BIS Care Mobile App": "অফিসিয়াল BIS Care মোবাইল অ্যাপে কীভাবে যাচাই করবেন",
        "Open the BIS Care App": "BIS Care অ্যাপটি খুলুন",
        "Tap 'Verify License Details' or 'Verify HUID'": "'লাইসেন্সের বিবরণ যাচাই করুন' বা 'HUID যাচাই করুন' এ আলতো চাপুন",
        "Authentic ISI / BIS Quality Mark": "প্রামাণিক ISI / BIS গুণমান চিহ্ন",
        "License Number": "লাইসেন্স নম্বর (CM/L নম্বর বা ৬-সংখ্যার HUID)",
        "Bureau of Indian Standards": "ব্যুরো অফ ইন্ডিয়ান স্ট্যান্ডার্ডস (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "স্কিম-I (ISI মার্ক সার্টিফিকেশন স্কিম)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "স্কিম-II (বাধ্যতামূলক নিবন্ধন স্কিম - CRS)",
        "Total Published Standards in Force": "বর্তমানে বলবৎ মোট প্রকাশিত মান",
        "Official Notice from BIS Intelligent Assistant": "BIS ইন্টেলিজেন্ট অ্যাসিস্ট্যান্ট থেকে অফিসিয়াল নোটিশ"
    },
    "kn": {
        "Business Compliance & Certification Assessment": "ವ್ಯಾಪಾರ ಅನುಸರಣೆ ಮತ್ತು ಪ್ರಮಾಣೀಕರಣ ಮೌಲ್ಯಮಾಪನ",
        "Citizen & Consumer Protection Guide": "ನಾಗರಿಕ ಮತ್ತು ಗ್ರಾಹಕ ರಕ್ಷಣಾ ಮಾರ್ಗದರ್ಶಿ",
        "Citizen Protection Guide": "ನಾಗರಿಕ ರಕ್ಷಣಾ ಮಾರ್ಗದರ್ಶಿ",
        "Mandatory BIS Scheme": "ಕಡ್ಡಾಯ ಬಿಐಎಸ್ ಪ್ರಮಾಣೀಕರಣ ಯೋಜನೆ",
        "Enforcing Statutory Authorities": "ಅನುಷ್ಠಾನಗೊಳಿಸುವ ಶಾಸನಬದ್ಧ ಪ್ರಾಧಿಕಾರಗಳು",
        "Key Applicable Indian Standards (IS Codes)": "ಪ್ರಮುಖ ಅನ್ವಯವಾಗುವ ಭಾರತೀಯ ಮಾನದಂಡಗಳು (IS ಕೋಡ್‌ಗಳು)",
        "Mandatory Technical Specifications & Quality Thresholds": "ಕಡ್ಡಾಯ ತಾಂತ್ರಿಕ ವಿಶೇಷಣಗಳು ಮತ್ತು ಗುಣಮಟ್ಟದ ಮಿತಿಗಳು",
        "Actionable Next Steps for Your Business": "ನಿಮ್ಮ ವ್ಯಾಪಾರಕ್ಕಾಗಿ ಮುಂದಿನ ಅಗತ್ಯ ಕ್ರಮಗಳು",
        "What Indian Consumers Must Check Before Purchasing": "ಭಾರತೀಯ ಗ್ರಾಹಕರು ಖರೀದಿಸುವ ಮುನ್ನ ಏನು ಪರಿಶೀಲಿಸಬೇಕು",
        "How to Verify on Official BIS Care Mobile App": "ಅಧಿಕೃತ BIS Care ಮೊಬೈಲ್ ಆಪ್‌ನಲ್ಲಿ ಹೇಗೆ ಪರಿಶೀಲಿಸುವುದು",
        "Open the BIS Care App": "BIS Care ಆಪ್ ತೆರೆಯಿರಿ",
        "Tap 'Verify License Details' or 'Verify HUID'": "'ಪರವಾನಗಿ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ' ಅಥವಾ 'HUID ಪರಿಶೀಲಿಸಿ' ಮೇಲೆ ಟ್ಯಾಪ್ ಮಾಡಿ",
        "Authentic ISI / BIS Quality Mark": "ಅಧಿಕೃತ ISI / BIS ಗುಣಮಟ್ಟದ ಗುರುತು",
        "License Number": "ಪರವಾನಗಿ ಸಂಖ್ಯೆ (CM/L ಅಥವಾ 6-ಅಂಕಿಯ HUID)",
        "Bureau of Indian Standards": "ಭಾರತೀಯ ಮಾನಕಗಳ ಬ್ಯೂರೋ (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "ಸ್ಕೀಮ್-I (ISI ಮಾರ್ಕ್ ಪ್ರಮಾಣೀಕರಣ ಯೋಜನೆ)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "ಸ್ಕೀಮ್-II (ಕಡ್ಡಾಯ ನೋಂದಣಿ ಯೋಜನೆ - CRS)",
        "Total Published Standards in Force": "ಚಾಲ್ತಿಯಲ್ಲಿರುವ ಒಟ್ಟು ಪ್ರಕಟಿತ ಮಾನದಂಡಗಳು",
        "Official Notice from BIS Intelligent Assistant": "BIS ಇಂಟೆಲಿಜೆಂಟ್ ಅಸಿಸ್ಟೆಂಟ್‌ನಿಂದ ಅಧಿಕೃತ ಸೂಚನೆ"
    },
    "gu": {
        "Business Compliance & Certification Assessment": "વ્યવસાયિક પાલન અને પ્રમાણપત્ર મૂલ્યાંકન",
        "Citizen & Consumer Protection Guide": "નાગરિક અને ગ્રાહક સુરક્ષા માર્ગદર્શિકા",
        "Citizen Protection Guide": "નાગરિક સુરક્ષા માર્ગદર્શિકા",
        "Mandatory BIS Scheme": "ફરજિયાત BIS પ્રમાણપત્ર યોજના",
        "Enforcing Statutory Authorities": "અમલીકરણ સત્તાવાળાઓ",
        "Key Applicable Indian Standards (IS Codes)": "મુખ્ય લાગુ ભારતીય ધોરણો (IS કોડ્સ)",
        "Mandatory Technical Specifications & Quality Thresholds": "ફરજિયાત તકનીકી વિશિષ્ટતાઓ અને ગુણવત્તા મર્યાદાઓ",
        "Actionable Next Steps for Your Business": "તમારા વ્યવસાય માટે આગળના જરૂરી પગલાં",
        "What Indian Consumers Must Check Before Purchasing": "ભારતીય ગ્રાહકોએ ખરીદી કરતા પહેલા શું તપાસવું જોઈએ",
        "How to Verify on Official BIS Care Mobile App": "સત્તાવાર BIS Care મોબાઇલ એપ્લિકેશન પર કેવી રીતે ચકાસણી કરવી",
        "Open the BIS Care App": "BIS Care એપ ખોલો",
        "Tap 'Verify License Details' or 'Verify HUID'": "'લાઇસન્સ વિગતો ચકાસો' અથવા 'HUID ચકાસો' પર ટેપ કરો",
        "Authentic ISI / BIS Quality Mark": "અધિકૃત ISI / BIS ગુણવત્તા માર્ક",
        "License Number": "લાઇસન્સ નંબર (CM/L નંબર અથવા 6-અંકનો HUID)",
        "Bureau of Indian Standards": "બ્યુરો ઓફ ઇન્ડિયન સ્ટાન્ડર્ડ્સ (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "સ્કીમ-I (ISI માર્ક પ્રમાણપત્ર યોજના)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "સ્કીમ-II (ફરજિયાત નોંધણી યોજના - CRS)",
        "Total Published Standards in Force": "અમલમાં રહેલા કુલ પ્રકાશિત ધોરણો",
        "Official Notice from BIS Intelligent Assistant": "BIS ઇન્ટેલિજન્ટ આસિસ્ટન્ટ તરફથી સત્તાવાર નોટિસ"
    },
    "ml": {
        "Business Compliance & Certification Assessment": "ബിസിനസ്സ് അനുസരണവും സർട്ടിഫിക്കേഷൻ വിലയിരുത്തലും",
        "Citizen & Consumer Protection Guide": "പൗരന്മാരുടെയും ഉപഭോക്താക്കളുടെയും സംരക്ഷണ ഗൈഡ്",
        "Citizen Protection Guide": "പൗര സംരക്ഷണ ഗൈഡ്",
        "Mandatory BIS Scheme": "നിർബന്ധിത BIS സർട്ടിഫിക്കേഷൻ സ്കീം",
        "Enforcing Statutory Authorities": "നടപ്പിലാക്കുന്ന നിയമപരമായ അധികാര സ്ഥാപനങ്ങൾ",
        "Key Applicable Indian Standards (IS Codes)": "പ്രധാന ബാധകമായ ഇന്ത്യൻ മാനദണ്ഡങ്ങൾ (IS കോഡുകൾ)",
        "Mandatory Technical Specifications & Quality Thresholds": "നിർബന്ധിത സാങ്കേതിക സവിശേഷതകളും ഗുണനിലവാര പരിധികളും",
        "Actionable Next Steps for Your Business": "നിങ്ങളുടെ ബിസിനസ്സിനായുള്ള അടുത്ത ഘട്ടങ്ങൾ",
        "What Indian Consumers Must Check Before Purchasing": "വാങ്ങുന്നതിന് മുമ്പ് ഉപഭോക്താക്കൾ എന്തൊക്കെ പരിശോധിക്കണം",
        "How to Verify on Official BIS Care Mobile App": "ഔദ്യോഗിക BIS Care മൊബൈൽ ആപ്പിൽ എങ്ങനെ പരിശോധിക്കാം",
        "Open the BIS Care App": "BIS Care ആപ്പ് തുറക്കുക",
        "Tap 'Verify License Details' or 'Verify HUID'": "'ലൈസൻസ് വിശദാംശങ്ങൾ പരിശോധിക്കുക' അല്ലെങ്കിൽ 'HUID പരിശോധിക്കുക' ടാപ്പ് ചെയ്യുക",
        "Authentic ISI / BIS Quality Mark": "യഥാർത്ഥ ISI / BIS ഗുണനിലവാര മുദ്ര",
        "License Number": "ലൈസൻസ് നമ്പർ (CM/L നമ്പർ അല്ലെങ്കിൽ 6-അക്ക HUID)",
        "Bureau of Indian Standards": "ബ്യൂറോ ഓഫ് ഇന്ത്യൻ സ്റ്റാൻഡേർഡ്സ് (BIS)",
        "Scheme-I (ISI Mark Certification Scheme)": "സ്കീം-I (ISI മാർക്ക് സർട്ടിഫിക്കേഷൻ സ്കീം)",
        "Scheme-II (Compulsory Registration Scheme - CRS)": "സ്കീം-II (നിർബന്ധിത രജിസ്ട്രേഷൻ സ്കീം - CRS)",
        "Total Published Standards in Force": "നിലവിലുള്ള ആകെ പ്രസിദ്ധീകരിച്ച മാനദണ്ഡങ്ങൾ",
        "Official Notice from BIS Intelligent Assistant": "BIS ഇന്റലിജന്റ് അസിസ്റ്റന്റിൽ നിന്നുള്ള ഔദ്യോഗിക അറിയിപ്പ്"
    }
}


MYMEMORY_LANG_CODES: Dict[str, str] = {
    "hi": "hi-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "kn": "kn-IN",
    "gu": "gu-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "ur": "ur-PK"
}


class MultilingualTranslator:
    """
    High-accuracy multilingual translation service for Indian Standards & Food Safety.
    Supports English, Hindi, Telugu, Tamil, Marathi, Bengali, Kannada, Gujarati, Malayalam, Punjabi, Urdu.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def detect_requested_language(self, query: str) -> Optional[str]:
        """Checks if the user explicitly requested a specific language in the prompt or wrote in an Indic script."""
        for pattern, lang_code in LANGUAGE_TRIGGER_REGEX:
            if re.search(pattern, query):
                return lang_code
        # Auto-detect native Indic scripts directly from unicode blocks
        if re.search(r'[\u0B80-\u0BFF]', query):
            return 'ta'  # Tamil
        if re.search(r'[\u0C00-\u0C7F]', query):
            return 'te'  # Telugu
        if re.search(r'[\u0C80-\u0CFF]', query):
            return 'kn'  # Kannada
        if re.search(r'[\u0980-\u09FF]', query):
            return 'bn'  # Bengali
        if re.search(r'[\u0A80-\u0AFF]', query):
            return 'gu'  # Gujarati
        if re.search(r'[\u0D00-\u0D7F]', query):
            return 'ml'  # Malayalam
        if re.search(r'[\u0A00-\u0A7F]', query):
            return 'pa'  # Punjabi
        if re.search(r'[\u0600-\u06FF]', query):
            return 'ur'  # Urdu
        if re.search(r'[\u0900-\u097F]', query):
            return 'hi'  # Hindi / Devanagari
        return None

    def _translate_gtx(self, text: str, target_lang: str) -> Optional[str]:
        """High-speed neural translation via direct Google GTX endpoint when online."""
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    translated_chunks = [chunk[0] for chunk in data[0] if chunk and chunk[0]]
                    result = "".join(translated_chunks)
                    if result and len(result.strip()) > 0:
                        return result
        except Exception as e:
            logger.debug(f"GTX translation attempt skipped/failed: {e}")
        return None

    def translate_text(self, text: str, target_lang: str) -> str:
        """
        Translates a single string or sentence into the target Indian language.
        Preserves technical codes, percentages, numbers, and units.
        """
        if not text or not text.strip() or not target_lang or target_lang.lower() == "en":
            return text

        target_lang = target_lang.lower()
        cache_key = f"txt:{target_lang}:{text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. High-speed Google GTX neural translation (fast 1.5s timeout)
        gtx_res = self._translate_gtx(text, target_lang)
        if gtx_res:
            self._cache[cache_key] = gtx_res
            return gtx_res

        # 2. Deep-Translator MyMemory Fallback (only if available)
        target_code = MYMEMORY_LANG_CODES.get(target_lang)
        if target_code:
            try:
                from deep_translator import MyMemoryTranslator
                translator = MyMemoryTranslator(source="en-IN", target=target_code)
                trans = translator.translate(text)
                if trans and len(trans.strip()) > 0:
                    self._cache[cache_key] = trans
                    return trans
            except Exception as e:
                logger.debug(f"MyMemory fallback failed: {e}")

        # 3. Deterministic dictionary fallback (100% offline, zero network)
        dict_map = PHRASE_DICTIONARY.get(target_lang, {})
        translated = text
        for eng_phrase, native_phrase in dict_map.items():
            translated = translated.replace(eng_phrase, native_phrase)

        self._cache[cache_key] = translated
        return translated

    def translate_markdown(self, markdown_text: str, target_lang: str) -> str:
        """
        Translates markdown response into target Indian language.
        Preserves markdown headings, tables, bullet points, and code blocks.
        Supports Hindi, Telugu, Tamil, Marathi, Bengali, Kannada, Gujarati, Malayalam, Punjabi, and Urdu.
        """
        if not target_lang or target_lang.lower() == "en" or not markdown_text or not markdown_text.strip():
            return markdown_text

        target_lang = target_lang.lower()
        cache_key = f"md:{target_lang}:{hash(markdown_text)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Gemini GenAI live neural translation if configured
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL or "gemini-3.8-flash")
                lang_meta = SUPPORTED_LANGUAGES.get(target_lang, {"name": target_lang, "native": target_lang})
                prompt = (
                    f"Translate the following Bureau of Indian Standards (BIS) and food safety response "
                    f"into fluent, professional {lang_meta['name']} ({lang_meta['native']}).\n"
                    f"Preserve all Markdown formatting (headings, bullet points, tables, bold text, and IS Standard numbers like IS 14543 or numbers/units like 20 ppb, 500 mg/L).\n\n"
                    f"Text to translate:\n{markdown_text}"
                )
                res = model.generate_content(prompt)
                if res.text and len(res.text.strip()) > 20:
                    self._cache[cache_key] = res.text
                    return res.text
            except Exception as e:
                logger.debug(f"Gemini live translation fallback: {e}")

        # 2. Extract code blocks so they are not mutated or mangled
        code_blocks = []
        def _save_code_block(match):
            code_blocks.append(match.group(0))
            return f"___CODE_BLOCK_{len(code_blocks)-1}___"

        text_no_code = re.sub(r'```[\s\S]*?```', _save_code_block, markdown_text)

        # 3. Translate in paragraph chunks (< 1500 chars) using neural GTX
        paragraphs = text_no_code.split("\n\n")
        translated_paragraphs = []

        for p in paragraphs:
            stripped = p.strip()
            if not stripped or stripped.startswith("___CODE_BLOCK_"):
                translated_paragraphs.append(p)
                continue

            if len(p) < 1500:
                trans_p = self.translate_text(p, target_lang)
                translated_paragraphs.append(trans_p)
            else:
                # If paragraph is unusually long, split by lines
                lines = p.split("\n")
                trans_lines = []
                for line in lines:
                    if not line.strip() or line.strip().startswith("http") or line.strip().startswith("---"):
                        trans_lines.append(line)
                    else:
                        trans_lines.append(self.translate_text(line, target_lang))
                translated_paragraphs.append("\n".join(trans_lines))

        result_text = "\n\n".join(translated_paragraphs)

        # 4. Restore preserved code blocks
        for idx, cb in enumerate(code_blocks):
            result_text = result_text.replace(f"___CODE_BLOCK_{idx}___", cb)

        # Add language indicator banner
        lang_info = SUPPORTED_LANGUAGES.get(target_lang, {"name": target_lang, "flag": "🇮🇳", "native": target_lang})
        header_banner = f"> 🌐 **अनुवाद / Translation:** `{lang_info['flag']} {lang_info['name']} ({lang_info['native']})`\n\n"
        final_text = header_banner + result_text
        self._cache[cache_key] = final_text
        return final_text

    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        return SUPPORTED_LANGUAGES


multilingual_translator = MultilingualTranslator()


