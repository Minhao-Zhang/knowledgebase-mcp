# KnowledgeBase MCP: Vector Store on Your Notes

KnowledgeBase MCP is a lightweight, containerized solution for creating a queryable knowledge base from your local documents. It focuses on the "Retrieval" part of Retrieval-Augmented Generation (RAG), indexing your documents and providing a search API to find relevant context. The knowledge base keeps itself up-to-date as your source files change.

## ✨ Features

* **External Embedding Models**: Connects to various embedding endpoints, including OpenAI, Gemini, and Ollama.
* **Secure File Content Retrieval**: Safely retrieve the content of indexed documents via a dedicated API tool, ensuring access is restricted to the configured documents directory.
* **Automatic Directory Indexing**: Ingests and indexes supported files (PDF, TXT, DOCX) from a specified directory.
* **Persistent File Tracking**: Detects and manages file changes (additions, modifications, deletions) across sessions, updating the index automatically on startup or via a dedicated MCP tool call.
* **Configurable Filtering**: Uses a `.indexignore` file to exclude specific files/directories from indexing.
* **Real-time API**: Exposes retrieval capabilities as FastMCP "Tools" via a Server-Sent Events (SSE) endpoint.
* **Multi-modal Ready**: Architecture supports future expansion for multi-modal embeddings.

## 🚀 Getting Started

### Installation and Setup

1. **Clone the repository**
2. **Prepare your documents:**
    The project now supports indexing documents from multiple directories, each mapped to a distinct Chroma collection. This is configured in `config.yaml` using the `document_collections` list. Each item in this list has a `directory` (the path inside the container) and a `collection_name`.

    **Crucial Requirement:** The `directory` paths specified in `config.yaml` for each document collection **must exactly match** the target paths of the volume mounts defined in `docker-compose.yml` for the `knowledgebase-mcp` service.

    **Example `config.yaml` snippet:**

    ```yaml
    document_collections:
      - directory: /ObsidianVault
        collection_name: obsidian_notes
      - directory: /ProjectDocs
        collection_name: project_documents
    ```

    **Corresponding `docker-compose.yml` snippet:**

    ```yaml
    services:
      knowledgebase-mcp:
        volumes:
          - ../ObsidianVault:/ObsidianVault
          - ./my_project_docs:/ProjectDocs
    ```

3. **Configure Environment Variables:**
    Copy `.env.example` to `.env` and edit it with your settings.

    ```bash
    cp .env.example .env
    ```

    Key variables in `.env`:
    * `EMBEDDING_API_KEY`: API key for the embedding service (dummy value for Ollama).

4. **Build and Run with Docker Compose:**

    ```bash
    docker-compose up --build -d
    ```

    This builds the image, starts ChromaDB, and then the KnowledgeBase MCP service, which begins indexing.

### Initial Data Loading and Indexing

On first run, all documents in the configured `document_collections` are indexed. Subsequent runs only process new or modified files.

## 💡 Usage

KnowledgeBase MCP provides FastMCP tools via an HTTP API on port `8002`.

### Available Tools

* **`query(query_text: str, collection_name: str) -> str`**:
    Performs semantic search within a specified collection. Returns relevant document chunks.

* **`refresh_index(collection_name: str)`**:
    Scans the directory associated with the specified collection and updates its index for new, modified, or deleted files.

* **`list_collections() -> list[str]`**:
    Lists all available Chroma collection names configured in the system.

* **`get_file_content(file_path: str) -> str`**:
    Returns the content of a single file given a path. This tool explicitly verifies that the `file_path` is within one of the configured `document_collections.directory` paths to prevent unauthorized access.

## 📂 Ignored Files

* **`.indexignore`**: Excludes files/directories from indexing (e.g., `*.png`, `*.pdf`).

## 🤝 Contributing

Refer to the `LICENSE` file for contribution details.
