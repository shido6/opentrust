import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import DNOEntryRequest, DNOEntryResponse
from ..repositories import dno as dno_repo
from ..telemetry import dno_matches_counter

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1/dno", tags=["dno"])


@router.get("/", response_model=list[DNOEntryResponse])
async def list_dno(session: AsyncSession = Depends(get_db)):
    entries = await dno_repo.list_dno_entries(session)
    return [
        DNOEntryResponse(
            id=str(e.id),
            number=e.number,
            source=e.source,
            reason=e.reason,
            created_at=e.created_at.isoformat(),
            expires_at=e.expires_at.isoformat(),
        )
        for e in entries
    ]


@router.post("/", response_model=DNOEntryResponse, status_code=201)
async def create_dno(req: DNOEntryRequest, session: AsyncSession = Depends(get_db)):
    entry = await dno_repo.create_dno_entry(session, req)
    dno_matches_counter.labels(source=req.source).inc()
    logger.info("DNO entry created", extra={"number": req.number, "source": req.source})
    return DNOEntryResponse(
        id=str(entry.id),
        number=entry.number,
        source=entry.source,
        reason=entry.reason,
        created_at=entry.created_at.isoformat(),
        expires_at=entry.expires_at.isoformat(),
    )


@router.delete("/{entry_id}")
async def delete_dno(entry_id: str, session: AsyncSession = Depends(get_db)):
    deleted = await dno_repo.delete_dno_entry(session, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="DNO entry not found")
    return {"status": "deleted"}
