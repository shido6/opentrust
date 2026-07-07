from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from ..database import DNOEntry
from ..models import DNOEntryRequest


async def check_dno(session: AsyncSession, number: str) -> DNOEntry | None:
    stmt = select(DNOEntry).where(
        DNOEntry.number == number,
        DNOEntry.expires_at > datetime.now(timezone.utc),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_dno_entry(session: AsyncSession, req: DNOEntryRequest) -> DNOEntry:
    from datetime import timedelta
    entry = DNOEntry(
        number=req.number,
        source=req.source,
        reason=req.reason,
        expires_at=datetime.now(timezone.utc) + timedelta(days=req.expires_in_days),
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def delete_dno_entry(session: AsyncSession, entry_id: str) -> bool:
    from sqlalchemy import delete
    stmt = delete(DNOEntry).where(DNOEntry.id == entry_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0


async def list_dno_entries(session: AsyncSession) -> list[DNOEntry]:
    stmt = select(DNOEntry).order_by(DNOEntry.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
