from langchain_ollama import OllamaLLM
from .rag_pipeline import augment_prompt, load_preprocess_prompt
from langchain_google_vertexai import VertexAI
from html import unescape
import re

def clean_llm_output(output: str) -> str:
    output = re.sub(r"<br\s*/?>", "\n", output)
    output = re.sub(r"<.*?>", "", output)
    return unescape(output).strip()

llm_model = VertexAI(
    model_name="gemini-2.0-flash-001", 
    temperature=0.2,
    max_output_tokens=1024
)

def ask(query: str) -> str:
    preprocess_prompt_template = load_preprocess_prompt()
    preprocess_prompt = preprocess_prompt_template.replace("{{query}}", query)
    preprocessed_query = clean_llm_output(llm_model.invoke(preprocess_prompt))

    print("\n--- PREPROCESSED QUERY ---\n")
    print(preprocessed_query)
    print("\n--- END OF PREPROCESSED QUERY ---\n")

    augmented_query = augment_prompt(preprocessed_query)

    print("\n--- AUGMENTED PROMPT ---\n")
    print(augmented_query)
    print("\n--- END OF AUGMENTED PROMPT ---\n")
    
    response = clean_llm_output(llm_model.invoke(augmented_query))
    return response.strip()