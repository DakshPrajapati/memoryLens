import json
from elasticsearch import Elasticsearch, helpers, exceptions

def upload_to_elasticsearch(file_path, index_name, es_host="http://localhost:9200"):
    try:
        # Connect to Elasticsearch
        es = Elasticsearch(es_host)
        if not es.ping():
            raise ConnectionError("Connection to Elasticsearch failed.")
        print("✅ Connected to Elasticsearch.")

        # Read JSON file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                records = json.load(file)
        except FileNotFoundError:
            print(f"❌ File '{file_path}' not found.")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
            return

        # Prepare data
        actions = [
            {
                "_index": index_name,
                "_source": record
            }
            for record in records
        ]

        # Create index if not exists
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
            print(f"📁 Index '{index_name}' created.")

        # Bulk upload
        helpers.bulk(es, actions)
        print(f"✅ Uploaded {len(actions)} documents to '{index_name}' index.")

    except exceptions.ConnectionError as e:
        print("❌ Connection error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)

# Run the function
if __name__ == "__main__":
    upload_to_elasticsearch("your_file.json", "image_descriptions")
