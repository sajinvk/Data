# Databricks notebook source
# MAGIC %md
# MAGIC # Auto Loader for Streaming Customers
# MAGIC
# MAGIC This notebook uses Databricks Auto Loader to read streaming customer data from the Volume
# MAGIC and create a live Delta table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Volume paths where streaming data is written
VOLUME_PATH = "/Volumes/pilotws/pilotschema/pilotvolume"
CUSTOMER_STREAM_PATH = f"{VOLUME_PATH}/customers"

# Target catalog and schema for Delta table
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"

# Checkpoint and schema locations
CHECKPOINT_PATH = f"{VOLUME_PATH}/_checkpoints/customers"
SCHEMA_PATH = f"{VOLUME_PATH}/_schemas/customers"

# Target table name
STREAMING_CUSTOMER_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.streaming_customers"

print("Configuration loaded successfully!")
print(f"Source: {CUSTOMER_STREAM_PATH}")
print(f"Target: {STREAMING_CUSTOMER_TABLE}")

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
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType, TimestampType

# Define schema for customers
customer_schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("country", StringType(), True),
    StructField("postal_code", StringType(), True),
    StructField("signup_date", DateType(), True),
    StructField("customer_segment", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("lifetime_value", DoubleType(), True),
    StructField("batch_timestamp", TimestampType(), True)
])

# Create streaming read with Auto Loader
# Let Auto Loader infer schema with evolution enabled
customers_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load(f"{CUSTOMER_STREAM_PATH}/batch_*")
)

# Add processing timestamp
customers_stream = customers_stream.withColumn("processing_timestamp", F.current_timestamp())

# Write to Delta table
customers_query = (customers_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)  # Process all available data then stop
    .table(STREAMING_CUSTOMER_TABLE)
)

print(f"✓ Customer stream started → {STREAMING_CUSTOMER_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Wait for Stream to Complete

# COMMAND ----------

import time

print("\nWaiting for stream to process data...")
print("Using trigger(availableNow=True) - will process all available data and stop.")
print()

max_wait_time = 300  # 5 minutes max wait
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
# MAGIC ## Verify Customer Table

# COMMAND ----------

print("=" * 80)
print("STREAMING CUSTOMERS TABLE SUMMARY")
print("=" * 80)

try:
    df = spark.table(STREAMING_CUSTOMER_TABLE)
    count = df.count()
    
    if count > 0:
        batch_info = df.agg(
            F.min("batch_timestamp").alias("first_batch"),
            F.max("batch_timestamp").alias("last_batch"),
            F.countDistinct("batch_timestamp").alias("num_batches")
        ).collect()[0]
        
        print(f"\nTable: {STREAMING_CUSTOMER_TABLE}")
        print(f"  Total Rows: {count}")
        print(f"  Number of Batches: {batch_info['num_batches']}")
        print(f"  First Batch: {batch_info['first_batch']}")
        print(f"  Last Batch: {batch_info['last_batch']}")
        
        # Show schema
        print(f"\nSchema:")
        df.printSchema()
    else:
        print(f"\nTable: {STREAMING_CUSTOMER_TABLE}")
        print(f"  Total Rows: 0 (No data loaded yet)")
        
except Exception as e:
    print(f"\nTable: {STREAMING_CUSTOMER_TABLE}")
    print(f"  Error: {str(e)[:200]}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Data

# COMMAND ----------

print("Latest Customer Records (Top 10):\n")

try:
    spark.table(STREAMING_CUSTOMER_TABLE).orderBy(F.desc("batch_timestamp")).select(
        "customer_id", 
        "first_name", 
        "last_name", 
        "email", 
        "customer_segment",
        "lifetime_value",
        "batch_timestamp",
        "processing_timestamp"
    ).show(10, truncate=False)
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Statistics

# COMMAND ----------

try:
    df = spark.table(STREAMING_CUSTOMER_TABLE)
    
    print("Customer Statistics:\n")
    
    # By segment
    print("Customers by Segment:")
    df.groupBy("customer_segment").count().orderBy(F.desc("count")).show()
    
    # By country
    print("Top 10 Countries:")
    df.groupBy("country").count().orderBy(F.desc("count")).show(10)
    
    # Lifetime value stats
    print("Lifetime Value Statistics:")
    df.select(
        F.avg("lifetime_value").alias("avg_ltv"),
        F.min("lifetime_value").alias("min_ltv"),
        F.max("lifetime_value").alias("max_ltv"),
        F.sum("lifetime_value").alias("total_ltv")
    ).show()
    
except Exception as e:
    print(f"Error generating statistics: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Continuous Streaming Mode (Optional)
# MAGIC
# MAGIC For continuous streaming, uncomment and run the code below:

# COMMAND ----------

"""
# Continuous streaming - checks for new files every 30 seconds
customers_stream_continuous = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .schema(customer_schema)
    .load(f"{CUSTOMER_STREAM_PATH}/batch_*")
    .withColumn("processing_timestamp", F.current_timestamp())
)

customers_query_continuous = (customers_stream_continuous.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", f"{CHECKPOINT_PATH}_continuous")
    .trigger(processingTime='30 seconds')
    .table(f"{STREAMING_CUSTOMER_TABLE}_continuous")
)

print("Continuous streaming started. This will run indefinitely until stopped.")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC **✓ What This Notebook Does:**
# MAGIC - Reads customer parquet files from Volume using Auto Loader
# MAGIC - Creates streaming Delta table with schema evolution
# MAGIC - Processes data incrementally (only new files)
# MAGIC - Adds processing_timestamp for observability
# MAGIC
# MAGIC **📊 Scheduling:**
# MAGIC - Schedule to run every 5-10 minutes using Databricks Workflows
# MAGIC - Auto Loader automatically picks up new files
# MAGIC - Checkpoint ensures exactly-once processing
