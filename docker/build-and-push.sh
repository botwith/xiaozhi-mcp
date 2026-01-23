#!/bin/bash

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# 加载 .env 文件（如果存在）
ENV_FILE="${SCRIPT_DIR}/.env"
if [ -f "${ENV_FILE}" ]; then
    set -a
    source "${ENV_FILE}" 2>/dev/null || true
    set +a
fi

# 配置变量（优先级：命令行参数 > 环境变量 > 默认值）
EXTRA_TAGS="${2:-${DOCKER_EXTRA_TAGS:-}}"
PLATFORM="${DOCKER_PLATFORM:-linux/amd64,linux/arm64}"
REGISTRY="${DOCKER_REGISTRY:-crpi-lwoxnalpjm9a03w9.cn-shanghai.personal.cr.aliyuncs.com}"
NAMESPACE="${DOCKER_NAMESPACE:-oj8k}"
IMAGE_NAME="${DOCKER_IMAGE_NAME:-xiaozhi-mcp}"
FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

# 根据 registry 选择 Dockerfile
if [[ "${REGISTRY}" == *aliyuncs.com* ]] || [[ "${REGISTRY}" == *cr.aliyuncs.com* ]]; then
    DOCKERFILE="${SCRIPT_DIR}/Dockerfile.acr"
else
    DOCKERFILE="${SCRIPT_DIR}/Dockerfile"
fi

# 生成日期版本号 (0.0.yymmdd格式)
DATE_VERSION="0.0.$(date +%y%m%d)"

# 构建标签列表：默认包含日期版本和 dev
TAGS=("${DATE_VERSION}" "dev")

# 解析额外标签参数
if [[ "${EXTRA_TAGS}" == *latest* ]]; then
    TAGS+=("latest")
fi
if [[ "${EXTRA_TAGS}" == *nightly* ]]; then
    TAGS+=("nightly")
fi

echo "Will build and push tags: ${TAGS[*]}"
echo "Platforms: ${PLATFORM}"

# 检查是否是多架构构建（平台包含逗号）
if [[ "${PLATFORM}" == *,* ]]; then
    # 多架构构建：使用 buildx 直接构建并推送
    for tag in "${TAGS[@]}"; do
        echo ""
        echo "Building and pushing ${FULL_IMAGE_NAME}:${tag}..."
        docker buildx build --platform "${PLATFORM}" \
            -f "${DOCKERFILE}" \
            -t "${FULL_IMAGE_NAME}:${tag}" \
            --push \
            .
    done
else
    # 单架构构建：传统方式
    BUILD_CMD="docker build"
    if [ -n "${PLATFORM}" ]; then
        BUILD_CMD="${BUILD_CMD} --platform ${PLATFORM}"
    fi
    
    # 先构建第一个标签
    MAIN_TAG="${TAGS[0]}"
    echo "Building ${FULL_IMAGE_NAME}:${MAIN_TAG}..."
    ${BUILD_CMD} -f "${DOCKERFILE}" -t "${FULL_IMAGE_NAME}:${MAIN_TAG}" .
    
    # 为其他标签创建标记
    for tag in "${TAGS[@]:1}"; do
        echo "Tagging ${FULL_IMAGE_NAME}:${tag}..."
        docker tag "${FULL_IMAGE_NAME}:${MAIN_TAG}" "${FULL_IMAGE_NAME}:${tag}"
    done
    
    # 推送所有标签
    for tag in "${TAGS[@]}"; do
        echo "Pushing ${FULL_IMAGE_NAME}:${tag}..."
        docker push "${FULL_IMAGE_NAME}:${tag}"
    done
fi

echo ""
echo "Done! Successfully pushed tags: ${TAGS[*]}"
