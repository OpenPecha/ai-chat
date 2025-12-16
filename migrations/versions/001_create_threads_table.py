"""create_threads_table

Revision ID: 001
Revises: 
Create Date: 2025-12-16 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the platform enum type
    platform_enum = postgresql.ENUM('sherab', 'webuddhist', 'webuddhist-app', name='platform_enum')
    platform_enum.create(op.get_bind(), checkfirst=True)
    
    # Create the threads table
    op.create_table(
        'threads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('platform', sa.Enum('sherab', 'webuddhist', 'webuddhist-app', name='platform_enum'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create an index on email for faster lookups
    op.create_index('ix_threads_email', 'threads', ['email'])
    
    # Create an index on created_at for sorting
    op.create_index('ix_threads_created_at', 'threads', ['created_at'])


def downgrade() -> None:
    # Drop indices
    op.drop_index('ix_threads_created_at', table_name='threads')
    op.drop_index('ix_threads_email', table_name='threads')
    
    # Drop the table
    op.drop_table('threads')
    
    # Drop the enum type
    platform_enum = postgresql.ENUM('sherab', 'webuddhist', 'webuddhist-app', name='platform_enum')
    platform_enum.drop(op.get_bind(), checkfirst=True)

