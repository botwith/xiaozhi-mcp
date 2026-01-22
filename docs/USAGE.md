# 股票查询工具使用指南

## 如何唤起股票查询工具

### 方式一：运行所有配置的服务（推荐）

这种方式会同时启动所有配置的工具（计算器、聊天、股票查询）：

```bash
# 使用 uv
uv run python src/app.py

# 或使用 pip
python src/app.py
```

**前提条件：**
1. 确保已设置 `MCP_ENDPOINT` 环境变量（在 `.env` 文件中或直接导出）
2. 确保 `mcp_config.json` 中 `local-stdio-stock` 没有被设置为 `disabled: true`

### 方式二：单独运行股票工具

直接运行股票工具脚本：

```bash
# 使用 uv
uv run python src/app.py src/mcp/tools/stock.py

# 或使用 pip
python src/app.py src/mcp/tools/stock.py
```

### 方式三：通过配置的服务名称运行

如果 `app.py` 支持通过服务名称运行（需要检查代码实现），可以：

```bash
uv run python src/app.py local-stdio-stock
```

## 环境配置

### 1. 设置 MCP_ENDPOINT

创建 `.env` 文件（如果还没有）：

```bash
cp env.example .env
```

编辑 `.env` 文件，设置你的 WebSocket 端点：

```bash
MCP_ENDPOINT=ws://your-endpoint-url/mcp
```

或者直接导出环境变量：

```bash
export MCP_ENDPOINT=ws://your-endpoint-url/mcp
```

### 2. 检查配置文件

确保 `mcp_config.json` 中包含股票工具配置：

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

## 可用的股票查询功能

启动后，股票工具提供以下三个功能：

1. **`query_stock(symbol)`** - 查询单个股票
   - 示例：查询苹果股票 `query_stock("AAPL")`
   - 支持的股票代码：AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA, BABA, TSM, NFLX

2. **`query_multiple_stocks(symbols)`** - 批量查询多个股票
   - 示例：`query_multiple_stocks("AAPL,GOOGL,MSFT")`
   - 多个股票代码用逗号分隔

3. **`list_available_stocks()`** - 列出所有可用的股票代码
   - 返回所有支持的股票代码列表

## 使用示例

### 查询单个股票

```python
# 通过 MCP 协议调用
query_stock("AAPL")
# 返回：{"success": True, "data": {"symbol": "AAPL", "name": "Apple Inc.", "price": 175.50, ...}}
```

### 批量查询股票

```python
query_multiple_stocks("AAPL,GOOGL,MSFT")
# 返回多个股票的信息
```

### 查看可用股票列表

```python
list_available_stocks()
# 返回所有可用的股票代码
```

## 故障排查

### 问题：找不到 MCP_ENDPOINT

**错误信息：** `Please set the MCP_ENDPOINT environment variable`

**解决方法：**
- 检查 `.env` 文件是否存在并包含 `MCP_ENDPOINT`
- 或直接导出环境变量：`export MCP_ENDPOINT=ws://your-endpoint`

### 问题：股票代码未找到

**错误信息：** `未找到股票代码 'XXX'`

**解决方法：**
- 使用 `list_available_stocks()` 查看所有可用的股票代码
- 确保股票代码使用大写字母（如 'AAPL' 而不是 'aapl'）

### 问题：服务启动失败

**检查项：**
1. 确保已安装所有依赖：`uv sync` 或 `pip install -r requirements.txt`
2. 检查 Python 版本是否 >= 3.10
3. 检查 `src/mcp/tools/stock.py` 文件是否存在
4. 查看日志输出获取详细错误信息

## 注意事项

- 当前版本使用的是示例数据，价格会有小幅随机波动
- 如需真实股票数据，需要集成实际的股票 API（如 yfinance）
- 工具通过 stdio 协议与 MCP 服务器通信
- 确保 WebSocket 端点可访问且配置正确
