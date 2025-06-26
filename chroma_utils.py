import chromadb
import os
from typing import Any

from config import config
from logging_utils import logger


def get_embedding_model():
    """Initializes and returns the appropriate embedding model based on configuration."""
    logger.info(
        f"Using embedding model: {config.embedding_model_name} with base_url {config.embedding_api_base}")
    if config.embedding_service == 'openai':
        from llama_index.embeddings.openai import OpenAIEmbedding
        return OpenAIEmbedding(
            model=config.embedding_model_name,
            api_key=config.embedding_api_key,
            api_base=config.embedding_api_base
        )
    elif config.embedding_service == 'gemini':
        from llama_index.embeddings.gemini import GeminiEmbedding
        return GeminiEmbedding(
            model=config.embedding_model_name,
            api_key=config.embedding_api_key,
            api_base=config.embedding_api_base
        )
    elif config.embedding_service == 'ollama':
        from llama_index.embeddings.ollama import OllamaEmbedding
        return OllamaEmbedding(
            model_name=config.embedding_model_name,
            base_url=config.embedding_api_base
        )
    else:
        logger.error(
            f"Unsupported Embedding endpoint {config.embedding_service}. Only `openai`, `gemini`, and `ollama` are supported at the moment."
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
            f"Initializing remote ChromaDB client at {config.chroma_host}:{config.chroma_port}")
        return chromadb.HttpClient(host=config.chroma_host, port=config.chroma_port)
