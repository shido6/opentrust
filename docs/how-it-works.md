# How OpenTrust SIP Works

OpenTrust SIP is an open carrier trust platform for ITSPs, CLECs, SIP operators, and enterprise voice providers.

Its job is not to let AI block calls. Its job is to help carriers make better, explainable, observable, and recoverable call-handling decisions.

The core idea is simple:

```text
Policy + Evidence + Analytics + Observability + Redress
```

## The Problem

Carriers are under pressure from both sides.

Customers want fewer spam and fraud calls. Regulators expect reasonable call-blocking practices, transparency, and redress. At the same time, legitimate callers must not be silently blocked by opaque scoring systems.

The old model is brittle:

- Block more calls and risk false positives.
- Let more calls through and risk fraud complaints.
- Use black-box analytics and lose customer trust.
- Block without evidence and create regulatory exposure.

OpenTrust SIP gives the carrier a middle path: every decision is explainable, logged, replayable, and tied to customer outcomes.

## The Short Version

When a call arrives, Kamailio asks the Trust API what to do.

The Trust API evaluates deterministic policy first, then analytics signals. It returns a decision such as `ALLOW`, `WARN`, `CHALLENGE`, `VOICEMAIL`, `RATE_LIMIT`, `BLOCK_DNO`, or `BLOCK_ANALYTICS`.

Kamailio enforces the decision. Asterisk is used only when media interaction is needed, such as an IVR challenge or voicemail screening.

Every decision is recorded with reason codes and signal evidence so the ITSP can later answer: "Why did this happen?"

## Call Flow

```text
Caller
  ↓
Carrier / Interconnect
  ↓
Kamailio
  ↓
Trust Engine API
  ↓
Decision + evidence
  ↓
Kamailio enforcement
  ↓
Customer, Asterisk challenge, voicemail, rate limit, or block response
```

## What Each Component Does

### Kamailio

Kamailio is the SIP policy enforcement point.

It receives the SIP `INVITE`, extracts metadata, calls the Trust API, then routes or rejects the call based on the returned decision.

Kamailio should remain fast and predictable. It should not become the analytics engine.

### Trust API

The Trust API is the decision layer.

It receives call metadata such as:

- SIP Call-ID
- From number
- To number
- Source IP
- Source carrier
- STIR/SHAKEN attestation or Identity header
- User-Agent
- Timestamp

It evaluates policy and signals, stores the evidence, and returns a decision.

### PostgreSQL

PostgreSQL is the durable system of record.

It stores:

- Calls
- Decision events
- DNO entries
- Customer policies
- Feedback
- Redress requests

If a customer or regulator asks why something happened, PostgreSQL contains the replayable evidence.

### Asterisk

Asterisk is only used when media is needed.

Examples:

- IVR challenge
- Voicemail screening
- Announcements
- Call recording, if explicitly enabled

This keeps SIP routing and media interaction separate.

### Gigapipe

Gigapipe is the recommended production observability layer.

It gives the ITSP traces, metrics, logs, and customer-impact timelines across Kamailio, the Trust API, Asterisk, and supporting infrastructure.

Grafana dashboards are also included for local development, NOC screens, and self-hosted Prometheus deployments.

### NLP Assistant

The NLP assistant lets operators ask questions like:

- "Why was this call blocked?"
- "Was this DNO or analytics?"
- "What evidence contributed to this score?"
- "Does this need redress?"

The assistant is read-only. It explains from stored evidence. It does not silently change policies, DNO entries, thresholds, or redress state.

Operators can use local deterministic mode, Ollama, OpenAI-compatible APIs, or Vultr Serverless Inference.

## Policy Comes Before Analytics

This is the most important design rule.

OpenTrust SIP separates deterministic policy from probabilistic analytics.

| Category | Meaning | Example | Enforcement |
|---|---|---|---|
| Policy | Deterministic rule | DNO number, customer blocklist | Direct enforcement |
| Analytics | Risk-based signal | Velocity anomaly, low reputation | Recommendation with evidence |

Why this matters:

- DNO is a clear policy decision.
- Fraud scoring is probabilistic.
- Customers need to know which one affected them.
- Regulators and support teams need a clean audit trail.

`BLOCK_DNO` and `BLOCK_ANALYTICS` are intentionally separate decisions.

## Decision Types

| Decision | What Happens | Why It Helps |
|---|---|---|
| `ALLOW` | Route normally | Legitimate calls complete without friction |
| `WARN` | Route with warning metadata | Customer gets context without losing the call |
| `CHALLENGE` | Send to Asterisk IVR | Suspicious calls get friction before blocking |
| `VOICEMAIL` | Send to voicemail screening | Customer avoids interruption but can recover legitimate calls |
| `RATE_LIMIT` | Throttle source or campaign | Reduces abuse without permanent blocking |
| `BLOCK_DNO` | Deterministic policy block | Stops numbers that should not originate calls |
| `BLOCK_ANALYTICS` | Analytics block with redress context | High-risk calls are stopped with evidence and recovery path |

## Evidence Signals

OpenTrust SIP evaluates multiple signals:

- DNO lookup
- Customer policy
- STIR/SHAKEN attestation or PASSporT structure
- Source IP reputation
- Source carrier reputation
- Call velocity
- Historical answer-rate signal
- User-Agent heuristics
- Customer feedback
- Redress outcomes

Each signal can produce a reason code. Reason codes are stored in `decision_events` and are returned in API responses.

## Observability And Replay

Every decision should be answerable after the fact.

For each call, the ITSP can inspect:

- Call metadata
- Final decision
- Trust score
- Confidence
- Reason codes
- Signal weights
- Redress status
- Customer feedback
- Call completion outcome

This allows customer support, engineering, compliance, and leadership to work from the same evidence.

## Redress And Recovery

Mistakes will happen. The platform is designed around recovery.

If a legitimate call is blocked or challenged incorrectly, the customer should have a redress path. OpenTrust SIP stores redress requests and can notify external systems through webhooks.

That means an ITSP can connect OpenTrust SIP to:

- Ticketing systems
- Customer portals
- Support workflows
- Compliance reporting

The goal is not "zero mistakes." The goal is explainable decisions and fast recovery.

## How The ITSP Wins

The ITSP wins because OpenTrust SIP improves trust without turning call blocking into a black box.

Benefits:

- Better fraud prevention
- Fewer unsupported customer complaints
- Faster root-cause analysis
- Clear separation of policy and analytics
- Better regulatory posture
- Customer-visible redress path
- Observable call outcomes
- Configurable rollout from observe-only to enforcement
- Open-source reference architecture instead of vendor lock-in

Operationally, the ITSP gets a defensible workflow:

1. Observe calls and collect evidence.
2. Warn customers and operators.
3. Challenge suspicious calls.
4. Block deterministic DNO cases.
5. Use feedback and redress to improve decisions.

## How The Customer Wins

The customer wins because call handling becomes transparent and recoverable.

Benefits:

- Fewer spam and fraud calls
- Fewer silent false positives
- Legitimate calls have recovery paths
- Blocking is explainable
- Customer policies can be respected
- Disputes can be investigated with evidence
- Medium-risk calls can be challenged instead of blindly blocked

The customer does not need to understand SIP, STIR/SHAKEN, or scoring models. They need clear answers:

- Was my call allowed, warned, challenged, sent to voicemail, or blocked?
- Why?
- Was it policy or analytics?
- Can it be fixed?
- How do we prevent it next time?

OpenTrust SIP is built to answer those questions.

## How Regulators And Auditors Win

Regulators and auditors need evidence, not vague claims.

OpenTrust SIP supports:

- Decision logs
- Reason codes
- DNO/analytics separation
- Redress tracking
- Observability exports
- Compliance readiness documentation
- Deployment runbooks
- Clear control boundaries

The system does not claim compliance by default. It gives operators the evidence and architecture needed to support compliance programs such as SOC 2, HIPAA-adjacent deployments, FCC call-blocking obligations, CPNI, and privacy requirements.

## Why Open Source Matters

Carrier trust should not depend entirely on opaque proprietary scoring.

OpenTrust SIP is open so ITSPs can inspect, adapt, deploy, and improve the architecture.

The intelligence belongs to the operator and the community.

## The North Star

Do not optimize for "calls blocked."

Optimize for trusted call completion.

The best system is not the one that blocks the most calls. It is the one that helps legitimate calls complete, stops obvious abuse, adds friction when uncertainty is high, and explains every decision after the fact.

That is the OpenTrust SIP model:

```text
Better Signals. Better Decisions. Better Outcomes.
```
