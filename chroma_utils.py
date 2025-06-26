import chromadb
import os
from typing import Any

from config import config
from logging_utils import logger


def initialize_chroma() -> chromadb.Collection:
    """Initializes ChromaDB client and returns the collection."""
    chroma_client = chromadb.HttpClient(
        host=config.CHROMA_HOST, port=config.CHROMA_PORT)
    chroma_collection = chroma_client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME)
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
