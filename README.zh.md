# xiaozhi-mcp

一个强大的接口，用于通过远程控制、计算、邮件操作、知识搜索等方式扩展AI能力。

## About

MCP（模型上下文协议）是一个允许服务器向语言模型暴露可调用工具的协议。本项目提供了一个灵活的框架，用于创建和管理MCP工具，支持多种传输类型（stdio、SSE、HTTP），并实现AI模型与外部系统之间的无缝集成。

**主要特性：**
- 🔌 AI与外部工具之间的双向通信
- 🔄 具有指数退避的自动重连机制
- 📊 实时数据流传输
- 🛠️ 简单易用的工具创建接口
- 🔒 安全的WebSocket通信
- ⚙️ 支持多种传输类型（stdio/sse/http）

## How to Install

### 使用 uv（推荐）

1. 安装 uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 安装依赖:
```bash
uv sync
```

### 使用 pip

1. 安装依赖:
```bash
pip install -r requirements.txt
```

**环境要求：**
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

### 运行所有配置的服务

从配置文件启动所有启用的服务：

```bash
# 使用 uv
uv run python src/app.py

# 使用 pip
python src/app.py
```

### 运行单个服务脚本

直接运行特定的服务脚本：

```bash
# 使用 uv
uv run python src/app.py src/mcp/tools/calculator.py

# 使用 pip
python src/app.py src/mcp/tools/calculator.py
```

### 使用 Docker 运行

#### 使用 Docker Compose（推荐）

```bash
# 复制示例 docker-compose 文件
cp docker/docker-compose.example.yml docker-compose.yml

# 启动服务（从项目根目录）
docker-compose -f docker-compose.yml up -d

# 查看日志
docker-compose -f docker-compose.yml logs -f

# 停止服务
docker-compose -f docker-compose.yml down
```

#### 直接使用 Docker

```bash
# 构建镜像（从项目根目录）
docker build -f docker/Dockerfile -t xiaozhi-mcp .

# 运行容器
docker run -d --name xiaozhi-mcp \
  -v $(pwd)/mcp_config.yaml:/app/mcp_config.yaml:ro \
  xiaozhi-mcp
```

#### 构建和推送 Docker 镜像

**构建并推送到镜像仓库：**

```bash
# 构建带版本标签的镜像（从项目根目录）
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .

# 标记为仓库地址（替换为你的实际地址）
docker tag xiaozhi-mcp:latest <registry>/<namespace>/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 <registry>/<namespace>/xiaozhi-mcp:1.0.0

# 推送到仓库
docker push <registry>/<namespace>/xiaozhi-mcp:latest
docker push <registry>/<namespace>/xiaozhi-mcp:1.0.0
```

**示例 - 阿里云容器镜像服务：**
```bash
# 示例仓库地址格式
REGISTRY="<your-registry>.cn-shanghai.personal.cr.aliyuncs.com"
NAMESPACE="<your-namespace>"

# 构建和标记（从项目根目录）
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .
docker tag xiaozhi-mcp:latest ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:1.0.0

# 推送
docker push ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:latest
docker push ${REGISTRY}/${NAMESPACE}/xiaozhi-mcp:1.0.0
```

**使用提供的脚本：**
```bash
# 使用 build-and-push-acr.sh 脚本（从项目根目录）
# 脚本会自动使用 docker/Dockerfile 和 docker/.env
./docker/build-and-push-acr.sh 1.0.0
```

更多 Docker 构建和推送选项，请参阅 [docs/DOCKER_BUILD_PUSH.md](docs/DOCKER_BUILD_PUSH.md)。

更多 Docker 部署选项，请参阅 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## Configs

配置文件采用 YAML 格式：

- `mcp_config.yaml` - 主配置文件

### 配置结构

编辑 `mcp_config.yaml` 来配置你的 MCP 端点和服务器：

```yaml
mcp:
  endpoint: ws://your-endpoint-url/mcp
  token: your-token-here  # 可选
  
  servers:
    local-stdio-calculator:
      enabled: true
      type: stdio
      command: python
      args:
        - src/mcp/tools/calculator.py
```

详细的配置示例，请参阅 [docs/CONFIG.md](docs/CONFIG.md)。

### 配置加载优先级

1. `MCP_CONFIG` 环境变量（如果设置，直接使用，向后兼容）
2. `mcp_config.yaml`（默认配置文件）
3. `mcp_config.json`（回退选项，向后兼容）

## Thanks To

- 感谢所有帮助塑造这个项目的贡献者
- 灵感来源于对可扩展AI能力的需求
- 基于 MCP（模型上下文协议）规范构建

## License

本项目采用MIT许可证 - 详情请查看LICENSE文件。
