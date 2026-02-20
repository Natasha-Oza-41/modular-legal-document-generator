from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class FieldValidation(BaseModel):
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    min_age: Optional[int] = None
    shares_must_total: Optional[int] = None
    must_equal: Optional[str] = None
    error_message: Optional[str] = None


class FieldDependency(BaseModel):
    field: str
    condition: Literal["not_skipped", "equals", "not_equals"]
    value: Optional[str] = None


class FieldSpec(BaseModel):
    id: str
    label: str
    type: Literal[
        "text",
        "date",
        "address",
        "beneficiary_list",
        "gift_list",
        "text_optional",
        "signature_block",
    ]
    required: bool
    section: str
    question: str
    clarification_prompt: str
    vagueness_triggers: List[str] = Field(default_factory=list)
    validation: Optional[FieldValidation] = None
    context_note: Optional[str] = None
    depends_on: Optional[FieldDependency] = None
    skip_if_answer_is: Optional[List[str]] = None


class SectionSpec(BaseModel):
    id: str
    title: str
    order: int


class ConversationConfig(BaseModel):
    greeting: str
    completion_message: str
    advice_redirect: str


class DocumentConfig(BaseModel):
    document_type_id: str
    display_name: str
    jurisdiction: str
    version: str
    template_file: str
    conversation_config: ConversationConfig
    fields: List[FieldSpec]
    sections: List[SectionSpec]
