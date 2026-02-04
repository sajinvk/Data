-- Gold Layer: Monthly Sales Trends by Category
-- Aggregates sales data by month and category for trend analysis
CREATE OR REFRESH MATERIALIZED VIEW streaming_gld_monthly_sales_trends
COMMENT "Monthly sales trends showing revenue and quantity by category"
CLUSTER BY (sale_month, category)
AS
SELECT
  DATE_TRUNC('MONTH', sale_date) AS sale_month,
  category,
  COUNT(DISTINCT sale_id) AS total_transactions,
  SUM(quantity) AS total_quantity_sold,
  ROUND(SUM(total_amount), 2) AS total_revenue,
  ROUND(AVG(total_amount), 2) AS avg_transaction_value,
  COUNT(DISTINCT customer_name) AS unique_customers
FROM pilotws.pilotschema.streaming_slv_sales_master
GROUP BY DATE_TRUNC('MONTH', sale_date), category;