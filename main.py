import hashlib
from fastmcp import FastMCP
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import SimpleDirectoryReader
from config import config
from utils import (
    configure_logging,
    initialize_chroma,
    get_embedding_model,
    initialize_file_tracker_db,
    is_file_modified,
    update_hash
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
embed_model = get_embedding_model()

conn = initialize_file_tracker_db()

directory_loader = SimpleDirectoryReader(
    input_dir=config.DOCUMENTS_DIRECTORY,
    recursive=True,
    exclude=["*.jpg", "*.png", "*.pdf"],
    filename_as_id=True
)

files = directory_loader.load_data()

for f in files:
    f_hash = hashlib.md5(f.get_content().encode('utf-8')).hexdigest()
    if is_file_modified(conn, f.doc_id, f_hash):
        update_hash(conn, f.get_doc_id(), f_hash)

conn.close()
