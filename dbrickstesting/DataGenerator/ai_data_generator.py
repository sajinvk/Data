# Databricks notebook source
# MAGIC %md
# MAGIC # AI-Powered Data Generator
# MAGIC
# MAGIC This notebook uses Databricks AI foundational models to generate custom tables based on:
# MAGIC - **Industry**: The industry domain (e.g., "healthcare", "retail", "finance")
# MAGIC - **Domain**: The specific data domain (e.g., "customer records", "product inventory", "transactions")
# MAGIC - **Table Name**: The name of the table to create
# MAGIC - **Schema**: Either provide your own schema or let AI generate one
# MAGIC
# MAGIC Features:
# MAGIC - AI-generated schemas when not provided
# MAGIC - AI-generated sample data using `ai_query()` that is highly relevant to the industry and domain
# MAGIC - Configurable constraints for specific columns (e.g., product_id range 1-100)
# MAGIC - Supports custom column-level prompts for fine-grained data generation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Import json for parsing widget parameters
import json

# ========================
# WIDGET SETUP FOR JOB PARAMETERS
# ========================

# Create widgets to accept parameters from Databricks Jobs
dbutils.widgets.text("industry", "healthcare", "Industry")
dbutils.widgets.text("domain", "patient records", "Domain")
dbutils.widgets.text("table_name", "patients", "Table Name")
dbutils.widgets.text("target_catalog", "pilotws", "Target Catalog")
dbutils.widgets.text("target_schema", "pilotschema", "Target Schema")
dbutils.widgets.text("num_rows", "100", "Number of Rows")
dbutils.widgets.text("ai_model_endpoint", "databricks-meta-llama-3-3-70b-instruct", "AI Model Endpoint")
dbutils.widgets.text("custom_schema_json", "", "Custom Schema (JSON)")
dbutils.widgets.text("column_constraints_json", "{}", "Column Constraints (JSON)")

# ========================
# DATA CONFIGURATION
# ========================

# Get parameters from widgets
INDUSTRY = dbutils.widgets.get("industry")
DOMAIN = dbutils.widgets.get("domain")
TABLE_NAME = dbutils.widgets.get("table_name")
TARGET_CATALOG = dbutils.widgets.get("target_catalog")
TARGET_SCHEMA = dbutils.widgets.get("target_schema")
NUM_ROWS = int(dbutils.widgets.get("num_rows"))
AI_MODEL_ENDPOINT = dbutils.widgets.get("ai_model_endpoint")

FULL_TABLE_NAME = f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{TABLE_NAME}"

# ========================
# SCHEMA CONFIGURATION
# ========================

# Parse custom schema from JSON if provided
custom_schema_json = dbutils.widgets.get("custom_schema_json")
if custom_schema_json and custom_schema_json.strip():
    try:
        CUSTOM_SCHEMA = json.loads(custom_schema_json)
        print(f"✓ Custom schema loaded from parameter")
    except Exception as e:
        print(f"⚠️  Warning: Could not parse custom_schema_json. Using AI generation. Error: {e}")
        CUSTOM_SCHEMA = None
else:
    CUSTOM_SCHEMA = None

# ========================
# COLUMN-SPECIFIC CONSTRAINTS
# ========================

# Parse column constraints from JSON
column_constraints_json = dbutils.widgets.get("column_constraints_json")
try:
    COLUMN_CONSTRAINTS = json.loads(column_constraints_json)
    print(f"✓ Column constraints loaded: {len(COLUMN_CONSTRAINTS)} constraints")
except Exception as e:
    print(f"⚠️  Warning: Could not parse column_constraints_json. Using empty constraints. Error: {e}")
    COLUMN_CONSTRAINTS = {}

# ========================
# DISPLAY CONFIGURATION
# ========================

print("=" * 80)
print("JOB CONFIGURATION")
print("=" * 80)
print(f"Industry: {INDUSTRY}")
print(f"Domain: {DOMAIN}")
print(f"Table Name: {TABLE_NAME}")
print(f"Target: {FULL_TABLE_NAME}")
print(f"Number of Rows: {NUM_ROWS}")
print(f"AI Model: {AI_MODEL_ENDPOINT}")
print(f"Custom Schema: {'Yes' if CUSTOM_SCHEMA else 'AI Generated'}")
print(f"Column Constraints: {len(COLUMN_CONSTRAINTS)} defined")
print("=" * 80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DoubleType, DateType, TimestampType, BooleanType
import pyspark.sql.functions as F
from datetime import datetime
import re

print("✓ Libraries imported successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Schema Generation with AI

# COMMAND ----------

def generate_schema_with_ai(industry, domain, table_name, model_endpoint):
    """
    Use Databricks AI to generate a schema for the specified industry and domain
    
    Args:
        industry (str): The industry domain
        domain (str): The specific data domain
        table_name (str): The name of the table
        model_endpoint (str): The AI model endpoint
        
    Returns:
        dict: A dictionary mapping column names to data types
    """
    print(f"Using AI to generate schema for {industry} - {domain}...")
    
    prompt = f"""Generate a database table schema for a '{table_name}' table in the {industry} industry, specifically for {domain}.
    
Provide 8-12 relevant columns that would be typical for this use case.
Include appropriate data types from: STRING, INT, BIGINT, DOUBLE, BOOLEAN, DATE, TIMESTAMP.
Make the schema realistic and useful for the specified industry and domain.

Return ONLY a valid JSON object in this exact format, no other text:
{{"column_name": "DATA_TYPE", "column_name2": "DATA_TYPE"}}

Example for patient records in healthcare:
{{"patient_id": "INT", "first_name": "STRING", "last_name": "STRING", "date_of_birth": "DATE", "blood_type": "STRING", "admission_date": "TIMESTAMP", "diagnosis": "STRING", "insurance_id": "STRING", "emergency_contact": "STRING", "is_critical": "BOOLEAN"}}
"""
    
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        # Clean the response
        clean_response = ai_response.strip()
        
        # Remove markdown code blocks if present
        if '```' in clean_response:
            lines = clean_response.split('\n')
            clean_response = '\n'.join([l for l in lines if not l.strip().startswith('```')])
        
        # Extract JSON if wrapped in other text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', clean_response)
        if json_match:
            clean_response = json_match.group(0)
        
        schema_dict = json.loads(clean_response)
        
        print(f"✓ AI generated schema with {len(schema_dict)} columns")
        return schema_dict
        
    except Exception as e:
        print(f"❌ Schema generation failed: {str(e)}")
        print(f"AI Response: {ai_response if 'ai_response' in locals() else 'No response'}")
        raise

def convert_schema_to_struct(schema_dict):
    """
    Convert a schema dictionary to a PySpark StructType
    
    Args:
        schema_dict (dict): Dictionary mapping column names to data types
        
    Returns:
        StructType: PySpark schema
    """
    type_mapping = {
        'STRING': StringType(),
        'INT': IntegerType(),
        'INTEGER': IntegerType(),
        'BIGINT': LongType(),
        'LONG': LongType(),
        'DOUBLE': DoubleType(),
        'FLOAT': DoubleType(),
        'BOOLEAN': BooleanType(),
        'BOOL': BooleanType(),
        'DATE': DateType(),
        'TIMESTAMP': TimestampType(),
        'DATETIME': TimestampType()
    }
    
    fields = []
    for col_name, col_type in schema_dict.items():
        col_type_upper = col_type.upper()
        spark_type = type_mapping.get(col_type_upper, StringType())
        fields.append(StructField(col_name, spark_type, True))
    
    return StructType(fields)

def display_schema(schema_dict):
    """
    Display the schema in a readable format
    """
    print("\n" + "=" * 80)
    print(f"GENERATED SCHEMA FOR '{TABLE_NAME}'")
    print("=" * 80)
    for col_name, col_type in schema_dict.items():
        print(f"  {col_name:<30} {col_type}")
    print("=" * 80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate or Use Custom Schema

# COMMAND ----------

if CUSTOM_SCHEMA:
    print("Using provided custom schema...")
    schema_dict = CUSTOM_SCHEMA
else:
    print("No custom schema provided. Generating schema with AI...")
    schema_dict = generate_schema_with_ai(INDUSTRY, DOMAIN, TABLE_NAME, AI_MODEL_ENDPOINT)

# Display the schema
display_schema(schema_dict)

# Convert to PySpark StructType
pyspark_schema = convert_schema_to_struct(schema_dict)

# COMMAND ----------

# MAGIC %md
# MAGIC ## AI-Powered Data Generation

# COMMAND ----------

def generate_row_with_ai(industry, domain, schema_dict, column_constraints, model_endpoint, row_number=1):
    """
    Use Databricks AI to generate a single row of data
    
    Args:
        industry (str): The industry domain
        domain (str): The specific data domain
        schema_dict (dict): Dictionary mapping column names to data types
        column_constraints (dict): Dictionary of column-specific constraints
        model_endpoint (str): The AI model endpoint
        row_number (int): The current row number for unique values
        
    Returns:
        dict: A dictionary representing one row of data
    """
    
    # Build the prompt with schema and constraints
    schema_description = []
    for col_name, col_type in schema_dict.items():
        constraint = column_constraints.get(col_name, "")
        if constraint:
            schema_description.append(f'"{col_name}" ({col_type}): {constraint}')
        else:
            schema_description.append(f'"{col_name}" ({col_type})')
    
    schema_str = '\n'.join(schema_description)
    
    prompt = f"""Generate realistic sample data for a '{TABLE_NAME}' table in the {industry} industry ({domain} domain).

Schema and constraints:
{schema_str}

Important guidelines:
1. Generate realistic data that fits the {industry} industry and {domain} domain
2. Follow the specified data types exactly
3. Apply any column-specific constraints provided
4. For dates, use format: YYYY-MM-DD
5. For timestamps, use format: YYYY-MM-DD HH:MM:SS
6. Make sure values are realistic and internally consistent (e.g., dates make logical sense together)
7. Use varied but realistic values (avoid repeating the same data)
8. For ID fields, use unique values (this is row #{row_number})

Return ONLY a valid JSON object with one key-value pair per column, no other text:
{{"column1": "value1", "column2": "value2", ...}}
"""
    
    prompt_escaped = prompt.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    
    try:
        ai_response = spark.sql(f"""
            SELECT ai_query(
                '{model_endpoint}',
                '{prompt_escaped}'
            ) as response
        """).collect()[0]['response']
        
        # Clean the response
        clean_response = ai_response.strip()
        
        # Remove markdown code blocks
        if '```' in clean_response:
            lines = clean_response.split('\n')
            clean_response = '\n'.join([l for l in lines if not l.strip().startswith('```')])
        
        # Extract JSON
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', clean_response)
        if json_match:
            clean_response = json_match.group(0)
        
        row_data = json.loads(clean_response)
        
        # Convert string values to appropriate types
        converted_row = {}
        for col_name, col_type in schema_dict.items():
            value = row_data.get(col_name)
            if value is None:
                converted_row[col_name] = None
            else:
                # Type conversion based on schema
                col_type_upper = col_type.upper()
                try:
                    if col_type_upper in ['INT', 'INTEGER']:
                        converted_row[col_name] = int(value)
                    elif col_type_upper in ['BIGINT', 'LONG']:
                        converted_row[col_name] = int(value)
                    elif col_type_upper in ['DOUBLE', 'FLOAT']:
                        converted_row[col_name] = float(value)
                    elif col_type_upper in ['BOOLEAN', 'BOOL']:
                        if isinstance(value, str):
                            converted_row[col_name] = value.lower() in ['true', '1', 'yes']
                        else:
                            converted_row[col_name] = bool(value)
                    elif col_type_upper == 'DATE':
                        if isinstance(value, str):
                            # Parse date string
                            from datetime import datetime
                            converted_row[col_name] = datetime.strptime(value.split()[0], '%Y-%m-%d').date()
                        else:
                            converted_row[col_name] = value
                    elif col_type_upper in ['TIMESTAMP', 'DATETIME']:
                        if isinstance(value, str):
                            # Parse timestamp string
                            from datetime import datetime
                            try:
                                converted_row[col_name] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            except:
                                converted_row[col_name] = datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        else:
                            converted_row[col_name] = value
                    else:
                        converted_row[col_name] = str(value)
                except Exception as e:
                    # If conversion fails, keep as string
                    print(f"  ⚠️  Warning: Could not convert {col_name}={value} to {col_type}, keeping as string")
                    converted_row[col_name] = str(value)
        
        return converted_row
        
    except Exception as e:
        print(f"  ❌ Row generation failed: {str(e)}")
        # Return None to indicate failure
        return None

def generate_table_data(industry, domain, schema_dict, column_constraints, model_endpoint, num_rows):
    """
    Generate multiple rows of data using AI
    
    Args:
        industry (str): The industry domain
        domain (str): The specific data domain
        schema_dict (dict): Dictionary mapping column names to data types
        column_constraints (dict): Dictionary of column-specific constraints
        model_endpoint (str): The AI model endpoint
        num_rows (int): Number of rows to generate
        
    Returns:
        list: List of dictionaries, each representing a row
    """
    print(f"Generating {num_rows} rows of data using AI...")
    print(f"This may take a few minutes...\n")
    
    rows = []
    failed_rows = 0
    progress_interval = max(1, num_rows // 10)
    
    for i in range(1, num_rows + 1):
        if i % progress_interval == 0 or i == 1:
            print(f"  Progress: {i}/{num_rows} rows ({int(i/num_rows*100)}%)")
        
        row_data = generate_row_with_ai(
            industry, 
            domain, 
            schema_dict, 
            column_constraints, 
            model_endpoint,
            row_number=i
        )
        
        if row_data:
            rows.append(row_data)
        else:
            failed_rows += 1
            # Generate a basic fallback row
            fallback_row = {}
            for col_name, col_type in schema_dict.items():
                col_type_upper = col_type.upper()
                if col_type_upper in ['INT', 'INTEGER', 'BIGINT', 'LONG']:
                    fallback_row[col_name] = i
                elif col_type_upper in ['DOUBLE', 'FLOAT']:
                    fallback_row[col_name] = float(i)
                elif col_type_upper in ['BOOLEAN', 'BOOL']:
                    fallback_row[col_name] = i % 2 == 0
                elif col_type_upper == 'DATE':
                    from datetime import date, timedelta
                    fallback_row[col_name] = date.today() - timedelta(days=i)
                elif col_type_upper in ['TIMESTAMP', 'DATETIME']:
                    from datetime import datetime, timedelta
                    fallback_row[col_name] = datetime.now() - timedelta(hours=i)
                else:
                    fallback_row[col_name] = f"{col_name}_{i}"
            rows.append(fallback_row)
    
    print(f"\n✓ Generated {len(rows)} rows")
    if failed_rows > 0:
        print(f"  ⚠️  {failed_rows} rows failed and used fallback data")
    
    return rows

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Sample Data

# COMMAND ----------

# Generate the data
data_rows = generate_table_data(
    INDUSTRY,
    DOMAIN,
    schema_dict,
    COLUMN_CONSTRAINTS,
    AI_MODEL_ENDPOINT,
    NUM_ROWS
)

# Create DataFrame
df = spark.createDataFrame(data_rows, schema=pyspark_schema)

# Show sample data
print("\n" + "=" * 80)
print(f"SAMPLE DATA FROM '{TABLE_NAME}'")
print("=" * 80)
df.show(10, truncate=False)

print(f"\nTotal rows generated: {df.count()}")
print(f"Schema:")
df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save to Delta Table

# COMMAND ----------

# Create catalog and schema if they don't exist
spark.sql(f"CREATE CATALOG IF NOT EXISTS {TARGET_CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {TARGET_CATALOG}.{TARGET_SCHEMA}")

print(f"✓ Catalog and schema verified: {TARGET_CATALOG}.{TARGET_SCHEMA}")

# Drop table if exists
spark.sql(f"DROP TABLE IF EXISTS {FULL_TABLE_NAME}")

# Save as Delta table
print(f"\nSaving data to {FULL_TABLE_NAME}...")
df.write.format("delta").mode("overwrite").saveAsTable(FULL_TABLE_NAME)

print(f"✓ Table saved successfully!")

# Verify the saved table
saved_count = spark.table(FULL_TABLE_NAME).count()
print(f"\nVerification: {FULL_TABLE_NAME} contains {saved_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary and Statistics

# COMMAND ----------

print("=" * 80)
print("TABLE GENERATION COMPLETE")
print("=" * 80)
print(f"\nTable Details:")
print(f"  Industry: {INDUSTRY}")
print(f"  Domain: {DOMAIN}")
print(f"  Table Name: {FULL_TABLE_NAME}")
print(f"  Total Rows: {saved_count}")
print(f"  Total Columns: {len(schema_dict)}")
print(f"  AI Model Used: {AI_MODEL_ENDPOINT}")
print(f"\nSchema Used:")
for col_name, col_type in schema_dict.items():
    print(f"  - {col_name}: {col_type}")

print("\n" + "=" * 80)
print("You can now query your table:")
print(f"  spark.table('{FULL_TABLE_NAME}').display()")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Query Examples

# COMMAND ----------

# Display the full table
print("Full table preview:")
display(spark.table(FULL_TABLE_NAME))

# COMMAND ----------

# Show basic statistics for numeric columns
print("Basic statistics for numeric columns:")
spark.table(FULL_TABLE_NAME).describe().display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Usage Examples
# MAGIC
# MAGIC ### Example 1: Healthcare - Patient Records
# MAGIC ```python
# MAGIC INDUSTRY = "healthcare"
# MAGIC DOMAIN = "patient records"
# MAGIC TABLE_NAME = "patients"
# MAGIC CUSTOM_SCHEMA = None  # Let AI generate
# MAGIC COLUMN_CONSTRAINTS = {
# MAGIC     "patient_id": "Unique integers starting from 1000",
# MAGIC     "age": "Ages between 18 and 95"
# MAGIC }
# MAGIC ```
# MAGIC
# MAGIC ### Example 2: Retail - Product Inventory
# MAGIC ```python
# MAGIC INDUSTRY = "retail"
# MAGIC DOMAIN = "product inventory"
# MAGIC TABLE_NAME = "products"
# MAGIC CUSTOM_SCHEMA = {
# MAGIC     "product_id": "INT",
# MAGIC     "product_name": "STRING",
# MAGIC     "category": "STRING",
# MAGIC     "price": "DOUBLE",
# MAGIC     "stock_quantity": "INT",
# MAGIC     "supplier": "STRING",
# MAGIC     "last_restocked": "DATE"
# MAGIC }
# MAGIC COLUMN_CONSTRAINTS = {
# MAGIC     "product_id": "Range between 1 and 100",
# MAGIC     "price": "Between 5.00 and 500.00",
# MAGIC     "stock_quantity": "Between 0 and 1000"
# MAGIC }
# MAGIC ```
# MAGIC
# MAGIC ### Example 3: Finance - Transaction Records
# MAGIC ```python
# MAGIC INDUSTRY = "finance"
# MAGIC DOMAIN = "transaction records"
# MAGIC TABLE_NAME = "transactions"
# MAGIC CUSTOM_SCHEMA = None  # Let AI generate
# MAGIC COLUMN_CONSTRAINTS = {
# MAGIC     "transaction_id": "Unique UUIDs or sequential IDs",
# MAGIC     "amount": "Between 10.00 and 10000.00",
# MAGIC     "transaction_type": "Either 'debit' or 'credit'"
# MAGIC }
# MAGIC ```
