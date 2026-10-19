"""002_add_provenance_and_audit_fields

Revision ID: 002_audit_fields
Revises: 001_initial_schema
Create Date: 2026-10-19 17:15:00.000000

Adds missing audit and provenance columns to news_records and collection_logs
if upgrading from legacy schema:
- news_records.last_seen_at
- news_records.validation_status
- news_records.provenance
- collection_logs.items_failed
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_audit_fields'
down_revision: Union[str, Sequence[str], None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 1. Inspect news_records
    news_cols = [c["name"] for c in inspector.get_columns("news_records")]
    with op.batch_alter_table("news_records") as batch_op:
        if "last_seen_at" not in news_cols:
            batch_op.add_column(sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
        if "validation_status" not in news_cols:
            batch_op.add_column(sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="valid"))
        if "provenance" not in news_cols:
            batch_op.add_column(sa.Column("provenance", sa.JSON(), nullable=False, server_default="{}"))

    # 2. Inspect collection_logs
    log_cols = [c["name"] for c in inspector.get_columns("collection_logs")]
    with op.batch_alter_table("collection_logs") as batch_op:
        if "items_failed" not in log_cols:
            batch_op.add_column(sa.Column("items_failed", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    news_cols = [c["name"] for c in inspector.get_columns("news_records")]
    with op.batch_alter_table("news_records") as batch_op:
        if "last_seen_at" in news_cols:
            batch_op.drop_column("last_seen_at")
        if "validation_status" in news_cols:
            batch_op.drop_column("validation_status")
        if "provenance" in news_cols:
            batch_op.drop_column("provenance")

    log_cols = [c["name"] for c in inspector.get_columns("collection_logs")]
    with op.batch_alter_table("collection_logs") as batch_op:
        if "items_failed" in log_cols:
            batch_op.drop_column("items_failed")
