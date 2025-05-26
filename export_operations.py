"""
Export operations for notebooks.
"""

from typing import Any, Dict, Optional

try:
    import nbformat
    from nbformat import v4 as nbf
except ImportError:
    print("Error: nbformat not installed. Install with: pip install nbformat")
    exit(1)

# Optional dependencies
try:
    import nbconvert
    NBCONVERT_AVAILABLE = True
except ImportError:
    NBCONVERT_AVAILABLE = False

try:
    from .notebook_utils import safe_load_notebook, extract_output_text
except ImportError:
    from notebook_utils import safe_load_notebook, extract_output_text


def export_notebook_to_python(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to Python script (.py file)."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.py')
        
        python_code = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                python_code.append(f"# Cell {i + 1}")
                python_code.append(cell.source)
                python_code.append("")
            elif cell.cell_type == "markdown":
                # Convert markdown to comments
                python_code.append(f"# Markdown Cell {i + 1}")
                for line in cell.source.split('\n'):
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


def export_notebook_to_markdown(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to Markdown (.md file)."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.md')
        
        markdown_content = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "markdown":
                markdown_content.append(cell.source)
                markdown_content.append("")
            elif cell.cell_type == "code":
                markdown_content.append("```python")
                markdown_content.append(cell.source)
                markdown_content.append("```")
                markdown_content.append("")
                
                # Include outputs if available
                if cell.outputs:
                    markdown_content.append("**Output:**")
                    for output in cell.outputs:
                        output_text = extract_output_text(output)
                        if output_text.strip():
                            markdown_content.append("```")
                            markdown_content.append(output_text)
                            markdown_content.append("```")
                    markdown_content.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path,
            "total_cells_exported": len(notebook.cells)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_notebook_to_html(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to HTML using nbconvert (if available)."""
    if not NBCONVERT_AVAILABLE:
        return {"success": False, "error": "nbconvert not available. Install with: pip install nbconvert"}
    
    try:
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.html')
        
        html_exporter = nbconvert.HTMLExporter()
        (body, resources) = html_exporter.from_filename(notebook_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_notebook_to_pdf(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to PDF using nbconvert (if available)."""
    if not NBCONVERT_AVAILABLE:
        return {"success": False, "error": "nbconvert not available. Install with: pip install nbconvert"}
    
    try:
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '.pdf')
        
        pdf_exporter = nbconvert.PDFExporter()
        (body, resources) = pdf_exporter.from_filename(notebook_path)
        
        with open(output_path, 'wb') as f:
            f.write(body)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_notebook_to_slides(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export notebook to HTML slides using nbconvert (if available)."""
    if not NBCONVERT_AVAILABLE:
        return {"success": False, "error": "nbconvert not available. Install with: pip install nbconvert"}
    
    try:
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '_slides.html')
        
        slides_exporter = nbconvert.SlidesExporter()
        (body, resources) = slides_exporter.from_filename(notebook_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_notebook_code_only(notebook_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Export only the code cells from a notebook to a Python file."""
    try:
        notebook = safe_load_notebook(notebook_path)
        
        if output_path is None:
            output_path = notebook_path.replace('.ipynb', '_code_only.py')
        
        python_code = []
        code_cell_count = 0
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code" and cell.source.strip():
                python_code.append(f"# Code Cell {code_cell_count + 1} (Original Cell {i + 1})")
                python_code.append(cell.source)
                python_code.append("")
                code_cell_count += 1
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(python_code))
        
        return {
            "success": True,
            "notebook_path": notebook_path,
            "output_path": output_path,
            "code_cells_exported": code_cell_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_export_formats() -> Dict[str, Any]:
    """Get available export formats."""
    formats = {
        "python": {
            "extension": ".py",
            "description": "Python script with all cells",
            "available": True
        },
        "python_code_only": {
            "extension": "_code_only.py",
            "description": "Python script with code cells only",
            "available": True
        },
        "markdown": {
            "extension": ".md",
            "description": "Markdown document",
            "available": True
        },
        "html": {
            "extension": ".html",
            "description": "HTML document",
            "available": NBCONVERT_AVAILABLE
        },
        "pdf": {
            "extension": ".pdf",
            "description": "PDF document",
            "available": NBCONVERT_AVAILABLE
        },
        "slides": {
            "extension": "_slides.html",
            "description": "HTML slides presentation",
            "available": NBCONVERT_AVAILABLE
        }
    }
    
    return {
        "success": True,
        "formats": formats,
        "nbconvert_available": NBCONVERT_AVAILABLE
    }
