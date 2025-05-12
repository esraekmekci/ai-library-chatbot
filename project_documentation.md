# AI Library Chatbot Project Documentation

This document provides a comprehensive overview of the AI Library Chatbot project, explaining each file, its purpose, and how the components interact.

## Project Overview

This is a chatbot application for the IZTECH Library that uses Retrieval-Augmented Generation (RAG) to answer user queries. The system scrapes library data, stores it in a vector database, and retrieves relevant information to enhance responses to user questions.

## File Structure

```
ai-library-chatbot/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── embedding.py
│   ├── index_setup.py
│   └── rag_pipeline.py
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── scrape_announcements.py
│   ├── scrape_faqs.py
│   └── scrape_usage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Backend Components

### `backend/config.py`

**Purpose**: Manages environment variables and configuration settings.

**Key Features**:
- Loads environment variables from a `.env` file
- Sets up Pinecone vector database configuration
- Configures Google Vertex AI settings

```python
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PROJECT_ID = os.getenv("VERTEX_PROJECT_ID")
REGION = os.getenv("VERTEX_REGION", "us-central1")
```

### `backend/embedding.py`

**Purpose**: Provides text embedding functionality using Google's Vertex AI.

**Key Features**:
- Initializes Vertex AI with project ID and region
- Creates and returns a text embedding model

```python
from langchain_google_vertexai import VertexAIEmbeddings
import vertexai
from .config import PROJECT_ID, REGION

vertexai.init(project=PROJECT_ID, location=REGION)

def get_embeddings():
    return VertexAIEmbeddings(model="text-embedding-005")
```

### `backend/rag_pipeline.py`

**Purpose**: Implements the Retrieval-Augmented Generation pipeline.

**Key Features**:
- Connects to Pinecone vector database
- Retrieves relevant documents based on user queries
- Formats prompts with retrieved context for improved responses
- Handles error cases when no relevant context is found

```python
def get_all_vectorstores():
    # Initialize Pinecone connection and get embedding model
    # Return vector stores for each index (FAQ, announcements, etc.)

def augment_prompt(query: str):
    # Search across vector stores for relevant documents
    # Format documents and scores into prompt context
    # Return formatted prompt for LLM processing
```

### `backend/index_setup.py`

**Purpose**: Sets up and manages vector indexes for different data types.

**Key Features**:
- Defines scraper configurations for different data types
- Creates and manages Pinecone indexes
- Embeds and stores documents in the vector database
- Provides functions to rebuild indexes with fresh data

```python
SCRAPER_CONFIGS = {
    # Configuration for different data types (FAQs, announcements)
    # Specifies scraper module, function, index name, and dimension
}

def setup_index(key: str):
    # Import and run the specified scraper
    # Create or update Pinecone index
    # Embed and store documents in vector database
```

### `backend/app.py`

**Purpose**: Core application logic and LLM integration.

**Key Features**:
- Initializes the LLM (Google Vertex AI's Gemini model)
- Provides the main query function (`ask`)
- Connects the RAG pipeline with the LLM
- Includes alternate configuration for Ollama (commented out)

```python
llm_model = VertexAI(
    model_name="gemini-2.0-flash-001", 
    temperature=0.2,
    max_output_tokens=1024
)

def ask(query: str) -> str:
    # Get augmented prompt with context from RAG pipeline
    # Send to LLM and return response
```

## Frontend Components

### `frontend/streamlit_app.py`

**Purpose**: User interface for the chatbot.

**Key Features**:
- Creates a chat interface using Streamlit
- Manages conversation history
- Processes user input and displays responses
- Handles loading/thinking state

```python
st.title("📚 Chatbot for IZTECH Library")

# Initialize session state for message history
# Display existing messages
# Process new user input
# Show chatbot response
```

## Data Collection Scripts

### `scripts/scrape_faqs.py`

**Purpose**: Scrapes FAQ data from the library website.

**Key Features**:
- Extracts questions and answers from the FAQ page
- Formats data with metadata for storage
- Handles errors and network issues

```python
def scrape_faqs():
    # Request FAQ page
    # Parse HTML to extract questions and answers
    # Format with metadata and return
```

### `scripts/scrape_announcements.py`

**Purpose**: Scrapes announcement data from the library website.

**Key Features**:
- Extracts announcements from the library's announcement page
- Follows links to get full announcement details
- Parses rich text content while preserving links
- Formats data with metadata for storage

```python
def scrape_announcements(max_items=20):
    # Request announcements page
    # For each announcement:
    #   - Extract title and link
    #   - Follow link to get full details
    #   - Parse content and date
    #   - Format with metadata
```

### `scripts/scrape_usage.py`

**Purpose**: Scrapes usage conditions and policies from the library website.

**Key Features**:
- Extracts library usage conditions and policies
- Organizes content into titled sections
- Preserves structured data including tables and links
- Formats data with metadata for storage

```python
def scrape_usage():
    # Request usage conditions page
    # Parse HTML to extract sections and content
    # Format with metadata and return
```

### `scripts/scrape_pickedups.py`

**Purpose**: Scrapes selected books and media recommended by the library.

**Key Features**:
- Extracts "Sizin İçin Seçtiklerimiz" (Selected For You) content from the library website
- Organizes books by category and month
- Preserves links to monthly archive pages
- Formats data with metadata for storage and retrieval

```python
def scrape_pickedups():
    # Request selected books page
    # Extract books by category and month
    # Format with metadata and return
```

## Project Configuration Files

### `requirements.txt`

**Purpose**: Defines project dependencies.

**Key Components**:
- Streamlit for the web interface
- LangChain and related packages for the RAG pipeline
- Pinecone client for vector database integration
- Google Vertex AI integration
- Web scraping tools (BeautifulSoup, requests)
- Utility packages

```
streamlit
langchain
langchain-ollama
langchain-pinecone>=0.1.0
pinecone-client>=3.0.0
langchain-google-vertexai
tqdm
python-dotenv
beautifulsoup4
requests
urllib3
```

## How to Run the Project

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up a `.env` file with the following variables:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment (e.g., us-east-1)
   VERTEX_PROJECT_ID=your_google_cloud_project_id
   VERTEX_REGION=your_google_cloud_region (e.g., us-central1)
   ```

3. Run the data indexing process:
   
   To index all data sources:
   ```python
   python -c "from backend.index_setup import setup_index; \
   setup_index('faq'); \
   setup_index('announcements'); \
   setup_index('usage'); \
   setup_index('pickedups')"
   ```
   
   Or to index a specific data source:
   ```python
   python -c "from backend.index_setup import setup_index; setup_index('usage')"
   ```

   To index only the selected books (pickedups):
   ```python
   python -c "from backend.index_setup import setup_index; setup_index('pickedups')"
   ```

4. Start the Streamlit application:
   ```
   streamlit run frontend/streamlit_app.py
   ```

## Flow of Operation

1. User enters a query in the Streamlit interface
2. The query is sent to the backend's `ask` function
3. The RAG pipeline searches for relevant documents across vector stores
4. Retrieved documents are formatted into a prompt with the user's query
5. The formatted prompt is sent to the LLM (Gemini)
6. The LLM's response is returned to the frontend
7. The response is displayed to the user in the chat interface

## Troubleshooting

If you encounter errors with Pinecone integration, ensure:
- You're using compatible versions of the packages (as specified in requirements.txt)
- The correct import statements are used:
  ```python
  from langchain_pinecone import PineconeVectorStore
  ```
- Your Pinecone API key is valid and properly set in the environment variables 