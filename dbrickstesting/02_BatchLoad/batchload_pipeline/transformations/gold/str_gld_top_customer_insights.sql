-- Identifies high-value customers with their purchase and review activity
CREATE OR REFRESH MATERIALIZED VIEW streaming_gld_top_customer_insights
COMMENT "Customer insights combining purchase history and review engagement"
CLUSTER BY (customer_name)
AS
SELECT
  s.customer_name,
  COUNT(DISTINCT s.sale_id) AS total_purchases,
  SUM(s.quantity) AS total_items_purchased,
  ROUND(SUM(s.total_amount), 2) AS total_spent,
  ROUND(AVG(s.total_amount), 2) AS avg_purchase_value,
  MIN(s.sale_date) AS first_purchase_date,
  MAX(s.sale_date) AS last_purchase_date,
  COUNT(DISTINCT r.review_id) AS total_reviews_written,
  ROUND(AVG(r.rating), 2) AS avg_rating_given
FROM pilotws.pilotschema.streaming_slv_sales_master s
LEFT JOIN pilotws.pilotschema.streaming_slv_reviews_master r
  ON s.customer_name = r.customer_name
GROUP BY s.customer_name;
