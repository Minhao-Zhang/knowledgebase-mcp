
# KnowledgeBase MCP: Your Personal RAG Vector Store

KnowledgeBase MCP is a lightweight, containerized solution for creating a queryable knowledge base from your local documents. It focuses on the "Retrieval" part of Retrieval-Augmented Generation (RAG), indexing your documents and providing a search API to find relevant context.

## ✨ Features

* **External Embedding Models**: Connects to OpenAI-compatible embedding endpoints (OpenAI, Gemini, Ollama).
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
* **Dependencies**: `pip` and `requirements.txt`

## ⚙️ How File Change Tracking Works

KnowledgeBase MCP uses a **SQLite** database to track indexed files by their path and MD5 hash. On startup, it scans the `DOCUMENTS_DIRECTORY` and compares file hashes with the database:

* **New Files**: Indexed and added to the database.
* **Modified Files**: Old version removed, new version indexed, database hash updated.
* **Deleted Files**: Removed from the index and database.
* **Unchanged Files**: Skipped for efficiency.

This ensures the knowledge base is always synchronized with your document directory.

## 🚀 Getting Started

### Prerequisites

* [Docker](https://www.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Installation and Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/knowledgebase-mcp.git
    cd knowledgebase-mcp
    ```

2. **Prepare your documents:**
    Create a `documents` directory in the project root or modify `docker-compose.yml` to map your desired local document directory to `/app/documents` inside the container.

    ```bash
    mkdir documents
    # Place your files here
    ```

    Example `docker-compose.yml` volume modification:

    ```yaml
    volumes:
      - ./documents:/app/documents
      - knowledgebase_volume:/sqlite_db
    ```

3. **Configure Environment Variables:**
    Copy `.env.example` to `.env` and edit it with your settings.

    ```bash
    cp .env.example .env
    ```

    Key variables in `.env`:
    * `LOG_LEVEL`: Logging verbosity (e.g., `INFO`).
    * `MCP_PORT`: Port for the FastMCP server (default: `8002`).
    * `EMBEDDING_SERVICE`: `openai`, `gemini`, or `ollama`.
    * `EMBEDDING_API_BASE`: URL of your embedding service (e.g., `http://host.docker.internal:11434` for host Ollama).
    * `EMBEDDING_API_KEY`: API key (dummy for Ollama).
    * `EMBEDDING_MODEL_NAME`: Embedding model (e.g., `all-minilm`).
    * `DOCUMENTS_DIRECTORY`: Path inside the container (default: `./documents`).
    * `CHUNK_SIZE`, `CHUNK_OVERLAP`: Document chunking parameters.
    * `CHROMA_HOST`: ChromaDB service name (e.g., `chromadb` for Docker Compose).
    * `CHROMA_PORT`: ChromaDB port (default: `8000`).
    * `CHROMA_COLLECTION_NAME`: ChromaDB collection name.
    * `SQLITE_DB_PATH`: SQLite DB path inside the container (default: `file_tracker.db`).

4. **Build and Run with Docker Compose:**

    ```bash
    docker-compose up --build -d
    ```

    This builds the image, starts ChromaDB, and then the KnowledgeBase MCP service, which begins indexing.
    Monitor logs:

    ```bash
    docker-compose logs -f knowledgebase-mcp
    ```

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

* **`reindex()`**:
    **DANGEROUS**: Erases all vectors and rebuilds the entire index from scratch. Use with caution.

    ```bash
    curl -N -X POST http://localhost:8002/tool/reindex
    ```

## 📂 Ignored Files

* **`.indexignore`**: Excludes files/directories from indexing (e.g., `*.png`, `*.pdf`).
* **`.dockerignore`**: Excludes files/directories when building the Docker image.
* **`.gitignore`**: Standard Git ignore file.

## 🤝 Contributing

Refer to the `LICENSE` file for contribution details.
