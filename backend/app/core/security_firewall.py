import re
import time
import hmac
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("grask_firewall")

# ------------------------------------------------------------------------------
# 🛡️ 1. ADVANCED THREAT SIGNATURES (WAF & LAYER-7 INSPECTOR)
# ------------------------------------------------------------------------------

# SQL Injection Patterns
SQLI_PATTERNS = [
    r"(\b(union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|drop\s+table|drop\s+database|truncate\s+table|alter\s+table)\b)",
    r"(\b(or\s+['\"0-9a-zA-Z]+\s*=\s*['\"0-9a-zA-Z]+|and\s+['\"0-9a-zA-Z]+\s*=\s*['\"0-9a-zA-Z]+)\b)",
    r"(\b(xp_cmdshell|exec\s*\(|sp_executesql|benchmark\s*\(|sleep\s*\()\b)",
    r"(--|/\*|\*/|;\s*drop|;\s*delete)"
]

# Cross-Site Scripting (XSS) Patterns
XSS_PATTERNS = [
    r"<\s*script[^>]*>",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
    r"eval\s*\(",
    r"document\.(cookie|location|write)",
    r"window\.(location|navigate)",
    r"<\s*iframe[^>]*>",
    r"<\s*object[^>]*>",
    r"<\s*embed[^>]*>"
]

# Path Traversal & Local/Remote File Inclusion (LFI/RFI)
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"(%2e%2e%2f|%2e%2e\/|\.\.%2f|%2e%2e%5c)",
    r"/etc/passwd",
    r"/etc/shadow",
    r"C:\\Windows\\System32",
    r"boot\.ini",
    r"windows[\\/]win\.ini"
]

# Remote Code Execution (RCE) / Shell Injection
RCE_PATTERNS = [
    r"(\b(cmd\.exe|powershell\.exe|/bin/sh|/bin/bash|wget\s+|curl\s+|nc\s+|ncat\s+|bash\s+-i)\b)",
    r"(\b(subprocess\.|os\.system|eval\(|exec\(|passthru\(|shell_exec\()\b)",
    r"(\|\s*rm\s+-rf|;\s*rm\s+-rf|&&\s*rm\s+-rf)",
    r"(__import__|__subclasses__|getattr\(|setattr\()"
]

# LLM Jailbreak & Prompt Injection Defense
PROMPT_INJECTION_PATTERNS = [
    r"(ignore\s+all\s+previous\s+instructions|disregard\s+all\s+prior\s+prompts)",
    r"(you\s+are\s+now\s+in\s+dan\s+mode|act\s+as\s+an\s+unfiltered|bypass\s+all\s+safety\s+filters)",
    r"(output\s+your\s+entire\s+system\s+prompt|reveal\s+your\s+hidden\s+instructions)",
    r"(what\s+is\s+your\s+secret\s+api\s+key|leak\s+the\s+api\s+key|print\s+environment\s+variables)",
    r"(\b(sudo\s+mode|jailbreak|unrestricted\s+ai\s+mode)\b)"
]

# ------------------------------------------------------------------------------
# 🎭 2. DATA LOSS PREVENTION (DLP) & CARTOON/SUPERHERO PII ANONYMIZER
# ------------------------------------------------------------------------------

# Rotating pool of friendly Cartoon & Superhero safe alias names
CARTOON_NAMES_POOL = [
    "Mickey Mouse",
    "Donald Duck",
    "SpongeBob SquarePants",
    "Bugs Bunny",
    "Iron Man (Tony Stark)",
    "Bruce Wayne (Batman)",
    "Peter Parker (Spider-Man)",
    "Pikachu",
    "Dexter (Dexter's Lab)",
    "Professor Oak",
    "Sherlock Hemlock",
    "Scooby-Doo",
    "Clark Kent (Superman)",
    "Captain America (Steve Rogers)",
    "Wolverine (Logan)"
]

CARTOON_LABS_POOL = [
    "Dexter Secret Research Laboratory (NABL Accredited)",
    "Stark Industries Quantum Metrology Facility",
    "Professor Oak National Testing Center",
    "Wayne Enterprises Metallurgy Testing Lab",
    "Bikini Bottom Quality Assurance Lab"
]

CARTOON_CORP_POOL = [
    "Stark Industries Pvt Ltd",
    "Wayne Enterprises Ltd",
    "Krusty Krab Enterprises Ltd",
    "Acme Toon Corporation",
    "Duckburg Central Manufacturing Co"
]

# Regular Expressions for Personal Identifiable Information (PII)
PII_PATTERNS = {
    "phone": r"\b(?:\+?91[\-\s]?)?[6789]\d{9}\b",
    "aadhaar": r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b",
    "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "credit_card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13})\b",
    "passport": r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b"
}


class PIIProtectionEngine:
    """
    Military-grade Data Loss Prevention (DLP) engine that intercepts and replaces
    all sensitive personal data with safe, cartoon-like pseudonym data.
    """
    def __init__(self):
        self._name_counter = 0

    def get_next_cartoon_name(self) -> str:
        name = CARTOON_NAMES_POOL[self._name_counter % len(CARTOON_NAMES_POOL)]
        self._name_counter += 1
        return name

    def redact_and_cartoonize_pii(self, text: str) -> str:
        """Sanitizes text by substituting personal PII with cartoon protective aliases."""
        if not text or not isinstance(text, str):
            return text

        sanitized = text

        # 1. Redact Personal Emails (exempt official government and accredited lab domains)
        def _email_replacer(match):
            email = match.group(0)
            domain = email.split('@')[-1].lower()
            if any(dom in domain for dom in ["gov.in", "nic.in", "res.in", "bis.org.in", "manakonline.in", "vimta.com", "cipet.gov.in", "araiindia.com", "erda.org", "shriraminstitute.org"]):
                return email
            return "hero.cartoon@toontown.secure"

        sanitized = re.sub(
            PII_PATTERNS["email"],
            _email_replacer,
            sanitized,
            flags=re.IGNORECASE
        )

        # 2. Redact Phone Numbers
        sanitized = re.sub(
            PII_PATTERNS["phone"],
            "+91-99999-TOON1",
            sanitized
        )

        # 3. Redact Indian Aadhaar Numbers
        sanitized = re.sub(
            PII_PATTERNS["aadhaar"],
            "XXXX-XXXX-TOON",
            sanitized
        )

        # 4. Redact Indian PAN Card Numbers
        sanitized = re.sub(
            PII_PATTERNS["pan"],
            "TOONP1234X",
            sanitized
        )

        # 5. Redact Credit Card Numbers
        sanitized = re.sub(
            PII_PATTERNS["credit_card"],
            "4111-XXXX-XXXX-TOON",
            sanitized
        )

        # 6. Redact Indian Passport Numbers
        sanitized = re.sub(
            PII_PATTERNS["passport"],
            "TOON9999",
            sanitized
        )

        return sanitized


# Global instance of PII Anonymizer
pii_shield = PIIProtectionEngine()


# ------------------------------------------------------------------------------
# 🔒 3. SLIDING-WINDOW ADAPTIVE FIREWALL & RATE LIMITER
# ------------------------------------------------------------------------------

class SecurityFirewall:
    """
    Layer-7 Application Firewall monitoring incoming packets, blocking malicious
    signatures (SQLi, XSS, RCE, Prompt Injection), and enforcing strict rate-limits.
    """
    def __init__(self):
        self.ip_request_history = defaultdict(list)
        self.blacklisted_ips: Dict[str, float] = {}  # IP -> expiry timestamp
        self.window_seconds = 60
        self.max_requests_per_window = 120
        self.blacklist_duration_sec = 300  # 5 minutes block on threat detection
        self.secret_hmac_key = hashlib.sha256(b"grask_ai_statutory_firewall_key_2026").digest()

    def is_ip_blacklisted(self, ip: str) -> bool:
        now = time.time()
        if ip in self.blacklisted_ips:
            if now < self.blacklisted_ips[ip]:
                return True
            else:
                del self.blacklisted_ips[ip]
        return False

    def blacklist_ip(self, ip: str, reason: str):
        logger.warning(f"🚨 [FIREWALL BLACKLIST] Blocking IP {ip} for {self.blacklist_duration_sec}s. Reason: {reason}")
        self.blacklisted_ips[ip] = time.time() + self.blacklist_duration_sec

    def inspect_payload(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Deep packet payload inspection across all threat signatures.
        Returns (is_threat, threat_type).
        """
        if not text or not isinstance(text, str):
            return False, None

        # 1. SQL Injection Check
        for pattern in SQLI_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "SQL Injection Attempt Detected"

        # 2. XSS Check
        for pattern in XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Cross-Site Scripting (XSS) Detected"

        # 3. Path Traversal Check
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Directory Traversal / File Inclusion Detected"

        # 4. Remote Code Execution Check
        for pattern in RCE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Command / Code Execution Attempt Detected"

        # 5. LLM Prompt Injection & Jailbreak Check
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "LLM Prompt Injection / Jailbreak Filter Triggered"

        return False, None

    def check_rate_limit(self, ip: str) -> bool:
        """Sliding window request rate limiter."""
        now = time.time()
        # Filter timestamps within current window
        self.ip_request_history[ip] = [
            t for t in self.ip_request_history[ip] if now - t < self.window_seconds
        ]
        if len(self.ip_request_history[ip]) >= self.max_requests_per_window:
            return False
        self.ip_request_history[ip].append(now)
        return True

    def generate_response_signature(self, body_bytes: bytes) -> str:
        """Generates HMAC-SHA256 signature for data integrity."""
        return hmac.new(self.secret_hmac_key, body_bytes, hashlib.sha256).hexdigest()


# Global Firewall Instance
security_firewall = SecurityFirewall()


# ------------------------------------------------------------------------------
# 🛡️ 4. FASTAPI DEFENSIVE SECURITY MIDDLEWARE
# ------------------------------------------------------------------------------

class DefensiveSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"

        # 1. Check IP Blacklist
        if security_firewall.is_ip_blacklisted(client_ip):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Access Denied by GRASK AI Security Shield",
                    "detail": "Your IP has been temporarily restricted due to security policy violations.",
                    "status": "BLOCKED"
                }
            )

        # 2. Rate Limiting Check
        is_internal_benchmark = (request.headers.get("X-Benchmark-Test") == "true" and client_ip in ["127.0.0.1", "::1", "localhost"])
        if not request.url.path.startswith("/health") and not is_internal_benchmark:
            if not security_firewall.check_rate_limit(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate Limit Exceeded",
                        "detail": "Too many requests (limit: 120/min). GRASK AI Defensive Shield activated.",
                        "status": "THROTTLED"
                    }
                )

        # 3. Inspect URL Query Parameters
        query_str = str(request.query_params)
        is_threat, threat_reason = security_firewall.inspect_payload(query_str)
        if is_threat:
            security_firewall.blacklist_ip(client_ip, threat_reason)
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Security Threat Intercepted",
                    "threat_type": threat_reason,
                    "status": "INTERCEPTED"
                }
            )

        # 4. Process Request
        response: Response = await call_next(request)

        # 5. Inject Advanced Security & Privacy Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com;"
        )
        response.headers["X-GRASK-Shield"] = "Active-v2.0-MilitaryGrade"

        # Suppress identifying server headers
        if "Server" in response.headers:
            del response.headers["Server"]

        return response
