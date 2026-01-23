# Project Structure

```
xiaozhi-mcp/
├── src/
│   ├── __init__.py
│   ├── app.py           # Main application
│   └── mcp/
│       ├── __init__.py
│       └── tools/
│           ├── __init__.py
│           ├── calculator.py    # Calculator MCP tool
│           ├── stock.py         # Stock query MCP tool
│           ├── email_tool.py     # Email MCP tool
│           └── netease_music.py # NetEase Music MCP tool
├── docker/
│   ├── Dockerfile              # Docker image definition
│   ├── docker-compose.example.yml  # Docker Compose example
│   ├── build-and-push.sh   # Build and push script
│   ├── .env.example            # Docker env example
│   ├── .env                    # Docker env (not in git)
│   └── .dockerignore           # Docker ignore file
├── docs/
│   ├── CONFIG.md              # Configuration guide
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── DOCKER_BUILD_PUSH.md   # Docker build & push guide
│   ├── TOOLS.md               # Tool creation guide
│   ├── PROJECT_STRUCTURE.md   # This file
│   ├── USAGE.md               # Usage examples
│   ├── HTTP_MCP_GUIDE.md      # HTTP MCP guide
│   └── MCP_AI_INTEGRATION.md  # AI integration guide
├── pyproject.toml       # Project configuration
├── requirements.txt     # Legacy dependencies
├── mcp_config.yaml      # Server configuration (YAML format)
├── README.md            # English README
└── README.zh.md         # Chinese README
```

## File Descriptions

### Core Files

- **`src/app.py`**: Main application that handles WebSocket connections and process management. Supports multiple transport types (stdio, SSE, HTTP) and config-driven server management.

- **`src/mcp/tools/calculator.py`**: Example MCP tool implementation for mathematical calculations.

- **`src/mcp/tools/stock.py`**: Stock query tool for querying stock prices and information using yfinance.

- **`src/mcp/tools/email_tool.py`**: Email tool for sending emails and managing recipients with SMTP configuration.

- **`src/netease_music.py`**: NetEase Music MCP tool for music-related operations.

### Configuration Files

- **`pyproject.toml`**: Project configuration and dependencies (uv/pip compatible). Defines project metadata, Python version requirements, and all dependencies.

- **`requirements.txt`**: Project dependencies (legacy, for pip users). Maintained for backward compatibility.

- **`mcp_config.yaml`**: Server configuration in YAML format. Defines MCP endpoint, servers, and their settings.

### Docker Files

- **`docker/Dockerfile`**: Docker image definition for building the application container.

- **`docker/docker-compose.example.yml`**: Example Docker Compose configuration for easy deployment.

- **`docker/build-and-push.sh`**: Script for building and pushing Docker images to container registries (defaults to ACR, configurable via environment variables).

- **`docker/.env.example`**: Example Docker environment configuration file.

- **`docker/.env`**: Docker environment configuration file (not committed to git, user-specific).

- **`docker/.dockerignore`**: Files and directories to exclude from Docker build context.

### Documentation

- **`README.md`**: English README with project overview, installation, and usage instructions.

- **`README.zh.md`**: Chinese README with the same content in Chinese.

- **`docs/`**: Detailed documentation covering configuration, deployment, tool creation, and more.

## Key Concepts

### Config-driven Servers

The project uses a configuration-driven approach where servers are defined in YAML files. This allows:
- Easy environment management
- Centralized configuration
- Dynamic server discovery
- Local overrides without modifying shared configs

### Transport Types

- **stdio**: Direct process communication via standard input/output
- **sse**: Server-Sent Events for remote servers
- **http**: HTTP requests for REST APIs

### Configuration

Configuration is managed through a single YAML file:
- `mcp_config.yaml` - Main configuration file
