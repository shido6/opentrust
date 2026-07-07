"""
Call velocity scoring — tracks recent calls per source IP and penalizes bursts.
Phase 1: in-memory sliding window.
Phase 2: replace with Redis or DB-backed counter.
"""

from collections import defaultdict
from datetime import datetime, timezone
from ..config import VELOCITY_MAX_CALLS, VELOCITY_WINDOW_SECONDS
from ..models import CallRequest
from .signals import SignalResult


class VelocityTracker:
    def __init__(self):
        self._calls: dict[str, list[datetime]] = defaultdict(list)

    async def check(self, req: CallRequest) -> SignalResult:
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - VELOCITY_WINDOW_SECONDS
        key = req.source_ip

        # Prune old entries
        self._calls[key] = [
            t for t in self._calls[key]
            if t.timestamp() > cutoff
        ]

        count = len(self._calls[key])
        self._calls[key].append(now)

        if count >= VELOCITY_MAX_CALLS:
            return SignalResult("call_velocity", -30, "velocity_anomaly", 1.0)
        elif count >= VELOCITY_MAX_CALLS // 2:
            return SignalResult("call_velocity", -10, "elevated_velocity", 0.7)

        return SignalResult("call_velocity", 0, None, 0.3)


# Module-level singleton
velocity_tracker = VelocityTracker()
