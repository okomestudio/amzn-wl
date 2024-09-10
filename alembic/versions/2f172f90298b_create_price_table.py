"""Create price table.

Revision ID: 2f172f90298b
Revises: 8981a7eed573
Create Date: 2023-07-20 18:56:24.997189

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2f172f90298b"
down_revision = "8981a7eed573"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    price_update_updated
AFTER UPDATE ON price
BEGIN
    UPDATE price
    SET updated = DATETIME('NOW')
    WHERE price_id = NEW.price_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS price_update_updated;
"""


def upgrade() -> None:  # noqa
    op.create_table(
        "price",
        sa.Column("price_id", sa.String(), primary_key=True),
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
        sa.Column("product_id", sa.String(), sa.ForeignKey("product.product_id")),
        sa.Column("site", sa.String(), nullable=False),
        sa.Column("data", sa.String(), nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:  # noqa
    op.execute(sql_drop_trigger)
    op.drop_table("price")