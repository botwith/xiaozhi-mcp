# Docker 相关文件

本目录包含所有 Docker 相关的配置文件。

## 文件说明

- **`Dockerfile`** - Docker 镜像构建文件
- **`docker-compose.example.yml`** - Docker Compose 配置示例
- **`build-and-push-acr.sh`** - 构建和推送脚本（支持阿里云容器镜像服务）
- **`.env.example`** - Docker 环境变量配置示例
- **`.env`** - Docker 环境变量配置文件（不会被提交到 git）
- **`.dockerignore`** - Docker 构建时忽略的文件列表

## 快速开始

### 1. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 根据需要编辑配置
vim .env
```

### 2. 构建镜像

从项目根目录运行：

```bash
docker build -f docker/Dockerfile -t xiaozhi-mcp .
```

### 3. 使用构建脚本

从项目根目录运行：

```bash
# 构建并推送（推送 dev、日期版本和指定版本）
./docker/build-and-push-acr.sh 1.0.0

# 只推送 dev 和日期版本
./docker/build-and-push-acr.sh

# 推送时包含 latest 标签
./docker/build-and-push-acr.sh 1.0.0 latest
```

### 4. 使用 Docker Compose

从项目根目录运行：

```bash
# 复制示例文件
cp docker/docker-compose.example.yml docker-compose.yml

# 启动服务
docker-compose -f docker-compose.yml up -d

# 查看日志
docker-compose -f docker-compose.yml logs -f

# 停止服务
docker-compose -f docker-compose.yml down
```

## 详细文档

更多信息请参考：
- [Docker Build & Push Guide](../docs/DOCKER_BUILD_PUSH.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
