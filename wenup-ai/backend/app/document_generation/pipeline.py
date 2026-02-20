from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.ai.client import OpenAIClient
from app.document_generation.docx_renderer import DOCXRenderer
from app.document_generation.drafter import DraftingAgent
from app.document_generation.pdf_renderer import PDFRenderer
from app.document_generation.template_loader import TemplateLoader
from app.models.document_config import DocumentConfig


@dataclass
class GeneratedDocument:
    text: str
    pdf_bytes: bytes
    docx_bytes: bytes


class DocumentPipeline:
    """
    Orchestrates the full document generation flow:
      1. Load Jinja2 structural template
      2. AI drafting — Claude fills placeholders (temperature=0)
      3. [Validation gate — assumed to exist per requirements]
      4. Render to PDF (WeasyPrint)
      5. Render to DOCX (python-docx)

    Each stage is a separate injected dependency so they can be unit-tested
    and swapped independently.
    """

    def __init__(
        self,
        config: DocumentConfig,
        ai_client: OpenAIClient,
        template_loader: TemplateLoader | None = None,
        pdf_renderer: PDFRenderer | None = None,
        docx_renderer: DOCXRenderer | None = None,
    ) -> None:
        self._config = config
        self._drafter = DraftingAgent(ai_client, config)
        self._template_loader = template_loader or TemplateLoader()
        self._pdf_renderer = pdf_renderer or PDFRenderer()
        self._docx_renderer = docx_renderer or DOCXRenderer()

    def run(self, collected_data: Dict[str, Any]) -> GeneratedDocument:
        # Stage 1 — load template
        template_text = self._template_loader.load(self._config.template_file)

        # Stage 2 — AI drafting
        document_text = self._drafter.draft(template_text, collected_data)

        # Stage 3 — Validation gate (assumed to exist; wire in here when available)
        # document_text = validation_service.validate(document_text, collected_data)

        # Stage 4 — Render PDF
        pdf_bytes = self._pdf_renderer.render(document_text)

        # Stage 5 — Render DOCX
        docx_bytes = self._docx_renderer.render(document_text, collected_data)

        return GeneratedDocument(
            text=document_text,
            pdf_bytes=pdf_bytes,
            docx_bytes=docx_bytes,
        )
