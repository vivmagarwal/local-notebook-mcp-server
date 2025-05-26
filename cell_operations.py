"""
Cell operations for notebook management.
"""

from typing import Any, Dict, Optional

try:
    import nbformat
    from nbformat import v4 as nbf
except ImportError:
    print("Error: nbformat not installed. Install with: pip install nbformat")
    exit(1)

try:
    from .notebook_utils import safe_load_notebook, safe_save_notebook, extract_output_text
except ImportError:
    from notebook_utils import safe_load_notebook, safe_save_notebook, extract_output_text


def add_notebook_cell(notebook_path: str, cell_type: str, content: str, index: Optional[int] = None) -> Dict[str, Any]:
    """Add a new cell to a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if cell_type == "code":
            new_cell = nbf.new_code_cell(content)
        elif cell_type == "markdown":
            new_cell = nbf.new_markdown_cell(content)
        elif cell_type == "raw":
            new_cell = nbf.new_raw_cell(content)
        else:
            return {"success": False, "error": f"Invalid cell type: {cell_type}"}
        
        if index is None:
            notebook.cells.append(new_cell)
            index = len(notebook.cells) - 1
        else:
            notebook.cells.insert(index, new_cell)
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "cell_type": cell_type,
            "index": index,
            "total_cells": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def modify_notebook_cell(notebook_path: str, index: int, content: str) -> Dict[str, Any]:
    """Modify the content of an existing cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        notebook.cells[index].source = content
        
        # Clear outputs for code cells when modified
        if notebook.cells[index].cell_type == "code":
            notebook.cells[index].outputs = []
            notebook.cells[index].execution_count = None
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "index": index,
            "cell_type": notebook.cells[index].cell_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_notebook_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Delete a cell from a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        deleted_cell = notebook.cells.pop(index)
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "deleted_index": index,
            "deleted_cell_type": deleted_cell.cell_type,
            "remaining_cells": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_notebook_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Get the content of a specific cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        cell = notebook.cells[index]
        cell_info = {
            "success": True,
            "index": index,
            "cell_type": cell.cell_type,
            "source": cell.source,
            "metadata": cell.metadata
        }
        
        if cell.cell_type == "code":
            cell_info["execution_count"] = cell.execution_count
            cell_info["outputs"] = [extract_output_text(output) for output in cell.outputs]
        
        return cell_info
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_notebook_cell(notebook_path: str, from_index: int, to_index: int) -> Dict[str, Any]:
    """Move a cell to a different position in the notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if from_index < 0 or from_index >= len(notebook.cells):
            return {"success": False, "error": f"Source index {from_index} out of range"}
        
        if to_index < 0 or to_index >= len(notebook.cells):
            return {"success": False, "error": f"Target index {to_index} out of range"}
        
        cell = notebook.cells.pop(from_index)
        notebook.cells.insert(to_index, cell)
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "from_index": from_index,
            "to_index": to_index,
            "cell_type": cell.cell_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def duplicate_notebook_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Duplicate a cell in the notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        # Get the original cell
        original_cell = notebook.cells[index]
        
        # Create a new cell of the same type with the same content
        if original_cell.cell_type == "code":
            new_cell = nbf.new_code_cell(original_cell.source)
        elif original_cell.cell_type == "markdown":
            new_cell = nbf.new_markdown_cell(original_cell.source)
        elif original_cell.cell_type == "raw":
            new_cell = nbf.new_raw_cell(original_cell.source)
        else:
            return {"success": False, "error": f"Unknown cell type: {original_cell.cell_type}"}
        
        # Copy metadata
        new_cell.metadata = original_cell.metadata.copy()
        
        # Insert the new cell right after the original
        new_index = index + 1
        notebook.cells.insert(new_index, new_cell)
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "original_index": index,
            "new_index": new_index,
            "cell_type": original_cell.cell_type,
            "total_cells": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def clear_cell_outputs(notebook_path: str, index: Optional[int] = None) -> Dict[str, Any]:
    """Clear outputs from a specific cell or all code cells."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index is not None:
            # Clear specific cell
            if index < 0 or index >= len(notebook.cells):
                return {"success": False, "error": f"Cell index {index} out of range"}
            
            cell = notebook.cells[index]
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
                cleared_cells = 1
            else:
                return {"success": False, "error": f"Cell {index} is not a code cell"}
        else:
            # Clear all code cells
            cleared_cells = 0
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    cell.outputs = []
                    cell.execution_count = None
                    cleared_cells += 1
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "cleared_cells": cleared_cells,
            "target_index": index
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def change_cell_type(notebook_path: str, index: int, new_type: str) -> Dict[str, Any]:
    """Change the type of an existing cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        if new_type not in ["code", "markdown", "raw"]:
            return {"success": False, "error": f"Invalid cell type: {new_type}"}
        
        old_cell = notebook.cells[index]
        old_type = old_cell.cell_type
        
        if old_type == new_type:
            return {"success": True, "message": "Cell is already of the specified type"}
        
        # Create new cell with the same content but different type
        if new_type == "code":
            new_cell = nbf.new_code_cell(old_cell.source)
        elif new_type == "markdown":
            new_cell = nbf.new_markdown_cell(old_cell.source)
        elif new_type == "raw":
            new_cell = nbf.new_raw_cell(old_cell.source)
        
        # Copy metadata
        new_cell.metadata = old_cell.metadata.copy()
        
        # Replace the cell
        notebook.cells[index] = new_cell
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "index": index,
            "old_type": old_type,
            "new_type": new_type
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
