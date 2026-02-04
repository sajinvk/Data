# Databricks Asset Bundle - AI Data Generator

This folder contains the Databricks Asset Bundle configuration for deploying the AI Data Generator as automated jobs.

## 📁 Structure

```
bundle/
├── databricks.yml          # Main bundle configuration (with sync)
├── job_parameters.conf     # Parameter templates for quick setup
└── resources/
    └── jobs.yml           # Job definitions (5 pre-configured jobs)

Note: The notebook (ai_data_generator.py) is synced from the parent directory.
```

## 🔄 File Sync

The bundle automatically syncs the notebook to the workspace:

- **Local**: `../ai_data_generator.py`
- **Workspace**: `${workspace.root_path}/files/ai_data_generator.py`

During deployment, the notebook is uploaded to your workspace and jobs reference the synced copy.

## 🚀 Quick Start

### 1. Configure Workspace

Edit `databricks.yml` (line 36):

```yaml
workspace:
  host: "https://your-actual-workspace.cloud.databricks.com"
```

### 2. Authenticate

```bash
databricks configure --token
# Enter your workspace URL and personal access token
```

### 3. Validate

```bash
databricks bundle validate -t dev
```

### 4. Deploy

```bash
databricks bundle deploy -t dev
```

### 5. Run a Job

```bash
# Run pre-configured healthcare patients job
databricks bundle run generate_patients_job -t dev

# Or run generic job with custom parameters
databricks bundle run ai_data_generator_job -t dev \
  --param industry="finance" \
  --param domain="transactions" \
  --param num_rows="500"
```

## 📋 Available Jobs

### 1. ai_data_generator_job
**Generic template** - Fully customizable via parameters

**Default Parameters:**
- Industry: healthcare
- Domain: patient records
- Rows: 100
- All parameters can be overridden at runtime

### 2. generate_patients_job
**Healthcare patient records** - Pre-configured

**Generates:**
- Table: `{catalog}.{schema}.patients`
- Rows: 500
- Constraints: Patient ID from 10000, ages 18-95

### 3. generate_products_job
**Retail product inventory** - Pre-configured with custom schema

**Generates:**
- Table: `{catalog}.{schema}.products`
- Rows: 200
- Custom schema with product details

### 4. generate_transactions_job
**Finance transactions** - Pre-configured

**Generates:**
- Table: `{catalog}.{schema}.transactions`
- Rows: 1000
- Amounts: $10-$10,000

### 5. generate_complete_dataset_job
**Multi-table generation** - Creates related tables

**Generates:**
- `customers` (500 rows)
- `products` (200 rows)
- `orders` (1000 rows) - depends on customers and products

## 🌍 Environments

### Development (dev)
```bash
databricks bundle deploy -t dev
```

- Path: `~/.bundle/ai_data_generator/dev`
- Catalog: `pilotws`
- Schema: `pilotschema`

### Staging (staging)
```bash
databricks bundle deploy -t staging
```

- Path: `/Shared/.bundle/ai_data_generator/staging`
- Catalog: `staging_catalog`
- Schema: `staging_schema`

### Production (prod)
```bash
databricks bundle deploy -t prod
```

- Path: `/Shared/.bundle/ai_data_generator/prod`
- Catalog: `prod_catalog`
- Schema: `prod_schema`

## ⚙️ Configuration

### Variables (databricks.yml)

These variables can be overridden per environment:

| Variable | Default | Description |
|----------|---------|-------------|
| `environment` | "dev" | Environment name |
| `catalog` | "pilotws" | Unity Catalog name |
| `schema` | "pilotschema" | Schema name |
| `cluster_node_type` | "i3.xlarge" | Node type for clusters |
| `cluster_spark_version` | "14.3.x-scala2.12" | Databricks runtime version |

### Override Variables

**Method 1: Edit databricks.yml targets**

```yaml
targets:
  dev:
    variables:
      catalog: my_catalog
      schema: my_schema
```

**Method 2: Environment variables**

```bash
export DATABRICKS_CATALOG="my_catalog"
export DATABRICKS_SCHEMA="my_schema"
databricks bundle deploy -t dev
```

## 📝 Customizing Jobs

### Edit Existing Job

Edit `resources/jobs.yml` and modify base_parameters:

```yaml
base_parameters:
  industry: "your_industry"
  domain: "your_domain"
  table_name: "your_table"
  num_rows: "500"
  # ... other parameters
```

### Add New Job

Add to `resources/jobs.yml`:

```yaml
resources:
  jobs:
    my_custom_job:
      name: "[${bundle.target}] My Custom Job"
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
            notebook_path: ../../ai_data_generator.py
            base_parameters:
              industry: "manufacturing"
              domain: "equipment maintenance"
              table_name: "maintenance_logs"
              target_catalog: ${var.catalog}
              target_schema: ${var.schema}
              num_rows: "300"
              ai_model_endpoint: "databricks-meta-llama-3-3-70b-instruct"
              custom_schema_json: ""
              column_constraints_json: '{}'
```

### Use Parameter Templates

Copy configurations from `job_parameters.conf`:

```bash
# View available templates
cat job_parameters.conf

# Examples include:
# - Healthcare: patients, appointments, prescriptions
# - Retail: products, orders, customers
# - Finance: transactions, loans, portfolios
# - Manufacturing: sensors, maintenance
# - And many more!
```

## 🔧 Common Commands

```bash
# Validate configuration
databricks bundle validate -t dev

# View deployment plan
databricks bundle summary -t dev

# Deploy to environment
databricks bundle deploy -t dev

# List deployed jobs
databricks bundle jobs list -t dev

# Run a specific job
databricks bundle run <job_name> -t dev

# Run with custom parameters
databricks bundle run ai_data_generator_job -t dev \
  --param industry="retail" \
  --param num_rows="1000"

# Destroy deployment
databricks bundle destroy -t dev
```

## 🐛 Troubleshooting

### Issue: Variable not defined

**Error:**
```
Error: variable environment is not defined but is assigned a value
```

**Solution:** This is already fixed. The `environment` variable is defined in `databricks.yml`.

### Issue: Notebook not found

**Error:**
```
Error: notebook not found
```

**Solution:** The notebook path is relative to the resources folder:
```yaml
notebook_path: ../../ai_data_generator.py  # Correct
```

### Issue: Authentication failed

**Solution:**
```bash
databricks configure --token
# Enter your workspace URL and token
```

### More Help

See `../docs/TROUBLESHOOTING.md` for comprehensive troubleshooting guide.

## 📊 Job Parameters

All jobs accept these 9 parameters:

| Parameter | Required | Type | Example |
|-----------|----------|------|---------|
| `industry` | Yes | string | "healthcare" |
| `domain` | Yes | string | "patient records" |
| `table_name` | Yes | string | "patients" |
| `target_catalog` | Yes | string | "pilotws" |
| `target_schema` | Yes | string | "pilotschema" |
| `num_rows` | Yes | string | "100" |
| `ai_model_endpoint` | Yes | string | "databricks-meta-llama-3-3-70b-instruct" |
| `custom_schema_json` | No | JSON string | `'{"col": "TYPE"}'` |
| `column_constraints_json` | No | JSON string | `'{"col": "constraint"}'` |

## 🎯 Example Workflows

### Test in Dev, Deploy to Prod

```bash
# 1. Test with small dataset in dev
databricks bundle deploy -t dev
databricks bundle run ai_data_generator_job -t dev --param num_rows="10"

# 2. Verify results
databricks sql "SELECT * FROM pilotws.pilotschema.patients LIMIT 10"

# 3. Deploy to staging
databricks bundle deploy -t staging
databricks bundle run ai_data_generator_job -t staging --param num_rows="100"

# 4. Deploy to production
databricks bundle deploy -t prod
databricks bundle run ai_data_generator_job -t prod --param num_rows="10000"
```

### Generate Multiple Tables

```bash
# Run jobs in parallel for different tables
databricks bundle run generate_patients_job -t dev &
databricks bundle run generate_products_job -t dev &
databricks bundle run generate_transactions_job -t dev &
wait
```

### Schedule Daily Generation

Uncomment the schedule section in `resources/jobs.yml`:

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

## 📚 Additional Documentation

- **Full Deployment Guide**: `../docs/DEPLOYMENT.md`
- **Quick Reference**: `../docs/QUICK_REFERENCE.md`
- **Usage Examples**: `../docs/EXAMPLES.md`
- **Troubleshooting**: `../docs/TROUBLESHOOTING.md`

## ✅ Checklist

Before deploying:
- [ ] Workspace URL updated in `databricks.yml`
- [ ] Authentication configured
- [ ] Bundle validated successfully
- [ ] Target catalog/schema exists
- [ ] AI endpoint access verified

## 🔗 Links

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/)
- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/)

---

**Quick Start:** Update `databricks.yml`, run `databricks bundle deploy -t dev`, then `databricks bundle run generate_patients_job -t dev`

**Need Help?** Check `../docs/TROUBLESHOOTING.md` or `../docs/DEPLOYMENT.md`
