# NLP Operations Assistant

OpenTrust SIP includes a read-only NLP layer so ITSP operators can talk to the system without giving the model authority over call blocking.

The assistant answers from stored audit evidence first. It can explain calls, summarize decision events, and identify whether a request would require an approval workflow. It does not change policies, DNO entries, thresholds, redress status, or customer configuration.

## Endpoint

```http
POST /v1/nlp/query
X-API-Key: <api-key>
Content-Type: application/json

{
  "query": "Why was call abc123 blocked?",
  "call_id": "abc123"
}
```

Response:

```json
{
  "answer": "Call abc123 received decision 'block_analytics'...",
  "intent": "explain_call_decision",
  "confidence": 0.82,
  "provider": "local",
  "requires_approval": false,
  "evidence": []
}
```

## Provider Options

The default provider is `local`, which uses deterministic templates and never sends data to a third party.

```bash
export NLP_PROVIDER=local
```

### Ollama

For local inference:

```bash
export NLP_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export NLP_MODEL=llama3.1
```

### OpenAI / ChatGPT-Compatible API

For OpenAI or compatible chat-completions APIs:

```bash
export NLP_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
export NLP_MODEL=gpt-4o-mini
```

### Vultr Serverless Inference

For Vultr Serverless Inference or a Vultr-hosted OpenAI-compatible endpoint:

```bash
export NLP_PROVIDER=vultr
export VULTR_API_KEY=...
export VULTR_INFERENCE_URL=https://YOUR-VULTR-INFERENCE-ENDPOINT/v1/chat/completions
export NLP_MODEL=llama-3.1-8b-instruct
```

## Safety Rules

- The model receives only the user query, deterministic answer, and audit evidence for the requested call.
- The assistant must not invent facts outside the supplied evidence.
- Requests to change policy, DNO, thresholds, or redress state return `requires_approval: true`.
- Use `local` mode for HIPAA-sensitive or privacy-sensitive deployments unless vendor contracts and BAAs are in place.
- Do not export voicemail content, secrets, API keys, or unnecessary PHI/PII to external providers.

## Customer-Backwards Use Cases

- "Why was call abc123 blocked?"
- "Was this DNO or analytics?"
- "What evidence contributed to the score?"
- "Does this need redress?"
- "Prepare a policy change proposal for this customer" (approval required)

## ITSP Controls To Add Before Production

- Tenant-scoped auth for NLP queries.
- Audit log of every prompt, actor, evidence IDs used, provider, and response.
- Per-customer provider policy: local-only, approved external provider, or disabled.
- Redaction controls for phone numbers and customer identifiers.
- Approval workflow for policy/DNO/redress changes proposed by NLP.
