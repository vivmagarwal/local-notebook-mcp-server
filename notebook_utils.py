"""
Utility functions for notebook operations.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import json

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


def normalize_source(source):
    """Normalize cell source to string format."""
    if isinstance(source, list):
        return ''.join(source)
    return str(source) if source is not None else ""


def safe_load_notebook(notebook_path: str) -> nbformat.NotebookNode:
    """Safely load a notebook file with error handling, bypassing validation."""
    try:
        # Read as JSON first to avoid validation issues
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        # Remove problematic 'id' fields from cells and normalize source
        if 'cells' in notebook_data:
            for cell in notebook_data['cells']:
                if 'id' in cell:
                    del cell['id']
                
                # Normalize source field
                if 'source' in cell:
                    cell['source'] = normalize_source(cell['source'])
        
        # Convert to NotebookNode without validation
        notebook = nbformat.from_dict(notebook_data)
        
        # Ensure source fields are strings
        for cell in notebook.cells:
            cell.source = normalize_source(getattr(cell, 'source', ''))
        
        return notebook
    except Exception as e:
        raise ValueError(f"Failed to load notebook {notebook_path}: {str(e)}")


def safe_save_notebook(notebook: nbformat.NotebookNode, notebook_path: str) -> None:
    """Safely save a notebook with backup, avoiding validation issues."""
    if os.path.exists(notebook_path):
        backup_path = get_backup_path(notebook_path)
        shutil.copy2(notebook_path, backup_path)
    
    # Convert to dict manually
    notebook_dict = {
        'cells': [],
        'metadata': notebook.metadata,
        'nbformat': notebook.nbformat,
        'nbformat_minor': notebook.nbformat_minor
    }
    
    # Process cells
    for cell in notebook.cells:
        cell_dict = {
            'cell_type': cell.cell_type,
            'metadata': getattr(cell, 'metadata', {}),
            'source': normalize_source(getattr(cell, 'source', ''))
        }
        
        if cell.cell_type == 'code':
            cell_dict['outputs'] = getattr(cell, 'outputs', [])
            cell_dict['execution_count'] = getattr(cell, 'execution_count', None)
        
        notebook_dict['cells'].append(cell_dict)
    
    # Write as JSON to avoid nbformat validation
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_dict, f, indent=2, ensure_ascii=False)


def extract_output_text(output: Dict[str, Any]) -> str:
    """Extract readable text from cell output."""
    output_type = output.get("output_type")
    
    if output_type == "stream":
        text = output.get("text", "")
        return normalize_source(text)
    elif output_type in ["display_data", "execute_result"]:
        data = output.get("data", {})
        if "text/plain" in data:
            return normalize_source(data["text/plain"])
        elif "text/html" in data:
            html_content = data["text/html"]
            if isinstance(html_content, list):
                html_content = ''.join(html_content)
            return f"[HTML Output: {len(html_content)} chars]"
        elif "image/png" in data:
            return "[Image Output: PNG]"
        else:
            return f"[{output_type}: {list(data.keys())}]"
    elif output_type == "error":
        traceback = output.get("traceback", [])
        if isinstance(traceback, list):
            return "\n".join(str(line) for line in traceback)
        else:
            return str(traceback)
    else:
        return f"[Unknown output type: {output_type}]"
