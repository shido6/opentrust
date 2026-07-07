"""
STIR/SHAKEN signal evaluation.

`attestation_only` mode trusts a previously verified upstream attestation value.
`passport_structural` mode parses the SIP Identity PASSporT enough to detect
missing/malformed identity and attestation/origination mismatches. Full x5u cert
chain and TNAuthList validation should be added before regulated enforcement.
"""

import base64
import json

from ..config import SIGNAL_WEIGHTS, STIR_SHAKEN_VERIFY_MODE
from ..models import CallRequest
from .signals import SignalResult


def stir_shaken_signal(req: CallRequest) -> SignalResult:
    if STIR_SHAKEN_VERIFY_MODE == "passport_structural" and req.identity_header:
        structural = _parse_passport(req.identity_header, req)
        if structural.reason_code:
            return structural

    if req.stir_shaken:
        match req.stir_shaken.upper():
            case "A":
                return SignalResult("stir_shaken", +15, None, SIGNAL_WEIGHTS["stir_shaken"])
            case "B":
                return SignalResult("stir_shaken", +5, None, SIGNAL_WEIGHTS["stir_shaken"] * 0.8)
            case "C":
                return SignalResult("stir_shaken", -10, "low_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.9)
            case _:
                return SignalResult("stir_shaken", -5, "unknown_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.7)

    if STIR_SHAKEN_VERIFY_MODE == "passport_structural":
        return SignalResult("stir_shaken", -25, "missing_identity_header", SIGNAL_WEIGHTS["stir_shaken"])

    return SignalResult("stir_shaken", -15, "missing_stir_shaken", SIGNAL_WEIGHTS["stir_shaken"])


def _parse_passport(identity_header: str, req: CallRequest) -> SignalResult:
    token = identity_header.split(";", 1)[0].strip()
    parts = token.split(".")
    if len(parts) != 3:
        return SignalResult("stir_shaken", -25, "malformed_identity_header", SIGNAL_WEIGHTS["stir_shaken"])

    try:
        header = _decode_json(parts[0])
        payload = _decode_json(parts[1])
    except (ValueError, json.JSONDecodeError):
        return SignalResult("stir_shaken", -25, "malformed_passport", SIGNAL_WEIGHTS["stir_shaken"])

    if header.get("ppt") not in (None, "shaken"):
        return SignalResult("stir_shaken", -10, "unsupported_passport_type", SIGNAL_WEIGHTS["stir_shaken"] * 0.6)

    attest = payload.get("attest")
    if not attest:
        return SignalResult("stir_shaken", -20, "missing_passport_attestation", SIGNAL_WEIGHTS["stir_shaken"])

    passport_orig = _extract_orig(payload)
    if passport_orig and _normalize_number(passport_orig) != _normalize_number(req.from_number):
        return SignalResult("stir_shaken", -25, "passport_orig_mismatch", SIGNAL_WEIGHTS["stir_shaken"])

    if attest == "A":
        return SignalResult("stir_shaken", +15, None, SIGNAL_WEIGHTS["stir_shaken"])
    if attest == "B":
        return SignalResult("stir_shaken", +5, None, SIGNAL_WEIGHTS["stir_shaken"] * 0.8)
    if attest == "C":
        return SignalResult("stir_shaken", -10, "low_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.9)

    return SignalResult("stir_shaken", -5, "unknown_attestation", SIGNAL_WEIGHTS["stir_shaken"] * 0.7)


def _decode_json(segment: str) -> dict:
    padded = segment + "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))


def _extract_orig(payload: dict) -> str | None:
    orig = payload.get("orig") or {}
    if isinstance(orig, dict):
        return orig.get("tn") or orig.get("uri")
    return None


def _normalize_number(value: str) -> str:
    if value.startswith("sip:"):
        value = value[4:].split("@", 1)[0]
    return "".join(ch for ch in value if ch.isdigit())
