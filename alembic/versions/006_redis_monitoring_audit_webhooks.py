"""redis monitoring audit webhooks

Revision ID: 006_redis_monitoring_audit_webhooks
Revises: 005_uploads_batch_tasks
Create Date: 2026-09-28 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_redis_audit_webhooks'
down_revision: Union[str, None] = '005_uploads_batch_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. API Keys table
    op.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        hashed_key VARCHAR(128) NOT NULL,
        prefix VARCHAR(16) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        last_used_at TIMESTAMP WITH TIME ZONE,
        expires_at TIMESTAMP WITH TIME ZONE,
        permissions JSON NOT NULL DEFAULT '[]'::json,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_api_keys_user_id ON api_keys (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_api_keys_hashed_key ON api_keys (hashed_key);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_api_keys_prefix ON api_keys (prefix);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_api_keys_is_active ON api_keys (is_active);")

    # 2. Audit Logs table
    op.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        action VARCHAR(100) NOT NULL,
        resource VARCHAR(100) NOT NULL,
        resource_id VARCHAR(255),
        ip_address VARCHAR(50),
        user_agent VARCHAR(255),
        status VARCHAR(50) NOT NULL DEFAULT 'success',
        metadata_json JSON NOT NULL DEFAULT '{}'::json,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_resource ON audit_logs (resource);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_status ON audit_logs (status);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp);")

    # 3. Webhooks table
    op.execute("""
    CREATE TABLE IF NOT EXISTS webhooks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        url VARCHAR(500) NOT NULL,
        secret VARCHAR(255) NOT NULL,
        event_type VARCHAR(100) NOT NULL DEFAULT '*',
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        last_success_at TIMESTAMP WITH TIME ZONE,
        failure_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_user_id ON webhooks (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_event_type ON webhooks (event_type);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_webhooks_is_active ON webhooks (is_active);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS webhooks CASCADE;")
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS api_keys CASCADE;")
