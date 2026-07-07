from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import NLPQueryRequest, NLPQueryResponse
from ..nlp.assistant import answer_query

router = APIRouter(prefix="/v1/nlp", tags=["nlp"])


@router.post("/query", response_model=NLPQueryResponse)
async def query_assistant(
    req: NLPQueryRequest,
    session: AsyncSession = Depends(get_db),
):
    return await answer_query(session, req)
