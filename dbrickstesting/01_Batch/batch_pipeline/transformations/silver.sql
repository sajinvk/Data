CREATE OR REFRESH MATERIALIZED VIEW slv_sales_master
AS
SELECT
  s.*,
  p.product_name,
  p.brand,
  p.category,
  p.subcategory,
  p.price AS product_price,
  concat(c.first_name, " ", c.last_name) as customer_name,
  c.email as customer_email,
  c.customer_segment
FROM
  brz_sales_mv s
JOIN
  brz_products_mv p
    ON s.product_id = p.product_id
JOIN
  brz_customers_mv c
    ON s.customer_id = c.customer_id;


CREATE OR REFRESH MATERIALIZED VIEW slv_reviews_master
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
  brz_customer_reviews_mv r
JOIN
  brz_customers_mv c
    ON r.customer_id = c.customer_id
JOIN
  brz_products_mv p
    ON r.product_id = p.product_id;