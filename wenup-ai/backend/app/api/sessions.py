from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.conversation_engine import ConversationEngine
from app.core.document_registry import DocumentRegistry, get_registry
from app.core.session_store import SessionStore, get_session_store
from app.ai.client import OpenAIClient, get_ai_client
from app.models.session import Session

router = APIRouter()


class CreateSessionRequest(BaseModel):
    document_type_id: str


class CreateSessionResponse(BaseModel):
    session_id: str
    document_type_id: str
    status: str
    opening_message: str
    progress: int


class GetSessionResponse(BaseModel):
    session_id: str
    document_type_id: str
    status: str
    progress: int
    created_at: datetime
    last_activity_at: datetime


@router.post("/sessions", response_model=CreateSessionResponse, status_code=201)
def create_session(
    body: CreateSessionRequest,
    registry: DocumentRegistry = Depends(get_registry),
    store: SessionStore = Depends(get_session_store),
    ai_client: OpenAIClient = Depends(get_ai_client),
) -> CreateSessionResponse:
    # Validate the requested document type exists
    try:
        config = registry.get(body.document_type_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Document type '{body.document_type_id}' not found.",
        )

    session = Session(document_type_id=body.document_type_id)

    engine = ConversationEngine(
        config=config,
        state=session.state_machine_state,
        ai_client=ai_client,
        history=session.history,
    )
    opening = engine.get_opening_message()
    session.history.append({"role": "assistant", "content": opening})
    session.status = "collecting"
    store.save(session)

    return CreateSessionResponse(
        session_id=session.session_id,
        document_type_id=session.document_type_id,
        status=session.status,
        opening_message=opening,
        progress=0,
    )


@router.get("/sessions/{session_id}", response_model=GetSessionResponse)
def get_session(
    session_id: str,
    store: SessionStore = Depends(get_session_store),
) -> GetSessionResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    state = session.state_machine_state
    total = 0  # rough progress — engine not needed for a status check
    progress = 100 if session.status in ("complete", "generating", "ready") else (
        min(99, int((state.current_field_index / max(1, 1)) * 100))
    )

    return GetSessionResponse(
        session_id=session.session_id,
        document_type_id=session.document_type_id,
        status=session.status,
        progress=progress,
        created_at=session.created_at,
        last_activity_at=session.last_activity_at,
    )
