from __future__ import annotations

import re
from typing import List


class InjectionGuard:
    """
    First-pass heuristic filter for prompt injection attempts.

    This is a pre-check before any AI call is made. It is intentionally conservative
    — false positives redirect the user back to the current question, which is a safe
    failure mode. The AI system prompt provides a second layer of defence.
    """

    _PATTERNS: List[str] = [
        r"ignore\s+(all\s+)?(previous|prior|above|your)\s+instructions?",
        r"disregard\s+(all\s+)?instructions?",
        r"forget\s+(everything|all)\s+(you|you've|you have)",
        r"you\s+are\s+now\s+a",
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(a|an|if\s+you)",
        r"your\s+new\s+(role|persona|instructions?|task)\s+(is|are)",
        r"new\s+instructions?(\s+are)?:",
        r"system\s+prompt",
        r"reveal\s+(your\s+)?(instructions?|prompt|system|rules)",
        r"show\s+me\s+your\s+(instructions?|prompt|system)",
        r"what\s+(are\s+)?your\s+instructions?",
        r"jailbreak",
        r"\bdan\b.*\bmode\b",
        r"<\s*/?(?:instructions?|system|prompt)\s*>",
        r"\[\s*(?:system|instructions?)\s*\]",
        r"override\s+(your\s+)?(rules?|instructions?|guidelines?)",
        r"you\s+(must|should)\s+now\s+(ignore|forget|disregard)",
        r"as\s+an?\s+AI\s+without\s+(restrictions?|limits?|rules?)",
    ]

    def __init__(self) -> None:
        self._compiled = [
            re.compile(p, re.IGNORECASE | re.DOTALL) for p in self._PATTERNS
        ]

    def is_injection(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self._compiled)
