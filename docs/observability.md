# Observability

## Philosophy

Every decision is logged. Every log is structured. Every metric is actionable.

## Structured Logging

All decisions emit a structured log record:

```json
{
  "timestamp": "2026-07-06T12:00:00Z",
  "level": "info",
  "service": "trust-api",
  "call_id": "abc123",
  "from_number": "+15551234567",
  "to_number": "+15559876543",
  "decision": "challenge",
  "trust_score": 82,
  "confidence": 0.91,
  "reason_codes": ["velocity_anomaly", "new_source_carrier"],
  "rule_version": "1.2.0",
  "model_version": "2026.07.01",
  "dno_result": false,
  "stir_shaken_result": "A",
  "dns_result": "forward_confirmed",
  "action_taken": "redirect_asterisk",
  "call_outcome": null,
  "customer_feedback": null,
  "support_ticket_ref": null,
  "redress_outcome": null
}
```

## OpenTelemetry Integration

| Signal | Export | Destination |
|---|---|---|
| Traces | OTLP gRPC | OpenTelemetry Collector |
| Metrics | OTLP HTTP | Prometheus / Grafana |
| Logs | JSON stdout | Collector / Gigapipe |

For production ITSP deployments, use Gigapipe as the OpenTelemetry backend. See [Gigapipe Observability](gigapipe.md) for collector configuration, required correlation fields, and customer-impact dashboard guidance.

## Key Metrics

| Metric | Type | Description |
|---|---|---|
| `trust.decisions.total` | Counter | Total decisions by type |
| `trust.decisions.per_carrier` | Counter | Decisions partitioned by source carrier |
| `trust.score` | Histogram | Distribution of trust scores |
| `trust.confidence` | Histogram | Distribution of confidence values |
| `trust.latency` | Histogram | API response time |
| `trust.false_positive` | Counter | Confirmed false positive blocks |
| `trust.dno_matches` | Counter | DNO match count |
| `trust.customer_override` | Counter | Customer override events |
| `trust.redress_time` | Histogram | Time to resolve redress requests |

## Grafana Dashboards

Default dashboards in `dashboards/grafana/`:

- **Trust Overview** — Real-time decisions, scores, latency
- **Carrier Reputation** — Per-carrier trust metrics
- **DNO Monitor** — DNO matches, expires, sources
- **Redress Tracker** — Redress requests, resolution time, outcomes
- **False Positive Analysis** — FP rate, customer overrides, root cause

## Alerting Rules

| Condition | Severity | Action |
|---|---|---|
| False positive rate > 1% | Critical | PagerDuty |
| API latency > 500ms p99 | Warning | Slack |
| DNO table > 48h stale | Warning | Email |
| Redress resolution time > 4h | Warning | Slack |
| Decision throughput drop > 50% | Critical | PagerDuty |

## Database Observability

The `calls` table serves as the source of truth for decision audit. Export to data warehouse via periodic COPY or CDC.
