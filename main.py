from fastmcp import FastMCP
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

import os
from pathlib import Path

from config import config
from logging_utils import configure_logging, logger
from chroma_utils import get_embedding_model, get_chroma_client
from document_processor import update_index, format_nodes

logger = configure_logging()

mcp = FastMCP(
    name="KnowledgeBase MCP",
    instructions="A lightweight, powerful, and containerized retrieval solution for your local documents.",
    version="0.1.0"
)

# Dictionary to hold indices for each collection
indices = {}
embed_model = get_embedding_model()
chroma_client = get_chroma_client()

for collection_name, collection_config in config.document_collections.items():
    logger.info(f"Initializing Chroma for collection: {collection_name}")

    chroma_collection = chroma_client.get_or_create_collection(
        name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )

    # Update index for the specific collection's directory
    update_index(index, collection_config.directory)
    indices[collection_name] = index
    logger.info(
        f"Index for collection '{collection_name}' initialized and updated.")


@mcp.tool
def query(query_text: str, collection_name: str) -> str:
    """Semantic search for a piece of text within a specified collection.
    You shall format this as detailed as possible.
    """
    if collection_name not in indices:
        raise ValueError(f"Collection '{collection_name}' not found.")

    logger.info(
        f"Semantic searching: `{query_text}` in collection `{collection_name}`.")
    retriever = indices[collection_name].as_retriever()
    return format_nodes(retriever.retrieve(query_text))


@mcp.tool
def refresh_index(collection_name: str):
    """Refresh the vector store for a specified collection so that new documents can be queried.
    This might take a while.
    """
    if collection_name not in indices:
        raise ValueError(f"Collection '{collection_name}' not found.")

    logger.info(f"Updating Index for collection: {collection_name}.")
    collection_config = config.document_collections.get(collection_name)
    if not collection_config:
        raise ValueError(
            f"Configuration for collection '{collection_name}' not found.")

    result = update_index(indices[collection_name],
                          collection_config.directory)

    return f"Refresh complete for collection '{collection_name}'. {sum(result)} out of {len(result)} files have been updated."


@mcp.tool
def list_collections() -> list[str]:
    """Lists all available Chroma collections."""
    logger.info("Listing all Chroma collections.")
    return list(indices.keys())


@mcp.tool
def get_file_content(file_path: str) -> str:
    """Returns the content of a single file given a path, verifying it's under the configured documents directory."""
    logger.info(f"Attempting to read file: {file_path}")

    abs_file_path = Path(file_path).resolve()

    # Check if the file path is within any of the configured document directories
    is_allowed = False
    for collection_config in config.document_collections.values():
        documents_dir_abs = Path(collection_config.directory).resolve()
        if os.path.commonpath([abs_file_path, documents_dir_abs]) == str(documents_dir_abs):
            is_allowed = True
            break

    if not is_allowed:
        raise ValueError(
            f"Access denied: File path '{file_path}' is not within any of the allowed document directories.")

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
        port=config.mcp_port,
        log_level=config.log_level,
    )
