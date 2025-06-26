
# KnowledgeBase MCP: Your Personal RAG Vector Store

KnowledgeBase MCP is a lightweight, containerized solution for creating a queryable knowledge base from your local documents. It focuses on the "Retrieval" part of Retrieval-Augmented Generation (RAG), indexing your documents and providing a search API to find relevant context.

## ✨ Features

* **External Embedding Models**: Connects to various embedding endpoints, including OpenAI, Gemini, and Ollama.
* **Secure File Content Retrieval**: Safely retrieve the content of indexed documents via a dedicated API tool, ensuring access is restricted to the configured documents directory.
* **Automatic Directory Indexing**: Ingests and indexes supported files (PDF, TXT, DOCX) from a specified directory.
* **Persistent File Tracking**: Detects and manages file changes (additions, modifications, deletions) across sessions.
* **Configurable Filtering**: Uses a `.indexignore` file to exclude specific files/directories from indexing.
* **Real-time API**: Exposes retrieval capabilities as FastMCP "Tools" via a Server-Sent Events (SSE) endpoint.
* **Multi-modal Ready**: Architecture supports future expansion for multi-modal embeddings.

## 🛠️ Tech Stack

* **Indexing & Retrieval**: [**LlamaIndex**](https://www.llamaindex.ai/)
* **Vector Database**: [**ChromaDB**](https://www.trychroma.com/)
* **API Framework**: [**FastMCP**](https://github.com/cognitive-metamodel/fastmcp) (built on FastAPI)
* **Containerization**: [**Docker**](https://www.docker.com/) & [**Docker Compose**](https://docs.docker.com/compose/)
* **File Tracking**: [**SQLite**](https://www.sqlite.org/index.html)

## 🚀 Getting Started

### Installation and Setup

1. **Clone the repository:**
2. **Prepare your documents:**
    For the directory you wish to index and semantically search, alter volumes under `docker-compose.yml`'s `knowledgebase-mcp` to

    ```yaml
    volumes:
      - YOUR_RELATIVE_PATH_TO_DIRECTORY:DOCUMENTS_DIRECTORY_ENV_VAR_IN_DOT_ENV_FILE
    ```

3. **Configure Environment Variables:**
    Copy `.env.example` to `.env` and edit it with your settings.

    ```bash
    cp .env.example .env
    ```

    Key variables in `.env`:
    * `LOG_LEVEL`: Logging verbosity (e.g., `INFO`).
    * `MCP_PORT`: Port for the FastMCP server (default: `8002`).
    * `EMBEDDING_SERVICE`: Specifies the embedding service to use (`openai`, `gemini`, or `ollama`).
    * `EMBEDDING_API_BASE`: The base URL for your embedding service (e.g., `http://host.docker.internal:11434` for a local Ollama instance).
    * `EMBEDDING_API_KEY`: API key for the embedding service (dummy value for Ollama).
    * `EMBEDDING_MODEL_NAME`: The specific embedding model to use (e.g., `text-embedding-ada-002` for OpenAI, `all-minilm` for Ollama).
    * `DOCUMENTS_DIRECTORY`: Path inside the container where your documents are located (default: `./documents`).
    * `CHROMA_HOST`: The hostname or IP address of the ChromaDB server (e.g., `chromadb` if running in Docker Compose).
    * `CHROMA_PORT`: The port on which the ChromaDB server is listening (default: `8001`).
    * `CHROMA_COLLECTION_NAME`: The name of the collection within ChromaDB where document embeddings will be stored.

4. **Build and Run with Docker Compose:**

    ```bash
    docker-compose up --build -d
    ```

    This builds the image, starts ChromaDB, and then the KnowledgeBase MCP service, which begins indexing.

### Initial Data Loading and Indexing

On first run, all documents in `DOCUMENTS_DIRECTORY` are indexed. Subsequent runs only process new or modified files.

## 💡 Usage

KnowledgeBase MCP provides FastMCP tools via an HTTP API on port `8002`.

### Available Tools

* **`query(query_text: str) -> str`**:
    Performs semantic search. Returns relevant document chunks.

    ```bash
    curl -N -X POST http://localhost:8002/tool/query \
         -H "Content-Type: application/json" \
         -d '{"query_text": "What is the main purpose of KnowledgeBase MCP?"}'
    ```

    (Returns an SSE stream)

* **`refresh_index()`**:
    Scans `DOCUMENTS_DIRECTORY` and updates the index for new, modified, or deleted files.

    ```bash
    curl -N -X POST http://localhost:8002/tool/refresh_index
    ```

* **`get_file_content(file_path: str) -> str`**:
    Returns the content of a single file given a path, verifying it's under the configured documents directory.

    ```bash
    curl -N -X POST http://localhost:8002/tool/get_file_content \
         -H "Content-Type: application/json" \
         -d '{"file_path": "./documents/your_document.txt"}'
    ```

## 📂 Ignored Files

* **`.indexignore`**: Excludes files/directories from indexing (e.g., `*.png`, `*.pdf`).

## 🤝 Contributing

Refer to the `LICENSE` file for contribution details.
