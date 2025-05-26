"""
File operations for notebook management.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import nbformat
    from nbformat import v4 as nbf
except ImportError:
    print("Error: nbformat not installed. Install with: pip install nbformat")
    exit(1)

try:
    from .notebook_utils import safe_load_notebook, safe_save_notebook, get_backup_path, extract_output_text
except ImportError:
    from notebook_utils import safe_load_notebook, safe_save_notebook, get_backup_path, extract_output_text


def read_notebook_file(notebook_path: str) -> Dict[str, Any]:
    """Read and parse a local Jupyter notebook file."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        cells_info = []
        for i, cell in enumerate(notebook.cells):
            cell_info = {
                "index": i,
                "cell_type": cell.cell_type,
                "source": cell.source,
                "metadata": cell.metadata
            }
            
            if cell.cell_type == "code":
                cell_info["execution_count"] = cell.execution_count
                cell_info["outputs"] = [extract_output_text(output) for output in cell.outputs]
            
            cells_info.append(cell_info)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "metadata": notebook.metadata,
            "nbformat": notebook.nbformat,
            "nbformat_minor": notebook.nbformat_minor,
            "cells_count": len(notebook.cells),
            "cells": cells_info
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_notebook_files(directory: str = ".") -> Dict[str, Any]:
    """List all Jupyter notebook files in a directory."""
    try:
        path_obj = Path(directory)
        if not path_obj.exists():
            return {"success": False, "error": f"Directory {directory} does not exist"}
        
        notebooks = []
        for notebook_path in path_obj.glob("*.ipynb"):
            try:
                notebook = safe_load_notebook(str(notebook_path))
                info = {
                    "path": str(notebook_path),
                    "name": notebook_path.name,
                    "size": notebook_path.stat().st_size,
                    "modified": datetime.fromtimestamp(notebook_path.stat().st_mtime).isoformat(),
                    "cells_count": len(notebook.cells),
                    "title": notebook.metadata.get("title", "")
                }
                notebooks.append(info)
            except Exception:
                # Skip invalid notebooks
                continue
        
        return {
            "success": True,
            "directory": directory,
            "notebooks": sorted(notebooks, key=lambda x: x["name"])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def backup_notebook_file(notebook_path: str) -> Dict[str, Any]:
    """Create a backup of a notebook file."""
    try:
        if not os.path.exists(notebook_path):
            return {"success": False, "error": f"Notebook {notebook_path} does not exist"}
        
        backup_path = get_backup_path(notebook_path)
        shutil.copy2(notebook_path, backup_path)
        
        return {
            "success": True,
            "original_path": notebook_path,
            "backup_path": backup_path,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_new_notebook(notebook_path: str, title: str = "New Notebook") -> Dict[str, Any]:
    """Create a new empty Jupyter notebook."""
    try:
        # Create a new notebook
        notebook = nbf.new_notebook()
        
        # Set metadata
        notebook.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            },
            "title": title
        }
        
        # Add an initial markdown cell with the title
        title_cell = nbf.new_markdown_cell(f"# {title}")
        notebook.cells.append(title_cell)
        
        # Add an initial code cell
        code_cell = nbf.new_code_cell("# Your code here")
        notebook.cells.append(code_cell)
        
        # Save the notebook
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "title": title,
            "cells_count": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_notebook_metadata(notebook_path: str) -> Dict[str, Any]:
    """Get comprehensive metadata and statistics about a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        # Count cells by type
        cell_counts = {"code": 0, "markdown": 0, "raw": 0}
        executed_cells = 0
        cells_with_outputs = 0
        
        for cell in notebook.cells:
            cell_counts[cell.cell_type] = cell_counts.get(cell.cell_type, 0) + 1
            
            if cell.cell_type == "code":
                if cell.execution_count is not None:
                    executed_cells += 1
                if cell.outputs:
                    cells_with_outputs += 1
        
        # File info
        file_path = Path(notebook_path)
        file_stats = file_path.stat()
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "file_size": file_stats.st_size,
            "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "nbformat_version": f"{notebook.nbformat}.{notebook.nbformat_minor}",
            "metadata": notebook.metadata,
            "total_cells": len(notebook.cells),
            "cell_counts": cell_counts,
            "executed_cells": executed_cells,
            "cells_with_outputs": cells_with_outputs,
            "kernel_spec": notebook.metadata.get("kernelspec", {})
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_notebook_dependencies(notebook_path: str) -> Dict[str, Any]:
    """Analyze imported packages and dependencies in a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        imports = set()
        pip_installs = set()
        
        for cell in notebook.cells:
            if cell.cell_type == "code":
                lines = cell.source.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Standard imports
                    if line.startswith('import '):
                        module = line.split()[1].split('.')[0]
                        imports.add(module)
                    elif line.startswith('from '):
                        module = line.split()[1].split('.')[0]
                        imports.add(module)
                    
                    # Pip installs
                    if '!pip install' in line or '%pip install' in line:
                        parts = line.split('install')
                        if len(parts) > 1:
                            packages = parts[1].strip().split()
                            for pkg in packages:
                                if not pkg.startswith('-'):  # Skip flags
                                    pip_installs.add(pkg)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "imported_modules": sorted(list(imports)),
            "pip_installs": sorted(list(pip_installs)),
            "total_imports": len(imports),
            "total_pip_installs": len(pip_installs)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_notebook_cells(notebook_path: str, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """Search for content across all cells in a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        matches = []
        search_text = search_term if case_sensitive else search_term.lower()
        
        for i, cell in enumerate(notebook.cells):
            cell_content = cell.source if case_sensitive else cell.source.lower()
            
            if search_text in cell_content:
                # Find line numbers
                lines = cell.source.split('\n')
                matching_lines = []
                
                for line_num, line in enumerate(lines):
                    check_line = line if case_sensitive else line.lower()
                    if search_text in check_line:
                        matching_lines.append({
                            "line_number": line_num + 1,
                            "content": line.strip()
                        })
                
                matches.append({
                    "cell_index": i,
                    "cell_type": cell.cell_type,
                    "matching_lines": matching_lines
                })
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "search_term": search_term,
            "matches_found": len(matches),
            "matches": matches
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
