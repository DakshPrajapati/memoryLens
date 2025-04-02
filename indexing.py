from elasticsearch import Elasticsearch, helpers
import json

# Config
ES_HOST = "https://localhost:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "PI2YFhUS4ycPWNw8VdcX"
INDEX_NAME = "imageindex"
JSON_FILE = "responses.json"

# Connect
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False
)

if not es.ping():
    raise ValueError("Connection failed")
print("Connected to Elasticsearch!")

# Ensure index exists
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)
    print(f"Created index '{INDEX_NAME}'")

# Load JSON data
with open(JSON_FILE, "r") as f:
    data = json.load(f)

# Build actions
actions = [
    {
        "_index": INDEX_NAME,
        "_source": {
            "image_path": doc["image_path"].replace("\\", "/"),
            "response": doc["response"]
        }
    }
    for doc in data
]

# Bulk index with error handling
try:
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} documents into '{INDEX_NAME}' index.")
except helpers.BulkIndexError as e:
    print("❌ Bulk indexing failed:")
    for err in e.errors:
        print(err)
