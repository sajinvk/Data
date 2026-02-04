# AI Data Generator - Architecture & Workflow

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Data Generator System                      │
│                                                                  │
│  Input: Industry + Domain + Schema (optional) + Constraints     │
│                            ↓                                     │
│         Databricks AI Foundational Models (LLMs)                │
│                            ↓                                     │
│  Output: Realistic, Context-Aware Delta Table                   │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Diagram

```
┌──────────────────┐
│ User Input       │
│ ┌──────────────┐ │
│ │ Industry     │ │ ──┐
│ │ Domain       │ │   │
│ │ Table Name   │ │   │
│ │ # Rows       │ │   │
│ └──────────────┘ │   │
└──────────────────┘   │
                       │
┌──────────────────┐   │
│ Schema Input     │   │
│ ┌──────────────┐ │   │
│ │ Option A:    │ │   │
│ │ Custom       │ │   ├──► Step 1: Schema Generation
│ │ Schema       │ │   │
│ │              │ │   │          ┌─────────────────┐
│ │ Option B:    │ │   │          │ If no custom    │
│ │ AI-Generated │ │ ──┘          │ schema:         │
│ │ Schema       │ │              │                 │
│ └──────────────┘ │              │ ai_query()      │
└──────────────────┘              │    +            │
                                  │ Industry/Domain │
                                  │       ↓         │
                                  │ JSON Schema     │
                                  └─────────────────┘
                                          │
┌──────────────────┐                      │
│ Constraints      │                      │
│ ┌──────────────┐ │                      │
│ │ Column 1:    │ │                      │
│ │ "range 1-100"│ │ ──┐                  │
│ │              │ │   │                  │
│ │ Column 2:    │ │   ├──► Step 2: Data Generation
│ │ "between     │ │   │                  │
│ │  10-500"     │ │   │          ┌───────▼─────────┐
│ └──────────────┘ │   │          │ For each row:   │
└──────────────────┘   │          │                 │
                       │          │ ai_query()      │
                       └─────────►│    +            │
                                  │ Schema          │
                                  │    +            │
                                  │ Constraints     │
                                  │    +            │
                                  │ Industry/Domain │
                                  │       ↓         │
                                  │ JSON Row Data   │
                                  └─────────────────┘
                                          │
                                          │
                                  ┌───────▼─────────┐
                                  │ Type Conversion │
                                  │                 │
                                  │ String → INT    │
                                  │ String → DOUBLE │
                                  │ String → DATE   │
                                  │ etc.            │
                                  └─────────────────┘
                                          │
                                          │
                                  ┌───────▼─────────┐
                                  │ DataFrame       │
                                  │ Creation        │
                                  │                 │
                                  │ PySpark Schema  │
                                  │ + Row Data      │
                                  └─────────────────┘
                                          │
                                          │
                                  ┌───────▼─────────┐
                                  │ Delta Table     │
                                  │                 │
                                  │ Save to Unity   │
                                  │ Catalog         │
                                  └─────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ai_data_generator.py                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Configuration Section                                   │    │
│  │ • INDUSTRY                                              │    │
│  │ • DOMAIN                                                │    │
│  │ • TABLE_NAME                                            │    │
│  │ • CUSTOM_SCHEMA (optional)                              │    │
│  │ • COLUMN_CONSTRAINTS (optional)                         │    │
│  │ • AI_MODEL_ENDPOINT                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Schema Generation Module                                │    │
│  │                                                          │    │
│  │ • generate_schema_with_ai()                             │    │
│  │   - Builds AI prompt with industry/domain               │    │
│  │   - Calls ai_query()                                    │    │
│  │   - Parses JSON response                                │    │
│  │                                                          │    │
│  │ • convert_schema_to_struct()                            │    │
│  │   - Maps string types to PySpark types                  │    │
│  │   - Creates StructType schema                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Data Generation Module                                  │    │
│  │                                                          │    │
│  │ • generate_row_with_ai()                                │    │
│  │   - Builds row-specific prompt                          │    │
│  │   - Includes schema + constraints                       │    │
│  │   - Calls ai_query()                                    │    │
│  │   - Parses and converts data types                      │    │
│  │                                                          │    │
│  │ • generate_table_data()                                 │    │
│  │   - Loops through NUM_ROWS                              │    │
│  │   - Calls generate_row_with_ai() for each              │    │
│  │   - Handles failures with fallback data                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ DataFrame & Storage Module                              │    │
│  │                                                          │    │
│  │ • spark.createDataFrame()                               │    │
│  │   - Applies PySpark schema                              │    │
│  │   - Validates data types                                │    │
│  │                                                          │    │
│  │ • df.write.format("delta").saveAsTable()                │    │
│  │   - Saves to Unity Catalog                              │    │
│  │   - Creates Delta table                                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Example: Healthcare Patient Records

```
Input:
┌────────────────────────────────────┐
│ INDUSTRY = "healthcare"            │
│ DOMAIN = "patient records"         │
│ TABLE_NAME = "patients"            │
│ CUSTOM_SCHEMA = None               │
│ COLUMN_CONSTRAINTS = {             │
│   "patient_id": "start from 10000" │
│   "age": "between 18-95"           │
│ }                                  │
└────────────────────────────────────┘
         │
         ▼
Step 1: Schema Generation
┌────────────────────────────────────┐
│ AI Prompt:                         │
│ "Generate schema for 'patients'    │
│  table in healthcare industry for  │
│  patient records..."               │
└────────────────────────────────────┘
         │
         ▼ ai_query()
┌────────────────────────────────────┐
│ AI Response (JSON):                │
│ {                                  │
│   "patient_id": "INT",             │
│   "first_name": "STRING",          │
│   "last_name": "STRING",           │
│   "date_of_birth": "DATE",         │
│   "diagnosis": "STRING",           │
│   "admission_date": "TIMESTAMP",   │
│   "insurance_provider": "STRING"   │
│ }                                  │
└────────────────────────────────────┘
         │
         ▼
Step 2: Data Generation (for each row)
┌────────────────────────────────────┐
│ AI Prompt for Row 1:               │
│ "Generate data for 'patients'      │
│  table in healthcare...            │
│                                    │
│ Schema:                            │
│  patient_id (INT): start from      │
│    10000                           │
│  age: between 18-95                │
│  ... (other columns)               │
│                                    │
│ This is row #1"                    │
└────────────────────────────────────┘
         │
         ▼ ai_query()
┌────────────────────────────────────┐
│ AI Response (JSON):                │
│ {                                  │
│   "patient_id": "10001",           │
│   "first_name": "Sarah",           │
│   "last_name": "Johnson",          │
│   "date_of_birth": "1985-04-12",   │
│   "diagnosis": "Type 2 Diabetes",  │
│   "admission_date":                │
│     "2024-01-15 09:30:00",         │
│   "insurance_provider":            │
│     "Blue Cross"                   │
│ }                                  │
└────────────────────────────────────┘
         │
         ▼ Type Conversion
┌────────────────────────────────────┐
│ Converted Row:                     │
│ {                                  │
│   "patient_id": 10001,        (int)│
│   "first_name": "Sarah",   (string)│
│   "last_name": "Johnson",  (string)│
│   "date_of_birth":          (date) │
│     date(1985, 4, 12),             │
│   "diagnosis":             (string)│
│     "Type 2 Diabetes",             │
│   "admission_date":     (timestamp)│
│     datetime(2024,1,15,9,30,0),    │
│   "insurance_provider": (string)   │
│     "Blue Cross"                   │
│ }                                  │
└────────────────────────────────────┘
         │
         ▼ Repeat for all rows
┌────────────────────────────────────┐
│ DataFrame with 100 rows            │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Delta Table:                       │
│ pilotws.pilotschema.patients       │
│                                    │
│ 100 rows × 7 columns               │
└────────────────────────────────────┘
```

## Key Technologies

```
┌─────────────────────────────────────────────────────────────┐
│                        Technology Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Databricks Platform                                        │
│  ├─ Unity Catalog (table storage)                           │
│  ├─ Delta Lake (table format)                               │
│  └─ AI Foundational Models                                  │
│     ├─ Meta LLaMA 3.3 70B (recommended)                     │
│     ├─ Meta LLaMA 3.1 70B                                   │
│     ├─ DBRX Instruct                                        │
│     └─ Mixtral 8x7B                                         │
│                                                              │
│  PySpark                                                    │
│  ├─ DataFrame API                                           │
│  ├─ SQL API (for ai_query)                                 │
│  └─ Data Types (StructType, StructField, etc.)             │
│                                                              │
│  Python                                                     │
│  ├─ json (parsing AI responses)                            │
│  ├─ re (regex for text cleaning)                           │
│  └─ datetime (date/time handling)                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────┐
│                    Performance Profile                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Schema Generation:     ~5-10 seconds (one-time)            │
│  Per-Row Generation:    ~1-3 seconds per row                │
│  Type Conversion:       < 0.1 seconds per row               │
│  DataFrame Creation:    < 1 second (for 100 rows)           │
│  Delta Table Write:     ~2-5 seconds (for 100 rows)         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Total Time Estimates                                 │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  50 rows:    ~2-4 minutes                            │  │
│  │  100 rows:   ~3-6 minutes                            │  │
│  │  500 rows:   ~15-30 minutes                          │  │
│  │  1000 rows:  ~30-60 minutes                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Bottleneck: AI inference time per row                      │
│  Solution: Batch generation (run multiple times)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Comparison with Other Tools

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Feature Comparison                               │
├──────────────────────┬──────────────┬─────────────────┬─────────────────┤
│ Feature              │ AI Data Gen  │ generate_fake   │ Faker Library   │
│                      │              │ _data.py        │ (standalone)    │
├──────────────────────┼──────────────┼─────────────────┼─────────────────┤
│ Custom Industries    │ ✅ Yes       │ ❌ No           │ ❌ No           │
│ Custom Schemas       │ ✅ Yes       │ ❌ Fixed only   │ ⚠️  Manual      │
│ AI-Generated         │ ✅ Yes       │ ⚠️  Partial     │ ❌ No           │
│ Context Awareness    │ ✅ High      │ ⚠️  Limited     │ ❌ None         │
│ Column Constraints   │ ✅ Yes       │ ❌ No           │ ⚠️  Manual      │
│ Ease of Use          │ ✅ High      │ ⚠️  Medium      │ ⚠️  Low         │
│ Speed                │ ⚠️  Slow     │ ✅ Fast         │ ✅ Fast         │
│ Data Realism         │ ✅ Excellent │ ⚠️  Good        │ ⚠️  Generic     │
│ Flexibility          │ ✅ Maximum   │ ❌ Limited      │ ⚠️  Medium      │
└──────────────────────┴──────────────┴─────────────────┴─────────────────┘

Use AI Data Generator when:
  • You need custom schemas for any industry
  • Data must be highly realistic and context-aware
  • You're building demos or POCs
  • You need flexible column constraints

Use generate_fake_data.py when:
  • You need the predefined customer/product/sales schema
  • Speed is critical
  • You need large datasets (10,000+ rows)

Use Faker directly when:
  • You're writing Python scripts outside Databricks
  • You need complete programmatic control
  • You're comfortable writing custom data generation code
```

## Architecture Benefits

```
┌─────────────────────────────────────────────────────────────┐
│                          Benefits                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ Industry Agnostic                                       │
│     Works for any industry/domain combination               │
│                                                              │
│  ✅ No Coding Required                                      │
│     Configuration-driven, no Python coding needed           │
│                                                              │
│  ✅ Context-Aware Data                                      │
│     AI understands industry semantics                       │
│                                                              │
│  ✅ Flexible Schema                                         │
│     Use custom or AI-generated schemas                      │
│                                                              │
│  ✅ Fine-Grained Control                                    │
│     Column-level constraints for business rules             │
│                                                              │
│  ✅ Production-Ready Output                                 │
│     Delta tables in Unity Catalog                           │
│                                                              │
│  ✅ Reproducible                                            │
│     Configuration can be versioned and shared               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
DataGenerator/
│
├── ai_data_generator.py     [Main script - 700+ lines]
│   ├── Configuration Section (lines 1-100)
│   ├── Schema Generation (lines 100-200)
│   ├── Data Generation (lines 200-500)
│   ├── Execution & Storage (lines 500-700)
│   └── Examples & Docs (lines 700+)
│
├── README.md                [Full documentation]
│   ├── Overview
│   ├── Features
│   ├── Quick Start
│   ├── Usage Examples
│   ├── Configuration Reference
│   └── Troubleshooting
│
├── QUICKSTART.md            [3-minute getting started]
│   ├── 3-Step Process
│   ├── Common Scenarios
│   └── Quick Tips
│
├── EXAMPLES.md              [19+ ready-to-use templates]
│   ├── Healthcare (3 examples)
│   ├── Retail (3 examples)
│   ├── Finance (3 examples)
│   ├── Insurance (2 examples)
│   ├── Manufacturing (2 examples)
│   ├── Logistics (2 examples)
│   ├── Education (2 examples)
│   ├── Hospitality (1 example)
│   └── Telecommunications (1 example)
│
└── ARCHITECTURE.md          [This file]
    ├── Workflow Diagrams
    ├── Component Architecture
    ├── Data Flow Examples
    ├── Performance Profile
    └── Comparison Analysis
```

## Extension Points

Want to customize or extend the generator? Here are the key extension points:

```python
# 1. Add new data type support
# In convert_schema_to_struct():
type_mapping = {
    'DECIMAL': DecimalType(10, 2),  # Add custom types
    'ARRAY': ArrayType(StringType()),
    # ... etc
}

# 2. Add custom prompt templates
# In generate_row_with_ai():
if domain == "special_domain":
    custom_prompt = """Your custom prompt here..."""
    # Use custom_prompt instead of default

# 3. Add validation rules
# After generate_table_data():
def validate_data(df, rules):
    # Add custom validation logic
    pass

# 4. Add post-processing
# Before saving Delta table:
def post_process(df):
    # Add calculated columns
    # Apply transformations
    return df
```

---

**Last Updated:** February 2026
**Version:** 1.0
**Compatible with:** Databricks Runtime 13.0+
