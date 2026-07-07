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
from ..repositories.calls import create_decision_event
from .signals import SignalResult
from .reputation import ip_reputation_signal, carrier_reputation_signal
from .velocity import velocity_tracker
from .answer_rate import answer_rate_tracker
from .dno import dno_signal
from .policies import policy_signal

logger = logging.getLogger("trust-api.scoring")


async def score_and_decide(
    session: AsyncSession,
    req: CallRequest,
) -> tuple[DecisionType, int, float, list[str]]:
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
    if req.stir_shaken:
        match req.stir_shaken.upper():
            case "A":
                signals.append(SignalResult("stir_shaken", +15, None, SIGNAL_WEIGHTS["stir_shaken"]))
            case "B":
                signals.append(SignalResult("stir_shaken", +5, None, SIGNAL_WEIGHTS["stir_shaken"] * 0.8))
            case "C":
                signals.append(SignalResult("stir_shaken", -10, "low_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.9))
            case _:
                signals.append(SignalResult("stir_shaken", -5, "unknown_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.7))
    else:
        signals.append(SignalResult("stir_shaken", -15, "missing_stir_shaken", SIGNAL_WEIGHTS["stir_shaken"]))

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
    confidence = min(1.0, total_weight / 8.0) if total_weight > 0 else 0.0

    reason_codes = [s.reason_code for s in signals if s.reason_code]

    # Persist signal events
    for sig in signals:
        await create_decision_event(
            session,
            req.call_id,
            sig.name,
            str(sig.score_delta),
            sig.weight,
            sig.reason_code,
        )

    # Check for DNO/policy hard block
    for sig in signals:
        if sig.reason_code and sig.reason_code.startswith("dno_match"):
            return DecisionType.block_dno, trust_score, confidence, reason_codes
        if sig.reason_code and sig.reason_code.startswith("policy_block"):
            return DecisionType.block_dno, trust_score, confidence, reason_codes
        if sig.reason_code and sig.reason_code.startswith("policy_allow"):
            return DecisionType.allow, trust_score, confidence, reason_codes

    # Threshold-based decision
    if trust_score >= THRESHOLD_WARN:
        return DecisionType.allow, trust_score, confidence, reason_codes
    elif trust_score >= THRESHOLD_CHALLENGE:
        return DecisionType.challenge, trust_score, confidence, reason_codes

    redress_required = trust_score < THRESHOLD_BLOCK
    if redress_required:
        return DecisionType.block_analytics, trust_score, confidence, reason_codes

    return DecisionType.block_analytics, trust_score, confidence, reason_codes
