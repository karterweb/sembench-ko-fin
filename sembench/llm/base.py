"""Abstract base class for LLM providers used by the judge."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str

    @property
    def cost_usd(self) -> float:
        # Subclasses should override with real pricing
        return 0.0


class LLMProvider(ABC):
    """Thin wrapper around an LLM API for judge calls."""

    @property
    @abstractmethod
    def model_id(self) -> str: ...

    @abstractmethod
    def complete(self, system: str, user: str) -> LLMResponse: ...
