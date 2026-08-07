"""
Gemini API client with retry logic, fallback models, and error handling.
"""
import time
import logging
from typing import Optional, List, Dict
import google.generativeai as genai

from config import CONFIG

logger = logging.getLogger(__name__)


class GeminiClient:
    """Thread-safe(ish) Gemini client with automatic fallback."""

    def __init__(self):
        self._configure()
        self.primary_model = CONFIG.gemini_model_primary
        self.fallback_model = CONFIG.gemini_model_fallback
        self._primary = None
        self._fallback = None

    def _configure(self):
        """Configure the Gemini API with the key from environment."""
        try:
            genai.configure(api_key=CONFIG.gemini_api_key)
            logger.info("Gemini API configured successfully")
        except ValueError as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise

    @property
    def primary(self) -> genai.GenerativeModel:
        if self._primary is None:
            self._primary = genai.GenerativeModel(self.primary_model)
        return self._primary

    @property
    def fallback(self) -> genai.GenerativeModel:
        if self._fallback is None:
            self._fallback = genai.GenerativeModel(self.fallback_model)
        return self._fallback

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_retries: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text with automatic retry and model fallback.

        Args:
            prompt: The user prompt
            temperature: Generation temperature (0.0 - 1.0)
            max_retries: Override default retry count
            system_instruction: Optional system prompt

        Returns:
            Generated text or error message
        """
        temp = temperature or CONFIG.gemini_temperature
        retries = max_retries or CONFIG.gemini_max_retries

        models_to_try = [
            (self.primary, self.primary_model),
            (self.fallback, self.fallback_model),
        ]

        last_error = None

        for model, model_name in models_to_try:
            for attempt in range(retries):
                try:
                    logger.info(f"Trying {model_name} (attempt {attempt + 1}/{retries})")

                    if system_instruction:
                        chat = model.start_chat(
                            history=[
                                {"role": "user", "parts": [system_instruction]},
                                {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                            ]
                        )
                        response = chat.send_message(prompt)
                    else:
                        response = model.generate_content(
                            prompt,
                            generation_config={"temperature": temp}
                        )

                    text = response.text
                    logger.info(f"Success with {model_name}")
                    return text

                except Exception as e:
                    last_error = e
                    error_msg = str(e).lower()

                    # Check for specific errors
                    if "404" in error_msg or "not found" in error_msg:
                        logger.warning(f"Model {model_name} not found (404). Trying fallback...")
                        break  # Move to next model immediately

                    if "rate limit" in error_msg or "429" in error_msg:
                        wait_time = (attempt + 1) * CONFIG.gemini_retry_delay * 2
                        logger.warning(f"Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    if "quota" in error_msg:
                        logger.warning(f"Quota exceeded for {model_name}. Trying fallback...")
                        break

                    # Generic retry
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * CONFIG.gemini_retry_delay
                        logger.warning(f"Error: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All retries exhausted for {model_name}: {e}")

        # All models failed
        error_str = str(last_error) if last_error else "Unknown error"
        logger.critical(f"All models failed. Last error: {error_str}")
        return f"[AI Error: {error_str}. Please check your API key and model availability.]"

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chat-style generation with conversation history.

        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            system_instruction: Optional system prompt
            temperature: Generation temperature

        Returns:
            Generated response text
        """
        # Build conversation context
        context = ""
        if system_instruction:
            context = f"[System Instructions]: {system_instruction}\n\n"

        for msg in messages[-10:]:  # Last 10 messages for context
            prefix = "User" if msg["role"] == "user" else "Assistant"
            context += f"{prefix}: {msg['content']}\n"

        context += "Assistant:"

        return self.generate(context, temperature=temperature)


# Singleton instance
_client: Optional[GeminiClient] = None


def get_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
