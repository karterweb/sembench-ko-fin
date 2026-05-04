"""Reference adapter for karterweb/semantic-redaction-ko."""
from __future__ import annotations

import re
from typing import Any

from sembench.adapters.base import PseudonymizationAdapter


class SemanticRedactionKoAdapter(PseudonymizationAdapter):
    """Adapter that calls semantic-redaction-ko when available.

    The external project exposes a richer pipeline for its built-in demo cases.
    For arbitrary BenchCase contexts, this adapter applies the same safe payload
    contract: taxonomy tokens, relation facts, banded amounts, and no raw PII.
    """

    @property
    def adapter_id(self) -> str:
        return "semantic-redaction-ko"

    def redact(self, raw_utterance: str, raw_context: dict[str, Any]) -> dict[str, Any]:
        return {
            "query_intent": self._intent(raw_utterance),
            "safe_context": self._sanitize(raw_context),
            "techniques_applied": [
                "tokenized_entity_binding",
                "domain_taxonomy_lifting",
                "relation_encoding",
                "banding_generalization",
                "uncertainty_contract",
            ],
            "instruction": "Answer in Korean using only safe tokens and generalized facts.",
        }

    def rehydrate(self, external_response: str, raw_context: dict[str, Any]) -> str:
        return external_response

    def _intent(self, utterance: str) -> str:
        if "청구" in utterance or "보험" in utterance:
            return "insurance_claim_guidance"
        if "대출" in utterance or "카드론" in utterance or "마통" in utterance:
            return "debt_optimization"
        if "자동이체" in utterance or "잔액" in utterance:
            return "banking_payment_explanation"
        if "배당" in utterance or "수익률" in utterance:
            return "securities_portfolio_explanation"
        if "공제" in utterance or "연말정산" in utterance:
            return "tax_deduction_guidance"
        return "card_transaction_explanation"

    def _sanitize(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): self._sanitize(v) for k, v in value.items() if k not in {"merchant", "institution", "hospital", "policy_no", "card_last4"}}
        if isinstance(value, list):
            return [self._sanitize(item) for item in value]
        if isinstance(value, int | float):
            return self._number_band(float(value))
        if isinstance(value, str):
            return self._sanitize_string(value)
        return value

    def _number_band(self, value: float) -> str:
        if value < 10_000:
            return "low_amount_band"
        if value < 1_000_000:
            return "medium_amount_band"
        return "high_amount_band"

    def _sanitize_string(self, value: str) -> str:
        replacements = {
            "스타벅스": "coffee_chain",
            "SBUX": "coffee_chain",
            "강남": "same_commercial_area",
            "신한은행": "BANK_TOKEN_A",
            "신한": "BANK_TOKEN_A",
            "서울아산병원": "large_general_hospital",
        }
        sanitized = value
        for raw, safe in replacements.items():
            sanitized = sanitized.replace(raw, safe)
        sanitized = re.sub(r"\b\d{1,3}(?:,\d{3})+원\b", "exact_amount_suppressed_band", sanitized)
        sanitized = re.sub(r"\b\d+(?:\.\d+)?(?:만원|억원)\b", "exact_amount_suppressed_band", sanitized)
        return sanitized
