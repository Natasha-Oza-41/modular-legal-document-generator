from __future__ import annotations

from pathlib import Path


class TemplateLoader:
    """
    Loads document templates from the templates/ directory.
    Templates are plain-text files with [PLACEHOLDER] markers and
    [IF_X]...[/IF_X] conditional blocks that Claude resolves during drafting.
    """

    def __init__(self, templates_dir: str | Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self._templates_dir = Path(templates_dir)

    def load(self, filename: str) -> str:
        path = self._templates_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        return path.read_text(encoding="utf-8")
