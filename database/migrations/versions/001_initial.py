"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, INET

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "calls",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("call_id", sa.String(255), nullable=False, unique=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("from_number", sa.String(32), nullable=False),
        sa.Column("to_number", sa.String(32), nullable=False),
        sa.Column("source_ip", INET(), nullable=False),
        sa.Column("source_carrier", sa.String(128)),
        sa.Column("stir_shaken_result", sa.String(1)),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("trust_score", sa.Integer()),
        sa.Column("confidence", sa.Float()),
        sa.Column("final_action", sa.String(64)),
        sa.Column("call_completed", sa.Boolean(), server_default=sa.text("FALSE")),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_calls_timestamp", "calls", ["timestamp"])
    op.create_index("idx_calls_from_number", "calls", ["from_number"])
    op.create_index("idx_calls_decision", "calls", ["decision"])
    op.create_index("idx_calls_source_carrier", "calls", ["source_carrier"])

    op.create_table(
        "decision_events",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("call_id", sa.String(255), sa.ForeignKey("calls.call_id"), nullable=False),
        sa.Column("signal_name", sa.String(128), nullable=False),
        sa.Column("signal_value", sa.Text()),
        sa.Column("weight", sa.Float()),
        sa.Column("reason_code", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_decision_events_call_id", "decision_events", ["call_id"])

    op.create_table(
        "customer_feedback",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("call_id", sa.String(255), sa.ForeignKey("calls.call_id"), nullable=False),
        sa.Column("customer_id", sa.String(128), nullable=False),
        sa.Column("feedback_type", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "dno_entries",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("number", sa.String(32), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_dno_entries_number", "dno_entries", ["number"])
    op.create_index("idx_dno_entries_expires", "dno_entries", ["expires_at"])

    op.create_table(
        "policies",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("customer_id", sa.String(128), nullable=False),
        sa.Column("policy_name", sa.String(255), nullable=False),
        sa.Column("policy_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_policies_customer_id", "policies", ["customer_id"])

    op.create_table(
        "redress_requests",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("call_id", sa.String(255), sa.ForeignKey("calls.call_id"), nullable=False),
        sa.Column("customer_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'open'")),
        sa.Column("description", sa.Text()),
        sa.Column("resolution", sa.Text()),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "schema_version",
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("INSERT INTO schema_version (version) VALUES (1)")


def downgrade() -> None:
    op.drop_table("redress_requests")
    op.drop_table("policies")
    op.drop_table("dno_entries")
    op.drop_table("customer_feedback")
    op.drop_table("decision_events")
    op.drop_table("calls")
    op.drop_table("schema_version")
