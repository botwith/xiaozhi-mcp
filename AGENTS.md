# AGENTS.md - Guide for Agentic Coding

This document contains essential information for AI agents working on this repository.

## Project Overview

xiaozhi-mcp is a Python-based MCP (Model Context Protocol) project that provides tool servers for AI capabilities including calculations, email, stock queries, todo management, and more. The project uses FastMCP to create stdio-based MCP servers.

## Build/Install/Test Commands

### Installation
```bash
# Recommended: Use uv for dependency management
uv sync

# Alternative: Use pip
pip install -r requirements.txt
```

### Running the Application
```bash
# Run all configured servers from mcp_config.yaml
uv run python src/app.py

# Run a single server script
uv run python src/app.py src/mcp/tools/calculator.py

# Run with Docker
docker build -f docker/Dockerfile -t xiaozhi-mcp .
docker run -d --name xiaozhi-mcp -v $(pwd)/mcp_config.yaml:/app/mcp_config.yaml:ro xiaozhi-mcp
```

### Testing
```bash
# No test framework is currently configured
# If pytest is added: pytest tests/; pytest tests/test_file.py::test_func
```

### Linting/Type Checking
```bash
# No commands configured in pyproject.toml
# Common tools: ruff check ., ruff format ., mypy src/
```

## Code Style Guidelines

### File Structure
- Main application: `src/app.py`
- MCP tools: `src/mcp/tools/*.py`
- Each tool is a standalone FastMCP server with `@mcp.tool()` decorated functions
- Configuration: `mcp_config.yaml` (YAML format)

### Imports
```python
# Standard import order:
from fastmcp import FastMCP
import sys
import logging
# Third-party imports
import yaml
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
# Local imports (if any)
from pathlib import Path
import uuid
```

### Module Layout
```python
# 1. File docstring (optional)
# 2. Imports
# 3. Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
# 4. Logger setup
logger = logging.getLogger('ServerName')
# 5. Create MCP server
mcp = FastMCP("ServerName")
# 6. Constants (UPPER_CASE)
CONSTANT_NAME = "value"
# 7. Helper functions
# 8. Tool functions (@mcp.tool())
# 9. Main entry point
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `get_all_todos`, `send_email`)
- **Variables**: `snake_case` (e.g., `todo_data`, `result`)
- **Constants**: `UPPER_CASE` (e.g., `SMTP_HOST`, `DATA_DIR`)
- **Classes**: `PascalCase` (rarely used in this codebase)
- **File names**: `snake_case.py` (e.g., `email_tool.py`, `todo.py`)

### Type Hints
Use type hints for function signatures where applicable:
```python
from typing import Optional, Dict, List, Any

def get_todo_by_id_from_db(todo_id: str) -> Optional[Dict[str, Any]]:
    """Get a todo by ID from database."""
    pass
```

### Tool Functions
All MCP tools must:
1. Be decorated with `@mcp.tool()`
2. Have a docstring in Chinese describing the tool's purpose
3. Return dict with `"success"`, `"error"` (if False), and `"timestamp"` (ISO format) keys

```python
@mcp.tool()
def example_tool(param: str) -> dict:
    """工具描述（中文）。Args: param: 参数描述"""
    try:
        return {"success": True, "data": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}
```

### Error Handling
- Use try/except blocks for operations that may fail
- Log errors using `logger.error()` with context
- Return structured error responses with `{"success": False, "error": "...", "timestamp": "..."}`
- Validate input parameters early
- Handle specific exceptions when possible (e.g., `ValueError`, `smtplib.SMTPException`)

### Logging
- Use the standard logging module
- Create a logger for each server: `logger = logging.getLogger('ServerName')`
- Log important events at appropriate levels:
  - `logger.debug()` for detailed debugging info
  - `logger.info()` for normal operations
  - `logger.warning()` for recoverable issues
  - `logger.error()` for errors
- Include context in log messages, not just the error string

### Documentation
- Write docstrings for all tool functions in Chinese
- Include Args and Returns sections in docstrings for clarity
- Comments should be minimal; code should be self-explanatory

### Configuration
- Server configuration is in `mcp_config.yaml`
- Each server has an `enabled` field (true/false)
- Use `${path:default}` syntax for variable references
- Environment variables can be passed via the `env` section in server config

### Database Operations
- Use SQLite for local data storage (e.g., `data/todos.db`)
- Always use `conn.row_factory = sqlite3.Row` for column access by name
- Use context managers or try/finally to ensure connections are closed
- Use parameterized queries to prevent SQL injection
- Commit transactions after writes; rollback on errors

### External API Calls
- Use `httpx` for HTTP requests when needed
- Implement caching for expensive operations (e.g., stock data with 60s cache)
