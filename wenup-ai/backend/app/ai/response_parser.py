from __future__ import annotations

import json
import re

from app.models.conversation import ExtractionResult


def parse_extraction_response(raw: str) -> ExtractionResult:
    """
    Parse Claude's structured JSON extraction response into an ExtractionResult.

    Claude is instructed to return only JSON, but we defensively strip any accidental
    markdown code fences before parsing.
    """
    cleaned = _strip_code_fences(raw.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # If Claude returns malformed JSON, treat it as a vague answer so the
        # conversation continues rather than crashing.
        return ExtractionResult(
            is_vague=True,
            vagueness_reason="Could not parse your answer. Please try again.",
        )

    return ExtractionResult(
        extracted_value=data.get("extracted_value"),
        is_vague=bool(data.get("is_vague", False)),
        vagueness_reason=data.get("vagueness_reason"),
        best_effort_value=data.get("best_effort_value"),
        is_contradiction=bool(data.get("is_contradiction", False)),
        contradiction_detail=data.get("contradiction_detail"),
        is_advice_request=bool(data.get("is_advice_request", False)),
        is_injection=bool(data.get("is_injection", False)),
    )


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers if present."""
    pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return text
