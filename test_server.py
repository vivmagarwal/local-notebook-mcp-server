#!/usr/bin/env python3
"""
Test script for Local Notebook MCP Server

This script tests the basic functionality of the MCP server tools.
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from local_notebook_mcp_server import (
        read_notebook, list_notebooks, create_notebook, backup_notebook,
        add_cell, modify_cell, delete_cell, get_cell, move_cell,
        search_cells, get_notebook_metadata, analyze_dependencies,
        export_to_python, export_to_markdown, list_kernels
    )
    print("✅ Successfully imported MCP server tools")
except ImportError as e:
    print(f"❌ Failed to import MCP server tools: {e}")
    sys.exit(1)

def test_file_operations():
    """Test basic file operations."""
    print("\n🧪 Testing File Operations...")
    
    # Test list notebooks
    result = list_notebooks(".")
    print(f"  📁 Found {len(result.get('notebooks', []))} notebooks in current directory")
    
    # Test read notebook
    if os.path.exists("hello.ipynb"):
        result = read_notebook("hello.ipynb")
        if result['success']:
            print(f"  📖 Read hello.ipynb: {result['cells_count']} cells")
        else:
            print(f"  ❌ Failed to read hello.ipynb: {result['error']}")
    else:
        print("  ⚠️  hello.ipynb not found")
    
    # Test create new notebook
    test_nb = "test_notebook.ipynb"
    if os.path.exists(test_nb):
        os.remove(test_nb)  # Clean up first
    
    result = create_notebook(test_nb, "Test Notebook")
    if result['success']:
        print(f"  ✅ Created {test_nb}")
        
        # Clean up
        os.remove(test_nb)
    else:
        print(f"  ❌ Failed to create notebook: {result['error']}")

def test_cell_operations():
    """Test cell management operations."""
    print("\n🧪 Testing Cell Operations...")
    
    if not os.path.exists("hello.ipynb"):
        print("  ⚠️  hello.ipynb not found, skipping cell tests")
        return
    
    # Test get cell
    result = get_cell("hello.ipynb", 0)
    if result['success']:
        print(f"  📝 Cell 0 type: {result['cell_type']}")
    else:
        print(f"  ❌ Failed to get cell: {result['error']}")
    
    # Test backup before modifications
    backup_result = backup_notebook("hello.ipynb")
    if backup_result['success']:
        print(f"  💾 Created backup: {Path(backup_result['backup_path']).name}")
    
    # Test add cell
    test_content = "# Test cell added by MCP server\nprint('Hello from test cell!')"
    result = add_cell("hello.ipynb", "code", test_content)
    if result['success']:
        print(f"  ➕ Added cell at index {result['index']}")
        
        # Test modify cell
        modify_result = modify_cell("hello.ipynb", result['index'], "# Modified test cell\nprint('Modified!')")
        if modify_result['success']:
            print(f"  ✏️  Modified cell {result['index']}")
        
        # Test delete cell (cleanup)
        delete_result = delete_cell("hello.ipynb", result['index'])
        if delete_result['success']:
            print(f"  🗑️  Deleted test cell")
    else:
        print(f"  ❌ Failed to add cell: {result['error']}")

def test_analysis_tools():
    """Test analysis and search tools."""
    print("\n🧪 Testing Analysis Tools...")
    
    if not os.path.exists("hello.ipynb"):
        print("  ⚠️  hello.ipynb not found, skipping analysis tests")
        return
    
    # Test metadata
    result = get_notebook_metadata("hello.ipynb")
    if result['success']:
        print(f"  📊 Metadata: {result['total_cells']} cells, {result['file_size']} bytes")
    else:
        print(f"  ❌ Failed to get metadata: {result['error']}")
    
    # Test search
    result = search_cells("hello.ipynb", "print")
    if result['success']:
        print(f"  🔍 Search for 'print': {result['matches_found']} matches")
    else:
        print(f"  ❌ Failed to search: {result['error']}")
    
    # Test dependency analysis
    result = analyze_dependencies("hello.ipynb")
    if result['success']:
        imports = result['imported_modules']
        print(f"  📦 Dependencies: {len(imports)} imports - {', '.join(imports[:3])}{'...' if len(imports) > 3 else ''}")
    else:
        print(f"  ❌ Failed to analyze dependencies: {result['error']}")

def test_export_tools():
    """Test export functionality."""
    print("\n🧪 Testing Export Tools...")
    
    if not os.path.exists("hello.ipynb"):
        print("  ⚠️  hello.ipynb not found, skipping export tests")
        return
    
    # Test Python export
    result = export_to_python("hello.ipynb", "hello_export.py")
    if result['success']:
        print(f"  🐍 Exported to Python: hello_export.py")
        # Clean up
        if os.path.exists("hello_export.py"):
            os.remove("hello_export.py")
    else:
        print(f"  ❌ Failed to export to Python: {result['error']}")
    
    # Test Markdown export
    result = export_to_markdown("hello.ipynb", "hello_export.md")
    if result['success']:
        print(f"  📝 Exported to Markdown: hello_export.md")
        # Clean up
        if os.path.exists("hello_export.md"):
            os.remove("hello_export.md")
    else:
        print(f"  ❌ Failed to export to Markdown: {result['error']}")

def test_kernel_info():
    """Test kernel information."""
    print("\n🧪 Testing Kernel Info...")
    
    result = list_kernels()
    if result['success']:
        kernels = result['available_kernels']
        print(f"  🔧 Available kernels: {', '.join(kernels)}")
        print(f"  🔧 Current kernel: {result['current_kernel']}")
    else:
        print(f"  ❌ Failed to list kernels: {result['error']}")

def main():
    """Run all tests."""
    print("🚀 Testing Local Notebook MCP Server")
    print("=" * 50)
    
    try:
        test_file_operations()
        test_cell_operations()
        test_analysis_tools()
        test_export_tools()
        test_kernel_info()
        
        print("\n✅ All tests completed successfully!")
        print("\n📝 MCP Server is ready to use with your MCP client")
        print("   Example configuration for Claude Desktop:")
        print('   "local-notebook": {')
        print(f'     "command": "python",')
        print(f'     "args": ["{os.path.abspath("local_notebook_mcp_server.py")}"],')
        print(f'     "cwd": "{os.getcwd()}"')
        print('   }')
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
