"""Initial migration

Revision ID: b7fe882f94bc
Revises: 
Create Date: 2025-04-05 13:03:06.418802
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7fe882f94bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create party first
    op.create_table('party',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('total_seats', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create state (depends on party)
    op.create_table('state',
        sa.Column('id', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('CM_party_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['CM_party_id'], ['party.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. Create candidate WITHOUT FK to constituency yet
    op.create_table('candidate',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('photo', sa.String(), nullable=True),
        sa.Column('const_id', sa.String(), nullable=True),  # temporarily allow null
        sa.Column('party_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum('WON', 'LOST', name='candidate_status'), nullable=False),
        sa.Column('elec_type', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['party_id'], ['party.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create constituency (can reference candidate)
    op.create_table('constituency',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('state_id', sa.String(length=10), nullable=False),
        sa.Column('mla_id', sa.UUID(), nullable=True),
        sa.Column('mp_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['state_id'], ['state.id']),
        sa.ForeignKeyConstraint(['mla_id'], ['candidate.id']),
        sa.ForeignKeyConstraint(['mp_id'], ['candidate.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Add FK from candidate.const_id → constituency.id AFTER constituency exists
    op.create_foreign_key(
        "fk_candidate_constituency", "candidate", "constituency", ["const_id"], ["id"]
    )

    # 6. Create election table
    op.create_table('election',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('LOKSABHA', 'VIDHANSABHA', name='election_type'), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('state_id', sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(['state_id'], ['state.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state_id', 'year', 'type', name='unique_state_year_type')
    )


def downgrade():
    # Drop tables in reverse dependency order
    op.drop_table('election')
    op.drop_constraint('fk_candidate_constituency', 'candidate', type_='foreignkey')
    op.drop_table('constituency')
    op.drop_table('candidate')
    op.drop_table('state')
    op.drop_table('party')
