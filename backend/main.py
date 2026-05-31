"""
Christianity AI Assistant — FastAPI Backend
Main application entrypoint with lifespan management.
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("christianity_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build FAISS index on startup if not cached."""
    logger.info("🚀 Starting Christianity AI Assistant...")
    from rag.vector_store import VectorStore
    store = VectorStore()
    store.initialize()
    app.state.vector_store = store
    logger.info("✅ FAISS index ready.")
    yield
    logger.info("🛑 Shutting down...")


app = FastAPI(
    title="Christianity AI Assistant",
    description="Production-grade RAG-powered Christianity AI with multi-agent routing, hallucination prevention, and safety layers.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from api.routes import router
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Christianity AI Assistant", "version": "1.0.0"}
