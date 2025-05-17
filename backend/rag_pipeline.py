from .embedding import get_embeddings
from langchain_pinecone import PineconeVectorStore
from .config import PINECONE_API_KEY, PINECONE_ENV
from pinecone import Pinecone
import datetime
import numpy as np

#caching icin embedingi globalde yapmamın sebebi vertex ai da kotayı daha yavaş harcamak
VECTORSTORES = None  # caching için
EMBEDDING_MODEL = None  

def load_prompt_template(file_path="prompts/answer_generation_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{date}}", datetime.datetime.now().strftime("%Y-%m-%d")).strip() + "\n"

def load_preprocess_prompt(file_path="prompts/query_preprocess_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{date}}", datetime.datetime.now().strftime("%Y-%m-%d")).strip() + "\n"

def get_all_vectorstores():
    global VECTORSTORES, EMBEDDING_MODEL

    if VECTORSTORES is not None:
        return VECTORSTORES

    pc = Pinecone(api_key=PINECONE_API_KEY)

    # embedding model sadece bir kez alınır
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = get_embeddings()

    index_names = [
        "general-index",
        "guides-index",
        "book-index"
    ]

    vectorstores = []
    for name in index_names:
        index = pc.Index(name)
        vectorstore = PineconeVectorStore(index=index, embedding=EMBEDDING_MODEL, text_key="page_content")
        vectorstores.append((name, vectorstore))
    
    VECTORSTORES = vectorstores
    return VECTORSTORES


def augment_prompt(query: str, chat_history=None):
    """
    Augment the query with relevant context from vector stores.
    The query is already preprocessed to include context from chat history,
    but we also include full chat history separately for LLM reference.
    
    Args:
        query: The preprocessed query from the preprocessing LLM
        chat_history: The full conversation history
    """
    system_prompt = load_prompt_template()
    vectorstores = get_all_vectorstores()
    all_results = []
    #SCORE_THRESHOLD = 0.4
    for name, store in vectorstores:
        try:
            results = store.similarity_search_with_score(query, k=5)

            # bi bunu da denicem hangisi daha iyi calisiyo diye 
            #results = store.max_marginal_relevance_search_with_score(query, k=6, fetch_k=10, lambda_mult=0.5)
            
            for doc, score in results:
                #if score >= SCORE_THRESHOLD:
                all_results.append((doc, score, name))
        except Exception as e:
            print(f"Error searching in index {name}: {e}")
            continue
    
    if not all_results:
        print("No results found in any index.")
        augmented_prompt = system_prompt.replace("{{context}}", "No relevant context found.")
    else:
        # NORMALİZASYON 
        # scores = [score for _, score, _ in all_results]
        # mean = np.mean(scores)
        # std = np.std(scores) or 1  # sıfıra bölme hatası engelleniyor

        all_results.sort(key=lambda x: x[1], reverse=True)


        # normalized_results = [
        #     (doc, (score - mean) / std, index_name)
        #     for doc, score, index_name in all_results
        # ]

        # Normalize edilmiş skorlarla sırala
        # normalized_results.sort(key=lambda x: x[1], reverse=True)

        # Get the top 10 results
        top_contexts = [
            f"From: {index_name}\nDocument: {doc.page_content}\nSource URL: {doc.metadata.get('source_url', '')}\nNormalized Score: {score:.2f}"
            for doc, score, index_name in all_results[:10]
        ]

        context_block = "\n\n".join(top_contexts)
        augmented_prompt = system_prompt.replace("{{context}}", context_block)
    
    # Always include the preprocessed query
    augmented_prompt = augmented_prompt.replace("{{query}}", query)
    
    # Include the full chat history if provided
    if chat_history and len(chat_history) > 0:
        history_text = format_chat_history(chat_history)
        augmented_prompt = augmented_prompt.replace("{{chat_history}}", history_text)
    else:
        augmented_prompt = augmented_prompt.replace("{{chat_history}}", "No previous conversation history available.")
    
    return augmented_prompt

def format_chat_history(chat_history):
    """Format chat history into a readable string for the LLM."""
    if not chat_history or len(chat_history) == 0:
        return "No previous conversation history available."
        
    formatted_history = []
    # Add a timestamp for reference
    formatted_history.append(f"Conversation history as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
    
    # Number each exchange for clarity
    message_counter = 1
    for message in chat_history:
        role = message.get("role", "").upper()
        content = message.get("content", "")
        if role and content:
            # Format with clear delineation between messages
            formatted_history.append(f"[{message_counter}] {role}: {content}")
            message_counter += 1
    
    if len(formatted_history) > 1:  # Check if we have actual messages beyond the timestamp
        return "\n\n".join(formatted_history)
    return "No previous conversation history available."
