from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel


class ExtractionResult(BaseModel):
    """Parsed response from Claude during the conversation/extraction phase."""

    extracted_value: Optional[Any] = None
    is_vague: bool = False
    vagueness_reason: Optional[str] = None
    best_effort_value: Optional[Any] = None
    is_contradiction: bool = False
    contradiction_detail: Optional[str] = None
    is_advice_request: bool = False
    is_injection: bool = False


class EngineResponse(BaseModel):
    """What the ConversationEngine returns for each user turn."""

    response_type: Literal["advance", "clarify", "redirect", "injection", "complete"]
    assistant_message: str
    progress: int
    is_complete: bool
