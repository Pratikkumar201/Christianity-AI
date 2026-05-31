"""
Embeddings Module
Loads BAAI/bge-small-en-v1.5 as a singleton sentence-transformer encoder.
"""

import logging
import os
from typing import List

import numpy as np

logger = logging.getLogger("christianity_ai.embeddings")

_encoder = None


def get_encoder():
    """Singleton encoder loader."""
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        logger.info(f"Loading embedding model: {model_name} ...")
        _encoder = SentenceTransformer(model_name)
        logger.info("Embedding model loaded.")
    return _encoder


def encode(texts: List[str]) -> np.ndarray:
    """
    Encode a list of strings to L2-normalized float32 vectors.
    BGE models work best with a query instruction prefix for retrieval.
    """
    encoder = get_encoder()
    embeddings = encoder.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=64,
    )
    return embeddings.astype(np.float32)


def encode_query(query: str) -> np.ndarray:
    """Encode a single query string (with BGE instruction prefix)."""
    instruction = (
    "Represent this biblical question for retrieving relevant Bible verses: "
)
    return encode([instruction + query])
