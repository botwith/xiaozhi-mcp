"""
Simple MCP stdio <-> WebSocket pipe with unified config.
Version: 0.2.0

Usage:
    Configure endpoint in mcp_config.yaml:
        mcp:
          endpoint: ws://your-endpoint-url/mcp
    
    Start server process(es) from config:
    Run all configured servers (default)
        python app.py
    
    Run a single local server script (back-compat)
        python app.py path/to/server.py

Config loading:
    1. $MCP_CONFIG environment variable (if set, used directly - backward compatibility)
    2. mcp_config.yaml (default configuration file)
    3. mcp_config.json (fallback, backward compatibility)

Note:
    Endpoint is configured in mcp_config.yaml under mcp.endpoint
"""

import asyncio
import websockets
import subprocess
import logging
import os
import signal
import sys
import json
import yaml
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCP_APP')

# Reconnection settings
INITIAL_BACKOFF = 1  # Initial wait time in seconds
MAX_BACKOFF = 600  # Maximum wait time in seconds

async def connect_with_retry(uri, target):
    """Connect to WebSocket server with retry mechanism for a given server target."""
    reconnect_attempt = 0
    backoff = INITIAL_BACKOFF
    while True:  # Infinite reconnection
        try:
            if reconnect_attempt > 0:
                logger.info(f"[{target}] Waiting {backoff}s before reconnection attempt {reconnect_attempt}...")
                await asyncio.sleep(backoff)

            # Attempt to connect
            await connect_to_server(uri, target)

        except KeyboardInterrupt:
            # Don't retry on keyboard interrupt
            logger.info(f"[{target}] Interrupted by user")
            raise
        except Exception as e:
            reconnect_attempt += 1
            error_msg = str(e)
            # Provide more helpful error messages for common issues
            if "410" in error_msg or "Gone" in error_msg:
                logger.error(
                    f"[{target}] Server endpoint returned 410 Gone (endpoint expired or invalid). "
                    f"Please check your endpoint_id configuration."
                )
            else:
                logger.warning(f"[{target}] Connection closed (attempt {reconnect_attempt}): {e}")
            # Calculate wait time for next reconnection (exponential backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)

async def connect_to_server(uri, target):
    """Connect to WebSocket server and pipe stdio for the given server target."""
    try:
        logger.info(f"[{target}] Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            logger.info(f"[{target}] Successfully connected to WebSocket server")

            # Start server process (built from CLI arg or config)
            cmd, env = build_server_command(target)
            # Get the project root directory (where pyproject.toml is located)
            # This ensures uv run can find the project and virtual environment
            project_root = os.getcwd()
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                text=True,
                env=env,
                cwd=project_root  # Set working directory so uv run can find the project
            )
            logger.info(f"[{target}] Started server process: {' '.join(cmd)}")
            
            # Create two tasks: read from WebSocket and write to process, read from process and write to WebSocket
            await asyncio.gather(
                pipe_websocket_to_process(websocket, process, target),
                pipe_process_to_websocket(process, websocket, target),
                pipe_process_stderr_to_terminal(process, target)
            )
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"[{target}] WebSocket connection closed: {e}")
        raise  # Re-throw exception to trigger reconnection
    except Exception as e:
        logger.error(f"[{target}] Connection error: {e}")
        raise  # Re-throw exception
    finally:
        # Ensure the child process is properly terminated
        if 'process' in locals():
            logger.info(f"[{target}] Terminating server process")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info(f"[{target}] Server process terminated")

async def pipe_websocket_to_process(websocket, process, target):
    """Read data from WebSocket and write to process stdin"""
    try:
        while True:
            # Read message from WebSocket
            message = await websocket.recv()
            logger.debug(f"[{target}] << {message[:120]}...")
            
            # Write to process stdin (in text mode)
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            process.stdin.write(message + '\n')
            process.stdin.flush()
    except Exception as e:
        logger.error(f"[{target}] Error in WebSocket to process pipe: {e}")
        raise  # Re-throw exception to trigger reconnection
    finally:
        # Close process stdin
        if not process.stdin.closed:
            process.stdin.close()

async def pipe_process_to_websocket(process, websocket, target):
    """Read data from process stdout and send to WebSocket"""
    try:
        while True:
            # Read data from process stdout
            data = await asyncio.to_thread(process.stdout.readline)
            
            if not data:  # If no data, the process may have ended
                logger.info(f"[{target}] Process has ended output")
                break
                
            # Send data to WebSocket
            logger.debug(f"[{target}] >> {data[:120]}...")
            # In text mode, data is already a string, no need to decode
            await websocket.send(data)
    except Exception as e:
        logger.error(f"[{target}] Error in process to WebSocket pipe: {e}")
        raise  # Re-throw exception to trigger reconnection

async def pipe_process_stderr_to_terminal(process, target):
    """Read data from process stderr and print to terminal"""
    try:
        while True:
            # Read data from process stderr
            data = await asyncio.to_thread(process.stderr.readline)
            
            if not data:  # If no data, the process may have ended
                logger.info(f"[{target}] Process has ended stderr output")
                break
                
            # Print stderr data to terminal (in text mode, data is already a string)
            sys.stderr.write(data)
            sys.stderr.flush()
    except Exception as e:
        logger.error(f"[{target}] Error in process stderr pipe: {e}")
        raise  # Re-throw exception to trigger reconnection

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    logger.info("Received interrupt signal, shutting down...")
    sys.exit(0)

def deep_merge(base_dict, override_dict):
    """Deep merge two dictionaries. Values from override_dict take precedence."""
    result = base_dict.copy()
    for key, value in override_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config_file(file_path):
    """Load config file (YAML or JSON format). Returns dict or None."""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f) or {}
            else:
                # Backward compatibility: support JSON files
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config {file_path}: {e}")
        return None

def get_config_value(cfg, *keys, default=None):
    """Get nested config value by keys path. Returns default if not found."""
    value = cfg
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value

def resolve_config_variable(cfg, var_path, default=None):
    """Resolve a config variable by path (e.g., 'mcp.modelscope.api-key').
    
    Args:
        cfg: The configuration dictionary
        var_path: Dot-separated path to the config value (e.g., 'mcp.modelscope.api-key')
        default: Default value if path not found
        
    Returns:
        The resolved value or default
    """
    keys = var_path.split('.')
    return get_config_value(cfg, *keys, default=default)

def resolve_config_string(cfg, value):
    """Resolve variable references in a string value.
    
    Supports format: ${path:default} or ${path}
    Example: ${mcp.modelscope.api-key:default-value}
    
    Args:
        cfg: The configuration dictionary
        value: String value that may contain variable references
        
    Returns:
        Resolved string with variables replaced
    """
    if not isinstance(value, str):
        return value
    
    # Pattern: ${path:default} or ${path}
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
    
    def replace_var(match):
        var_path = match.group(1).strip()
        default = match.group(2) if match.group(2) is not None else None
        
        # Resolve the variable
        resolved = resolve_config_variable(cfg, var_path, default=default)
        
        # Convert to string, handling None
        if resolved is None:
            return default if default is not None else ''
        return str(resolved)
    
    return re.sub(pattern, replace_var, value)

def resolve_config_variables(cfg, root_cfg=None):
    """Recursively resolve all variable references in the configuration.
    
    This function processes the entire config dictionary and replaces
    all variable references in string values with their resolved values.
    
    Args:
        cfg: The configuration dictionary (will be modified in place)
        root_cfg: The root configuration dictionary for variable resolution (defaults to cfg)
        
    Returns:
        The configuration dictionary with variables resolved
    """
    if root_cfg is None:
        root_cfg = cfg
    
    if isinstance(cfg, dict):
        for key, value in cfg.items():
            if isinstance(value, str):
                # Resolve variables in string values using root config
                cfg[key] = resolve_config_string(root_cfg, value)
            elif isinstance(value, (dict, list)):
                # Recursively process nested structures
                resolve_config_variables(value, root_cfg)
    elif isinstance(cfg, list):
        for i, item in enumerate(cfg):
            if isinstance(item, str):
                cfg[i] = resolve_config_string(root_cfg, item)
            elif isinstance(item, (dict, list)):
                resolve_config_variables(item, root_cfg)
    
    return cfg

def get_endpoint_from_config(cfg):
    """Get MCP endpoint from config. Returns None if not configured."""
    return get_config_value(cfg, "mcp", "endpoint")

def get_servers_from_config(cfg):
    """Get servers config from config. Supports both new (mcp.servers) and old (mcpServers) format."""
    # Try new format first: mcp.servers
    servers = get_config_value(cfg, "mcp", "servers")
    if servers:
        return servers
    # Fallback to old format: mcpServers (backward compatibility)
    servers = cfg.get("mcpServers")
    if servers:
        return servers
    return {}

def is_server_enabled(server_entry):
    """Check if a server is enabled.
    
    Priority:
    1. If 'enabled' field exists, use it
    2. If 'disabled' field exists, use its inverse (backward compatibility)
    3. Default to True (enabled)
    
    Args:
        server_entry: Server configuration dict
        
    Returns:
        bool: True if server is enabled, False otherwise
    """
    if not isinstance(server_entry, dict):
        return True
    
    # Priority 1: Check 'enabled' field
    if "enabled" in server_entry:
        return bool(server_entry["enabled"])
    
    # Priority 2: Check 'disabled' field (backward compatibility)
    if "disabled" in server_entry:
        return not bool(server_entry["disabled"])
    
    # Priority 3: Default to enabled
    return True

def load_config():
    """Load YAML config file.
    
    Config loading priority:
    1. If MCP_CONFIG env var is set, use it directly (backward compatibility)
    2. mcp_config.yaml (default configuration file)
    3. mcp_config.json (fallback, backward compatibility)
    
    After loading, all variable references (${path:default}) are resolved.
    
    Returns dict or {}.
    """
    # Priority 1: Direct config path (backward compatibility)
    direct_config = os.environ.get("MCP_CONFIG")
    if direct_config:
        config = load_config_file(direct_config)
        if config is not None:
            logger.info(f"Loaded config from: {direct_config}")
            resolve_config_variables(config)
            return config
        logger.warning(f"Config file specified by MCP_CONFIG not found: {direct_config}")
        return {}
    
    # Priority 2: Load default config file
    base_dir = os.getcwd()
    default_config_path = os.path.join(base_dir, "mcp_config.yaml")
    config = load_config_file(default_config_path)
    if config is not None:
        logger.info(f"Loaded config from: {default_config_path}")
        resolve_config_variables(config)
        return config
    
    # Priority 3: Backward compatibility: try JSON format
    json_config_path = os.path.join(base_dir, "mcp_config.json")
    config = load_config_file(json_config_path)
    if config is not None:
        logger.info(f"Loaded config from: {json_config_path} (JSON format, backward compatibility)")
        resolve_config_variables(config)
        return config
    
    logger.warning("No configuration file found. Please create mcp_config.yaml")
    return {}


def build_server_command(target=None):
    """Build [cmd,...] and env for the server process for a given target.

    Priority:
    - If target matches a server in config.mcpServers: use its definition
    - Else: treat target as a Python script path (back-compat)
    If target is None, read from sys.argv[1].
    """
    if target is None:
        args = sys.argv[1:]
        if not args:
            raise RuntimeError("missing server name or script path")
        target = args[0]
    cfg = load_config()
    servers = get_servers_from_config(cfg)

    if target in servers:
        entry = servers[target] or {}
        if not is_server_enabled(entry):
            raise RuntimeError(f"Server '{target}' is disabled in config")
        typ = (entry.get("type") or entry.get("transportType") or "stdio").lower()

        # environment for child process
        child_env = os.environ.copy()
        for k, v in (entry.get("env") or {}).items():
            child_env[str(k)] = str(v)
        
        # If server has smtp config, pass it as environment variables
        smtp_config = entry.get("smtp")
        if smtp_config:
            child_env["SMTP_HOST"] = str(smtp_config.get("host", ""))
            child_env["SMTP_PORT"] = str(smtp_config.get("port", ""))
            child_env["SMTP_USER"] = str(smtp_config.get("user", ""))
            child_env["SMTP_PASSWORD"] = str(smtp_config.get("password", ""))
            child_env["SMTP_FROM_EMAIL"] = str(smtp_config.get("from_email", smtp_config.get("user", "")))
            child_env["SMTP_FROM_NAME"] = str(smtp_config.get("from_name", "MCP Email Tool"))

        if typ == "stdio":
            command = entry.get("command")
            args = entry.get("args") or []
            if not command:
                raise RuntimeError(f"Server '{target}' is missing 'command'")
            
            # If command is 'uv', replace it with the virtual environment Python interpreter
            # This ensures the subprocess uses the correct environment with all dependencies
            if command == "uv" and len(args) >= 2 and args[0] == "run" and args[1] == "python":
                # Use the virtual environment Python directly
                # In Docker, the venv is typically at /app/.venv/bin/python
                venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
                if os.path.exists(venv_python):
                    # Replace 'uv run python' with direct venv python path
                    new_args = args[2:]  # Get the script path and remaining args
                    return [venv_python] + new_args, child_env
                else:
                    # Fallback: try to find Python in common venv locations
                    for venv_path in [".venv", "venv", ".env"]:
                        venv_python = os.path.join(os.getcwd(), venv_path, "bin", "python")
                        if os.path.exists(venv_python):
                            new_args = args[2:]
                            return [venv_python] + new_args, child_env
                    # If no venv found, log warning but continue with original command
                    logger.warning(f"[{target}] Virtual environment not found, using original command: {command}")
            
            return [command, *args], child_env

        if typ in ("sse", "http", "streamablehttp"):
            url = entry.get("url")
            if not url:
                raise RuntimeError(f"Server '{target}' (type {typ}) is missing 'url'")
            
            # Unified approach: always use current Python to run mcp-proxy module
            cmd = [sys.executable, "-m", "mcp_proxy"]
            if typ in ("http", "streamablehttp"):
                cmd += ["--transport", "streamablehttp"]
            # optional headers: {"Authorization": "Bearer xxx"}
            headers = entry.get("headers") or {}
            for hk, hv in headers.items():
                cmd += ["-H", hk, str(hv)]
            cmd.append(url)
            return cmd, child_env

        raise RuntimeError(f"Unsupported server type: {typ}")

    # Fallback to script path (back-compat)
    script_path = target
    if not os.path.exists(script_path):
        raise RuntimeError(
            f"'{target}' is neither a configured server nor an existing script"
        )
    return [sys.executable, script_path], os.environ.copy()

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Determine target: default to all if no arg; single target otherwise
    args = sys.argv[1:]
    target_arg = args[0] if args else None
    
    # Load config
    cfg = load_config()
    endpoint_url = get_endpoint_from_config(cfg)
    if not endpoint_url:
        logger.error("Please configure `mcp.endpoint` in mcp_config.yaml")
        sys.exit(1)

    async def _main():
        if not target_arg:
            servers_cfg = get_servers_from_config(cfg)
            all_servers = list(servers_cfg.items())
            enabled = [name for name, entry in all_servers if is_server_enabled(entry)]
            skipped = [name for name, entry in all_servers if name not in enabled]
            if skipped:
                logger.info(f"Skipping disabled servers: {', '.join(skipped)}")
            if not enabled:
                raise RuntimeError("No enabled mcpServers found in config")
            logger.info(f"Starting servers: {', '.join(enabled)}")
            tasks = [asyncio.create_task(connect_with_retry(endpoint_url, t)) for t in enabled]
            # Run all forever; if any crashes it will auto-retry inside
            # Use return_exceptions=True to prevent one server failure from crashing all servers
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Log any exceptions that occurred
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Server '{enabled[i]}' failed with exception: {result}")
        else:
            if os.path.exists(target_arg):
                await connect_with_retry(endpoint_url, target_arg)
            else:
                logger.error("Argument must be a local Python script path. To run configured servers, run without arguments.")
                sys.exit(1)

    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Program execution error: {e}")
