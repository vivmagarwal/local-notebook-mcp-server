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

### For Cline/VS Code Extension

#### Step 1: Install the Server
First, install the server in your Python environment:

```bash
pip install local-notebook-mcp-server
```

Or install from source:
```bash
git clone https://github.com/your-username/local-notebook-mcp-server.git
cd local-notebook-mcp-server
pip install -e .
```

#### Step 2: Find the Server Location
Find where the server was installed:

```bash
which local-notebook-mcp-server
```

This will return the full path, e.g., `/Users/username/Library/Caches/pypoetry/virtualenvs/your-env/bin/local-notebook-mcp-server`

#### Step 3: Configure Cline
Add to your Cline MCP settings file (`~/.config/cline/settings.json` or access through VS Code settings):

```json
{
  "mcpServers": {
    "local-notebook-mcp-server": {
      "autoApprove": [
        "read_notebook",
        "list_notebooks",
        "create_notebook",
        "backup_notebook",
        "add_cell",
        "modify_cell",
        "delete_cell",
        "get_cell",
        "move_cell",
        "duplicate_cell",
        "search_cells",
        "get_notebook_metadata",
        "analyze_dependencies",
        "export_to_python",
        "export_to_markdown",
        "export_to_html",
        "export_code_only",
        "list_kernels"
      ],
      "disabled": false,
      "timeout": 300,
      "command": "/full/path/to/local-notebook-mcp-server",
      "args": [],
      "cwd": "/path/to/your/notebooks/directory",
      "transportType": "stdio"
    }
  }
}
```

**Important Notes:**
- Replace `/full/path/to/local-notebook-mcp-server` with the actual path from Step 2
- Replace `/path/to/your/notebooks/directory` with your actual notebooks directory
- The `autoApprove` list enables automatic approval of common operations for smoother workflow
- Set `disabled: false` to enable the server

#### Step 4: Restart VS Code
Restart VS Code or reload the Cline extension to pick up the new configuration.

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

6. **"Read-only file system" error**
   - This can occur when using relative paths with some MCP clients
   - **Solution**: Use absolute paths for notebook operations
   - Example: Use `/full/path/to/notebook.ipynb` instead of `notebook.ipynb`
   - The server works best when notebook paths are fully qualified

### Path Requirements

**Important**: Some MCP clients may have issues with relative paths. For best compatibility:

- ✅ **Recommended**: Use absolute paths like `/Users/username/notebooks/hello.ipynb`
- ❌ **May fail**: Relative paths like `hello.ipynb` or `./notebooks/hello.ipynb`

Example of correct usage:
```python
# Good - absolute path
create_notebook("/Users/username/notebooks/new_notebook.ipynb", "My Notebook")

# May fail - relative path
create_notebook("new_notebook.ipynb", "My Notebook")  # Can cause "Read-only file system" error
```

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
- [Datalayer Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server)

---

**Built for local notebook management with comprehensive MCP integration** 🚀
