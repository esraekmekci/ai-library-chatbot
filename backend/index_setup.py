from .config import PINECONE_API_KEY, INDEX_NAME, PINECONE_ENV
from .embedding import get_embeddings
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
import time

def load_faq_data(filename="data/raw/faqs.txt"):
    faqs = []
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().split('\n\n')
        for entry in content:
            lines = entry.split("\n")
            if len(lines) >= 2:
                question = lines[0].replace("Question: ", "").strip()
                answer = lines[1].replace("Answer: ", "").strip()
                faqs.append({"question": question, "answer": answer})
    return faqs

def setup_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

    if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(INDEX_NAME, dimension=768, metric='cosine', spec=spec)
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)

    index = pc.Index(INDEX_NAME)
    time.sleep(1)
    
    if index.describe_index_stats()["total_vector_count"] == 0:
        data = load_faq_data()
        embedder = get_embeddings()
        batch_size = 5
        for i in tqdm(range(0, len(data), batch_size)):
            i_end = min(len(data), i + batch_size)
            batch = data[i:i_end]
            ids = [f"faq-{i + j}" for j, _ in enumerate(batch)]
            texts = [f"Question: {item['question']} Answer: {item['answer']}" for item in batch]
            embeds = embedder.embed_documents(texts)
            metadata = [
                {"Question": item["question"], "Answer": item["answer"]} for item in batch
            ]
            index.upsert(vectors=zip(ids, embeds, metadata))
            time.sleep(60)

if __name__ == "__main__":
    setup_index()
