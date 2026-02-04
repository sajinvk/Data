# Quick Start Guide - AI Data Generator

Get started in 3 simple steps!

## Step 1: Choose Your Scenario (30 seconds)

Pick one of these common scenarios or create your own:

### Scenario A: Let AI Generate Everything
```python
INDUSTRY = "healthcare"
DOMAIN = "patient records"
TABLE_NAME = "patients"
NUM_ROWS = 100
CUSTOM_SCHEMA = None  # AI generates schema
COLUMN_CONSTRAINTS = {}  # No specific constraints
```

### Scenario B: Custom Schema, AI-Generated Data
```python
INDUSTRY = "retail"
DOMAIN = "product inventory"
TABLE_NAME = "products"
NUM_ROWS = 100
CUSTOM_SCHEMA = {
    "product_id": "INT",
    "product_name": "STRING",
    "price": "DOUBLE",
    "stock": "INT"
}
COLUMN_CONSTRAINTS = {}
```

### Scenario C: Full Control with Constraints
```python
INDUSTRY = "finance"
DOMAIN = "transactions"
TABLE_NAME = "transactions"
NUM_ROWS = 100
CUSTOM_SCHEMA = None
COLUMN_CONSTRAINTS = {
    "transaction_id": "Sequential IDs starting from 1000",
    "amount": "Between 10.00 and 1000.00",
    "status": "Either 'completed', 'pending', or 'failed'"
}
```

## Step 2: Configure the Script (1 minute)

1. Open `ai_data_generator.py` in Databricks
2. Find the "Configuration" section (around line 20)
3. Paste your chosen scenario or modify the defaults
4. Update these required fields:
   ```python
   TARGET_CATALOG = "your_catalog_name"
   TARGET_SCHEMA = "your_schema_name"
   AI_MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"
   ```

## Step 3: Run the Notebook (2-5 minutes)

1. Attach to a cluster with AI endpoint access
2. Click "Run All"
3. Watch the magic happen! ✨

The notebook will:
- ✅ Generate or display your schema
- ✅ Create realistic sample data
- ✅ Save to a Delta table
- ✅ Show you sample results

## What You Get

After running, you'll have:
- A Delta table with your generated data
- Sample data preview
- Schema documentation
- Ready-to-query table in Unity Catalog

## Example Output

```
========================================
GENERATED SCHEMA FOR 'patients'
========================================
  patient_id                     INT
  first_name                     STRING
  last_name                      STRING
  date_of_birth                  DATE
  diagnosis                      STRING
  admission_date                 TIMESTAMP
  insurance_provider             STRING
========================================

Generating 100 rows of data using AI...
  Progress: 10/100 rows (10%)
  Progress: 20/100 rows (20%)
  ...
  Progress: 100/100 rows (100%)

✓ Generated 100 rows

SAMPLE DATA FROM 'patients'
+------------+----------+---------+-------------+------------------+-------------------+--------------------+
|patient_id  |first_name|last_name|date_of_birth|diagnosis         |admission_date     |insurance_provider  |
+------------+----------+---------+-------------+------------------+-------------------+--------------------+
|10001       |Sarah     |Johnson  |1985-04-12   |Type 2 Diabetes   |2024-01-15 09:30:00|Blue Cross         |
|10002       |Michael   |Smith    |1972-08-23   |Hypertension      |2024-01-16 11:20:00|Aetna              |
...
```

## Common Use Cases

### Use Case 1: Testing a Pipeline
Generate test data that matches your production schema:
```python
INDUSTRY = "your_production_industry"
DOMAIN = "your_data_type"
CUSTOM_SCHEMA = {
    # Copy your production schema here
}
NUM_ROWS = 100  # Start small for testing
```

### Use Case 2: Demo/POC Data
Create realistic demo data for presentations:
```python
INDUSTRY = "retail"  # Whatever makes sense for your demo
DOMAIN = "sales transactions"
NUM_ROWS = 500  # Enough to look realistic
CUSTOM_SCHEMA = None  # Let AI make it look good
```

### Use Case 3: Training/Development
Generate sample data for training or development environments:
```python
INDUSTRY = "finance"
DOMAIN = "customer accounts"
NUM_ROWS = 1000
COLUMN_CONSTRAINTS = {
    "account_balance": "Between 100 and 100000",
    "account_status": "active, dormant, or closed"
}
```

## Tips for Success

### ✅ DO:
- Start with 50-100 rows to test your configuration
- Be specific with your industry and domain
- Use constraints for important business rules
- Review the generated schema before proceeding
- Check sample data quality before scaling up

### ❌ DON'T:
- Don't generate 10,000 rows on your first try (it's slow!)
- Don't use vague descriptions like "data" or "records"
- Don't ignore data type mismatches in constraints
- Don't forget to update TARGET_CATALOG and TARGET_SCHEMA

## Troubleshooting

### "AI query failed"
- ✅ Check that you have access to AI endpoints
- ✅ Verify the AI_MODEL_ENDPOINT name is correct
- ✅ Try a different model like "databricks-dbrx-instruct"

### "Schema parsing error"
- ✅ Simplify your column constraints
- ✅ Use CUSTOM_SCHEMA instead of AI generation
- ✅ Check that your industry/domain descriptions are clear

### "Data quality is poor"
- ✅ Add more specific column constraints
- ✅ Provide examples in constraints: "Like: Electronics, Clothing, Food"
- ✅ Be more specific with industry and domain

### "Too slow"
- ✅ Reduce NUM_ROWS (each row takes 1-3 seconds)
- ✅ Generate in batches (100 rows at a time)
- ✅ Try a faster AI model

## Next Steps

Once you have good data:

1. **Scale up**: Increase NUM_ROWS for production datasets
2. **Create related tables**: Run again with related schemas
3. **Build pipelines**: Use the generated data as source
4. **Create dashboards**: Visualize your generated data

## Need More Examples?

Check out `EXAMPLES.md` for 19+ ready-to-use templates including:
- Healthcare: patients, appointments, prescriptions
- Retail: products, orders, stores
- Finance: transactions, loans, portfolios
- Insurance: claims, policies
- Manufacturing: maintenance, production
- And many more!

## Support

For detailed documentation, see `README.md`
For configuration examples, see `EXAMPLES.md`
For this quick start, you're already here! 🎉

---

**Time to first data: ~3 minutes** ⚡
**Lines of code you write: ~10** 📝
**AI models doing the work: 100%** 🤖
