from app.models import CallRequest, DecisionResponse
from app.routers.decision import decide
import pytest


@pytest.mark.asyncio
async def test_decide_high_trust():
    req = CallRequest(
        call_id="test-d1",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        source_carrier="VerifiedCarrier",
        stir_shaken="A",
        user_agent="sip-client",
        timestamp="2026-07-06T12:00:00Z",
    )
    resp = await decide(req)
    assert resp.decision.value == "allow"
    assert resp.trust_score >= 70
    assert not resp.redress_required


@pytest.mark.asyncio
async def test_decide_low_trust():
    req = CallRequest(
        call_id="test-d2",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        timestamp="2026-07-06T12:00:00Z",
    )
    resp = await decide(req)
    assert resp.decision.value in ("block_analytics", "challenge")
    assert resp.trust_score < 50
