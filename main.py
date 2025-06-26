from fastmcp import FastMCP
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

import os
from pathlib import Path

from config import config
from logging_utils import configure_logging, logger
from chroma_utils import initialize_chroma, get_embedding_model
from document_processor import update_index, format_nodes

logger = configure_logging()

mcp = FastMCP(
    name="KnowledgeBase MCP",
    instructions="A lightweight, powerful, and containerized retrieval solution for your local documents.",
    version="0.1.0"
)


chroma_collection = initialize_chroma()
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embed_model = get_embedding_model()
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=embed_model,
)
update_index(index)
retriever = index.as_retriever()


@mcp.tool
def query(query_text: str) -> str:
    """Semantic search for a piece of text. You shall format this as detailed as possible. """
    logger.info(f"Semantic searching: `{query_text}`.")
    return format_nodes(retriever.retrieve(query_text))


@mcp.tool
def refresh_index():
    """Refresh the vector store so that new documents can be queried. This might take a while."""
    logger.info("Updating Index.")
    result = update_index(index)

    return f"Refresh complete. {sum(result)} out of {len(result)} files have been updated."


@mcp.tool
def get_file_content(file_path: str) -> str:
    """Returns the content of a single file given a path, verifying it's under the configured documents directory."""
    logger.info(f"Attempting to read file: {file_path}")

    abs_file_path = Path(file_path).resolve()
    documents_dir_abs = Path(config.DOCUMENTS_DIRECTORY).resolve()

    if os.path.commonpath([abs_file_path, documents_dir_abs]) != str(documents_dir_abs):
        raise ValueError(
            f"Access denied: File path '{file_path}' is not within the allowed documents directory.")

    try:
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Successfully read file: {file_path}")
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


app = mcp.http_app()


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=config.MCP_PORT,
        log_level=config.LOG_LEVEL,
    )
