import os
import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        # Load from YAML
        self.embedding_service = config_data.get(
            'embedding', {}).get('service')
        self.embedding_api_base = config_data.get(
            'embedding', {}).get('api_base')
        self.embedding_model_name = config_data.get(
            'embedding', {}).get('model_name')
        self.documents_directory = config_data.get(
            'documents', {}).get('directory')
        self.log_level = config_data.get('logging', {}).get('level')
        self.chroma_host = config_data.get('chroma', {}).get('host')
        self.chroma_port = config_data.get('chroma', {}).get('port')
        self.chroma_collection_name = config_data.get(
            'chroma', {}).get('collection_name')
        self.mcp_port = config_data.get('mcp', {}).get('port')

        # Override with environment variables
        self.embedding_api_key = os.getenv("EMBEDDING_API_KEY", "")
        self.embedding_service = os.getenv(
            "EMBEDDING_SERVICE", self.embedding_service)
        self.embedding_api_base = os.getenv(
            "EMBEDDING_API_BASE", self.embedding_api_base)
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL_NAME", self.embedding_model_name)
        self.documents_directory = os.getenv(
            "DOCUMENTS_DIRECTORY", self.documents_directory)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.chroma_host = os.getenv("CHROMA_HOST", self.chroma_host)
        self.chroma_port = int(os.getenv("CHROMA_PORT", self.chroma_port)) if os.getenv(
            "CHROMA_PORT") else self.chroma_port
        self.chroma_collection_name = os.getenv(
            "CHROMA_COLLECTION_NAME", self.chroma_collection_name)
        self.mcp_port = int(os.getenv("MCP_PORT", self.mcp_port)) if os.getenv(
            "MCP_PORT") else self.mcp_port


config = Config()
