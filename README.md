# OpenTrust SIP

**Open-source Carrier Trust Engine for ITSPs, CLECs, SIP operators, and enterprise voice providers.**

Make call-blocking and fraud-prevention decisions explainable, observable, auditable, and recoverable.

[!CAUTION]
This is not "AI blocks calls." The engine recommends. The carrier controls policy. Every decision must be explainable and replayable.

## Architecture

```
INVITE
  ↓
Kamailio (SIP policy enforcement)
  ↓
Trust Engine API
  ↓
Decision
  ↓
ALLOW / WARN / CHALLENGE / VOICEMAIL / BLOCK
  ↓
Asterisk (only when media interaction needed)
```

- **Kamailio** — SIP policy enforcement point
- **Trust API** — Policy + evidence + analytics scoring engine
- **Asterisk** — IVR challenge / voicemail screening (media-only)

## Decision Types

| Decision | Action |
|---|---|
| `ALLOW` | Route normally |
| `WARN` | Route with customer-visible warning |
| `CHALLENGE` | Send to Asterisk IVR / screening |
| `VOICEMAIL` | Send to voicemail screening |
| `RATE_LIMIT` | Throttle source or campaign |
| `BLOCK_DNO` | Deterministic policy block (DNO) |
| `BLOCK_ANALYTICS` | Analytics-based block with notification |

## Policy vs Analytics

| DNO (Policy) | Fraud Scoring (Analytics) |
|---|---|
| Deterministic | Probabilistic |
| Explicit block/allow | Risk score + confidence |
| Immediate enforcement | Recommendation only |

Do not mix them. DNO match = deterministic policy. High risk score = probabilistic analytics.

## Rollout Plan

| Phase | Action |
|---|---|
| 1 — Observe | Score calls, no enforcement |
| 2 — Warn | Dashboards, warnings, reporting |
| 3 — Challenge | Asterisk IVR for medium-risk |
| 4 — Block | DNO blocks + analytics blocks separated |
| 5 — Closed-Loop | Feedback + redress → improved scoring |

## Repo Structure

```
opentrust-sip/
  README.md
  SEED.md
  docs/
    architecture.md
    fcc-notes.md
    dno.md
    sip-603-plus.md
    observability.md
    deployment.md
  kamailio/
    route-examples/
    trust-api.cfg
  asterisk/
    ivr-challenge/
    voicemail-screening/
  trust-api/
    app/
    tests/
    Dockerfile
  database/
    schema.sql
    migrations/
  dashboards/
    grafana/
  examples/
    docker-compose.yml
    sample-calls.json
```

## Quick Start

```bash
# Start the full stack
docker compose -f examples/docker-compose.yml up -d

# Check Trust API health
curl http://localhost:8000/health

# Score a call
curl -X POST http://localhost:8000/v1/decision \
  -H 'Content-Type: application/json' \
  -d '{
    "call_id": "abc123",
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "source_ip": "203.0.113.10",
    "source_carrier": "ExampleCarrier",
    "stir_shaken": "A",
    "user_agent": "sip-client",
    "timestamp": "2026-07-06T12:00:00Z"
  }'
```

## Success Metrics

Optimize for **trusted call completion**, not "calls blocked."

- Trusted Call Completion Rate
- False-positive rate / False-negative rate
- Customer override rate
- Redress resolution time
- Support tickets caused by blocking
- Customer churn after intervention
- Fraudulent calls reaching customers
- Legitimate calls completed without friction

## License

MIT
