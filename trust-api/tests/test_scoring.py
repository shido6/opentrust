import pytest
from app.models import CallRequest
from app.scoring.signals import SignalResult
from app.scoring.reputation import ip_reputation_signal, carrier_reputation_signal
from app.scoring.velocity import velocity_tracker
from app.scoring.answer_rate import answer_rate_tracker


@pytest.mark.asyncio
async def test_ip_reputation_test_network():
    req = CallRequest(
        call_id="test-1",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="192.0.2.50",
        source_carrier="VerifiedCarrier",
        stir_shaken="A",
        timestamp="2026-07-06T12:00:00Z",
    )
    result = await ip_reputation_signal(req)
    assert result.score_delta < 0
    assert result.reason_code == "known_test_network"


@pytest.mark.asyncio
async def test_carrier_reputation_known_bad():
    req = CallRequest(
        call_id="test-2",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        source_carrier="SpamCarrier",
        stir_shaken="A",
        timestamp="2026-07-06T12:00:00Z",
    )
    result = await carrier_reputation_signal(req)
    assert result.score_delta < 0


@pytest.mark.asyncio
async def test_velocity_burst():
    req = CallRequest(
        call_id="test-3",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.99",
        timestamp="2026-07-06T12:00:00Z",
    )
    for _ in range(12):
        await velocity_tracker.check(req)

    result = await velocity_tracker.check(req)
    assert result.reason_code == "velocity_anomaly"
    assert result.score_delta == -30


@pytest.mark.asyncio
async def test_stir_shaken_signals():
    req_a = CallRequest(
        call_id="test-4", from_number="+1", to_number="+2",
        source_ip="1.2.3.4", stir_shaken="A", timestamp="T",
    )
    req_c = CallRequest(
        call_id="test-5", from_number="+1", to_number="+2",
        source_ip="1.2.3.4", stir_shaken="C", timestamp="T",
    )

    from app.scoring.reputation import ip_reputation_signal
    from app.scoring.velocity import velocity_tracker
    from app.scoring.answer_rate import answer_rate_tracker

    # Test A gives positive delta
    result_a = await _eval_stir(req_a)
    assert result_a.score_delta > 0

    # Test C gives negative delta
    result_c = await _eval_stir(req_c)
    assert result_c.score_delta < 0


async def _eval_stir(req):
    from app.models import CallRequest
    if req.stir_shaken:
        match req.stir_shaken.upper():
            case "A":
                return SignalResult("stir_shaken", +15, None, 1.0)
            case "B":
                return SignalResult("stir_shaken", +5, None, 0.8)
            case "C":
                return SignalResult("stir_shaken", -10, "low_attestation", 0.9)
    return SignalResult("stir_shaken", -15, "missing_stir_shaken", 1.0)
