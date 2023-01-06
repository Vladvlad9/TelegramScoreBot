"""create account table

Revision ID: bc0c3e62806a
Revises: 
Create Date: 2022-12-06 22:45:04.362631

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BYTEA

# revision identifiers, used by Alembic.
revision = 'bc0c3e62806a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('position_menu',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('baskets',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('parent_id', sa.Integer(), nullable=True),
                    sa.Column('menu_id', sa.Integer(), nullable=True),
                    sa.Column('count', sa.Integer(), nullable=True),
                    sa.Column('user_id', sa.BigInteger(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('sizes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('types',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('menu',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('parent_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Text(), nullable=True),
                    sa.Column('photo', BYTEA, nullable=True),
                    sa.Column('type_id', sa.Integer(), nullable=True),
                    sa.Column('price', sa.Text(), nullable=True),
                    sa.Column('size_id', sa.Integer(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['type_id'], ['types.id'], ondelete='NO ACTION'),
                    sa.ForeignKeyConstraint(['size_id'], ['sizes.id'], ondelete='NO ACTION'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('sizes')
    op.drop_table('types')
    op.drop_table('pizza_menu')
