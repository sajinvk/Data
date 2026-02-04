# Databricks notebook source
# MAGIC %md
# MAGIC # Streaming Fake Data Generator
# MAGIC
# MAGIC This notebook generates incremental synthetic data for:
# MAGIC 1. Customer table (new signups)
# MAGIC 2. Product table (new products launched)
# MAGIC 3. Sales table (new transactions)
# MAGIC 4. Customer Reviews table (new reviews)
# MAGIC
# MAGIC The data is written to Databricks Volumes as parquet files to simulate a streaming data source.
# MAGIC This can be used with Auto Loader or Structured Streaming to create a real-time data pipeline.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration Parameters

# COMMAND ----------

# Streaming Configuration
ROWS_PER_BATCH = 10  # Number of rows to generate per batch for each table
BATCH_INTERVAL_SECONDS = 300  # 5 minutes (300 seconds)
MAX_BATCHES = 1  # Set to a number to limit batches, None for infinite

# Volume Configuration - Where to write the streaming data
VOLUME_PATH = "/Volumes/pilotws/pilotschema/pilotvolume"  # Update this to your volume path

# Separate folders for each table
CUSTOMER_STREAM_PATH = f"{VOLUME_PATH}/customers"
PRODUCT_STREAM_PATH = f"{VOLUME_PATH}/products"
SALES_STREAM_PATH = f"{VOLUME_PATH}/sales"
REVIEWS_STREAM_PATH = f"{VOLUME_PATH}/reviews"

# Source Tables Configuration (to get valid foreign keys and product info)
SOURCE_CATALOG = "pilotws"
SOURCE_SCHEMA = "pilotschema"
CUSTOMER_TABLE = f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.customers"
PRODUCT_TABLE = f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.products"
SALES_TABLE = f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.sales"
REVIEWS_TABLE = f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.customer_reviews"

# Industry for AI-generated reviews (should match your base data)
INDUSTRY = "health insurance"

# AI Model Configuration
AI_MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"  # Set to None to disable AI

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install and Import Libraries

# COMMAND ----------

# MAGIC %pip install faker

# COMMAND ----------

from faker import Faker
import random
from datetime import datetime, timedelta
import time
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType, TimestampType, BooleanType

# Initialize Faker with a dynamic seed for variety
fake = Faker()

print("Libraries imported successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Validation

# COMMAND ----------

# Create volume directories if they don't exist
dbutils.fs.mkdirs(CUSTOMER_STREAM_PATH)
dbutils.fs.mkdirs(PRODUCT_STREAM_PATH)
dbutils.fs.mkdirs(SALES_STREAM_PATH)
dbutils.fs.mkdirs(REVIEWS_STREAM_PATH)

print(f"✓ Volume directories created/verified:")
print(f"  - Customers: {CUSTOMER_STREAM_PATH}")
print(f"  - Products: {PRODUCT_STREAM_PATH}")
print(f"  - Sales: {SALES_STREAM_PATH}")
print(f"  - Reviews: {REVIEWS_STREAM_PATH}")

# COMMAND ----------

# Get maximum IDs from existing tables to ensure unique IDs
try:
    max_customer_id = spark.table(CUSTOMER_TABLE).agg(F.max("customer_id")).collect()[0][0] or 0
    max_product_id = spark.table(PRODUCT_TABLE).agg(F.max("product_id")).collect()[0][0] or 0
    max_sale_id = spark.table(SALES_TABLE).agg(F.max("sale_id")).collect()[0][0] or 0
    max_review_id = spark.table(REVIEWS_TABLE).agg(F.max("review_id")).collect()[0][0] or 0
    
    print(f"✓ Loaded existing ID ranges:")
    print(f"  - Max Customer ID: {max_customer_id}")
    print(f"  - Max Product ID: {max_product_id}")
    print(f"  - Max Sale ID: {max_sale_id}")
    print(f"  - Max Review ID: {max_review_id}")
    
    # Load valid customer and product IDs for foreign key references
    customer_ids = [row.customer_id for row in spark.table(CUSTOMER_TABLE).select('customer_id').collect()]
    product_ids = [row.product_id for row in spark.table(PRODUCT_TABLE).select('product_id').collect()]
    
    # Load product details for reviews
    product_details = spark.table(PRODUCT_TABLE).select('product_id', 'product_name', 'category').collect()
    product_details_dict = {row.product_id: {'name': row.product_name, 'category': row.category} for row in product_details}
    
    # Load product prices for sales
    product_prices = spark.table(PRODUCT_TABLE).select('product_id', 'price').collect()
    product_price_dict = {row.product_id: row.price for row in product_prices}
    
    print(f"  - Valid Customer IDs: {len(customer_ids)}")
    print(f"  - Valid Product IDs: {len(product_ids)}")
    
except Exception as e:
    print(f"⚠️  Warning: Could not load existing tables: {e}")
    print("Please run generate_fake_data.py first to create base tables.")
    dbutils.notebook.exit("Base tables not found. Run generate_fake_data.py first.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Incremental Data Generation Functions

# COMMAND ----------

def generate_customer_batch(start_id, num_customers):
    """
    Generate a batch of new customers
    """
    customers = []
    customer_segments = ['Premium', 'Standard', 'Basic', 'VIP']
    countries = ['Australia', 'United States', 'United Kingdom', 'Canada', 'New Zealand']
    
    for i in range(num_customers):
        customer = {
            'customer_id': start_id + i,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state(),
            'country': random.choice(countries),
            'postal_code': fake.postcode(),
            'signup_date': datetime.now().date(),  # Current date for new signups
            'customer_segment': random.choice(customer_segments),
            'age': random.randint(18, 80),
            'lifetime_value': round(random.uniform(100, 5000), 2),  # New customers start lower
            'batch_timestamp': datetime.now()
        }
        customers.append(customer)
    
    return customers

def generate_product_batch(start_id, num_products, industry):
    """
    Generate a batch of new products
    """
    products = []
    
    # Industry-specific product categories
    industry_categories = {
        'health insurance': {
            'Health Plans': ['Individual Plans', 'Family Plans', 'Medicare Plans', 'Medicaid Plans', 'Supplemental Plans'],
            'Dental Coverage': ['Basic Dental', 'Premium Dental', 'Orthodontic Plans', 'Preventive Care'],
            'Vision Coverage': ['Basic Vision', 'Premium Vision', 'Eye Care Plans', 'Contact Lens Plans'],
            'Life Insurance': ['Term Life', 'Whole Life', 'Universal Life', 'Final Expense'],
            'Wellness Programs': ['Fitness Programs', 'Mental Health', 'Nutrition Counseling', 'Chronic Care Management']
        },
        'electronics retailer': {
            'Electronics': ['Smartphones', 'Laptops', 'Tablets', 'Headphones', 'Cameras'],
            'Computing': ['Desktop PCs', 'Monitors', 'Keyboards', 'Mice', 'Printers'],
            'Smart Home': ['Security Cameras', 'Smart Speakers', 'Smart Lights', 'Thermostats']
        }
    }
    
    categories = industry_categories.get(industry.lower(), {
        'General': ['Products', 'Services', 'Plans', 'Packages', 'Solutions']
    })
    
    brands = ['Premier', 'Elite', 'Standard', 'Plus', 'Prime', 'Select', 'Choice', 'Essential']
    
    for i in range(num_products):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(categories[category])
        cost = round(random.uniform(5, 500), 2)
        price = round(cost * random.uniform(1.2, 3.0), 2)
        
        product = {
            'product_id': start_id + i,
            'product_name': f"{random.choice(brands)} {subcategory}",
            'category': category,
            'subcategory': subcategory,
            'brand': random.choice(brands),
            'description': f'Comprehensive {subcategory.lower()} coverage and benefits',
            'price': price,
            'cost': cost,
            'stock_quantity': random.randint(50, 1000),
            'weight_kg': round(random.uniform(0.1, 50), 2),
            'launch_date': datetime.now().date(),  # Current date for new products
            'is_active': True,
            'batch_timestamp': datetime.now()
        }
        products.append(product)
    
    return products

def generate_sales_batch(start_id, num_sales, customer_ids, product_ids, product_prices):
    """
    Generate a batch of new sales transactions
    """
    sales = []
    payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']
    statuses = ['Completed', 'Completed', 'Completed', 'Completed', 'Pending', 'Cancelled']
    
    for i in range(num_sales):
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 10)
        unit_price = product_prices.get(product_id, round(random.uniform(10, 1000), 2))
        discount_percent = random.choice([0, 0, 0, 5, 10, 15, 20])
        discount_amount = round(unit_price * quantity * discount_percent / 100, 2)
        total_amount = round(unit_price * quantity - discount_amount, 2)
        
        sale = {
            'sale_id': start_id + i,
            'customer_id': customer_id,
            'product_id': product_id,
            'sale_date': datetime.now(),  # Current timestamp for new sales
            'quantity': quantity,
            'unit_price': unit_price,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'total_amount': total_amount,
            'payment_method': random.choice(payment_methods),
            'status': random.choice(statuses),
            'shipping_address': fake.address(),
            'batch_timestamp': datetime.now()
        }
        sales.append(sale)
    
    return sales

def generate_ai_review(product_name, product_category, rating, model_endpoint=None):
    """
    Use Databricks AI to generate a product-specific review
    """
    if model_endpoint is None:
        return None
    
    clean_product_name = product_name.split('(Variant')[0].strip()
    
    sentiment_map = {
        1: "very negative (1 star)",
        2: "negative (2 stars)",
        3: "neutral/mixed (3 stars)",
        4: "positive (4 stars)",
        5: "very positive/enthusiastic (5 stars)"
    }
    
    sentiment = sentiment_map.get(rating, "neutral")
    
    prompt = f"""You are writing a realistic customer review for "{clean_product_name}" which is a {product_category} product.
Write a {sentiment} review that sounds like a real person wrote it.
The review should be 1-4 sentences (between 50-300 characters).
Include specific details about the product, coverage, service, or experience.
Use natural language - you can use contractions, varied sentence structure.
DO NOT include star ratings, emojis, or labels in the review text itself.
Return ONLY the review text."""
    
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        review_text = ai_response.strip()
        
        # Remove common AI response artifacts
        prefixes_to_remove = ["Here's a review:", "Here is a review:", "Review:", "Customer review:", '"', "'", "**", "*"]
        for prefix in prefixes_to_remove:
            review_text = review_text.replace(prefix, "").strip()
        
        if len(review_text) > 800:
            sentences = review_text[:800].split('.')
            review_text = '.'.join(sentences[:-1]) + '.' if len(sentences) > 1 else review_text[:797] + "..."
        
        if len(review_text.strip()) < 10:
            return None
            
        return review_text
        
    except Exception as e:
        return None

def generate_reviews_batch(start_id, num_reviews, customer_ids, product_ids, product_details, model_endpoint=None):
    """
    Generate a batch of new customer reviews
    """
    reviews = []
    
    for i in range(num_reviews):
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
        
        product_info = product_details.get(product_id, {'name': 'Unknown Product', 'category': 'General'})
        product_name = product_info['name']
        product_category = product_info['category']
        clean_product_name = product_name.split('(Variant')[0].strip()
        
        # Try AI-generated review
        review_text = generate_ai_review(product_name, product_category, rating, model_endpoint)
        
        # Fallback to templates if AI fails
        if not review_text:
            templates = {
                1: [
                    f"Very disappointed with {clean_product_name}. The coverage is inadequate and customer service was unhelpful.",
                    f"Not satisfied with {clean_product_name}. Claims process was complicated.",
                    f"Poor experience with {clean_product_name}. High premiums for minimal coverage."
                ],
                2: [
                    f"{clean_product_name} has some issues. Coverage is limited.",
                    f"Expected better from {clean_product_name}. The policy has too many exclusions.",
                    f"Somewhat disappointed with {clean_product_name}."
                ],
                3: [
                    f"{clean_product_name} is decent for the price. Coverage is adequate.",
                    f"Average experience with {clean_product_name}. Does what it's supposed to do.",
                    f"{clean_product_name} meets basic needs."
                ],
                4: [
                    f"Happy with {clean_product_name}! Good coverage and reasonable premiums.",
                    f"Satisfied with {clean_product_name}. Comprehensive benefits and responsive service.",
                    f"{clean_product_name} offers great value."
                ],
                5: [
                    f"Excellent choice! {clean_product_name} exceeded expectations.",
                    f"Absolutely love {clean_product_name}! Best decision I made.",
                    f"{clean_product_name} is outstanding. Premium benefits and quick approvals."
                ]
            }
            review_text = random.choice(templates[rating])
        
        review = {
            'review_id': start_id + i,
            'customer_id': customer_id,
            'product_id': product_id,
            'rating': rating,
            'review_text': review_text,
            'review_date': datetime.now(),  # Current timestamp for new reviews
            'helpful_count': random.randint(0, 10),  # New reviews start with lower helpful counts
            'verified_purchase': random.choice([True, True, True, False]),
            'batch_timestamp': datetime.now()
        }
        reviews.append(review)
    
    return reviews

# COMMAND ----------

# MAGIC %md
# MAGIC ## Streaming Data Generator Main Loop

# COMMAND ----------

def write_batch_to_volume(data, path, batch_number):
    """
    Write a batch of data to volume as parquet
    """
    if not data or len(data) == 0:
        return
    
    # Create DataFrame
    df = spark.createDataFrame(data)
    
    # Create subdirectory for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = f"batch_{batch_number:06d}_{timestamp}"
    full_path = f"{path}/{batch_dir}"
    
    # Write as parquet (this creates a directory with part files)
    df.coalesce(1).write.mode("overwrite").parquet(full_path)
    
    return full_path

def run_streaming_generator():
    """
    Main loop to generate and write streaming data
    """
    global max_customer_id, max_product_id, max_sale_id, max_review_id
    global customer_ids, product_ids, product_price_dict, product_details_dict
    
    batch_count = 0
    
    print("=" * 80)
    print("STREAMING DATA GENERATOR STARTED")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  - Rows per batch: {ROWS_PER_BATCH}")
    print(f"  - Batch interval: {BATCH_INTERVAL_SECONDS} seconds")
    print(f"  - Max batches: {MAX_BATCHES if MAX_BATCHES else 'Unlimited'}")
    print(f"  - Volume path: {VOLUME_PATH}")
    print(f"  - AI Model: {AI_MODEL_ENDPOINT if AI_MODEL_ENDPOINT else 'Disabled'}")
    print("=" * 80)
    print("\nPress Ctrl+C in the notebook to stop the generator.")
    print()
    
    try:
        while True:
            batch_count += 1
            batch_start_time = time.time()
            
            print(f"\n[Batch {batch_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 80)
            
            # Generate Customer Batch
            customer_batch = generate_customer_batch(max_customer_id + 1, ROWS_PER_BATCH)
            customer_path = write_batch_to_volume(customer_batch, CUSTOMER_STREAM_PATH, batch_count)
            max_customer_id += ROWS_PER_BATCH
            # Add new customers to the pool for future sales/reviews
            customer_ids.extend([c['customer_id'] for c in customer_batch])
            print(f"  ✓ Customers: {ROWS_PER_BATCH} rows → {customer_path}")
            
            # Generate Product Batch
            product_batch = generate_product_batch(max_product_id + 1, ROWS_PER_BATCH, INDUSTRY)
            product_path = write_batch_to_volume(product_batch, PRODUCT_STREAM_PATH, batch_count)
            max_product_id += ROWS_PER_BATCH
            # Add new products to the pool
            for p in product_batch:
                product_ids.append(p['product_id'])
                product_price_dict[p['product_id']] = p['price']
                product_details_dict[p['product_id']] = {'name': p['product_name'], 'category': p['category']}
            print(f"  ✓ Products: {ROWS_PER_BATCH} rows → {product_path}")
            
            # Generate Sales Batch (more sales than new customers/products)
            sales_batch_size = ROWS_PER_BATCH * 5  # 5x more sales
            sales_batch = generate_sales_batch(max_sale_id + 1, sales_batch_size, customer_ids, product_ids, product_price_dict)
            sales_path = write_batch_to_volume(sales_batch, SALES_STREAM_PATH, batch_count)
            max_sale_id += sales_batch_size
            print(f"  ✓ Sales: {sales_batch_size} rows → {sales_path}")
            
            # Generate Reviews Batch (fewer reviews than sales)
            reviews_batch_size = ROWS_PER_BATCH * 3  # 3x reviews
            reviews_batch = generate_reviews_batch(max_review_id + 1, reviews_batch_size, customer_ids, product_ids, product_details_dict, AI_MODEL_ENDPOINT)
            reviews_path = write_batch_to_volume(reviews_batch, REVIEWS_STREAM_PATH, batch_count)
            max_review_id += reviews_batch_size
            print(f"  ✓ Reviews: {reviews_batch_size} rows → {reviews_path}")
            
            batch_duration = time.time() - batch_start_time
            print(f"\n  Batch completed in {batch_duration:.2f} seconds")
            
            # Check if we've reached max batches
            if MAX_BATCHES and batch_count >= MAX_BATCHES:
                print(f"\n✓ Reached maximum of {MAX_BATCHES} batches. Stopping.")
                break
            
            # Wait for next batch
            sleep_time = max(0, BATCH_INTERVAL_SECONDS - batch_duration)
            if sleep_time > 0:
                print(f"  Sleeping for {sleep_time:.2f} seconds until next batch...")
                time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Generator stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 80)
        print("STREAMING DATA GENERATOR STOPPED")
        print("=" * 80)
        print(f"Total batches generated: {batch_count}")
        print(f"Total new records created:")
        print(f"  - Customers: {batch_count * ROWS_PER_BATCH}")
        print(f"  - Products: {batch_count * ROWS_PER_BATCH}")
        print(f"  - Sales: {batch_count * ROWS_PER_BATCH * 5}")
        print(f"  - Reviews: {batch_count * ROWS_PER_BATCH * 3}")
        print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Start the Generator
# MAGIC
# MAGIC Run the cell below to start generating streaming data.
# MAGIC
# MAGIC **Note:** This will run continuously until you stop it or reach MAX_BATCHES.

# COMMAND ----------

# Start the streaming data generator
run_streaming_generator()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Generated Files

# COMMAND ----------

def count_parquet_files(path):
    """Count parquet batch directories in a path"""
    try:
        files = dbutils.fs.ls(path)
        # Filter for batch directories or parquet files
        batch_dirs = [f for f in files if f.name.startswith('batch_')]
        return batch_dirs
    except Exception as e:
        return []

print("Files generated in each stream path:\n")

print(f"Customers: {CUSTOMER_STREAM_PATH}")
customer_files = count_parquet_files(CUSTOMER_STREAM_PATH)
print(f"  Total batches: {len(customer_files)}")
if customer_files:
    for f in customer_files[:5]:  # Show first 5
        print(f"    {f.name}")
else:
    print("    No files generated yet. Run the streaming generator first.")

print(f"\nProducts: {PRODUCT_STREAM_PATH}")
product_files = count_parquet_files(PRODUCT_STREAM_PATH)
print(f"  Total batches: {len(product_files)}")
if product_files:
    for f in product_files[:5]:
        print(f"    {f.name}")
else:
    print("    No files generated yet. Run the streaming generator first.")

print(f"\nSales: {SALES_STREAM_PATH}")
sales_files = count_parquet_files(SALES_STREAM_PATH)
print(f"  Total batches: {len(sales_files)}")
if sales_files:
    for f in sales_files[:5]:
        print(f"    {f.name}")
else:
    print("    No files generated yet. Run the streaming generator first.")

print(f"\nReviews: {REVIEWS_STREAM_PATH}")
reviews_files = count_parquet_files(REVIEWS_STREAM_PATH)
print(f"  Total batches: {len(reviews_files)}")
if reviews_files:
    for f in reviews_files[:5]:
        print(f"    {f.name}")
else:
    print("    No files generated yet. Run the streaming generator first.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Data from Streams

# COMMAND ----------

def read_and_display_stream(path, name):
    """Read and display sample data from stream if files exist"""
    try:
        files = count_parquet_files(path)
        if not files:
            print(f"{name}: No data generated yet. Run the streaming generator first.\n")
            return
        
        # Read all parquet files/directories under the path
        # Spark can read parquet directories automatically
        df = spark.read.parquet(f"{path}/batch_*")
        row_count = df.count()
        print(f"{name} ({row_count} total rows):")
        df.orderBy(F.desc("batch_timestamp")).show(5, truncate=False)
        print()
        
    except Exception as e:
        print(f"{name}: Error reading data - {str(e)[:200]}\n")

# Read and display sample data from each stream
read_and_display_stream(CUSTOMER_STREAM_PATH, "Sample Customer Data from Stream")
read_and_display_stream(PRODUCT_STREAM_PATH, "Sample Product Data from Stream")
read_and_display_stream(SALES_STREAM_PATH, "Sample Sales Data from Stream")
read_and_display_stream(REVIEWS_STREAM_PATH, "Sample Reviews Data from Stream")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps: Setup Streaming Tables
# MAGIC
# MAGIC Use these paths with Auto Loader or Structured Streaming to create live tables:
# MAGIC
# MAGIC ```python
# MAGIC # Example 1: Read streaming data with Auto Loader
# MAGIC spark.readStream \
# MAGIC     .format("cloudFiles") \
# MAGIC     .option("cloudFiles.format", "parquet") \
# MAGIC     .option("cloudFiles.schemaLocation", f"{VOLUME_PATH}/_schema/customers") \
# MAGIC     .load(f"{CUSTOMER_STREAM_PATH}/batch_*") \
# MAGIC     .writeStream \
# MAGIC     .option("checkpointLocation", f"{VOLUME_PATH}/_checkpoint/customers") \
# MAGIC     .option("mergeSchema", "true") \
# MAGIC     .table("streaming_customers")
# MAGIC
# MAGIC # Example 2: Simple structured streaming
# MAGIC spark.readStream \
# MAGIC     .format("parquet") \
# MAGIC     .schema("customer_id INT, first_name STRING, ...") \
# MAGIC     .load(f"{CUSTOMER_STREAM_PATH}/batch_*") \
# MAGIC     .writeStream \
# MAGIC     .format("delta") \
# MAGIC     .option("checkpointLocation", f"{VOLUME_PATH}/_checkpoint/customers") \
# MAGIC     .table("streaming_customers")
# MAGIC ```
# MAGIC
# MAGIC Or schedule this notebook to run periodically using Databricks Workflows.
# MAGIC
# MAGIC **Scheduling Recommendations:**
# MAGIC - Create a Databricks Workflow/Job
# MAGIC - Set MAX_BATCHES = 1 or 2 for scheduled runs
# MAGIC - Schedule to run every 5-10 minutes
# MAGIC - This simulates continuous streaming without keeping notebook running
