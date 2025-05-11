from .embedding import get_embeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from .config import PINECONE_API_KEY, PINECONE_ENV
from pinecone import Pinecone
import datetime

def get_all_vectorstores():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    embedding_model = get_embeddings()

    index_names = [
        "faq-index",
        "announcements-index",
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
    vectorstores = get_all_vectorstores()
    all_results = []

    for name, store in vectorstores:
        try:
            results = store.similarity_search_with_score(query, k=3)
            for doc, score in results:
                all_results.append((doc, score, name))
        except Exception as e:
            print(f"Error searching in index {name}: {e}")
            continue
    
    if not all_results:
        return f"""<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
No relevant context was found.
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Query: {query}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""

    all_results.sort(key=lambda x: x[1], reverse=True)
    top_result = all_results[0][0]

    # Get the top 3 results
    top_contexts = [
        f"From: {index_name}\nDocument: {doc.page_content}\nSource URL: {doc.metadata.get('source_url', '')}\nScore: {score:.2f}"
        for doc, score, index_name in all_results[:3]
    ]

    context_block = "\n\n".join(top_contexts)

    return f"""<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}.
You are an AI assistant for the IZTECH Library. Use only the context below to answer the question. If unsure, say you don't know.
At the end of your answer, include the source link from the context.

Context:
{context_block}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Query: {query}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""
