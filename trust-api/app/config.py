import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://opentrust:opentrust@localhost:5432/opentrust",
)

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

API_KEY = os.getenv("API_KEY", "")

THRESHOLD_WARN = int(os.getenv("THRESHOLD_WARN", "70"))
THRESHOLD_CHALLENGE = int(os.getenv("THRESHOLD_CHALLENGE", "50"))
THRESHOLD_BLOCK = int(os.getenv("THRESHOLD_BLOCK", "30"))
