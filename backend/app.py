from langchain_ollama import OllamaLLM
from .rag_pipeline import augment_prompt

llm_model = OllamaLLM(model="llama3.1:8b")

def ask(query: str) -> str:
    augmented = augment_prompt(query)
    print(augmented)
    result = llm_model.generate([augmented])
    return result.generations[0][0].text.strip()
