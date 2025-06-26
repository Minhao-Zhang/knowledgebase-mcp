from fastmcp import FastMCP
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex


from config import config
from utils import (
    configure_logging,
    initialize_chroma,
    get_embedding_model,
    clear_index,
    update_index,
    format_nodes
)

logger = configure_logging()

mcp = FastMCP(
    name="KnowledgeBase MCP",
    instructions="A lightweight, powerful, and containerized retrieval solution for your local documents.",
    version="0.1.0"
)

chroma_collection = initialize_chroma(
    config.CHROMA_HOST, config.CHROMA_PORT, config.CHROMA_COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embed_model = get_embedding_model()
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=embed_model,
)

update_index(index, embed_model)

retriever = index.as_retriever()


@mcp.tool
def query(query_text: str) -> str:
    """Semantic search for a piece of text. You shall format this as detailed as possible. """
    return format_nodes(retriever.retrieve(query_text))


@mcp.tool
def refresh_index():
    """Refresh the vector store so that new documents can be queried. This might take a while."""
    update_index(index, embed_model)


@mcp.tool
def reindex():
    """DANGEROUS: This will erase all vectors in vector store and build them from the group up. This operation is time consuming."""
    clear_index()
    update_index(index, embed_model)


app = mcp.http_app()


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=config.MCP_PORT,
        log_level=config.LOG_LEVEL,
    )
