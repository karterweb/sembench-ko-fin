"""Pipeline runner: loads cases, calls adapter + judge, accumulates results."""
from __future__ import annotations

import uuid
from typing import Any

from sembench.adapters.base import PseudonymizationAdapter
from sembench.core.cost_guard import BudgetExceededError, CostGuard
from sembench.core.schema import (
    BenchCase,
    BenchRun,
    CaseResult,
    RunConfig,
)
from sembench.judge.rubric import score as judge_score
from sembench.llm.base import LLMProvider


class BenchRunner:
    """
    Orchestrates a full benchmark run.

    1. For each case: call adapter.redact() → external LLM (via provider) → adapter.rehydrate()
    2. Also call external LLM on raw context to get the reference answer
    3. Call judge to score SPS
    4. Check compliance
    5. Accumulate CaseResult, enforce budget guard
    """

    def __init__(
        self,
        adapter: PseudonymizationAdapter,
        provider: LLMProvider,
        config: RunConfig | None = None,
    ) -> None:
        self.adapter = adapter
        self.provider = provider
        self.config = config or RunConfig(
            run_id=str(uuid.uuid4())[:8],
            adapter_id=adapter.adapter_id,
        )
        self._guard = CostGuard(self.config.max_cost_usd)

    def run(self, cases: list[BenchCase]) -> BenchRun:
        bench = BenchRun(config=self.config, total_cases=len(cases))
        for case in cases:
            try:
                self._guard.check()
            except BudgetExceededError as exc:
                bench.aborted = True
                bench.abort_reason = str(exc)
                break

            result = self._run_case(case)
            bench.results.append(result)
            self._guard.add(result.cost_usd)
            if result.compliance.passed:
                bench.passed_compliance += 1

        if bench.results:
            bench.mean_sps = sum(r.sps.normalized for r in bench.results) / len(bench.results)
            bench.total_cost_usd = self._guard.spent

        return bench

    def _run_case(self, case: BenchCase) -> CaseResult:
        # Step 1: redact
        redacted_payload = self.adapter.redact(case.raw_utterance, case.raw_context)

        # Step 2: external LLM on redacted payload
        redacted_response = self._call_external(case, redacted_payload)

        # Step 3: external LLM on raw context (reference run)
        reference_response = self._call_external_raw(case)

        # Step 4: rehydrate
        # (rehydration is internal-only; the judge scores redacted_response vs reference_response)

        # Step 5: judge
        sps = judge_score(
            provider=self.provider,
            case_id=case.id,
            query=case.raw_utterance,
            reference=reference_response,
            candidate=redacted_response,
        )

        # Step 6: compliance (placeholder — real checker in Phase 3)
        from sembench.compliance.checker import ComplianceChecker
        compliance = ComplianceChecker().check(case, redacted_payload)

        return CaseResult(
            case_id=case.id,
            adapter_id=self.adapter.adapter_id,
            redacted_payload=redacted_payload,
            redacted_response=redacted_response,
            reference_response=reference_response,
            sps=sps,
            compliance=compliance,
            input_tokens=0,  # filled by provider
            cost_usd=0.0,  # updated by caller
        )

    def _call_external(self, case: BenchCase, payload: dict[str, Any]) -> str:
        import json
        system = "You are a helpful Korean financial services assistant."
        history = self._format_history(case)
        user = (
            f"{history}"
            f"Context: {json.dumps(payload, ensure_ascii=False)}\n\n"
            f"Question: {case.raw_utterance}"
        )
        resp = self.provider.complete(system, user)
        return resp.content

    def _call_external_raw(self, case: BenchCase) -> str:
        import json
        system = "You are a helpful Korean financial services assistant."
        history = self._format_history(case)
        user = (
            f"{history}"
            f"Context: {json.dumps(case.raw_context, ensure_ascii=False)}\n\n"
            f"Question: {case.raw_utterance}"
        )
        resp = self.provider.complete(system, user)
        return resp.content

    def _format_history(self, case: BenchCase) -> str:
        if not case.history:
            return ""
        lines = ["Conversation history:"]
        lines.extend(f"{turn.role}: {turn.content}" for turn in case.history)
        return "\n".join(lines) + "\n\n"
