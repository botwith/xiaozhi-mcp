# Configuration Guide

## Configuration File Structure

Configuration files use YAML format:

- `mcp_config.yaml` - Main configuration file

## Basic Configuration

Edit `mcp_config.yaml` to configure your MCP endpoint and servers:

```yaml
mcp:
  # WebSocket endpoint URL (can be overridden by MCP_ENDPOINT env var)
  endpoint: ws://localhost:8080/mcp
  
  # Optional: Token for authentication (can be overridden by MCP_TOKEN env var)
  # token: your-token-here

  # MCP servers configuration
  servers:
    local-stdio-calculator:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/calculator.py
    
    local-stdio-stock:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/stock.py
    
    local-stdio-email:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/email_tool.py
      smtp:
        host: smtp.example.com
        port: 587
        user: your-email@example.com
        password: your-password
        from_email: your-email@example.com
        from_name: Your Name
```

## Server Types

### stdio Servers

For local Python scripts that communicate via standard input/output:

```yaml
local-stdio-calculator:
  enabled: true
  type: stdio
  command: python
  args:
    - src/mcp/tools/calculator.py
```

### SSE Servers

For remote servers using Server-Sent Events:

```yaml
remote-sse-server:
  enabled: true
  type: sse
  url: https://api.example.com/sse
```

### HTTP Servers

For remote servers using HTTP:

```yaml
remote-http-server:
  enabled: true
  type: http
  url: https://api.example.com/mcp
  headers:
    Authorization: Bearer YOUR_API_KEY_HERE
    Content-Type: application/json
```

## Configuration Notes

- Servers with `enabled: false` are automatically skipped
- `type=stdio` servers are started directly
- `type=sse/http` servers are proxied through `python -m mcp_proxy`
- When using uv, commands automatically use `uv run python` execution
