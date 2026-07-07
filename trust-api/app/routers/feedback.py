import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import FeedbackRequest, FeedbackResponse
from ..repositories import feedback as feedback_repo
from ..telemetry import false_positive_counter, customer_override_counter

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(req: FeedbackRequest, session: AsyncSession = Depends(get_db)):
    fb = await feedback_repo.create_feedback(session, req)

    if req.feedback_type.value == "wrongly_blocked":
        false_positive_counter.labels(carrier="unknown").inc()
    elif req.feedback_type.value == "wrongly_allowed":
        customer_override_counter.inc()

    logger.info(
        "Feedback submitted",
        extra={
            "call_id": req.call_id,
            "customer_id": req.customer_id,
            "feedback_type": req.feedback_type.value,
        },
    )

    return FeedbackResponse(
        id=str(fb.id),
        call_id=fb.call_id,
        customer_id=fb.customer_id,
        feedback_type=fb.feedback_type,
        notes=fb.notes,
        created_at=fb.created_at.isoformat(),
    )


@router.get("/{call_id}", response_model=list[FeedbackResponse])
async def get_feedback(call_id: str, session: AsyncSession = Depends(get_db)):
    records = await feedback_repo.list_feedback_for_call(session, call_id)
    return [
        FeedbackResponse(
            id=str(f.id),
            call_id=f.call_id,
            customer_id=f.customer_id,
            feedback_type=f.feedback_type,
            notes=f.notes,
            created_at=f.created_at.isoformat(),
        )
        for f in records
    ]
