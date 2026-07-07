import logging

import httpx

from .config import REDRESS_WEBHOOK_URL

logger = logging.getLogger("trust-api.notifications")


async def notify_redress(event_type: str, record) -> None:
    if not REDRESS_WEBHOOK_URL:
        return

    payload = {
        "event_type": event_type,
        "redress_id": str(record.id),
        "call_id": record.call_id,
        "customer_id": record.customer_id,
        "status": record.status,
        "description": record.description,
        "resolution": record.resolution,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(REDRESS_WEBHOOK_URL, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning(
            "Redress webhook notification failed",
            extra={
                "event_type": event_type,
                "redress_id": str(record.id),
                "call_id": record.call_id,
                "error": str(exc),
            },
        )
