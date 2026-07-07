"""
Prodigal Son signal — grace for repentant callers.

If a caller has past negative history (was on DNO, flagged as fraud, etc.)
but this specific call arrives with full STIR/SHAKEN A attestation and is
calling a number they have never called before, give them a grace bonus.

"There is more joy in heaven over one sinner who repents than over
ninety-nine righteous persons who need no repentance." — Luke 15:7
"""

import logging

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import SIGNAL_WEIGHTS, PRODIGAL_GRACE_BONUS
from ..database import CallRecord, CustomerFeedback, DNOEntry
from ..models import CallRequest
from .signals import SignalResult

logger = logging.getLogger("trust-api.scoring.prodigal")


async def prodigal_signal(session: AsyncSession, req: CallRequest) -> SignalResult:
    if not req.stir_shaken or req.stir_shaken.upper() != "A":
        return SignalResult("prodigal_grace", 0, None, 0.0)

    has_negative_history = await _has_negative_history(session, req.from_number)
    if not has_negative_history:
        return SignalResult("prodigal_grace", 0, None, 0.0)

    is_new_pair = await _is_new_caller_callee_pair(session, req.from_number, req.to_number)
    if not is_new_pair:
        return SignalResult("prodigal_grace", 0, None, 0.0)

    weight = SIGNAL_WEIGHTS.get("prodigal_grace", 1.0)
    logger.info(
        "Prodigal grace applied",
        extra={
            "from_number": req.from_number,
            "to_number": req.to_number,
            "bonus": PRODIGAL_GRACE_BONUS,
        },
    )
    return SignalResult("prodigal_grace", PRODIGAL_GRACE_BONUS, None, weight)


async def _has_negative_history(session: AsyncSession, from_number: str) -> bool:
    dno_stmt = select(func.count(DNOEntry.id)).where(DNOEntry.number == from_number)
    dno_result = await session.execute(dno_stmt)
    dno_count = dno_result.scalar() or 0
    if dno_count > 0:
        return True

    feedback_stmt = (
        select(func.count(CustomerFeedback.id))
        .select_from(CustomerFeedback)
        .join(CallRecord, CallRecord.call_id == CustomerFeedback.call_id)
        .where(
            and_(
                CallRecord.from_number == from_number,
                CustomerFeedback.feedback_type.in_(["suspicious", "confirmed_fraud"]),
            )
        )
    )
    feedback_result = await session.execute(feedback_stmt)
    feedback_count = feedback_result.scalar() or 0
    if feedback_count > 0:
        return True

    call_stmt = (
        select(func.count(CallRecord.id))
        .where(CallRecord.from_number == from_number, CallRecord.decision.in_(["block_analytics", "block_dno"]))
    )
    call_result = await session.execute(call_stmt)
    call_count = call_result.scalar() or 0
    if call_count > 0:
        return True

    return False


async def _is_new_caller_callee_pair(session: AsyncSession, from_number: str, to_number: str) -> bool:
    stmt = (
        select(func.count(CallRecord.id))
        .where(CallRecord.from_number == from_number, CallRecord.to_number == to_number)
    )
    result = await session.execute(stmt)
    count = result.scalar() or 0
    return count == 0
