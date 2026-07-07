import pytest
from unittest.mock import AsyncMock, patch
from app.models import CallRequest


@pytest.mark.asyncio
async def test_decide_high_trust():
    """High trust call should return allow."""
    req = CallRequest(
        call_id="test-d1",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="10.0.0.1",  # private IP = good
        source_carrier="VerifiedCarrier",
        stir_shaken="A",
        user_agent="Grandstream-GXP2170",
        timestamp="2026-07-06T12:00:00Z",
    )

    # Mock DB session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with patch("app.routers.decision.get_db", return_value=iter([mock_session])):
        from app.routers.decision import decide
        resp = await decide(req, mock_session)
        # Without DB, this will fail on commit — just check basic API response shape
        assert resp.decision.value == "allow"
        assert resp.trust_score >= 70


@pytest.mark.asyncio
async def test_decide_low_trust():
    """Low trust call should return block_analytics or challenge."""
    req = CallRequest(
        call_id="test-d2",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="192.0.2.50",
        stir_shaken="C",
        user_agent="python-requests",
        timestamp="2026-07-06T12:00:00Z",
    )

    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with patch("app.routers.decision.get_db", return_value=iter([mock_session])):
        from app.routers.decision import decide
        resp = await decide(req, mock_session)
        assert resp.decision.value in ("block_analytics", "challenge")
        assert resp.trust_score < 50
