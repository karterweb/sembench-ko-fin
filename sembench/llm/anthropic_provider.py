"""Anthropic (Claude) LLM provider."""
from __future__ import annotations

import os

import anthropic

from sembench.llm.base import LLMProvider, LLMResponse

# Pricing as of 2025-05 (USD per million tokens)
_PRICING: dict[str, tuple[float, float]] = {
    "claude-opus-4-5":   (15.0, 75.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-3-5":  (0.8,  4.0),
}


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-opus-4-5", api_key: str | None = None) -> None:
        self._model = model
        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    @property
    def model_id(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> LLMResponse:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        first_block = msg.content[0] if msg.content else None
        content = getattr(first_block, "text", "") if first_block else ""
        in_tok = msg.usage.input_tokens
        out_tok = msg.usage.output_tokens
        return _AnthropicResponse(content=content, input_tokens=in_tok, output_tokens=out_tok, model=self._model)


class _AnthropicResponse(LLMResponse):
    @property
    def cost_usd(self) -> float:
        in_price, out_price = _PRICING.get(self.model, (15.0, 75.0))
        return (self.input_tokens * in_price + self.output_tokens * out_price) / 1_000_000
