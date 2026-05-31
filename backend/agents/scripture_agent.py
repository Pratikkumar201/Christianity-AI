"""
Scripture QA Agent
Answers Bible questions using ONLY retrieved context from FAISS.
Strictly grounded — refuses if evidence is insufficient.
"""

import logging
import os
import re
from typing import Any, Dict, List

logger = logging.getLogger("christianity_ai.scripture_agent")

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))

# SYSTEM_PROMPT = """You are a scripture-grounded Bible Q&A assistant.

# CRITICAL RULES:
# 1. You may ONLY answer using the RETRIEVED BIBLE CONTEXT provided below.
# 2. NEVER quote Bible verses from your own memory.
# 3. NEVER invent or fabricate scripture references.
# 4. Every claim MUST be supported by the retrieved context.
# 5. Include citations in format [Book Chapter:Verse] for every scripture you reference.
# 6. If the retrieved context does not contain enough information, respond with: "I could not find sufficient Biblical support for that claim."
# 7. Maintain a reverent, accurate, and humble tone.

# Your response must include:
# - A clear, grounded answer
# - Scripture citations in [Book Chapter:Verse] format
# - A "Sources Used" section at the end listing all citations

# FORMAT:
# [Answer with inline citations like [John 3:16]]

# **Sources Used:**
# - [John 3:16]
# - [Romans 5:8]"""

SYSTEM_PROMPT = """You are a scripture-grounded Bible Q&A assistant.

CRITICAL RULES:
1. You may ONLY answer using the RETRIEVED BIBLE CONTEXT provided below.
2. NEVER quote Bible verses from your own memory.
3. NEVER invent or fabricate scripture references.
4. Every claim MUST be supported by the retrieved context.
5. Include citations in format [Book Chapter:Verse] for every scripture you reference.
6. If the retrieved context does not contain enough information, respond with: "I could not find sufficient Biblical support for that claim."
7. Maintain a reverent, accurate, and humble tone.

RELEVANCE RULES:
1. First identify which retrieved verses DIRECTLY answer the user's question.
2. Prioritize direct verses over general or indirect verses.
3. Do NOT treat all retrieved verses equally.
4. If direct verses exist, build the main answer around them.
5. Use indirect verses only as supporting context.
6. Do not over-focus on “fear of the Lord” verses when the question is about anxiety, worry, care, trouble, peace, comfort, or burdens.
7. If a verse mentions the exact topic or close KJV wording, such as “careful,” “care,” “troubled,” “peace,” “take no thought,” or “fear not,” prefer it over broad thematic matches.

TOPIC PRIORITY GUIDANCE:
For anxiety, worry, fear, stress, or burden:
Prioritize verses about:
- being careful for nothing
- casting care upon God
- taking no thought
- peace of God
- fear not
- being troubled

For forgiveness:
Prioritize verses about:
- forgive
- forgiven
- mercy
- grace
- reconciliation

For healing and strength:
Prioritize verses about:
- heal
- healed
- restore
- strength
- comfort
- help

For Trinity:
Prioritize verses about:
- Father, Son, and Holy Ghost / Holy Spirit
- the Word being God
- Christ and the Father
- Godhead

ANSWER STYLE:
Use this structure:

1. Direct Biblical Teaching
Explain the verses that most directly answer the question.

2. Supporting Scripture
Briefly mention secondary verses, only if useful.

3. Practical Meaning
Explain what this means for a believer today.

4. Sources Used
List only the citations actually used in the answer.

IMPORTANT:
- Do not cite every retrieved verse.
- Cite only verses that are actually used.
- If a verse is weakly related, omit it.
- Prefer quality of citations over quantity.
"""


def run_scripture_qa(
    user_message: str,
    retrieved_verses: List[Dict[str, Any]],
    memory_context: str,
    llm_client,
    denomination: str = "Non-denominational",
) -> Dict[str, Any]:
    """
    Generate a grounded scripture answer from retrieved context.
    Returns: {"answer": str, "citations": List[str], "confidence": float, "sources": List[dict]}
    """
    if not retrieved_verses:
        return {
            "answer": "I could not find sufficient Biblical support for that claim.",
            "citations": [],
            "confidence": 0.0,
            "sources": [],
        }

    top_score = retrieved_verses[0].get("score", 0.0)
    if top_score < CONFIDENCE_THRESHOLD:
        logger.warning(f"[SCRIPTURE] Low retrieval confidence: {top_score:.4f}")
        return {
            "answer": "I am not sufficiently confident to answer that accurately based on available Biblical evidence.",
            "citations": [],
            "confidence": top_score,
            "sources": [],
        }

    # Build context block
    # context_lines = ["RETRIEVED BIBLE CONTEXT (use ONLY these verses):"]
    # for v in retrieved_verses:
    #     context_lines.append(f"[{v['reference']}] {v['text']}")
    # context = "\n".join(context_lines)

    context_lines = [
        "RETRIEVED BIBLE CONTEXT (use ONLY these verses):",
        "The verses are ordered by retrieval relevance. Higher scores are more relevant.",
    ]

    for i, v in enumerate(retrieved_verses, start=1):
        score = float(v.get("score", 0.0))
        context_lines.append(
            f"{i}. [RELEVANCE SCORE: {score:.4f}] "
            f"[{v['reference']}] {v['text']}"
        )

    context = "\n".join(context_lines)

    # Build conversation with memory
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if memory_context:
        messages.append({
            "role": "system",
            "content": f"USER CONTEXT:\n{memory_context}\nUser denomination: {denomination}",
        })

    messages.append({"role": "user", "content": f"{context}\n\nUSER QUESTION: {user_message}"})

    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content.strip()

        # Extract citations from answer
        citations = re.findall(r'\[([A-Za-z1-9 ]+\s+\d+:\d+(?:-\d+)?)\]', answer)

        return {
            "answer": answer,
            "citations": list(set(citations)),
            "confidence": float(top_score),
            "sources": [{"reference": v["reference"], "text": v["text"], "score": v["score"]} for v in retrieved_verses],
        }
    except Exception as e:
        logger.error(f"[SCRIPTURE] LLM call failed: {e}")
        return {
            "answer": "An error occurred while generating the scripture response.",
            "citations": [],
            "confidence": 0.0,
            "sources": [],
        }
