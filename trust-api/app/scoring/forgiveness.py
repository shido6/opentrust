"""
Forgiveness signal — customer feedback heals caller reputation.

When a customer marks a call as "wrongly_blocked", the system forgives
that caller's past sins. Future calls from that number to that customer
get a strong positive signal.

"Father, forgive them, for they know not what they spoof." — adapted
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import SIGNAL_WEIGHTS, FORGIVENESS_BONUS
from ..models import CallRequest
from ..repositories.forgiveness import count_wrongly_blocked_feedback
from .signals import SignalResult

logger = logging.getLogger("trust-api.scoring.forgiveness")


async def forgiveness_signal(session: AsyncSession, req: CallRequest) -> SignalResult:
    customer_id = req.to_number

    forgiveness_count = await count_wrongly_blocked_feedback(
        session, req.from_number, customer_id
    )

    if forgiveness_count > 0:
        weight = SIGNAL_WEIGHTS.get("forgiveness", 1.0)
        bonus = FORGIVENESS_BONUS * min(forgiveness_count, 5)
        logger.info(
            "Forgiveness applied",
            extra={
                "from_number": req.from_number,
                "customer_id": customer_id,
                "forgiveness_count": forgiveness_count,
                "bonus": bonus,
            },
        )
        return SignalResult("forgiveness", bonus, None, weight)

    return SignalResult("forgiveness", 0, None, 0.0)
