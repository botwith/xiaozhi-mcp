# Creating MCP Tools

## Overview

This guide explains how to create your own MCP tools using the FastMCP framework.

## Basic Tool Structure

Here's a simple example of creating an MCP tool:

```python
from fastmcp import FastMCP

mcp = FastMCP("YourToolName")

@mcp.tool()
def your_tool(parameter: str) -> dict:
    """Tool description here"""
    # Your implementation
    return {"success": True, "result": result}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Example Tools

### Calculator Tool

**File:** `src/mcp/tools/calculator.py`

Performs mathematical calculations:

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Stock Tool

**File:** `src/mcp/tools/stock.py`

Query stock prices and information:

- `query_stock(symbol)`: Query a single stock by symbol (e.g., 'AAPL', 'GOOGL')
- `query_multiple_stocks(symbols)`: Query multiple stocks at once (comma-separated)
- `list_available_stocks()`: List all available stock symbols

**Supported stock symbols:** AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA, BABA, TSM, NFLX

### Email Tool

**File:** `src/mcp/tools/email_tool.py`

Send emails and manage recipients:

- `list_recipients()`: List all available recipients
- `get_recipient(email)`: Get recipient information by email address
- `send_email(to_email, subject, body, is_html)`: Send email to a single recipient

**Note:** Email tool SMTP configuration is in `mcp_config.yaml` under `mcp.servers.{server-name}.smtp`

## Tool Configuration

Add your tool to `mcp_config.yaml`:

```yaml
mcp:
  servers:
    local-stdio-your-tool:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/your_tool.py
```

## Best Practices

1. **Error Handling:** Always return structured error responses
2. **Documentation:** Provide clear tool descriptions
3. **Type Hints:** Use type hints for better IDE support
4. **Testing:** Test tools individually before adding to config
5. **Logging:** Use appropriate logging levels

## Transport Types

Tools can use different transport types:

- **stdio**: Standard input/output (for local Python scripts)
- **sse**: Server-Sent Events (for remote servers)
- **http**: HTTP requests (for REST APIs)

For stdio tools, use `mcp.run(transport="stdio")` in your script.
