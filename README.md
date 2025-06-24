# KnowledgeBase MCP: Your Personal RAG Vector Store

KnowledgeBase MCP is a lightweight, powerful, and containerized retrieval solution. It allows you to turn a local directory of documents into a smart, queryable knowledge base, accessible via a simple API. Designed to run on your personal machine, it automatically keeps your data indexed and ready for retrieval.

This system focuses on the "Retrieval" part of Retrieval-Augmented Generation (RAG). It ingests your documents, indexes them, and provides a powerful search tool to find the most relevant context for any given query.

## ✨ Features

* **🔌 External Embedding Models**: Connects to OpenAI-compatible embedding endpoints (e.g., OpenAI, or other self-hosted solutions). These models run externally and are not part of the Dockerized stack.
* **📂 Automatic Directory Indexing**: Point it to a directory, and KnowledgeBase MCP will ingest and index all supported files (PDF, TXT, DOCX, etc.).
* **🔄 Persistent File Tracking**: Automatically detects changes, additions, or deletions of files between sessions to ensure the knowledge base is always up-to-date without re-indexing unchanged documents.
* **🚫 Configurable Filtering**: Use a dedicated ignore file, similar in concept to `.gitignore`, to specify patterns for files and directories that should be excluded from indexing.
* **⚡ Real-time API**: Exposes its retrieval capabilities as "Tools" using the **FastMCP** framework, providing an efficient Server-Sent Events (SSE) endpoint for real-time streaming of retrieved document chunks.
* **🖼️ Multi-modal Ready**: The architecture is designed to be extended to support multi-modal embeddings for text-and-image search.

## 🛠️ Tech Stack

* **Indexing & Retrieval Framework**: [**LlamaIndex**](https://www.llamaindex.ai/) is the core engine for data ingestion, indexing, and executing retrieval queries against the data.
* **Vector Database**: [**ChromaDB**](https://www.trychroma.com/) provides efficient, local storage and retrieval of vector embeddings.
* **API Framework**: [**FastMCP**](https://github.com/cognitive-metamodel/fastmcp) (built on FastAPI) exposes the core LlamaIndex functionalities as structured "Tools" over a Server-Sent Events (SSE) protocol.
* **Containerization**: [**Docker**](https://www.docker.com/) & [**Docker Compose**](https://docs.docker.com/compose/) containerize and manage the application and database services.
* **File Tracking Database**: [**SQLite**](https://www.sqlite.org/index.html) is used to persistently track the state of indexed files.

## ⚙️ How File Change Tracking Works

To ensure that the knowledge base remains synchronized with your local document directory even when the system is shut down and restarted, KnowledgeBase MCP implements a robust file tracking mechanism.

This system uses a **SQLite** database to store a record of every file that has been indexed. For each file, it stores its path and an **MD5 hash** of its content. A hash is a unique fingerprint for the file's content; if the content changes, the hash changes.

When the application starts, it performs the following synchronization logic:

1. **Scan Directory**: It scans the `DOCUMENTS_DIRECTORY` to get a list of all current files and calculates the MD5 hash for each one.
2. **Compare with Database**: It compares this list with the records stored in the SQLite database.
    * **New Files**: If a file exists in the directory but not in the database, it is treated as **new**. It gets indexed, and its file path and hash are added to the database.
    * **Modified Files**: If a file exists in both the directory and the database, their hashes are compared. If the hashes do not match, the file has been **modified**. The old version is removed from the index, the new version is indexed, and the hash in the database is updated.
    * **Deleted Files**: If a file exists in the database but is no longer in the directory, it is considered **deleted**. It is removed from the index, and its record is deleted from the database.
    * **Unchanged Files**: If a file's hash in the directory matches its hash in the database, the file is **unchanged** and is skipped, saving significant processing time.

This process guarantees that the retrieval system is always an accurate reflection of your documents directory without the overhead of re-indexing the entire dataset on every startup.

## Configuration

Configuration is managed through environment variables, which you should place in a `.env` file in the project's root directory.

* `EMBEDDING_API_BASE`: The endpoint for your embedding service (e.g., `https://api.openai.com/v1`).
* `EMBEDDING_API_KEY`: Your authentication key for the embedding service.
* `EMBEDDING_MODEL_NAME`: The specific model identifier (e.g., `text-embedding-ada-002`).
* `DOCUMENTS_DIRECTORY`: The local path to your documents (e.g., `./documents`).
* `CHUNK_SIZE`: This defines the size of the text fragments (in tokens) that your documents are broken into before being embedded.
* `CHUNK_OVERLAP`: This defines how many tokens are repeated between adjacent chunks.
* `LOG_LEVEL`: Controls the verbosity of application logs.
* `CHROMA_HOST`: Host URL of the Chroma server.
* `CHROMA_PORT`: Host port of the Chroma Server.
* `CHROMA_COLLECTION_NAME`: Collection name.
