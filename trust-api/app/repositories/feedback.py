from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import CustomerFeedback
from ..models import FeedbackRequest


async def create_feedback(session: AsyncSession, req: FeedbackRequest) -> CustomerFeedback:
    record = CustomerFeedback(
        call_id=req.call_id,
        customer_id=req.customer_id,
        feedback_type=req.feedback_type.value,
        notes=req.notes,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def list_feedback_for_call(session: AsyncSession, call_id: str) -> list[CustomerFeedback]:
    stmt = select(CustomerFeedback).where(CustomerFeedback.call_id == call_id).order_by(CustomerFeedback.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
