from __future__ import annotations

from typing import Any, Dict

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings


class OpenAIClient:
    """
    Thin wrapper around the OpenAI Chat Completions API.

    The prompt payload format is {"system": str, "messages": list}, matching
    what the prompt builders produce. The system prompt is prepended to the
    messages list as a "system" role message before each API call.

    Two public methods intentionally separate the two AI roles:
    - complete()       for conversation/extraction (caller controls temperature)
    - complete_draft() for document drafting (always temperature=0)
    """

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str | None = None) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def complete(self, prompt_payload: Dict[str, Any], temperature: float = 1.0) -> str:
        """
        General-purpose completion.
        prompt_payload must contain 'system' (str) and 'messages' (list).
        """
        messages = [{"role": "system", "content": prompt_payload["system"]}]
        messages.extend(prompt_payload["messages"])

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""

    def complete_draft(self, prompt_payload: Dict[str, Any]) -> str:
        """
        Document drafting — always uses temperature=0 for reproducibility.
        max_tokens is higher to accommodate full document text.
        """
        messages = [{"role": "system", "content": prompt_payload["system"]}]
        messages.extend(prompt_payload["messages"])

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# FastAPI dependency — single instance shared across requests
# ---------------------------------------------------------------------------

_client: OpenAIClient | None = None


def get_ai_client() -> OpenAIClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.model_id,
            base_url=settings.openai_base_url or None,
        )
    return _client
