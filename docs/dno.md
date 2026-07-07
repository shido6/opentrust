# Do Not Originate (DNO) Reference

## Overview

DNO (Do Not Originate) is a deterministic policy mechanism to block calls that should never originate from a given number. Unlike analytics-based blocking, DNO is immediate, non-probabilistic, and requires no scoring.

## When to Use DNO

- Numbers that will never originate calls (e.g., government helplines, bank customer service lines)
- Numbers ported to your network that should not be calling out
- Numbers flagged by industry DNO feeds or consortiums
- Numbers explicitly listed by customers as "never call from us"

## DNO Data Sources

| Source | Description | Freshness |
|---|---|---|
| Internal DNO table | Manually curated numbers | As needed |
| DNO provider feed | Third-party DNO data service | Daily/weekly |
| Industry consortium | Trade group DNO lists | Varies |
| Customer-submitted | Customer self-declares DNO numbers | Real-time via portal |

## DNO Entry Schema

```json
{
  "number": "+15551234567",
  "source": "internal",
  "reason": "Bank customer service line — never originates calls",
  "created_at": "2026-07-06T12:00:00Z",
  "expires_at": "2027-07-06T12:00:00Z"
}
```

## DNO vs Analytics Blocking

| Aspect | DNO | Analytics |
|---|---|---|
| Nature | Deterministic | Probabilistic |
| Block reason | Number should never originate | Call pattern looks fraudulent |
| Customer notification | Not always required | Required (FCC 20-72) |
| Redress path | Expedited | Standard |
| Override | Policy exception only | Score threshold adjustment |

## DNO in Kamailio

Kamailio checks DNO via the Trust API before any analytics evaluation. If a DNO match is found, the API returns `BLOCK_DNO` immediately, bypassing the scoring engine entirely.

## DNO Configuration

```sql
-- Add a DNO entry
INSERT INTO dno_entries (number, source, reason, created_at, expires_at)
VALUES ('+15551234567', 'internal', 'Bank customer service line', NOW(), NOW() + INTERVAL '1 year');

-- Query active DNO entries
SELECT * FROM dno_entries WHERE expires_at > NOW();
```
