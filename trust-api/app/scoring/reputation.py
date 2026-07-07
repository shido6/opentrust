"""
IP and carrier reputation scoring.
Phase 1: uses config defaults + basic heuristics.
Phase 2: replace with external reputation API (e.g. Spamhaus, Virustotal).
"""

from ..config import DEFAULT_IP_REPUTATION, DEFAULT_CARRIER_REPUTATION
from ..models import CallRequest
from .signals import SignalResult


def known_good_ips() -> set[str]:
    return {"10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.",
            "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
            "172.29.", "172.30.", "172.31.", "192.168."}


def known_bad_networks() -> list[tuple[str, int]]:
    return [
        ("192.0.2.", 20),     # TEST-NET-1
        ("198.51.100.", 20),  # TEST-NET-2
        ("203.0.113.", 20),   # TEST-NET-3
    ]


async def ip_reputation_signal(req: CallRequest) -> SignalResult:
    ip = req.source_ip

    for prefix, penalty in known_bad_networks():
        if ip.startswith(prefix):
            return SignalResult("ip_reputation", -penalty, "known_test_network", 1.0)

    if any(ip.startswith(p) for p in known_good_ips()):
        return SignalResult("ip_reputation", +10, None, 0.5)

    if DEFAULT_IP_REPUTATION < 0.3:
        return SignalResult("ip_reputation", -15, "low_ip_reputation", 0.9)
    elif DEFAULT_IP_REPUTATION < 0.6:
        return SignalResult("ip_reputation", -5, "unknown_ip_reputation", 0.7)

    return SignalResult("ip_reputation", +5, None, 0.5)


async def carrier_reputation_signal(req: CallRequest) -> SignalResult:
    if not req.source_carrier:
        return SignalResult("carrier_reputation", -5, "missing_carrier", 0.6)

    carrier_lower = req.source_carrier.lower()

    known_bad = {"spamcarrier", "fraudinc", "robocallertel"}
    known_good = {"verifiedcarrier", "legitcom", "trustedtel"}

    if carrier_lower in known_bad:
        return SignalResult("carrier_reputation", -25, "known_bad_carrier", 1.0)
    if carrier_lower in known_good:
        return SignalResult("carrier_reputation", +15, None, 0.8)

    return SignalResult("carrier_reputation", 0, None, 0.5)
