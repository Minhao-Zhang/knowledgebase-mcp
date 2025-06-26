import sqlite3
import hashlib
import os

from config import config
from logging_utils import logger


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


def delete_file_tracker_db():
    """
    Deletes the file_tracker_db.
    """
    if os.path.exists(config.SQLITE_DB_PATH):
        try:
            os.remove(config.SQLITE_DB_PATH)
            logger.info(
                f"File tracker database '{config.SQLITE_DB_PATH}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting file tracker database: {e}")
    else:
        logger.info(
            f"File tracker database '{config.SQLITE_DB_PATH}' does not exist. No need to delete.")
