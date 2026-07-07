"""
OpenTelemetry + Prometheus + structured logging setup.
"""

import json
import logging
import sys
from datetime import datetime, timezone

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, make_asgi_app

from .config import LOG_FORMAT, LOG_LEVEL, OTEL_EXPORTER_OTLP_ENDPOINT

# --- Prometheus metrics ---

decisions_total = Counter(
    "trust_decisions_total",
    "Total decisions by type",
    ["decision", "carrier"],
)

decisions_per_carrier = Counter(
    "trust_decisions_per_carrier_total",
    "Decisions partitioned by source carrier",
    ["carrier", "decision"],
)

trust_score_hist = Histogram(
    "trust_score",
    "Distribution of trust scores",
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
)

trust_latency = Histogram(
    "trust_latency_seconds",
    "API response time in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

false_positive_counter = Counter(
    "trust_false_positive_total",
    "Confirmed false positive blocks",
    ["carrier"],
)

customer_override_counter = Counter(
    "trust_customer_override_total",
    "Customer override events",
)

dno_matches_counter = Counter(
    "trust_dno_matches_total",
    "DNO match count",
    ["source"],
)

redress_time_hist = Histogram(
    "trust_redress_time_hours",
    "Time to resolve redress requests in hours",
    buckets=[1, 4, 8, 24, 48, 72, 168],
)


def setup_telemetry(app):
    """Configure OpenTelemetry tracing, metrics, and structured logging."""

    # --- Structured JSON logging ---

    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if hasattr(record, "extra"):
                log_entry.update(record.extra)
            if record.exc_info and record.exc_info[0]:
                log_entry["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_entry)

    handler = logging.StreamHandler(sys.stdout)
    if LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL.upper())
    # Remove default handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)

    # --- OpenTelemetry ---

    resource = Resource.create({"service.name": "trust-api"})
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    # --- Prometheus metrics endpoint ---
    app.mount("/metrics", make_asgi_app())
