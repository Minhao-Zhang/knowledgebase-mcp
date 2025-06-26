import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    EMBEDDING_SERVICE: str = os.getenv(
        "EMBEDDING_SERVICE", "openai")
    EMBEDDING_API_BASE: str = os.getenv(
        "EMBEDDING_API_BASE", "https://api.openai.com/v1")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "text-embedding-ada-002")
    DOCUMENTS_DIRECTORY: str = os.getenv("DOCUMENTS_DIRECTORY", "./documents")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1024"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "20"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ChromaDB specific configurations
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8001"))
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "knowledgebase_mcp")

    MCP_PORT: int = int(os.getenv("MCP_PORT", "8002"))

    @classmethod
    def validate_config(cls):
        if not cls.EMBEDDING_API_KEY:
            print(
                "Warning: EMBEDDING_API_KEY is not set. Embedding functionality may be limited.")
        if not os.path.exists(cls.DOCUMENTS_DIRECTORY):
            print(
                f"Warning: DOCUMENTS_DIRECTORY '{cls.DOCUMENTS_DIRECTORY}' does not exist.")


config = Config()
