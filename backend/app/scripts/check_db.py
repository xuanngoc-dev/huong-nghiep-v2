"""Kiểm tra kết nối MySQL từ terminal.

Chạy từ thư mục backend:

    python -m app.scripts.check_db
"""

from __future__ import annotations

import sys

from app.db.session import probe_db_connection


def main() -> int:
    result = probe_db_connection()
    print(f"status:   {result['status']}")
    print(f"host:     {result['host']}:{result['port']}")
    print(f"user:     {result['user']}")
    print(f"database: {result['database']}")

    if result["status"] == "ok":
        print("MySQL connection OK")
        return 0

    print(f"detail:   {result.get('detail')}")
    print("MySQL connection FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
