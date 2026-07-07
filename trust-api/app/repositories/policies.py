from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from ..database import Policy
from ..models import PolicyRequest


async def get_customer_policies(session: AsyncSession, customer_id: str) -> list[Policy]:
    stmt = select(Policy).where(
        Policy.customer_id == customer_id,
        Policy.enabled == True,
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_policy(session: AsyncSession, req: PolicyRequest) -> Policy:
    policy = Policy(
        customer_id=req.customer_id,
        policy_name=req.policy_name,
        policy_json=req.policy_json,
        enabled=req.enabled,
    )
    session.add(policy)
    await session.commit()
    await session.refresh(policy)
    return policy


async def update_policy(session: AsyncSession, policy_id: str, req: PolicyRequest) -> Policy | None:
    stmt = (
        update(Policy)
        .where(Policy.id == policy_id)
        .values(
            customer_id=req.customer_id,
            policy_name=req.policy_name,
            policy_json=req.policy_json,
            enabled=req.enabled,
            updated_at=datetime.now(timezone.utc),
        )
        .returning(Policy)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()


async def delete_policy(session: AsyncSession, policy_id: str) -> bool:
    stmt = delete(Policy).where(Policy.id == policy_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0


async def list_policies(session: AsyncSession) -> list[Policy]:
    stmt = select(Policy).order_by(Policy.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
