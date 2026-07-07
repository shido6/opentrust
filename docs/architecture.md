# Architecture

## Overview

OpenTrust SIP is a modular carrier trust engine that separates SIP routing (Kamailio), media handling (Asterisk), and decision logic (Trust API) into distinct layers.

## System Diagram

```
                    +------------------+
                    |   SIP Carrier    |
                    |    (Ingress)     |
                    +--------+---------+
                             |
                     INVITE (SIP)
                             |
                    +--------v---------+
                    |    Kamailio      |
                    |  SIP Proxy       |
                    +--------+---------+
                             |
                     HTTP POST /v1/decision
                             |
                    +--------v---------+
                    |   Trust API      |
                    |  (FastAPI)       |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   PostgreSQL     |
                    | calls, policies  |
                    | dno, feedback    |
                    +--------+---------+
                             |
                    Decision returned
                             |
                    +--------v---------+
                    |   Kamailio       |
                    |  enforces action |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
         ALLOW/WARN    CHALLENGE      BLOCK/DNO
              |              |              |
              v              v              v
         Route SIP    Asterisk IVR   603+ SIP response
                      voicemail
```

## Trust API

The Trust API is a stateless HTTP service that evaluates per-call metadata against policy rules, analytics signals, and reputation data. It returns a decision with trust score, confidence, and reason codes.

### Input

```json
{
  "call_id": "abc123",
  "from_number": "+15551234567",
  "to_number": "+15559876543",
  "source_ip": "203.0.113.10",
  "source_carrier": "ExampleCarrier",
  "stir_shaken": "A",
  "user_agent": "sip-client",
  "timestamp": "2026-07-06T12:00:00Z"
}
```

### Output

```json
{
  "decision": "challenge",
  "trust_score": 82,
  "confidence": 0.91,
  "reason_codes": ["velocity_anomaly", "new_source_carrier"],
  "recommended_sip_response": null,
  "redress_required": false
}
```

## Decision Flow

```python
def decide(call_data):
    # 1. DNO check (deterministic policy)
    dno = check_dno(call_data.from_number)
    if dno:
        return BLOCK_DNO

    # 2. Policy evaluation (customer-specific rules)
    policy = get_policy(call_data.to_number)
    if policy and not policy.evaluate(call_data):
        return BLOCK_DNO

    # 3. Analytics scoring (probabilistic)
    score = score_call(call_data)
    if score.trust < THRESHOLD_WARN:
        return WARN
    if score.trust < THRESHOLD_CHALLENGE:
        return CHALLENGE
    if score.trust < THRESHOLD_BLOCK:
        return BLOCK_ANALYTICS

    # 4. Allow
    return ALLOW
```

## Data Layer

PostgreSQL serving five core tables: `calls`, `decision_events`, `customer_feedback`, `dno_entries`, `policies`. Migrations managed via Alembic.

## Observability

All decisions produce structured logs ingested via OpenTelemetry. Grafana dashboards consume metrics for trusted call completion rate, false positives, and redress metrics.
