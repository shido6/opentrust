from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from ..database import RedressRequest
from ..models import RedressRequest as RedressRequestModel, RedressUpdate


async def create_redress(session: AsyncSession, req: RedressRequestModel) -> RedressRequest:
    record = RedressRequest(
        call_id=req.call_id,
        customer_id=req.customer_id,
        description=req.description,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def update_redress(session: AsyncSession, redress_id: str, req: RedressUpdate) -> RedressRequest | None:
    now = datetime.now(timezone.utc)
    values = {
        "status": req.status.value,
        "resolution": req.resolution,
        "updated_at": now,
    }
    if req.status.value == "resolved":
        values["resolved_at"] = now

    stmt = (
        update(RedressRequest)
        .where(RedressRequest.id == redress_id)
        .values(**values)
        .returning(RedressRequest)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()


async def get_redress(session: AsyncSession, redress_id: str) -> RedressRequest | None:
    stmt = select(RedressRequest).where(RedressRequest.id == redress_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_redress(session: AsyncSession, status: str | None = None) -> list[RedressRequest]:
    stmt = select(RedressRequest)
    if status:
        stmt = stmt.where(RedressRequest.status == status)
    stmt = stmt.order_by(RedressRequest.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
