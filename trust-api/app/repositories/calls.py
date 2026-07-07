from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import CallRecord, DecisionEvent
from ..models import CallRequest


async def create_call(session: AsyncSession, req: CallRequest, decision: str, trust_score: int | None, confidence: float | None) -> CallRecord:
    record = CallRecord(
        call_id=req.call_id,
        from_number=req.from_number,
        to_number=req.to_number,
        source_ip=req.source_ip,
        source_carrier=req.source_carrier,
        stir_shaken_result=req.stir_shaken,
        decision=decision,
        trust_score=trust_score,
        confidence=confidence,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_call(session: AsyncSession, call_id: str) -> CallRecord | None:
    stmt = select(CallRecord).where(CallRecord.call_id == call_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_call_cdr(session: AsyncSession, call_id: str, completed: bool, duration_seconds: int) -> CallRecord | None:
    stmt = (
        update(CallRecord)
        .where(CallRecord.call_id == call_id)
        .values(call_completed=completed, duration_seconds=duration_seconds)
        .returning(CallRecord)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()


async def create_decision_event(session: AsyncSession, call_id: str, signal_name: str, signal_value: str | None, weight: float | None, reason_code: str | None) -> DecisionEvent:
    event = DecisionEvent(
        call_id=call_id,
        signal_name=signal_name,
        signal_value=signal_value,
        weight=weight,
        reason_code=reason_code,
    )
    session.add(event)
    await session.commit()
    return event


async def get_decision_events(session: AsyncSession, call_id: str) -> list[DecisionEvent]:
    stmt = select(DecisionEvent).where(DecisionEvent.call_id == call_id).order_by(DecisionEvent.created_at)
    result = await session.execute(stmt)
    return list(result.scalars().all())
