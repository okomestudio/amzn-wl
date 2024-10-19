"""add currency_id column

Revision ID: e1413d549209
Revises: d01bf8db3764
Create Date: 2024-10-18 23:14:27.193229

"""

import sqlalchemy as sa

from alembic import op

revision = "e1413d549209"
down_revision = "d01bf8db3764"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE product_price ADD COLUMN currency_id INTEGER REFERENCES currency(currency_id)"
    )
    op.execute(
        "ALTER TABLE product_price_drop ADD COLUMN currency_id INTEGER REFERENCES currency(currency_id)"
    )
    op.execute(
        "ALTER TABLE product_price_drop ADD COLUMN original_currency_id INTEGER REFERENCES currency(currency_id)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE product_price_drop DROP COLUMN original_currency_id")
    op.execute("ALTER TABLE product_price_drop DROP COLUMN currency_id")
    op.execute("ALTER TABLE product_price DROP COLUMN currency_id")
