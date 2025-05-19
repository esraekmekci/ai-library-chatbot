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
        "index_name": "general-index",
        "dimension": 768
    },
    "announcements": {
        "module": "scripts.scrape_announcements",
        "function": "scrape_announcements",
        "index_name": "general-index",
        "dimension": 768
    },
    "guides": {
        "module": "scripts.scrape_guides",
        "function": "scrape_guides",
        "index_name": "guides-index",
        "dimension": 768
    },
    "databases": {
        "module": "scripts.scrape_databases",
        "function": "scrape_databases",
        "index_name": "general-index",
        "dimension": 768
    },
    "usage": {
        "module": "scripts.scrape_usage",
        "function": "scrape_usage",
        "index_name": "general-index",
        "dimension": 768
    },
    "pickedups": {
        "module": "scripts.scrape_pickedups",
        "function": "scrape_pickedups",
        "index_name": "general-index",
        "dimension": 768
    },
    "book_loc": {
        "module": "scripts.scrape_books_with_locations",
        "function": "scrape_book_locations",
        "index_name": "book-index",
        "dimension": 768
    },
    "book_facets": {
        "module": "scripts.scrape_book_collection",
        "function": "scrape_book_facets",
        "index_name": "book-index",
        "dimension": 768
    },
    "thesis_facets": {
        "module": "scripts.scrape_thesis_collection",
        "function": "scrape_thesis_facets",
        "index_name": "article-index",
        "dimension": 768
    },
    "article_facets": {
        "module": "scripts.scrape_article_collection",
        "function": "scrape_article_facets",
        "index_name": "article-index",
        "dimension": 768
    }
}

def batch_add_documents(vectorstore, documents, batch_size=10, wait_time=30):
    total = len(documents)
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        print(f"Uploading batch {i//batch_size + 1} with {len(batch)} documents...")
        vectorstore.add_documents(batch)
        if i + batch_size < total:
            print(f"Waiting {wait_time} seconds before next batch...")
            time.sleep(wait_time)
    print("All documents uploaded.")

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

    # if index.describe_index_stats().total_vector_count > 0:
    #     print(f"[{key}] Deleting existing vectors...")
    #     index.delete(delete_all=True)
    #     time.sleep(2)
    
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

    batch_add_documents(vectorstore, langchain_docs, batch_size=20, wait_time=15)

    print(f"[{key}] Indexing complete.")
if __name__ == "__main__":
    # for key in SCRAPER_CONFIGS.keys():
    #     setup_index(key)
    setup_index("thesis_facets")
