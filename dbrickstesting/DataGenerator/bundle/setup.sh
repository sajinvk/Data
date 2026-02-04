#!/bin/bash

# Setup Script for AI Data Generator
# This script uploads the notebook to your Databricks workspace

echo "🚀 Setting up AI Data Generator..."
echo ""

# Configuration
NOTEBOOK_PATH="/Workspace/Users/shreya.sharma@databricks.com/ausunity/DataGenerator/ai_data_generator"
LOCAL_NOTEBOOK="../ai_data_generator.py"

echo "📝 Configuration:"
echo "  Local notebook: $LOCAL_NOTEBOOK"
echo "  Workspace path: $NOTEBOOK_PATH"
echo ""

# Check if local notebook exists
if [ ! -f "$LOCAL_NOTEBOOK" ]; then
    echo "❌ Error: Notebook not found at $LOCAL_NOTEBOOK"
    echo "   Make sure you're running this script from the bundle/ directory"
    exit 1
fi

echo "1️⃣ Creating workspace directory..."
databricks workspace mkdirs /Workspace/Users/shreya.sharma@databricks.com/ausunity/DataGenerator/

echo "2️⃣ Uploading notebook to workspace..."
databricks workspace import $LOCAL_NOTEBOOK $NOTEBOOK_PATH --language PYTHON --overwrite

echo "3️⃣ Verifying upload..."
if databricks workspace get-status $NOTEBOOK_PATH &> /dev/null; then
    echo "   ✅ Notebook uploaded successfully!"
else
    echo "   ❌ Failed to upload notebook"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Deploy the bundle:"
echo "      databricks bundle deploy -t dev"
echo ""
echo "   2. Run a job:"
echo "      databricks bundle run generate_patients_job -t dev"
echo ""
echo "📌 Notebook location: $NOTEBOOK_PATH"
echo ""
