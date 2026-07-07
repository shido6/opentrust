"""
Policy evaluation — checks customer-specific allow/block rules.
Policy JSON schema:
{
  "block_numbers": ["+15551234567"],
  "block_prefixes": ["+1900"],
  "allow_numbers": ["+15559876543"],
  "stir_shaken_min": "B",
  "max_trust_score": null
}
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.policies import get_customer_policies
from ..models import CallRequest
from .signals import SignalResult


async def policy_signal(session: AsyncSession, req: CallRequest) -> SignalResult:
    # Resolve customer by the called number (destination account)
    customer_id = req.to_number
    policies = await get_customer_policies(session, customer_id)

    for policy in policies:
        cfg = policy.policy_json

        # Block specific numbers
        blocked_numbers = cfg.get("block_numbers", [])
        if req.from_number in blocked_numbers:
            return SignalResult("policy_eval", -100, f"policy_block:{policy.policy_name}", 1.0)

        # Block prefixes
        blocked_prefixes = cfg.get("block_prefixes", [])
        for prefix in blocked_prefixes:
            if req.from_number.startswith(prefix):
                return SignalResult("policy_eval", -100, f"policy_block:{policy.policy_name}", 1.0)

        # Allow specific numbers (override other signals)
        allowed_numbers = cfg.get("allow_numbers", [])
        if req.from_number in allowed_numbers:
            return SignalResult("policy_eval", +100, f"policy_allow:{policy.policy_name}", 1.0)

        # STIR/SHAKEN minimum
        min_attestation = cfg.get("stir_shaken_min")
        if min_attestation and req.stir_shaken:
            attested_order = {"A": 3, "B": 2, "C": 1}
            req_level = attested_order.get(req.stir_shaken.upper(), 0)
            min_level = attested_order.get(min_attestation.upper(), 0)
            if req_level < min_level:
                return SignalResult("policy_eval", -50, f"policy_below_stir:{policy.policy_name}", 1.0)

    return SignalResult("policy_eval", 0, None, 0.0)
