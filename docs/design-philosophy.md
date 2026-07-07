# Design Philosophy: The Grace-Oriented Trust Engine

Most carrier trust architectures are built on Old Testament logic: strict rules, swift judgment, and stoning the sinner (sending a 603 reject). OpenTrust SIP takes a different approach.

We call it the **Grace-Oriented Trust Engine**.

## The Core Principle

> AI is never the final authority. The carrier controls policy. Every decision must be explainable, observable, and recoverable.

But beyond that: the system should extend grace to the legitimate while maintaining clarity for the illegitimate.

### You Are In Control

Every grace-oriented feature is a configurable default, not a hard-coded mandate. Each pillar has an environment variable the operator can set to `0`, `false`, or an alternative value. The defaults encode a point of view, but the carrier is always the final authority over their own trust engine. The settings are documented in `config.py` and the SpoonFeed `.env` template.

## The Five Pillars

### 1. No Unnecessary Burdens (No "Press 7")

Legitimate callers should not be forced to prove themselves through DTMF mazes or IVR gauntlets. The default challenge mode uses **silence detection** — the call is answered, AMD (Answering Machine Detection) listens for voice activity, and a human who says "Hello?" is passed through with zero friction. Machines reveal themselves through silence or impatience.

> "My yoke is easy, and my burden is light." — Matthew 11:30

**Configurable via**: `CHALLENGE_MODE=silence` (set to `dtmf` for the legacy "Press 7" approach).

### 2. Grace for Repentant Callers (The Prodigal Son Signal)

If a caller has past negative history (was on the DNO list, flagged as fraud, or previously blocked) but this specific call arrives with full STIR/SHAKEN A attestation and is calling a number they have never called before — the system extends grace. Instead of penalizing for past behavior, it adds a positive score bonus.

> "There is more joy in heaven over one sinner who repents than over ninety-nine righteous persons who need no repentance." — Luke 15:7

**Configurable via**: `PRODIGAL_GRACE_BONUS=20` (set to `0` to disable, or adjust the bonus value). Signal weight `WEIGHT_PRODIGAL_GRACE=1.0` (set to `0` to exclude from scoring entirely).

### 3. Radical Forgiveness Through Customer Feedback

When a customer marks a call as "wrongly blocked," the system forgives that caller's past sins. Future calls from that number to that customer receive a strong positive signal. The feedback loop is not just for analytics — it is a mechanism for reputation healing.

> "Father, forgive them, for they know not what they do." — Luke 23:34

**Configurable via**: `FORGIVENESS_BONUS=15` (set to `0` to disable). Signal weight `WEIGHT_FORGIVENESS=1.0` (set to `0` to exclude).

### 4. Public Accountability for Bad Actors

Carriers who refuse to implement STIR/SHAKEN or who consistently originate fraudulent traffic are named transparently in SIP Reason headers. This is not punitive for its own sake — it creates a market incentive for compliance and gives ITSPs the tools to hold upstream carriers accountable.

> "He made a whip of cords and drove them all out of the temple." — John 2:15

**Configurable via**: `SHAME_BAD_CARRIERS=false` (set to `true` to enable public naming in SIP Reason headers).

### 5. Redress as a Personal Invitation

Blocked calls carry a 603+ response with a human-readable contact path — not just a SIP code. Every blocked caller receives an invitation to appeal: a URL, an email address, a real person who will investigate. This turns a dead-end rejection into a recovery path.

> "I am the good shepherd. I know my sheep, and my sheep know me." — John 10:14

**Configurable via**: `REDRESS_CONTACT_URL` and `REDRESS_CONTACT_EMAIL` — set these to your support team's contact info. Leave empty to omit the redress path from SIP responses.

## Operator Override

Every grace-oriented setting can be disabled. An ITSP that wants a strict Old Testament engine sets:

```
PRODIGAL_GRACE_BONUS=0
FORGIVENESS_BONUS=0
CHALLENGE_MODE=dtmf
SHAME_BAD_CARRIERS=false
REDRESS_CONTACT_URL=
REDRESS_CONTACT_EMAIL=
```

The defaults encode a point of view. The carrier is always the final authority.

## The Relationship Score

We track a **Relationship Score** alongside the Risk Score. While the Risk Score answers "How dangerous is this call?", the Relationship Score answers "How healthy is our relationship with this customer?" It is computed as `1.0 - (wrongly_blocked_complaints / total_feedback)` — a customer who frequently reports false positives drives the score down. A declining Relationship Score is an early indicator of churn risk.

## Rollout: Observe Before You Judge

The observe-only phase should last six months, not six days. A single wrongly blocked bank call is a millstone around the ITSP's neck. Let 100 scam calls annoy a customer rather than block one legitimate call from a distressed grandparent.

> "Do not judge, or you too will be judged. For in the same way you judge others, you will be judged." — Matthew 7:1-2

## The Bottom Line

Run your trust engine with **radical mercy for the legitimate** and **radical clarity for the illegitimate**.

Do not rely on rote rules. Rely on knowing the heart of the caller (behavioral intent). Do not hide behind algorithms. Provide a clear path for redemption (redress).

Grace, truth, and a really fast Redis cache for the DNO list.
