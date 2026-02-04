# Databricks notebook source
# MAGIC %md
# MAGIC # Auto Loader for Streaming Customer Reviews
# MAGIC
# MAGIC This notebook uses Databricks Auto Loader to read streaming customer review data from the Volume
# MAGIC and create a live Delta table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Volume paths where streaming data is written
VOLUME_PATH = "/Volumes/pilotws/pilotschema/pilotvolume"
REVIEWS_STREAM_PATH = f"{VOLUME_PATH}/reviews"

# Target catalog and schema for Delta table
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"

# Checkpoint and schema locations
CHECKPOINT_PATH = f"{VOLUME_PATH}/_checkpoints/reviews"
SCHEMA_PATH = f"{VOLUME_PATH}/_schemas/reviews"

# Target table name
STREAMING_REVIEWS_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.streaming_reviews"

print("Configuration loaded successfully!")
print(f"Source: {REVIEWS_STREAM_PATH}")
print(f"Target: {STREAMING_REVIEWS_TABLE}")

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
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType

# Define schema for reviews
reviews_schema = StructType([
    StructField("review_id", IntegerType(), False),
    StructField("customer_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("rating", IntegerType(), True),
    StructField("review_text", StringType(), True),
    StructField("review_date", TimestampType(), True),
    StructField("helpful_count", IntegerType(), True),
    StructField("verified_purchase", BooleanType(), True),
    StructField("batch_timestamp", TimestampType(), True)
])

# Create streaming read with Auto Loader
# Let Auto Loader infer schema with evolution enabled
reviews_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", SCHEMA_PATH)
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load(f"{REVIEWS_STREAM_PATH}/batch_*")
)

# Add processing timestamp and calculated fields
reviews_stream = (reviews_stream
    .withColumn("processing_timestamp", F.current_timestamp())
    .withColumn("review_length", F.length("review_text"))
    .withColumn("sentiment_category", 
        F.when(F.col("rating") >= 4, "Positive")
         .when(F.col("rating") == 3, "Neutral")
         .otherwise("Negative")
    )
)

# Write to Delta table
reviews_query = (reviews_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .table(STREAMING_REVIEWS_TABLE)
)

print(f"✓ Reviews stream started → {STREAMING_REVIEWS_TABLE}")

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
# MAGIC ## Verify Reviews Table

# COMMAND ----------

print("=" * 80)
print("STREAMING REVIEWS TABLE SUMMARY")
print("=" * 80)

try:
    df = spark.table(STREAMING_REVIEWS_TABLE)
    count = df.count()
    
    if count > 0:
        batch_info = df.agg(
            F.min("batch_timestamp").alias("first_batch"),
            F.max("batch_timestamp").alias("last_batch"),
            F.countDistinct("batch_timestamp").alias("num_batches")
        ).collect()[0]
        
        print(f"\nTable: {STREAMING_REVIEWS_TABLE}")
        print(f"  Total Rows: {count}")
        print(f"  Number of Batches: {batch_info['num_batches']}")
        print(f"  First Batch: {batch_info['first_batch']}")
        print(f"  Last Batch: {batch_info['last_batch']}")
        
        print(f"\nSchema:")
        df.printSchema()
    else:
        print(f"\nTable: {STREAMING_REVIEWS_TABLE}")
        print(f"  Total Rows: 0 (No data loaded yet)")
        
except Exception as e:
    print(f"\nTable: {STREAMING_REVIEWS_TABLE}")
    print(f"  Error: {str(e)[:200]}")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Data

# COMMAND ----------

print("Latest Review Records (Top 10):\n")

try:
    spark.table(STREAMING_REVIEWS_TABLE).orderBy(F.desc("batch_timestamp")).select(
        "review_id",
        "customer_id",
        "product_id",
        "rating",
        "review_text",
        "sentiment_category",
        "verified_purchase",
        "batch_timestamp"
    ).show(10, truncate=False)
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Statistics

# COMMAND ----------

try:
    df = spark.table(STREAMING_REVIEWS_TABLE)
    
    print("Review Statistics:\n")
    
    # Rating distribution
    print("Rating Distribution:")
    df.groupBy("rating").count().orderBy("rating").show()
    
    # Sentiment breakdown
    print("Sentiment Breakdown:")
    df.groupBy("sentiment_category").agg(
        F.count("*").alias("review_count"),
        F.avg("rating").alias("avg_rating")
    ).orderBy(F.desc("review_count")).show()
    
    # Verified vs Unverified
    print("Verified Purchase Status:")
    df.groupBy("verified_purchase").agg(
        F.count("*").alias("review_count"),
        F.avg("rating").alias("avg_rating")
    ).show()
    
    # Overall metrics
    print("Overall Review Metrics:")
    df.agg(
        F.count("*").alias("total_reviews"),
        F.avg("rating").alias("avg_rating"),
        F.avg("helpful_count").alias("avg_helpful_count"),
        F.avg("review_length").alias("avg_review_length")
    ).show()
    
    # Top rated products (if joined with products table)
    print("Most Reviewed Products:")
    df.groupBy("product_id").agg(
        F.count("*").alias("review_count"),
        F.avg("rating").alias("avg_rating")
    ).orderBy(F.desc("review_count")).show(10)
    
except Exception as e:
    print(f"Error generating statistics: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## AI Sentiment Analysis (Optional)
# MAGIC
# MAGIC Uncomment to run AI sentiment analysis on reviews:

# COMMAND ----------

"""
# Run AI sentiment analysis on new reviews
# Requires AI_QUERY function to be available

df_with_sentiment = spark.table(STREAMING_REVIEWS_TABLE)

# Add AI sentiment
df_with_sentiment = df_with_sentiment.withColumn(
    "ai_sentiment",
    F.expr("ai_analyze_sentiment(review_text)")
)

# Display results
df_with_sentiment.select(
    "review_id",
    "rating",
    "review_text",
    "sentiment_category",
    "ai_sentiment"
).show(10, truncate=False)
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC **✓ What This Notebook Does:**
# MAGIC - Reads review parquet files from Volume using Auto Loader
# MAGIC - Creates streaming Delta table with schema evolution
# MAGIC - Adds sentiment categorization (Positive/Neutral/Negative)
# MAGIC - Calculates review length for analysis
# MAGIC - Processes data incrementally (only new files)
# MAGIC
# MAGIC **📊 Scheduling:**
# MAGIC - Schedule to run every 5-10 minutes using Databricks Workflows
# MAGIC - Auto Loader automatically picks up new files
# MAGIC - Perfect for sentiment analysis dashboards
# MAGIC
# MAGIC **🔗 Next Steps:**
# MAGIC - Run AI sentiment analysis on review_text
# MAGIC - Join with products and customers for deeper insights
# MAGIC - Create alerts for negative reviews
