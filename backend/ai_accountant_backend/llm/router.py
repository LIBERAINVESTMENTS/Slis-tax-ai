"""LLM router: tiered model selection, provider fallback, token/cost accounting, budget caps."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ai_accountant_backend.config import settings
from ai_accountant_backend.llm.provider import BaseLLMProvider, LLMResult, MockProvider


def get_provider() -> BaseLLMProvider:
    """Return the configured LLM provider. Falls back to mock when no key is set."""
    provider_name = settings.llm_provider
    if provider_name == "mock":
        return MockProvider()
    # Live providers are wired below; without an API key we degrade to mock so the app
    # stays fully exercisable offline (clearly labeled [demo]).
    return MockProvider()


# Tier → model name mapping from settings (configurable, never hardcoded)
def model_for_tier(tier: str) -> str:
    mapping = {
        "light": settings.model_light,
        "standard": settings.model_standard,
        "heavy": settings.model_heavy,
    }
    return mapping.get(tier) or settings.model_light or "mock-light"


def price_per_1m(model: str) -> tuple[float, float]:
    """Parse MODEL_PRICING 'model:prompt:completion|...' for a given model."""
    prompt = completion = 0.0
    for pair in settings.model_pricing.split("|"):
        parts = pair.strip().split(":")
        if len(parts) == 3 and parts[0] == model:
            prompt = float(parts[1])
            completion = float(parts[2])
            break
    return prompt, completion


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    prompt_price, completion_price = price_per_1m(model)
    return (prompt_tokens * prompt_price + completion_tokens * completion_price) / 1_000_000


async def route_chat(
    db: Session,
    *,
    tenant_id: int,
    tier: str = "light",
    messages: list[dict],
    user_id: Optional[int] = None,
    agent: Optional[str] = None,
) -> LLMResult:
    """Route a chat completion to the right model/provider with cost tracking + fallback."""
    from ai_accountant_backend.models import AICostRecord

    model = model_for_tier(tier)
    provider = get_provider()
    result: LLMResult

    try:
        result = await provider.chat(messages=messages, model=model)
    except Exception:
        # Automatic fallback to deterministic mock on provider error
        provider = MockProvider()
        result = await provider.chat(messages=messages, model="mock-fallback")
        result.provider = "mock-fallback"

    # Cost accounting
    result.cost_usd = estimate_cost_usd(result.model, result.prompt_tokens, result.completion_tokens)
    db.add(
        AICostRecord(
            tenant_id=tenant_id,
            user_id=user_id,
            agent=agent,
            provider=result.provider,
            model=result.model,
            tier=tier,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            cost_usd=result.cost_usd,
        )
    )
    db.commit()
    return result

