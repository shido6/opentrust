"""
Scoring engine — evaluates call metadata against reputation signals.
Phase 1 implementation: simple scoring with expandable signal registry.
"""

from typing import NamedTuple

from .models import CallRequest


class SignalResult(NamedTuple):
    name: str
    score_delta: int
    reason_code: str | None
    weight: float


def score_call(req: CallRequest) -> tuple[int, float, list[SignalResult]]:
    signals: list[SignalResult] = []

    # STIR/SHAKEN signal
    if req.stir_shaken:
        match req.stir_shaken.upper():
            case "A":
                signals.append(SignalResult("stir_shaken", +15, None, 1.0))
            case "B":
                signals.append(SignalResult("stir_shaken", +5, None, 0.8))
            case "C":
                signals.append(SignalResult(
                    "stir_shaken", -10, "low_attestation", 0.9
                ))
            case _:
                signals.append(SignalResult(
                    "stir_shaken", -5, "unknown_attestation", 0.7
                ))
    else:
        signals.append(SignalResult(
            "stir_shaken", -15, "missing_stir_shaken", 1.0
        ))

    # Source carrier presence
    if req.source_carrier:
        signals.append(SignalResult("source_carrier", +5, None, 0.5))
    else:
        signals.append(SignalResult(
            "source_carrier", -5, "missing_source_carrier", 0.6
        ))

    # User agent presence
    if req.user_agent:
        if "friendly" in req.user_agent.lower() or "scanner" in req.user_agent.lower():
            signals.append(SignalResult(
                "user_agent", -20, "suspicious_user_agent", 1.0
            ))
        else:
            signals.append(SignalResult("user_agent", +3, None, 0.3))

    # Compute weighted score
    base_score = 50
    weighted_delta = 0
    total_weight = 0

    for sig in signals:
        weighted_delta += sig.score_delta * sig.weight
        total_weight += sig.weight

    trust_score = max(0, min(100, base_score + int(weighted_delta)))
    confidence = min(1.0, total_weight / 5.0)

    reason_codes = [s.reason_code for s in signals if s.reason_code]

    return trust_score, confidence, signals
