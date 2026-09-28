"""review history analytics

Revision ID: 004_review_history_analytics
Revises: 003_add_generator_and_export_fields
Create Date: 2026-09-28 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_review_history_analytics'
down_revision: Union[str, None] = '003_generator_export_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE NOT NULL")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0 NOT NULL")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS last_viewed TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]'::json")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS language_version VARCHAR(50)")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS analysis_duration DOUBLE PRECISION")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'completed' NOT NULL")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS review_version INTEGER DEFAULT 1 NOT NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_is_deleted ON reviews (is_deleted)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_status ON reviews (status)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_reviews_status")
    op.execute("DROP INDEX IF EXISTS ix_reviews_is_deleted")
    op.drop_column('reviews', 'review_version')
    op.drop_column('reviews', 'status')
    op.drop_column('reviews', 'analysis_duration')
    op.drop_column('reviews', 'language_version')
    op.drop_column('reviews', 'tags')
    op.drop_column('reviews', 'last_viewed')
    op.drop_column('reviews', 'view_count')
    op.drop_column('reviews', 'deleted_at')
    op.drop_column('reviews', 'is_deleted')
