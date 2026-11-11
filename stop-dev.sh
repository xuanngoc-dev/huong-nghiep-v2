#!/usr/bin/env bash
# Dừng các tiến trình đang listen trên port 3060 và 5173
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "========================================================"
echo "      ĐANG DỪNG DỊCH VỤ (PORT 3060 VÀ 5173)..."
echo "========================================================"
echo

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "[*] Dừng tiến trình trên port ${port}: ${pids}"
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
  else
    echo "[*] Không có tiến trình nào trên port ${port}"
  fi
}

kill_port 3060
kill_port 5173

echo
echo "[*] Đã dừng các tiến trình trên port 3060 và 5173."
