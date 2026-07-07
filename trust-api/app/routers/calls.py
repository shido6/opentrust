from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories import calls as calls_repo

router = APIRouter(prefix="/v1/calls", tags=["calls"])


@router.get("/{call_id}")
async def get_call(call_id: str, session: AsyncSession = Depends(get_db)):
    record = await calls_repo.get_call(session, call_id)
    if not record:
        raise HTTPException(status_code=404, detail="Call not found")

    events = await calls_repo.get_decision_events(session, call_id)

    return {
        "call_id": record.call_id,
        "timestamp": record.timestamp.isoformat(),
        "from_number": record.from_number,
        "to_number": record.to_number,
        "source_ip": record.source_ip,
        "source_carrier": record.source_carrier,
        "stir_shaken_result": record.stir_shaken_result,
        "decision": record.decision,
        "trust_score": record.trust_score,
        "confidence": record.confidence,
        "call_completed": record.call_completed,
        "duration_seconds": record.duration_seconds,
        "events": [
            {
                "signal_name": e.signal_name,
                "signal_value": e.signal_value,
                "weight": e.weight,
                "reason_code": e.reason_code,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }
