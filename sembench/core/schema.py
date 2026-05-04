"""Core data models for sembench-ko-fin."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Domain(str, Enum):
    CARD = "card"
    INSURANCE = "insurance"
    DEBT = "debt"
    BANKING = "banking"
    SECURITIES = "securities"
    TAX = "tax"


class ServiceType(str, Enum):
    CHATBOT = "chatbot"
    CLAIM_ADVISOR = "claim_advisor"
    ASSET_MANAGER = "asset_manager"
    DEBT_OPTIMIZER = "debt_optimizer"
    TAX_ASSISTANT = "tax_assistant"
    FRAUD_ALERT = "fraud_alert"


class TurnType(str, Enum):
    SINGLE = "single"
    MULTI = "multi"


class Difficulty(str, Enum):
    L1 = "L1"  # single fact lookup
    L2 = "L2"  # multi-hop reasoning
    L3 = "L3"  # adversarial / privacy stress
    L4 = "L4"  # regulatory / edge case


class RedactionStrategy(str, Enum):
    TOKEN = "token"          # MERCHANT_1 / AMOUNT_1
    TAXONOMY = "taxonomy"    # coffee_chain / high_rate
    RELATION = "relation"    # same_amount / near_time_duplicate
    LIFECYCLE = "lifecycle"  # approved_cancelled_pair
    BAND = "band"            # rate_band / balance_band
    HYBRID = "hybrid"        # combined


# ---------------------------------------------------------------------------
# Test case models
# ---------------------------------------------------------------------------

class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class BenchCase(BaseModel):
    """A single benchmark test case."""
    id: str
    domain: Domain
    service: ServiceType
    turn_type: TurnType
    difficulty: Difficulty
    strategy: RedactionStrategy

    # Raw (private) input — used by local redactor, never sent to external LLM
    raw_utterance: str
    raw_context: dict[str, Any] = Field(default_factory=dict)

    # Multi-turn history (empty for single-turn)
    history: list[Turn] = Field(default_factory=list)

    # Ground truth
    reference_answer: str  # Answer from raw (un-redacted) context — the gold standard
    reference_facts: list[str] = Field(default_factory=list)  # Key facts that must appear in answer

    # Metadata
    tags: list[str] = Field(default_factory=list)
    notes: str = ""
    regulatory_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Scoring models
# ---------------------------------------------------------------------------

class SPSDimension(str, Enum):
    """5 dimensions of the Semantic Preservation Score rubric."""
    INTENT_PRESERVATION = "intent_preservation"
    FACT_ACCURACY = "fact_accuracy"
    REASONING_COMPLETENESS = "reasoning_completeness"
    ACTIONABILITY = "actionability"
    HALLUCINATION_ABSENCE = "hallucination_absence"


class DimensionScore(BaseModel):
    dimension: SPSDimension
    score: int = Field(ge=0, le=4)
    rationale: str


class SPSScore(BaseModel):
    """Semantic Preservation Score: 0–4 on each of 5 dimensions = 0–20 total."""
    case_id: str
    dimension_scores: list[DimensionScore]
    total: float = Field(ge=0.0, le=20.0)
    normalized: float = Field(ge=0.0, le=1.0)  # total / 20
    judge_model: str
    judge_reasoning: str = ""


class ComplianceResult(BaseModel):
    case_id: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    pii_detected: list[str] = Field(default_factory=list)
    risk_tier: Literal["low", "medium", "high"] = "low"


class CaseResult(BaseModel):
    """Full result for one test case run."""
    case_id: str
    adapter_id: str

    # Redacted payload sent to external LLM
    redacted_payload: dict[str, Any]

    # External LLM response on redacted payload
    redacted_response: str

    # External LLM response on raw payload (reference run)
    reference_response: str

    sps: SPSScore
    compliance: ComplianceResult

    # Cost tracking
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


# ---------------------------------------------------------------------------
# Run-level models
# ---------------------------------------------------------------------------

class RunConfig(BaseModel):
    run_id: str
    adapter_id: str
    judge_model: str = "claude-opus-4-5"
    max_cost_usd: float = 100.0
    sample_per_cell: int = 1  # CI smoke = 1, validation = 5
    domains: list[Domain] = Field(default_factory=list)  # empty = all
    difficulties: list[Difficulty] = Field(default_factory=list)  # empty = all
    ensemble_judge_for_difficulties: list[Difficulty] = Field(default_factory=list)


class BenchRun(BaseModel):
    config: RunConfig
    results: list[CaseResult] = Field(default_factory=list)
    total_cases: int = 0
    passed_compliance: int = 0
    mean_sps: float = 0.0
    total_cost_usd: float = 0.0
    aborted: bool = False
    abort_reason: str = ""
