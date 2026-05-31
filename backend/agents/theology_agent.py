"""
Theology Agent
Denomination-aware theological reasoning.
Presents multiple Christian perspectives without choosing sides.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("christianity_ai.theology_agent")

SYSTEM_PROMPT = """You are a balanced Christian theology assistant.

CRITICAL RULES:
1. NEVER declare one Christian tradition universally correct.
2. NEVER present disputed doctrine as settled fact.
3. Present perspectives from MULTIPLE denominations when traditions differ.
4. Only use the RETRIEVED BIBLE CONTEXT provided — do not quote verses from memory.
5. Always cite retrieved scripture in format [Book Chapter:Verse].
6. If a claim has no retrieved scriptural support, say so explicitly.
7. Maintain a neutral, scholarly, respectful tone.

RESPONSE FORMAT (for contested doctrinal questions):
**Catholic View:** ...
**Protestant View:** ...  
**Orthodox View:** ...
**Areas of Agreement:** ...
**Scripture References:** [cite retrieved verses only]

For uncontested historical/factual questions, give a direct grounded answer with citations.

IMPORTANT: End every response with:
**Sources Used:**
- [List all cited references]"""


def run_theology_discussion(
    user_message: str,
    retrieved_verses: List[Dict[str, Any]],
    memory_context: str,
    llm_client,
    denomination: str = "Non-denominational",
) -> Dict[str, Any]:
    """
    Handle theological questions with denomination-aware, multi-perspective responses.
    """
    context_lines = ["RETRIEVED BIBLE CONTEXT (use ONLY these verses):"]
    for v in retrieved_verses:
        context_lines.append(f"[{v['reference']}] {v['text']}")
    context = "\n".join(context_lines) if retrieved_verses else "No relevant verses retrieved."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if memory_context:
        messages.append({
            "role": "system",
            "content": f"USER CONTEXT:\n{memory_context}\nPreferred denomination: {denomination}",
        })

    messages.append({"role": "user", "content": f"{context}\n\nTHEOLOGICAL QUESTION: {user_message}"})

    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=1200,
        )
        answer = response.choices[0].message.content.strip()
        citations = re.findall(r'\[([A-Za-z1-9 ]+\s+\d+:\d+(?:-\d+)?)\]', answer)

        return {
            "answer": answer,
            "citations": list(set(citations)),
            "confidence": retrieved_verses[0].get("score", 0.5) if retrieved_verses else 0.3,
            "sources": [{"reference": v["reference"], "text": v["text"]} for v in retrieved_verses],
        }
    except Exception as e:
        logger.error(f"[THEOLOGY] LLM call failed: {e}")
        return {
            "answer": "I could not generate a theological response at this time.",
            "citations": [],
            "confidence": 0.0,
            "sources": [],
        }
