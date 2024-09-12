"""Create price_drop table.

Revision ID: 7f617bc0dfc3
Revises: 09a61aaf486d
Create Date: 2023-07-21 00:21:23.637352

"""

import sqlalchemy as sa

from alembic import op

revision = "7f617bc0dfc3"
down_revision = "09a61aaf486d"
branch_labels = None
depends_on = None


sql_create_trigger = """-- sql
CREATE TRIGGER IF NOT EXISTS
    price_drop_update_updated
AFTER UPDATE ON price_drop
BEGIN
    UPDATE price_drop
    SET updated = DATETIME('NOW')
    WHERE price_drop_id = NEW.price_drop_id;
END;
"""

sql_drop_trigger = """-- sql
DROP TRIGGER IF EXISTS price_drop_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "price_drop",
        sa.Column("price_drop_id", sa.Integer(), primary_key=True),
        sa.Column(
            "created",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("deleted", sa.TIMESTAMP, nullable=True),
        sa.Column("asin", sa.String(), sa.ForeignKey("product.asin")),
        sa.Column("hostname", sa.String(), sa.ForeignKey("site.hostname")),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("price_drop")
