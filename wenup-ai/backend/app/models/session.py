from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class StateMachineState(BaseModel):
    """Serialisable snapshot of FieldStateMachine runtime state."""

    current_field_index: int = 0
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    skipped_fields: List[str] = Field(default_factory=list)
    clarification_count: int = 0
    max_clarifications: int = 3


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    document_type_id: str
    # greeting | collecting | clarifying | complete | generating | ready | error
    status: str = "greeting"
    state_machine_state: StateMachineState = Field(default_factory=StateMachineState)
    # [{role: "user"|"assistant", content: str}, ...]
    history: List[Dict[str, str]] = Field(default_factory=list)
    generated_document_text: Optional[str] = None
    pdf_bytes: Optional[bytes] = None
    docx_bytes: Optional[bytes] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int = 3600
