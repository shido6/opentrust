# Deployment

## Requirements

- Docker + Docker Compose (or Podman)
- PostgreSQL 15+
- Kamailio 5.7+
- Asterisk 20+ (LTS)
- Python 3.11+ (Trust API)

## Quick Start (Development)

```bash
docker compose -f examples/docker-compose.yml up -d
```

This starts:
- Trust API on `:8000`
- PostgreSQL on `:5432`
- OpenTelemetry Collector on `:4317`

## Production Deployment

### Minimum Topology

```
Kamailio (1+N) → Trust API (2+N behind LB) → PostgreSQL (HA)
                                                       ↓
                                              OpenTelemetry Collector
                                                       ↓
                                              Prometheus + Grafana
```

### Trust API

```bash
cd trust-api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` | OpenTelemetry endpoint |
| `LOG_LEVEL` | `info` | Logging level |
| `API_KEY` | - | Kamailio-to-API auth key |

### Kamailio

```bash
cp kamailio/trust-api.cfg /etc/kamailio/kamailio.cfg
# Configure database and API endpoint
kamailio -f /etc/kamailio/kamailio.cfg
```

### Database

```bash
psql -h localhost -U postgres -d opentrust -f database/schema.sql
```

Migrations use Alembic:
```bash
cd trust-api
alembic upgrade head
```

### Asterisk (Challenge/Voicemail only)

```bash
cp asterisk/ivr-challenge/* /etc/asterisk/
cp asterisk/voicemail-screening/* /etc/asterisk/
asterisk -rx "dialplan reload"
```

## Monitoring

Deploy Grafana with dashboards from `dashboards/grafana/`:

```bash
docker run -d -p 3000:3000 \
  -v $(pwd)/dashboards/grafana:/etc/grafana/provisioning/dashboards \
  grafana/grafana
```

## Scaling

| Component | Strategy |
|---|---|
| Trust API | Horizontal (stateless) |
| PostgreSQL | Read replicas for analytics queries |
| Kamailio | Active/active with shared DB |
| Asterisk | Per-region media pools |

## TLS

All inter-service communication should use TLS. Terminate at the Kamailio edge and use mTLS for API ↔ database connections.
