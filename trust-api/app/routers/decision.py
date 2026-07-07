import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import CallRequest, DecisionResponse, CDRRequest
from ..repositories.calls import create_call, update_call_cdr
from ..scoring.engine import score_and_decide
from ..scoring.answer_rate import answer_rate_tracker
from ..telemetry import decisions_total, decisions_per_carrier, trust_score_hist, trust_latency
import time

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1", tags=["decision"])


@router.post("/decision", response_model=DecisionResponse)
async def decide(req: CallRequest, session: AsyncSession = Depends(get_db)):
    start = time.time()

    decision, trust_score, confidence, reason_codes = await score_and_decide(session, req)

    # Persist call record
    await create_call(session, req, decision.value, trust_score, confidence)

    # Metrics
    carrier = req.source_carrier or "unknown"
    decisions_total.labels(decision=decision.value, carrier=carrier).inc()
    decisions_per_carrier.labels(carrier=carrier, decision=decision.value).inc()
    trust_score_hist.observe(trust_score)

    duration = time.time() - start
    trust_latency.observe(duration)

    redness_required = decision.value in ("block_analytics", "block_dno")

    logger.info(
        "Decision processed",
        extra={
            "call_id": req.call_id,
            "from": req.from_number,
            "to": req.to_number,
            "decision": decision.value,
            "trust_score": trust_score,
            "confidence": confidence,
            "reason_codes": reason_codes,
            "latency": round(duration, 4),
        },
    )

    return DecisionResponse(
        decision=decision,
        trust_score=trust_score,
        confidence=confidence,
        reason_codes=reason_codes,
        redress_required=redness_required,
    )


@router.post("/cdr", response_model=dict)
async def post_cdr(cdr: CDRRequest, session: AsyncSession = Depends(get_db)):
    record = await update_call_cdr(session, cdr.call_id, cdr.completed, cdr.duration_seconds)
    if not record:
        return {"status": "not_found", "call_id": cdr.call_id}

    # Feed answer-rate tracker
    answer_rate_tracker.record_outcome(record.source_carrier, cdr.completed)

    logger.info(
        "CDR processed",
        extra={
            "call_id": cdr.call_id,
            "completed": cdr.completed,
            "duration": cdr.duration_seconds,
        },
    )

    return {"status": "ok", "call_id": cdr.call_id}
