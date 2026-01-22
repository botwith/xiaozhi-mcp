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
PLATFORM="${DOCKER_PLATFORM:-linux/amd64,linux/arm64}"  # 支持多架构构建，默认构建 AMD64 和 ARM64
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
echo "  PLATFORM: ${PLATFORM}"
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

# 检查是否使用多架构构建
if [[ "${PLATFORM}" == *,* ]]; then
    # 多架构构建需要使用 buildx
    echo "Building multi-arch image for platforms: ${PLATFORM}"
    echo "Build context: ${PROJECT_ROOT}"
    echo "Dockerfile: ${SCRIPT_DIR}/Dockerfile"
    
    # 检查 buildx 是否可用
    if ! docker buildx version >/dev/null 2>&1; then
        echo "Error: docker buildx is not available. Please install Docker Buildx."
        echo "Falling back to single-arch build for first platform: $(echo ${PLATFORM} | cut -d',' -f1)"
        PLATFORM=$(echo ${PLATFORM} | cut -d',' -f1)
    else
        # 尝试使用现有的 builder 或默认 builder
        CURRENT_BUILDER=$(docker buildx inspect --bootstrap 2>/dev/null | head -1 | awk '{print $1}' || echo "")
        
        if [ -z "${CURRENT_BUILDER}" ] || [ "${CURRENT_BUILDER}" = "default" ]; then
            # 检查是否有 multiarch builder
            if docker buildx ls 2>/dev/null | grep -q "multiarch"; then
                echo "Using existing multiarch builder..."
                docker buildx use multiarch 2>/dev/null || true
            else
                # 尝试创建新的 builder，如果失败则使用默认 builder
                echo "Setting up buildx builder..."
                if ! docker buildx create --name multiarch --driver docker-container --use 2>/dev/null; then
                    echo "Warning: Failed to create buildx builder. Trying to use default builder..."
                    docker buildx use default 2>/dev/null || true
                fi
            fi
        fi
        
        # 验证 builder 是否可用
        if ! docker buildx inspect --bootstrap >/dev/null 2>&1; then
            echo "Warning: Buildx builder setup failed. Falling back to single-arch build."
            PLATFORM=$(echo ${PLATFORM} | cut -d',' -f1)
        fi
    fi
fi

# 如果仍然是多架构，使用 buildx
if [[ "${PLATFORM}" == *,* ]]; then
    # 使用 buildx 构建并推送多架构镜像
    set -e
    MAIN_TAG="${TAGS[0]}"
    BUILDX_CMD="docker buildx build --platform ${PLATFORM} -f ${SCRIPT_DIR}/Dockerfile"
    
    # 为每个标签构建并推送
    PUSH_FAILED=0
    PUSHED_TAGS=()
    
        for tag in "${TAGS[@]}"; do
            echo "Building and pushing ${FULL_IMAGE_NAME}:${tag} for platforms: ${PLATFORM}..."
            if ${BUILDX_CMD} -t ${FULL_IMAGE_NAME}:${tag} --push "${PROJECT_ROOT}"; then
                PUSHED_TAGS+=("${tag}")
                echo "✓ Successfully built and pushed ${FULL_IMAGE_NAME}:${tag}"
            else
                echo "✗ Failed to build/push ${FULL_IMAGE_NAME}:${tag}"
                echo "  This might be due to network issues or buildx setup problems."
                echo "  You can try building for a single platform instead:"
                echo "    DOCKER_PLATFORM=linux/amd64 $0 ${VERSION} ${PUSH_LATEST}"
                PUSH_FAILED=1
            fi
        done
        set +e
else
    # 单架构构建 - 使用传统构建器避免 buildx 权限问题
    MAIN_TAG="${TAGS[0]}"
    echo "Building image ${IMAGE_NAME}:${MAIN_TAG} for platform: ${PLATFORM}..."
    echo "Build context: ${PROJECT_ROOT}"
    echo "Dockerfile: ${SCRIPT_DIR}/Dockerfile"
    set -e  # 从构建开始启用错误退出
    # 使用 DOCKER_BUILDKIT=0 禁用 buildx，使用传统构建器
    DOCKER_BUILDKIT=0 docker build --platform ${PLATFORM} -f "${SCRIPT_DIR}/Dockerfile" -t ${IMAGE_NAME}:${MAIN_TAG} "${PROJECT_ROOT}"
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
fi

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
