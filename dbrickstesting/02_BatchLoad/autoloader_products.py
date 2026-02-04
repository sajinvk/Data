# Databricks notebook source
# MAGIC %md
# MAGIC # Auto Loader for Streaming Products
# MAGIC
# MAGIC This notebook uses Databricks Auto Loader to read streaming product data from the Volume
# MAGIC and create a live Delta table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Volume paths where streaming data is written
VOLUME_PATH = "/Volumes/pilotws/pilotschema/pilotvolume"
PRODUCT_STREAM_PATH = f"{VOLUME_PATH}/products"

# Target catalog and schema for Delta table
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"

# Checkpoint and schema locations
CHECKPOINT_PATH = f"{VOLUME_PATH}/_checkpoints/products"
SCHEMA_PATH = f"{VOLUME_PATH}/_schemas/products"

# Target table name
STREAMING_PRODUCT_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.streaming_products"

print("Configuration loaded successfully!")
print(f"Source: {PRODUCT_STREAM_PATH}")
print(f"Target: {STREAMING_PRODUCT_TABLE}")

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
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType, TimestampType, BooleanType

# Define schema for products
product_schema = StructType([
    StructField("product_id", IntegerType(), False),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("subcategory", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("description", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("cost", DoubleType(), True),
    StructField("stock_quantity", IntegerType(), True),
    StructField("weight_kg", DoubleType(), True),
    StructField("launch_date", DateType(), True),
    StructField("is_active", BooleanType(), True),
    StructField("batch_timestamp", TimestampType(), True)
])

# Create streaming read with Auto Loader
# Let Auto Loader infer schema with evolution enabled
products_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load(f"{PRODUCT_STREAM_PATH}/batch_*")
)

# Add processing timestamp and calculated fields
products_stream = (products_stream
    .withColumn("processing_timestamp", F.current_timestamp())
    .withColumn("profit_margin", F.round((F.col("price") - F.col("cost")) / F.col("price") * 100, 2))
)

# Write to Delta table
products_query = (products_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .table(STREAMING_PRODUCT_TABLE)
)

print(f"✓ Product stream started → {STREAMING_PRODUCT_TABLE}")

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
# MAGIC ## Verify Product Table

# COMMAND ----------

print("=" * 80)
print("STREAMING PRODUCTS TABLE SUMMARY")
print("=" * 80)

try:
    df = spark.table(STREAMING_PRODUCT_TABLE)
    count = df.count()
    
    if count > 0:
        batch_info = df.agg(
            F.min("batch_timestamp").alias("first_batch"),
            F.max("batch_timestamp").alias("last_batch"),
            F.countDistinct("batch_timestamp").alias("num_batches")
        ).collect()[0]
        
        print(f"\nTable: {STREAMING_PRODUCT_TABLE}")
        print(f"  Total Rows: {count}")
        print(f"  Number of Batches: {batch_info['num_batches']}")
        print(f"  First Batch: {batch_info['first_batch']}")
        print(f"  Last Batch: {batch_info['last_batch']}")
        
        print(f"\nSchema:")
        df.printSchema()
    else:
        print(f"\nTable: {STREAMING_PRODUCT_TABLE}")
        print(f"  Total Rows: 0 (No data loaded yet)")
        
except Exception as e:
    print(f"\nTable: {STREAMING_PRODUCT_TABLE}")
    print(f"  Error: {str(e)[:200]}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Data

# COMMAND ----------

print("Latest Product Records (Top 10):\n")

try:
    spark.table(STREAMING_PRODUCT_TABLE).orderBy(F.desc("batch_timestamp")).select(
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "price",
        "profit_margin",
        "stock_quantity",
        "batch_timestamp"
    ).show(10, truncate=False)
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Statistics

# COMMAND ----------

try:
    df = spark.table(STREAMING_PRODUCT_TABLE)
    
    print("Product Statistics:\n")
    
    # By category
    print("Products by Category:")
    df.groupBy("category").agg(
        F.count("*").alias("product_count"),
        F.avg("price").alias("avg_price"),
        F.sum("stock_quantity").alias("total_stock")
    ).orderBy(F.desc("product_count")).show()
    
    # By brand
    print("Top 10 Brands:")
    df.groupBy("brand").count().orderBy(F.desc("count")).show(10)
    
    # Price statistics
    print("Price Statistics:")
    df.select(
        F.avg("price").alias("avg_price"),
        F.min("price").alias("min_price"),
        F.max("price").alias("max_price"),
        F.avg("profit_margin").alias("avg_profit_margin")
    ).show()
    
    # Active vs Inactive
    print("Active Status:")
    df.groupBy("is_active").count().show()
    
except Exception as e:
    print(f"Error generating statistics: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC **✓ What This Notebook Does:**
# MAGIC - Reads product parquet files from Volume using Auto Loader
# MAGIC - Creates streaming Delta table with schema evolution
# MAGIC - Calculates profit margin automatically
# MAGIC - Processes data incrementally (only new files)
# MAGIC
# MAGIC **📊 Scheduling:**
# MAGIC - Schedule to run every 5-10 minutes using Databricks Workflows
# MAGIC - Auto Loader automatically picks up new files
