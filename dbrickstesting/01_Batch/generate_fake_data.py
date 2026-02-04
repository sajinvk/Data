# Databricks notebook source
# MAGIC %md
# MAGIC # Fake Data Generator for Customer, Product, Sales, and Reviews
# MAGIC
# MAGIC This notebook generates synthetic data for:
# MAGIC 1. Customer table
# MAGIC 2. Product table
# MAGIC 3. Sales table
# MAGIC 4. Customer Reviews table
# MAGIC
# MAGIC All tables have primary keys and foreign key relationships for joins and dashboard creation.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration Parameters
# MAGIC Set the number of rows for each table and the target catalog/schema

# COMMAND ----------

# Configuration Variables - Modify these as needed
NUM_CUSTOMERS = 20000
NUM_PRODUCTS = 2000
NUM_SALES = 50000
NUM_REVIEWS = 30000

# Target catalog and schema
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"

# Industry/Company for product generation
# Examples: "retail fashion", "electronics retailer", "home improvement", "grocery store", "sporting goods"
INDUSTRY = "health insurance"

# AI Model Configuration
# Set to None to skip AI generation and use fallback data generation
# Common model options (check your workspace for available models):
# - "databricks-meta-llama-3-1-70b-instruct"
# - "databricks-llama-2-70b-chat" 
# - "databricks-mixtral-8x7b-instruct"
# - "databricks-dbrx-instruct"
# To find available models, run: spark.sql("SHOW MODELS IN system.ai").show()
AI_MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"  # Set to None to disable AI generation

# Full table paths
CUSTOMER_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.customers"
PRODUCT_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.products"
SALES_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.sales"
REVIEWS_TABLE = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.customer_reviews"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install and Import Required Libraries

# COMMAND ----------

# Install Faker library for generating realistic fake data
%pip install faker

# COMMAND ----------

# Import required libraries
from faker import Faker
import random
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType, TimestampType
import pyspark.sql.functions as F

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)

print("Libraries imported successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Generate Customer Data

# COMMAND ----------

def generate_customers(num_customers):
    """
    Generate fake customer data with realistic attributes
    """
    customers = []
    customer_segments = ['Premium', 'Standard', 'Basic', 'VIP']
    countries = ['Australia', 'United States', 'United Kingdom', 'Canada', 'New Zealand']
    
    for i in range(1, num_customers + 1):
        customer = {
            'customer_id': i,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state(),
            'country': random.choice(countries),
            'postal_code': fake.postcode(),
            'signup_date': fake.date_between(start_date='-5y', end_date='today'),
            'customer_segment': random.choice(customer_segments),
            'age': random.randint(18, 80),
            'lifetime_value': round(random.uniform(100, 50000), 2)
        }
        customers.append(customer)
    
    return customers

# Generate customer data
print(f"Generating {NUM_CUSTOMERS} customers...")
customer_data = generate_customers(NUM_CUSTOMERS)

# Create DataFrame
customer_df = spark.createDataFrame(customer_data)

# Show sample data
print("\nSample Customer Data:")
customer_df.show(5, truncate=False)
print(f"Total customers created: {customer_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Generate Product Data Using AI

# COMMAND ----------

# MAGIC %md
# MAGIC ### Check Available AI Models (Optional)
# MAGIC Uncomment the cell below to see what AI models are available in your workspace

# COMMAND ----------

# Uncomment to check available AI serving endpoints
# display(spark.sql("SHOW ENDPOINTS"))

# COMMAND ----------

def generate_industry_taxonomy_with_ai(industry, model_endpoint=None):
    """
    Use Databricks AI to generate industry-relevant categories and subcategories
    """
    if model_endpoint is None:
        return None
    
    print(f"Using AI to generate category taxonomy for {industry} industry...")
    
    prompt = f"""Generate a JSON object with product categories and subcategories for a {industry} company.
Provide 4-6 main categories, each with 4-6 subcategories.
Return ONLY valid JSON format, no other text.
Format: {{"Category1": ["Subcategory1", "Subcategory2", ...], "Category2": ["Subcategory1", ...]}}
Example for electronics: {{"Consumer Electronics": ["Smartphones", "Laptops", "Tablets"], "Audio": ["Headphones", "Speakers"]}}"""
    
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        # Parse the AI response and clean it
        import json
        # Remove markdown code blocks if present
        clean_response = ai_response.strip()
        if clean_response.startswith('```'):
            lines = clean_response.split('\n')
            clean_response = '\n'.join([l for l in lines if not l.startswith('```')])
        
        taxonomy = json.loads(clean_response)
        print(f"✓ AI generated {len(taxonomy)} categories")
        return taxonomy
        
    except Exception as e:
        print(f"Note: Category taxonomy AI generation failed: {str(e)[:100]}")
        return None

def generate_product_catalog_with_ai(industry, num_products, model_endpoint=None):
    """
    Use Databricks AI to generate a product catalog for the specified industry
    """
    if model_endpoint is None:
        print("AI model endpoint not configured. Using fallback product generation.")
        return [], None
    
    print(f"Using Databricks AI ({model_endpoint}) to generate product catalog for industry: {industry}")
    
    # First, generate the category taxonomy
    taxonomy = generate_industry_taxonomy_with_ai(industry, model_endpoint)
    
    # Generate product catalog
    prompt = f"""Generate a JSON array of {min(num_products, 50)} realistic products for a {industry} company.
For each product, provide: product_name, category, subcategory, brand, and a brief description.
Make the products specific and realistic for this industry.
Return ONLY valid JSON array format, no other text or markdown.
Format: [{{"product_name": "Product Name", "category": "Main Category", "subcategory": "Sub Category", "brand": "Brand Name", "description": "Brief description"}}]"""
    
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        # Parse the AI response
        import json
        # Clean response
        clean_response = ai_response.strip()
        if clean_response.startswith('```'):
            lines = clean_response.split('\n')
            clean_response = '\n'.join([l for l in lines if not l.startswith('```')])
        
        ai_products = json.loads(clean_response)
        print(f"✓ AI generated {len(ai_products)} products")
        
    except Exception as e:
        print(f"Note: Product AI generation encountered an issue: {str(e)[:200]}")
        print("Falling back to default product generation...")
        ai_products = []
    
    return ai_products, taxonomy

def generate_products(num_products, industry, model_endpoint=None):
    """
    Generate fake product data with AI-generated product names and attributes
    """
    products = []
    
    # Get AI-generated product catalog and taxonomy
    ai_products, taxonomy = generate_product_catalog_with_ai(industry, num_products, model_endpoint)
    
    # If we have AI products, use them; otherwise generate generic ones
    if ai_products and len(ai_products) > 0:
        # Use AI-generated products and repeat if needed
        for i in range(1, num_products + 1):
            ai_product = ai_products[(i - 1) % len(ai_products)]
            cost = round(random.uniform(5, 500), 2)
            price = round(cost * random.uniform(1.2, 3.0), 2)
            
            # Add variation to repeated products
            product_name = ai_product.get('product_name', f'Product {i}')
            if i > len(ai_products):
                product_name += f" (Variant {i // len(ai_products) + 1})"
            
            product = {
                'product_id': i,
                'product_name': product_name,
                'category': ai_product.get('category', 'General'),
                'subcategory': ai_product.get('subcategory', 'Other'),
                'brand': ai_product.get('brand', 'Generic'),
                'description': ai_product.get('description', ''),
                'price': price,
                'cost': cost,
                'stock_quantity': random.randint(0, 1000),
                'weight_kg': round(random.uniform(0.1, 50), 2),
                'launch_date': fake.date_between(start_date='-3y', end_date='today'),
                'is_active': random.choice([True, True, True, False])
            }
            products.append(product)
    else:
        # Fallback: Use AI taxonomy if available, otherwise hardcoded
        print("Using fallback product generation...")
        
        # Try to use AI-generated taxonomy first
        if taxonomy and len(taxonomy) > 0:
            print(f"Using AI-generated taxonomy with {len(taxonomy)} categories")
            categories = taxonomy
        else:
            # Industry-specific product categories (hardcoded fallback)
            print("Using hardcoded taxonomy for fallback")
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
                    'Home Entertainment': ['TVs', 'Sound Systems', 'Gaming Consoles', 'Streaming Devices'],
                    'Computing': ['Desktop PCs', 'Monitors', 'Keyboards', 'Mice', 'Printers'],
                    'Smart Home': ['Security Cameras', 'Smart Speakers', 'Smart Lights', 'Thermostats'],
                    'Accessories': ['Cables', 'Cases', 'Screen Protectors', 'Chargers']
                },
                'retail fashion': {
                    'Clothing': ['Mens Wear', 'Womens Wear', 'Kids Wear', 'Activewear', 'Outerwear'],
                    'Footwear': ['Casual Shoes', 'Formal Shoes', 'Athletic Shoes', 'Boots', 'Sandals'],
                    'Accessories': ['Bags', 'Belts', 'Hats', 'Scarves', 'Jewelry'],
                    'Seasonal': ['Summer Collection', 'Winter Collection', 'Fall Collection', 'Spring Collection']
                },
                'default': {
                    'General': ['Products', 'Services', 'Plans', 'Packages', 'Solutions'],
                    'Premium': ['Premium Products', 'Deluxe Services', 'Elite Plans'],
                    'Standard': ['Standard Products', 'Basic Services', 'Regular Plans']
                }
            }
            
            # Get categories for the industry (or use default)
            categories = industry_categories.get(industry.lower(), industry_categories['default'])
        
        brands = ['Premier', 'Elite', 'Standard', 'Plus', 'Prime', 'Select', 'Choice', 'Essential']
        
        for i in range(1, num_products + 1):
            category = random.choice(list(categories.keys()))
            subcategory = random.choice(categories[category])
            cost = round(random.uniform(5, 500), 2)
            price = round(cost * random.uniform(1.2, 3.0), 2)
            
            product = {
                'product_id': i,
                'product_name': f"{random.choice(brands)} {subcategory}",
                'category': category,
                'subcategory': subcategory,
                'brand': random.choice(brands),
                'description': f'Comprehensive {subcategory.lower()} coverage and benefits',
                'price': price,
                'cost': cost,
                'stock_quantity': random.randint(0, 1000),
                'weight_kg': round(random.uniform(0.1, 50), 2),
                'launch_date': fake.date_between(start_date='-3y', end_date='today'),
                'is_active': random.choice([True, True, True, False])
            }
            products.append(product)
    
    return products

# Generate product data
print(f"Generating {NUM_PRODUCTS} products for {INDUSTRY}...")
product_data = generate_products(NUM_PRODUCTS, INDUSTRY, AI_MODEL_ENDPOINT)

# Create DataFrame
product_df = spark.createDataFrame(product_data)

# Show sample data
print("\nSample Product Data:")
product_df.show(5, truncate=False)
print(f"Total products created: {product_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Generate Sales Data with Valid Foreign Keys

# COMMAND ----------

def generate_sales(num_sales, customer_ids, product_ids):
    """
    Generate fake sales transactions with VALID foreign keys to customers and products
    """
    sales = []
    payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']
    statuses = ['Completed', 'Completed', 'Completed', 'Completed', 'Pending', 'Cancelled']
    
    for i in range(1, num_sales + 1):
        # Ensure we only reference existing customers and products
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(10, 1000), 2)  # Placeholder, will be replaced
        discount_percent = random.choice([0, 0, 0, 5, 10, 15, 20])
        
        sale = {
            'sale_id': i,
            'customer_id': customer_id,
            'product_id': product_id,
            'sale_date': fake.date_time_between(start_date='-2y', end_date='now'),
            'quantity': quantity,
            'unit_price': unit_price,
            'discount_percent': discount_percent,
            'payment_method': random.choice(payment_methods),
            'status': random.choice(statuses),
            'shipping_address': fake.address()
        }
        sales.append(sale)
    
    return sales

# Get valid customer and product IDs
customer_ids = [row.customer_id for row in customer_df.select('customer_id').collect()]
product_ids = [row.product_id for row in product_df.select('product_id').collect()]

print(f"Valid customer IDs: {len(customer_ids)}")
print(f"Valid product IDs: {len(product_ids)}")

# Generate sales data with valid foreign keys
print(f"Generating {NUM_SALES} sales transactions...")
sales_data = generate_sales(NUM_SALES, customer_ids, product_ids)

# Create DataFrame
sales_df = spark.createDataFrame(sales_data)

# Join with product to get actual prices
sales_df = sales_df.drop('unit_price')
sales_df = sales_df.join(
    product_df.select('product_id', F.col('price').alias('unit_price')),
    'product_id',
    'left'
)

# Calculate amounts with actual product prices
sales_df = sales_df.withColumn(
    'discount_amount',
    F.round(F.col('unit_price') * F.col('quantity') * F.col('discount_percent') / 100, 2)
)
sales_df = sales_df.withColumn(
    'total_amount',
    F.round(F.col('unit_price') * F.col('quantity') - F.col('discount_amount'), 2)
)

# Verify foreign key integrity
print("\nVerifying Sales foreign keys...")
invalid_customers = sales_df.join(customer_df, 'customer_id', 'left_anti').count()
invalid_products = sales_df.join(product_df, 'product_id', 'left_anti').count()
print(f"Sales with invalid customer_id: {invalid_customers}")
print(f"Sales with invalid product_id: {invalid_products}")

# Show sample data
print("\nSample Sales Data:")
sales_df.show(5, truncate=False)
print(f"Total sales created: {sales_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Generate Customer Reviews with AI-Generated Product-Specific Content

# COMMAND ----------

def generate_ai_review(product_name, product_category, rating, model_endpoint=None):
    """
    Use Databricks AI to generate a product-specific review based on rating
    """
    if model_endpoint is None:
        # Return None to use fallback templates
        return None
    
    # Clean product name - remove variant markers and extra text
    clean_product_name = product_name.split('(Variant')[0].strip()
    
    sentiment_map = {
        1: "very negative (1 star)",
        2: "negative (2 stars)",
        3: "neutral/mixed (3 stars)",
        4: "positive (4 stars)",
        5: "very positive/enthusiastic (5 stars)"
    }
    
    sentiment = sentiment_map.get(rating, "neutral")
    
    # More detailed prompt for realistic reviews
    prompt = f"""You are writing a realistic customer review for "{clean_product_name}" which is a {product_category} product.
Write a {sentiment} review that sounds like a real person wrote it.
The review should be 1-4 sentences (between 50-300 characters).
Include specific details about the product, coverage, service, or experience.
Use natural language - you can use contractions, varied sentence structure.
DO NOT include star ratings, emojis, or labels in the review text itself.
Return ONLY the review text."""
    
    # Escape single quotes in prompt for SQL
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        # Clean up the response - remove common prefixes and quotes
        review_text = ai_response.strip()
        
        # Remove common AI response artifacts
        prefixes_to_remove = [
            "Here's a review:",
            "Here is a review:",
            "Review:",
            "Customer review:",
            '"', "'", "**", "*"
        ]
        for prefix in prefixes_to_remove:
            review_text = review_text.replace(prefix, "").strip()
        
        # Ensure it's not too long (for dashboard display)
        if len(review_text) > 800:
            # Find last complete sentence within limit
            sentences = review_text[:800].split('.')
            if len(sentences) > 1:
                review_text = '.'.join(sentences[:-1]) + '.'
            else:
                review_text = review_text[:797] + "..."
        
        # Make sure we have actual content
        if len(review_text.strip()) < 10:
            return None  # Trigger fallback
            
        return review_text
        
    except Exception as e:
        print(f"    AI review generation error: {str(e)[:100]}")
        return None  # Return None to use fallback

def generate_reviews_with_ai(num_reviews, customer_ids, product_data, model_endpoint=None):
    """
    Generate customer reviews with AI-generated product-specific content
    Ensures valid foreign keys to customers and products
    All reviews use AI when endpoint is available for consistency and quality
    """
    reviews = []
    product_ids = [p['product_id'] for p in product_data]
    
    if model_endpoint:
        print(f"Generating {num_reviews} AI-powered reviews using {model_endpoint}...")
        print(f"This may take a few minutes for large datasets...")
    else:
        print(f"Generating {num_reviews} reviews using templates (AI disabled)...")
    
    # Progress tracking
    progress_interval = max(1, num_reviews // 10)  # Show progress every 10%
    
    for i in range(1, num_reviews + 1):
        # Ensure valid foreign keys
        customer_id = random.choice(customer_ids)
        product = random.choice(product_data)
        product_id = product['product_id']
        
        # Generate rating (skewed toward positive)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
        
        # Clean product name for better reviews
        clean_product_name = product['product_name'].split('(Variant')[0].strip()
        
        # Try to generate AI review if endpoint is available
        review_text = None
        if model_endpoint:
            review_text = generate_ai_review(
                product['product_name'],
                product['category'],
                rating,
                model_endpoint
            )
        
        # Fallback to realistic templates if AI fails or is disabled
        if not review_text:
            templates = {
                1: [
                    f"Very disappointed with {clean_product_name}. The coverage is inadequate and customer service was unhelpful. Would not recommend.",
                    f"Not satisfied with {clean_product_name}. Claims process was complicated and benefits don't match what was advertised.",
                    f"Poor experience with {clean_product_name}. High premiums for minimal coverage. Looking for alternatives.",
                    f"{clean_product_name} fell short of expectations. Denied my claim without clear explanation. Frustrating experience."
                ],
                2: [
                    f"{clean_product_name} has some issues. Coverage is limited and premium increases were unexpected.",
                    f"Expected better from {clean_product_name}. The policy has too many exclusions for the price point.",
                    f"Somewhat disappointed with {clean_product_name}. Customer service response time is slow.",
                    f"{clean_product_name} is below average. Benefits are okay but the claims process needs improvement."
                ],
                3: [
                    f"{clean_product_name} is decent for the price. Coverage is adequate but nothing exceptional.",
                    f"Average experience with {clean_product_name}. Does what it's supposed to do, no major complaints.",
                    f"{clean_product_name} meets basic needs. Not the best but not the worst option available.",
                    f"Neutral about {clean_product_name}. Some good features, some areas need improvement. Fair value overall."
                ],
                4: [
                    f"Happy with {clean_product_name}! Good coverage and reasonable premiums. Claim was processed smoothly.",
                    f"Satisfied with {clean_product_name}. Comprehensive benefits and responsive customer service. Would recommend.",
                    f"{clean_product_name} offers great value. Easy to understand policy and helpful support team.",
                    f"Good experience with {clean_product_name}. Peace of mind knowing I'm well covered. Worth the investment."
                ],
                5: [
                    f"Excellent choice! {clean_product_name} exceeded expectations. Comprehensive coverage, easy claims, and fantastic customer service.",
                    f"Absolutely love {clean_product_name}! Best decision I made. Saved me thousands on medical expenses and the process was seamless.",
                    f"{clean_product_name} is outstanding. Premium benefits, quick claim approvals, and supportive team. Highly recommend!",
                    f"Could not be happier with {clean_product_name}. Excellent coverage that truly delivers. Five stars all the way!"
                ]
            }
            review_text = random.choice(templates[rating])
        
        review = {
            'review_id': i,
            'customer_id': customer_id,
            'product_id': product_id,
            'rating': rating,
            'review_text': review_text,
            'review_date': fake.date_time_between(start_date='-2y', end_date='now'),
            'helpful_count': random.randint(0, 100),
            'verified_purchase': random.choice([True, True, True, False])
        }
        reviews.append(review)
        
        # Show progress
        if i % progress_interval == 0:
            print(f"  Progress: {i}/{num_reviews} reviews generated ({int(i/num_reviews*100)}%)")
    
    return reviews

# Prepare product data for review generation
product_data_list = product_df.select('product_id', 'product_name', 'category').collect()
product_data_dicts = [
    {
        'product_id': row.product_id,
        'product_name': row.product_name,
        'category': row.category
    }
    for row in product_data_list
]

# Generate review data with valid foreign keys
print(f"Generating {NUM_REVIEWS} customer reviews...")
review_data = generate_reviews_with_ai(NUM_REVIEWS, customer_ids, product_data_dicts, AI_MODEL_ENDPOINT)

# Create DataFrame
reviews_df = spark.createDataFrame(review_data)

# Verify foreign key integrity
print("\nVerifying Review foreign keys...")
invalid_customers = reviews_df.join(customer_df, 'customer_id', 'left_anti').count()
invalid_products = reviews_df.join(product_df, 'product_id', 'left_anti').count()
print(f"Reviews with invalid customer_id: {invalid_customers}")
print(f"Reviews with invalid product_id: {invalid_products}")

# Show sample data
print("\nSample Review Data:")
reviews_df.show(5, truncate=False)
print(f"Total reviews created: {reviews_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Save Data as Delta Tables

# COMMAND ----------

# Create catalog and schema if they don't exist
spark.sql(f"CREATE CATALOG IF NOT EXISTS {TARGET_CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}")

print(f"Catalog and schema verified: {TARGET_CATALOG}.{TARGET_SCHEMA}")

# COMMAND ----------

# Drop tables if they exist
spark.sql(f"DROP TABLE IF EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}.{CUSTOMER_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}.{PRODUCT_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}.{SALES_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}.{REVIEWS_TABLE}")

# COMMAND ----------

# Save Customer table
print(f"Saving Customer table to {CUSTOMER_TABLE}...")
customer_df.write.format("delta").mode("append").saveAsTable(CUSTOMER_TABLE)
print(f"✓ Customer table saved successfully!")

# COMMAND ----------

# Save Product table
print(f"Saving Product table to {PRODUCT_TABLE}...")
product_df.write.format("delta").mode("append").saveAsTable(PRODUCT_TABLE)
print(f"✓ Product table saved successfully!")

# COMMAND ----------

# Save Sales table
print(f"Saving Sales table to {SALES_TABLE}...")
sales_df.write.format("delta").mode("append").saveAsTable(SALES_TABLE)
print(f"✓ Sales table saved successfully!")

# COMMAND ----------

# Save Customer Reviews table
print(f"Saving Customer Reviews table to {REVIEWS_TABLE}...")
reviews_df.write.format("delta").mode("append").saveAsTable(REVIEWS_TABLE)
print(f"✓ Customer Reviews table saved successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Verify Tables and Relationships

# COMMAND ----------

print("=" * 80)
print("TABLE SUMMARY")
print("=" * 80)

# Customer table
customer_count = spark.table(CUSTOMER_TABLE).count()
print(f"\n1. {CUSTOMER_TABLE}")
print(f"   - Total Rows: {customer_count}")
print(f"   - Primary Key: customer_id")
spark.table(CUSTOMER_TABLE).printSchema()

# Product table
product_count = spark.table(PRODUCT_TABLE).count()
print(f"\n2. {PRODUCT_TABLE}")
print(f"   - Total Rows: {product_count}")
print(f"   - Primary Key: product_id")
spark.table(PRODUCT_TABLE).printSchema()

# Sales table
sales_count = spark.table(SALES_TABLE).count()
print(f"\n3. {SALES_TABLE}")
print(f"   - Total Rows: {sales_count}")
print(f"   - Primary Key: sale_id")
print(f"   - Foreign Keys: customer_id, product_id")
spark.table(SALES_TABLE).printSchema()

# Reviews table
reviews_count = spark.table(REVIEWS_TABLE).count()
print(f"\n4. {REVIEWS_TABLE}")
print(f"   - Total Rows: {reviews_count}")
print(f"   - Primary Key: review_id")
print(f"   - Foreign Keys: customer_id, product_id")
spark.table(REVIEWS_TABLE).printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Test Joins Between Tables

# COMMAND ----------

# Test join: Sales with Customer and Product information
print("Testing join: Sales with Customer and Product details")
test_join_df = spark.table(SALES_TABLE) \
    .join(spark.table(CUSTOMER_TABLE), "customer_id", "left") \
    .join(spark.table(PRODUCT_TABLE), "product_id", "left") \
    .select(
        "sale_id",
        "sale_date",
        F.col("first_name").alias("customer_first_name"),
        F.col("last_name").alias("customer_last_name"),
        "product_name",
        "category",
        "quantity",
        "total_amount"
    )

test_join_df.show(10, truncate=False)

# COMMAND ----------

# Test join: Customer Reviews with Customer and Product information
print("Testing join: Reviews with Customer and Product details")
test_review_join_df = spark.table(REVIEWS_TABLE) \
    .join(spark.table(CUSTOMER_TABLE), "customer_id", "left") \
    .join(spark.table(PRODUCT_TABLE), "product_id", "left") \
    .select(
        "review_id",
        "review_date",
        F.col("first_name").alias("customer_first_name"),
        F.col("last_name").alias("customer_last_name"),
        "product_name",
        "rating",
        "review_text"
    )

test_review_join_df.show(10, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Summary Statistics for Dashboard Preparation

# COMMAND ----------

print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

# Sales by Category
print("\n1. Total Sales by Product Category:")
spark.table(SALES_TABLE) \
    .join(spark.table(PRODUCT_TABLE), "product_id") \
    .groupBy("category") \
    .agg(
        F.sum("total_amount").alias("total_revenue"),
        F.count("sale_id").alias("total_sales")
    ) \
    .orderBy(F.desc("total_revenue")) \
    .show()

# Top Customers by Lifetime Value
print("\n2. Top 10 Customers by Lifetime Value:")
spark.table(CUSTOMER_TABLE) \
    .orderBy(F.desc("lifetime_value")) \
    .select("customer_id", "first_name", "last_name", "customer_segment", "lifetime_value") \
    .show(10)

# Average Rating by Product Category
print("\n3. Average Rating by Product Category:")
spark.table(REVIEWS_TABLE) \
    .join(spark.table(PRODUCT_TABLE), "product_id") \
    .groupBy("category") \
    .agg(
        F.avg("rating").alias("avg_rating"),
        F.count("review_id").alias("total_reviews")
    ) \
    .orderBy(F.desc("avg_rating")) \
    .show()

# Sales Trends by Month
print("\n4. Recent Sales Trends (Last 6 Months by Total Revenue):")
spark.table(SALES_TABLE) \
    .withColumn("month", F.date_format("sale_date", "yyyy-MM")) \
    .groupBy("month") \
    .agg(
        F.sum("total_amount").alias("monthly_revenue"),
        F.count("sale_id").alias("total_sales")
    ) \
    .orderBy(F.desc("month")) \
    .show(6)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Completion Message

# COMMAND ----------

print("=" * 80)
print("✓ DATA GENERATION COMPLETE!")
print("=" * 80)
print(f"\nAll tables have been successfully created in {TARGET_CATALOG}.{TARGET_SCHEMA}")
print("\nGenerated Tables:")
print(f"  1. {CUSTOMER_TABLE} - {customer_count} rows")
print(f"  2. {PRODUCT_TABLE} - {product_count} rows")
print(f"  3. {SALES_TABLE} - {sales_count} rows")
print(f"  4. {REVIEWS_TABLE} - {reviews_count} rows")
print("\nYou can now use these tables to create dashboards and perform analysis!")
print("=" * 80)
