from __future__ import annotations

from typing import Any, Optional

from app.models.document_config import DocumentConfig, FieldSpec
from app.models.session import StateMachineState


class FieldStateMachine:
    """
    Deterministic driver for the ordered field list defined in a DocumentConfig.

    Responsibilities:
    - Track which field is currently being collected
    - Advance to the next applicable field (respecting depends_on conditions)
    - Skip fields whose skip trigger was met
    - Record collected values
    - Report conversation progress as a percentage

    This class does NOT call any AI and has no side effects beyond mutating the
    injected StateMachineState object.
    """

    def __init__(self, config: DocumentConfig, state: StateMachineState) -> None:
        self.config = config
        self.state = state

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def current_field(self) -> Optional[FieldSpec]:
        """Return the FieldSpec we are currently collecting, or None if complete."""
        idx = self.state.current_field_index
        if idx >= len(self.config.fields):
            return None
        return self.config.fields[idx]

    def advance(self) -> Optional[FieldSpec]:
        """
        Move past the current field to the next applicable field.
        Resets the clarification counter.
        Returns the new current field, or None if the conversation is complete.
        """
        self.state.current_field_index += 1
        self.state.clarification_count = 0
        self._skip_inapplicable_fields()
        return self.current_field()

    def skip_current_field(self) -> Optional[FieldSpec]:
        """
        Mark the current field as skipped (e.g. user said 'no' to an optional field)
        and advance.
        """
        field = self.current_field()
        if field:
            if field.id not in self.state.skipped_fields:
                self.state.skipped_fields.append(field.id)
        return self.advance()

    def record_value(self, field_id: str, value: Any) -> None:
        self.state.collected_data[field_id] = value

    def increment_clarification(self) -> bool:
        """
        Increment the clarification attempt counter for the current field.
        Returns True if we have exhausted all allowed attempts and should give up.
        """
        self.state.clarification_count += 1
        return self.state.clarification_count >= self.state.max_clarifications

    def reset_clarification(self) -> None:
        self.state.clarification_count = 0

    def progress_percentage(self) -> int:
        total = len(self.config.fields)
        if total == 0:
            return 100
        return min(100, int((self.state.current_field_index / total) * 100))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _skip_inapplicable_fields(self) -> None:
        """Fast-forward past any fields whose depends_on condition is not met."""
        while True:
            field = self.current_field()
            if field is None:
                break
            if not self._field_is_applicable(field):
                if field.id not in self.state.skipped_fields:
                    self.state.skipped_fields.append(field.id)
                self.state.current_field_index += 1
            else:
                break

    def _field_is_applicable(self, field_spec: FieldSpec) -> bool:
        dep = field_spec.depends_on
        if dep is None:
            return True
        if dep.condition == "not_skipped":
            return (
                dep.field not in self.state.skipped_fields
                and dep.field in self.state.collected_data
            )
        if dep.condition == "equals":
            return str(self.state.collected_data.get(dep.field, "")) == dep.value
        if dep.condition == "not_equals":
            return str(self.state.collected_data.get(dep.field, "")) != dep.value
        return True
