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
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

API_KEY = os.getenv("API_KEY", "change-me-in-production")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

# Scoring thresholds (0-100)
THRESHOLD_WARN = int(os.getenv("THRESHOLD_WARN", "70"))
THRESHOLD_CHALLENGE = int(os.getenv("THRESHOLD_CHALLENGE", "50"))
THRESHOLD_BLOCK = int(os.getenv("THRESHOLD_BLOCK", "30"))

# Default signal weights
SIGNAL_WEIGHTS = {
    "stir_shaken": float(os.getenv("WEIGHT_STIR_SHAKEN", "1.0")),
    "source_carrier": float(os.getenv("WEIGHT_SOURCE_CARRIER", "0.8")),
    "user_agent": float(os.getenv("WEIGHT_USER_AGENT", "0.5")),
    "ip_reputation": float(os.getenv("WEIGHT_IP_REPUTATION", "0.9")),
    "carrier_reputation": float(os.getenv("WEIGHT_CARRIER_REPUTATION", "0.8")),
    "call_velocity": float(os.getenv("WEIGHT_CALL_VELOCITY", "0.7")),
    "answer_rate": float(os.getenv("WEIGHT_ANSWER_RATE", "0.6")),
    "dno_match": float(os.getenv("WEIGHT_DNO_MATCH", "1.0")),
    "policy_eval": float(os.getenv("WEIGHT_POLICY_EVAL", "1.0")),
}

# Velocity (max calls per source in window seconds)
VELOCITY_MAX_CALLS = int(os.getenv("VELOCITY_MAX_CALLS", "10"))
VELOCITY_WINDOW_SECONDS = int(os.getenv("VELOCITY_WINDOW_SECONDS", "60"))

# Reputation defaults
DEFAULT_IP_REPUTATION = float(os.getenv("DEFAULT_IP_REPUTATION", "0.5"))
DEFAULT_CARRIER_REPUTATION = float(os.getenv("DEFAULT_CARRIER_REPUTATION", "0.5"))
