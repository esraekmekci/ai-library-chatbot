from .config import PINECONE_API_KEY, PINECONE_ENV
from .embedding import get_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from tqdm.auto import tqdm
import time
from importlib import import_module

SCRAPER_CONFIGS = {
    "faq": {
        "module": "scripts.scrape_faqs",
        "function": "scrape_faqs",
        "index_name": "faq-index",
        "dimension": 768
    },
    "announcements": {
        "module": "scripts.scrape_announcements",
        "function": "scrape_announcements",
        "index_name": "announcements-index",
        "dimension": 768
    },
    "usage": {
        "module": "scripts.scrape_usage",
        "function": "scrape_usage",
        "index_name": "usage-index",
        "dimension": 768
    },
    "pickedups": {
        "module": "scripts.scrape_pickedups",
        "function": "scrape_pickedups",
        "index_name": "pickedups-index",
        "dimension": 768
    }
    # "events": {
    #     "module": "scrapers.scrape_events",
    #     "function": "scrape_events",
    #     "index_name": "events-index",
    #     "dimension": 768
    # },
    # "tools": {
    #     "module": "scrapers.scrape_tools",
    #     "function": "scrape_tools",
    #     "index_name": "tools-index",
    #     "dimension": 768
    # },
    # "databases": {
    #     "module": "scrapers.scrape_databases",
    #     "function": "scrape_databases",
    #     "index_name": "databases-index",
    #     "dimension": 768
    # }
}

def setup_index(key: str):
    config = SCRAPER_CONFIGS[key]
    module = import_module(config["module"])
    scrape_function = getattr(module, config["function"])
    docs = scrape_function()

    if not docs:
        print(f"[{key}] No documents found. Skipping.")
        return
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

    if config["index_name"] not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(config["index_name"], dimension=config["dimension"], metric='cosine', spec=spec)
        while not pc.describe_index(config["index_name"]).status['ready']:
            time.sleep(1)

    index = pc.Index(config["index_name"])
    time.sleep(1)

    if index.describe_index_stats().total_vector_count > 0:
        print(f"[{key}] Deleting existing vectors...")
        index.delete(delete_all=True)
        time.sleep(2)
    
    embedder = get_embeddings()

    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embedder,
        text_key="page_content"  # this will be filled from Document.page_content
    )

    langchain_docs = [
        Document(page_content=doc["text"], metadata=doc["metadata"])
        for doc in docs
    ]

    print(f"[{key}] Adding {len(langchain_docs)} documents...")
    vectorstore.add_documents(langchain_docs)

    print(f"[{key}] Indexing complete.")
if __name__ == "__main__":
    for key in SCRAPER_CONFIGS.keys():
        setup_index(key)
