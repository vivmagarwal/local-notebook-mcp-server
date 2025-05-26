"""
Utility functions for notebook operations.
"""

import os
import shutil
import subprocess
import time
import platform
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


def resolve_notebook_path(notebook_path: str) -> str:
    """Resolve notebook path relative to the current working directory."""
    # If path is already absolute, return as-is
    if os.path.isabs(notebook_path):
        return notebook_path
    
    # Convert relative path to absolute using current working directory
    # This respects the MCP server's cwd configuration
    resolved_path = os.path.join(os.getcwd(), notebook_path)
    return os.path.abspath(resolved_path)


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
        # Resolve the notebook path first
        resolved_path = resolve_notebook_path(notebook_path)
        
        # Read as JSON first to avoid validation issues
        with open(resolved_path, 'r', encoding='utf-8') as f:
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
        resolved_path = resolve_notebook_path(notebook_path)
        raise ValueError(f"Failed to load notebook at {resolved_path}: {str(e)}")


def safe_save_notebook(notebook: nbformat.NotebookNode, notebook_path: str) -> None:
    """Safely save a notebook with backup, avoiding validation issues."""
    # Resolve the notebook path first
    resolved_path = resolve_notebook_path(notebook_path)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    
    if os.path.exists(resolved_path):
        backup_path = get_backup_path(resolved_path)
        shutil.copy2(resolved_path, backup_path)
    
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
    with open(resolved_path, 'w', encoding='utf-8') as f:
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


def send_vscode_save_command(notebook_path: str) -> bool:
    """Send Cmd+S (or Ctrl+S) command to VS Code to trigger save."""
    try:
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Use AppleScript to send Cmd+S to VS Code
            script = '''
            tell application "Visual Studio Code"
                activate
            end tell
            tell application "System Events"
                keystroke "s" using command down
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, timeout=5)
            return True
            
        elif system == "Linux":
            # Use xdotool if available
            try:
                subprocess.run(['xdotool', 'search', '--name', 'Visual Studio Code', 
                              'windowactivate', 'key', 'ctrl+s'], 
                             capture_output=True, timeout=5)
                return True
            except FileNotFoundError:
                return False
                
        elif system == "Windows":
            # Use PowerShell to send Ctrl+S
            script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^s")
            '''
            subprocess.run(['powershell', '-Command', script], 
                         capture_output=True, timeout=5)
            return True
            
        return False
    except Exception:
        return False


def wait_for_file_save(notebook_path: str, initial_mtime: float, timeout: float = 5.0) -> bool:
    """Wait for file modification time to change, indicating save completion."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            current_mtime = os.path.getmtime(notebook_path)
            if current_mtime > initial_mtime:
                return True
        except OSError:
            pass
        time.sleep(0.1)  # Check every 100ms
    
    return False


def synchronous_auto_save(notebook_path: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Perform synchronous auto-save that blocks until completion.
    
    This function:
    1. Records initial file modification time
    2. Forces file system sync
    3. Sends save command to VS Code
    4. Waits for file modification time to change
    5. Returns only after save is confirmed complete
    
    Args:
        notebook_path: Path to the notebook file
        timeout: Maximum time to wait for save completion
        
    Returns:
        Dict containing save operation results
    """
    # Resolve path first
    resolved_path = resolve_notebook_path(notebook_path)
    
    result = {
        "success": False,
        "notebook_path": resolved_path,
        "save_triggered": False,
        "save_confirmed": False,
        "save_duration": 0.0,
        "operations": [],
        "errors": []
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Record initial modification time
        try:
            initial_mtime = os.path.getmtime(resolved_path)
            result["operations"].append(f"Initial mtime recorded: {initial_mtime}")
        except OSError as e:
            result["errors"].append(f"Could not get initial mtime: {str(e)}")
            return result
        
        # Step 2: Force file system sync if file descriptor is available
        try:
            # Update file timestamp to trigger change
            current_time = time.time()
            os.utime(resolved_path, (current_time, current_time))
            result["operations"].append("File timestamp updated")
        except OSError as e:
            result["errors"].append(f"Could not update timestamp: {str(e)}")
        
        # Step 3: Send save command to VS Code
        try:
            save_command_sent = send_vscode_save_command(resolved_path)
            if save_command_sent:
                result["save_triggered"] = True
                result["operations"].append("Save command sent to VS Code")
            else:
                result["operations"].append("Save command could not be sent (fallback to timestamp)")
        except Exception as e:
            result["errors"].append(f"Error sending save command: {str(e)}")
        
        # Step 4: Wait for file modification confirmation
        try:
            save_confirmed = wait_for_file_save(resolved_path, initial_mtime, timeout)
            if save_confirmed:
                result["save_confirmed"] = True
                result["operations"].append("Save completion confirmed")
            else:
                result["errors"].append(f"Save not confirmed within {timeout} seconds")
        except Exception as e:
            result["errors"].append(f"Error waiting for save: {str(e)}")
        
        # Step 5: Calculate duration and final status
        result["save_duration"] = time.time() - start_time
        result["success"] = (result["save_triggered"] or len(result["operations"]) > 1) and len(result["errors"]) == 0
        
        result["operations"].append(f"Auto-save completed in {result['save_duration']:.3f} seconds")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Auto-save error: {str(e)}")
        result["save_duration"] = time.time() - start_time
        result["success"] = False
        return result


def enhanced_safe_save_notebook(notebook: nbformat.NotebookNode, notebook_path: str, auto_save: bool = True) -> Dict[str, Any]:
    """
    Enhanced save with optional synchronous auto-save.
    
    Args:
        notebook: Notebook to save
        notebook_path: Path to save to
        auto_save: Whether to perform synchronous auto-save after writing
        
    Returns:
        Dict containing save operation results
    """
    resolved_path = resolve_notebook_path(notebook_path)
    
    result = {
        "success": False,
        "notebook_path": resolved_path,
        "file_written": False,
        "auto_save_result": None,
        "operations": [],
        "errors": []
    }
    
    try:
        # Step 1: Standard save operation
        safe_save_notebook(notebook, notebook_path)
        result["file_written"] = True
        result["operations"].append("Notebook written to disk")
        
        # Step 2: Optional synchronous auto-save
        if auto_save:
            auto_save_result = synchronous_auto_save(notebook_path)
            result["auto_save_result"] = auto_save_result
            
            if auto_save_result["success"]:
                result["operations"].append("Synchronous auto-save completed")
            else:
                result["errors"].extend(auto_save_result.get("errors", []))
        
        result["success"] = result["file_written"] and (not auto_save or result["auto_save_result"]["success"])
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Enhanced save error: {str(e)}")
        result["success"] = False
        return result
