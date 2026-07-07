"""
Forgiveness repository — queries to support grace-based reputation healing.
"""

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import CallRecord, CustomerFeedback


async def count_wrongly_blocked_feedback(
    session: AsyncSession, from_number: str, customer_id: str
) -> int:
    stmt = (
        select(func.count(CustomerFeedback.id))
        .select_from(CustomerFeedback)
        .join(CallRecord, CallRecord.call_id == CustomerFeedback.call_id)
        .where(
            and_(
                CallRecord.from_number == from_number,
                CustomerFeedback.customer_id == customer_id,
                CustomerFeedback.feedback_type == "wrongly_blocked",
            )
        )
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


async def count_confirmed_fraud_for_number(
    session: AsyncSession, from_number: str
) -> int:
    stmt = (
        select(func.count(CustomerFeedback.id))
        .select_from(CustomerFeedback)
        .join(CallRecord, CallRecord.call_id == CustomerFeedback.call_id)
        .where(
            and_(
                CallRecord.from_number == from_number,
                CustomerFeedback.feedback_type == "confirmed_fraud",
            )
        )
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


async def get_relationship_score(
    session: AsyncSession, customer_id: str
) -> float | None:
    total_stmt = (
        select(func.count(CustomerFeedback.id))
        .where(CustomerFeedback.customer_id == customer_id)
    )
    total_result = await session.execute(total_stmt)
    total = total_result.scalar() or 0
    if total < 3:
        return None

    complaints_stmt = (
        select(func.count(CustomerFeedback.id))
        .where(
            and_(
                CustomerFeedback.customer_id == customer_id,
                CustomerFeedback.feedback_type == "wrongly_blocked",
            )
        )
    )
    complaints_result = await session.execute(complaints_stmt)
    complaints = complaints_result.scalar() or 0

    complaint_ratio = complaints / total
    return max(0.0, 1.0 - complaint_ratio)
