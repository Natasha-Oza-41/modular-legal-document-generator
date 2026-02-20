from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from app.models.document_config import DocumentConfig


class DocumentRegistry:
    """
    Scans the document_types/ directory on startup and loads all YAML configs.
    New document types are discovered automatically — no code changes required.
    """

    def __init__(self, config_dir: str | Path | None = None) -> None:
        if config_dir is None:
            # Default: sibling 'document_types' directory relative to this file's package root
            config_dir = Path(__file__).parent.parent / "document_types"
        self._config_dir = Path(config_dir)
        self._configs: Dict[str, DocumentConfig] = {}
        self._load_all()

    def _load_all(self) -> None:
        for yaml_file in sorted(self._config_dir.glob("*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            config = DocumentConfig.model_validate(raw)
            self._configs[config.document_type_id] = config

    def get(self, document_type_id: str) -> DocumentConfig:
        if document_type_id not in self._configs:
            raise KeyError(f"Unknown document type: '{document_type_id}'")
        return self._configs[document_type_id]

    def list_all(self) -> List[DocumentConfig]:
        return list(self._configs.values())

    @property
    def loaded_ids(self) -> List[str]:
        return list(self._configs.keys())


# ---------------------------------------------------------------------------
# FastAPI dependency — single instance shared across requests
# ---------------------------------------------------------------------------

_registry: DocumentRegistry | None = None


def get_registry() -> DocumentRegistry:
    global _registry
    if _registry is None:
        _registry = DocumentRegistry()
    return _registry
