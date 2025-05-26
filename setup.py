from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="local-notebook-mcp-server",
    version="1.0.0",
    author="Vivek M. Agarwal",
    author_email="vivmagarwal@gmail.com",
    description="A production-ready MCP server for local Jupyter notebook management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vivmagarwal/local-notebook-mcp-server",
    py_modules=["local_notebook_mcp_server"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "nbformat>=5.7.0",
        "jupyter-client>=7.0.0",
        "ipykernel>=6.0.0"
    ],
    entry_points={
        "console_scripts": [
            "local-notebook-mcp-server=local_notebook_mcp_server:main",
        ],
    },
)
