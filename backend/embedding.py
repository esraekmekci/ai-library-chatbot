from langchain_google_vertexai import VertexAIEmbeddings
import vertexai
from .config import PROJECT_ID, REGION

vertexai.init(project=PROJECT_ID, location=REGION)

def get_embeddings():
    return VertexAIEmbeddings(model="text-embedding-005")
#BAAI/bge-m3  yeni ve ggucluymus
#intfloat/multilingual-e5-small query ve passage kullanılıyor