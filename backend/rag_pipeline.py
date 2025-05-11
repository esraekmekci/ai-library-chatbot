from .embedding import get_embeddings
from langchain_pinecone import PineconeVectorStore
from .config import INDEX_NAME, PINECONE_API_KEY, PINECONE_ENV
from pinecone import Pinecone

def get_vectorstore():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    return PineconeVectorStore(index=index, embedding=get_embeddings(), text_key="Question")

def augment_prompt(query: str):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=5)
    results.sort(key=lambda x: x[1], reverse=True)
    top_result = results[0][0]
    contexts = [
        f"Question: {result[0].page_content}\nAnswer: {result[0].metadata['Answer']}\nScore: {result[1]}"
        for result in results
    ]

    return f"""<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
You are an AI chatbot assisting users with the IZTECH Library. Only use the provided context to answer.
Context:
{top_result.page_content} - {top_result.metadata['Answer']}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Query: {query}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""
