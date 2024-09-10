"""Create product_wishlist table.

Revision ID: 09a61aaf486d
Revises: d10c8eddc0cf
Create Date: 2023-07-21 00:00:54.942808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "09a61aaf486d"
down_revision = "d10c8eddc0cf"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_wishlist_update_updated
AFTER UPDATE ON product_wishlist
BEGIN
    UPDATE product_wishlist
    SET updated = DATETIME('NOW')
    WHERE wishlist_id = NEW.wishlist_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_wishlist_update_updated;
"""


def upgrade() -> None:  # noqa
    op.create_table(
        "product_wishlist",
        sa.Column(
            "product_id",
            sa.String(),
            sa.ForeignKey("product.product_id"),
            primary_key=True,
        ),
        sa.Column(
            "wishlist_id",
            sa.String(),
            sa.ForeignKey("wishlist.wishlist_id"),
            primary_key=True,
        ),
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
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:  # noqa
    op.execute(sql_drop_trigger)
    op.drop_table("product_wishlist")
