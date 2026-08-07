"""
Text-to-Speech module using Edge TTS.
"""
import asyncio
import io
import re
import logging
from typing import Optional

import edge_tts

from config import CONFIG, LANGUAGES

logger = logging.getLogger(__name__)


def clean_text_for_tts(text: str) -> str:
    """Remove markdown and HTML tags that break TTS."""
    # Remove markdown
    text = re.sub(r'\*\*|\*|__|_|#|`|>', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove brackets
    text = re.sub(r'\[|\]|\(|\)', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text


async def _generate_audio_async(text: str, voice: str) -> bytes:
    """Async core TTS generation."""
    clean_text = clean_text_for_tts(text)

    if not clean_text.strip():
        return b""

    communicate = edge_tts.Communicate(
        clean_text,
        voice,
        rate=CONFIG.tts_default_speed,
        volume=CONFIG.tts_volume
    )

    mp3_data = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data.write(chunk["data"])

    mp3_data.seek(0)
    return mp3_data.read()


def text_to_speech(text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
    """
    Convert text to MP3 audio bytes.

    Args:
        text: Text to speak
        language: Language code (en/ru) — auto-selects voice if voice not given
        voice: Specific Edge TTS voice name

    Returns:
        MP3 audio bytes
    """
    if voice is None:
        lang = language or "en"
        voice = LANGUAGES[lang].voice

    try:
        return asyncio.run(_generate_audio_async(text, voice))
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return b""


def get_available_voices() -> dict:
    """Return available voices per language."""
    return {
        "en": ["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural", "en-GB-RyanNeural"],
        "ru": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural", "ru-RU-EkaterinaNeural"],
    }
