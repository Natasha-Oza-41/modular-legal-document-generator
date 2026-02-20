from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.document_registry import DocumentRegistry, get_registry

router = APIRouter()


class DocumentTypeSummary(BaseModel):
    document_type_id: str
    display_name: str
    jurisdiction: str


class DocumentTypesResponse(BaseModel):
    document_types: List[DocumentTypeSummary]


@router.get("/document-types", response_model=DocumentTypesResponse)
def list_document_types(
    registry: DocumentRegistry = Depends(get_registry),
) -> DocumentTypesResponse:
    return DocumentTypesResponse(
        document_types=[
            DocumentTypeSummary(
                document_type_id=c.document_type_id,
                display_name=c.display_name,
                jurisdiction=c.jurisdiction,
            )
            for c in registry.list_all()
        ]
    )
