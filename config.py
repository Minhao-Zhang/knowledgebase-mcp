import os
import yaml
from dotenv import load_dotenv

load_dotenv()


class DocumentCollection:
    def __init__(self, directory: str, collection_name: str):
        self.directory = directory
        self.collection_name = collection_name


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

        self.document_collections = {}
        for item in config_data.get('document_collections', []):
            directory = item.get('directory')
            collection_name = item.get('collection_name')
            if directory and collection_name:
                self.document_collections[collection_name] = DocumentCollection(
                    directory, collection_name)

        self.log_level = config_data.get('logging', {}).get('level')
        self.chroma_host = config_data.get('chroma', {}).get('host')
        self.chroma_port = config_data.get('chroma', {}).get('port')
        self.mcp_port = config_data.get('mcp', {}).get('port')

        self.embedding_api_key = os.getenv("EMBEDDING_API_KEY", "")


config = Config()
