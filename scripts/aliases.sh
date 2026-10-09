# Lệnh tiện lợi cho dự án Định hướng nghề.
# Dùng một lần mỗi session:
#   source scripts/aliases.sh
# hoặc thêm vào ~/.zshrc:
#   source /đường/dẫn/tới/dinh_huong_nghe/scripts/aliases.sh

# Xác định thư mục gốc project (khi file được source)
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  _DH_SCRIPT="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then
  _DH_SCRIPT="${(%):-%x}"
else
  _DH_SCRIPT="$0"
fi
export DH_ROOT="$(cd "$(dirname "$_DH_SCRIPT")/.." && pwd)"
unset _DH_SCRIPT

dh() {
  make -C "$DH_ROOT" "${1:-help}" "${@:2}"
}

dh-help() { make -C "$DH_ROOT" help; }
dh-install() { make -C "$DH_ROOT" install; }
dh-be() { make -C "$DH_ROOT" be; }
dh-fe() { make -C "$DH_ROOT" fe; }
dh-migrate() { make -C "$DH_ROOT" migrate; }
dh-migrate-down() { make -C "$DH_ROOT" migrate-down; }
dh-migrate-history() { make -C "$DH_ROOT" migrate-history; }
dh-migrate-current() { make -C "$DH_ROOT" migrate-current; }
dh-stamp() { make -C "$DH_ROOT" stamp; }
dh-db() { make -C "$DH_ROOT" db-check; }

# Tạo migration: dh-migrate-new "mo ta"
dh-migrate-new() {
  if [ -z "${1:-}" ]; then
    echo 'Dùng: dh-migrate-new "mo ta"'
    return 1
  fi
  make -C "$DH_ROOT" migrate-new m="$1"
}

echo "Đã nạp lệnh Định hướng nghề (DH_ROOT=$DH_ROOT)"
echo "  dh / dh-help          hiện lệnh"
echo "  dh-be                 chạy backend"
echo "  dh-fe                 chạy frontend"
echo "  dh-migrate            áp dụng migration"
echo "  dh-migrate-new \"...\"  tạo migration mới"
echo "  dh-db                 kiểm tra DB"
echo "  dh-install            cài dependency"
