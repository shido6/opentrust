# Engineer Deployment Runbook

This runbook is for the engineer deploying OpenTrust SIP into a lab, pilot ITSP environment, or production network.

OpenTrust SIP has four runtime responsibilities:

- Kamailio enforces SIP routing decisions.
- Trust API decides and records evidence.
- PostgreSQL stores durable audit and policy state.
- Observability exports customer-impact traces, metrics, and logs, preferably to Gigapipe.

Do not treat this deployment as compliant by default. See `docs/compliance-readiness.md` before using the system in SOC 2, HIPAA-adjacent, FCC/CPNI, or investor-diligence contexts.

## Requirements

- Docker + Docker Compose (or Podman)
- PostgreSQL 15+
- Kamailio 5.7+
- Asterisk 20+ (LTS)
- Python 3.11+ (Trust API)
- OpenTelemetry Collector for production telemetry
- Gigapipe account/API key for production observability
- Optional NLP backend: local mode, Ollama, OpenAI-compatible API, or Vultr Serverless Inference

## Deployment Modes

| Mode | Purpose | Enforcement |
|---|---|---|
| Development | Local API/DB/metrics smoke testing | No real SIP traffic |
| Pilot | ITSP lab or limited customer traffic | Prefer observe/warn first |
| Production | Carrier traffic | HA, secrets, TLS/mTLS, backups, alerting required |

## Required Secrets

Do not commit these values. Use a secret manager in production.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Trust API PostgreSQL DSN |
| `API_KEY` | Yes | Kamailio/client API key for Trust API |
| `GIGAPIPE_OTLP_ENDPOINT` | Production | Gigapipe OTLP endpoint |
| `GIGAPIPE_API_KEY` | Production | Gigapipe ingest API key |
| `OPENAI_API_KEY` | Optional | OpenAI-compatible NLP provider |
| `VULTR_API_KEY` | Optional | Vultr Serverless Inference |
| `VULTR_INFERENCE_URL` | Optional | Vultr inference endpoint |

## Fresh Checkout

```bash
git clone git@github.com:shido6/opentrust.git
cd opentrust
```

Verify the expected project layout:

```bash
ls README.md trust-api database kamailio asterisk examples docs
```

## Quick Start (Development)

```bash
docker compose -f examples/docker-compose.yml up -d
```

This starts:

- Trust API on `:8000`
- PostgreSQL on `:5432`
- OpenTelemetry Collector on `:4317`
- Prometheus on `:9090`
- Grafana on `:3000`

Development defaults:

- Trust API key: `dev-api-key`
- PostgreSQL user/password/database: `opentrust` / `opentrust` / `opentrust`
- Grafana password: `admin`

Replace all of these in any shared environment.

## Smoke Test

Health check:

```bash
curl http://localhost:8000/health
```

Decision API:

```bash
curl -X POST http://localhost:8000/v1/decision \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-api-key' \
  -d '{
    "call_id": "deploy-smoke-001",
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "source_ip": "203.0.113.10",
    "source_carrier": "ExampleCarrier",
    "stir_shaken": "A",
    "user_agent": "sip-client",
    "timestamp": "2026-07-06T12:00:00Z"
  }'
```

Audit lookup:

```bash
curl -H 'X-API-Key: dev-api-key' \
  http://localhost:8000/v1/calls/deploy-smoke-001
```

NLP assistant:

```bash
curl -X POST http://localhost:8000/v1/nlp/query \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: dev-api-key' \
  -d '{"query":"Why was call deploy-smoke-001 blocked?","call_id":"deploy-smoke-001"}'
```

Metrics:

```bash
curl http://localhost:8000/metrics
```

## Database Setup

For Compose development, `database/schema.sql` initializes the database automatically on first volume creation.

For a managed or existing PostgreSQL database, use Alembic:

```bash
cd database
alembic -c alembic.ini upgrade head
```

If deploying manually from SQL:

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

Verify core tables:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Expected tables include:

- `calls`
- `decision_events`
- `customer_feedback`
- `dno_entries`
- `policies`
- `redress_requests`

## Trust API Production Configuration

Run the API with multiple workers behind a load balancer:

```bash
cd trust-api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Core environment variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | local dev DSN | PostgreSQL connection string |
| `API_KEY` | `change-me-in-production` | Client auth key; replace before deployment |
| `API_KEY_HEADER` | `X-API-Key` | Header used for API auth |
| `LOG_LEVEL` | `info` | Python logging level |
| `LOG_FORMAT` | `json` | Use `json` in production |
| `THRESHOLD_WARN` | `70` | Above this, allow |
| `THRESHOLD_CHALLENGE` | `50` | Challenge threshold |
| `THRESHOLD_BLOCK` | `30` | Low-score analytics block threshold |

## Gigapipe Observability

Preferred production path:

```bash
export GIGAPIPE_OTLP_ENDPOINT="https://YOUR-GIGAPIPE-OTLP-ENDPOINT:4317"
export GIGAPIPE_API_KEY="YOUR-GIGAPIPE-API-KEY"
export DEPLOYMENT_ENVIRONMENT="production"

docker compose \
  -f examples/docker-compose.yml \
  -f examples/docker-compose.gigapipe.yml \
  up -d
```

Trust API direct-export variables:

| Variable | Purpose |
|---|---|
| `OBSERVABILITY_BACKEND=gigapipe` | Tags telemetry resources |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP destination |
| `OTEL_EXPORTER_OTLP_HEADERS` | Example: `authorization=Bearer ...` |
| `SERVICE_NAME` | Defaults to `trust-api` |
| `DEPLOYMENT_ENVIRONMENT` | `dev`, `staging`, `production` |

Use collector mode for production so retries, batching, and resource enrichment are centralized.

See `docs/gigapipe.md` for dashboard and correlation requirements.

## NLP Provider Setup

The NLP assistant is read-only and evidence-grounded. Default mode is local deterministic responses:

```bash
export NLP_PROVIDER=local
```

Ollama:

```bash
export NLP_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export NLP_MODEL=llama3.1
```

OpenAI-compatible:

```bash
export NLP_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
export NLP_MODEL=gpt-4o-mini
```

Vultr Serverless Inference:

```bash
export NLP_PROVIDER=vultr
export VULTR_API_KEY=...
export VULTR_INFERENCE_URL=https://YOUR-VULTR-INFERENCE-ENDPOINT/v1/chat/completions
export NLP_MODEL=llama-3.1-8b-instruct
```

For HIPAA-sensitive or privacy-sensitive deployments, prefer `NLP_PROVIDER=local` unless vendor contracts, BAAs, and redaction controls are approved.

## Production Deployment

### Minimum Topology

```
Kamailio (1+N) → Trust API (2+N behind LB) → PostgreSQL (HA)
                                                       ↓
                                              OpenTelemetry Collector
                                                       ↓
                                              Gigapipe / Prometheus / Grafana
```

### Production Checklist

- Replace all default secrets.
- Put API keys and provider tokens in a secret manager.
- Enable TLS/mTLS between SIP edge, Trust API, database, collector, and vendors.
- Configure PostgreSQL backups and restore tests.
- Configure alert routing for latency, false-positive rate, API downtime, and redress SLA breaches.
- Move process-local velocity and answer-rate state to Redis/PostgreSQL before horizontal scaling.
- Use tenant-scoped auth/RBAC before multi-customer production use.
- Add log redaction and retention policies for phone numbers and customer identifiers.
- Validate Kamailio and Asterisk configs in a lab with representative traffic.

## Kamailio Handoff

Copy and adapt the sample config:

```bash
sudo cp kamailio/trust-api.cfg /etc/kamailio/kamailio.cfg
```

Update at minimum:

- Trust API URL
- API key
- Asterisk IVR/voicemail destinations
- STIR/SHAKEN result extraction
- Fail-open/fail-closed policy
- SIP response mapping

Start or reload Kamailio:

```bash
kamailio -f /etc/kamailio/kamailio.cfg
```

Recommended pilot posture:

- Start in observe-only mode.
- Move to warn-only after metrics are stable.
- Add challenge flows before analytics blocking.
- Keep DNO blocks separate from analytics blocks.

## Asterisk Handoff

Asterisk is only used when media interaction is required.

Install sample challenge/voicemail configs:

```bash
sudo cp asterisk/ivr-challenge/* /etc/asterisk/
sudo cp asterisk/voicemail-screening/* /etc/asterisk/
sudo asterisk -rx "dialplan reload"
```

Before production:

- Replace demo challenge logic with a secure customer experience.
- Bridge successful challenged calls to the intended destination.
- Decide whether voicemail/audio content is stored; if so, apply PHI/PII retention controls.
- Send call completion data to `POST /v1/cdr`.

## Verification Matrix

| Check | Command / Method | Expected Result |
|---|---|---|
| API health | `curl /health` | `status=ok` |
| Auth enforcement | Call `/v1/decision` without key | 401/403 |
| Decision write | `POST /v1/decision` | Decision JSON returned |
| Audit replay | `GET /v1/calls/{call_id}` | Call and decision events returned |
| Metrics | `curl /metrics` | Prometheus metrics returned |
| NLP local | `POST /v1/nlp/query` | Evidence-grounded answer |
| Gigapipe | Check traces/metrics in Gigapipe | `trust-api` service visible |
| CDR update | `POST /v1/cdr` | Call completion updated |
| Grafana dashboards | Open `http://localhost:3000` | OpenTrust dashboards provisioned |

## Grafana Dashboards

Compose provisions dashboards from `dashboards/grafana/provisioning/dashboards/` into Grafana. Use them for NOC screens and quick local validation:

- `OpenTrust SIP - Operator Overview`
- `OpenTrust SIP - Policy vs Analytics`
- `OpenTrust SIP - Redress & Compliance`
- `OpenTrust SIP - Trust API Health`
- `OpenTrust SIP - NLP Assistant Safety`

## Rollback

Trust API rollback:

1. Stop new deployment tasks or pods.
2. Repoint the load balancer to the prior healthy Trust API version.
3. Confirm `/health` and `/v1/decision` on the prior version.
4. Keep PostgreSQL unchanged unless a migration specifically requires rollback.

Database rollback:

1. Prefer forward-fix migrations in production.
2. If rollback is mandatory, restore from a tested backup.
3. Verify `calls` and `decision_events` integrity after restore.

SIP rollback:

1. Revert Kamailio routing config to observe-only or allow-through mode.
2. Reload Kamailio.
3. Confirm calls route normally without Trust API enforcement.

## Compliance Notes

Before production with enterprise, healthcare, government, or regulated customers:

- Review `docs/compliance-readiness.md`.
- Classify call metadata and telemetry.
- Confirm vendor contracts and BAAs where required.
- Define retention periods for call records, decision events, NLP prompts, and observability data.
- Ensure staff access is role-scoped and logged.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---|---|---|
| API returns 401/403 | Missing or wrong `X-API-Key` | Set matching `API_KEY` and client header |
| No decision events in audit | DB write failure or migration mismatch | Check Trust API logs and migration status |
| Gigapipe empty | Collector endpoint/key wrong | Verify `GIGAPIPE_OTLP_ENDPOINT` and `GIGAPIPE_API_KEY` |
| NLP provider fails | Missing provider key or bad endpoint | Use `NLP_PROVIDER=local` or fix provider env vars |
| Kamailio allows all calls | Trust API unreachable and fail-open active | Check API health and Kamailio logs |
| Analytics inconsistent across replicas | In-memory velocity/answer-rate state | Move state to Redis/PostgreSQL |

## Engineer Sign-Off

Do not mark deployment ready until these are true:

- Health checks pass.
- Decision API works with auth.
- Audit replay works for a real call.
- Observability data appears in Gigapipe or the selected backend.
- Rollback path is tested.
- Default secrets are removed.
- Redress and customer support paths are documented.
- Compliance owner has reviewed the deployment posture.
