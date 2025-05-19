from langchain_ollama import OllamaLLM
from .rag_pipeline import augment_prompt, load_preprocess_prompt, format_chat_history
from langchain_google_vertexai import VertexAI
from html import unescape
import re
import json

def clean_llm_output(output: str) -> str:
    output = re.sub(r"<br\s*/?>", "\n", output)
    output = re.sub(r"<.*?>", "", output)
    return unescape(output).strip()

def clean_llm_output_full(raw_text: str) -> str:
    if raw_text.strip().startswith("```"):
        raw_text = "\n".join(
            line for line in raw_text.splitlines() if not line.strip().startswith("```")
        )

    text = re.sub(r"<br\s*/?>", "\n", raw_text)
    text = re.sub(r"<.*?>", "", text)

    return  json.loads(unescape(text).strip())

llm_model = VertexAI(
    model_name="gemini-2.0-flash-001", 
    temperature=0.2,
    max_output_tokens=1024
)

def ask(query: str, chat_history=None) -> tuple:
    """
    Process user query and generate a response.
    
    Args:
        query: The raw user query
        chat_history: Previous conversation history
    
    Returns:
        tuple: (response, preprocessed_query) - The LLM's response and the preprocessed version of the query
    """
    # Preprocess the current query with chat history context
    preprocess_prompt_template = load_preprocess_prompt()
    preprocess_prompt = preprocess_prompt_template.replace("{{query}}", query)
    
    # Include chat history in the preprocessing step
    if chat_history and len(chat_history) > 0:
        history_text = format_chat_history(chat_history)
        preprocess_prompt = preprocess_prompt.replace("{{chat_history}}", history_text)
    else:
        preprocess_prompt = preprocess_prompt.replace("{{chat_history}}", "No previous conversation.")
    
    # Get the preprocessed query that now includes context from chat history
    preprocessed_query = clean_llm_output_full(llm_model.invoke(preprocess_prompt))

    print("\n--- PREPROCESSED QUERY ---\n")
    print(preprocessed_query)
    print("\n--- END OF PREPROCESSED QUERY ---\n")

    # Augment the query with relevant context from vector stores
    # Still pass chat_history to include it in the answer generation prompt
    # but the query itself is already the preprocessed one
    augmented_query = augment_prompt(preprocessed_query, chat_history)

    print("\n--- AUGMENTED PROMPT ---\n")
    print(augmented_query)
    print("\n--- END OF AUGMENTED PROMPT ---\n")
    
    response = clean_llm_output(llm_model.invoke(augmented_query))
    
    # Return both the response and the preprocessed query
    return response.strip(), preprocessed_query