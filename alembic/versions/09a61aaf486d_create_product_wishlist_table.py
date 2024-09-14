"""Create product_wishlist table.

Revision ID: 09a61aaf486d
Revises: d10c8eddc0cf
Create Date: 2023-07-21 00:00:54.942808

"""

import sqlalchemy as sa

from alembic import op

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
    SET updated = datetime('now')
    WHERE asin = NEW.asin
      AND wishlist_id = NEW.wishlist_id ;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_wishlist_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "product_wishlist",
        sa.Column(
            "asin",
            sa.String(),
            sa.ForeignKey("product.asin"),
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
        sa.PrimaryKeyConstraint("asin", "wishlist_id", name="product_wishlist_pk"),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("product_wishlist")
