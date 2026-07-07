import json
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
OTEL_EXPORTER_OTLP_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
OBSERVABILITY_BACKEND = os.getenv("OBSERVABILITY_BACKEND", "local")
SERVICE_NAME = os.getenv("SERVICE_NAME", "trust-api")
DEPLOYMENT_ENVIRONMENT = os.getenv("DEPLOYMENT_ENVIRONMENT", "dev")

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

API_KEY = os.getenv("API_KEY", "change-me-in-production")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
API_KEYS_RAW = os.getenv("API_KEYS", "")

try:
    API_KEYS = json.loads(API_KEYS_RAW) if API_KEYS_RAW else {}
except json.JSONDecodeError:
    API_KEYS = {}

if not API_KEYS and API_KEY:
    API_KEYS = {
        API_KEY: {"tenant_id": "default", "role": "admin", "name": "legacy-api-key"}
    }

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
    "prodigal_grace": float(os.getenv("WEIGHT_PRODIGAL_GRACE", "1.0")),
    "forgiveness": float(os.getenv("WEIGHT_FORGIVENESS", "1.0")),
}

# Velocity (max calls per source in window seconds)
VELOCITY_MAX_CALLS = int(os.getenv("VELOCITY_MAX_CALLS", "10"))
VELOCITY_WINDOW_SECONDS = int(os.getenv("VELOCITY_WINDOW_SECONDS", "60"))
VELOCITY_BACKEND = os.getenv("VELOCITY_BACKEND", "memory")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Reputation defaults
DEFAULT_IP_REPUTATION = float(os.getenv("DEFAULT_IP_REPUTATION", "0.5"))
DEFAULT_CARRIER_REPUTATION = float(os.getenv("DEFAULT_CARRIER_REPUTATION", "0.5"))

# Grace-Oriented Trust Engine settings
PRODIGAL_GRACE_BONUS = int(os.getenv("PRODIGAL_GRACE_BONUS", "20"))
FORGIVENESS_BONUS = int(os.getenv("FORGIVENESS_BONUS", "15"))

# Challenge mode: dtmf (legacy "Press 7") or silence (AMD-based voice detection)
CHALLENGE_MODE = os.getenv("CHALLENGE_MODE", "silence")

# When enabled, SIP 603+ responses include a human-readable redress path
REDRESS_CONTACT_URL = os.getenv("REDRESS_CONTACT_URL", "")
REDRESS_CONTACT_EMAIL = os.getenv("REDRESS_CONTACT_EMAIL", "")

# When enabled, SIP responses shame carriers not implementing STIR/SHAKEN
SHAME_BAD_CARRIERS = os.getenv("SHAME_BAD_CARRIERS", "false").lower() == "true"

# NLP assistant provider. Default is deterministic/read-only local responses.
NLP_PROVIDER = os.getenv("NLP_PROVIDER", "local")
NLP_MODEL = os.getenv("NLP_MODEL", "")
NLP_TIMEOUT_SECONDS = float(os.getenv("NLP_TIMEOUT_SECONDS", "10"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
VULTR_API_KEY = os.getenv("VULTR_API_KEY", "")
VULTR_INFERENCE_URL = os.getenv("VULTR_INFERENCE_URL", "")

# STIR/SHAKEN verification mode: attestation_only or passport_structural.
STIR_SHAKEN_VERIFY_MODE = os.getenv("STIR_SHAKEN_VERIFY_MODE", "attestation_only")

# Optional redress notification webhook for ticketing/customer-support systems.
REDRESS_WEBHOOK_URL = os.getenv("REDRESS_WEBHOOK_URL", "")
