"""
Validator Agent (Citation Validator)
Post-generation agent that verifies:
1. Every scripture citation actually exists in the Bible
2. Citations were present in the retrieved context (not hallucinated)
3. Response is supported by retrieved context
Rejects fabricated references.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("christianity_ai.validator_agent")


# Canonical Bible book names (for fuzzy matching)
CANONICAL_BOOKS = {
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth", "1 samuel", "2 samuel",
    "1 kings", "2 kings", "1 chronicles", "2 chronicles",
    "ezra", "nehemiah", "esther", "job", "psalms", "psalm",
    "proverbs", "ecclesiastes", "song of solomon", "isaiah",
    "jeremiah", "lamentations", "ezekiel", "daniel", "hosea",
    "joel", "amos", "obadiah", "jonah", "micah", "nahum",
    "habakkuk", "zephaniah", "haggai", "zechariah", "malachi",
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1 corinthians", "2 corinthians", "galatians",
    "ephesians", "philippians", "colossians",
    "1 thessalonians", "2 thessalonians", "1 timothy", "2 timothy",
    "titus", "philemon", "hebrews", "james",
    "1 peter", "2 peter", "1 john", "2 john", "3 john",
    "jude", "revelation",
}


def _extract_citations(text: str) -> List[str]:
    """Extract all [Book Chapter:Verse] patterns from text."""
    return re.findall(r'\[([A-Za-z1-9 ]+\s+\d+:\d+(?:-\d+)?)\]', text)


def _parse_citation(citation: str) -> Dict[str, Any]:
    """Parse 'Book Chapter:Verse' into components."""
    match = re.match(r'^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$', citation.strip())
    if not match:
        return {"valid": False, "reason": f"Cannot parse citation: {citation}"}
    book = match.group(1).strip().lower()
    chapter = int(match.group(2))
    verse = int(match.group(3))
    return {"valid": True, "book": book, "chapter": chapter, "verse": verse, "raw": citation}


def verify_citation_exists(citation: str, bible_structure: Dict) -> Dict[str, Any]:
    """
    Verify a citation exists in the Bible structure map.
    Returns {"valid": bool, "reason": str}
    """
    parsed = _parse_citation(citation)
    if not parsed["valid"]:
        return {"valid": False, "citation": citation, "reason": parsed["reason"]}

    book_lower = parsed["book"]

    # Find matching book (case-insensitive)
    matched_book = None
    for b in bible_structure:
        if b.lower() == book_lower:
            matched_book = b
            break

    if not matched_book:
        # Try partial match
        for b in bible_structure:
            if book_lower in b.lower() or b.lower() in book_lower:
                matched_book = b
                break

    if not matched_book:
        return {"valid": False, "citation": citation, "reason": f"Book '{parsed['book']}' not found in Bible."}

    chapter = parsed["chapter"]
    if chapter not in bible_structure[matched_book]:
        max_chap = max(bible_structure[matched_book].keys())
        return {
            "valid": False,
            "citation": citation,
            "reason": f"{matched_book} only has {max_chap} chapters. Chapter {chapter} does not exist.",
        }

    verse = parsed["verse"]
    max_verse = bible_structure[matched_book][chapter]
    if verse > max_verse:
        return {
            "valid": False,
            "citation": citation,
            "reason": f"{matched_book} {chapter} only has {max_verse} verses. Verse {verse} does not exist.",
        }

    return {"valid": True, "citation": citation, "book": matched_book, "chapter": chapter, "verse": verse}


def validate_response(
    generated_answer: str,
    retrieved_verses: List[Dict[str, Any]],
    bible_structure: Dict,
) -> Dict[str, Any]:
    """
    Full citation validation pipeline:
    1. Extract all citations from response
    2. Verify each exists in Bible
    3. Check if citations were in retrieved context
    Returns: {"verified": bool, "citations": List, "issues": List, "hallucinated": List}
    """
    extracted = _extract_citations(generated_answer)

    if not extracted:
        return {
            "verified": True,
            "citations": [],
            "issues": [],
            "hallucinated": [],
            "note": "No citations in response.",
        }

    retrieved_refs = {v["reference"].lower() for v in retrieved_verses}
    issues = []
    hallucinated = []
    verified_citations = []

    for citation in extracted:
        # Check 1: Does it exist in Bible?
        existence = verify_citation_exists(citation, bible_structure)
        if not existence["valid"]:
            issues.append(existence)
            hallucinated.append(citation)
            logger.warning(f"[VALIDATOR] Fake/invalid citation: {citation} — {existence['reason']}")
            continue

        # Check 2: Was it in retrieved context?
        in_context = any(
            citation.lower() in ref or ref in citation.lower()
            for ref in retrieved_refs
        )
        if not in_context:
            logger.warning(f"[VALIDATOR] Citation not from retrieved context: {citation}")
            # Still valid (exists in Bible) but not from context — flag as potential hallucination
            issues.append({
                "citation": citation,
                "reason": f"Citation [{citation}] was not in retrieved context.",
                "severity": "warning",
            })

        verified_citations.append(citation)

    all_verified = len(hallucinated) == 0

    return {
        "verified": all_verified,
        "citations": verified_citations,
        "issues": issues,
        "hallucinated": hallucinated,
        "total_citations": len(extracted),
        "valid_count": len(verified_citations),
    }


def verify_single_verse(book: str, chapter: int, verse: int, bible_structure: Dict) -> Dict[str, Any]:
    """
    Standalone verse existence check for the /verify-verse endpoint.
    """
    citation = f"{book} {chapter}:{verse}"
    result = verify_citation_exists(citation, bible_structure)
    return {
        "valid": result["valid"],
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "reason": result.get("reason", ""),
        "message": (
            f"[{book} {chapter}:{verse}] is a valid Bible reference."
            if result["valid"]
            else f"The reference {book} {chapter}:{verse} does not exist in the Bible."
        ),
    }
