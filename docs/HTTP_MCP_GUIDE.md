# HTTP服务作为MCP工具指南

## 概述

MCP (Model Context Protocol) 支持通过HTTP/SSE协议连接外部服务，使其作为MCP工具使用。本文档详细说明如何配置和使用外部HTTP服务。

## 支持的传输类型

MCP支持三种传输类型：

1. **stdio** - 标准输入输出（本地Python脚本）
2. **sse** - Server-Sent Events（单向流）
3. **http** - HTTP请求（双向通信，也称为streamablehttp）

## 配置外部HTTP服务

### 1. 编辑 mcp_config.json

在 `mcp_config.json` 中添加HTTP服务配置：

```json
{
  "mcpServers": {
    "remote-http-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY",
        "X-Custom-Header": "custom-value"
      }
    },
    "remote-sse-server": {
      "type": "sse",
      "url": "https://api.example.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### 2. 配置参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 传输类型：`http`、`sse` 或 `stdio` |
| `url` | string | 是 | HTTP服务的完整URL |
| `headers` | object | 否 | HTTP请求头（用于认证等） |
| `disabled` | boolean | 否 | 是否禁用该服务（默认false） |

### 3. HTTP vs SSE 的选择

- **HTTP (streamablehttp)**: 适用于需要双向通信的场景，支持流式响应
- **SSE**: 适用于服务器推送数据的单向流场景

## 工作原理

当配置为HTTP/SSE类型时，`app.py` 会：

1. 使用 `python -m mcp_proxy` 启动代理进程
2. 通过代理连接到指定的HTTP服务URL
3. 在WebSocket（MCP_ENDPOINT）和HTTP服务之间建立双向管道
4. 自动处理重连和错误恢复

## 启动配置的HTTP服务

### 启动所有配置的服务（包括HTTP服务）

```bash
# 使用 uv
uv run python src/app.py

# 或使用 pip
python src/app.py
```

这会启动 `mcp_config.json` 中所有未禁用的服务。

### 启动特定的HTTP服务

```bash
# 使用 uv
uv run python src/app.py remote-http-server

# 或使用 pip
python src/app.py remote-http-server
```

## 实际示例

### 示例1：连接OpenAI API作为MCP工具

```json
{
  "mcpServers": {
    "openai-mcp": {
      "type": "http",
      "url": "https://api.openai.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer sk-your-api-key-here",
        "Content-Type": "application/json"
      }
    }
  }
}
```

### 示例2：连接自定义API服务

```json
{
  "mcpServers": {
    "my-api-server": {
      "type": "http",
      "url": "https://my-api.example.com/mcp-endpoint",
      "headers": {
        "X-API-Key": "your-secret-key",
        "X-Client-ID": "mcp-client"
      }
    }
  }
}
```

### 示例3：使用SSE连接流式服务

```json
{
  "mcpServers": {
    "streaming-service": {
      "type": "sse",
      "url": "https://stream.example.com/events",
      "headers": {
        "Authorization": "Bearer token123"
      }
    }
  }
}
```

## 环境变量支持

为了安全起见，建议将敏感信息（如API密钥）存储在环境变量中：

### 1. 创建 .env 文件

```bash
cp env.example .env
```

### 2. 在 .env 中添加变量

```bash
OPENAI_API_KEY=sk-your-api-key-here
MY_API_SECRET=your-secret-key
```

### 3. 在 mcp_config.json 中引用

```json
{
  "mcpServers": {
    "openai-mcp": {
      "type": "http",
      "url": "https://api.openai.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${OPENAI_API_KEY}"
      }
    }
  }
}
```

**注意**: 当前版本的 `app.py` 不直接支持环境变量替换。如需此功能，可以：

1. 在启动脚本中设置环境变量
2. 或者使用 `env` 字段传递环境变量给子进程（仅适用于stdio类型）

## 故障排查

### 问题1：连接失败

**错误信息**: `Failed to connect to HTTP server`

**解决方法**:
1. 检查URL是否正确且可访问
2. 验证API密钥是否有效
3. 检查网络连接和防火墙设置
4. 查看日志输出获取详细错误信息

### 问题2：认证错误

**错误信息**: `401 Unauthorized` 或 `403 Forbidden`

**解决方法**:
1. 确认headers中的认证信息正确
2. 检查API密钥是否过期
3. 验证API密钥是否有访问权限

### 问题3：mcp_proxy模块未找到

**错误信息**: `ModuleNotFoundError: No module named 'mcp_proxy'`

**解决方法**:
```bash
# 安装 mcp-proxy
uv add mcp-proxy
# 或
pip install mcp-proxy
```

### 问题4：服务被禁用

**错误信息**: `Server 'xxx' is disabled in config`

**解决方法**:
在 `mcp_config.json` 中移除或设置 `"disabled": false`：

```json
{
  "mcpServers": {
    "remote-http-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "disabled": false
    }
  }
}
```

## 高级配置

### 自定义环境变量（仅stdio类型）

对于本地stdio服务，可以通过 `env` 字段设置环境变量：

```json
{
  "mcpServers": {
    "local-service": {
      "type": "stdio",
      "command": "python",
      "args": ["src/my_service.py"],
      "env": {
        "API_KEY": "your-key",
        "DEBUG": "true"
      }
    }
  }
}
```

### 禁用特定服务

临时禁用某个服务而不删除配置：

```json
{
  "mcpServers": {
    "remote-http-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "disabled": true
    }
  }
}
```

## 安全建议

1. **不要将敏感信息硬编码在配置文件中**
   - 使用环境变量存储API密钥
   - 将 `.env` 文件添加到 `.gitignore`

2. **使用HTTPS**
   - 始终使用 `https://` 而非 `http://`
   - 验证SSL证书

3. **限制API密钥权限**
   - 为MCP服务创建专用的API密钥
   - 只授予必要的权限

4. **定期轮换密钥**
   - 定期更新API密钥
   - 监控异常使用情况

## 完整示例

以下是一个完整的 `mcp_config.json` 示例，包含所有类型的配置：

```json
{
  "mcpServers": {
    "local-calculator": {
      "type": "stdio",
      "command": "python",
      "args": ["src/mcp/tools/calculator.py"]
    },
    "local-stock": {
      "type": "stdio",
      "command": "python",
      "args": ["src/mcp/tools/stock.py"]
    },
    "remote-openai": {
      "type": "http",
      "url": "https://api.openai.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer sk-your-key-here"
      }
    },
    "remote-streaming": {
      "type": "sse",
      "url": "https://stream.example.com/events",
      "headers": {
        "Authorization": "Bearer token123"
      }
    },
    "disabled-service": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "disabled": true
    }
  }
}
```

## 相关文档

- [../README.md](../README.md) - 项目概述和快速开始
- [USAGE.md](USAGE.md) - 使用指南
- [MCP_AI_INTEGRATION.md](MCP_AI_INTEGRATION.md) - AI集成说明

## 总结

添加外部HTTP服务作为MCP工具的步骤：

1. ✅ 在 `mcp_config.json` 中添加HTTP服务配置
2. ✅ 设置正确的URL和认证headers
3. ✅ 确保 `mcp-proxy` 已安装
4. ✅ 运行 `python src/app.py` 启动服务
5. ✅ 通过MCP协议调用HTTP服务提供的工具

通过这种方式，你可以轻松地将任何符合MCP协议的HTTP服务集成到你的AI应用中。
