#!/bin/bash

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# 加载 .env 文件（如果存在）
ENV_FILE="${SCRIPT_DIR}/.env"
if [ -f "${ENV_FILE}" ]; then
    echo "Loading configuration from ${ENV_FILE}..."
    # 读取 .env 文件，忽略注释和空行，并导出变量
    set -a
    while IFS= read -r line || [ -n "$line" ]; do
        # 跳过注释和空行
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        # 导出变量
        export "$line" 2>/dev/null || true
    done < "${ENV_FILE}"
    set +a
fi

# 配置变量（优先级：命令行参数 > 环境变量 > .env文件 > 默认值）
VERSION="${1:-${DOCKER_VERSION:-dev}}"
PUSH_LATEST="${2:-${DOCKER_PUSH_LATEST:-false}}"
REGISTRY="${DOCKER_REGISTRY:-crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com}"
NAMESPACE="${DOCKER_NAMESPACE:-oj8k}"
IMAGE_NAME="${DOCKER_IMAGE_NAME:-xiaozhi-mcp}"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

# 显示使用的配置
echo "Configuration:"
echo "  REGISTRY: ${REGISTRY}"
echo "  NAMESPACE: ${NAMESPACE}"
echo "  IMAGE_NAME: ${IMAGE_NAME}"
echo "  VERSION: ${VERSION}"
echo ""

# 生成日期版本号 (yyMMdd格式)
DATE_VERSION="0.0.$(date +%y%m%d)"

# 构建标签列表
TAGS=("${VERSION}" "${DATE_VERSION}")

# 如果版本不是dev，添加dev标签
if [ "$VERSION" != "dev" ]; then
    TAGS+=("dev")
fi

# 如果指定推送latest，添加到标签列表
if [ "$PUSH_LATEST" = "latest" ] || [ "$PUSH_LATEST" = "true" ]; then
    TAGS+=("latest")
    echo "Will push with latest tag"
fi

echo "Will push with tags: ${TAGS[*]}"

# 检查是否已登录到目标 registry
echo "Checking Docker login status for ${REGISTRY}..."
DOCKER_CONFIG="${HOME}/.docker/config.json"
LOGGED_IN=0

if [ -f "${DOCKER_CONFIG}" ]; then
    # 检查配置文件中是否包含目标 registry 的认证信息
    if grep -q "${REGISTRY}" "${DOCKER_CONFIG}" 2>/dev/null; then
        echo "✓ Found login credentials for ${REGISTRY}"
        LOGGED_IN=1
    fi
fi

if [ $LOGGED_IN -eq 0 ]; then
    echo "Warning: No login credentials found for ${REGISTRY}"
    echo "Please login first:"
    echo "  docker login ${REGISTRY}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 构建镜像（使用第一个标签作为主标签）
MAIN_TAG="${TAGS[0]}"
echo "Building image ${IMAGE_NAME}:${MAIN_TAG}..."
echo "Build context: ${PROJECT_ROOT}"
echo "Dockerfile: ${SCRIPT_DIR}/Dockerfile"
set -e  # 从构建开始启用错误退出
docker build -f "${SCRIPT_DIR}/Dockerfile" -t ${IMAGE_NAME}:${MAIN_TAG} "${PROJECT_ROOT}"
set +e  # 暂时关闭错误退出，以便更好地处理推送错误

# 标记镜像（为所有标签创建标记）
echo "Tagging images..."
for tag in "${TAGS[@]}"; do
    docker tag ${IMAGE_NAME}:${MAIN_TAG} ${FULL_IMAGE_NAME}:${tag}
done

# 推送镜像
echo "Pushing images to ${FULL_IMAGE_NAME}..."
PUSH_FAILED=0
PUSHED_TAGS=()

for tag in "${TAGS[@]}"; do
    if docker push ${FULL_IMAGE_NAME}:${tag}; then
        PUSHED_TAGS+=("${tag}")
        echo "✓ Successfully pushed ${FULL_IMAGE_NAME}:${tag}"
    else
        echo "✗ Failed to push ${FULL_IMAGE_NAME}:${tag}"
        PUSH_FAILED=1
    fi
done

if [ $PUSH_FAILED -eq 1 ]; then
    echo ""
    echo "Some pushes failed. Common issues:"
    echo "  1. Not logged in: docker login ${REGISTRY}"
    echo "  2. No permission to push to namespace '${NAMESPACE}'"
    echo "  3. Invalid credentials"
    echo ""
    echo "Please check your login status and permissions."
    exit 1
fi

echo ""
echo "Done! Successfully pushed images:"
for tag in "${PUSHED_TAGS[@]}"; do
    echo "  - ${FULL_IMAGE_NAME}:${tag}"
done
