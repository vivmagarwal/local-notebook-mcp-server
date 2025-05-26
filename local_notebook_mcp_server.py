#!/usr/bin/env python3
"""
Local Notebook MCP Server - Production Ready

A simple, efficient MCP server for working with local Jupyter notebooks.
All functionality consolidated into a single file for maximum simplicity.
"""

import os
import json
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp not installed. Install with: pip install mcp")
    exit(1)

try:
    import nbformat
    from nbformat import v4 as nbf
except ImportError:
    print("Error: nbformat not installed. Install with: pip install nbformat")
    exit(1)

try:
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import find_kernel_specs
except ImportError:
    print("Error: jupyter_client not installed. Install with: pip install jupyter_client")
    exit(1)

# Initialize MCP server
mcp = FastMCP("local-notebook-mcp-server")

# Global kernel manager
_kernel_manager: Optional[KernelManager] = None
_current_kernel_spec = "python3"


def safe_load_notebook(notebook_path: str) -> nbformat.NotebookNode:
    """Load a notebook file safely."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)
    
    # Clean up problematic fields
    if 'cells' in notebook_data:
        for cell in notebook_data['cells']:
            if 'id' in cell:
                del cell['id']
            if 'source' in cell and isinstance(cell['source'], list):
                cell['source'] = ''.join(cell['source'])
    
    return nbformat.from_dict(notebook_data)


def safe_save_notebook(notebook: nbformat.NotebookNode, notebook_path: str) -> None:
    """Save a notebook file safely."""
    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
    
    # Create backup if file exists
    if os.path.exists(notebook_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{Path(notebook_path).stem}_backup_{timestamp}.ipynb"
        shutil.copy2(notebook_path, backup_path)
    
    # Convert to dict and save
    notebook_dict = {
        'cells': [],
        'metadata': notebook.metadata,
        'nbformat': notebook.nbformat,
        'nbformat_minor': notebook.nbformat_minor
    }
    
    for cell in notebook.cells:
        cell_dict = {
            'cell_type': cell.cell_type,
            'metadata': getattr(cell, 'metadata', {}),
            'source': str(getattr(cell, 'source', ''))
        }
        
        if cell.cell_type == 'code':
            cell_dict['outputs'] = getattr(cell, 'outputs', [])
            cell_dict['execution_count'] = getattr(cell, 'execution_count', None)
        
        notebook_dict['cells'].append(cell_dict)
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_dict, f, indent=2, ensure_ascii=False)


def extract_output_text(output: Dict[str, Any]) -> str:
    """Extract text from cell output."""
    output_type = output.get("output_type")
    
    if output_type == "stream":
        text = output.get("text", "")
        return str(text) if not isinstance(text, list) else ''.join(text)
    elif output_type in ["display_data", "execute_result"]:
        data = output.get("data", {})
        if "text/plain" in data:
            text = data["text/plain"]
            return str(text) if not isinstance(text, list) else ''.join(text)
        return f"[{output_type}]"
    elif output_type == "error":
        traceback = output.get("traceback", [])
        return "\n".join(str(line) for line in traceback)
    return f"[{output_type}]"


def ensure_kernel_manager(kernel_spec: str = "python3") -> KernelManager:
    """Ensure kernel manager is running."""
    global _kernel_manager, _current_kernel_spec
    
    if _kernel_manager is None or _current_kernel_spec != kernel_spec:
        if _kernel_manager is not None:
            try:
                _kernel_manager.shutdown_kernel()
            except:
                pass
        
        _kernel_manager = KernelManager(kernel_name=kernel_spec)
        _kernel_manager.start_kernel()
        _current_kernel_spec = kernel_spec
    
    return _kernel_manager


# File Operations
@mcp.tool()
def read_notebook(notebook_path: str) -> Dict[str, Any]:
    """Read and parse a notebook file."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        cells_info = []
        for i, cell in enumerate(notebook.cells):
            cell_info = {
                "index": i,
                "cell_type": cell.cell_type,
                "source": str(getattr(cell, 'source', '')),
                "metadata": getattr(cell, 'metadata', {})
            }
            
            if cell.cell_type == "code":
                cell_info["execution_count"] = getattr(cell, 'execution_count', None)
                cell_info["outputs"] = [extract_output_text(output) for output in getattr(cell, 'outputs', [])]
            
            cells_info.append(cell_info)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "metadata": notebook.metadata,
            "cells_count": len(notebook.cells),
            "cells": cells_info
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_notebooks(directory: str = ".") -> Dict[str, Any]:
    """List all notebook files in a directory."""
    try:
        path_obj = Path(directory)
        if not path_obj.exists():
            return {"success": False, "error": f"Directory {directory} does not exist"}
        
        notebooks = []
        for notebook_path in path_obj.glob("*.ipynb"):
            try:
                info = {
                    "path": str(notebook_path),
                    "name": notebook_path.name,
                    "size": notebook_path.stat().st_size,
                    "modified": datetime.fromtimestamp(notebook_path.stat().st_mtime).isoformat()
                }
                notebooks.append(info)
            except:
                continue
        
        return {
            "success": True,
            "directory": directory,
            "notebooks": sorted(notebooks, key=lambda x: x["name"])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_notebook(notebook_path: str, title: str = "New Notebook") -> Dict[str, Any]:
    """Create a new notebook."""
    try:
        notebook = nbf.new_notebook()
        notebook.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            },
            "title": title
        }
        
        # Add title cell
        notebook.cells.append(nbf.new_markdown_cell(f"# {title}"))
        # Add code cell
        notebook.cells.append(nbf.new_code_cell("# Your code here"))
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "title": title,
            "cells_count": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Cell Operations
@mcp.tool()
def add_cell(notebook_path: str, cell_type: str, content: str, index: Optional[int] = None) -> Dict[str, Any]:
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


@mcp.tool()
def modify_cell(notebook_path: str, index: int, content: str) -> Dict[str, Any]:
    """Modify an existing cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        notebook.cells[index].source = content
        
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


@mcp.tool()
def delete_cell(notebook_path: str, index: int) -> Dict[str, Any]:
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
            "remaining_cells": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Get content of a specific cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        cell = notebook.cells[index]
        result = {
            "success": True,
            "index": index,
            "cell_type": cell.cell_type,
            "source": str(getattr(cell, 'source', '')),
            "metadata": getattr(cell, 'metadata', {})
        }
        
        if cell.cell_type == "code":
            result["execution_count"] = getattr(cell, 'execution_count', None)
            result["outputs"] = [extract_output_text(output) for output in getattr(cell, 'outputs', [])]
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# Code Execution
@mcp.tool()
async def execute_cell(notebook_path: str, index: int, kernel_spec: str = "python3", timeout: int = 30) -> Dict[str, Any]:
    """Execute a code cell."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        cell = notebook.cells[index]
        if cell.cell_type != "code":
            return {"success": False, "error": f"Cell {index} is not a code cell"}
        
        km = ensure_kernel_manager(kernel_spec)
        kc = km.client()
        
        # Clear outputs
        cell.outputs = []
        
        # Execute
        msg_id = kc.execute(cell.source)
        
        outputs = []
        execution_count = None
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                msg = kc.get_iopub_msg(timeout=0.5)
                msg_type = msg['msg_type']
                content = msg['content']
                
                if msg_type == 'execute_input':
                    execution_count = content['execution_count']
                elif msg_type == 'stream':
                    output = {
                        'output_type': 'stream',
                        'name': content.get('name', 'stdout'),
                        'text': content.get('text', '')
                    }
                    outputs.append(output)
                    cell.outputs.append(output)
                elif msg_type in ['display_data', 'execute_result']:
                    output = {
                        'output_type': msg_type,
                        'data': content.get('data', {}),
                        'metadata': content.get('metadata', {})
                    }
                    if msg_type == 'execute_result':
                        output['execution_count'] = content.get('execution_count')
                    outputs.append(output)
                    cell.outputs.append(output)
                elif msg_type == 'error':
                    error_output = {
                        'output_type': 'error',
                        'ename': content['ename'],
                        'evalue': content['evalue'],
                        'traceback': content['traceback']
                    }
                    outputs.append(error_output)
                    cell.outputs.append(error_output)
                elif msg_type == 'status' and content['execution_state'] == 'idle':
                    break
                        
            except:
                await asyncio.sleep(0.1)
                continue
        
        if execution_count is not None:
            cell.execution_count = execution_count
        
        safe_save_notebook(notebook, notebook_path)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "index": index,
            "execution_count": execution_count,
            "outputs": [extract_output_text(output) for output in outputs]
        }
                    
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def execute_notebook(notebook_path: str, kernel_spec: str = "python3", timeout: int = 300) -> Dict[str, Any]:
    """Execute all code cells in a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        # Restart kernel for clean execution
        global _kernel_manager
        if _kernel_manager is not None:
            try:
                _kernel_manager.shutdown_kernel()
            except:
                pass
            _kernel_manager = None
        
        results = []
        code_cells = [i for i, cell in enumerate(notebook.cells) if cell.cell_type == "code"]
        
        for i in code_cells:
            result = await execute_cell(notebook_path, i, kernel_spec, timeout // len(code_cells) if code_cells else 30)
            results.append({
                "index": i,
                "success": result["success"],
                "outputs": result.get("outputs", []),
                "error": result.get("error")
            })
            
            if not result["success"]:
                break
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "total_code_cells": len(code_cells),
            "executed_cells": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# Utility Functions
@mcp.tool()
def search_cells(notebook_path: str, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """Search for content across cells."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        matches = []
        search_text = search_term if case_sensitive else search_term.lower()
        
        for i, cell in enumerate(notebook.cells):
            cell_content = str(getattr(cell, 'source', ''))
            check_content = cell_content if case_sensitive else cell_content.lower()
            
            if search_text in check_content:
                lines = cell_content.split('\n')
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


@mcp.tool()
def export_to_python(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to Python script."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.py')
        
        python_code = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                python_code.append(f"# Cell {i + 1}")
                python_code.append(str(getattr(cell, 'source', '')))
                python_code.append("")
            elif cell.cell_type == "markdown":
                python_code.append(f"# Markdown Cell {i + 1}")
                for line in str(getattr(cell, 'source', '')).split('\n'):
                    python_code.append(f"# {line}")
                python_code.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(python_code))
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path,
            "total_cells_exported": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_kernels() -> Dict[str, Any]:
    """List available kernel specifications."""
    try:
        kernels = find_kernel_specs()
        return {
            "success": True,
            "available_kernels": list(kernels.keys()),
            "current_kernel": _current_kernel_spec
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
