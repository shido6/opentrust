# Captain's Log

## Stardate 2026.07.06 — OpenTrust SIP Commissioned

### First Watch
Seed brief acquired. Architecture green-lit. Repo skeleton laid in at `opentrust-sip/`. Mission: build a transparent carrier trust engine that makes call-blocking explainable, observable, and recoverable. No AI-as-authority. Policy + Evidence + Analytics.

### Second Watch
Trust API stub online. FastAPI accepting call metadata, returning decisions. PostgreSQL schema drafted — `calls`, `decision_events`, `customer_feedback`, `dno_entries`, `policies`, `redress_requests`. Kamailio config wired for API lookup. Asterisk IVR challenge + voicemail screening dialplans written. Grafana dashboards provisioned. Docker Compose standing by.

Commit: `d8ec780` — 39 files, 1370 lines.

### Third Watch — Production Push
Captain reviewed readiness gaps. Found 16 deficiencies. Ordered full remediation:

- **Scoring Engine v2**: Signal registry architecture. Six signals live — STIR/SHAKEN, IP reputation, carrier reputation, call velocity, answer rate, DNO lookup. Configurable weights via env vars. Customers can tune without redeploying.
- **DNO Engine**: DB-backed lookup + full CRUD API. Hard deterministic blocks bypassing analytics entirely.
- **Policy Engine**: Customer-specific rule evaluation — block numbers, block prefixes, allow overrides, STIR/SHAKEN minimum floors. Schema: JSON policy documents evaluated at decision time.
- **API Surface**: Seven endpoints now. Decision, CDR webhook, DNO management, policy CRUD, feedback ingestion, redress workflow, call audit trail.
- **Auth**: API key middleware on all routes. `/health` and `/metrics` open for monitoring.
- **Observability**: OpenTelemetry tracing wired. Prometheus `/metrics` exporting 7 metric families. Structured JSON logging across all services.
- **Operations**: GitHub Actions CI (lint + test + build). Alembic migrations. 6 Prometheus alerting rules. Fail-open Kamailio config with jansson JSON parsing.

Commit: `8a07879` — 43 files changed, 1809 insertions.

### Engineering Notes
- Signal weights live in env vars prefixed `WEIGHT_` — ITSPs tune without touching code
- Velocity tracker uses in-memory sliding window; swap for Redis when scaling past single instance
- Answer rate tracker records per-carrier; sufficient for Phase 1 closed-loop
- DNO entry CRUD returns 404 on delete miss — standard REST, Kamailio can treat 404 as "already deleted"
- Kamailio fails open on API timeout (2s default) — carrier ops never block due to analytics outage
- No AI final authority. Ever.

### Standing Orders
- Phase 2: Warn dashboards active
- Phase 3: Asterisk challenge ready for medium-risk
- Phase 4: DNO/analytics block separation locked
- Phase 5: Closed-loop learning pipeline — feedback → redress → scoring improvement — operational

**End log.**
