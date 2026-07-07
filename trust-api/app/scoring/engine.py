"""
Scoring engine — evaluates all registered signals and produces a weighted trust score.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import (
    SIGNAL_WEIGHTS,
    THRESHOLD_WARN,
    THRESHOLD_CHALLENGE,
    THRESHOLD_BLOCK,
)
from ..models import CallRequest, DecisionType
from ..repositories.forgiveness import get_relationship_score
from .signals import SignalResult
from .reputation import ip_reputation_signal, carrier_reputation_signal
from .velocity import velocity_tracker
from .answer_rate import answer_rate_tracker
from .dno import dno_signal
from .policies import policy_signal
from .stir_shaken import stir_shaken_signal
from .prodigal import prodigal_signal
from .forgiveness import forgiveness_signal

logger = logging.getLogger("trust-api.scoring")


async def score_and_decide(
    session: AsyncSession,
    req: CallRequest,
) -> tuple[DecisionType, int, float, list[str], list[SignalResult], float]:
    # Evaluate all signals
    signals: list[SignalResult] = []

    # DNO check (deterministic — always first)
    signals.append(await dno_signal(session, req))

    # Policy check
    signals.append(await policy_signal(session, req))

    # Analytics signals
    signals.append(await ip_reputation_signal(req))
    signals.append(await carrier_reputation_signal(req))
    signals.append(await velocity_tracker.check(req))
    signals.append(await answer_rate_tracker.check(req))

    # STIR/SHAKEN
    signals.append(stir_shaken_signal(req))

    # Grace-Oriented Trust Engine signals
    signals.append(await prodigal_signal(session, req))
    signals.append(await forgiveness_signal(session, req))

    # Source carrier signal
    if req.source_carrier:
        signals.append(SignalResult("source_carrier", +5, None, SIGNAL_WEIGHTS["source_carrier"] * 0.6))
    else:
        signals.append(SignalResult("source_carrier", -5, "missing_source_carrier", SIGNAL_WEIGHTS["source_carrier"] * 0.7))

    # User agent signal
    if req.user_agent:
        ua = req.user_agent.lower()
        if any(kw in ua for kw in ("friendly", "scanner", "bot", "python")):
            signals.append(SignalResult("user_agent", -20, "suspicious_user_agent", SIGNAL_WEIGHTS["user_agent"]))
        else:
            signals.append(SignalResult("user_agent", +3, None, SIGNAL_WEIGHTS["user_agent"] * 0.5))

    # Compute weighted score
    base_score = 50
    weighted_delta = 0.0
    total_weight = 0.0

    for sig in signals:
        weighted_delta += sig.score_delta * sig.weight
        total_weight += sig.weight

    trust_score = max(0, min(100, int(base_score + weighted_delta)))
    confidence = min(1.0, total_weight / 10.0) if total_weight > 0 else 0.0

    reason_codes = [s.reason_code for s in signals if s.reason_code]

    # Relationship score — customer trust health based on feedback ratio
    customer_id = req.to_number
    relationship_score = await get_relationship_score(session, customer_id) or 0.5

    # Check for DNO/policy hard block
    for sig in signals:
        if sig.reason_code and sig.reason_code.startswith("dno_match"):
            return DecisionType.block_dno, trust_score, confidence, reason_codes, signals, relationship_score
        if sig.reason_code and sig.reason_code.startswith("policy_block"):
            return DecisionType.block_dno, trust_score, confidence, reason_codes, signals, relationship_score
        if sig.reason_code and sig.reason_code.startswith("policy_allow"):
            return DecisionType.allow, trust_score, confidence, reason_codes, signals, relationship_score

    # Threshold-based decision
    if trust_score >= THRESHOLD_WARN:
        return DecisionType.allow, trust_score, confidence, reason_codes, signals, relationship_score
    elif trust_score >= THRESHOLD_CHALLENGE:
        return DecisionType.challenge, trust_score, confidence, reason_codes, signals, relationship_score

    redress_required = trust_score < THRESHOLD_BLOCK
    if redress_required:
        return DecisionType.block_analytics, trust_score, confidence, reason_codes, signals, relationship_score

    return DecisionType.block_analytics, trust_score, confidence, reason_codes, signals, relationship_score
