"""Base LLM provider interface and result types."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResult:
    text: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0


class BaseLLMProvider:
    name: str = "base"

    async def chat(self, *, messages: list[dict], model: str, temperature: float = 0.2, max_tokens: int = 1000) -> LLMResult:
        raise NotImplementedError


class MockProvider(BaseLLMProvider):
    """Deterministic offline provider — no API key needed. Clearly labeled [demo]."""
    name = "mock"

    async def chat(self, *, messages: list[dict], model: str = "mock-light", temperature: float = 0.2, max_tokens: int = 1000) -> LLMResult:
        user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_msg = m.get("content", "")
                break
        # Deterministic, keyword-aware response so the UI is exercisable offline.
        text = f"[demo mock] I received your request. You asked: {user_msg[:120]}...\n" \
               "(No LLM API key configured. Set LLM_PROVIDER and the relevant API key for live AI.)"
        return LLMResult(text=text, model=model, provider="mock", prompt_tokens=len(user_msg), completion_tokens=len(text))
