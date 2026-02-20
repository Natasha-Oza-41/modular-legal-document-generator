from __future__ import annotations

from app.models.document_config import FieldSpec


class InputValidator:
    """
    Pre-AI check for obvious vagueness using the trigger words defined in each
    field's YAML config.

    This is a lightweight hint passed to the extraction prompt so that Claude
    knows what to flag. Claude makes the final determination on whether to accept
    or reject a value; this class only provides a fast pre-signal.
    """

    @staticmethod
    def has_vagueness_triggers(field_spec: FieldSpec, user_input: str) -> bool:
        """
        Return True if the user's input contains any vagueness trigger word
        defined for this field in the YAML config.
        """
        lower = user_input.lower()
        return any(trigger.lower() in lower for trigger in field_spec.vagueness_triggers)

    @staticmethod
    def is_skip_response(field_spec: FieldSpec, user_input: str) -> bool:
        """
        Return True if the user's input matches one of the skip triggers
        defined for this optional field.
        """
        if not field_spec.skip_if_answer_is:
            return False
        normalised = user_input.strip().lower()
        return normalised in [s.lower() for s in field_spec.skip_if_answer_is]
