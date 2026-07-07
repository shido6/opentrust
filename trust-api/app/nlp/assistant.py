"""
Read-only natural-language assistant for carrier operations.

The first NLP layer intentionally answers from stored evidence only. It does
not change policy, DNO entries, thresholds, or redress state without a future
approval-gated workflow.
"""

import json
import re

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import (
    NLP_MODEL,
    NLP_PROVIDER,
    NLP_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    VULTR_API_KEY,
    VULTR_INFERENCE_URL,
)
from ..models import NLPQueryRequest, NLPQueryResponse
from ..repositories.calls import get_call, get_decision_events

DEFAULT_MODELS = {"ollama": "llama3.1", "openai": "gpt-4o-mini", "vultr": "llama-3.1-8b-instruct"}


def classify_intent(query: str) -> tuple[str, float]:
    q = query.lower()
    if any(term in q for term in ("why", "blocked", "declined", "reason")):
        return "explain_call_decision", 0.82
    if any(term in q for term in ("redress", "complaint", "appeal")):
        return "redress_status", 0.7
    if any(term in q for term in ("change", "update", "set", "block", "allow")):
        return "policy_change_request", 0.64
    return "general_audit_query", 0.45


def extract_call_id(query: str) -> str | None:
    explicit = re.search(r"call[_ -]?id\s*[:=]?\s*([A-Za-z0-9_.:-]+)", query, re.I)
    if explicit:
        return explicit.group(1)
    informal = re.search(r"\bcall\s+([A-Za-z0-9_.:-]{3,})\b", query, re.I)
    if informal:
        return informal.group(1)
    return None


async def answer_query(session: AsyncSession, req: NLPQueryRequest) -> NLPQueryResponse:
    intent, confidence = classify_intent(req.query)

    if intent == "policy_change_request":
        return NLPQueryResponse(
            answer=(
                "I can explain policy and prepare a proposed change, but I cannot "
                "modify DNO entries, customer policies, thresholds, or redress state "
                "without an explicit approval workflow."
            ),
            intent=intent,
            confidence=confidence,
            evidence=[],
            requires_approval=True,
        )

    call_id = req.call_id or extract_call_id(req.query)
    if not call_id:
        return NLPQueryResponse(
            answer="I need a call_id to answer from audit evidence.",
            intent=intent,
            confidence=0.35,
            evidence=[],
        )

    call = await get_call(session, call_id)
    if not call:
        return NLPQueryResponse(
            answer=f"I could not find call_id {call_id} in the decision audit store.",
            intent=intent,
            confidence=0.8,
            evidence=[{"type": "call_lookup", "call_id": call_id, "found": False}],
        )

    events = await get_decision_events(session, call_id)
    reason_codes = [event.reason_code for event in events if event.reason_code]
    signal_summary = [
        {
            "signal_name": event.signal_name,
            "signal_value": event.signal_value,
            "weight": event.weight,
            "reason_code": event.reason_code,
        }
        for event in events
    ]

    reason_text = ", ".join(reason_codes) if reason_codes else "no negative reason codes were recorded"
    answer = (
        f"Call {call.call_id} received decision '{call.decision}' with trust score "
        f"{call.trust_score} and confidence {call.confidence}. The recorded reasons "
        f"were: {reason_text}."
    )

    return NLPQueryResponse(
        answer=answer,
        intent=intent,
        confidence=confidence,
        evidence=[
            {
                "type": "call_decision",
                "call_id": call.call_id,
                "decision": call.decision,
                "trust_score": call.trust_score,
                "confidence": call.confidence,
            },
            {"type": "decision_events", "events": signal_summary},
        ],
    )
