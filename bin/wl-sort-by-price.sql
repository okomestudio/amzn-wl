-- Sort items by price in ascending order

WITH
  price AS (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY
          asin
        ORDER BY
          created DESC
      ) AS NO,
      product_price_id,
      asin,
      hostname,
      created,
      value AS price
    FROM
      product_price
    WHERE
      created > DATETIME('now', '-1 day')
  )
SELECT
  price.price,
  SUBSTR(title, 0, 40) AS title,
  'https://' || SUBSTR(price.hostname, 5) || '/dp/' || product.asin || '/' AS product_url,
  'https://' || SUBSTR(wishlist.hostname, 5) || '/hz/wishlist/ls/' || pw.wishlist_id AS wishlist_url,
  ppd.original_value
FROM
  product
  INNER JOIN price ON product.asin = price.asin
  AND price.no = 1
  LEFT JOIN product_wishlist pw ON product.asin = pw.asin
  LEFT JOIN wishlist ON pw.wishlist_id = wishlist.wishlist_id
  LEFT JOIN product_price_drop ppd ON price.product_price_id = ppd.product_price_id
ORDER BY
  price ASC
