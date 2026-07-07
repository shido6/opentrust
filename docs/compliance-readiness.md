# Compliance Readiness

OpenTrust SIP is a reference implementation. It can support regulated operations, but deploying this repository does not by itself make an ITSP SOC 2, HIPAA, FCC, CPNI, or privacy compliant.

The goal is to make compliance evidence easy to produce: every call decision should be attributable, explainable, access-controlled, retained according to policy, and recoverable during audit or customer dispute.

## Common-Sense Compliance Model

| Concern | What OpenTrust SIP Should Provide | Operator Responsibility |
|---|---|---|
| SOC 2 Security | Auth, audit trails, least privilege, vulnerability management hooks | Formal controls, access reviews, vendor risk, change management |
| SOC 2 Availability | Health checks, telemetry, fail-open SIP behavior, alerting | SLOs, incident response, backups, DR testing |
| SOC 2 Confidentiality | Minimal sensitive data capture, protected secrets, scoped access | Encryption policy, key management, data classification |
| HIPAA-adjacent use | Avoid unnecessary PHI, protect call metadata, audit access | Determine if call metadata is PHI, sign BAAs where required |
| FCC call blocking | Decision logs, redress records, DNO/analytics separation | Customer notices, redress SLA, regulatory reporting |
| CPNI / telecom privacy | Customer-scoped policies and call records | Customer authentication, staff training, disclosure controls |
| Privacy laws | Data minimization and retention hooks | DPA, retention schedule, deletion/export process |

## SOC 2 Readiness Controls

### Security

Required before production:

- Replace global API key auth with tenant-scoped tokens or mTLS.
- Store API keys, Gigapipe credentials, and NLP provider credentials in a secret manager.
- Enforce role-based access for DNO, policy, feedback, redress, NLP, and call-audit APIs.
- Log all administrative actions with actor, timestamp, object, before/after values, and source IP.
- Run dependency scanning and container image scanning in CI.
- Require code review and signed releases for production deployments.

Current repo support:

- API key middleware exists as a development baseline.
- Structured logs, OpenTelemetry traces, and database decision events provide audit evidence.
- GitHub Actions provides lint/test/build hooks.

### Availability

Required before production:

- Define SLOs for decision latency and Trust API uptime.
- Use multiple Trust API replicas behind a load balancer.
- Move process-local velocity and answer-rate state to Redis or PostgreSQL.
- Backup PostgreSQL and test restore procedures.
- Configure alert routing and incident ownership.

Current repo support:

- Kamailio config fails open if the Trust API is unavailable.
- Health checks and Prometheus alert rules are present.
- Gigapipe collector profile supports centralized telemetry.

### Confidentiality

Required before production:

- Classify call metadata as sensitive customer data.
- Encrypt database storage and backups.
- Use TLS/mTLS between Kamailio, Trust API, database, collector, Gigapipe, and NLP providers.
- Redact numbers where possible in logs and NLP prompts, or retain full numbers only in controlled audit stores.
- Define retention periods for call records, decision events, feedback, redress records, prompts, and responses.

Current repo support:

- Decision evidence is structured and can be routed to controlled observability systems.
- No payload encryption, token-scoped RBAC, or redaction layer is implemented yet.

## HIPAA / PHI Guidance

OpenTrust SIP should assume call metadata may become PHI when used by healthcare customers or when caller/callee identity reveals care relationships.

Required safeguards for HIPAA-regulated deployments:

- Execute BAAs with hosting, observability, ticketing, support, and NLP vendors where PHI may be processed.
- Prefer `NLP_PROVIDER=local` for regulated healthcare deployments unless external vendor terms are approved.
- Minimize PHI in logs, telemetry, and NLP prompts.
- Restrict call-audit and NLP access by role and customer.
- Record access to call records and redress records.
- Encrypt data at rest and in transit.
- Define breach notification and incident escalation procedures.

OpenTrust SIP should not store call audio by default. If Asterisk challenge recordings or voicemails are enabled, they require a separate PHI/PII storage and retention model.

## FCC, Redress, and Call Blocking

The repo intentionally separates deterministic policy blocks from analytics-based blocks:

- `BLOCK_DNO` is deterministic policy.
- `BLOCK_ANALYTICS` is probabilistic and should trigger notification/redress handling.

Before production, ITSPs should add:

- Customer-visible notices for analytics blocking.
- A public or customer-portal redress intake path.
- SLA metrics for redress response and resolution.
- Reporting for false-positive rate, override rate, and unresolved complaints.

## Gigapipe And NLP Evidence Use

Recommended evidence split:

- PostgreSQL: durable call decisions, policies, DNO, feedback, redress.
- Gigapipe: traces, logs, metrics, incident investigation, customer-impact timelines.
- Ticketing system: customer communications and redress workflow artifacts.
- NLP provider: optional read-only summarization from already-authorized evidence.

Do not send secrets, auth headers, full voicemail content, or unnecessary PHI to Gigapipe or external NLP providers.

## Investor / Enterprise Buyer Checklist

- Architecture diagram and data-flow diagram.
- Data inventory and retention policy.
- Access control matrix.
- Incident response plan.
- Vulnerability management process.
- Change management process.
- Backup and restore evidence.
- Vendor list with data processed and contract status.
- Audit log samples showing call decision replay.
- Redress workflow evidence.

## Current Gaps To Close

- Tenant-scoped auth/RBAC.
- Admin action audit log table.
- Secret-manager examples.
- Data retention jobs.
- PII/PHI redaction controls.
- mTLS deployment examples.
- Dependency/container security scanning in CI.
- Formal redress notification integrations.
