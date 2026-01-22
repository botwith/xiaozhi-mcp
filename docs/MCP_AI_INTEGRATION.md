# AI 如何触发 MCP 工具

## MCP 工作流程概述

MCP (Model Context Protocol) 是一个标准化的协议，允许 AI 模型通过统一的方式调用外部工具。以下是完整的工作流程：

```
AI 模型 (Claude/ChatGPT等)
    ↓ (WebSocket 连接)
MCP 代理服务器 (app.py)
    ↓ (stdio 管道)
MCP 工具服务器 (calculator.py/stock.py/email_tool.py)
    ↓ (执行工具函数)
返回结果
    ↑ (通过相同路径返回)
AI 模型接收结果
```

## 详细流程说明

### 1. 架构组件

#### AI 模型端
- **角色**：发起工具调用请求
- **协议**：通过 WebSocket 连接到 MCP 代理服务器
- **行为**：发送 JSON-RPC 格式的工具调用请求

#### MCP 代理服务器 (`app.py`)
- **角色**：WebSocket 和 stdio 之间的桥梁
- **功能**：
  - 接收 AI 的 WebSocket 请求
  - 将请求转发给对应的 MCP 工具服务器（通过 stdio）
  - 将工具服务器的响应返回给 AI（通过 WebSocket）

#### MCP 工具服务器 (`calculator.py`, `stock.py`, `email_tool.py`)
- **角色**：实际执行工具逻辑
- **框架**：使用 FastMCP 框架
- **协议**：通过 stdio 与代理服务器通信

### 2. 工具注册机制

每个工具服务器使用 `@mcp.tool()` 装饰器注册工具：

```python
# 示例：stock.py
from fastmcp import FastMCP

mcp = FastMCP("Stock")

@mcp.tool()
def query_stock(symbol: str) -> dict:
    """查询股票信息"""
    # 工具实现逻辑
    return {"success": True, "data": {...}}
```

FastMCP 会自动：
1. 将函数转换为 MCP 工具定义
2. 提取函数签名和文档字符串作为工具描述
3. 通过 stdio 暴露工具列表和调用接口

### 3. AI 如何发现可用工具

当 MCP 服务器启动后，AI 模型可以通过以下方式发现工具：

#### 步骤 1：初始化连接
```
AI → WebSocket → app.py → tool_server.py
```

#### 步骤 2：请求工具列表
AI 发送 MCP 协议请求：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

#### 步骤 3：接收工具列表
工具服务器返回可用工具：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "query_stock",
        "description": "查询股票信息。输入股票代码（如 AAPL, GOOGL, MSFT 等）...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "symbol": {
              "type": "string",
              "description": "股票代码"
            }
          },
          "required": ["symbol"]
        }
      },
      {
        "name": "query_multiple_stocks",
        ...
      },
      {
        "name": "list_available_stocks",
        ...
      }
    ]
  }
}
```

### 4. AI 如何调用工具

#### 步骤 1：AI 决定调用工具
当用户提问："帮我查一下苹果的股价"

AI 分析后决定调用 `query_stock` 工具，参数为 `{"symbol": "AAPL"}`

#### 步骤 2：发送工具调用请求
AI 通过 WebSocket 发送：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "query_stock",
    "arguments": {
      "symbol": "AAPL"
    }
  }
}
```

#### 步骤 3：请求流转
```
AI (WebSocket)
  → app.py (接收 WebSocket 消息)
  → 转发到 stdio (写入 stock.py 的 stdin)
  → stock.py (FastMCP 解析请求)
  → 调用 query_stock("AAPL") 函数
  → 执行工具逻辑
  → 返回结果到 stdout
  → app.py (读取 stdout)
  → 转发到 WebSocket
  → AI (接收结果)
```

#### 步骤 4：接收工具结果
工具服务器返回：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"data\": {\"symbol\": \"AAPL\", \"name\": \"Apple Inc.\", \"price\": 175.50, ...}}"
      }
    ]
  }
}
```

#### 步骤 5：AI 处理结果
AI 接收结果后，解析 JSON 数据，并生成用户友好的回复：
"苹果公司 (AAPL) 的当前股价是 $175.50，上涨了 $2.30 (1.33%)"

## 实际使用场景示例

### 场景 1：用户询问股票价格

**用户**："帮我查一下苹果、谷歌和微软的股价"

**AI 处理流程**：
1. AI 识别需要查询多个股票
2. AI 调用 `query_multiple_stocks` 工具，参数：`{"symbols": "AAPL,GOOGL,MSFT"}`
3. 工具返回三个股票的数据
4. AI 格式化结果并回复用户

### 场景 2：用户需要计算

**用户**："帮我算一下 123 * 456 + 789"

**AI 处理流程**：
1. AI 识别需要数学计算
2. AI 调用 `calculator` 工具，参数：`{"python_expression": "123 * 456 + 789"}`
3. 工具返回计算结果
4. AI 回复计算结果

## 配置 AI 客户端连接 MCP

### 方式 1：通过 WebSocket 端点

AI 客户端需要配置连接到你的 MCP 代理服务器：

```javascript
// 示例：JavaScript/TypeScript 客户端
const ws = new WebSocket('ws://your-mcp-endpoint/mcp');

ws.on('open', () => {
  // 请求工具列表
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list"
  }));
});

ws.on('message', (data) => {
  const response = JSON.parse(data);
  // 处理工具列表或工具调用结果
});
```

### 方式 2：使用 MCP SDK

许多 AI 平台提供了 MCP SDK，简化连接过程：

```python
# 示例：Python MCP 客户端
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # 初始化会话
        await session.initialize()
        
        # 列出可用工具
        tools = await session.list_tools()
        
        # 调用工具
        result = await session.call_tool("query_stock", {"symbol": "AAPL"})
```

## 关键配置点

### 1. WebSocket 端点配置

在 `.env` 文件中设置：
```bash
MCP_ENDPOINT=ws://your-server:8080/mcp
```

### 2. 工具服务器配置

在 `mcp_config.json` 中配置：
```json
{
  "mcpServers": {
    "local-stdio-stock": {
      "type": "stdio",
      "command": "python",
      "args": ["src/mcp/tools/stock.py"]
    }
  }
}
```

### 3. 启动 MCP 代理服务器

```bash
uv run python src/app.py
```

这会：
- 连接到 WebSocket 端点 (`MCP_ENDPOINT`)
- 启动所有配置的工具服务器
- 建立双向通信管道

## 工具调用的 JSON-RPC 格式

MCP 使用 JSON-RPC 2.0 协议：

### 请求格式
```json
{
  "jsonrpc": "2.0",
  "id": <unique_id>,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": {
      "<param_name>": "<param_value>"
    }
  }
}
```

### 响应格式
```json
{
  "jsonrpc": "2.0",
  "id": <same_id>,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "<tool_result_json>"
      }
    ]
  }
}
```

## 调试和监控

### 查看日志

工具服务器会输出日志：
```bash
# 查看工具调用日志
tail -f logs/app.log
```

### 测试工具调用

可以使用 MCP 客户端工具测试：
```bash
# 使用 mcp-cli 测试
mcp-cli call query_stock --symbol AAPL
```

## 常见问题

### Q: AI 如何知道什么时候调用工具？
A: AI 模型会根据用户的问题和可用工具的描述，自动决定是否需要调用工具。工具的描述（docstring）非常重要，应该清晰说明工具的用途。

### Q: 可以同时调用多个工具吗？
A: 可以，AI 可以并行调用多个工具，或者顺序调用多个工具来完成复杂任务。

### Q: 工具调用失败怎么办？
A: MCP 协议会返回错误响应，AI 可以根据错误信息决定重试或使用其他方法。

### Q: 如何添加新工具？
A: 在工具服务器文件中使用 `@mcp.tool()` 装饰器添加新函数，重启服务器后 AI 就能看到新工具。

## 总结

AI 触发 MCP 工具的完整流程：

1. **连接建立**：AI 通过 WebSocket 连接到 MCP 代理服务器
2. **工具发现**：AI 请求并接收可用工具列表
3. **工具选择**：AI 根据用户需求选择合适的工具
4. **工具调用**：AI 发送工具调用请求（JSON-RPC 格式）
5. **请求转发**：MCP 代理服务器将请求转发给工具服务器
6. **工具执行**：工具服务器执行函数并返回结果
7. **结果返回**：结果通过相同路径返回给 AI
8. **结果处理**：AI 解析结果并生成用户友好的回复

整个过程对用户是透明的，用户只需要正常与 AI 对话，AI 会自动在需要时调用相应的工具。
