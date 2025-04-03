import customtkinter as ctk
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
ES_HOST = os.getenv("ES_HOST")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
INDEX_NAME = "imageindex"

# Connect to Elasticsearch
es = Elasticsearch(
    [ES_HOST],
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False
)

if not es.ping():
    raise ValueError("Could not connect to Elasticsearch")

# Set up UI theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create main window
app = ctk.CTk()
app.geometry("800x600")
app.title("🖼️ MemoryLens — Image Search")

# Title
title_label = ctk.CTkLabel(
    app,
    text="Search for memories 🔎",
    font=ctk.CTkFont(size=22, weight="bold")
)
title_label.pack(pady=20)

# Search input
search_entry = ctk.CTkEntry(
    app,
    width=500,
    height=40,
    placeholder_text="Try: 'child playing ball'"
)
search_entry.pack(pady=10)

# Search results textbox
results_box = ctk.CTkTextbox(
    app,
    width=700,
    height=350,
    wrap="word",
    font=("Segoe UI", 12)
)
results_box.pack(pady=20)
results_box.configure(state="disabled")

# Search logic
def search_es():
    query_text = search_entry.get().strip()
    results_box.configure(state="normal")
    results_box.delete("1.0", "end")

    if not query_text:
        results_box.insert("end", "Search 🔎")
        results_box.configure(state="disabled")
        return

    query = {
        "match": {
            "response": {
                "query": query_text,
                "fuzziness": "AUTO"
            }
        }
    }

    try:
        res = es.search(index=INDEX_NAME, query=query)
        hits = res["hits"]["hits"]

        if not hits:
            results_box.insert("end", "No results found.")
        else:
            for i, hit in enumerate(hits, 1):
                source = hit["_source"]
                result = (
                    f"Result {i}:\n"
                    f"📍 Image Path: {source['image_path']}\n"
                    f"📝 Description: {source['response']}\n"
                    + "-" * 60 + "\n"
                )
                results_box.insert("end", result)

    except Exception as e:
        results_box.insert("end", f"Error: {str(e)}")

    results_box.configure(state="disabled")

# Search button
search_button = ctk.CTkButton(
    app,
    text="Search",
    command=search_es,
    width=160,
    height=40
)
search_button.pack(pady=10)

# Launch app
app.mainloop()
