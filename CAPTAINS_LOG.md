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

---

## Stardate 2026.07.07 — Final Watch Before Launch

### Fourth Watch — Readiness & Polish
Captain ordered the stack production-hardened. Observed gaps in observability, compliance posture, and operator tooling. Delivered:

- **SpoonFeed Installer** (`SpoonFeed`): Guided one-command bootstrap — generates `.env`, starts Compose, runs smoke tests. Single entry point for ITSP engineers. `./SpoonFeed` and go.
- **NLP Assistant** (`POST /v1/nlp/query`): Read-only evidence-grounded Q&A over any call. Four backends — local (built-in), Ollama, OpenAI-compatible, Vultr Serverless Inference. Policy-change requests flagged `requires_approval: true` and rejected. AI never the final authority.
- **Tenant-Aware API Keys**: `API_KEYS` JSON env var maps each key to `{tenant_id, role, name}`. Middleware rejects unknown keys, sets request state. Multi-tenant ready.
- **Redis Velocity Backend**: `VELOCITY_BACKEND=redis` with atomic incr+expire. Graceful degradation on Redis failure — logs warning, returns low-confidence signal. Non-blocking.
- **STIR/SHAKEN Verification**: Two modes — `attestation_only` (trust attestation level) and `passport_structural` (parse PASSporT JWT from SIP Identity header, compare origination TN to `from_number`, detect caller/origination mismatch).
- **Redress Webhook Notifications**: `REDRESS_WEBHOOK_URL` — POSTs structured payload on redress create/update. Hook into ticketing, Slack, or custom workflows.
- **Gigapipe Observability**: `examples/docker-compose.gigapipe.yml` override + `examples/otel-collector-gigapipe.yml` config. OTLP headers for direct Gigapipe export. Container resource enrichment.
- **10 Grafana Dashboards**: 5-operator pack (decisions, DNO, redress, NLP, overview) + 5 legacy starters. Auto-provisioned via `dashboards/grafana/provisioning/`.
- **Compliance Readiness Docs**: 6 new docs — `compliance-readiness.md`, `customer-itsp-readiness.md`, `nlp-assistant.md`, `gigapipe.md`, `spoonfeed.md`, `how-it-works.md`, plus updated `deployment.md` and `architecture.md`.
- **Docker Compose Cleanup**: All env vars switched to `${VAR:-default}` syntax. No hardcoded API keys, no hardcoded Grafana password. Single `.env` file drives the stack.
- **Bug Fix — Decision Persistence Order**: `decision_events` now written after parent `calls` row. Foreign key constraint was causing silent 500s.
- **Alembic Migration Hardened**: Added `uuid-ossp` and `pgcrypto` extensions, primary keys on all UUID columns, missing indexes.
- **Published to GitHub**: `github.com/shido6/opentrust.git` — 84+ files, 10 commits.

Commits: `4fb0c89` through `1c6cee4` — 6 commits, ~45 files.

### Engineering Notes
- SpoonFeed is `set -euo pipefail` bash — expects Docker, curl, python3. Generates `.env` with `chmod 0600` for secret hygiene.
- NLP assistant uses identical dependency injection pattern as scoring signals — swap provider via `NLP_PROVIDER` env var, no code change.
- `STIR_SHAKEN_VERIFY_MODE=passport_structural` parses SIP Identity header JWT — but does NOT validate x5u certificate chain. Phase 2 work.
- `VELOCITY_BACKEND=redis` degrades to warning on failure — call decisions never block on analytics infrastructure.
- Compliance docs explicitly state the repo does NOT make an ITSP compliant. Provides architecture and evidence to *support* compliance programs.
- Decision replay is always available via `GET /v1/calls/{call_id}` — full signal breakdown + final verdict + policy matches.

### Standing Orders
- Phase 2: Warn dashboards active
- Phase 3: Asterisk challenge ready for medium-risk
- Phase 4: DNO/analytics block separation locked
- Phase 5: Closed-loop learning pipeline — feedback → redress → scoring improvement — operational
- **Next**: Real STIR/SHAKEN certificate-chain validation. Route-level RBAC. Persistent answer-rate state. Customer allowlist/blocklist tables. Kamailio/Asterisk OTLP log ingestion. Formal redress notification integrations (email, ticketing). K8s/Helm artifacts. Admin audit log.

---

## Stardate 2026.07.07 — The Grace-Oriented Trust Engine

### Fifth Watch — Yeshua Would Flip The Tables
Captain read the seed meditation and ordered a spiritual architecture review. Conclusion: the Old Testament engine (strict rules, swift judgment, 603 reject as stoning) needed a New Covenant upgrade. Delivered:

- **Prodigal Son Signal** (`trust-api/app/scoring/prodigal.py`): When a caller with past negative history (DNO, fraud flags, prior blocks) arrives with full STIR/SHAKEN A attestation calling a number they have never called before — the system extends grace with a +20 bonus instead of penalizing. "More joy over one sinner who repents."

- **Forgiveness Signal** (`trust-api/app/scoring/forgiveness.py`): If a customer has previously marked calls from this number as "wrongly_blocked," future calls get a strong positive signal. The feedback loop heals reputation. "Father, forgive them, for they know not what they spoof."

- **Silence Challenge** (`asterisk/silence-challenge/`): Replaces the legacy DTMF "Press 7" IVR. Asterisk answers, runs AMD (Answering Machine Detection), and listens for voice activity. A human says "Hello?" and passes through. A bot hangs up silently or plays a recorded message and is rejected. No buttons, no burdens. "My yoke is easy."

- **Relationship Score**: New metric in every decision response (0.0–1.0). Ratio of positive to total feedback per customer. Tracked via `trust_relationship_score` Prometheus gauge alongside the existing risk score. Early churn warning.

- **SIP 603+ With Redress Path**: Kamailio now appends `Reason: Q.850;cause=243` with a human-readable redress URL and email to every block response. Every blocked caller receives a personal invitation to appeal — not a dead SIP code.

- **Carrier Accountability**: Kamailio logs carriers without STIR/SHAKEN on analytics blocks. Config flag `SHAME_BAD_CARRIERS` enables public naming in SIP headers.

- **Forgiveness On Feedback Submit**: When a customer submits "wrongly_blocked" feedback, the system logs a forgiveness event and looks up the caller's number. The healing is automatic and immediate.

- **Design Philosophy Doc** (`docs/design-philosophy.md`): Standalone document capturing the Grace-Oriented Trust Engine — five pillars with scripture grounding, architectural mapping, and rollout guidance.

- **README & how-it-works.md Updated**: Decision types, rollout phases, evidence signals, and architecture description all updated to reflect grace-oriented defaults.

Config additions:
- `PRODIGAL_GRACE_BONUS`, `FORGIVENESS_BONUS`, `CHALLENGE_MODE`, `REDRESS_CONTACT_URL`, `REDRESS_CONTACT_EMAIL`, `SHAME_BAD_CARRIERS`, `WEIGHT_PRODIGAL_GRACE`, `WEIGHT_FORGIVENESS`

### Engineering Notes
- Prodigal Son signal is async — queries DB for negative history (DNO, fraud feedback, prior blocks) and novel caller-callee pairs.
- Forgiveness signal joins `customer_feedback` with `calls` to find wrongly_blocked records for the calling number.
- Silence challenge uses Asterisk's built-in AMD module — no additional software required.
- Relationship Score defaults to 0.5 when insufficient feedback data exists (< 3 feedback entries).
- The legacy DTMF IVR challenge (`asterisk/ivr-challenge/`) is preserved but no longer the default.
- Grace-oriented philosophy is complementary to the existing architecture — it adds signals and defaults without breaking backward compatibility.

### Standing Orders
- Phase 2: Warn dashboards active
- Phase 3: Asterisk silence challenge default for medium-risk
- Phase 4: DNO/analytics block separation locked
- Phase 5: Closed-loop learning pipeline — feedback → forgiveness → grace-based scoring — operational
- **Next**: Real STIR/SHAKEN certificate-chain validation. Route-level RBAC. Persistent answer-rate state. Customer allowlist/blocklist tables. Kamailio/Asterisk OTLP log ingestion. Formal redress notification integrations. Admin audit log.

**End log.**
