#!/usr/bin/env bash
# Khởi động Backend (FastAPI :3060) + Frontend (Vite :5173) trên macOS
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "========================================================"
echo "      ĐANG KHỞI ĐỘNG HỆ THỐNG (BACKEND + FRONTEND)"
echo "========================================================"
echo

# Chọn Python: ưu tiên .venv của project
BACKEND_PYTHON="python3"
if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  BACKEND_PYTHON="$ROOT/backend/.venv/bin/python"
fi

echo "[*] Khởi động Backend (Port 3060)..."
# Mở tab Terminal mới cho backend
osascript <<EOF
tell application "Terminal"
  do script "cd '$ROOT/backend' && '$BACKEND_PYTHON' -m uvicorn app.main:app --reload --port 3060"
  activate
end tell
EOF

echo "[*] Khởi động Frontend (Port 5173)..."
# Mở tab Terminal mới cho frontend
osascript <<EOF
tell application "Terminal"
  do script "cd '$ROOT/frontend' && npm run dev"
  activate
end tell
EOF

echo
echo "========================================================"
echo "  Backend Swagger: http://127.0.0.1:3060/docs"
echo "  Frontend Web:    http://localhost:5173"
echo "========================================================"
echo

# Đợi vài giây rồi mở trình duyệt
sleep 3
open "http://localhost:5173"
