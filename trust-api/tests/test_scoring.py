import pytest
from app.models import CallRequest
from app.scoring import score_call


def test_high_trust_stir_shaken_a():
    req = CallRequest(
        call_id="test-1",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        source_carrier="VerifiedCarrier",
        stir_shaken="A",
        user_agent="sip-client",
        timestamp="2026-07-06T12:00:00Z",
    )
    score, confidence, signals = score_call(req)
    assert score >= 60
    assert confidence > 0


def test_low_trust_no_stir_shaken():
    req = CallRequest(
        call_id="test-2",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        timestamp="2026-07-06T12:00:00Z",
    )
    score, confidence, signals = score_call(req)
    assert score < 50


def test_suspicious_user_agent():
    req = CallRequest(
        call_id="test-3",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        stir_shaken="A",
        user_agent="friendly-scanner",
        timestamp="2026-07-06T12:00:00Z",
    )
    score, confidence, signals = score_call(req)
    assert any("suspicious_user_agent" in s.reason_code for s in signals if s.reason_code)


def test_low_attestation():
    req = CallRequest(
        call_id="test-4",
        from_number="+15551234567",
        to_number="+15559876543",
        source_ip="203.0.113.10",
        stir_shaken="C",
        user_agent="sip-client",
        timestamp="2026-07-06T12:00:00Z",
    )
    score, confidence, signals = score_call(req)
    assert any("low_attestation" in s.reason_code for s in signals if s.reason_code)
