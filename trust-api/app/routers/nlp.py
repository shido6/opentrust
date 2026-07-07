from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import NLPQueryRequest, NLPQueryResponse
from ..nlp.assistant import answer_query
from ..telemetry import nlp_queries_total

router = APIRouter(prefix="/v1/nlp", tags=["nlp"])


@router.post("/query", response_model=NLPQueryResponse)
async def query_assistant(
    req: NLPQueryRequest,
    session: AsyncSession = Depends(get_db),
):
    response = await answer_query(session, req)
    nlp_queries_total.labels(
        intent=response.intent,
        provider=response.provider,
        requires_approval=str(response.requires_approval).lower(),
    ).inc()
    return response
