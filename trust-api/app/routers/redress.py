import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import RedressRequest as RedressRequestModel, RedressUpdate, RedressResponse, RedressStatus
from ..notifications import notify_redress
from ..repositories import redress as redress_repo
from ..telemetry import redress_time_hist

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1/redress", tags=["redress"])


@router.post("/", response_model=RedressResponse, status_code=201)
async def create_redress(req: RedressRequestModel, session: AsyncSession = Depends(get_db)):
    record = await redress_repo.create_redress(session, req)
    logger.info("Redress request created", extra={"call_id": req.call_id, "customer_id": req.customer_id})
    await notify_redress("redress.created", record)
    return RedressResponse(
        id=str(record.id),
        call_id=record.call_id,
        customer_id=record.customer_id,
        status=record.status,
        description=record.description,
        resolution=record.resolution,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


@router.put("/{redress_id}", response_model=RedressResponse)
async def update_redress(redress_id: str, req: RedressUpdate, session: AsyncSession = Depends(get_db)):
    record = await redress_repo.update_redress(session, redress_id, req)
    if not record:
        raise HTTPException(status_code=404, detail="Redress request not found")

    if req.status.value == "resolved" and record.resolved_at and record.created_at:
        hours = (record.resolved_at - record.created_at).total_seconds() / 3600
        redress_time_hist.observe(hours)

    await notify_redress("redress.updated", record)
    return RedressResponse(
        id=str(record.id),
        call_id=record.call_id,
        customer_id=record.customer_id,
        status=record.status,
        description=record.description,
        resolution=record.resolution,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


@router.get("/", response_model=list[RedressResponse])
async def list_redress(
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    records = await redress_repo.list_redress(session, status)
    return [
        RedressResponse(
            id=str(r.id),
            call_id=r.call_id,
            customer_id=r.customer_id,
            status=r.status,
            description=r.description,
            resolution=r.resolution,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in records
    ]
