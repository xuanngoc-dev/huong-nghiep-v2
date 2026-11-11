#!/usr/bin/env bash
# Cách dùng:
#   ./build_and_push.sh [tag]                 (mặc định tag=latest, platform=linux/amd64)
#   ./build_and_push.sh --platform linux/arm64 [tag]
#   ./build_and_push.sh v1.0.0 --platform linux/amd64
set -euo pipefail

REGISTRY="103.226.249.128:8142/huongnghiep"
TAG="latest"
PLATFORM="linux/amd64"
ROOT="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      if [[ -z "${2:-}" ]]; then
        echo "***** LỖI: --platform cần giá trị (vd: linux/amd64) *****" >&2
        exit 1
      fi
      PLATFORM="$2"
      shift 2
      ;;
    --platform=*)
      PLATFORM="${1#*=}"
      shift
      ;;
    -h|--help)
      echo "Cách dùng: $0 [--platform linux/amd64|linux/arm64] [tag]"
      echo "  Mặc định: tag=latest, platform=linux/amd64"
      exit 0
      ;;
    -*)
      echo "***** LỖI: tùy chọn không hợp lệ: $1 *****" >&2
      exit 1
      ;;
    *)
      TAG="$1"
      shift
      ;;
  esac
done

cleanup() {
  cd "$ROOT"
}
trap cleanup EXIT

echo "===== Platform: ${PLATFORM} | Tag: ${TAG} ====="

echo "===== [1/4] Build image backend ====="
cd "$ROOT/backend"
# Build context là thư mục gốc dự án (Dockerfile cần copy data_dh_json)
docker build --platform "${PLATFORM}" -f Dockerfile -t "huongnghiep-backend:${TAG}" ..

echo "===== [2/4] Build frontend (npm run build) ====="
cd "$ROOT/frontend"
npm run build

echo "===== [3/4] Build image frontend ====="
docker build --platform "${PLATFORM}" -t "huongnghiep-frontend:${TAG}" .

echo "===== [4/4] Tag và push image lên ${REGISTRY} ====="
docker tag "huongnghiep-backend:${TAG}" "${REGISTRY}/huongnghiep-backend:${TAG}"
docker tag "huongnghiep-frontend:${TAG}" "${REGISTRY}/huongnghiep-frontend:${TAG}"
docker push "${REGISTRY}/huongnghiep-backend:${TAG}"
docker push "${REGISTRY}/huongnghiep-frontend:${TAG}"

echo
echo "===== HOÀN THÀNH ====="
echo "  ${REGISTRY}/huongnghiep-backend:${TAG}"
echo "  ${REGISTRY}/huongnghiep-frontend:${TAG}"
echo "  platform: ${PLATFORM}"
