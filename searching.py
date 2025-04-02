from elasticsearch import Elasticsearch
import json

# Config
ES_HOST = "https://localhost:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "PI2YFhUS4ycPWNw8VdcX"
INDEX_NAME = "imageindex"

# Connect to Elasticsearch
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False
)

# Check connection
if not es.ping():
    raise ValueError("Could not connect to Elasticsearch")
else:
    print("Connected to Elasticsearch!")

# ---- SEARCH CONFIG ----
query_text = "child ball"

# Use match query for full-text search with fuzziness
query = {
    "match": {
        "response": {
            "query": query_text,
            "fuzziness": "AUTO"
        }
    }
}

# Perform search
res = es.search(index=INDEX_NAME, query=query)

# Display results
hits = res["hits"]["hits"]
print(f"Found {len(hits)} result(s):\n")

for i, hit in enumerate(hits, 1):
    print(f"Result {i}:")
    print("Image Path:", hit["_source"]["image_path"])
    print("Response:", hit["_source"]["response"])
    print("-" * 40)
