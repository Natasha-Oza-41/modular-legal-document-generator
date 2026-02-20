from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.ai.client import OpenAIClient, get_ai_client
from app.core.conversation_engine import ConversationEngine
from app.core.document_registry import DocumentRegistry, get_registry
from app.core.session_store import SessionStore, get_session_store

router = APIRouter()


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    session_id: str
    response: str
    response_type: str
    progress: int
    is_complete: bool


@router.post("/sessions/{session_id}/message", response_model=MessageResponse)
def send_message(
    session_id: str,
    body: MessageRequest,
    store: SessionStore = Depends(get_session_store),
    registry: DocumentRegistry = Depends(get_registry),
    ai_client: OpenAIClient = Depends(get_ai_client),
) -> MessageResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.status in ("generating", "ready"):
        raise HTTPException(
            status_code=409,
            detail="Conversation is complete. Document generation has been triggered.",
        )

    config = registry.get(session.document_type_id)

    engine = ConversationEngine(
        config=config,
        state=session.state_machine_state,
        ai_client=ai_client,
        history=session.history,
    )

    try:
        result = engine.process_message(body.message)
    except Exception as exc:
        logger.exception("Error processing message for session %s", session_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Persist turn to history
    session.history.append({"role": "user", "content": body.message})
    session.history.append({"role": "assistant", "content": result.assistant_message})

    # Update session status
    if result.is_complete:
        session.status = "complete"
    elif result.response_type in ("clarify", "redirect", "injection"):
        session.status = result.response_type
    else:
        session.status = "collecting"

    store.save(session)

    return MessageResponse(
        session_id=session_id,
        response=result.assistant_message,
        response_type=result.response_type,
        progress=result.progress,
        is_complete=result.is_complete,
    )
