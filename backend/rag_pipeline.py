from .embedding import get_embeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from .config import PINECONE_API_KEY, PINECONE_ENV
from pinecone import Pinecone
import datetime

def load_prompt_template(file_path="prompts/answer_generation_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{date}}", datetime.datetime.now().strftime("%Y-%m-%d")).strip() + "\n"

def load_preprocess_prompt(file_path="prompts/query_preprocess_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{date}}", datetime.datetime.now().strftime("%Y-%m-%d")).strip() + "\n"

def get_all_vectorstores():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    embedding_model = get_embeddings()

    index_names = [
        "faq-index",
        "announcements-index",
        "guides-index",
        "usage-index", 
        "pickedups-index"
        # "events-index",
        # "tools-index",
        # "databases-index"
    ]

    vectorstores = []
    for name in index_names:
        index = pc.Index(name)
        vectorstore = PineconeVectorStore(index=index, embedding=embedding_model, text_key="page_content")
        vectorstores.append((name, vectorstore))
    
    return vectorstores


def augment_prompt(query: str):
    system_prompt = load_prompt_template()
    vectorstores = get_all_vectorstores()
    all_results = []

    for name, store in vectorstores:
        try:
            results = store.similarity_search_with_score(query, k=3)

            # bi bunu da denicem hangisi daha iyi calisiyo diye 
            # results = store.max_marginal_relevance_search_with_score(query, k=6, fetch_k=10, lambda_mult=0.5)
            
            for doc, score in results:
                all_results.append((doc, score, name))
        except Exception as e:
            print(f"Error searching in index {name}: {e}")
            continue
    
    if not all_results:
        print("No results found in any index.")
        return system_prompt.replace("{{context}}", "No relevant context found.").replace("{{query}}", query)

    all_results.sort(key=lambda x: x[1], reverse=True)

    # Get the top 3 results
    top_contexts = [
        f"From: {index_name}\nDocument: {doc.page_content}\nSource URL: {doc.metadata.get('source_url', '')}\nScore: {score:.2f}"
        for doc, score, index_name in all_results[:3]
    ]

    context_block = "\n\n".join(top_contexts)

    augmented_prompt = system_prompt.replace("{{context}}", context_block)
    augmented_prompt = augmented_prompt.replace("{{query}}", query)

    return augmented_prompt
