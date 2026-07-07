-- OpenTrust SIP Database Schema
-- PostgreSQL 15+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Core call records
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(255) NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    from_number VARCHAR(32) NOT NULL,
    to_number VARCHAR(32) NOT NULL,
    source_ip INET NOT NULL,
    source_carrier VARCHAR(128),
    stir_shaken_result CHAR(1),
    decision VARCHAR(32) NOT NULL,
    trust_score INTEGER CHECK (trust_score BETWEEN 0 AND 100),
    confidence REAL CHECK (confidence BETWEEN 0 AND 1),
    final_action VARCHAR(64),
    call_completed BOOLEAN DEFAULT FALSE,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_calls_timestamp ON calls (timestamp DESC);
CREATE INDEX idx_calls_from_number ON calls (from_number);
CREATE INDEX idx_calls_to_number ON calls (to_number);
CREATE INDEX idx_calls_decision ON calls (decision);
CREATE INDEX idx_calls_source_carrier ON calls (source_carrier);

-- Per-call signal evaluation log
CREATE TABLE decision_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(255) NOT NULL REFERENCES calls(call_id),
    signal_name VARCHAR(128) NOT NULL,
    signal_value TEXT,
    weight REAL,
    reason_code VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_decision_events_call_id ON decision_events (call_id);
CREATE INDEX idx_decision_events_reason_code ON decision_events (reason_code);

-- Customer feedback on decisions
CREATE TABLE customer_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(255) NOT NULL REFERENCES calls(call_id),
    customer_id VARCHAR(128) NOT NULL,
    feedback_type VARCHAR(32) NOT NULL CHECK (feedback_type IN (
        'wrongly_blocked', 'wrongly_allowed', 'suspicious', 'confirmed_fraud', 'other'
    )),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customer_feedback_call_id ON customer_feedback (call_id);
CREATE INDEX idx_customer_feedback_type ON customer_feedback (feedback_type);

-- Do Not Originate entries
CREATE TABLE dno_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    number VARCHAR(32) NOT NULL,
    source VARCHAR(64) NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_dno_entries_number ON dno_entries (number);
CREATE INDEX idx_dno_entries_expires ON dno_entries (expires_at);

-- Customer-specific policies
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(128) NOT NULL,
    policy_name VARCHAR(255) NOT NULL,
    policy_json JSONB NOT NULL DEFAULT '{}',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policies_customer_id ON policies (customer_id);
CREATE INDEX idx_policies_enabled ON policies (enabled);

-- Redress requests
CREATE TABLE redress_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(255) NOT NULL REFERENCES calls(call_id),
    customer_id VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'open' CHECK (status IN (
        'open', 'investigating', 'resolved', 'rejected'
    )),
    description TEXT,
    resolution TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_redress_requests_status ON redress_requests (status);
CREATE INDEX idx_redress_requests_customer_id ON redress_requests (customer_id);

-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_version (version) VALUES (1);
