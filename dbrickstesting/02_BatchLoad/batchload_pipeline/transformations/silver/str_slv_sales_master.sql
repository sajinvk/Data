CREATE OR REFRESH MATERIALIZED VIEW streaming_slv_sales_master
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
  streaming_sales s
LEFT JOIN
  streaming_products p
    ON s.product_id = p.product_id
LEFT JOIN
  streaming_customers c
    ON s.customer_id = c.customer_id;