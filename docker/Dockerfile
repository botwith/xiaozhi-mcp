# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv (推荐的包管理器)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# 先复制依赖文件，只安装依赖（不安装项目本身）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 复制源代码和 README（构建项目时需要）
COPY README.md ./
COPY src/ ./src/

# 安装项目本身
RUN uv sync --frozen

# 复制配置文件（如果存在）
COPY mcp_config.yaml* ./

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# 默认命令：运行所有配置的服务器
CMD ["uv", "run", "python", "src/app.py"]
