"""Abstract base class for pseudonymization adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PseudonymizationAdapter(ABC):
    """
    Pluggable interface for any pseudonymization service.

    An adapter takes raw private context and produces a redacted payload
    that is safe to send to an external LLM.
    """

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Unique identifier for this adapter (e.g. 'semantic-redaction-ko-v1')."""
        ...

    @abstractmethod
    def redact(
        self,
        raw_utterance: str,
        raw_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Pseudonymize the raw input.

        Args:
            raw_utterance: The user's natural-language query (may contain PII).
            raw_context: Structured private records (transactions, policies, etc.).

        Returns:
            A dict that is safe to forward to an external LLM.
            Must NOT contain raw PII — the compliance checker will verify this.
        """
        ...

    @abstractmethod
    def rehydrate(
        self,
        external_response: str,
        raw_context: dict[str, Any],
    ) -> str:
        """
        Rehydrate an external LLM response with private detail for the internal user.

        Args:
            external_response: The LLM's response to the redacted payload.
            raw_context: Original private records for token substitution.

        Returns:
            Final user-facing response with private detail restored where appropriate.
        """
        ...
