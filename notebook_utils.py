"""
Utility functions for notebook operations.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    import nbformat
    from nbformat import v4 as nbf
except ImportError:
    print("Error: nbformat not installed. Install with: pip install nbformat")
    exit(1)


def get_backup_path(notebook_path: str) -> str:
    """Generate backup file path with timestamp."""
    path_obj = Path(notebook_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path_obj.stem}_backup_{timestamp}{path_obj.suffix}"
    return str(path_obj.parent / backup_name)


def safe_load_notebook(notebook_path: str) -> nbformat.NotebookNode:
    """Safely load a notebook file with error handling."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)
    except Exception as e:
        raise ValueError(f"Failed to load notebook {notebook_path}: {str(e)}")


def safe_save_notebook(notebook: nbformat.NotebookNode, notebook_path: str) -> None:
    """Safely save a notebook with backup."""
    if os.path.exists(notebook_path):
        backup_path = get_backup_path(notebook_path)
        shutil.copy2(notebook_path, backup_path)
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(notebook, f)


def extract_output_text(output: Dict[str, Any]) -> str:
    """Extract readable text from cell output."""
    output_type = output.get("output_type")
    
    if output_type == "stream":
        return output.get("text", "")
    elif output_type in ["display_data", "execute_result"]:
        data = output.get("data", {})
        if "text/plain" in data:
            return data["text/plain"]
        elif "text/html" in data:
            return f"[HTML Output: {len(data['text/html'])} chars]"
        elif "image/png" in data:
            return "[Image Output: PNG]"
        else:
            return f"[{output_type}: {list(data.keys())}]"
    elif output_type == "error":
        return "\n".join(output.get("traceback", []))
    else:
        return f"[Unknown output type: {output_type}]"
