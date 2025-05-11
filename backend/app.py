from langchain_ollama import OllamaLLM
from .rag_pipeline import augment_prompt
from langchain_google_vertexai import VertexAI

llm_model = VertexAI(
    model_name="gemini-2.0-flash-001", 
    temperature=0.2,
    max_output_tokens=1024
)

def ask(query: str) -> str:
    augmented = augment_prompt(query)
    print("\n--- AUGMENTED PROMPT ---\n")
    print(augmented)
    response = llm_model.invoke(augmented)
    return response.strip()

# llm_model = OllamaLLM(model="llama3.1:8b")

# def ask(query: str) -> str:
#     augmented = augment_prompt(query)
#     print(augmented)
#     result = llm_model.generate([augmented])
#     return result.generations[0][0].text.strip()
