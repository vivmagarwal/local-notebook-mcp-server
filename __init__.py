"""
Local Notebook MCP Server

A comprehensive MCP server for working with local Jupyter notebooks (.ipynb files).
Works directly with files without requiring a running Jupyter server.
"""

__version__ = "1.0.0"
__author__ = "Vivek M. Agarwal"
__email__ = "vivmagarwal@gmail.com"

from .local_notebook_mcp_server import mcp

__all__ = ["mcp"]
