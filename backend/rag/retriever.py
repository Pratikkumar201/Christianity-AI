"""
Retriever Module
High-level retrieval interface over VectorStore.
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("christianity_ai.retriever")

_store = None


def get_store():
    """Get the shared VectorStore instance."""
    global _store
    if _store is None:
        from rag.vector_store import VectorStore
        _store = VectorStore()
        _store.initialize()
    return _store


def retrieve(
    query: str,
    top_k: Optional[int] = None,
    store=None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k Bible verses relevant to query.
    Returns list of {book, chapter, verse, text, reference, score}.
    """
    from rag.embeddings import encode_query

    if top_k is None:
        top_k = int(os.getenv("TOP_K_RETRIEVAL", "5"))

    if store is None:
        store = get_store()

    query_vec = encode_query(query)
    results = store.search(query_vec, query_text=query, top_k=top_k)

    logger.info(
        f"Retrieved {len(results)} verses for query: '{query[:60]}...' "
        f"| Top score: {results[0]['score']:.4f}" if results else "No results."
    )
    return results


def build_context_string(results: List[Dict[str, Any]]) -> str:
    """Format retrieved verses as a readable context block for the LLM."""
    if not results:
        return "No relevant Bible verses found."
    lines = ["RETRIEVED BIBLE CONTEXT:"]
    for r in results:
        lines.append(f"[{r['reference']}] {r['text']}")
    return "\n".join(lines)
