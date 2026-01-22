# xiaozhi-mcp

A powerful interface for extending AI capabilities through remote control, calculations, email operations, knowledge search, and more.

## About

MCP (Model Context Protocol) is a protocol that allows servers to expose tools that can be invoked by language models. This project provides a flexible framework for creating and managing MCP tools, supporting multiple transport types (stdio, SSE, HTTP) and enabling seamless integration between AI models and external systems.

**Key Features:**
- 🔌 Bidirectional communication between AI and external tools
- 🔄 Automatic reconnection with exponential backoff
- 📊 Real-time data streaming
- 🛠️ Easy-to-use tool creation interface
- 🔒 Secure WebSocket communication
- ⚙️ Multiple transport types support (stdio/sse/http)

## How to Install

### Using uv (Recommended)

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

### Using pip

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+
- websockets>=16.0
- python-dotenv>=1.2.1
- mcp>=1.25.0
- pydantic>=2.12.5
- mcp-proxy>=0.11.0
- fastmcp>=2.14.3
- httpx>=0.28.1
- yfinance>=1.0
- pyyaml>=6.0.3

## How to Run

### Run All Configured Servers

Start all enabled servers from the configuration file:

```bash
# Using uv
uv run python src/app.py

# Using pip
python src/app.py
```

### Run a Single Server Script

Run a specific server script directly:

```bash
# Using uv
uv run python src/app.py src/mcp/tools/calculator.py

# Using pip
python src/app.py src/mcp/tools/calculator.py
```


### Run with Docker

#### Using Docker Compose (Recommended)

```bash
# Copy example docker-compose file
cp docker/docker-compose.example.yml docker-compose.yml

# Start the service (from project root)
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose -f docker-compose.yml logs -f

# Stop the service
docker-compose -f docker-compose.yml down

# Rebuild after code changes
docker-compose -f docker-compose.yml build && docker-compose -f docker-compose.yml up -d
```

#### Using Docker directly

```bash
# Build the image (from project root)
docker build -f docker/Dockerfile -t xiaozhi-mcp .

# Run the container
docker run -d --name xiaozhi-mcp \
  -v $(pwd)/mcp_config.yaml:/app/mcp_config.yaml:ro \
  xiaozhi-mcp
```

#### Building and Pushing Docker Images

**Build and push to registry:**

```bash
# Build image with version tag (from project root)
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .

# Tag for registry (replace with your registry address)
docker tag xiaozhi-mcp:latest <registry>/<namespace>/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 <registry>/<namespace>/xiaozhi-mcp:1.0.0

# Push to registry
docker push <registry>/<namespace>/xiaozhi-mcp:latest
docker push <registry>/<namespace>/xiaozhi-mcp:1.0.0
```

**Example - Aliyun Container Registry:**
```bash
# Example registry address format
REGISTRY="<your-registry>.cn-shanghai.personal.cr.aliyuncs.com"
NAMESPACE="<your-namespace>"

# Build and tag (from project root)
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .
docker tag xiaozhi-mcp:latest ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:1.0.0

# Push
docker push ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:latest
docker push ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:1.0.0
```

**Using the provided script:**
```bash
# Use the build-and-push-acr.sh script (from project root)
# Script will automatically use docker/Dockerfile and docker/.env
./docker/build-and-push-acr.sh 1.0.0
```

For more Docker build and push options, see [docs/DOCKER_BUILD_PUSH.md](docs/DOCKER_BUILD_PUSH.md).

For more Docker deployment options, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Configs

Configuration files use YAML format:

- `mcp_config.yaml` - Main configuration file

### Configuration Structure

Edit `mcp_config.yaml` to configure your MCP endpoint and servers:

```yaml
mcp:
  endpoint: ws://your-endpoint-url/mcp
  token: your-token-here  # Optional
  
  servers:
    local-stdio-calculator:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/calculator.py
```

For detailed configuration examples, see [docs/CONFIG.md](docs/CONFIG.md).

### Config Loading Priority

1. `MCP_CONFIG` environment variable (if set, used directly - backward compatibility)
2. `mcp_config.yaml` (default configuration file)
3. `mcp_config.json` (fallback, backward compatibility)

## Thanks To

- Thanks to all contributors who have helped shape this project
- Inspired by the need for extensible AI capabilities
- Built on top of the MCP (Model Context Protocol) specification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
