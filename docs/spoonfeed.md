# SpoonFeed Installer

`SpoonFeed` is the guided bootstrap installer for OpenTrust SIP.

It is designed for engineers who have just cloned the repository and want a working local stack without manually stitching together Compose commands, environment variables, and smoke tests.

## What It Does

SpoonFeed performs these steps:

1. Checks required commands: Docker, Docker Compose, curl, Python 3.
2. Generates a local `.env` file.
3. Starts the Docker Compose stack.
4. Optionally enables the Gigapipe collector override.
5. Configures the NLP assistant provider.
6. Waits for the Trust API health endpoint.
7. Runs smoke tests for decisioning, audit replay, NLP, and metrics.

## Quick Start

```bash
./SpoonFeed
```

This starts the default development stack:

- Trust API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Metrics: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Development credentials:

- `X-API-Key: dev-api-key`
- Grafana: `admin / admin`

Do not use default credentials in shared or production environments.

## Common Commands

Generate `.env` but do not start containers:

```bash
./SpoonFeed --no-start
```

Run smoke tests against an existing stack:

```bash
./SpoonFeed --smoke-only
```

Regenerate `.env`:

```bash
./SpoonFeed --force-env
```

Preview actions:

```bash
./SpoonFeed --dry-run
```

## Gigapipe

```bash
export GIGAPIPE_OTLP_ENDPOINT="https://YOUR-GIGAPIPE-OTLP-ENDPOINT:4317"
export GIGAPIPE_API_KEY="YOUR-GIGAPIPE-API-KEY"

./SpoonFeed --with-gigapipe
```

This uses both:

- `examples/docker-compose.yml`
- `examples/docker-compose.gigapipe.yml`

## NLP Providers

Default local deterministic mode:

```bash
./SpoonFeed --nlp local
```

Ollama:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export NLP_MODEL=llama3.1

./SpoonFeed --nlp ollama
```

OpenAI-compatible API:

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
export NLP_MODEL=gpt-4o-mini

./SpoonFeed --nlp openai
```

Vultr Serverless Inference:

```bash
export VULTR_API_KEY=...
export VULTR_INFERENCE_URL=https://YOUR-VULTR-INFERENCE-ENDPOINT/v1/chat/completions
export NLP_MODEL=llama-3.1-8b-instruct

./SpoonFeed --nlp vultr
```

## Production Warning

SpoonFeed is a bootstrap helper, not a full production orchestrator.

Before production:

- Move secrets to a secret manager.
- Replace default API and Grafana credentials.
- Use TLS/mTLS.
- Configure PostgreSQL backups and restore tests.
- Review `docs/compliance-readiness.md`.
- Review `docs/deployment.md`.
- Validate Kamailio and Asterisk in a lab before enforcing call blocking.

## Troubleshooting

If the stack does not start:

```bash
docker compose -f examples/docker-compose.yml logs -f
```

If smoke tests fail, check:

- `http://localhost:8000/health`
- `.env` values
- Docker container health
- PostgreSQL initialization logs
- Trust API logs
