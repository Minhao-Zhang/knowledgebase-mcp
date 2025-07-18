import os
from llama_index.core import SimpleDirectoryReader

from logging_utils import logger


def format_nodes(nodes_with_score) -> str:
    """
    Formats a list of nodes with scores into a human-readable string.
    """
    result = ""
    for i, node in enumerate(nodes_with_score):
        result += f"DOC {i+1}: \nFile Path:`{node.node.metadata['file_path']}`\nContent:\n{node.node.get_content()}\n{"="*40}\n\n"
    return result


def update_index(index, directory: str) -> list[bool]:
    """
    Updates the document index by checking for modified files and re-indexing them.
    """
    documents = SimpleDirectoryReader(
        input_dir=directory,
        recursive=True,
        exclude=parse_gitignore_style_file(),
        filename_as_id=True
    ).load_data()
    updated = index.refresh_ref_docs(documents)
    logger.info(
        f"Refresh complete. {sum(updated)} out of {len(updated)} files have been updated.")
    return updated


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
