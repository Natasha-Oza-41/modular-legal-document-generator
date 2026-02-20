from __future__ import annotations

from fastapi import APIRouter

from app.api import conversation, document_types, documents, sessions

api_router = APIRouter()

api_router.include_router(document_types.router, tags=["document-types"])
api_router.include_router(sessions.router, tags=["sessions"])
api_router.include_router(conversation.router, tags=["conversation"])
api_router.include_router(documents.router, tags=["documents"])
