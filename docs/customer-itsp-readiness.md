# Customer-to-ITSP Readiness Map

## Work Backwards From The Customer

The customer does not care which model, carrier feed, or SIP module made a decision. They care about outcomes:

| Customer Question | Required OpenTrust Evidence | ITSP Operational Need |
|---|---|---|
| Why was my call blocked? | `call_id`, decision, trust score, reason codes | Fast call lookup and explainable audit trail |
| Was this my policy or carrier analytics? | Decision type and source signal | Separation of `BLOCK_DNO` and `BLOCK_ANALYTICS` |
| Can I override it? | Customer policy and allowlist records | Scoped policy management with tenant isolation |
| How do I get this fixed? | Feedback and redress records | Redress workflow, SLA tracking, ticket/webhook integration |
| Did the carrier system fail? | Kamailio, Asterisk, Trust API traces linked by `call_id` | Gigapipe correlation across SIP, API, and media systems |
| Can I talk to the system? | NLP answers grounded in audit evidence | Safe read-only assistant with approval-gated changes |

## Meet In The Middle From The ITSP

The ITSP needs controls that preserve customer trust without creating network risk:

1. Deterministic policy must be auditable and reversible.
2. Analytics must recommend with confidence and reason codes.
3. Enforcement must fail safely when dependencies are unavailable.
4. Every decision must be replayable from stored evidence.
5. Observability must answer customer-impact questions before internal component questions.
6. NLP must explain and summarize; it must not silently change enforcement.

## Current Repo Status

Implemented:

- DB-backed call and decision event storage
- DNO and policy decision paths
- Feedback and redress APIs
- CDR update hook
- API key enforcement
- Prometheus metrics and OpenTelemetry tracing
- Gigapipe collector profile and direct OTLP header support
- Read-only NLP assistant with local, Ollama, OpenAI-compatible, and Vultr provider options
- Tenant-aware API keys, Redis-backed velocity option, STIR/SHAKEN PASSporT structural parsing, and redress webhooks

Still required before broad ITSP production use:

- Certificate-chain/TNAuthList STIR/SHAKEN validation and persistent answer-rate state
- Full route-level RBAC beyond tenant-aware API keys
- Customer allowlist/blocklist tables and APIs
- Kamailio/Asterisk log ingestion with `call_id` enrichment into Gigapipe
- Asterisk challenge flow that bridges successful callers to the intended destination
- Compliance readiness controls for SOC 2, HIPAA-adjacent deployments, CPNI, privacy, and investor diligence
