"""
DNO check — looks up the calling number in the DNO table.
If matched, signals a hard block.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.dno import check_dno
from .signals import SignalResult


async def dno_signal(session: AsyncSession, req) -> SignalResult:
    entry = await check_dno(session, req.from_number)
    if entry:
        return SignalResult("dno_match", -100, "dno_match", 1.0)
    return SignalResult("dno_match", 0, None, 0.0)
