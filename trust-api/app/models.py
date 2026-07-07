from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class DecisionType(str, Enum):
    allow = "allow"
    warn = "warn"
    challenge = "challenge"
    voicemail = "voicemail"
    rate_limit = "rate_limit"
    block_dno = "block_dno"
    block_analytics = "block_analytics"


class FeedbackType(str, Enum):
    wrongly_blocked = "wrongly_blocked"
    wrongly_allowed = "wrongly_allowed"
    suspicious = "suspicious"
    confirmed_fraud = "confirmed_fraud"
    other = "other"


class RedressStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    rejected = "rejected"


# --- Request models ---

class CallRequest(BaseModel):
    call_id: str = Field(..., examples=["abc123"])
    from_number: str = Field(..., examples=["+15551234567"])
    to_number: str = Field(..., examples=["+15559876543"])
    source_ip: str = Field(..., examples=["203.0.113.10"])
    source_carrier: Optional[str] = Field(None, examples=["ExampleCarrier"])
    stir_shaken: Optional[str] = Field(None, examples=["A"])
    identity_header: Optional[str] = Field(None, examples=["eyJhbGciOiJFUzI1NiJ9...;info=<https://cert.example>;alg=ES256;ppt=shaken"])
    user_agent: Optional[str] = Field(None, examples=["sip-client"])
    timestamp: str = Field(..., examples=["2026-07-06T12:00:00Z"])


class CDRRequest(BaseModel):
    call_id: str
    completed: bool
    duration_seconds: int = 0
    answer_rate_topo: Optional[str] = None


class DNOEntryRequest(BaseModel):
    number: str = Field(..., examples=["+15551234567"])
    source: str = Field(..., examples=["internal"])
    reason: Optional[str] = None
    expires_in_days: int = 365


class PolicyRequest(BaseModel):
    customer_id: str = Field(..., examples=["cust_001"])
    policy_name: str = Field(..., examples=["block_anonymous"])
    policy_json: dict = Field(default_factory=dict)
    enabled: bool = True


class FeedbackRequest(BaseModel):
    call_id: str
    customer_id: str
    feedback_type: FeedbackType
    notes: Optional[str] = None


class RedressRequest(BaseModel):
    call_id: str
    customer_id: str
    description: Optional[str] = None


class RedressUpdate(BaseModel):
    status: RedressStatus
    resolution: Optional[str] = None


class NLPQueryRequest(BaseModel):
    query: str = Field(..., examples=["Why was call abc123 blocked?"])
    customer_id: Optional[str] = None
    call_id: Optional[str] = None


# --- Response models ---

class DecisionResponse(BaseModel):
    decision: DecisionType
    trust_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason_codes: list[str] = Field(default_factory=list)
    relationship_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Customer trust health — ratio of positive to total feedback")
    challenge_mode: Optional[str] = Field(None, description="dtmf or silence — only set when decision is challenge")
    recommended_sip_response: Optional[str] = None
    redress_required: bool = False
    redress_contact: Optional[dict] = Field(None, description="Human-readable contact info for redress path")


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class DNOEntryResponse(BaseModel):
    id: str
    number: str
    source: str
    reason: Optional[str]
    created_at: str
    expires_at: str


class PolicyResponse(BaseModel):
    id: str
    customer_id: str
    policy_name: str
    policy_json: dict
    enabled: bool
    created_at: str
    updated_at: str


class FeedbackResponse(BaseModel):
    id: str
    call_id: str
    customer_id: str
    feedback_type: str
    notes: Optional[str]
    created_at: str


class RedressResponse(BaseModel):
    id: str
    call_id: str
    customer_id: str
    status: str
    description: Optional[str]
    resolution: Optional[str]
    created_at: str
    updated_at: str


class NLPQueryResponse(BaseModel):
    answer: str
    intent: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: list[dict] = Field(default_factory=list)
    provider: str = "local"
    requires_approval: bool = False
