import logging
from config import config


def configure_logging():
    """Configures the logging for the application."""
    logging.basicConfig(level=getattr(logging, config.log_level.upper()),
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


logger = configure_logging()
