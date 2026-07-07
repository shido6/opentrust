# Gigapipe Observability

Gigapipe is the recommended production observability sink for OpenTrust SIP traces, metrics, and logs. Local Prometheus/Grafana remains useful for development.

## Customer-Backwards Goal

When a customer asks, "Why did this call fail?", the ITSP should be able to answer:

- Which call was affected?
- What decision did OpenTrust SIP make?
- Which policy or analytic signals contributed?
- Was this deterministic DNO blocking or analytics-based blocking?
- Was redress required, created, and resolved?
- Did Kamailio, Asterisk, or the Trust API cause the outcome?

## Collector Path

```text
Kamailio / Asterisk / Trust API
        ↓ OTLP / logs
OpenTelemetry Collector
        ↓ OTLP + auth headers
Gigapipe
        ↓
Customer-impact dashboards, traces, and incident review
```

## Configuration

```bash
export GIGAPIPE_OTLP_ENDPOINT="https://YOUR-GIGAPIPE-OTLP-ENDPOINT:4317"
export GIGAPIPE_API_KEY="YOUR-GIGAPIPE-API-KEY"
export DEPLOYMENT_ENVIRONMENT="production"

docker compose \
  -f examples/docker-compose.yml \
  -f examples/docker-compose.gigapipe.yml \
  up -d
```

## Direct Export

Collector mode is preferred, but the Trust API can export traces directly:

```bash
export OBSERVABILITY_BACKEND=gigapipe
export OTEL_EXPORTER_OTLP_ENDPOINT="https://YOUR-GIGAPIPE-OTLP-ENDPOINT:4317"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer YOUR-GIGAPIPE-API-KEY"
```

## Required Correlation Fields

Every log, trace, metric exemplar, and database record should carry these fields where available:

- `call_id`
- `from_number`
- `to_number`
- `source_ip`
- `source_carrier`
- `decision`
- `trust_score`
- `reason_codes`
- `customer_id`
- `redress_required`

## Minimum Production Dashboards

- Trusted call completion rate by customer and carrier
- Analytics blocks requiring redress
- DNO blocks by source and expiration age
- Challenge completion and abandonment rate
- False positive feedback rate
- Decision latency p50/p95/p99
- Kamailio fail-open events
- Redress time to resolution

## Current Limits

- Kamailio and Asterisk OTLP instrumentation still need deployment-specific log collection.
- Trust API logs are JSON stdout; route them through a collector or host log agent.
- Velocity and answer-rate state remain process-local and should move to Redis/PostgreSQL before horizontal scale.
