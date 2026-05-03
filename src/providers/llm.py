from openai import OpenAI
from src.config import setup_logger, Settings

logger = setup_logger(Settings.LOG_DIR / "provider.log", "daemon.providers.llm")


class LLMProvider:
    """Thin, stateless wrapper around the OpenAI-compatible client.
    
    Defaults to Settings values but allows overrides for flexibility.
    """

    def __init__(
        self, 
        base_url: str | None = None, 
        api_key: str | None = None, 
        model: str | None = None
    ) -> None:
        self._client = OpenAI(
            base_url=base_url or Settings.LLM_BASE_URL,
            api_key=api_key or Settings.LLM_API_KEY
        )
        self._model = model or Settings.LLM_MODEL

    def call(
        self,
        system: str,
        user: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request and return the stripped content."""
        try:
            # Use provided overrides or fall back to Settings
            temp = temperature if temperature is not None else Settings.LLM_TEMPERATURE
            tokens = max_tokens if max_tokens is not None else Settings.LLM_MAX_TOKENS

            resp = self._client.chat.completions.create(
                model=self._model,
                temperature=temp,
                max_tokens=tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            raise
