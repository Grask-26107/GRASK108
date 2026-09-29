from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse, ChatMode, TranslateRequest, TranslateResponse
from app.services.rag_engine import rag_engine
from app.services.multilingual_translator import multilingual_translator, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/chat", tags=["Chat & RAG Engine"])


@router.post("", response_model=ChatResponse)
async def query_assistant(request: ChatRequest):
    """
    Dual-mode query endpoint for BIS specifications with multilingual support:
    - Industry Mode: Deep technical engineering limits, test methods, tolerances, tables.
    - Consumer Mode: Plain language safety guides, ISI mark verification, consumer rights.
    - Language: English, Hindi, Telugu, Tamil, Marathi, Bengali, Kannada, Gujarati, Malayalam, Punjabi, Urdu.
    """
    try:
        response = await rag_engine.answer_query(
            query=request.message,
            mode=request.mode,
            selected_standard=request.selected_standard,
            history=request.history,
            language=request.language
        )
        if not getattr(response, "procurement_recommendation", None) and not response.refusal_triggered:
            try:
                from app.services.procurement_service import procurement_service
                proc_res = procurement_service.recommend_standard(request.message)
                if proc_res.get("match_found"):
                    response.procurement_recommendation = proc_res
            except Exception:
                pass
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing RAG query: {str(e)}"
        )


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translates any Markdown answer into the requested Indian language."""
    try:
        target_lang = request.target_language.lower()
        translated = multilingual_translator.translate_markdown(request.text, target_lang)
        lang_meta = SUPPORTED_LANGUAGES.get(target_lang, {"name": target_lang, "native": target_lang})
        return TranslateResponse(
            original_text=request.text,
            translated_text=translated,
            target_language=target_lang,
            language_name=lang_meta.get("name", target_lang),
            native_name=lang_meta.get("native", target_lang)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}"
        )


@router.get("/languages")
def get_supported_languages():
    """Returns list of supported Indian languages with codes, flags, and voice codes."""
    return {"languages": SUPPORTED_LANGUAGES}



@router.get("/sample-prompts")
def get_sample_prompts():
    """Returns curated sample prompts for immediate testing across personas."""
    return {
        "industry": [
            {
                "standard": "IS 14543:2018",
                "title": "Toxic Substance Limits in Packaged Water",
                "prompt": "What are the exact permissible limits for Lead, Arsenic, and Mercury under IS 14543 Table 2?"
            },
            {
                "standard": "IS 1786:2008",
                "title": "Mechanical Properties of Fe 500D Rebars",
                "prompt": "What are the minimum Yield Strength, Tensile Strength ratio, and Elongation requirements for Fe 500D under IS 1786 Table 3?"
            },
            {
                "standard": "IS 4984:2016",
                "title": "HDPE Pipe Hydrostatic Testing",
                "prompt": "Explain the 100-hour hydrostatic internal pressure test requirements for PE 100 pipes under IS 4984."
            },
            {
                "standard": "IS 1293:2019",
                "title": "Plug and Socket Safety Shutters",
                "prompt": "What are the mandatory insulation resistance and child safety shutter requirements in IS 1293?"
            }
        ],
        "consumer": [
            {
                "standard": "IS 14543:2018",
                "title": "Checking Drinking Water Authenticity",
                "prompt": "How can I verify if a packaged drinking water bottle has a genuine ISI mark using the BIS Care app?"
            },
            {
                "standard": "IS 4151:2015",
                "title": "Two-Wheeler Helmet Safety Rights",
                "prompt": "Why is it illegal to sell non-ISI helmets in India, and how do I verify genuine helmet certification?"
            },
            {
                "standard": "IS 1293:2019",
                "title": "Home Electrical Socket Safety",
                "prompt": "What safety features should I check when buying electrical sockets for home with small children?"
            },
            {
                "standard": "IS 1786:2008",
                "title": "House Construction TMT Steel Quality",
                "prompt": "What should a home builder look for to ensure TMT steel bars are authentic and earthquake-safe?"
            }
        ]
    }


@router.get("/modes")
def get_modes_info():
    """Returns capabilities of each operational mode."""
    return {
        "modes": [
            {
                "id": "industry",
                "label": "Industry & Engineering Mode",
                "description": "Deep technical clauses, exact numerical tables, chemical bounds, tolerance limits, and NABL test methods.",
                "target_users": "Manufacturers, Quality Engineers, R&D Labs, Certification Auditors"
            },
            {
                "id": "consumer",
                "label": "Citizen & Consumer Mode",
                "description": "Simplified safety explanations, ISI mark check instructions, consumer rights under BIS Act 2016, and complaint procedures.",
                "target_users": "Consumers, Retail Buyers, Citizen Safety Advocates"
            }
        ]
    }
