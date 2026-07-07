# OpenTrust SIP — Agent Seed Brief

## Mission
Build an open-source Carrier Trust Engine for ITSPs, CLECs, SIP operators, and enterprise voice providers.
The goal is to make call-blocking and fraud-prevention decisions explainable, observable, auditable, and recoverable.
This is not "AI blocks calls."
This is:
Policy + Evidence + Analytics + Observability + Customer Feedback.

## Core Principle
Never make AI the final authority.
The engine recommends.
The carrier controls policy.
Every decision must be explainable and replayable.

## Architecture
Kamailio is the SIP policy enforcement point.
Asterisk is used only when media interaction is needed.

```
INVITE
  ↓
Kamailio
  ↓
Trust Engine API
  ↓
Decision
  ↓
ALLOW / WARN / CHALLENGE / VOICEMAIL / BLOCK
  ↓
Asterisk only if media is required
```

### Required Modules

1. **Trust API** — Accepts per-call metadata and returns a decision.
2. **Kamailio** — SIP proxy; queries Trust API per INVITE.
3. **Asterisk** — IVR challenge / voicemail screening flows.
4. **Database** — PostgreSQL with calls, decision_events, customer_feedback, dno_entries, policies tables.
5. **Observability** — OpenTelemetry + structured logging for every decision.
6. **Dashboards** — Grafana for real-time trust metrics.

## Decision Types

- `ALLOW` — Route normally.
- `WARN` — Route but add customer-visible warning or metadata.
- `CHALLENGE` — Send to Asterisk IVR or screening flow.
- `VOICEMAIL` — Send to voicemail/screening.
- `RATE_LIMIT` — Throttle source or campaign.
- `BLOCK_DNO` — Deterministic policy block.
- `BLOCK_ANALYTICS` — Analytics-based block requiring proper notification handling.

## Policy vs Analytics

DNO is policy. Fraud scoring is analytics. Do not mix them.

- DNO Match = deterministic policy
- High Risk Score = probabilistic analytics

## Data Sources

- SIP metadata
- STIR/SHAKEN result
- DNO provider or local DNO table
- Customer allowlist / blocklist
- Call velocity
- Source IP reputation
- Source carrier reputation
- Historical answer rate
- Customer feedback
- Support ticket outcomes
- Redress requests

## Observability Requirements

Every decision must be logged. Store:

SIP Call-ID, timestamp, source/destination, decision, trust score, reason codes, rule version, model version, DNO result, STIR/SHAKEN result, action taken, call outcome, customer feedback, support ticket reference, redress outcome.

## Success Metrics

Optimize for trusted call completion. Track:

- Trusted Call Completion Rate
- False-positive rate / False-negative rate
- Customer override rate
- Redress resolution time
- Support tickets caused by blocking
- Customer churn after intervention
- Fraudulent calls reaching customers
- Legitimate calls completed without unnecessary friction

## Rollout Plan

1. **Observe only** — Score calls but do not enforce.
2. **Warn only** — Add warnings, dashboards, and reporting.
3. **Challenge** — Use Asterisk for medium-risk calls.
4. **Block obvious cases** — Separate DNO blocks from analytics blocks.
5. **Closed-loop learning** — Use feedback and redress outcomes to improve scoring.

## Positioning

OpenTrust SIP is an open-source reference architecture for transparent carrier call trust.

Built on Kamailio. Enhanced by Asterisk. Observed by OpenTelemetry. Explained by evidence.
