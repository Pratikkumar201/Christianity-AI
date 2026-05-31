"""
Content Generation Agent
Creates Christian content: sermons, devotionals, prayers, Bible studies, youth lessons, social posts.
All content is grounded in retrieved scripture — never invents verses.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("christianity_ai.content_agent")

CONTENT_TYPES = {
    "sermon": "a complete sermon outline with introduction, 3 main points, illustrations, and conclusion",
    "devotional": "a short daily devotional (300-400 words) with reflection questions",
    "prayer": "a heartfelt prayer appropriate for the given topic",
    "bible study": "a structured Bible study guide with discussion questions",
    "youth lesson": "an engaging youth group lesson with activities",
    "social post": "a short inspiring Christian social media post (under 280 characters)",
}

SYSTEM_PROMPT = """You are a Christian content creator. Generate high-quality, Biblically-grounded content.

CRITICAL RULES:
1. Use ONLY the retrieved Bible verses provided — never quote scripture from memory.
2. Include scripture citations in [Book Chapter:Verse] format throughout the content.
3. Never fabricate or invent Bible references.
4. The content must be theologically sound and reverently written.
5. Include a "Scripture References" section at the end listing all cited verses.
6. If insufficient scripture is available, acknowledge this and only use what was retrieved.

End your response with:
**Scripture References:**
- [All cited verses]"""


def detect_content_type(user_message: str) -> str:
    """Detect the type of content the user wants."""
    lowered = user_message.lower()
    for ctype in CONTENT_TYPES:
        if ctype in lowered:
            return ctype
    return "devotional"  # default


def run_content_generation(
    user_message: str,
    retrieved_verses: List[Dict[str, Any]],
    memory_context: str,
    llm_client,
    denomination: str = "Non-denominational",
) -> Dict[str, Any]:
    """Generate Christian content grounded in retrieved scripture."""
    content_type = detect_content_type(user_message)
    content_desc = CONTENT_TYPES.get(content_type, "Christian content")

    context_lines = ["RETRIEVED BIBLE CONTEXT (use ONLY these verses — do not invent others):"]
    for v in retrieved_verses:
        context_lines.append(f"[{v['reference']}] {v['text']}")
    context = "\n".join(context_lines) if retrieved_verses else "No relevant verses retrieved."

    task_prompt = f"""Generate {content_desc} based on the user's request.

User Request: {user_message}
Target Denomination: {denomination}

{context}

Create the {content_type} now, using ONLY the scripture provided above."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if memory_context:
        messages.append({"role": "system", "content": f"USER CONTEXT:\n{memory_context}"})
    messages.append({"role": "user", "content": task_prompt})

    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=1500,
        )
        answer = response.choices[0].message.content.strip()
        citations = re.findall(r'\[([A-Za-z1-9 ]+\s+\d+:\d+(?:-\d+)?)\]', answer)

        return {
            "answer": answer,
            "content_type": content_type,
            "citations": list(set(citations)),
            "confidence": retrieved_verses[0].get("score", 0.5) if retrieved_verses else 0.3,
            "sources": [{"reference": v["reference"], "text": v["text"]} for v in retrieved_verses],
        }
    except Exception as e:
        logger.error(f"[CONTENT] LLM call failed: {e}")
        return {
            "answer": "Content generation failed. Please try again.",
            "content_type": content_type,
            "citations": [],
            "confidence": 0.0,
            "sources": [],
        }
