from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
)
from llama_index.core import SimpleDirectoryReader
import os
import logging
import sqlite3
import hashlib

import chromadb

from config import config


def configure_logging():
    """Configures the logging for the application."""
    logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()),
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


logger = configure_logging()


def initialize_chroma(host, port, collection_name):
    """Initializes ChromaDB client and returns the collection."""
    chroma_client = chromadb.HttpClient(host=host, port=port)
    chroma_collection = chroma_client.get_or_create_collection(
        name=collection_name)
    return chroma_collection


def get_embedding_model():
    """Initializes and returns the appropriate embedding model based on configuration."""
    logger.info(
        f"Using embedding model: {config.EMBEDDING_MODEL_NAME} with base_url {config.EMBEDDING_API_BASE}")
    if config.EMBEDDING_SERVICE == 'openai':
        from llama_index.embeddings.openai import OpenAIEmbedding
        return OpenAIEmbedding(
            model=config.EMBEDDING_MODEL_NAME,
            api_key=config.EMBEDDING_API_KEY,
            api_base=config.EMBEDDING_API_BASE
        )
    elif config.EMBEDDING_API_BASE == 'gemini':
        from llama_index.embeddings.gemini import GeminiEmbedding
        return GeminiEmbedding(
            model=config.EMBEDDING_MODEL_NAME,
            api_key=config.EMBEDDING_API_KEY,
            api_base=config.EMBEDDING_API_BASE
        )
    elif config.EMBEDDING_SERVICE == 'ollama':
        from llama_index.embeddings.ollama import OllamaEmbedding
        return OllamaEmbedding(
            model_name=config.EMBEDDING_MODEL_NAME,
            base_url=config.EMBEDDING_API_BASE
        )
    else:
        logger.error(
            f"Unsupported Embedding endpoint {config.EMBEDDING_SERVICE}. Only `openai`, `gemini`, and `ollama` are supported at the moment."
        )
        raise ValueError(
            "Only `openai`, `gemini`, and `ollama` are supported for embedding service.")


def get_chroma_client(use_local_chroma: bool = False):
    """
    Initializes and returns a ChromaDB client.
    If use_local_chroma is True, a persistent local client is used.
    Otherwise, an HTTP client connecting to the configured host/port is used.
    """
    if use_local_chroma:
        persist_directory = os.path.join(os.getcwd(), "chroma_db_local")
        os.makedirs(persist_directory, exist_ok=True)
        logger.info(
            f"Initializing local persistent ChromaDB client at: {persist_directory}")
        return chromadb.PersistentClient(path=persist_directory)
    else:
        logger.info(
            f"Initializing remote ChromaDB client at {config.CHROMA_HOST}:{config.CHROMA_PORT}")
        return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)


def initialize_file_tracker_db():
    """Initializes the SQLite database for file tracking."""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files_hash (
            filepath TEXT PRIMARY KEY,
            md5_hash TEXT
        )
    """)
    conn.commit()
    logger.info(
        f"Initialized file tracking database at: {config.SQLITE_DB_PATH}")
    return conn


def is_file_modified(conn: sqlite3.Connection, filepath: str, current_hash: str) -> bool:
    """
    Checks if a file's hash in the database is different from the current_hash.
    Returns True if the file is new or modified, False otherwise.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM files_hash WHERE filepath = ? AND md5_hash = ?", (filepath, current_hash))
    result = cursor.fetchone()

    if result is None:
        logger.info(
            f"File '{filepath}' is new or hash has changed. Current hash: {current_hash}. Treating as modified.")
        return True
    else:
        logger.info(
            f"File '{filepath}' hash matches stored hash. Current hash: {current_hash}. Treating as not modified.")
        return False


def update_hash(conn: sqlite3.Connection, filepath: str, new_hash: str):
    """
    Updates the hash for a given filepath in the files_hash table.
    Inserts a new record if the filepath does not exist, otherwise updates it.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO files_hash (filepath, md5_hash) VALUES (?, ?)", (filepath, new_hash))
    conn.commit()
    logger.info(f"Updated hash for file '{filepath}' to {new_hash}.")


def calculate_md5(input_string: str) -> str:
    """
    Calculates the MD5 hash for a given string.
    """
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()


def format_nodes(nodes_with_score):
    result = ""
    for i, node in enumerate(nodes_with_score):
        result += f"DOC {i+1}: \nFile Path:`{node.node.metadata['file_path']}`\nContent:\n{node.node.get_content()}\n{"="*40}\n\n"
    return result


def update_index(index, embed_model):
    conn = initialize_file_tracker_db()

    documents = SimpleDirectoryReader(
        input_dir=config.DOCUMENTS_DIRECTORY,
        recursive=True,
        exclude=parse_gitignore_style_file(),
        filename_as_id=True
    )

    files = documents.load_data()
    splitter = SemanticSplitterNodeParser(
        embed_model=embed_model, include_prev_next_rel=False)

    for f in files:
        f_hash = hashlib.md5(f.get_content().encode('utf-8')).hexdigest()
        if is_file_modified(conn, f.doc_id, f_hash):
            index.delete_ref_doc(ref_doc_id=f.doc_id)
            nodes = splitter.get_nodes_from_documents([f])
            index.insert_nodes(nodes)
            update_hash(conn, f.get_doc_id(), f_hash)
    conn.close()


def parse_gitignore_style_file(filepath: str = '.indexignore') -> list[str]:
    """
    Parses a .gitignore-style file into a list of strings, ignoring comments and empty lines.
    If the file is not found, returns an empty list.
    """
    if not os.path.exists(filepath):
        logger.info(f"File '{filepath}' not found. Returning empty list.")
        return []

    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
    logger.info(f"Parsed {len(patterns)} patterns from '{filepath}'.")
    return patterns
