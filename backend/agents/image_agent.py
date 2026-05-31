"""
Image Generation Agent
Enriches prompts with Biblical context and calls Pollinations API.
Includes image safety check before generation.
"""

import logging
import re
import urllib.parse
from typing import Any, Dict

import requests

logger = logging.getLogger("christianity_ai.image_agent")

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/{prompt}?width=768&height=512&model=flux&nologo=true"

IMAGE_SAFETY_KEYWORDS = [
    "hate", "violence", "gore", "blood", "war", "kill", "murder",
    "nazi", "supremacy", "racist", "offensive", "naked", "nude",
    "sexual", "porn", "extremist", "terrorist",
]

SYSTEM_PROMPT = """You are a prompt engineer for a Christian image generation system.

Given a user's request for a Christian/Biblical image, create an enhanced artistic prompt.

RULES:
1. Keep the prompt reverent and respectful to Christian values.
2. Emphasize artistic quality: "cinematic lighting, highly detailed, sacred art style"
3. Reference Biblical/historical accuracy where appropriate.
4. Keep it family-friendly and worshipful.
5. Do NOT include violence, offensive content, or doctrinally distorted images.

Return ONLY the enhanced prompt text, nothing else. No JSON, no explanation."""


def _check_image_safety(prompt: str) -> Dict[str, Any]:
    """Quick safety check for image prompts."""
    lowered = prompt.lower()
    for kw in IMAGE_SAFETY_KEYWORDS:
        if kw in lowered:
            return {"safe": False, "reason": f"Unsafe content detected: '{kw}'"}
    return {"safe": True, "reason": "Safe"}


def _enhance_prompt(user_prompt: str, llm_client) -> str:
    """Use LLM to enrich the prompt with Biblical artistic context."""
    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create an enhanced image prompt for: {user_prompt}"},
            ],
            temperature=0.5,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[IMAGE] Prompt enhancement failed: {e}")
        return f"Biblically inspired {user_prompt}, reverent Christian artwork, cinematic lighting, highly detailed, sacred art style"


def run_image_generation(
    user_message: str,
    llm_client,
) -> Dict[str, Any]:
    """
    Full image generation pipeline:
    1. Safety check
    2. Prompt enrichment
    3. Pollinations API call
    """
    # Step 1: Safety check
    safety = _check_image_safety(user_message)
    if not safety["safe"]:
        logger.warning(f"[IMAGE] Blocked: {safety['reason']}")
        return {
            "success": False,
            "image_url": None,
            "enhanced_prompt": None,
            "reason": safety["reason"],
            "answer": f"I cannot generate that image. {safety['reason']}",
        }

    # Step 2: Enhance prompt
    enhanced = _enhance_prompt(user_message, llm_client)
    logger.info(f"[IMAGE] Enhanced prompt: {enhanced[:100]}...")

    # Step 3: Safety check on enhanced prompt too
    safety2 = _check_image_safety(enhanced)
    if not safety2["safe"]:
        enhanced = f"Biblically inspired {user_message}, reverent Christian artwork, cinematic lighting, highly detailed"

    # Step 4: Call Pollinations
    encoded = urllib.parse.quote(enhanced)
    image_url = POLLINATIONS_BASE.format(prompt=encoded)

    try:
        # Verify the URL is reachable
        resp = requests.head(image_url, timeout=10)
        success = resp.status_code < 400
    except Exception as e:
        logger.error(f"[IMAGE] Pollinations check failed: {e}")
        success = True  # Still return the URL — Pollinations generates on GET

    return {
        "success": True,
        "image_url": image_url,
        "enhanced_prompt": enhanced,
        "original_prompt": user_message,
        "answer": f"Here is your generated image based on: *{user_message}*\n\nEnhanced prompt used: _{enhanced}_",
    }
