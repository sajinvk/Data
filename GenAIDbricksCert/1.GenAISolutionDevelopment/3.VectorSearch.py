{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Databricks notebook (Python)\n",
    "# Install SDK (if not already installed)\n",
    "# %pip install databricks-vectorsearch\n",
    "# dbutils.library.restartPython()\n",
    "\n",
    "from databricks.vector_search.client import VectorSearchClient\n",
    "\n",
    "client = VectorSearchClient()\n",
    "\n",
    "# 1) Create a Vector Search endpoint (STANDARD or STORAGE_OPTIMIZED)\n",
    "endpoint_name = \"vs-endpoint-prod\"\n",
    "client.create_endpoint(name=endpoint_name, endpoint_type=\"STANDARD\")\n",
    "\n",
    "# 2) Create a Delta Sync index from a Delta table\n",
    "index_name = \"catalog.schema.my_delta_sync_index\"\n",
    "primary_key = \"id\"\n",
    "\n",
    "index = client.create_delta_sync_index(\n",
    "    endpoint_name=endpoint_name,\n",
    "    index_name=index_name,\n",
    "    source_table=\"catalog.schema.source_documents\",  # your Delta table\n",
    "    primary_key=primary_key,\n",
    "    embedding_source_column=\"text\",                  # text to embed\n",
    "    # OR if you already have vectors in table:\n",
    "    # embedding_vector_column=\"text_vector\",\n",
    "    pipeline_type=\"CONTINUOUS\",                     # or \"TRIGGERED\"\n",
    "    columns_to_sync=[\"id\", \"text\", \"title\", \"tags\"] # optional subset of columns\n",
    ")\n",
    "\n",
    "# 3) (Optional) Trigger a one-off sync if using TRIGGERED\n",
    "client.get_index(index_name).sync()  # equivalent to REST /sync for Delta Sync          \n"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  },
  "orig_nbformat": 4
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
