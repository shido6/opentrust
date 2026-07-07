"""
Historical answer-rate signal.
Phase 1: tracks per-carrier answer rate in-memory.
Phase 2: query from call_history table in DB.
"""

from collections import defaultdict
from ..models import CallRequest
from .signals import SignalResult


class AnswerRateTracker:
    def __init__(self):
        self._answered: dict[str, int] = defaultdict(int)
        self._total: dict[str, int] = defaultdict(int)

    def record_outcome(self, carrier: str | None, answered: bool) -> None:
        if not carrier:
            return
        self._total[carrier] += 1
        if answered:
            self._answered[carrier] += 1

    def rate_for(self, carrier: str | None) -> float | None:
        if not carrier or self._total.get(carrier, 0) < 5:
            return None
        return self._answered[carrier] / self._total[carrier]

    async def check(self, req: CallRequest) -> SignalResult:
        rate = self.rate_for(req.source_carrier)
        if rate is None:
            return SignalResult("answer_rate", -3, "insufficient_answer_data", 0.3)
        if rate < 0.1:
            return SignalResult("answer_rate", -15, "low_answer_rate", 0.8)
        if rate < 0.3:
            return SignalResult("answer_rate", -5, "below_avg_answer_rate", 0.6)
        return SignalResult("answer_rate", +5, None, 0.5)


answer_rate_tracker = AnswerRateTracker()
