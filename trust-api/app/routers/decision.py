import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import REDRESS_CONTACT_URL, REDRESS_CONTACT_EMAIL
from ..models import CallRequest, DecisionResponse, CDRRequest
from ..repositories.calls import create_call, create_decision_event, update_call_cdr
from ..scoring.engine import score_and_decide
from ..scoring.answer_rate import answer_rate_tracker
from ..telemetry import decisions_total, decisions_per_carrier, trust_score_hist, trust_latency, relationship_score_gauge
import time

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1", tags=["decision"])


@router.post("/decision", response_model=DecisionResponse)
async def decide(req: CallRequest, session: AsyncSession = Depends(get_db)):
    start = time.time()

    decision, trust_score, confidence, reason_codes, signals, relationship_score = await score_and_decide(session, req)

    # Persist call record
    await create_call(session, req, decision.value, trust_score, confidence)

    for sig in signals:
        await create_decision_event(
            session,
            req.call_id,
            sig.name,
            str(sig.score_delta),
            sig.weight,
            sig.reason_code,
        )

    # Metrics
    carrier = req.source_carrier or "unknown"
    decisions_total.labels(decision=decision.value, carrier=carrier).inc()
    decisions_per_carrier.labels(carrier=carrier, decision=decision.value).inc()
    trust_score_hist.observe(trust_score)
    relationship_score_gauge.labels(customer_id=req.to_number).set(relationship_score)

    duration = time.time() - start
    trust_latency.observe(duration)

    redness_required = decision.value in ("block_analytics", "block_dno")
    challenged = decision.value == "challenge"
    challenge_mode = "silence" if challenged else None

    logger.info(
        "Decision processed",
        extra={
            "call_id": req.call_id,
            "from": req.from_number,
            "to": req.to_number,
            "decision": decision.value,
            "trust_score": trust_score,
            "confidence": confidence,
            "relationship_score": round(relationship_score, 3),
            "reason_codes": reason_codes,
            "latency": round(duration, 4),
        },
    )

    redress_contact = {}
    if redness_required:
        if REDRESS_CONTACT_URL:
            redress_contact["url"] = REDRESS_CONTACT_URL
        if REDRESS_CONTACT_EMAIL:
            redress_contact["email"] = REDRESS_CONTACT_EMAIL

    return DecisionResponse(
        decision=decision,
        trust_score=trust_score,
        confidence=confidence,
        reason_codes=reason_codes,
        relationship_score=round(relationship_score, 3),
        challenge_mode=challenge_mode,
        redress_required=redness_required,
        redress_contact=redress_contact if redness_required else None,
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
