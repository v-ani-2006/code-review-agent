"""uploads batch tasks

Revision ID: 005_uploads_batch_tasks
Revises: 004_review_history_analytics
Create Date: 2026-09-28 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_uploads_batch_tasks'
down_revision: Union[str, None] = '004_review_history_analytics'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        task_type VARCHAR(50) NOT NULL DEFAULT 'batch_upload',
        status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
        filename VARCHAR(255),
        total_files INTEGER NOT NULL DEFAULT 0,
        processed_files INTEGER NOT NULL DEFAULT 0,
        failed_files INTEGER NOT NULL DEFAULT 0,
        progress_percentage DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        started_at TIMESTAMP WITH TIME ZONE,
        completed_at TIMESTAMP WITH TIME ZONE,
        error_message TEXT,
        output_path TEXT,
        processing_time DOUBLE PRECISION,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status);")

    op.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        original_filename VARCHAR(255) NOT NULL,
        stored_filename VARCHAR(255) NOT NULL,
        file_size INTEGER NOT NULL,
        file_hash VARCHAR(64) NOT NULL,
        mime_type VARCHAR(100) NOT NULL DEFAULT 'text/x-python',
        language VARCHAR(50) NOT NULL DEFAULT 'python',
        uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        review_id UUID REFERENCES reviews(id) ON DELETE SET NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
    );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploads_user_id ON uploads (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploads_file_hash ON uploads (file_hash);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploads_review_id ON uploads (review_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS uploads CASCADE;")
    op.execute("DROP TABLE IF EXISTS tasks CASCADE;")
