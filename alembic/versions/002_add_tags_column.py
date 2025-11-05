"""Add missing tags column to experiments table

This migration adds the tags column that might be missing in production databases.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column exists, if not add it
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='experiments' AND column_name='tags'
            ) THEN
                ALTER TABLE experiments ADD COLUMN tags JSONB DEFAULT '[]'::jsonb;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column('experiments', 'tags')
