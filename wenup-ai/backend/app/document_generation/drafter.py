from __future__ import annotations

from typing import Any, Dict

from app.ai.client import OpenAIClient
from app.ai.drafting_prompts import build_drafting_prompt
from app.models.document_config import DocumentConfig


class DraftingAgent:
    """
    Calls Claude at temperature=0 to fill the document template with collected data.
    The AI system prompt prevents fact invention and prompt injection via collected data.
    """

    def __init__(self, ai_client: OpenAIClient, config: DocumentConfig) -> None:
        self._ai = ai_client
        self._config = config

    def draft(self, template_text: str, collected_data: Dict[str, Any]) -> str:
        prompt = build_drafting_prompt(
            template_text=template_text,
            collected_data=collected_data,
            document_config_summary={
                "display_name": self._config.display_name,
                "jurisdiction": self._config.jurisdiction,
            },
        )
        return self._ai.complete_draft(prompt)
