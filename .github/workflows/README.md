# GitHub Actions 工作流

## Docker 构建和推送工作流

`docker-build-push.yml` 工作流会自动构建和推送 Docker 镜像到多个容器镜像服务。

### 功能特性

- ✅ **多架构支持**：自动构建 `linux/amd64` 和 `linux/arm64` 架构
- ✅ **多 Registry 支持**：同时推送到 GitHub Container Registry (GHCR)、Docker Hub、ACR、GCR、ECR（GHCR 默认启用，其他根据配置的 Secrets）
- ✅ **智能标签管理**：自动生成版本号、日期版本、dev 和 latest 标签
- ✅ **构建缓存**：使用 GitHub Actions 缓存加速构建
- ✅ **安全推送**：PR 时只构建不推送，保护主分支

### 触发条件

1. **自动触发**：
   - 推送到 `main` 或 `dev` 分支 → 构建并推送 `dev` 和日期版本标签
   - 推送版本标签（如 `v1.0.0`）→ 构建并推送版本号、`dev`、日期版本和 `latest` 标签

2. **手动触发**：
   - 在 GitHub Actions 页面选择工作流
   - 点击 "Run workflow"
   - 选择版本号和是否推送 `latest` 标签

### 配置 Secrets

在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加以下 Secrets：

#### GitHub Container Registry (GHCR)

**无需配置！** GHCR 默认启用，使用 `GITHUB_TOKEN` 自动认证。

镜像地址格式：`ghcr.io/<owner>/xiaozhi-mcp`

如果需要使用 Personal Access Token（可选），可以添加：
```
GHCR_TOKEN=your-personal-access-token
```

#### Docker Hub

```
DOCKERHUB_USERNAME=shagua
DOCKERHUB_TOKEN=your-token
```

默认仓库：`docker.io/shagua/xiaozhi-mcp`

获取 Token：https://hub.docker.com/settings/security

#### 阿里云 ACR

```
ACR_REGISTRY=crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com  # 可选，有默认值
ACR_NAMESPACE=oj8k  # 可选，有默认值
ACR_USERNAME=your-username
ACR_PASSWORD=your-password
```

#### Google GCR

```
GCR_PROJECT_ID=your-project-id
GCR_SERVICE_ACCOUNT_KEY=your-service-account-json-key
```

#### AWS ECR

```
ECR_REGISTRY=your-account.dkr.ecr.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

### 标签规则

- **版本标签**：从 Git 标签或手动输入获取（如 `1.0.0`）
- **日期标签**：自动生成（格式：`0.0.yyMMdd`，如 `0.0.241215`）
- **dev 标签**：当版本不是 `dev` 时自动添加
- **latest 标签**：仅在推送版本标签或手动选择时添加

### 示例

#### 推送版本标签

```bash
git tag v1.0.0
git push origin v1.0.0
```

工作流会自动：
- 构建多架构镜像
- 推送到所有配置的 registry
- 打标签：`1.0.0`、`0.0.241215`、`dev`、`latest`

#### 推送到主分支

```bash
git push origin main
```

工作流会自动：
- 构建多架构镜像
- 推送到所有配置的 registry
- 打标签：`dev`、`0.0.241215`

### 故障排除

1. **构建失败**：检查 Dockerfile 和构建上下文
2. **推送失败**：检查 Secrets 配置和权限
3. **标签错误**：检查版本号格式和标签规则

更多信息请参考 [Docker README](../docker/README.md)。
