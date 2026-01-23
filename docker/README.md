# Docker 相关文件

本目录包含所有 Docker 相关的配置文件。

## 文件说明

- **`Dockerfile`** - Docker 镜像构建文件
- **`Dockerfile.acr`** - Docker 镜像构建文件（使用国内镜像源，适用于 Docker Hub 访问受限的情况）
- **`docker-compose.example.yml`** - Docker Compose 配置示例
- **`build-and-push.sh`** - 构建和推送脚本（默认配置为 ACR，可通过环境变量配置为任意容器镜像服务）
- **`.env.example`** - Docker 环境变量配置示例
- **`.env`** - Docker 环境变量配置文件（不会被提交到 git）
- **`.dockerignore`** - Docker 构建时忽略的文件列表
- **`.github/workflows/docker-build-push.yml`** - GitHub Actions 工作流（自动构建和推送 Docker 镜像）

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

### 3. 使用 GitHub Actions（推荐）

GitHub Actions 会自动构建和推送 Docker 镜像，支持多架构（amd64/arm64）和多个容器镜像服务。

#### 3.1 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**GitHub Container Registry (GHCR):**
- **无需配置！** GHCR 默认启用，使用 `GITHUB_TOKEN` 自动认证
- 镜像地址格式：`ghcr.io/<owner>/xiaozhi-mcp`
- 如果需要使用 Personal Access Token（可选），可以添加 `GHCR_TOKEN`

**Docker Hub:**
- `DOCKERHUB_USERNAME` - Docker Hub 用户名
- `DOCKERHUB_TOKEN` - Docker Hub 访问令牌

**阿里云 ACR:**
- `ACR_REGISTRY` - ACR registry 地址（可选，有默认值）
- `ACR_NAMESPACE` - ACR 命名空间（可选，有默认值）
- `ACR_USERNAME` - ACR 用户名
- `ACR_PASSWORD` - ACR 密码

**Google GCR:**
- `GCR_PROJECT_ID` - GCP 项目 ID
- `GCR_SERVICE_ACCOUNT_KEY` - GCP 服务账号 JSON 密钥

**AWS ECR:**
- `ECR_REGISTRY` - ECR registry 地址
- `AWS_ACCESS_KEY_ID` - AWS 访问密钥 ID
- `AWS_SECRET_ACCESS_KEY` - AWS 密钥

#### 3.2 触发构建

**自动触发：**
- 推送到 `main` 或 `dev` 分支 → 构建并推送 `dev` 和日期版本标签
- 推送版本标签（如 `v1.0.0`）→ 构建并推送版本号、`dev`、日期版本和 `latest` 标签

**手动触发：**
1. 进入 GitHub Actions 页面
2. 选择 "Build and Push Docker Image" 工作流
3. 点击 "Run workflow"
4. 选择版本号和是否推送 `latest` 标签

#### 3.3 工作流特性

- ✅ 多架构构建（linux/amd64, linux/arm64）
- ✅ 支持多个容器镜像服务（GitHub Container Registry (GHCR)、Docker Hub、ACR、GCR、ECR）
- ✅ GHCR 默认启用，无需配置
- ✅ 自动版本标签管理
- ✅ 构建缓存加速
- ✅ PR 时只构建不推送

### 4. 使用构建脚本

从项目根目录运行：

```bash
# 构建并推送（推送 dev、日期版本和指定版本）
./docker/build-and-push.sh 1.0.0

# 只推送 dev 和日期版本
./docker/build-and-push.sh

# 推送时包含 latest 标签
./docker/build-and-push.sh 1.0.0 latest
```

### 5. 纯手工构建和推送

如果你不想使用脚本，也可以手动执行构建和推送步骤：

#### 4.1 登录到容器镜像服务

```bash
# 登录到容器镜像服务（替换为你的 registry 地址）
# Docker Hub 示例：
docker login

# 阿里云容器镜像服务 (ACR) 示例：
docker login crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com

# Google Container Registry (GCR) 示例：
docker login gcr.io

# AWS ECR 示例：
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### 4.2 构建镜像

从项目根目录运行：

```bash
# 使用标准 Dockerfile 构建
docker build -f docker/Dockerfile -t xiaozhi-mcp:dev .

# 如果 Docker Hub 访问受限，可以使用 Dockerfile.acr（使用国内镜像源）
docker build -f docker/Dockerfile.acr -t xiaozhi-mcp:dev .
```

#### 4.3 标记镜像

```bash
# 设置变量（根据实际情况修改）
# Docker Hub 示例：
REGISTRY="docker.io"
NAMESPACE="shagua"  # Docker Hub 用户名
IMAGE_NAME="xiaozhi-mcp"
VERSION="dev"  # 或使用具体版本号，如 1.0.0

# 阿里云 ACR 示例：
# REGISTRY="crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com"
# NAMESPACE="oj8k"

# Google GCR 示例：
# REGISTRY="gcr.io"
# NAMESPACE="your-project-id"

# AWS ECR 示例：
# REGISTRY="<account-id>.dkr.ecr.us-east-1.amazonaws.com"
# NAMESPACE=""  # ECR 通常不需要 namespace

FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"
# 注意：如果 NAMESPACE 为空，使用：FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"

# 标记镜像
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:${VERSION}

# 如果需要多个标签，可以继续标记
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:latest
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)  # 日期版本
```

#### 4.4 推送镜像

```bash
# 推送单个标签
docker push ${FULL_IMAGE_NAME}:${VERSION}

# 推送多个标签
docker push ${FULL_IMAGE_NAME}:${VERSION}
docker push ${FULL_IMAGE_NAME}:latest
docker push ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)
```

#### 4.5 完整示例

**Docker Hub 示例：**

```bash
# 1. 登录
docker login

# 2. 构建
docker build -f docker/Dockerfile -t xiaozhi-mcp:dev .

# 3. 标记
REGISTRY="docker.io"
NAMESPACE="shagua"  # Docker Hub 用户名
IMAGE_NAME="xiaozhi-mcp"
VERSION="1.0.0"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:${VERSION}
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:dev
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)

# 4. 推送
docker push ${FULL_IMAGE_NAME}:${VERSION}
docker push ${FULL_IMAGE_NAME}:dev
docker push ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)
```

**阿里云 ACR 示例：**

```bash
# 1. 登录
docker login crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com

# 2. 构建（如果 Docker Hub 访问受限，使用 Dockerfile.acr）
docker build -f docker/Dockerfile.acr -t xiaozhi-mcp:dev .

# 3. 标记
REGISTRY="crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com"
NAMESPACE="oj8k"
IMAGE_NAME="xiaozhi-mcp"
VERSION="1.0.0"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:${VERSION}
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:dev
docker tag xiaozhi-mcp:dev ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)

# 4. 推送
docker push ${FULL_IMAGE_NAME}:${VERSION}
docker push ${FULL_IMAGE_NAME}:dev
docker push ${FULL_IMAGE_NAME}:0.0.$(date +%y%m%d)
```

### 6. 使用 Docker Compose

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

## 故障排除

### Docker Hub 访问问题

如果遇到 `Get "https://registry-1.docker.io/v2/": EOF` 错误，说明无法访问 Docker Hub。

**解决方案 1：配置 Docker 镜像加速器（推荐）**

对于 OrbStack/Docker Desktop，可以在设置中配置镜像加速器：
- 阿里云：`https://your-id.mirror.aliyuncs.com`
- 腾讯云：`https://mirror.ccs.tencentyun.com`
- 网易：`https://hub-mirror.c.163.com`

**解决方案 2：手动拉取基础镜像**

如果已配置镜像加速器，可以直接拉取：

```bash
# 拉取基础镜像（会自动使用配置的镜像加速器）
docker pull python:3.12-slim

# 然后再构建
docker build -f docker/Dockerfile -t xiaozhi-mcp .
```

**解决方案 2.1：使用 Dockerfile.acr（已配置为使用标准镜像）**

`Dockerfile.acr` 使用标准的 `python:3.12-slim` 镜像，需要先配置镜像加速器：

```bash
# 确保已配置镜像加速器后，使用 Dockerfile.acr 构建
docker build -f docker/Dockerfile.acr -t xiaozhi-mcp .
```

**解决方案 3：使用代理**

如果已配置代理，确保 Docker 可以使用代理：
```bash
# 设置代理环境变量
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
docker build -f docker/Dockerfile -t xiaozhi-mcp .
```

## 详细文档

更多信息请参考：
- [Docker Build & Push Guide](../docs/DOCKER_BUILD_PUSH.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
