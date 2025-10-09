# Data lake vs Lakehouse 
* Lakehouse - has got metadata on top of data . This helps to mimic datawarehouse functionaly on top of data lake.
* Staging data by utilizing metadata-centric Parquet-based file formats, including Delta Lake,Apache Iceberg, or Apache Hudi. Grounded in Parquet—a com‐pressed, columnar format designed for large datasets—these formats incorporate a metadata layer, offering features such as time travel,ACID (atomicity, consistency, isolation, and durability) compliance,
and more.
# Source Checklist 
Question Example
* Who will we collaborate with? Engineering (Payments)
* How will the data be used? Financial reporting and quarterly strategizing
* Are there multiple sources? Yes
* What’s the format? Semi-structured APIs (Stripe and Internal)
* What’s the frequency? Hourly
* What’s the volume? Approximately 1K new rows/day, with an existing pool of ~100K
* What processing is required? Data tidying, such as column renaming, and enrichment from
* supplementary sources
* How will the data be stored? Storing staged data in Delta tables via Databricks


# Source to Destination
* For OLTP sources , enabling CDC eases the implementation of SCD type 1 & 2.
* SCD Type 1 & 2 : [https://docs.databricks.com/aws/en/dlt/cdc?language=SQL#scd-type-1-and-scd-type-2-on-databricks]

