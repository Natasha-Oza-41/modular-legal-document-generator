from __future__ import annotations

from typing import Any, Dict, List

from app.ai.client import OpenAIClient
from app.ai.conversation_prompts import (
    build_clarification_message,
    build_extraction_prompt,
)
from app.ai.response_parser import parse_extraction_response
from app.core.injection_guard import InjectionGuard
from app.core.input_validator import InputValidator
from app.core.state_machine import FieldStateMachine
from app.models.conversation import EngineResponse
from app.models.document_config import DocumentConfig
from app.models.session import StateMachineState

_ADVICE_KEYWORDS = [
    "should i",
    "what should",
    "advise me",
    "legal advice",
    "is it legal",
    "am i allowed",
    "do i have to",
    "can i legally",
    "is that valid",
    "will this hold up",
    "what happens if i",
    "is this enforceable",
]


class ConversationEngine:
    """
    Central orchestrator for a single conversation session.

    Receives one user message at a time, updates the state machine, and returns
    the next assistant message.

    Responsibilities (in order):
    1. Injection guard (regex pre-filter)
    2. Legal advice redirect
    3. Skip trigger check (for optional fields)
    4. AI extraction (Claude)
    5. Vagueness / contradiction handling
    6. Advance state machine and return next question
    """

    def __init__(
        self,
        config: DocumentConfig,
        state: StateMachineState,
        ai_client: OpenAIClient,
        history: List[Dict[str, str]],
    ) -> None:
        self.config = config
        self.machine = FieldStateMachine(config, state)
        self.ai_client = ai_client
        self.history = history
        self._guard = InjectionGuard()

    # ------------------------------------------------------------------
    # Opening message (called once per session, before any user turn)
    # ------------------------------------------------------------------

    def get_opening_message(self) -> str:
        opening = self.config.conversation_config.greeting
        first_field = self.machine.current_field()
        if first_field:
            opening = opening.strip() + "\n\n" + self._interpolate(first_field.question)
        return opening

    # ------------------------------------------------------------------
    # Main turn handler
    # ------------------------------------------------------------------

    def process_message(self, user_message: str) -> EngineResponse:
        # 1. Injection guard
        if self._guard.is_injection(user_message):
            return EngineResponse(
                response_type="injection",
                assistant_message=(
                    "I can only help with collecting information for your legal document. "
                    "Please answer the question I asked."
                ),
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        # 2. Legal advice redirect
        if self._is_advice_request(user_message):
            return EngineResponse(
                response_type="redirect",
                assistant_message=self.config.conversation_config.advice_redirect,
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        current_field = self.machine.current_field()

        # Guard: if there is no current field, conversation is already complete
        if current_field is None:
            return EngineResponse(
                response_type="complete",
                assistant_message=self.config.conversation_config.completion_message,
                progress=100,
                is_complete=True,
            )

        # 3. Skip trigger check (for optional fields)
        if InputValidator.is_skip_response(current_field, user_message):
            next_field = self.machine.skip_current_field()
            if next_field is None:
                return EngineResponse(
                    response_type="complete",
                    assistant_message=self.config.conversation_config.completion_message,
                    progress=100,
                    is_complete=True,
                )
            return EngineResponse(
                response_type="advance",
                assistant_message=self._interpolate(next_field.question),
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        # 4. AI extraction
        prompt = build_extraction_prompt(
            field_spec=current_field,
            user_message=user_message,
            conversation_history=self.history,
            collected_data=self.machine.state.collected_data,
        )
        raw = self.ai_client.complete(prompt)
        extraction = parse_extraction_response(raw)

        # Re-check injection / advice flags that Claude detected
        if extraction.is_injection:
            return EngineResponse(
                response_type="injection",
                assistant_message=(
                    "I can only help with collecting information for your legal document. "
                    "Please answer the question I asked."
                ),
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        if extraction.is_advice_request:
            return EngineResponse(
                response_type="redirect",
                assistant_message=self.config.conversation_config.advice_redirect,
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        # 5a. Vague answer handling
        if extraction.is_vague:
            give_up = self.machine.increment_clarification()
            if give_up:
                # Accept best-effort value and move on; flag for review
                value = extraction.best_effort_value or user_message
                self.machine.record_value(current_field.id, value)
                next_field = self.machine.advance()
                note = (
                    " Note: your previous answer was recorded as best we could interpret "
                    "it, but you may wish to review that section before signing."
                )
                if next_field is None:
                    return EngineResponse(
                        response_type="complete",
                        assistant_message=self.config.conversation_config.completion_message + note,
                        progress=100,
                        is_complete=True,
                    )
                return EngineResponse(
                    response_type="advance",
                    assistant_message=self._interpolate(next_field.question) + note,
                    progress=self.machine.progress_percentage(),
                    is_complete=False,
                )

            clarification = build_clarification_message(current_field, extraction.vagueness_reason)
            return EngineResponse(
                response_type="clarify",
                assistant_message=clarification,
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        # 5b. Contradiction handling
        if extraction.is_contradiction:
            give_up = self.machine.increment_clarification()
            if give_up:
                # Accept contradictory answer after repeated attempts; flag it
                value = extraction.extracted_value or extraction.best_effort_value or user_message
                self.machine.record_value(current_field.id, value)
                next_field = self.machine.advance()
                note = (
                    " Note: there was an apparent contradiction in your answers for that "
                    "section. Please review it carefully before signing."
                )
                if next_field is None:
                    return EngineResponse(
                        response_type="complete",
                        assistant_message=self.config.conversation_config.completion_message + note,
                        progress=100,
                        is_complete=True,
                    )
                return EngineResponse(
                    response_type="advance",
                    assistant_message=self._interpolate(next_field.question) + note,
                    progress=self.machine.progress_percentage(),
                    is_complete=False,
                )

            return EngineResponse(
                response_type="clarify",
                assistant_message=(
                    f"I notice there may be a contradiction with something you told me "
                    f"earlier ({extraction.contradiction_detail}). Could you clarify?"
                ),
                progress=self.machine.progress_percentage(),
                is_complete=False,
            )

        # 6. Value is clean — record and advance
        self.machine.record_value(current_field.id, extraction.extracted_value)
        next_field = self.machine.advance()

        if next_field is None:
            return EngineResponse(
                response_type="complete",
                assistant_message=self.config.conversation_config.completion_message,
                progress=100,
                is_complete=True,
            )

        return EngineResponse(
            response_type="advance",
            assistant_message=self._interpolate(next_field.question),
            progress=self.machine.progress_percentage(),
            is_complete=False,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_advice_request(self, message: str) -> bool:
        lower = message.lower()
        return any(kw in lower for kw in _ADVICE_KEYWORDS)

    def _interpolate(self, template: str) -> str:
        """Replace {field_id} placeholders with already-collected values."""
        result = template
        for key, value in self.machine.state.collected_data.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
