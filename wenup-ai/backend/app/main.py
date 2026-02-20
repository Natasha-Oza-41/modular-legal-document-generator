from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.core.document_registry import DocumentRegistry, get_registry
from app.core.session_store import SessionStore, get_session_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # ---- Startup ----
    settings = get_settings()
    logger.info("Starting Wenup AI backend")

    # Eagerly initialise singletons so startup failures are visible immediately
    registry: DocumentRegistry = get_registry()
    logger.info("Loaded document types: %s", registry.loaded_ids)

    store: SessionStore = get_session_store()

    # Background task: purge expired sessions every 10 minutes
    async def _purge_loop() -> None:
        while True:
            await asyncio.sleep(600)
            n = store.purge_expired(ttl_seconds=3600)
            if n:
                logger.info("Purged %d expired session(s)", n)

    purge_task = asyncio.create_task(_purge_loop())

    yield

    # ---- Shutdown ----
    purge_task.cancel()
    logger.info("Wenup AI backend shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Wenup AI — Legal Document Platform",
        description="Generates personalised legal documents through a structured conversation.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
