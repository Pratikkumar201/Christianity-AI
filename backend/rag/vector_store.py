"""
Vector Store Module
Builds and persists FAISS index from KJV Bible JSON.
Supports similarity search with metadata retrieval.
"""

import json
import logging
import os
from typing import Any, Dict, List

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

logger = logging.getLogger("christianity_ai.vector_store")

# Bible structure limits for verse validation
BIBLE_STRUCTURE: Dict[str, Dict[int, int]] = {}


class VectorStore:
    def __init__(self):
        self.index_path = os.getenv("FAISS_INDEX_PATH", "./data/bible.index")
        self.metadata_path = os.getenv("BIBLE_METADATA_PATH", "./data/bible_metadata.json")
        self.bible_path = os.getenv("BIBLE_JSON_PATH", "./data/bible_kjv.json")
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.bm25 = None

    def initialize(self):
        """Load or build the FAISS index."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            logger.info("Loading cached FAISS index...")
            self._load()
        else:
            logger.info("Building FAISS index from Bible JSON (this may take a few minutes)...")
            self._build()
        self._build_structure_map()
        logger.info(f"Vector store ready: {len(self.metadata)} verses indexed.")

    # def _load(self):
    #     self.index = faiss.read_index(self.index_path)
    #     with open(self.metadata_path, "r", encoding="utf-8") as f:
    #         self.metadata = json.load(f)

    def _load(self):
        self.index = faiss.read_index(self.index_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        # Build BM25 index
        corpus = [m["chunk"].lower().split() for m in self.metadata]
        self.bm25 = BM25Okapi(corpus)

    # def _build(self):
    #     from rag.embeddings import encode
    #     with open(self.bible_path, "r", encoding="utf-8") as f:
    #         bible_data = json.load(f)

    #     texts = []
    #     self.metadata = []

    #     for book_name, chapters in bible_data.items():
    #         for chapter_num, verses in chapters.items():
    #             for verse_num, verse_text in verses.items():
    #                 ref = f"{book_name} {chapter_num}:{verse_num}"
    #                 chunk = f"{ref} — {verse_text}"
    #                 texts.append(chunk)
    #                 self.metadata.append({
    #                     "book": book_name,
    #                     "chapter": int(chapter_num),
    #                     "verse": int(verse_num),
    #                     "text": verse_text,
    #                     "reference": ref,
    #                     "chunk": chunk,
    #                 })

    #     logger.info(f"Encoding {len(texts)} verses...")
    #     embeddings = encode(texts)

    #     dim = embeddings.shape[1]
    #     self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine after L2 norm)
    #     self.index.add(embeddings)

    #     os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
    #     faiss.write_index(self.index, self.index_path)
    #     with open(self.metadata_path, "w", encoding="utf-8") as f:
    #         json.dump(self.metadata, f, ensure_ascii=False)
    #     logger.info("FAISS index saved.")


    def _build(self):
        from rag.embeddings import encode

        bible_folder = "./data"

        texts = []
        self.metadata = []

        for filename in os.listdir(bible_folder):

            if not filename.endswith(".json"):
                continue

            # Skip non-book files
            if filename in [
                "Books.json",
                "bible_kjv.json",
                "bible_metadata.json",
            ]:
                continue

            filepath = os.path.join(bible_folder, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    book_data = json.load(f)

                book_name = book_data["book"]

                for chapter in book_data["chapters"]:

                    chapter_num = int(chapter["chapter"])

                    for verse in chapter["verses"]:

                        verse_num = int(verse["verse"])
                        verse_text = verse["text"]

                        ref = f"{book_name} {chapter_num}:{verse_num}"
                        chunk = f"{ref} — {verse_text}"

                        texts.append(chunk)

                        self.metadata.append(
                            {
                                "book": book_name,
                                "chapter": chapter_num,
                                "verse": verse_num,
                                "text": verse_text,
                                "reference": ref,
                                "chunk": chunk,
                            }
                        )

            except Exception as e:
                logger.warning(f"Skipping {filename}: {e}")

        logger.info(f"Encoding {len(texts)} verses...")

        embeddings = encode(texts)

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False)

        # Build BM25 corpus
        corpus = [m["chunk"].lower().split() for m in self.metadata]
        self.bm25 = BM25Okapi(corpus)

        logger.info("FAISS index saved.")
        

    def _build_structure_map(self):
        """Build book→chapter→max_verse map for verse validation."""
        global BIBLE_STRUCTURE
        for entry in self.metadata:
            book = entry["book"]
            chap = entry["chapter"]
            verse = entry["verse"]
            if book not in BIBLE_STRUCTURE:
                BIBLE_STRUCTURE[book] = {}
            if chap not in BIBLE_STRUCTURE[book]:
                BIBLE_STRUCTURE[book][chap] = 0
            if verse > BIBLE_STRUCTURE[book][chap]:
                BIBLE_STRUCTURE[book][chap] = verse


    def search(
        self,
        query_vector: np.ndarray,
        query_text: str = "",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if self.index is None:
            return []

        # Semantic Search (FAISS)
        semantic_scores, semantic_indices = self.index.search(
            query_vector,
            min(top_k * 10, len(self.metadata))
        )

        candidate_scores = {}

        for score, idx in zip(
            semantic_scores[0],
            semantic_indices[0]
        ):
            if idx >= 0:
                candidate_scores[idx] = {
                    "semantic": float(score),
                    "bm25": 0.0,
                }

        # BM25 Search
        if self.bm25 and query_text:

            # tokens = query_text.lower().split()
            query_lower = query_text.lower()

            # Query expansion for KJV language
            if "anxiety" in query_lower:
                query_lower += " careful troubled care peace fear not be careful for nothing cast all your care take no thought"

            if "depression" in query_lower:
                query_lower += " sorrow grief comfort hope"

            if "healing" in query_lower:
                query_lower += " heal healed restoration restore"

            if "forgiveness" in query_lower:
                query_lower += " forgive mercy grace"

            if "love" in query_lower:
                query_lower += " charity beloved"

            tokens = query_lower.split()

            bm25_scores = self.bm25.get_scores(tokens)

            top_debug = np.argsort(bm25_scores)[::-1][:10]

            logger.info("===== BM25 TOP RESULTS =====")

            for idx in top_debug:
                logger.info(
                    f"{self.metadata[idx]['reference']} "
                    f"| {bm25_scores[idx]:.4f}"
                )

            top_bm25_idx = np.argsort(bm25_scores)[::-1][: top_k * 10]

            max_bm25 = max(bm25_scores) if len(bm25_scores) else 1.0

            for idx in top_bm25_idx:

                normalized_bm25 = (
                    bm25_scores[idx] / max_bm25
                    if max_bm25 > 0
                    else 0
                )

                if idx not in candidate_scores:
                    candidate_scores[idx] = {
                        "semantic": 0.0,
                        "bm25": normalized_bm25,
                    }
                else:
                    candidate_scores[idx]["bm25"] = normalized_bm25

        # Hybrid Score
        ranked = []

        for idx, scores in candidate_scores.items():

            final_score = (
                0.5 * scores["semantic"]
                + 0.5 * scores["bm25"]
            )

            ranked.append((idx, final_score))


        for idx, scores in list(candidate_scores.items())[:10]:
            logger.info(
                f"{self.metadata[idx]['reference']} "
                f"SEM={scores['semantic']:.3f} "
                f"BM25={scores['bm25']:.3f}"
            )

        ranked.sort(key=lambda x: x[1], reverse=True)

        results = []

        for idx, score in ranked[:top_k]:

            entry = dict(self.metadata[idx])

            entry["score"] = float(score)

            results.append(entry)

        return results


    def get_metadata(self) -> List[Dict[str, Any]]:
        return self.metadata


def get_bible_structure() -> Dict[str, Dict[int, int]]:
    return BIBLE_STRUCTURE
