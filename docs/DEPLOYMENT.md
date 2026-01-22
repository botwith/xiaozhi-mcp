# Deployment Guide

## Running Locally

When running locally for development:

1. **Use local configuration:**
   - Edit `mcp_config.yaml` for your settings

2. **Connect to local endpoint:**
   ```yaml
   mcp:
     endpoint: ws://localhost:8080/mcp
   ```

3. **Run individual scripts for testing:**
   ```bash
   python src/app.py src/mcp/tools/calculator.py
   ```

4. **Use development tools:**
   - Debuggers
   - Logging
   - Hot reload (if supported)

## Running on Server

When deploying to a server:

1. **Use configuration:**
   - Edit `mcp_config.yaml` for your server settings

2. **Connect to remote endpoint:**
   ```yaml
   mcp:
     endpoint: ws://your-production-endpoint.com/mcp
     token: your-production-token
   ```

3. **Run all configured servers:**
   ```bash
   python src/app.py
   ```

4. **Use process managers:**
   - **systemd** (Linux)
   - **supervisor**
   - **PM2** (Node.js-based)
   - **Docker** containers

## Process Manager Examples

### systemd Service

Create `/etc/systemd/system/xiaozhi-mcp.service`:

```ini
[Unit]
Description=xiaozhi-mcp MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/xiaozhi-mcp
ExecStart=/usr/bin/python3 /path/to/xiaozhi-mcp/src/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable xiaozhi-mcp
sudo systemctl start xiaozhi-mcp
```

### Supervisor Configuration

Create `/etc/supervisor/conf.d/xiaozhi-mcp.conf`:

```ini
[program:xiaozhi-mcp]
command=/usr/bin/python3 /path/to/xiaozhi-mcp/src/app.py
directory=/path/to/xiaozhi-mcp
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/xiaozhi-mcp.err.log
stdout_logfile=/var/log/xiaozhi-mcp.out.log
```

Reload supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start xiaozhi-mcp
```

### Docker Deployment

#### Using Dockerfile

The project includes a `Dockerfile` in the `docker/` directory that uses Python 3.12 and uv package manager.

**Build the image:**
```bash
# Build from project root
docker build -f docker/Dockerfile -t xiaozhi-mcp .
```

**Run the container:**
```bash
# Run with default configuration
docker run -d --name xiaozhi-mcp \
  -v $(pwd)/mcp_config.yaml:/app/mcp_config.yaml:ro \
  xiaozhi-mcp
```

#### Using Docker Compose (Recommended)

The project includes a `docker-compose.example.yml` file in the `docker/` directory.

**Start the service:**
```bash
# Copy example file and start (from project root)
cp docker/docker-compose.example.yml docker-compose.yml
docker-compose -f docker-compose.yml up -d
```

**View logs:**
```bash
docker-compose -f docker-compose.yml logs -f
```

**Stop the service:**
```bash
docker-compose -f docker-compose.yml down
```

**Rebuild after code changes:**
```bash
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
```

**Customize docker-compose.yml:**

To mount config file:
```yaml
volumes:
  - ./mcp_config.yaml:/app/mcp_config.yaml:ro
```

## Environment Variables

While configuration is primarily done through YAML files, you can override specific settings:

- `MCP_CONFIG` - Path to configuration file (backward compatibility)
- `MCP_ENDPOINT` - WebSocket endpoint URL
- `MCP_TOKEN` - Authentication token

## Monitoring

Monitor your deployment:

1. **Check logs:**
   ```bash
   # systemd
   journalctl -u xiaozhi-mcp -f
   
   # supervisor
   tail -f /var/log/xiaozhi-mcp.out.log
   ```

2. **Check process status:**
   ```bash
   # systemd
   systemctl status xiaozhi-mcp
   
   # supervisor
   supervisorctl status xiaozhi-mcp
   ```

3. **Health checks:**
   - Monitor WebSocket connections
   - Check server process status
   - Verify endpoint connectivity
