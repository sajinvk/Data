# Databricks Bundle Deployment Guide

This guide explains how to deploy and run the AI Data Generator jobs using Databricks Asset Bundles.

## 📋 Prerequisites

1. **Databricks CLI** installed and configured
   ```bash
   # Install Databricks CLI
   pip install databricks-cli
   
   # Or use the new Databricks CLI
   curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
   ```

2. **Workspace Configuration**
   - Databricks workspace with access to AI endpoints
   - Unity Catalog enabled
   - Appropriate permissions to create jobs and clusters

3. **Authentication**
   ```bash
   # Configure authentication (choose one method)
   
   # Method 1: Using databricks configure
   databricks configure --token
   
   # Method 2: Using environment variables
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   ```

## 🚀 Quick Start

### Step 1: Update Configuration

Edit `databricks.yml` and update the workspace URL:

```yaml
workspace:
  host: "https://your-workspace-url.cloud.databricks.com"
```

### Step 2: Validate Bundle

```bash
cd DataGenerator
databricks bundle validate
```

### Step 3: Deploy to Dev Environment

```bash
# Deploy to development
databricks bundle deploy -t dev
```

### Step 4: Run a Job

```bash
# Run the main AI data generator job
databricks bundle run ai_data_generator_job -t dev

# Or run a specific example job
databricks bundle run generate_patients_job -t dev
databricks bundle run generate_products_job -t dev
databricks bundle run generate_transactions_job -t dev
```

## 📁 Bundle Structure

```
DataGenerator/
├── databricks.yml              # Main bundle configuration
├── resources/
│   └── jobs.yml               # Job definitions
├── ai_data_generator.py       # The notebook/script
└── DEPLOYMENT.md              # This file
```

## 🎯 Available Jobs

### 1. `ai_data_generator_job`
Generic template job with configurable parameters.

**Parameters:**
- `industry`: Industry domain (default: "healthcare")
- `domain`: Data domain (default: "patient records")
- `table_name`: Output table name (default: "patients")
- `target_catalog`: Unity Catalog name
- `target_schema`: Schema name
- `num_rows`: Number of rows to generate (default: "100")
- `ai_model_endpoint`: AI model to use
- `custom_schema_json`: Optional JSON schema
- `column_constraints_json`: Optional JSON constraints

### 2. `generate_patients_job`
Pre-configured job to generate healthcare patient records.

**Output:**
- Table: `{catalog}.{schema}.patients`
- Rows: 500
- Constraints: Patient ID from 10000, ages 18-95

### 3. `generate_products_job`
Pre-configured job to generate retail product inventory.

**Output:**
- Table: `{catalog}.{schema}.products`
- Rows: 200
- Custom schema with product details

### 4. `generate_transactions_job`
Pre-configured job to generate finance transactions.

**Output:**
- Table: `{catalog}.{schema}.transactions`
- Rows: 1000
- Transaction amounts $10-$10,000

### 5. `generate_complete_dataset_job`
Multi-task job that generates related tables sequentially.

**Output:**
- `customers` table (500 rows)
- `products` table (200 rows)
- `orders` table (1000 rows) - depends on customers and products

## 🔧 Customizing Jobs

### Method 1: Modify Existing Job

Edit `resources/jobs.yml` and change the `base_parameters`:

```yaml
base_parameters:
  industry: "your-industry"
  domain: "your-domain"
  table_name: "your-table"
  num_rows: "1000"
  # ... other parameters
```

### Method 2: Create New Job

Add a new job definition to `resources/jobs.yml`:

```yaml
resources:
  jobs:
    my_custom_job:
      name: "[${bundle.target}] My Custom Data Generator"
      
      job_clusters:
        - job_cluster_key: my_cluster
          new_cluster:
            spark_version: ${var.cluster_spark_version}
            node_type_id: ${var.cluster_node_type}
            num_workers: 2
      
      tasks:
        - task_key: generate_my_data
          job_cluster_key: my_cluster
          
          notebook_task:
            notebook_path: ../ai_data_generator.py
            base_parameters:
              industry: "manufacturing"
              domain: "equipment maintenance"
              table_name: "maintenance_logs"
              target_catalog: ${var.catalog}
              target_schema: ${var.schema}
              num_rows: "300"
              ai_model_endpoint: "databricks-meta-llama-3-3-70b-instruct"
              custom_schema_json: ""
              column_constraints_json: '{"equipment_id": "Format like EQ-1001"}'
```

### Method 3: Override Parameters at Runtime

Run a job with custom parameters:

```bash
databricks bundle run ai_data_generator_job -t dev \
  --param industry="finance" \
  --param domain="loan applications" \
  --param table_name="loans" \
  --param num_rows="500"
```

## 🌍 Environments

### Development (`dev`)
```bash
# Deploy to dev
databricks bundle deploy -t dev

# Run in dev
databricks bundle run ai_data_generator_job -t dev
```

**Configuration:**
- Workspace: `~/.bundle/ai_data_generator/dev`
- Catalog: `pilotws` (default)
- Schema: `pilotschema` (default)

### Staging (`staging`)
```bash
# Deploy to staging
databricks bundle deploy -t staging

# Run in staging
databricks bundle run ai_data_generator_job -t staging
```

**Configuration:**
- Workspace: `/Shared/.bundle/ai_data_generator/staging`
- Catalog: `staging_catalog`
- Schema: `staging_schema`

### Production (`prod`)
```bash
# Deploy to production
databricks bundle deploy -t prod

# Run in production
databricks bundle run ai_data_generator_job -t prod
```

**Configuration:**
- Workspace: `/Shared/.bundle/ai_data_generator/prod`
- Catalog: `prod_catalog`
- Schema: `prod_schema`

## 🔐 Environment Variables

Override default configurations using environment variables:

```bash
# Override catalog and schema
export DATABRICKS_CATALOG="my_catalog"
export DATABRICKS_SCHEMA="my_schema"

# Override cluster configuration
export DATABRICKS_NODE_TYPE="i3.2xlarge"
export DATABRICKS_SPARK_VERSION="14.3.x-scala2.12"

# Deploy with overrides
databricks bundle deploy -t dev
```

## 📊 Monitoring Jobs

### View Job Status

```bash
# List all jobs in the bundle
databricks bundle jobs list -t dev

# Get job run history
databricks jobs runs list --job-id <job-id>

# View specific run details
databricks jobs runs get --run-id <run-id>
```

### View Job in Workspace

After deployment, jobs will be visible in:
```
Databricks Workspace > Workflows > Jobs > [dev] AI Data Generator
```

## 🔄 Common Workflows

### Deploy and Test

```bash
# 1. Validate configuration
databricks bundle validate

# 2. Deploy to dev
databricks bundle deploy -t dev

# 3. Run a test job (small dataset)
databricks bundle run ai_data_generator_job -t dev \
  --param num_rows="10"

# 4. Check results
databricks sql "SELECT * FROM pilotws.pilotschema.patients LIMIT 10"
```

### Update and Redeploy

```bash
# 1. Make changes to ai_data_generator.py or jobs.yml

# 2. Redeploy
databricks bundle deploy -t dev

# 3. Run updated job
databricks bundle run ai_data_generator_job -t dev
```

### Promote to Production

```bash
# 1. Test in staging
databricks bundle deploy -t staging
databricks bundle run ai_data_generator_job -t staging

# 2. Verify results in staging

# 3. Deploy to production
databricks bundle deploy -t prod

# 4. Run in production
databricks bundle run ai_data_generator_job -t prod
```

## 📝 Example Use Cases

### Use Case 1: Generate Test Data for Development

```bash
# Deploy to dev
databricks bundle deploy -t dev

# Generate small patient dataset
databricks bundle run generate_patients_job -t dev
```

### Use Case 2: Generate Large Dataset for Staging

```yaml
# Edit resources/jobs.yml to increase num_rows
base_parameters:
  num_rows: "10000"  # Increase to 10,000
```

```bash
# Deploy and run
databricks bundle deploy -t staging
databricks bundle run ai_data_generator_job -t staging
```

### Use Case 3: Generate Multiple Related Tables

```bash
# Use the multi-table job
databricks bundle deploy -t dev
databricks bundle run generate_complete_dataset_job -t dev

# This creates:
# - customers table
# - products table  
# - orders table (with foreign keys)
```

### Use Case 4: Scheduled Daily Generation

Edit `resources/jobs.yml` and uncomment the schedule section:

```yaml
schedule:
  quartz_cron_expression: "0 0 2 * * ?"  # Daily at 2 AM
  timezone_id: "America/Los_Angeles"
  pause_status: UNPAUSED
```

Then deploy:

```bash
databricks bundle deploy -t prod
```

## 🐛 Troubleshooting

### Issue: Bundle validation fails

```bash
# Check syntax
databricks bundle validate

# Common issues:
# - Incorrect YAML indentation
# - Missing variables
# - Invalid notebook path
```

### Issue: Job fails to start

```bash
# Check job definition
databricks jobs get --job-id <job-id>

# Verify cluster can be created
# Check node_type_id is available in your workspace
```

### Issue: Notebook not found

```bash
# Verify notebook path in jobs.yml
notebook_path: ../ai_data_generator.py

# Ensure notebook is deployed
databricks bundle deploy -t dev
```

### Issue: Permission denied

```bash
# Verify you have permissions:
# - Create jobs
# - Create clusters
# - Access Unity Catalog
# - Access AI endpoints

# Check your token permissions
databricks auth login --host https://your-workspace.cloud.databricks.com
```

### Issue: AI model endpoint not accessible

```yaml
# Try different model endpoint in base_parameters:
ai_model_endpoint: "databricks-dbrx-instruct"
# or
ai_model_endpoint: "databricks-meta-llama-3-1-70b-instruct"
```

## 📚 Additional Commands

### List Deployed Resources

```bash
# Show all deployed jobs
databricks bundle jobs list -t dev
```

### Destroy Deployment

```bash
# Remove all deployed resources
databricks bundle destroy -t dev
```

### View Bundle Summary

```bash
# Show what will be deployed
databricks bundle summary -t dev
```

### Export Job Configuration

```bash
# Export job to JSON
databricks jobs get --job-id <job-id> > job-config.json
```

## 🔗 Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy Data Generator

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Databricks CLI
        run: |
          curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
      
      - name: Deploy Bundle
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          cd DataGenerator
          databricks bundle deploy -t prod
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Databricks Asset Bundles documentation
3. Verify workspace permissions and configuration
4. Check AI endpoint availability

## 🎓 Best Practices

1. **Start Small**: Test with `num_rows: "10"` before scaling up
2. **Use Dev First**: Always test in dev before staging/prod
3. **Version Control**: Keep all YAML files in version control
4. **Parameterize**: Use variables instead of hard-coded values
5. **Monitor**: Set up email notifications for job failures
6. **Document**: Add comments to custom job configurations
7. **Tag Resources**: Use custom_tags for cost tracking and organization

## 📈 Performance Tips

1. **Cluster Sizing**: Adjust `num_workers` based on `num_rows`
   - 100 rows: 2 workers
   - 1000 rows: 4 workers
   - 10000+ rows: 8+ workers

2. **Batch Processing**: For large datasets, run multiple jobs in parallel with different row ranges

3. **Caching**: Consider caching reference data between job runs

4. **Model Selection**: Faster models for testing, more powerful for production

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Databricks Runtime:** 14.3.x or higher
