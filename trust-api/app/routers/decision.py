import logging

from fastapi import APIRouter

from ..models import CallRequest, DecisionResponse, DecisionType
from ..scoring import score_call

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1", tags=["decision"])


@router.post("/decision", response_model=DecisionResponse)
async def decide(req: CallRequest):
    trust_score, confidence, signals = score_call(req)

    reason_codes = [s.reason_code for s in signals if s.reason_code]

    if trust_score >= 70:
        decision = DecisionType.allow
        redress_required = False
    elif trust_score >= 50:
        decision = DecisionType.challenge
        redress_required = False
    elif trust_score >= 30:
        decision = DecisionType.block_analytics
        redress_required = True
    else:
        decision = DecisionType.block_analytics
        redress_required = True

    logger.info(
        "Decision",
        extra={
            "call_id": req.call_id,
            "from_number": req.from_number,
            "to_number": req.to_number,
            "decision": decision.value,
            "trust_score": trust_score,
            "confidence": confidence,
            "reason_codes": reason_codes,
        },
    )

    return DecisionResponse(
        decision=decision,
        trust_score=trust_score,
        confidence=confidence,
        reason_codes=reason_codes,
        redress_required=redress_required,
    )
