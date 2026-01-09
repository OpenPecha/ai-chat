"""create applications table

Revision ID: cc98c477b5eb
Revises: 92ae4c8d0e00
Create Date: 2026-01-09 16:34:07.568047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc98c477b5eb'
down_revision = '92ae4c8d0e00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create applications table
    op.create_table('applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add application_id column to threads table
    op.add_column('threads', sa.Column('application_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_threads_application_id', 'threads', 'applications', ['application_id'], ['id'])
    
    # Remove old platform column if it exists
    op.drop_column('threads', 'platform')
    
    # Add device_type column
    op.execute("CREATE TYPE devicetype AS ENUM ('web', 'mobile_app')")
    op.add_column('threads', sa.Column('device_type', sa.Enum('web', 'mobile_app', name='devicetype'), nullable=True))


def downgrade() -> None:
    op.drop_column('threads', 'device_type')
    op.execute("DROP TYPE devicetype")
    op.drop_constraint('fk_threads_application_id', 'threads', type_='foreignkey')
    op.drop_column('threads', 'application_id')
    op.drop_table('applications')
    # Re-add platform column
    op.execute("CREATE TYPE platform AS ENUM ('sherab', 'webuddhist', 'webuddhist_app')")
    op.add_column('threads', sa.Column('platform', sa.Enum('sherab', 'webuddhist', 'webuddhist_app', name='platform'), nullable=False))

