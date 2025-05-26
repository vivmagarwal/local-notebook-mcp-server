"""
Kernel management for notebook execution.
"""

import asyncio
from typing import Any, Dict, Optional

try:
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import find_kernel_specs
except ImportError:
    print("Error: jupyter_client not installed. Install with: pip install jupyter_client")
    exit(1)

try:
    from .notebook_utils import safe_load_notebook, safe_save_notebook, extract_output_text
except ImportError:
    from notebook_utils import safe_load_notebook, safe_save_notebook, extract_output_text

# Global kernel manager for reuse
kernel_manager: Optional[KernelManager] = None
current_kernel_spec = "python3"


def ensure_kernel_manager(kernel_spec: str = "python3") -> KernelManager:
    """Ensure kernel manager is running with specified kernel."""
    global kernel_manager, current_kernel_spec
    
    if kernel_manager is None or current_kernel_spec != kernel_spec:
        if kernel_manager is not None:
            stop_kernel()
        
        kernel_manager = KernelManager(kernel_name=kernel_spec)
        kernel_manager.start_kernel()
        current_kernel_spec = kernel_spec
    
    return kernel_manager


def stop_kernel():
    """Stop the current kernel."""
    global kernel_manager
    if kernel_manager is not None:
        try:
            kernel_manager.shutdown_kernel()
        except:
            pass
        kernel_manager = None


async def execute_cell_code(notebook_path: str, index: int, kernel_spec: str = "python3", timeout: int = 30) -> Dict[str, Any]:
    """Execute a specific code cell and return the outputs."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if index < 0 or index >= len(notebook.cells):
            return {"success": False, "error": f"Cell index {index} out of range"}
        
        cell = notebook.cells[index]
        if cell.cell_type != "code":
            return {"success": False, "error": f"Cell {index} is not a code cell"}
        
        # Ensure kernel is running
        km = ensure_kernel_manager(kernel_spec)
        kc = km.client()
        
        # Clear previous outputs
        cell.outputs = []
        
        # Execute the cell
        msg_id = kc.execute(cell.source)
        
        outputs = []
        execution_count = None
        
        # Collect outputs with timeout
        try:
            end_time = asyncio.get_event_loop().time() + timeout
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Use a shorter timeout for individual message checks
                    msg = kc.get_iopub_msg(timeout=1)
                    msg_type = msg['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'execute_input':
                        execution_count = content['execution_count']
                    elif msg_type in ['stream', 'display_data', 'execute_result']:
                        output = {
                            'output_type': msg_type,
                            'data': content.get('data', {}),
                            'text': content.get('text', ''),
                            'name': content.get('name', '')
                        }
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
                        
                except Exception:
                    # Short sleep to avoid busy waiting
                    await asyncio.sleep(0.1)
                    continue
                    
        except Exception as e:
            return {"success": False, "error": f"Execution timeout or error: {str(e)}"}
        
        # Update execution count
        cell.execution_count = execution_count
        
        # Save notebook with outputs
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


async def execute_all_cells(notebook_path: str, kernel_spec: str = "python3", timeout: int = 300) -> Dict[str, Any]:
    """Execute all code cells in a notebook."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        # Ensure fresh kernel
        stop_kernel()
        km = ensure_kernel_manager(kernel_spec)
        
        results = []
        total_cells = len([cell for cell in notebook.cells if cell.cell_type == "code"])
        executed_cells = 0
        
        if total_cells == 0:
            return {
                "success": True,
                "notebook_path": notebook_path,
                "total_code_cells": 0,
                "executed_cells": 0,
                "results": []
            }
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                result = await execute_cell_code(notebook_path, i, kernel_spec, timeout // total_cells)
                results.append({
                    "index": i,
                    "success": result["success"],
                    "outputs": result.get("outputs", []),
                    "error": result.get("error")
                })
                executed_cells += 1
                
                if not result["success"]:
                    break
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "total_code_cells": total_cells,
            "executed_cells": executed_cells,
            "results": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def restart_kernel_manager(kernel_spec: str = "python3") -> Dict[str, Any]:
    """Restart the Jupyter kernel."""
    try:
        stop_kernel()
        ensure_kernel_manager(kernel_spec)
        
        return {
            "success": True,
            "kernel_spec": kernel_spec,
            "message": "Kernel restarted successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def interrupt_kernel_manager() -> Dict[str, Any]:
    """Interrupt the currently running kernel."""
    try:
        global kernel_manager
        if kernel_manager is None:
            return {"success": False, "error": "No kernel is running"}
        
        kernel_manager.interrupt_kernel()
        
        return {
            "success": True,
            "message": "Kernel interrupted successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_available_kernels() -> Dict[str, Any]:
    """List available kernel specifications."""
    try:
        kernels = find_kernel_specs()
        
        return {
            "success": True,
            "available_kernels": list(kernels.keys()),
            "current_kernel": current_kernel_spec
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
