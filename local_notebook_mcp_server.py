#!/usr/bin/env python3
"""
Local Notebook MCP Server

A comprehensive MCP server for working with local Jupyter notebooks (.ipynb files).
Works directly with files without requiring a running Jupyter server.

Features:
- Read/write notebook files
- Execute code cells with kernel management
- Add/modify/delete cells
- Search and analyze notebooks
- Export to various formats
- Backup and safety features
"""

import asyncio
from typing import Any, Dict, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp not installed. Install with: pip install mcp")
    exit(1)

# Import our modules with aliases to avoid name conflicts
try:
    # Try relative imports first (when running as a package)
    from .file_operations import (
        read_notebook_file as _read_notebook_file,
        list_notebook_files as _list_notebook_files,
        backup_notebook_file as _backup_notebook_file,
        create_new_notebook as _create_new_notebook,
        get_notebook_metadata as _get_notebook_metadata,
        analyze_notebook_dependencies as _analyze_notebook_dependencies,
        search_notebook_cells as _search_notebook_cells
    )

    from .cell_operations import (
        add_notebook_cell as _add_notebook_cell,
        modify_notebook_cell as _modify_notebook_cell,
        delete_notebook_cell as _delete_notebook_cell,
        get_notebook_cell as _get_notebook_cell,
        move_notebook_cell as _move_notebook_cell,
        duplicate_notebook_cell as _duplicate_notebook_cell,
        clear_cell_outputs as _clear_cell_outputs,
        change_cell_type as _change_cell_type
    )

    from .kernel_manager import (
        execute_cell_code as _execute_cell_code,
        execute_all_cells as _execute_all_cells,
        restart_kernel_manager as _restart_kernel_manager,
        interrupt_kernel_manager as _interrupt_kernel_manager,
        list_available_kernels as _list_available_kernels
    )

    from .export_operations import (
        export_notebook_to_python as _export_notebook_to_python,
        export_notebook_to_markdown as _export_notebook_to_markdown,
        export_notebook_to_html as _export_notebook_to_html,
        export_notebook_to_pdf as _export_notebook_to_pdf,
        export_notebook_to_slides as _export_notebook_to_slides,
        export_notebook_code_only as _export_notebook_code_only,
        get_export_formats as _get_export_formats
    )
except ImportError:
    # Fall back to absolute imports (when running directly)
    from file_operations import (
        read_notebook_file as _read_notebook_file,
        list_notebook_files as _list_notebook_files,
        backup_notebook_file as _backup_notebook_file,
        create_new_notebook as _create_new_notebook,
        get_notebook_metadata as _get_notebook_metadata,
        analyze_notebook_dependencies as _analyze_notebook_dependencies,
        search_notebook_cells as _search_notebook_cells
    )

    from cell_operations import (
        add_notebook_cell as _add_notebook_cell,
        modify_notebook_cell as _modify_notebook_cell,
        delete_notebook_cell as _delete_notebook_cell,
        get_notebook_cell as _get_notebook_cell,
        move_notebook_cell as _move_notebook_cell,
        duplicate_notebook_cell as _duplicate_notebook_cell,
        clear_cell_outputs as _clear_cell_outputs,
        change_cell_type as _change_cell_type
    )

    from kernel_manager import (
        execute_cell_code as _execute_cell_code,
        execute_all_cells as _execute_all_cells,
        restart_kernel_manager as _restart_kernel_manager,
        interrupt_kernel_manager as _interrupt_kernel_manager,
        list_available_kernels as _list_available_kernels
    )

    from export_operations import (
        export_notebook_to_python as _export_notebook_to_python,
        export_notebook_to_markdown as _export_notebook_to_markdown,
        export_notebook_to_html as _export_notebook_to_html,
        export_notebook_to_pdf as _export_notebook_to_pdf,
        export_notebook_to_slides as _export_notebook_to_slides,
        export_notebook_code_only as _export_notebook_code_only,
        get_export_formats as _get_export_formats
    )

# Initialize MCP server
mcp = FastMCP("local-notebook")

# File Operations Tools

@mcp.tool()
def read_notebook(notebook_path: str) -> Dict[str, Any]:
    """Read and parse a local Jupyter notebook file.
    
    Args:
        notebook_path: Path to the .ipynb file
        
    Returns:
        Dict containing notebook content and metadata
    """
    return _read_notebook_file(notebook_path)


@mcp.tool()
def list_notebooks(directory: str = ".") -> Dict[str, Any]:
    """List all Jupyter notebook files in a directory.
    
    Args:
        directory: Directory to search (default: current directory)
        
    Returns:
        Dict containing list of notebook files
    """
    return _list_notebook_files(directory)


@mcp.tool()
def backup_notebook(notebook_path: str) -> Dict[str, Any]:
    """Create a backup of a notebook file.
    
    Args:
        notebook_path: Path to the .ipynb file to backup
        
    Returns:
        Dict containing backup information
    """
    return _backup_notebook_file(notebook_path)


@mcp.tool()
def create_notebook(notebook_path: str, title: str = "New Notebook") -> Dict[str, Any]:
    """Create a new empty Jupyter notebook.
    
    Args:
        notebook_path: Path for the new .ipynb file
        title: Title for the new notebook
        
    Returns:
        Dict containing operation result
    """
    return _create_new_notebook(notebook_path, title)


@mcp.tool()
def get_notebook_metadata(notebook_path: str) -> Dict[str, Any]:
    """Get comprehensive metadata and statistics about a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        
    Returns:
        Dict containing notebook metadata and statistics
    """
    return _get_notebook_metadata(notebook_path)


@mcp.tool()
def analyze_dependencies(notebook_path: str) -> Dict[str, Any]:
    """Analyze imported packages and dependencies in a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        
    Returns:
        Dict containing dependency analysis
    """
    return _analyze_notebook_dependencies(notebook_path)


@mcp.tool()
def search_cells(notebook_path: str, search_term: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """Search for content across all cells in a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        search_term: Text to search for
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        Dict containing search results
    """
    return _search_notebook_cells(notebook_path, search_term, case_sensitive)


# Cell Management Tools

@mcp.tool()
def add_cell(notebook_path: str, cell_type: str, content: str, index: Optional[int] = None) -> Dict[str, Any]:
    """Add a new cell to a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        cell_type: Type of cell ('code', 'markdown', 'raw')
        content: Content of the new cell
        index: Position to insert cell (default: append to end)
        
    Returns:
        Dict containing operation result
    """
    return _add_notebook_cell(notebook_path, cell_type, content, index)


@mcp.tool()
def modify_cell(notebook_path: str, index: int, content: str) -> Dict[str, Any]:
    """Modify the content of an existing cell.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to modify
        content: New content for the cell
        
    Returns:
        Dict containing operation result
    """
    return _modify_notebook_cell(notebook_path, index, content)


@mcp.tool()
def delete_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Delete a cell from a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to delete
        
    Returns:
        Dict containing operation result
    """
    return _delete_notebook_cell(notebook_path, index)


@mcp.tool()
def get_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Get the content of a specific cell.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to retrieve
        
    Returns:
        Dict containing cell information
    """
    return _get_notebook_cell(notebook_path, index)


@mcp.tool()
def move_cell(notebook_path: str, from_index: int, to_index: int) -> Dict[str, Any]:
    """Move a cell to a different position in the notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        from_index: Current index of the cell
        to_index: Target index for the cell
        
    Returns:
        Dict containing operation result
    """
    return _move_notebook_cell(notebook_path, from_index, to_index)


@mcp.tool()
def duplicate_cell(notebook_path: str, index: int) -> Dict[str, Any]:
    """Duplicate a cell in the notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to duplicate
        
    Returns:
        Dict containing operation result
    """
    return _duplicate_notebook_cell(notebook_path, index)


@mcp.tool()
def clear_outputs(notebook_path: str, index: Optional[int] = None) -> Dict[str, Any]:
    """Clear outputs from a specific cell or all code cells.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of specific cell to clear (default: clear all)
        
    Returns:
        Dict containing operation result
    """
    return _clear_cell_outputs(notebook_path, index)


@mcp.tool()
def change_cell_type(notebook_path: str, index: int, new_type: str) -> Dict[str, Any]:
    """Change the type of an existing cell.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to change
        new_type: New cell type ('code', 'markdown', 'raw')
        
    Returns:
        Dict containing operation result
    """
    return _change_cell_type(notebook_path, index, new_type)


# Code Execution Tools

@mcp.tool()
async def execute_cell(notebook_path: str, index: int, kernel_spec: str = "python3", timeout: int = 30) -> Dict[str, Any]:
    """Execute a specific code cell and return the outputs.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to execute
        kernel_spec: Kernel specification to use
        timeout: Execution timeout in seconds
        
    Returns:
        Dict containing execution results
    """
    return await _execute_cell_code(notebook_path, index, kernel_spec, timeout)


@mcp.tool()
async def execute_notebook(notebook_path: str, kernel_spec: str = "python3", timeout: int = 300) -> Dict[str, Any]:
    """Execute all code cells in a notebook.
    
    Args:
        notebook_path: Path to the .ipynb file
        kernel_spec: Kernel specification to use
        timeout: Total execution timeout in seconds
        
    Returns:
        Dict containing execution results
    """
    return await _execute_all_cells(notebook_path, kernel_spec, timeout)


@mcp.tool()
async def restart_kernel(kernel_spec: str = "python3") -> Dict[str, Any]:
    """Restart the Jupyter kernel.
    
    Args:
        kernel_spec: Kernel specification to use
        
    Returns:
        Dict containing restart result
    """
    return await _restart_kernel_manager(kernel_spec)


@mcp.tool()
async def interrupt_kernel() -> Dict[str, Any]:
    """Interrupt the currently running kernel.
    
    Returns:
        Dict containing interrupt result
    """
    return await _interrupt_kernel_manager()


@mcp.tool()
def list_kernels() -> Dict[str, Any]:
    """List available kernel specifications.
    
    Returns:
        Dict containing available kernels
    """
    return _list_available_kernels()


# Export Tools

@mcp.tool()
def export_to_python(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to Python script (.py file).
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for .py file (default: same name with .py extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_to_python(notebook_path, output_path)


@mcp.tool()
def export_to_markdown(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to Markdown (.md file).
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for .md file (default: same name with .md extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_to_markdown(notebook_path, output_path)


@mcp.tool()
def export_to_html(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to HTML using nbconvert (if available).
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for .html file (default: same name with .html extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_to_html(notebook_path, output_path)


@mcp.tool()
def export_to_pdf(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to PDF using nbconvert (if available).
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for .pdf file (default: same name with .pdf extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_to_pdf(notebook_path, output_path)


@mcp.tool()
def export_to_slides(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to HTML slides using nbconvert (if available).
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for slides file (default: same name with _slides.html extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_to_slides(notebook_path, output_path)


@mcp.tool()
def export_code_only(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export only the code cells from a notebook to a Python file.
    
    Args:
        notebook_path: Path to the .ipynb file
        output_path: Output path for .py file (default: same name with _code_only.py extension)
        
    Returns:
        Dict containing export result
    """
    return _export_notebook_code_only(notebook_path, output_path)


@mcp.tool()
def get_available_export_formats() -> Dict[str, Any]:
    """Get available export formats.
    
    Returns:
        Dict containing available export formats
    """
    return _get_export_formats()


# Server entry point
if __name__ == "__main__":
    mcp.run()
