"""replace currency with currency_id

Revision ID: ff54dced33c2
Revises: e1413d549209
Create Date: 2024-10-31 10:04:56.166070

"""

import sqlalchemy as sa

from alembic import op

revision = "ff54dced33c2"
down_revision = "e1413d549209"
branch_labels = None
depends_on = None

sql_currency_to_currency_id = """
UPDATE {table}
SET
  {id} = c.currency_id
FROM
  currency as c
WHERE
  {table}.{id} IS NULL
  AND {table}.{key} = c.symbol
"""

sql_currency_id_to_currency = """
UPDATE {table}
SET
  {key} = c.symbol
FROM
  currency as c
WHERE
  {table}.{id} = c.currency_id
"""

updatables = [
    ("product_price", "currency", "currency_id"),
    ("product_price_drop", "currency", "currency_id"),
    ("product_price_drop", "original_currency", "original_currency_id"),
]


def upgrade() -> None:
    for updatable in updatables:
        table, key, id = updatable
        sql = sql_currency_to_currency_id.format(table=table, key=key, id=id)
        op.execute(sql)


def downgrade() -> None:
    for updatable in updatables[::-1]:
        table, key, id = updatable
        sql = sql_currency_id_to_currency.format(table=table, key=key, id=id)
        op.execute(sql)
