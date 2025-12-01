# Databricks notebook (Python)
# Install SDK (if not already installed)
# %pip install databricks-vectorsearch
# dbutils.library.restartPython()

from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# 1) Create a Vector Search endpoint (STANDARD or STORAGE_OPTIMIZED)
endpoint_name = "vs-endpoint-prod"
client.create_endpoint(name=endpoint_name, endpoint_type="STANDARD")

# 2) Create a Delta Sync index from a Delta table
index_name = "catalog.schema.my_delta_sync_index"
primary_key = "id"

index = client.create_delta_sync_index(
    endpoint_name=endpoint_name,
    index_name=index_name,
    source_table="catalog.schema.source_documents",  # your Delta table
    primary_key=primary_key,
    embedding_source_column="text",                  # text to embed
    # OR if you already have vectors in table:
    # embedding_vector_column="text_vector",
    pipeline_type="CONTINUOUS",                     # or "TRIGGERED"
    columns_to_sync=["id", "text", "title", "tags"] # optional subset of columns
)

# 3) (Optional) Trigger a one-off sync if using TRIGGERED
client.get_index(index_name).sync()  # equivalent to REST /sync for Delta Sync          


#-- ANN: query by text (embedding computed by the index's model endpoint)
SELECT *
FROM vector_search(
  index         => 'catalog.schema.my_delta_sync_index',
  query_text    => 'cloud migration plan for retail',
  num_results   => 10
);

#-- Hybrid: combine keyword + similarity
SELECT *
FROM vector_search(
  index         => 'catalog.schema.my_delta_sync_index',
  query_text    => 'SKU-8897 migration blueprint',
  query_type    => 'HYBRID',
  num_results   => 10
);

#-- ANN: query by self-managed vector (if you stored vectors in the Delta table)
SELECT *
FROM vector_search(
  index         => 'catalog.schema.my_delta_sync_index',
  query_vector  => array(0.12, -0.05, ...), #-- your normalized vector
  num_results   => 10
);




# Databricks notebook (Python)
from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

endpoint_name = "vs-endpoint-direct"
client.create_endpoint(name=endpoint_name, endpoint_type="STANDARD")

index_name = "catalog.schema.my_direct_index"

index = client.create_direct_access_index(
    endpoint_name=endpoint_name,
    index_name=index_name,
    primary_key="id",
    embedding_dimension=1024,
    embedding_vector_column="text_vector",
    schema={
        "id": "string",
        "title": "string",
        "text": "string",
        "tags": "array<string>",
        "text_vector": "array<float>"
    }
)



# Example batch upsert
rows = [
    {
        "id": "doc-001",
        "title": "Blueprint A",
        "text": "This document describes the migration plan.",
        "tags": ["plan", "retail"],
        "text_vector": [0.013, -0.08, ...]  # your computed (and normalized) vector
    },
    {
        "id": "doc-002",
        "title": "Blueprint B",
        "text": "Steps to implement phase two.",
        "tags": ["plan", "phase2"],
        "text_vector": [0.021, -0.05, ...]
    }
]

client.get_index(index_name).upsert(rows)  # upsert into Direct Access index



results = client.get_index(index_name).similarity_search(
    query_vector=[0.017, -0.06, ...],  # normalized query vector
    num_results=10,
    filters={"tags": ["retail"]}       # optional metadata filters
)
for r in results:
    print(r["id"], r["score"])
