# AI Data Generator

A powerful, flexible AI-driven data generation tool for Databricks that uses foundational models to create realistic sample data for any industry and domain.

## 📁 Folder Structure

```
DataGenerator/
├── ai_data_generator.py          # Main notebook/script
│
├── bundle/                        # Databricks Asset Bundle
│   ├── databricks.yml            # Main bundle configuration
│   ├── job_parameters.conf       # Parameter templates
│   └── resources/
│       └── jobs.yml              # Job definitions (5 pre-configured jobs)
│
└── docs/                         # Documentation
    ├── INDEX.md                  # Start here - Navigation guide
    ├── QUICKSTART.md             # 3-minute getting started
    ├── README.md                 # Full feature documentation
    ├── EXAMPLES.md               # 19+ usage examples
    ├── JOB_SUMMARY.md            # Job deployment overview
    ├── DEPLOYMENT.md             # Complete deployment guide
    ├── QUICK_REFERENCE.md        # Command reference card
    ├── TROUBLESHOOTING.md        # Common issues & solutions
    ├── FIX_SUMMARY.md            # Recent fixes
    └── ARCHITECTURE.md           # Technical architecture
```

## 🚀 Quick Start

### Option 1: Run as Notebook (Simple)

1. Upload `ai_data_generator.py` to Databricks workspace
2. Open in notebook and configure parameters
3. Run all cells

### Option 2: Deploy as Job (Recommended)

```bash
# 1. Navigate to bundle directory
cd bundle

# 2. Update workspace URL in databricks.yml
# Edit line 36: host: "https://your-workspace.cloud.databricks.com"

# 3. Configure authentication
databricks configure --token

# 4. Deploy
databricks bundle deploy -t dev

# 5. Run
databricks bundle run generate_patients_job -t dev
```

## 📖 Documentation Guide

| Document | Purpose | Start Here If... |
|----------|---------|------------------|
| **docs/INDEX.md** | Navigation & overview | You're new to this tool |
| **docs/QUICKSTART.md** | 3-minute start | You want to run it quickly |
| **docs/JOB_SUMMARY.md** | Job deployment overview | You want to deploy as a job |
| **docs/DEPLOYMENT.md** | Full deployment guide | You need detailed deployment steps |
| **docs/QUICK_REFERENCE.md** | Command reference | You need quick command lookup |
| **docs/EXAMPLES.md** | 19+ templates | You need example configurations |
| **docs/README.md** | Complete features | You want to understand everything |
| **docs/TROUBLESHOOTING.md** | Problem solving | You're having issues |
| **docs/ARCHITECTURE.md** | Technical details | You want deep technical knowledge |

## ✨ Key Features

- **AI-Generated Schemas**: Let AI create appropriate schemas for your industry
- **Custom Schemas**: Or provide your own schema for full control
- **Column Constraints**: Fine-tune data generation per column (e.g., "price between 10-500")
- **Industry-Aware**: Data is contextually realistic for your specific industry
- **Job Deployment**: Deploy as Databricks jobs with full automation
- **Multi-Environment**: Dev, staging, production support
- **Multi-Table**: Generate related tables with dependencies

## 🎯 Use Cases

- **Testing**: Generate test data for development pipelines
- **Demos**: Create realistic demo data for presentations
- **POCs**: Quick data generation for proof-of-concepts
- **Training**: Generate sample datasets for training
- **Development**: Match production schemas in dev environments

## 📋 Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `industry` | Industry domain | "healthcare", "retail", "finance" |
| `domain` | Data domain | "patient records", "transactions" |
| `table_name` | Output table name | "patients", "products" |
| `num_rows` | Number of rows | "100", "1000", "10000" |
| `ai_model_endpoint` | AI model to use | "databricks-meta-llama-3-3-70b-instruct" |
| `custom_schema_json` | Optional JSON schema | `'{"col": "TYPE"}'` |
| `column_constraints_json` | Optional constraints | `'{"col": "rule"}'` |

## 🎓 Example Usage

### Healthcare Patient Records

```bash
databricks bundle run ai_data_generator_job -t dev \
  --param industry="healthcare" \
  --param domain="patient records" \
  --param table_name="patients" \
  --param num_rows="500"
```

### Retail Product Inventory

```bash
databricks bundle run ai_data_generator_job -t dev \
  --param industry="retail" \
  --param domain="product inventory" \
  --param table_name="products" \
  --param num_rows="200"
```

### Finance Transactions

```bash
databricks bundle run ai_data_generator_job -t dev \
  --param industry="finance" \
  --param domain="transactions" \
  --param table_name="transactions" \
  --param num_rows="1000"
```

## 🔧 Pre-Configured Jobs

The bundle includes 5 ready-to-use jobs:

1. **ai_data_generator_job** - Generic template (fully customizable)
2. **generate_patients_job** - Healthcare patients (500 rows)
3. **generate_products_job** - Retail products (200 rows)
4. **generate_transactions_job** - Finance transactions (1000 rows)
5. **generate_complete_dataset_job** - Multi-table generation

## 📊 Performance

- ~2-3 seconds per row for AI generation
- Recommended: 50-200 rows for testing
- Production: Scale with cluster size and batch processing

| Rows | Cluster Workers | Time Estimate |
|------|----------------|---------------|
| 10-50 | 2 | 1-3 minutes |
| 100-500 | 2 | 3-10 minutes |
| 1,000 | 2-4 | 10-30 minutes |
| 10,000+ | 8+ | 1+ hours |

## 🌍 Multi-Environment Support

Deploy to different environments with environment-specific configurations:

```bash
# Development
databricks bundle deploy -t dev

# Staging
databricks bundle deploy -t staging

# Production
databricks bundle deploy -t prod
```

## 🐛 Troubleshooting

Having issues? Check:

1. **docs/TROUBLESHOOTING.md** - Solutions for 10+ common errors
2. **docs/FIX_SUMMARY.md** - Recent fixes
3. **docs/DEPLOYMENT.md** - Detailed deployment guide

Common fixes:
- Update workspace URL in `bundle/databricks.yml`
- Configure authentication: `databricks configure --token`
- Validate bundle: `databricks bundle validate -t dev`

## 🔗 Links

- **Documentation**: See `docs/` folder
- **Bundle Configuration**: See `bundle/` folder
- **Parameter Templates**: See `bundle/job_parameters.conf`
- **Databricks Bundles**: [Official Documentation](https://docs.databricks.com/dev-tools/bundles/)

## 📞 Getting Help

1. **Quick Start**: Read `docs/QUICKSTART.md`
2. **Examples**: Check `docs/EXAMPLES.md` for 19+ templates
3. **Troubleshooting**: Review `docs/TROUBLESHOOTING.md`
4. **Full Guide**: Read `docs/DEPLOYMENT.md`

## ✅ Prerequisites

- Databricks workspace with Unity Catalog
- Access to AI foundational models
- Databricks CLI (for job deployment)
- Appropriate permissions (create jobs, clusters, tables)

## 🎉 Quick Commands

```bash
# Validate configuration
cd bundle && databricks bundle validate -t dev

# Deploy to dev
databricks bundle deploy -t dev

# Run a job
databricks bundle run generate_patients_job -t dev

# List deployed jobs
databricks bundle jobs list -t dev

# Destroy deployment
databricks bundle destroy -t dev
```

## 📝 License

This tool is provided as-is for use with Databricks workspaces that have access to AI foundational models.

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Compatible with:** Databricks Runtime 13.0+

**Ready to generate data? Start with `docs/QUICKSTART.md`!** 🚀
