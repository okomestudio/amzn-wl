"""drop currency columns

Revision ID: 5b6303405a29
Revises: ff54dced33c2
Create Date: 2024-10-31 11:27:56.003671

"""

import sqlalchemy as sa

from alembic import op

revision = "5b6303405a29"
down_revision = "ff54dced33c2"
branch_labels = None
depends_on = None


droppables = [
    ("product_price", "currency"),
    ("product_price_drop", "currency"),
    ("product_price_drop", "original_currency"),
]


def upgrade() -> None:
    for droppable in droppables:
        table, column = droppable
        op.drop_column(table, column)


def downgrade() -> None:
    for droppable in droppables:
        table, column = droppable
        op.add_column(table, sa.Column(column, sa.String(1), nullable=True))
