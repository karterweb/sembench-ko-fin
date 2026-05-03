"""Passthrough adapter — sends raw context to external LLM (baseline, no redaction)."""
from __future__ import annotations

from typing import Any

from sembench.adapters.base import PseudonymizationAdapter


class PassthroughAdapter(PseudonymizationAdapter):
    """Baseline adapter: no pseudonymization. Used to establish upper-bound SPS."""

    @property
    def adapter_id(self) -> str:
        return "passthrough-baseline"

    def redact(self, raw_utterance: str, raw_context: dict[str, Any]) -> dict[str, Any]:
        return raw_context  # no redaction

    def rehydrate(self, external_response: str, raw_context: dict[str, Any]) -> str:
        return external_response  # no rehydration needed
