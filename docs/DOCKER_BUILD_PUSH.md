# Docker Build & Push Guide

本文档介绍如何构建和推送 xiaozhi-mcp 的 Docker 镜像。

## 前置要求

- 已安装 Docker（版本 20.10+）
- 已登录到目标镜像仓库（Docker Hub、私有仓库等）

## 快速开始 - 推送到阿里云容器镜像服务

### 镜像地址格式

阿里云容器镜像服务的镜像地址格式为：
```
<registry>/<namespace>/<image-name>
```

**示例：**
```
crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp
```

### 快速构建和推送

```bash
# 1. 登录阿里云容器镜像服务
docker login <your-registry>.cn-shanghai.personal.cr.aliyuncs.com

# 2. 构建镜像（替换 1.0.0 为实际版本号，从项目根目录）
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .

# 3. 标记镜像（替换为你的实际地址）
docker tag xiaozhi-mcp:latest <your-registry>/<namespace>/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 <your-registry>/<namespace>/xiaozhi-mcp:1.0.0

# 4. 推送镜像
docker push <your-registry>/<namespace>/xiaozhi-mcp:latest
docker push <your-registry>/<namespace>/xiaozhi-mcp:1.0.0
```

**示例：**
```bash
# 示例：使用实际的镜像地址
docker login crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com
docker tag xiaozhi-mcp:latest crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:1.0.0
docker push crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:latest
docker push crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:1.0.0
```

### 使用脚本（推荐）

使用提供的 `docker/build-and-push.sh` 脚本（脚本中已配置实际地址）：

```bash
# 从项目根目录运行
./docker/build-and-push.sh 1.0.0
```

详细说明请参考 [推送到阿里云容器镜像服务](#推送到阿里云容器镜像服务acr) 章节。

## 基本构建

### 构建镜像

在项目根目录执行：

```bash
docker build -f docker/Dockerfile -t xiaozhi-mcp .
```

### 指定标签构建

```bash
# 使用版本号标签
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 .

# 使用 latest 标签
docker build -f docker/Dockerfile -t xiaozhi-mcp:latest .

# 同时指定多个标签
docker build -f docker/Dockerfile -t xiaozhi-mcp:1.0.0 -t xiaozhi-mcp:latest .
```

## 推送到 Docker Hub

### 1. 登录 Docker Hub

```bash
docker login
```

输入你的 Docker Hub 用户名和密码。

### 2. 标记镜像

推送前需要将镜像标记为 Docker Hub 格式：

```bash
# 格式：docker tag <本地镜像名> <Docker Hub用户名>/<镜像名>:<标签>
docker tag xiaozhi-mcp:latest shagua/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:1.0.0 shagua/xiaozhi-mcp:1.0.0
```

### 3. 推送镜像

```bash
# 推送单个标签
docker push shagua/xiaozhi-mcp:latest

# 推送多个标签
docker push shagua/xiaozhi-mcp:latest
docker push shagua/xiaozhi-mcp:1.0.0

# 或者推送所有标签
docker push shagua/xiaozhi-mcp --all-tags
```

## 推送到阿里云容器镜像服务（ACR）

### 1. 登录阿里云容器镜像服务

```bash
# 登录到阿里云容器镜像服务（替换为你的实际注册表地址）
docker login --username=<你的阿里云用户名> <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
```

或者使用访问凭证（推荐）：

```bash
# 使用访问凭证登录（更安全）
docker login <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
```

输入你的阿里云用户名和密码（或访问凭证）。

**示例：**
```bash
docker login crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com
```

### 2. 构建并标记镜像

```bash
# 构建镜像（带版本号，从项目根目录）
VERSION="1.0.0"
docker build -f docker/Dockerfile -t xiaozhi-mcp:${VERSION} -t xiaozhi-mcp:latest .

# 标记为阿里云镜像地址（替换为你的实际地址）
docker tag xiaozhi-mcp:latest <your-registry>/<namespace>/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:${VERSION} <your-registry>/<namespace>/xiaozhi-mcp:${VERSION}
```

**示例：**
```bash
VERSION="1.0.0"
docker build -t xiaozhi-mcp:${VERSION} -t xiaozhi-mcp:latest .
docker tag xiaozhi-mcp:latest crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:latest
docker tag xiaozhi-mcp:${VERSION} crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:${VERSION}
```

### 3. 推送镜像

```bash
# 推送 latest 标签
docker push <your-registry>/<namespace>/xiaozhi-mcp:latest

# 推送版本标签
docker push <your-registry>/<namespace>/xiaozhi-mcp:${VERSION}
```

**示例：**
```bash
docker push crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:latest
docker push crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:1.0.0
```

### 一键构建和推送脚本

项目提供了 `build-and-push.sh` 脚本（已配置实际地址），你也可以根据需要进行修改：

```bash
#!/bin/bash

# 配置变量（根据你的实际情况修改）
VERSION="${1:-latest}"
REGISTRY="<your-registry>.cn-shanghai.personal.cr.aliyuncs.com"
NAMESPACE="<your-namespace>"
IMAGE_NAME="xiaozhi-mcp"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

# 检查版本号
if [ "$VERSION" = "latest" ]; then
    echo "Warning: Using 'latest' as version. Consider using semantic versioning (e.g., 1.0.0)"
fi

# 构建镜像（从项目根目录）
echo "Building image ${IMAGE_NAME}:${VERSION}..."
docker build -f docker/Dockerfile -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

# 标记镜像
echo "Tagging image..."
docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}:latest
if [ "$VERSION" != "latest" ]; then
    docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}:${VERSION}
fi

# 推送镜像
echo "Pushing image to ${FULL_IMAGE_NAME}..."
docker push ${FULL_IMAGE_NAME}:latest
if [ "$VERSION" != "latest" ]; then
    docker push ${FULL_IMAGE_NAME}:${VERSION}
fi

echo "Done! Image pushed to ${FULL_IMAGE_NAME}"
echo "  - ${FULL_IMAGE_NAME}:latest"
if [ "$VERSION" != "latest" ]; then
    echo "  - ${FULL_IMAGE_NAME}:${VERSION}"
fi
```

使用方法：

```bash
# 从项目根目录运行
# 推送 latest 和指定版本
./docker/build-and-push.sh 1.0.0

# 只推送 dev 和日期版本（使用默认值）
./docker/build-and-push.sh
```

**注意：** 
- 脚本位于 `docker/build-and-push.sh`
- 脚本会自动使用 `docker/Dockerfile` 和 `docker/.env`
- 配置文件位于 `docker/.env`（不会被提交到 git）
- 示例配置文件位于 `docker/.env.example`

## 推送到私有仓库

### 1. 登录私有仓库

```bash
# 格式：docker login <仓库地址>
docker login registry.example.com
```

### 2. 标记镜像

```bash
docker tag xiaozhi-mcp:latest registry.example.com/xiaozhi-mcp:latest
```

### 3. 推送镜像

```bash
docker push registry.example.com/xiaozhi-mcp:latest
```

## 使用构建参数

Dockerfile 支持通过构建参数自定义配置：

```bash
# 指定 Python 版本
docker build -f docker/Dockerfile --build-arg PYTHON_VERSION=3.12 -t xiaozhi-mcp .

# 指定工作目录
docker build -f docker/Dockerfile --build-arg WORKDIR=/app -t xiaozhi-mcp .
```

## 多阶段构建优化

如果需要优化镜像大小，可以使用多阶段构建：

```dockerfile
# 构建阶段
FROM python:3.12-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 运行阶段
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY mcp_config.yaml* ./
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
CMD ["uv", "run", "python", "src/app.py"]
```

## 多架构构建（可选）

如果需要支持多架构（如 ARM64、AMD64），可以使用 Docker Buildx：

### 1. 创建并使用 Buildx builder

```bash
# 创建新的 builder
docker buildx create --name multiarch --use

# 查看支持的平台
docker buildx inspect --bootstrap
```

### 2. 构建多架构镜像

**推送到 Docker Hub：**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t shagua/xiaozhi-mcp:latest \
  -t shagua/xiaozhi-mcp:1.0.0 \
  --push .
```

**推送到阿里云容器镜像服务：**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile \
  -t <your-registry>/<namespace>/xiaozhi-mcp:latest \
  -t <your-registry>/<namespace>/xiaozhi-mcp:1.0.0 \
  --push .
```

**示例：**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile \
  -t crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:latest \
  -t crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com/oj8k/xiaozhi-mcp:1.0.0 \
  --push .
```

### 3. 仅构建不推送

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile \
  -t xiaozhi-mcp:latest \
  --load .
```

注意：`--load` 只能加载单个架构，多架构需要使用 `--push`。

## 完整示例脚本

### 通用构建推送脚本

创建一个通用的 `build-and-push.sh` 脚本：

```bash
#!/bin/bash

# 配置变量
IMAGE_NAME="xiaozhi-mcp"
VERSION="${1:-latest}"
DOCKER_USERNAME="${DOCKER_USERNAME:-shagua}"
REGISTRY="${REGISTRY:-docker.io}"  # 或 registry.example.com

# 构建镜像（从项目根目录）
echo "Building image ${IMAGE_NAME}:${VERSION}..."
docker build -f docker/Dockerfile -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

# 标记镜像
echo "Tagging image..."
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:latest ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

# 推送镜像
echo "Pushing image..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

echo "Done!"
```

使用方法：

```bash
chmod +x docker/build-and-push.sh
./docker/build-and-push.sh 1.0.0
```

### 阿里云容器镜像服务专用脚本

项目提供了 `build-and-push.sh` 脚本（已配置实际地址），你也可以根据需要进行修改：

```bash
#!/bin/bash

# 配置变量（根据你的实际情况修改）
VERSION="${1:-latest}"
REGISTRY="<your-registry>.cn-shanghai.personal.cr.aliyuncs.com"
NAMESPACE="<your-namespace>"
IMAGE_NAME="xiaozhi-mcp"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

# 检查版本号
if [ "$VERSION" = "latest" ]; then
    echo "Warning: Using 'latest' as version. Consider using semantic versioning (e.g., 1.0.0)"
fi

# 构建镜像（从项目根目录）
echo "Building image ${IMAGE_NAME}:${VERSION}..."
docker build -f docker/Dockerfile -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

# 标记镜像
echo "Tagging image..."
docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}:latest
if [ "$VERSION" != "latest" ]; then
    docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}:${VERSION}
fi

# 推送镜像
echo "Pushing image to ${FULL_IMAGE_NAME}..."
docker push ${FULL_IMAGE_NAME}:latest
if [ "$VERSION" != "latest" ]; then
    docker push ${FULL_IMAGE_NAME}:${VERSION}
fi

echo "Done! Image pushed to ${FULL_IMAGE_NAME}"
echo "  - ${FULL_IMAGE_NAME}:latest"
if [ "$VERSION" != "latest" ]; then
    echo "  - ${FULL_IMAGE_NAME}:${VERSION}"
fi
```

使用方法：

```bash
# 从项目根目录运行
# 推送 dev、日期版本和指定版本
./docker/build-and-push.sh 1.0.0

# 只推送 dev 和日期版本（使用默认值）
./docker/build-and-push.sh
```

## CI/CD 集成

### GitHub Actions 示例

创建 `.github/workflows/docker-build-push.yml`：

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/xiaozhi-mcp:${{ steps.version.outputs.version }}
            ${{ secrets.DOCKER_USERNAME }}/xiaozhi-mcp:latest
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/xiaozhi-mcp:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/xiaozhi-mcp:buildcache,mode=max
```

### GitHub Actions - 推送到阿里云容器镜像服务

创建 `.github/workflows/docker-build-push-acr.yml`：

```yaml
name: Build and Push to Aliyun ACR

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

env:
  REGISTRY: <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
  NAMESPACE: <your-namespace>
  IMAGE_NAME: xiaozhi-mcp

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Aliyun ACR
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ALIYUN_ACR_USERNAME }}
          password: ${{ secrets.ALIYUN_ACR_PASSWORD }}

      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/${{ env.IMAGE_NAME }}:${{ steps.version.outputs.version }}
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/${{ env.IMAGE_NAME }}:latest
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.NAMESPACE }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.NAMESPACE }}/${{ env.IMAGE_NAME }}:buildcache,mode=max
```

**配置 GitHub Secrets：**
- `ALIYUN_ACR_USERNAME`: 阿里云容器镜像服务用户名
- `ALIYUN_ACR_PASSWORD`: 阿里云容器镜像服务密码或访问凭证

**示例配置：**
```yaml
env:
  REGISTRY: crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com
  NAMESPACE: oj8k
  IMAGE_NAME: xiaozhi-mcp
```

### GitLab CI 示例

创建 `.gitlab-ci.yml`：

```yaml
build-and-push:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - tags
```

### GitLab CI - 推送到阿里云容器镜像服务

创建 `.gitlab-ci.yml`：

```yaml
variables:
  REGISTRY: <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
  NAMESPACE: <your-namespace>
  IMAGE_NAME: xiaozhi-mcp
  FULL_IMAGE_NAME: ${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}

build-and-push:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $ALIYUN_ACR_USERNAME -p $ALIYUN_ACR_PASSWORD $REGISTRY
  script:
    - |
      VERSION=${CI_COMMIT_TAG:-latest}
      docker build -t ${FULL_IMAGE_NAME}:${VERSION} -t ${FULL_IMAGE_NAME}:latest .
      docker push ${FULL_IMAGE_NAME}:latest
      if [ "$VERSION" != "latest" ]; then
        docker push ${FULL_IMAGE_NAME}:${VERSION}
      fi
  only:
    - tags
  when: manual
```

**配置 GitLab CI/CD Variables：**
- `ALIYUN_ACR_USERNAME`: 阿里云容器镜像服务用户名
- `ALIYUN_ACR_PASSWORD`: 阿里云容器镜像服务密码或访问凭证

**示例配置：**
```yaml
variables:
  REGISTRY: crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com
  NAMESPACE: oj8k
  IMAGE_NAME: xiaozhi-mcp
```

## 验证镜像

构建完成后，可以验证镜像：

```bash
# 查看镜像信息
docker inspect xiaozhi-mcp:latest

# 查看镜像历史
docker history xiaozhi-mcp:latest

# 测试运行
docker run --rm xiaozhi-mcp:latest

# 进入容器检查
docker run -it --rm xiaozhi-mcp:latest /bin/bash
```

## 最佳实践

1. **使用语义化版本号**：遵循 [Semantic Versioning](https://semver.org/)
2. **始终推送 latest 标签**：方便用户快速获取最新版本
3. **使用多阶段构建**：减小最终镜像大小
4. **利用构建缓存**：合理组织 Dockerfile 顺序，提高构建速度
5. **扫描安全漏洞**：使用 `docker scan` 或第三方工具检查镜像安全
6. **添加镜像描述**：使用 Dockerfile LABEL 添加元数据

```dockerfile
LABEL maintainer="your-email@example.com"
LABEL description="xiaozhi-mcp MCP Server"
LABEL version="1.0.0"
```

## 故障排查

### 构建失败

```bash
# 查看详细构建日志
docker build -f docker/Dockerfile --progress=plain -t xiaozhi-mcp .

# 不使用缓存重新构建
docker build -f docker/Dockerfile --no-cache -t xiaozhi-mcp .
```

### 推送失败

**常见错误：`denied: requested access to the resource is denied`**

这个错误通常表示权限问题，可能的原因：

1. **未登录到镜像仓库**
   ```bash
   # 检查登录状态
   docker info | grep Username
   
   # 登录到阿里云容器镜像服务
   docker login <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
   ```

2. **登录凭证错误或过期**
   ```bash
   # 登出后重新登录
   docker logout <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
   docker login <your-registry>.cn-shanghai.personal.cr.aliyuncs.com
   ```

3. **没有权限访问指定的命名空间**
   - 确认你有权限推送到 `<namespace>` 命名空间
   - 检查阿里云容器镜像服务中的命名空间权限设置
   - 确认你使用的账号有推送权限

4. **镜像地址格式错误**
   - 确认镜像地址格式正确：`<registry>/<namespace>/<image-name>:<tag>`
   - 检查命名空间名称是否正确

**调试步骤：**
```bash
# 1. 检查 Docker 登录状态
cat ~/.docker/config.json | grep -A 5 "<your-registry>"

# 2. 测试登录
docker login <your-registry>.cn-shanghai.personal.cr.aliyuncs.com

# 3. 尝试拉取镜像（测试权限）
docker pull <your-registry>/<namespace>/xiaozhi-mcp:latest

# 4. 查看详细错误信息
docker push <your-registry>/<namespace>/xiaozhi-mcp:latest 2>&1
```

### 权限问题

**阿里云容器镜像服务权限检查：**

1. **确认登录状态**
   ```bash
   # 检查是否已登录
   docker info | grep Username
   
   # 或查看配置文件
   cat ~/.docker/config.json
   ```

2. **使用正确的认证方式**
   - 使用阿里云账号密码登录
   - 或使用访问凭证（推荐，更安全）
   - 访问凭证在阿里云控制台的"访问凭证"页面生成

3. **检查命名空间权限**
   - 登录阿里云容器镜像服务控制台
   - 确认命名空间存在且你有推送权限
   - 如果是个人版，命名空间通常是你的用户名

4. **Docker daemon 权限**
   ```bash
   # 确保当前用户有权限访问 Docker daemon
   docker ps  # 如果失败，可能需要 sudo 或添加用户到 docker 组
   ```

**示例 - 完整的登录和推送流程：**
```bash
# 1. 登录（使用访问凭证）
docker login crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com
# 输入用户名和访问凭证密码

# 2. 验证登录
docker info | grep Username

# 3. 构建和推送
./build-and-push.sh 1.0.0
```

## 相关文档

- [Deployment Guide](./DEPLOYMENT.md) - 部署指南
- [Configuration Guide](./CONFIG.md) - 配置指南
