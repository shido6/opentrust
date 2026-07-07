import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import PolicyRequest, PolicyResponse
from ..repositories import policies as policy_repo

logger = logging.getLogger("trust-api")
router = APIRouter(prefix="/v1/policies", tags=["policies"])


@router.get("/", response_model=list[PolicyResponse])
async def list_policies(session: AsyncSession = Depends(get_db)):
    policies = await policy_repo.list_policies(session)
    return [
        PolicyResponse(
            id=str(p.id),
            customer_id=p.customer_id,
            policy_name=p.policy_name,
            policy_json=p.policy_json,
            enabled=p.enabled,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
        )
        for p in policies
    ]


@router.post("/", response_model=PolicyResponse, status_code=201)
async def create_policy(req: PolicyRequest, session: AsyncSession = Depends(get_db)):
    policy = await policy_repo.create_policy(session, req)
    logger.info("Policy created", extra={"customer_id": req.customer_id, "policy_name": req.policy_name})
    return PolicyResponse(
        id=str(policy.id),
        customer_id=policy.customer_id,
        policy_name=policy.policy_name,
        policy_json=policy.policy_json,
        enabled=policy.enabled,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, req: PolicyRequest, session: AsyncSession = Depends(get_db)):
    policy = await policy_repo.update_policy(session, policy_id, req)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return PolicyResponse(
        id=str(policy.id),
        customer_id=policy.customer_id,
        policy_name=policy.policy_name,
        policy_json=policy.policy_json,
        enabled=policy.enabled,
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
    )


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, session: AsyncSession = Depends(get_db)):
    deleted = await policy_repo.delete_policy(session, policy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"status": "deleted"}
