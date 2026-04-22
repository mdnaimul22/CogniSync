"""Sensitive data masking dont expose secret key or api key"""

import re

_SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r'(api[_-]?key\s*[=:"\']+\s*)["\']?[\w\-]{8,}["\']?', re.IGNORECASE),
    re.compile(r'(token\s*[=:"\']+\s*)["\']?[\w\-]{8,}["\']?', re.IGNORECASE),
    re.compile(r'(secret\s*[=:"\']+\s*)["\']?[\w\-]{8,}["\']?', re.IGNORECASE),
    re.compile(r'(password\s*[=:"\']+\s*)["\']?[\w\-]{8,}["\']?', re.IGNORECASE),
    re.compile(r'\bnvapi-[\w\-]+'),
    re.compile(r'\bsk-[\w\-]{20,}'),
    re.compile(r'\bghp_[\w\-]{20,}'),
    re.compile(r'\bBearer\s+[\w\-]{10,}'),
]


def mask_sensitive_data(text: str) -> str:
    """Replace known secret patterns with [REDACTED] before LLM processing."""
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text
