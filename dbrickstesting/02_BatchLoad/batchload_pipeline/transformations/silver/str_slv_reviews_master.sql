
CREATE OR REFRESH MATERIALIZED VIEW streaming_slv_reviews_master
AS
SELECT
  r.review_id,
  r.customer_id,
  concat(c.first_name, " ", c.last_name) AS customer_name,
  c.email AS customer_email,
  c.customer_segment,
  r.product_id,
  p.product_name,
  p.brand,
  p.category,
  p.subcategory,
  p.price AS product_price,
  r.rating,
  r.review_text,
  r.review_date,
  r.verified_purchase,
  r.helpful_count
FROM
  pilotws.pilotschema.streaming_reviews r
LEFT JOIN
  pilotws.pilotschema.streaming_customers c
    ON r.customer_id = c.customer_id
LEFT JOIN
  pilotws.pilotschema.streaming_products p
    ON r.product_id = p.product_id;