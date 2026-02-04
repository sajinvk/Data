CREATE OR REFRESH MATERIALIZED VIEW streaming_gld_product_performance
COMMENT "Product performance metrics combining sales revenue, quantity, and customer ratings"
CLUSTER BY (product_name)
AS
SELECT
  s.product_name,
  s.category,
  COUNT(DISTINCT s.sale_id) AS total_sales,
  SUM(s.quantity) AS total_quantity_sold,
  ROUND(SUM(s.total_amount), 2) AS total_revenue,
  ROUND(AVG(s.total_amount), 2) AS avg_sale_amount,
  COUNT(DISTINCT r.review_id) AS total_reviews,
  ROUND(AVG(r.rating), 2) AS avg_rating
FROM pilotws.pilotschema.streaming_slv_sales_master s
LEFT JOIN pilotws.pilotschema.streaming_slv_reviews_master r
  ON s.product_name = r.product_name
GROUP BY s.product_name, s.category;
