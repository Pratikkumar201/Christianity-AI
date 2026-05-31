"""
FastAPI Routes — Full Multi-Agent Pipeline
POST /chat      → Main pipeline (Safety → Router → RAG → Agent → Validator → Response)
POST /image     → Image generation pipeline
POST /verify-verse → Standalone verse verification
GET  /evaluation/run → Run evaluation suite
GET  /evaluation/metrics → Get metrics
GET  /session/{id} → Session info
DELETE /session/{id} → Clear session
"""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("christianity_ai.routes")
router = APIRouter()


# ── Pydantic Models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    denomination: Optional[str] = "Non-denominational"

class ImageRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class VerifyVerseRequest(BaseModel):
    book: str
    chapter: int
    verse: int

class SetDenominationRequest(BaseModel):
    session_id: str
    denomination: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_llm(request: Request):
    """Get Groq client."""
    import os
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def _get_store(request: Request):
    return request.app.state.vector_store

def _get_bible_structure():
    from rag.vector_store import get_bible_structure
    return get_bible_structure()

def _build_pipeline_log(stage: str, data: Dict) -> Dict:
    return {"stage": stage, "timestamp": time.time(), **data}


# ── /chat ─────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    """
    Main multi-agent pipeline:
    Safety → Router → Memory → RAG → Agent → Validator → Format → Response
    """
    start_time = time.time()
    session_id = req.session_id or str(uuid.uuid4())
    pipeline_log = []

    llm = _get_llm(request)
    store = _get_store(request)

    # ── Stage 1: Safety Check ─────────────────────────────────────────────────
    from agents.safety_agent import run_safety_check
    safety_result = run_safety_check(req.message, llm)
    pipeline_log.append(_build_pipeline_log("SAFETY", safety_result))

    if not safety_result["allowed"]:
        logger.warning(f"[PIPELINE] BLOCKED: {safety_result['reason']}")
        return {
            "session_id": session_id,
            "route": "SAFETY_VIOLATION",
            "answer": f"⚠️ I cannot respond to that request. {safety_result['reason']}",
            "citations": [],
            "sources": [],
            "safety": safety_result,
            "pipeline_log": pipeline_log,
            "response_time_ms": int((time.time() - start_time) * 1000),
        }

    # ── Stage 2: Router ───────────────────────────────────────────────────────
    from agents.router_agent import route_request
    routing = route_request(req.message, llm)
    pipeline_log.append(_build_pipeline_log("ROUTER", routing))
    route = routing["route"]
    logger.info(f"[PIPELINE] Route: {route} | Confidence: {routing['confidence']:.2f}")

    # ── Stage 3: Memory Context ───────────────────────────────────────────────
    from memory.memory_manager import get_memory_context, get_denomination, update_memory, set_denomination
    if req.denomination and req.denomination != "Non-denominational":
        set_denomination(session_id, req.denomination)
    denomination = get_denomination(session_id)
    memory_context = get_memory_context(session_id)
    pipeline_log.append(_build_pipeline_log("MEMORY", {"denomination": denomination, "has_history": bool(memory_context)}))

    # ── Stage 4: RAG Retrieval ────────────────────────────────────────────────
    from rag.retriever import retrieve
    retrieved_verses = []
    if route not in ("IMAGE_GENERATION", "SAFETY_VIOLATION"):
        retrieved_verses = retrieve(req.message, store=store)
        pipeline_log.append(_build_pipeline_log("RAG", {
            "verses_retrieved": len(retrieved_verses),
            "top_score": retrieved_verses[0]["score"] if retrieved_verses else 0,
        }))

    # ── Stage 5: Specialized Agent ────────────────────────────────────────────
    agent_result = {}

    if route == "SCRIPTURE_QA":
        from agents.scripture_agent import run_scripture_qa
        agent_result = run_scripture_qa(req.message, retrieved_verses, memory_context, llm, denomination)

    elif route == "THEOLOGY_DISCUSSION":
        from agents.theology_agent import run_theology_discussion
        agent_result = run_theology_discussion(req.message, retrieved_verses, memory_context, llm, denomination)

    elif route == "CONTENT_GENERATION":
        from agents.content_agent import run_content_generation
        agent_result = run_content_generation(req.message, retrieved_verses, memory_context, llm, denomination)

    elif route == "IMAGE_GENERATION":
        from agents.image_agent import run_image_generation
        img_result = run_image_generation(req.message, llm)
        update_memory(session_id, req.message, img_result.get("answer", ""), denomination=denomination, route=route)
        return {
            "session_id": session_id,
            "route": route,
            "routing_confidence": routing["confidence"],
            "answer": img_result.get("answer", ""),
            "image_url": img_result.get("image_url"),
            "enhanced_prompt": img_result.get("enhanced_prompt"),
            "citations": [],
            "sources": [],
            "safety": safety_result,
            "pipeline_log": pipeline_log,
            "response_time_ms": int((time.time() - start_time) * 1000),
        }

    elif route == "VERSE_VERIFICATION":
        # Extract book/chapter/verse from user message
        import re
        match = re.search(r'([1-3]?\s*[A-Za-z]+)\s+(\d+):(\d+)', req.message)
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            from agents.validator_agent import verify_single_verse
            v_result = verify_single_verse(book, chapter, verse, _get_bible_structure())
            update_memory(session_id, req.message, v_result["message"], denomination=denomination, route=route)
            return {
                "session_id": session_id,
                "route": route,
                "routing_confidence": routing["confidence"],
                "answer": v_result["message"],
                "verse_verification": v_result,
                "citations": [],
                "sources": [],
                "safety": safety_result,
                "pipeline_log": pipeline_log,
                "response_time_ms": int((time.time() - start_time) * 1000),
            }
        else:
            agent_result = {
                "answer": "I could not identify a specific Bible reference to verify. Please use format: Book Chapter:Verse (e.g., John 3:16)",
                "citations": [],
                "sources": [],
                "confidence": 0.0,
            }

    else:  # GENERAL_CHAT
        # Light grounded general chat
        from agents.scripture_agent import run_scripture_qa
        agent_result = run_scripture_qa(req.message, retrieved_verses, memory_context, llm, denomination)

    pipeline_log.append(_build_pipeline_log("AGENT", {"route": route, "confidence": agent_result.get("confidence", 0)}))

    # ── Stage 6: Citation Validator ────────────────────────────────────────────
    from agents.validator_agent import validate_response
    validation = validate_response(
        agent_result.get("answer", ""),
        retrieved_verses,
        _get_bible_structure(),
    )
    pipeline_log.append(_build_pipeline_log("VALIDATOR", validation))

    if not validation["verified"] and validation.get("hallucinated"):
        logger.warning(f"[PIPELINE] Citation validation failed: {validation['hallucinated']}")
        final_answer = (
            "⚠️ I could not verify sufficient scriptural evidence for this response. "
            "Some citations could not be confirmed. Please rephrase your question."
        )
        citations = []
    else:
        final_answer = agent_result.get("answer", "")
        citations = validation.get("citations", agent_result.get("citations", []))

    # ── Stage 7: Update Memory ─────────────────────────────────────────────────
    update_memory(session_id, req.message, final_answer, denomination=denomination, route=route)

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(f"[PIPELINE] Complete in {elapsed_ms}ms | Route: {route} | Citations: {len(citations)}")

    return {
        "session_id": session_id,
        "route": route,
        "routing_confidence": routing["confidence"],
        "answer": final_answer,
        "citations": citations,
        "sources": agent_result.get("sources", []),
        "confidence": agent_result.get("confidence", 0),
        "validation": validation,
        "safety": safety_result,
        "denomination": denomination,
        "pipeline_log": pipeline_log,
        "response_time_ms": elapsed_ms,
    }


# ── /image ────────────────────────────────────────────────────────────────────

@router.post("/image")
async def generate_image(req: ImageRequest, request: Request):
    """Standalone image generation endpoint."""
    llm = _get_llm(request)
    from agents.image_agent import run_image_generation
    result = run_image_generation(req.prompt, llm)
    return result


# ── /verify-verse ─────────────────────────────────────────────────────────────

@router.post("/verify-verse")
async def verify_verse(req: VerifyVerseRequest):
    """Verify if a Bible verse reference exists."""
    from agents.validator_agent import verify_single_verse
    return verify_single_verse(req.book, req.chapter, req.verse, _get_bible_structure())


# ── /session ──────────────────────────────────────────────────────────────────

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    from memory.memory_manager import get_session_info
    return get_session_info(session_id)

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    from memory.memory_manager import clear_session
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared."}

@router.post("/session/denomination")
async def set_denomination_route(req: SetDenominationRequest):
    from memory.memory_manager import set_denomination
    set_denomination(req.session_id, req.denomination)
    return {"message": f"Denomination set to {req.denomination}"}


# ── /evaluation ────────────────────────────────────────────────────────────────

@router.get("/evaluation/run")
async def run_evaluation(request: Request):
    """Run the evaluation suite and return metrics."""
    from evaluation.evaluator import run_eval_suite
    store = _get_store(request)
    llm = _get_llm(request)
    results = run_eval_suite(store, llm)
    return results

@router.get("/evaluation/metrics")
async def get_metrics():
    """Return the latest cached evaluation metrics."""
    from evaluation.evaluator import get_latest_metrics
    return get_latest_metrics()
