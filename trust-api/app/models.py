from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DecisionType(str, Enum):
    allow = "allow"
    warn = "warn"
    challenge = "challenge"
    voicemail = "voicemail"
    rate_limit = "rate_limit"
    block_dno = "block_dno"
    block_analytics = "block_analytics"


class CallRequest(BaseModel):
    call_id: str = Field(..., examples=["abc123"])
    from_number: str = Field(..., examples=["+15551234567"])
    to_number: str = Field(..., examples=["+15559876543"])
    source_ip: str = Field(..., examples=["203.0.113.10"])
    source_carrier: Optional[str] = Field(None, examples=["ExampleCarrier"])
    stir_shaken: Optional[str] = Field(None, examples=["A"])
    user_agent: Optional[str] = Field(None, examples=["sip-client"])
    timestamp: str = Field(..., examples=["2026-07-06T12:00:00Z"])


class DecisionResponse(BaseModel):
    decision: DecisionType
    trust_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason_codes: list[str] = Field(default_factory=list)
    recommended_sip_response: Optional[str] = None
    redress_required: bool = False


class HealthResponse(BaseModel):
    status: str = "ok"
