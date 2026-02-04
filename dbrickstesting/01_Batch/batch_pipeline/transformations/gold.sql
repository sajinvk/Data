-- Gold Layer: Product Performance Summary
-- Combines sales and review data to provide comprehensive product insights
CREATE OR REFRESH MATERIALIZED VIEW gld_product_performance
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
FROM pilotws.pilotschema.slv_sales_master s
LEFT JOIN pilotws.pilotschema.slv_reviews_master r
  ON s.product_name = r.product_name
GROUP BY s.product_name, s.category;


-- Gold Layer: Monthly Sales Trends by Category
-- Aggregates sales data by month and category for trend analysis
CREATE OR REFRESH MATERIALIZED VIEW gld_monthly_sales_trends
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
FROM pilotws.pilotschema.slv_sales_master
GROUP BY DATE_TRUNC('MONTH', sale_date), category;


-- Gold Layer: Top Customer Insights
-- Identifies high-value customers with their purchase and review activity
CREATE OR REFRESH MATERIALIZED VIEW gld_top_customer_insights
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
FROM pilotws.pilotschema.slv_sales_master s
LEFT JOIN pilotws.pilotschema.slv_reviews_master r
  ON s.customer_name = r.customer_name
GROUP BY s.customer_name;
