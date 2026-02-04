CREATE OR REFRESH MATERIALIZED VIEW pilotws.pilotschema.brz_products_mv
AS
SELECT *
FROM pilotws.pilotschema.products;

CREATE OR REFRESH MATERIALIZED VIEW pilotws.pilotschema.brz_sales_mv
AS
SELECT *
FROM pilotws.pilotschema.sales;

CREATE OR REFRESH MATERIALIZED VIEW pilotws.pilotschema.brz_customers_mv
AS
SELECT *
FROM pilotws.pilotschema.customers;

CREATE OR REFRESH MATERIALIZED VIEW pilotws.pilotschema.brz_customer_reviews_mv
AS
SELECT *
FROM pilotws.pilotschema.customer_reviews;
