from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.ai.client import OpenAIClient, get_ai_client
from app.core.document_registry import DocumentRegistry, get_registry
from app.core.session_store import SessionStore, get_session_store
from app.document_generation.pipeline import DocumentPipeline

router = APIRouter()

# Thread pool for blocking document generation (WeasyPrint is not async-native)
_executor = ThreadPoolExecutor(max_workers=4)


class GenerateResponse(BaseModel):
    session_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    session_id: str
    status: str
    error: str | None = None


def _run_pipeline(
    session_id: str,
    store: SessionStore,
    registry: DocumentRegistry,
    ai_client: OpenAIClient,
) -> None:
    """Blocking pipeline run — executed in thread pool."""
    session = store.get(session_id)
    if session is None:
        return

    try:
        config = registry.get(session.document_type_id)
        pipeline = DocumentPipeline(config=config, ai_client=ai_client)
        result = pipeline.run(session.state_machine_state.collected_data)

        session.generated_document_text = result.text
        session.pdf_bytes = result.pdf_bytes
        session.docx_bytes = result.docx_bytes
        session.status = "ready"
    except Exception as exc:  # noqa: BLE001
        session.status = "error"
        session.error_message = str(exc)
    finally:
        store.save(session)


@router.post("/sessions/{session_id}/generate", response_model=GenerateResponse, status_code=202)
def trigger_generation(
    session_id: str,
    background_tasks: BackgroundTasks,
    store: SessionStore = Depends(get_session_store),
    registry: DocumentRegistry = Depends(get_registry),
    ai_client: OpenAIClient = Depends(get_ai_client),
) -> GenerateResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.status not in ("complete",):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot generate document: session status is '{session.status}'. "
                   "Conversation must be complete first.",
        )

    session.status = "generating"
    store.save(session)

    background_tasks.add_task(
        _run_pipeline,
        session_id=session_id,
        store=store,
        registry=registry,
        ai_client=ai_client,
    )

    return GenerateResponse(
        session_id=session_id,
        status="generating",
        message="Your document is being prepared. Poll /status to check progress.",
    )


@router.get("/sessions/{session_id}/status", response_model=StatusResponse)
def get_generation_status(
    session_id: str,
    store: SessionStore = Depends(get_session_store),
) -> StatusResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    return StatusResponse(
        session_id=session_id,
        status=session.status,
        error=session.error_message,
    )


@router.get("/sessions/{session_id}/download/pdf")
def download_pdf(
    session_id: str,
    store: SessionStore = Depends(get_session_store),
) -> Response:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.status != "ready" or session.pdf_bytes is None:
        raise HTTPException(status_code=409, detail="Document is not ready yet.")

    return Response(
        content=session.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="will_{session_id[:8]}.pdf"'
            )
        },
    )


@router.get("/sessions/{session_id}/download/docx")
def download_docx(
    session_id: str,
    store: SessionStore = Depends(get_session_store),
) -> Response:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.status != "ready" or session.docx_bytes is None:
        raise HTTPException(status_code=409, detail="Document is not ready yet.")

    return Response(
        content=session.docx_bytes,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="will_{session_id[:8]}.docx"'
            )
        },
    )
