#!/usr/bin/env python3
"""
Workflow Operations Module for Local Notebook MCP Server

Enhanced high-level operations that combine multiple basic operations
for improved user experience and better UI synchronization.
"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional

# Import existing operations
from cell_operations import add_notebook_cell as _add_cell, modify_notebook_cell as _modify_cell
from kernel_manager import execute_cell_code as _execute_cell
from file_operations import read_notebook_file as _read_notebook, backup_notebook_file as _backup_notebook
from notebook_utils import synchronous_auto_save


def force_file_refresh(notebook_path: str) -> bool:
    """
    DEPRECATED: Use synchronous_auto_save instead.
    Force file system refresh to trigger VS Code update.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        bool: Success status
    """
    try:
        # Use the new synchronous auto-save mechanism
        result = synchronous_auto_save(notebook_path)
        return result.get("success", False)
    except Exception as e:
        print(f"Warning: Auto-save failed: {e}")
        return False


async def create_and_execute_cell(
    notebook_path: str,
    cell_type: str,
    content: str,
    index: Optional[int] = None,
    kernel_spec: str = "python3",
    timeout: int = 30,
    auto_refresh: bool = True,
    auto_backup: bool = True
) -> Dict[str, Any]:
    """Create a new cell and execute it if it's a code cell.
    
    Enhanced workflow that combines cell creation, execution, and refresh.
    
    Args:
        notebook_path: Path to the .ipynb file
        cell_type: Type of cell ('code', 'markdown', 'raw')
        content: Content of the new cell
        index: Position to insert cell (default: append to end)
        kernel_spec: Kernel specification for execution
        timeout: Execution timeout in seconds
        auto_refresh: Whether to trigger file refresh
        auto_backup: Whether to create backup before operation
        
    Returns:
        Dict containing combined operation results
    """
    result = {
        "success": False,
        "notebook_path": notebook_path,
        "cell_type": cell_type,
        "operations": [],
        "execution_results": None,
        "errors": []
    }
    
    try:
        # Step 1: Optional backup
        if auto_backup:
            try:
                backup_result = _backup_notebook(notebook_path)
                result["operations"].append(f"Backup created: {backup_result.get('backup_path', 'Unknown')}")
            except Exception as e:
                result["errors"].append(f"Backup failed: {str(e)}")
        
        # Step 2: Create the cell
        try:
            cell_result = _add_cell(notebook_path, cell_type, content, index)
            if not cell_result.get("success", False):
                result["errors"].append(f"Cell creation failed: {cell_result.get('error', 'Unknown error')}")
                return result
            
            result["cell_index"] = cell_result.get("index")
            result["total_cells"] = cell_result.get("total_cells")
            result["operations"].append(f"Cell created at index {result['cell_index']}")
            
        except Exception as e:
            result["errors"].append(f"Cell creation error: {str(e)}")
            return result
        
        # Step 3: Execute if it's a code cell
        if cell_type.lower() == "code":
            try:
                execution_result = await _execute_cell(
                    notebook_path, 
                    result["cell_index"], 
                    kernel_spec, 
                    timeout
                )
                
                if execution_result.get("success", False):
                    result["execution_results"] = {
                        "execution_count": execution_result.get("execution_count"),
                        "outputs": execution_result.get("outputs", []),
                        "execution_time": execution_result.get("execution_time")
                    }
                    result["operations"].append(f"Cell executed successfully (count: {execution_result.get('execution_count')})")
                else:
                    result["errors"].append(f"Execution failed: {execution_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                result["errors"].append(f"Execution error: {str(e)}")
        else:
            result["operations"].append(f"Skipped execution for {cell_type} cell")
        
        # Step 4: Force file refresh
        if auto_refresh:
            try:
                refresh_success = force_file_refresh(notebook_path)
                if refresh_success:
                    result["operations"].append("File refreshed for VS Code sync")
                else:
                    result["errors"].append("File refresh failed")
            except Exception as e:
                result["errors"].append(f"Refresh error: {str(e)}")
        
        # Step 5: Final status
        result["success"] = len(result["errors"]) == 0
        result["operation_summary"] = f"Created {cell_type} cell at index {result['cell_index']}"
        if cell_type.lower() == "code" and result["execution_results"]:
            result["operation_summary"] += f" and executed successfully"
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Workflow error: {str(e)}")
        result["success"] = False
        return result


async def execute_with_refresh(
    notebook_path: str,
    index: int,
    kernel_spec: str = "python3",
    timeout: int = 30,
    auto_refresh: bool = True,
    retry_on_failure: bool = True
) -> Dict[str, Any]:
    """Execute a cell with enhanced refresh and retry logic.
    
    Args:
        notebook_path: Path to the .ipynb file
        index: Index of the cell to execute
        kernel_spec: Kernel specification
        timeout: Execution timeout in seconds
        auto_refresh: Whether to trigger file refresh
        retry_on_failure: Whether to retry on execution failure
        
    Returns:
        Dict containing execution results and refresh status
    """
    result = {
        "success": False,
        "notebook_path": notebook_path,
        "index": index,
        "operations": [],
        "execution_results": None,
        "errors": []
    }
    
    try:
        # Attempt execution (with retry logic)
        max_retries = 2 if retry_on_failure else 1
        execution_result = None
        
        for attempt in range(max_retries):
            try:
                execution_result = await _execute_cell(notebook_path, index, kernel_spec, timeout)
                if execution_result.get("success", False):
                    break
                else:
                    if attempt < max_retries - 1:
                        result["operations"].append(f"Execution attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(0.5)  # Brief delay before retry
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    result["operations"].append(f"Execution attempt {attempt + 1} error: {str(e)}, retrying...")
                    await asyncio.sleep(0.5)
                else:
                    raise e
        
        # Process execution results
        if execution_result and execution_result.get("success", False):
            result["execution_results"] = {
                "execution_count": execution_result.get("execution_count"),
                "outputs": execution_result.get("outputs", []),
                "execution_time": execution_result.get("execution_time")
            }
            result["operations"].append(f"Cell executed successfully (count: {execution_result.get('execution_count')})")
        else:
            result["errors"].append(f"Execution failed after {max_retries} attempts")
            if execution_result:
                result["errors"].append(f"Final error: {execution_result.get('error', 'Unknown error')}")
        
        # Force file refresh
        if auto_refresh:
            try:
                refresh_success = force_file_refresh(notebook_path)
                if refresh_success:
                    result["operations"].append("File refreshed for VS Code sync")
                else:
                    result["errors"].append("File refresh failed")
            except Exception as e:
                result["errors"].append(f"Refresh error: {str(e)}")
        
        result["success"] = len(result["errors"]) == 0
        return result
        
    except Exception as e:
        result["errors"].append(f"Execute with refresh error: {str(e)}")
        result["success"] = False
        return result


async def batch_create_and_execute(
    notebook_path: str,
    cells: List[Dict[str, Any]],
    start_index: Optional[int] = None,
    execute_code_cells: bool = True,
    kernel_spec: str = "python3",
    timeout_per_cell: int = 30,
    stop_on_error: bool = False,
    auto_backup: bool = True
) -> Dict[str, Any]:
    """Create and optionally execute multiple cells in batch.
    
    Args:
        notebook_path: Path to the .ipynb file
        cells: List of cell specifications [{"type": "code", "content": "..."}, ...]
        start_index: Starting index for cell insertion
        execute_code_cells: Whether to execute code cells
        kernel_spec: Kernel specification
        timeout_per_cell: Timeout per cell execution
        stop_on_error: Whether to stop on first error
        auto_backup: Whether to create backup before operations
        
    Returns:
        Dict containing batch operation results
    """
    result = {
        "success": False,
        "notebook_path": notebook_path,
        "total_cells_requested": len(cells),
        "cells_created": 0,
        "cells_executed": 0,
        "operations": [],
        "cell_results": [],
        "errors": []
    }
    
    try:
        # Step 1: Optional backup
        if auto_backup:
            try:
                backup_result = _backup_notebook(notebook_path)
                result["operations"].append(f"Backup created: {backup_result.get('backup_path', 'Unknown')}")
            except Exception as e:
                result["errors"].append(f"Backup failed: {str(e)}")
                if stop_on_error:
                    return result
        
        # Step 2: Process each cell
        current_index = start_index
        
        for i, cell_spec in enumerate(cells):
            cell_result = {
                "index": i,
                "cell_type": cell_spec.get("type", "code"),
                "success": False,
                "created": False,
                "executed": False,
                "errors": []
            }
            
            try:
                # Create cell
                creation_result = _add_cell(
                    notebook_path,
                    cell_spec.get("type", "code"),
                    cell_spec.get("content", ""),
                    current_index
                )
                
                if creation_result.get("success", False):
                    cell_result["created"] = True
                    cell_result["notebook_index"] = creation_result.get("index")
                    result["cells_created"] += 1
                    
                    if current_index is not None:
                        current_index += 1
                    
                    result["operations"].append(f"Cell {i+1} created at index {cell_result['notebook_index']}")
                    
                    # Execute if it's a code cell and execution is enabled
                    if (cell_spec.get("type", "code").lower() == "code" and 
                        execute_code_cells and 
                        creation_result.get("success", False)):
                        
                        try:
                            execution_result = await _execute_cell(
                                notebook_path,
                                cell_result["notebook_index"],
                                kernel_spec,
                                timeout_per_cell
                            )
                            
                            if execution_result.get("success", False):
                                cell_result["executed"] = True
                                cell_result["execution_count"] = execution_result.get("execution_count")
                                cell_result["outputs"] = execution_result.get("outputs", [])
                                result["cells_executed"] += 1
                                result["operations"].append(f"Cell {i+1} executed successfully")
                            else:
                                cell_result["errors"].append(f"Execution failed: {execution_result.get('error', 'Unknown')}")
                                
                        except Exception as e:
                            cell_result["errors"].append(f"Execution error: {str(e)}")
                    
                    cell_result["success"] = len(cell_result["errors"]) == 0
                    
                else:
                    cell_result["errors"].append(f"Creation failed: {creation_result.get('error', 'Unknown')}")
                
            except Exception as e:
                cell_result["errors"].append(f"Cell processing error: {str(e)}")
            
            result["cell_results"].append(cell_result)
            
            # Check if we should stop on error
            if not cell_result["success"] and stop_on_error:
                result["operations"].append(f"Stopped at cell {i+1} due to error")
                break
        
        # Step 3: Force file refresh
        try:
            refresh_success = force_file_refresh(notebook_path)
            if refresh_success:
                result["operations"].append("File refreshed for VS Code sync")
            else:
                result["errors"].append("File refresh failed")
        except Exception as e:
            result["errors"].append(f"Refresh error: {str(e)}")
        
        # Step 4: Final status
        result["success"] = (result["cells_created"] > 0 and 
                           all(cell["success"] for cell in result["cell_results"]))
        
        result["operation_summary"] = (f"Created {result['cells_created']}/{result['total_cells_requested']} cells, "
                                     f"executed {result['cells_executed']} code cells")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Batch operation error: {str(e)}")
        result["success"] = False
        return result
