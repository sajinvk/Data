# Databricks notebook source
# MAGIC %md
# MAGIC # Auto Loader for Streaming Sales
# MAGIC
# MAGIC This notebook uses Databricks Auto Loader to read streaming sales data from the Volume
# MAGIC and create a live Delta table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Volume paths where streaming data is written
VOLUME_PATH = "/Volumes/pilotws/pilotschema/pilotvolume"
SALES_STREAM_PATH = f"{VOLUME_PATH}/sales"

# Target catalog and schema for Delta table
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"

# Checkpoint and schema locations
CHECKPOINT_PATH = f"{VOLUME_PATH}/_checkpoints/sales"
SCHEMA_PATH = f"{VOLUME_PATH}/_schemas/sales"

# Target table name
STREAMING_SALES_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.streaming_sales"

print("Configuration loaded successfully!")
print(f"Source: {SALES_STREAM_PATH}")
print(f"Target: {STREAMING_SALES_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Checkpoint and Schema Directories

# COMMAND ----------

dbutils.fs.mkdirs(CHECKPOINT_PATH)
dbutils.fs.mkdirs(SCHEMA_PATH)

print("✓ Checkpoint and schema directories created/verified")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Schema and Start Auto Loader Stream

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

# Define schema for sales
sales_schema = StructType([
    StructField("sale_id", IntegerType(), False),
    StructField("customer_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("sale_date", TimestampType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("discount_percent", IntegerType(), True),
    StructField("discount_amount", DoubleType(), True),
    StructField("total_amount", DoubleType(), True),
    StructField("payment_method", StringType(), True),
    StructField("status", StringType(), True),
    StructField("shipping_address", StringType(), True),
    StructField("batch_timestamp", TimestampType(), True)
])

# Create streaming read with Auto Loader
# Let Auto Loader infer schema with evolution enabled
sales_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load(f"{SALES_STREAM_PATH}/batch_*")
)

# Add processing timestamp and calculated fields
sales_stream = (sales_stream
    .withColumn("processing_timestamp", F.current_timestamp())
    .withColumn("sale_year", F.year("sale_date"))
    .withColumn("sale_month", F.month("sale_date"))
    .withColumn("sale_day", F.dayofmonth("sale_date"))
)

# Write to Delta table
sales_query = (sales_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .table(STREAMING_SALES_TABLE)
)

print(f"✓ Sales stream started → {STREAMING_SALES_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Wait for Stream to Complete

# COMMAND ----------

import time

print("\nWaiting for stream to process data...")
print("Using trigger(availableNow=True) - will process all available data and stop.")
print()

max_wait_time = 300
start_time = time.time()

while time.time() - start_time < max_wait_time:
    active_streams = spark.streams.active
    if len(active_streams) == 0:
        print("✓ Stream completed processing!")
        break
    
    for stream in active_streams:
        status = stream.status
        print(f"  Stream status: {status.get('message', 'Processing...')}")
    
    time.sleep(5)
else:
    print("⚠️  Stream still running after timeout")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Sales Table

# COMMAND ----------

print("=" * 80)
print("STREAMING SALES TABLE SUMMARY")
print("=" * 80)

try:
    df = spark.table(STREAMING_SALES_TABLE)
    count = df.count()
    
    if count > 0:
        batch_info = df.agg(
            F.min("batch_timestamp").alias("first_batch"),
            F.max("batch_timestamp").alias("last_batch"),
            F.countDistinct("batch_timestamp").alias("num_batches")
        ).collect()[0]
        
        print(f"\nTable: {STREAMING_SALES_TABLE}")
        print(f"  Total Rows: {count}")
        print(f"  Number of Batches: {batch_info['num_batches']}")
        print(f"  First Batch: {batch_info['first_batch']}")
        print(f"  Last Batch: {batch_info['last_batch']}")
        
        print(f"\nSchema:")
        df.printSchema()
    else:
        print(f"\nTable: {STREAMING_SALES_TABLE}")
        print(f"  Total Rows: 0 (No data loaded yet)")
        
except Exception as e:
    print(f"\nTable: {STREAMING_SALES_TABLE}")
    print(f"  Error: {str(e)[:200]}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Data

# COMMAND ----------

print("Latest Sales Records (Top 10):\n")

try:
    spark.table(STREAMING_SALES_TABLE).orderBy(F.desc("batch_timestamp")).select(
        "sale_id",
        "customer_id",
        "product_id",
        "sale_date",
        "quantity",
        "total_amount",
        "payment_method",
        "status",
        "batch_timestamp"
    ).show(10, truncate=False)
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Statistics

# COMMAND ----------

try:
    df = spark.table(STREAMING_SALES_TABLE)
    
    print("Sales Statistics:\n")
    
    # Revenue by status
    print("Revenue by Status:")
    df.groupBy("status").agg(
        F.count("*").alias("transaction_count"),
        F.sum("total_amount").alias("total_revenue")
    ).orderBy(F.desc("total_revenue")).show()
    
    # By payment method
    print("Transactions by Payment Method:")
    df.groupBy("payment_method").agg(
        F.count("*").alias("transaction_count"),
        F.sum("total_amount").alias("total_revenue"),
        F.avg("total_amount").alias("avg_transaction")
    ).orderBy(F.desc("transaction_count")).show()
    
    # Overall metrics
    print("Overall Sales Metrics:")
    df.agg(
        F.count("*").alias("total_transactions"),
        F.sum("total_amount").alias("total_revenue"),
        F.avg("total_amount").alias("avg_transaction_value"),
        F.sum("quantity").alias("total_items_sold")
    ).show()
    
    # Daily trends (last 7 days)
    print("Daily Sales Trends:")
    df.groupBy(F.date_format("sale_date", "yyyy-MM-dd").alias("sale_date")).agg(
        F.count("*").alias("transactions"),
        F.sum("total_amount").alias("revenue")
    ).orderBy(F.desc("sale_date")).show(7)
    
except Exception as e:
    print(f"Error generating statistics: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC **✓ What This Notebook Does:**
# MAGIC - Reads sales parquet files from Volume using Auto Loader
# MAGIC - Creates streaming Delta table with schema evolution
# MAGIC - Adds date partitioning fields (year, month, day)
# MAGIC - Processes data incrementally (only new files)
# MAGIC
# MAGIC **📊 Scheduling:**
# MAGIC - Schedule to run every 5-10 minutes using Databricks Workflows
# MAGIC - Auto Loader automatically picks up new files
# MAGIC - Perfect for real-time revenue dashboards
