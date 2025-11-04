"""Initial migration - create experiments, metrics, and artifacts tables

Revision ID: 001
Revises: 
Create Date: 2025-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create experiments table
    op.create_table(
        'experiments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('hyperparameters', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('experiment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
    )

    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('experiment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('filepath', sa.String(500), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('artifacts')
    op.drop_table('metrics')
    op.drop_table('experiments')
