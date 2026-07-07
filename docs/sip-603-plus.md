# SIP 603+ Response Reference

## Overview

When OpenTrust SIP decides to block a call, Kamailio responds with an appropriate SIP final response. The choice of response code matters for transparency, debugging, and interop with downstream carriers.

## Response Code Mapping

| Decision | SIP Response | Meaning |
|---|---|---|
| `BLOCK_DNO` | `403 Forbidden` | Deterministic policy block |
| `BLOCK_ANALYTICS` | `603 Decline` | Analytics-based rejection |
| `RATE_LIMIT` | `503 Service Unavailable` | Temporary throttling |
| `CHALLENGE` | `302 Moved Temporarily` | Redirect to Asterisk |
| `VOICEMAIL` | `302 Moved Temporarily` | Redirect to Asterisk voicemail |
| `WARN` | `183 Session Progress` | Warning header + route |

## Why Not 608/607+

While the IETF has proposed `608 Rejected` and `607 Not Allowed` for richer blocking semantics, most carriers and SBCs do not yet handle them reliably. OpenTrust SIP currently uses:

- **403 Forbidden** — DNO blocks (clear, unambiguous)
- **603 Decline** — Analytics blocks (standard for "don't want this call")
- **503 Service Unavailable** — Rate limiting (also triggers retry logic)

As carrier adoption of 608/607 increases, OpenTrust SIP will add a configuration option to use them.

## Warning Header

For `WARN` decisions, Kamailio adds a SIP `Warning` header:

```sip
Warning: 399 opentrust "Low trust score (45/100) — verify caller"
```

## Kamailio Response Config

```kamailio
# trust-api.cfg decision mapping
route[TRUST_RESPONSE] {
    switch ($var(decision)) {
        case "allow":
            t_relay();
            break;
        case "warn":
            append_to_reply("Warning: 399 opentrust \"$var(warning_message)\"");
            t_relay();
            break;
        case "block_dno":
            sl_send_reply(403, "Forbidden");
            break;
        case "block_analytics":
            sl_send_reply(603, "Decline");
            break;
        case "rate_limit":
            sl_send_reply(503, "Service Unavailable");
            break;
        case "challenge":
            # redirect to Asterisk IVR
            append_to_reply("Contact: <sip:ivr@asterisk.internal:5060>");
            sl_send_reply(302, "Moved Temporarily");
            break;
        case "voicemail":
            append_to_reply("Contact: <sip:vm@asterisk.internal:5060>");
            sl_send_reply(302, "Moved Temporarily");
            break;
    }
}
```

## Best Practices

1. Always log the SIP response code alongside the decision
2. Use `Reason` header for machine-readable blocking context
3. Never silently drop calls — always send a final response
4. For analytics blocks, ensure the 603 includes enough context for downstream redress
