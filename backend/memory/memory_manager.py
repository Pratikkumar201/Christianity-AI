"""
Memory Manager
Session-based conversation memory.
Stores denomination, Q&A history, and user preferences.
Influences future responses through memory context injection.
"""

import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("christianity_ai.memory")

# In-memory session store (keyed by session_id)
_sessions: Dict[str, Dict[str, Any]] = {}

MAX_HISTORY = 10  # Maximum Q&A pairs to retain per session


def _get_session(session_id: str) -> Dict[str, Any]:
    """Get or create a session."""
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id": session_id,
            "denomination": "Non-denominational",
            "history": deque(maxlen=MAX_HISTORY),
            "preferences": {},
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "message_count": 0,
        }
    return _sessions[session_id]


def get_memory_context(session_id: str) -> str:
    """
    Build a memory context string to inject into agent prompts.
    Includes denomination and recent conversation history.
    """
    session = _get_session(session_id)
    parts = []

    if session["denomination"] != "Non-denominational":
        parts.append(f"User's denomination: {session['denomination']}")

    history = list(session["history"])
    if history:
        parts.append("Recent conversation history:")
        for i, turn in enumerate(history[-3:], 1):  # Last 3 turns
            parts.append(f"  Q{i}: {turn['question'][:100]}")
            parts.append(f"  A{i}: {turn['answer'][:150]}...")

    return "\n".join(parts) if parts else ""


def update_memory(
    session_id: str,
    question: str,
    answer: str,
    denomination: Optional[str] = None,
    route: Optional[str] = None,
) -> None:
    """Update session memory after a conversation turn."""
    session = _get_session(session_id)

    if denomination and denomination != session["denomination"]:
        logger.info(f"[MEMORY] Session {session_id}: denomination updated to {denomination}")
        session["denomination"] = denomination

    session["history"].append({
        "question": question,
        "answer": answer[:500],
        "route": route,
        "timestamp": datetime.utcnow().isoformat(),
    })
    session["message_count"] += 1
    session["last_active"] = datetime.utcnow().isoformat()


def get_denomination(session_id: str) -> str:
    """Get the stored denomination for a session."""
    return _get_session(session_id)["denomination"]


def set_denomination(session_id: str, denomination: str) -> None:
    """Explicitly set denomination for a session."""
    session = _get_session(session_id)
    session["denomination"] = denomination
    logger.info(f"[MEMORY] Session {session_id}: denomination set to {denomination}")


def get_session_info(session_id: str) -> Dict[str, Any]:
    """Return session metadata (for frontend memory indicator)."""
    session = _get_session(session_id)
    return {
        "session_id": session_id,
        "denomination": session["denomination"],
        "message_count": session["message_count"],
        "history_length": len(session["history"]),
        "created_at": session["created_at"],
        "last_active": session["last_active"],
    }


def clear_session(session_id: str) -> None:
    """Clear session memory."""
    if session_id in _sessions:
        del _sessions[session_id]
        logger.info(f"[MEMORY] Session {session_id} cleared.")
