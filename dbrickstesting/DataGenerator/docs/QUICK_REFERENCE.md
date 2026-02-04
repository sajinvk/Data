# Quick Reference Card - AI Data Generator Jobs

## 🚀 Essential Commands

### Setup & Validation
```bash
# Validate bundle
databricks bundle validate

# View what will be deployed
databricks bundle summary -t dev
```

### Deploy
```bash
databricks bundle deploy -t dev      # Development
databricks bundle deploy -t staging  # Staging
databricks bundle deploy -t prod     # Production
```

### Run Jobs
```bash
# Generic job
databricks bundle run ai_data_generator_job -t dev

# Pre-configured jobs
databricks bundle run generate_patients_job -t dev
databricks bundle run generate_products_job -t dev
databricks bundle run generate_transactions_job -t dev
databricks bundle run generate_complete_dataset_job -t dev
```

### Run with Custom Parameters
```bash
databricks bundle run ai_data_generator_job -t dev \
  --param industry="finance" \
  --param domain="loan applications" \
  --param table_name="loans" \
  --param num_rows="500"
```

### Manage Deployments
```bash
# List deployed jobs
databricks bundle jobs list -t dev

# Destroy deployment
databricks bundle destroy -t dev
```

## 📋 Job Parameters

| Parameter | Required | Example | Description |
|-----------|----------|---------|-------------|
| `industry` | Yes | "healthcare" | Industry domain |
| `domain` | Yes | "patient records" | Data domain |
| `table_name` | Yes | "patients" | Output table |
| `target_catalog` | Yes | "pilotws" | Catalog name |
| `target_schema` | Yes | "pilotschema" | Schema name |
| `num_rows` | Yes | "100" | Row count |
| `ai_model_endpoint` | Yes | "databricks-meta-llama-3-3-70b-instruct" | AI model |
| `custom_schema_json` | No | `'{"col":"TYPE"}'` | Custom schema |
| `column_constraints_json` | No | `'{"col":"rule"}'` | Column rules |

## 🎯 Pre-Configured Jobs

### 1. ai_data_generator_job
Generic template - customize all parameters.

### 2. generate_patients_job
- Industry: Healthcare
- Domain: Patient records
- Rows: 500
- Constraints: Patient ID from 10000, ages 18-95

### 3. generate_products_job
- Industry: Retail
- Domain: Product inventory
- Rows: 200
- Custom schema with product details

### 4. generate_transactions_job
- Industry: Finance
- Domain: Transactions
- Rows: 1000
- Amounts: $10-$10,000

### 5. generate_complete_dataset_job
Multi-table generation:
- Customers (500 rows)
- Products (200 rows)
- Orders (1000 rows with FK)

## 🌍 Environments

| Environment | Path | Catalog | Schema |
|-------------|------|---------|--------|
| **dev** | `~/.bundle/.../dev` | pilotws | pilotschema |
| **staging** | `/Shared/.bundle/.../staging` | staging_catalog | staging_schema |
| **prod** | `/Shared/.bundle/.../prod` | prod_catalog | prod_schema |

## 📖 Documentation Quick Links

| Need | Document | Command |
|------|----------|---------|
| Overview | JOB_SUMMARY.md | `cat JOB_SUMMARY.md` |
| Deployment | DEPLOYMENT.md | `cat DEPLOYMENT.md` |
| Parameters | job_parameters.conf | `cat job_parameters.conf` |
| Examples | EXAMPLES.md | `cat EXAMPLES.md` |

## 🔧 Common Patterns

### Pattern 1: Test → Stage → Prod
```bash
# Test in dev
databricks bundle deploy -t dev
databricks bundle run ai_data_generator_job -t dev --param num_rows="10"

# Stage
databricks bundle deploy -t staging
databricks bundle run ai_data_generator_job -t staging --param num_rows="100"

# Production
databricks bundle deploy -t prod
databricks bundle run ai_data_generator_job -t prod --param num_rows="10000"
```

### Pattern 2: Custom Job Creation
```yaml
# Add to resources/jobs.yml
my_custom_job:
  name: "[${bundle.target}] My Job"
  job_clusters: [...]
  tasks:
    - task_key: my_task
      notebook_task:
        notebook_path: ../ai_data_generator.py
        base_parameters:
          industry: "your_industry"
          domain: "your_domain"
          # ... other params
```

### Pattern 3: Multi-Table Generation
```yaml
tasks:
  - task_key: gen_customers
    # Generate customers

  - task_key: gen_products
    # Generate products

  - task_key: gen_orders
    depends_on:
      - task_key: gen_customers
      - task_key: gen_products
    # Generate orders with FK
```

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Validation fails | Check YAML syntax in databricks.yml |
| Job not found | Re-deploy: `databricks bundle deploy -t dev` |
| Permission denied | Run: `databricks auth login` |
| AI endpoint error | Try different model in parameters |
| Notebook not found | Check `notebook_path` in jobs.yml |

## 📊 Performance Guide

| Rows | Workers | Time Estimate |
|------|---------|---------------|
| 10-50 | 2 | 1-3 min |
| 100-500 | 2 | 3-10 min |
| 1,000 | 2-4 | 10-30 min |
| 5,000 | 4-8 | 30-90 min |
| 10,000+ | 8+ | 1+ hours |

## 🎯 Quick Start (3 Steps)

```bash
# 1. Configure
# Edit databricks.yml - set workspace URL

# 2. Deploy
databricks bundle deploy -t dev

# 3. Run
databricks bundle run generate_patients_job -t dev
```

## 📝 Example Parameter Sets

### Healthcare
```bash
--param industry="healthcare" \
--param domain="patient records" \
--param table_name="patients" \
--param num_rows="500"
```

### Retail
```bash
--param industry="retail" \
--param domain="product inventory" \
--param table_name="products" \
--param num_rows="200"
```

### Finance
```bash
--param industry="finance" \
--param domain="transactions" \
--param table_name="transactions" \
--param num_rows="1000"
```

## ⚡ Power User Tips

1. **Parallel jobs**: Run multiple jobs simultaneously for different tables
2. **Parameter files**: Use job_parameters.conf templates
3. **Environment variables**: Override configs without editing files
4. **Scheduled runs**: Uncomment schedule in jobs.yml for automation
5. **Cost tracking**: Use custom_tags in cluster config

## 🔗 Integration

### GitHub Actions
```yaml
- name: Deploy & Run
  run: |
    databricks bundle deploy -t prod
    databricks bundle run ai_data_generator_job -t prod
```

### Shell Script
```bash
#!/bin/bash
for job in generate_patients_job generate_products_job; do
  databricks bundle run $job -t dev &
done
wait
```

## 📞 Getting Help

1. **Validation errors**: Run `databricks bundle validate`
2. **Job failures**: Check logs in Databricks UI → Workflows
3. **Parameter errors**: Review job_parameters.conf
4. **Docs**: Read DEPLOYMENT.md for detailed guide

---

**Print this card for quick reference!** 📄
