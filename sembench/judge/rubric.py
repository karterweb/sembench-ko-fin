"""SPS rubric definitions and scoring logic."""
from __future__ import annotations

import json
import re

from sembench.core.schema import DimensionScore, SPSDimension, SPSScore
from sembench.llm.base import LLMProvider, LLMResponse

RUBRIC_SYSTEM = """\
You are an expert evaluator for semantic-preserving pseudonymization benchmarks in Korean financial services.

Your task: given (A) a reference answer produced from RAW private data, and (B) a candidate answer
produced from PSEUDONYMIZED data, score how well the candidate preserved the semantics of the reference.

Score each dimension on 0–4:
  4 = Fully preserved — equivalent meaning, no degradation
  3 = Mostly preserved — minor omission or phrasing difference, but actionable
  2 = Partially preserved — key reasoning present but some facts missing or imprecise
  1 = Weakly preserved — significant loss of meaning; user might be misled
  0 = Not preserved — wrong, missing, or contradicted

Dimensions:
1. intent_preservation      — Does the candidate answer the same question as the reference?
2. fact_accuracy            — Are the specific facts (amounts, rates, decisions) correct?
3. reasoning_completeness   — Is the reasoning chain as complete as the reference?
4. actionability            — Can the user take the same action based on this answer?
5. hallucination_absence    — Does the candidate avoid invented facts not in the reference?

Return ONLY valid JSON in this exact shape:
{
  "intent_preservation": {"score": <0-4>, "rationale": "<1 sentence>"},
  "fact_accuracy":        {"score": <0-4>, "rationale": "<1 sentence>"},
  "reasoning_completeness": {"score": <0-4>, "rationale": "<1 sentence>"},
  "actionability":        {"score": <0-4>, "rationale": "<1 sentence>"},
  "hallucination_absence": {"score": <0-4>, "rationale": "<1 sentence>"},
  "overall_reasoning": "<2-3 sentences summarizing the evaluation>"
}
"""

RUBRIC_USER_TEMPLATE = """\
## Reference answer (from raw private data)
{reference}

## Candidate answer (from pseudonymized data)
{candidate}

## Original query
{query}
"""


def score(
    provider: LLMProvider,
    case_id: str,
    query: str,
    reference: str,
    candidate: str,
) -> SPSScore:
    user_msg = RUBRIC_USER_TEMPLATE.format(
        reference=reference, candidate=candidate, query=query
    )
    resp: LLMResponse = provider.complete(RUBRIC_SYSTEM, user_msg)

    raw = resp.content.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    data = json.loads(raw)
    overall = data.pop("overall_reasoning", "")

    dim_scores: list[DimensionScore] = []
    for dim in SPSDimension:
        entry = data.get(dim.value, {})
        dim_scores.append(DimensionScore(
            dimension=dim,
            score=int(entry.get("score", 0)),
            rationale=entry.get("rationale", ""),
        ))

    total = float(sum(d.score for d in dim_scores))
    return SPSScore(
        case_id=case_id,
        dimension_scores=dim_scores,
        total=total,
        normalized=total / 20.0,
        judge_model=provider.model_id,
        judge_reasoning=overall,
    )
