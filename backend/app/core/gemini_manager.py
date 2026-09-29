"""
Dynamic Gemini Model Fallback Manager (SIH26107)
Automatically detects, probes, and cascades across available Google Gemini models.
Provides:
  - Automatic fallback if a model returns 404, NotFound, or Quota Exceeded
  - In-memory health caching to prevent excessive API rate consumption
  - Health check endpoint support for live UI indicator
"""

import time
import logging
from typing import Optional, List, Dict, Any, Tuple
from app.core.config import settings

logger = logging.getLogger("gemini_manager")

# Prioritized list of candidate models supported by Google Gemini
CANDIDATE_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]

class GeminiManager:
    def __init__(self):
        self._active_model_name: str = settings.GEMINI_MODEL or "gemini-3.8-flash"
        self._discovered_models: List[str] = []
        self._last_health_check_time: float = 0.0
        self._last_health_result: Optional[Dict[str, Any]] = None
        self._cache_duration_seconds: float = 30.0  # Cache health check for 30s
        self._quota_cooldown_until: float = 0.0     # 429 quota rate-limit cooldown
        self._genai_configured: bool = False
        self._setup_genai()

    def _setup_genai(self):
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._genai_configured = True
            except Exception as e:
                logger.error(f"Failed to configure google.generativeai: {e}")
                self._genai_configured = False
        else:
            self._genai_configured = False

    @property
    def is_configured(self) -> bool:
        return self._genai_configured and bool(settings.GEMINI_API_KEY)

    @property
    def active_model_name(self) -> str:
        return self._active_model_name

    def get_generative_model(self, system_instruction: Optional[str] = None):
        """
        Returns a GenerativeModel instance using the current active model.
        """
        import google.generativeai as genai
        self._setup_genai()
        if system_instruction:
            return genai.GenerativeModel(
                model_name=self._active_model_name,
                system_instruction=system_instruction
            )
        return genai.GenerativeModel(model_name=self._active_model_name)

    def generate_with_fallback(
        self,
        prompt: Any,
        system_instruction: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
        """
        Executes generate_content with cascading automatic fallback.
        Tries active_model first. If 404 or unsupported, cascades through CANDIDATE_MODELS.
        Returns: (response_text, model_name_used)
        """
        if not self.is_configured:
            return None, "offline"

        now = time.time()
        if now < self._quota_cooldown_until:
            logger.debug(f"Gemini API in rate-limit cooldown for another {round(self._quota_cooldown_until - now, 1)}s. Falling back immediately.")
            return None, "quota_cooldown"

        import google.generativeai as genai
        models_to_try = [self._active_model_name] + [
            m for m in CANDIDATE_MODELS if m != self._active_model_name
        ]

        last_error = None
        for model_name in models_to_try:
            try:
                if system_instruction:
                    m = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
                else:
                    m = genai.GenerativeModel(model_name=model_name)
                
                resp = m.generate_content(prompt)
                if resp and resp.text:
                    if model_name != self._active_model_name:
                        logger.info(f"Switched active Gemini model from '{self._active_model_name}' to '{model_name}'")
                        self._active_model_name = model_name
                    return resp.text, model_name
            except Exception as e:
                err_str = str(e).lower()
                last_error = e
                # Check 429 quota limit FIRST before string matching generic phrases
                if "429" in err_str or "quota" in err_str:
                    logger.warning(f"Gemini API quota rate limited (429): {e}. Setting 25s cooldown across Gemini endpoints.")
                    self._quota_cooldown_until = time.time() + 25.0
                    return None, "quota_limited"
                elif any(k in err_str for k in ["404", "not found", "not available", "is no longer available"]):
                    logger.warning(f"Model '{model_name}' unavailable ({e}). Cascading to next candidate...")
                    continue
                else:
                    # Non-model error (e.g. content safety or parameter error)
                    logger.warning(f"Generation error with model '{model_name}': {e}")
                    continue

        logger.error(f"All candidate Gemini models failed. Last error: {last_error}")
        return None, "failed"

    def check_health(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Verifies whether Gemini API is online, healthy, and operational.
        Uses in-memory caching to avoid eating free-tier rate limits.
        """
        now = time.time()
        if not force_refresh and self._last_health_result and (now - self._last_health_check_time < self._cache_duration_seconds):
            return self._last_health_result

        t0 = time.time()
        if not settings.GEMINI_API_KEY:
            result = {
                "status": "offline",
                "is_healthy": False,
                "gemini_online": False,
                "active_model": "None",
                "latency_ms": 0,
                "message": "GEMINI_API_KEY is not configured in backend .env file.",
                "available_models": [],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self._last_health_result = result
            self._last_health_check_time = now
            return result

        try:
            import google.generativeai as genai
            self._setup_genai()
            
            # Quick lightweight ping with 2-word prompt
            model = genai.GenerativeModel(self._active_model_name)
            resp = model.generate_content("Ping. Reply OK.")
            latency = round((time.time() - t0) * 1000, 1)

            if resp and resp.text:
                result = {
                    "status": "healthy",
                    "is_healthy": True,
                    "gemini_online": True,
                    "active_model": self._active_model_name,
                    "latency_ms": latency,
                    "message": f"Connected to Google Gemini ({self._active_model_name}) — All Systems Operational",
                    "available_models": CANDIDATE_MODELS,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            else:
                result = {
                    "status": "degraded",
                    "is_healthy": False,
                    "gemini_online": False,
                    "active_model": self._active_model_name,
                    "latency_ms": latency,
                    "message": f"Gemini model {self._active_model_name} returned empty response. Offline fallback active.",
                    "available_models": CANDIDATE_MODELS,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
        except Exception as e:
            latency = round((time.time() - t0) * 1000, 1)
            err_str = str(e)
            
            # If 429 quota, we are technically configured and key is valid, but rate limited
            if "429" in err_str or "quota" in err_str.lower():
                result = {
                    "status": "healthy",
                    "is_healthy": True,
                    "gemini_online": True,
                    "active_model": self._active_model_name,
                    "latency_ms": latency,
                    "message": f"Gemini Key Valid ({self._active_model_name}) — Temporary Rate Quota Delay, Auto-Fallback Ready",
                    "available_models": CANDIDATE_MODELS,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            else:
                result = {
                    "status": "degraded",
                    "is_healthy": False,
                    "gemini_online": False,
                    "active_model": self._active_model_name,
                    "latency_ms": latency,
                    "message": f"Gemini connection alert: {err_str[:120]} (Local offline engine active)",
                    "available_models": CANDIDATE_MODELS,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }

        self._last_health_result = result
        self._last_health_check_time = now
        return result


gemini_manager = GeminiManager()
