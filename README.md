# Local Notebook MCP Server

A comprehensive **Model Context Protocol (MCP) server** for working with local Jupyter notebooks (.ipynb files). This server provides extensive tools for reading, writing, executing, and managing Jupyter notebooks without requiring a running Jupyter server.

## 🚀 Features

### 📁 **File Operations**
- Read and parse notebook files
- List notebooks in directories
- Create new notebooks
- Backup notebooks with timestamps

### 🔧 **Cell Management**
- Add cells (code, markdown, raw) at any position
- Modify existing cell content
- Delete and move cells
- Get specific cell information

### ⚡ **Code Execution**
- Execute individual cells with kernel management
- Run entire notebooks
- Restart and interrupt kernels
- Support for multiple kernel types

### 🔍 **Analysis & Search**
- Search content across all cells
- Get comprehensive notebook metadata
- Analyze imported dependencies
- Get execution history

### 📤 **Export Capabilities**
- Export to Python (.py) scripts
- Export to Markdown (.md) files
- Export to HTML (with nbconvert)

### 🛡️ **Safety Features**
- Automatic backup before modifications
- Safe file operations with error handling
- Kernel lifecycle management

## 📦 Installation

### Method 1: Install from PyPI (Recommended)

```bash
pip install local-notebook-mcp-server
```

### Method 2: Install from Source

```bash
git clone https://github.com/your-username/local-notebook-mcp-server.git
cd local-notebook-mcp-server
pip install -e .
```

### Prerequisites
- Python 3.8 or higher
- MCP-compatible client (Claude Desktop, Cline, etc.)
- Jupyter installed (`pip install jupyter`)

## 🔧 Configuration

### For Claude Desktop

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "local-notebook": {
      "command": "local-notebook-mcp-server",
      "args": [],
      "cwd": "/path/to/your/notebooks/directory"
    }
  }
}
```

### For Cline/VSCode Extension

```json
{
  "local-notebook": {
    "command": "python",
    "args": ["-m", "local_notebook_mcp_server"],
    "cwd": "/path/to/your/notebooks"
  }
}
```

### For Other MCP Clients

The server runs via stdio transport. You can run it with:

```bash
local-notebook-mcp-server
```

Or as a Python module:

```bash
python -m local_notebook_mcp_server
```

## 🛠️ Available Tools

### **File Operations**
- `read_notebook(notebook_path)` - Read and parse notebook files
- `list_notebooks(directory)` - List all notebooks in directory
- `create_notebook(notebook_path, title)` - Create new notebook
- `backup_notebook(notebook_path)` - Create timestamped backup

### **Cell Management**
- `add_cell(notebook_path, cell_type, content, index)` - Add new cell
- `modify_cell(notebook_path, index, content)` - Modify existing cell
- `delete_cell(notebook_path, index)` - Delete cell
- `get_cell(notebook_path, index)` - Get cell information
- `move_cell(notebook_path, from_index, to_index)` - Move cell position

### **Code Execution**
- `execute_cell(notebook_path, index, kernel_spec, timeout)` - Execute specific cell
- `execute_notebook(notebook_path, kernel_spec, timeout)` - Execute all code cells
- `restart_kernel(kernel_spec)` - Restart Jupyter kernel
- `interrupt_kernel()` - Interrupt running execution
- `list_kernels()` - List available kernel specifications

### **Analysis & Search**
- `search_cells(notebook_path, search_term, case_sensitive)` - Search cell content
- `get_notebook_metadata(notebook_path)` - Get comprehensive metadata
- `analyze_dependencies(notebook_path)` - Analyze imported packages

### **Export Tools**
- `export_to_python(notebook_path, output_path)` - Export to Python script
- `export_to_markdown(notebook_path, output_path)` - Export to Markdown
- `export_to_html(notebook_path, output_path)` - Export to HTML

## 🎯 Usage Examples

### Reading a Notebook
```python
# In your MCP client
result = read_notebook("hello.ipynb")
print(f"Notebook has {result['cells_count']} cells")
```

### Adding and Executing Code
```python
# Add a new code cell
add_cell("hello.ipynb", "code", "print('Hello from MCP!')", index=1)

# Execute the cell
result = execute_cell("hello.ipynb", 1)
print(result['outputs'])
```

### Searching Content
```python
# Search for specific content
matches = search_cells("hello.ipynb", "matplotlib")
print(f"Found {matches['matches_found']} matches")
```

### Export Options
```python
# Export to different formats
export_to_python("hello.ipynb", "hello_script.py")
export_to_markdown("hello.ipynb", "hello_doc.md")
```

## 🧪 Testing the Server

Create a test script to verify functionality:

```python
#!/usr/bin/env python3

import subprocess
import json

def test_mcp_server():
    # Test basic notebook reading
    cmd = ["python", "local_notebook_mcp_server.py"]
    
    # This would be how an MCP client communicates
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "read_notebook",
            "arguments": {"notebook_path": "hello.ipynb"}
        }
    }
    
    print("MCP Server ready for testing!")
    print("Use your MCP client to connect and test the tools.")

if __name__ == "__main__":
    test_mcp_server()
```

## 🔧 Kernel Management

The server automatically manages Jupyter kernels:

- **Auto-start**: Kernels start automatically when needed
- **Reuse**: Same kernel is reused for multiple executions
- **Cleanup**: Kernels are properly shut down on server exit
- **Multiple types**: Support for different kernel specifications

## 🛡️ Safety & Backups

- **Automatic backups**: Created before any modifications
- **Error handling**: Comprehensive error reporting
- **Safe operations**: File operations are protected
- **Kernel safety**: Execution timeouts prevent hanging

## 📁 Project Structure

```
├── local_notebook_mcp_server.py    # Main MCP server
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── hello.ipynb                   # Sample notebook
└── hello_backup_YYYYMMDD_HHMMSS.ipynb  # Auto backups
```

## 🐛 Troubleshooting

### Common Issues

1. **"nbformat not installed"**
   ```bash
   pip install nbformat
   ```

2. **"jupyter_client not installed"**
   ```bash
   pip install jupyter-client
   ```

3. **"mcp not installed"**
   ```bash
   pip install mcp
   ```

4. **Kernel not starting**
   - Ensure ipykernel is installed: `pip install ipykernel`
   - Check available kernels: Use the `list_kernels()` tool

5. **Permission errors**
   - Ensure write permissions in the notebook directory
   - Check file ownership and permissions

### Debug Mode

Run the server with debug output:

```bash
python local_notebook_mcp_server.py --debug
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional export formats
- More kernel types support
- Enhanced search capabilities
- Cell execution visualization
- Notebook diffing tools

## 📄 License

This project is licensed under the MIT License.

## 🔗 References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Jupyter Notebook Format](https://nbformat.readthedocs.io/)
- [Analytics Vidhya Blog Post](https://www.analyticsvidhya.com/blog/2025/05/jupyter-mcp-server/)
- [Datalayer Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server)

---

**Built for local notebook management with comprehensive MCP integration** 🚀
