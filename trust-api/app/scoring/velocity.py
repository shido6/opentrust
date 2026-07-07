"""
Call velocity scoring — tracks recent calls per source IP and penalizes bursts.
Use Redis in production for multi-replica deployments; memory mode is for local dev.
"""

from collections import defaultdict
from datetime import datetime, timezone

from ..config import REDIS_URL, VELOCITY_BACKEND, VELOCITY_MAX_CALLS, VELOCITY_WINDOW_SECONDS
from ..models import CallRequest
from .signals import SignalResult


class VelocityTracker:
    def __init__(self):
        self._calls: dict[str, list[datetime]] = defaultdict(list)
        self._redis = None

    async def check(self, req: CallRequest) -> SignalResult:
        if VELOCITY_BACKEND == "redis":
            return await self._check_redis(req)
        return await self._check_memory(req)

    async def _check_redis(self, req: CallRequest) -> SignalResult:
        if self._redis is None:
            try:
                from redis.asyncio import from_url

                self._redis = from_url(REDIS_URL, decode_responses=True)
            except ImportError:
                return SignalResult("call_velocity", -5, "redis_velocity_unavailable", 0.5)

        key = f"opentrust:velocity:{req.source_ip}"
        try:
            count = await self._redis.incr(key)
            if count == 1:
                await self._redis.expire(key, VELOCITY_WINDOW_SECONDS)
            return self._result_for_count(count - 1)
        except Exception:
            return SignalResult("call_velocity", -5, "redis_velocity_error", 0.5)

    async def _check_memory(self, req: CallRequest) -> SignalResult:
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - VELOCITY_WINDOW_SECONDS
        key = req.source_ip

        self._calls[key] = [
            t for t in self._calls[key]
            if t.timestamp() > cutoff
        ]

        count = len(self._calls[key])
        self._calls[key].append(now)
        return self._result_for_count(count)

    def _result_for_count(self, count: int) -> SignalResult:
        if count >= VELOCITY_MAX_CALLS:
            return SignalResult("call_velocity", -30, "velocity_anomaly", 1.0)
        elif count >= VELOCITY_MAX_CALLS // 2:
            return SignalResult("call_velocity", -10, "elevated_velocity", 0.7)

        return SignalResult("call_velocity", 0, None, 0.3)


velocity_tracker = VelocityTracker()
