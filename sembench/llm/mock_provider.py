"""Mock LLM provider for testing — returns deterministic SPS JSON without real API calls."""
from __future__ import annotations

from sembench.llm.base import LLMProvider, LLMResponse

_MOCK_SPS_JSON = """{
  "intent_preservation": {"score": 3, "rationale": "Mock: intent preserved."},
  "fact_accuracy": {"score": 3, "rationale": "Mock: facts accurate."},
  "reasoning_completeness": {"score": 3, "rationale": "Mock: reasoning complete."},
  "actionability": {"score": 3, "rationale": "Mock: actionable."},
  "hallucination_absence": {"score": 3, "rationale": "Mock: no hallucination."},
  "overall_reasoning": "Mock judge: deterministic test response."
}"""


class MockProvider(LLMProvider):
    """Returns deterministic SPS JSON for testing — no real API calls."""

    def __init__(self, model: str = "mock-judge") -> None:
        self._model = model

    @property
    def model_id(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> LLMResponse:
        return LLMResponse(
            content=_MOCK_SPS_JSON,
            input_tokens=0,
            output_tokens=0,
            model=self._model,
        )
