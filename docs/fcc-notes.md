# FCC Compliance Notes

## Relevant Regulations

OpenTrust SIP is designed to align with FCC regulations on robocalling, caller ID authentication, and call blocking:

### STIR/SHAKEN (FCC 17-110)
- All originating and transiting SIP providers must sign calls using STIR/SHAKEN
- OpenTrust SIP consumes `stir_shaken` attestation levels (`A`, `B`, `C`) as a scoring signal
- Calls lacking STIR/SHAKEN or with `C` attestation receive elevated scrutiny

### Call Blocking Rules (FCC 20-72)
- Providers must notify customers of blocking
- Customers must have a redress path for erroneously blocked calls
- `BLOCK_DNO` and `BLOCK_ANALYTICS` decisions must log notification and redress tracking

### TRACED Act
- Requires voice service providers to implement STIR/SHAKEN
- Establishes a process for caller ID authentication framework
- OpenTrust SIP's observability layer provides the audit trail required for compliance

## Policy vs Analytics Alignment

FCC rules distinguish between:
- **Customer-directed blocking** (end-user opt-in, DNO lists) — maps to `BLOCK_DNO`
- **Provider analytics blocking** (network-level fraud detection) — maps to `BLOCK_ANALYTICS`

OpenTrust SIP keeps these paths fully separated in decision logic, logging, and redress workflows.

## Required Disclosures per FCC Guidelines

| Requirement | Implementation |
|---|---|
| Blocking notification | `BLOCK_ANALYTICS` triggers notification workflow |
| Redress mechanism | `redress_required` field in decision output |
| Call blocking records | `calls` table with `final_action`, `call_completed`, `duration_seconds` |
| Customer override | `policies` table with customer allowlist overrides |
| Analytics transparency | `decision_events` log every signal and weight per decision |

## State-Level Considerations

Several US states have proposed or enacted additional call blocking transparency requirements. OpenTrust SIP's structured logging of every signal, rule version, and model version provides the evidence base needed for state-level compliance reporting.
