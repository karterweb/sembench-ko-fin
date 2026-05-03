"""Budget guard: abort a run if cumulative cost exceeds the configured cap."""
from __future__ import annotations


class CostGuard:
    def __init__(self, max_cost_usd: float) -> None:
        self._max = max_cost_usd
        self._spent: float = 0.0

    def add(self, cost_usd: float) -> None:
        self._spent += cost_usd

    @property
    def spent(self) -> float:
        return self._spent

    def check(self) -> None:
        if self._spent >= self._max:
            raise BudgetExceededError(
                f"Budget cap of ${self._max:.2f} exceeded (spent ${self._spent:.2f})"
            )


class BudgetExceededError(RuntimeError):
    pass
