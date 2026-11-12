"""Xuất danh sách API của hệ thống ra file Markdown, chia theo nhóm quản trị, thành viên và khách vãng lai.

Quyền của từng API được đọc trực tiếp từ dependency của route nên file luôn khớp với code:
- get_admin_user: bắt buộc đăng nhập bằng tài khoản quản trị.
- get_current_user: bắt buộc đăng nhập.
- get_optional_user: không bắt buộc, đăng nhập thì được thêm quyền lợi (ví dụ đếm lượt theo tài khoản).
- Không có dependency nào ở trên: không cần đăng nhập.

Chạy từ thư mục backend:

    python -m app.scripts.xuat_danh_sach_api            # ghi ra backend/API.md
    python -m app.scripts.xuat_danh_sach_api duong/dan.md
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from fastapi import routing
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.api.deps import get_admin_user, get_current_user, get_optional_user
from app.core.config import settings
from app.main import app

FILE_MAC_DINH = Path(__file__).resolve().parents[2] / "API.md"

QUAN_TRI = "quan_tri"
THANH_VIEN = "thanh_vien"
KHACH = "khach"

NHOM = [
    (QUAN_TRI, "Quản trị (admin)", "Bắt buộc đăng nhập bằng tài khoản quản trị. Thiếu token trả 401, không phải admin trả 403."),
    (THANH_VIEN, "Thành viên (user)", "Bắt buộc đăng nhập. Thiếu hoặc sai token trả 401."),
    (
        KHACH,
        "Khách vãng lai",
        "Không cần đăng nhập. Các API ghi “Tùy chọn” vẫn nhận token: có token hợp lệ thì xử lý theo tài khoản.",
    ),
]

DANG_NHAP = {
    QUAN_TRI: "Bắt buộc (admin)",
    THANH_VIEN: "Bắt buộc",
}


def _cac_ham_phu_thuoc(dependant: Dependant) -> set:
    """Mọi hàm dependency của route, kể cả dependency lồng nhau và dependency khai báo ở router."""
    ham = set()
    for dep in dependant.dependencies:
        if dep.call is not None:
            ham.add(dep.call)
        ham |= _cac_ham_phu_thuoc(dep)
    return ham


def _phan_loai(dependant: Dependant) -> tuple[str, str]:
    ham = _cac_ham_phu_thuoc(dependant)
    if get_admin_user in ham:
        return QUAN_TRI, DANG_NHAP[QUAN_TRI]
    if get_current_user in ham and get_optional_user not in ham:
        return THANH_VIEN, DANG_NHAP[THANH_VIEN]
    if get_optional_user in ham:
        return KHACH, "Tùy chọn"
    return KHACH, "Không"


def _mo_ta(route: APIRoute) -> str:
    text = (route.summary or route.description or "").strip()
    if not text and route.endpoint.__doc__:
        text = route.endpoint.__doc__.strip()
    # Lấy câu đầu tiên của docstring để bảng gọn.
    dong = text.splitlines()[0].strip() if text else ""
    return dong.replace("|", "\\|") or "—"


def _nhom_chuc_nang(path: str) -> str:
    """Nhóm theo đoạn đầu của đường dẫn sau tiền tố API, ví dụ /danh-muc/truong-hoc → danh-muc/truong-hoc."""
    duong_dan = path.removeprefix(settings.api_v1_prefix).strip("/")
    phan = [p for p in duong_dan.split("/") if p and not p.startswith("{")]
    if not phan:
        return "(gốc)"
    if phan[0] in {"danh-muc", "he-thong"} and len(phan) > 1:
        return f"{phan[0]}/{phan[1]}"
    return phan[0]


def thu_thap() -> dict[str, dict[str, list[dict]]]:
    ket_qua: dict[str, dict[str, list[dict]]] = {key: defaultdict(list) for key, _, _ in NHOM}
    # Router được include theo kiểu lười nên phải đi qua iter_route_contexts (cách FastAPI dựng OpenAPI)
    # để có đường dẫn đầy đủ và dependency khai báo ở router.
    for ctx in routing.iter_route_contexts(app.routes):
        route = ctx.original_route
        if not isinstance(route, APIRoute) or not route.include_in_schema:
            continue
        nhom, dang_nhap = _phan_loai(ctx.dependant)
        for method in sorted(set(ctx.methods) - {"HEAD", "OPTIONS"}):
            ket_qua[nhom][_nhom_chuc_nang(ctx.path)].append(
                {"method": method, "path": ctx.path, "dang_nhap": dang_nhap, "mo_ta": _mo_ta(route)}
            )
    return ket_qua


def tao_markdown(ket_qua: dict[str, dict[str, list[dict]]]) -> str:
    thu_tu_method = {"GET": 0, "POST": 1, "PUT": 2, "PATCH": 3, "DELETE": 4}
    tong = sum(len(api) for nhom in ket_qua.values() for api in nhom.values())
    dong = [
        "# Danh sách API",
        "",
        f"Tự sinh từ code lúc {datetime.now():%d/%m/%Y %H:%M} bằng `python -m app.scripts.xuat_danh_sach_api`. "
        "Không sửa tay, chạy lại lệnh khi thêm hoặc đổi API.",
        "",
        f"Tiền tố chung: `{settings.api_v1_prefix}`. Tổng cộng **{tong}** API.",
        "",
        "Đăng nhập bằng header `Authorization: Bearer <access_token>` lấy từ API đăng nhập.",
        "",
        "| Nhóm | Số API | Yêu cầu đăng nhập |",
        "|---|---:|---|",
    ]
    for key, ten, quy_dinh in NHOM:
        so = sum(len(api) for api in ket_qua[key].values())
        dong.append(f"| [{ten}](#{key}) | {so} | {quy_dinh} |")
    for key, ten, quy_dinh in NHOM:
        dong += ["", f'<a id="{key}"></a>', "", f"## {ten}", "", quy_dinh]
        for chuc_nang in sorted(ket_qua[key]):
            dong += ["", f"### `{chuc_nang}`", "", "| Method | Đường dẫn | Đăng nhập | Mô tả |", "|---|---|---|---|"]
            for api in sorted(ket_qua[key][chuc_nang], key=lambda a: (a["path"], thu_tu_method.get(a["method"], 9))):
                dong.append(f"| `{api['method']}` | `{api['path']}` | {api['dang_nhap']} | {api['mo_ta']} |")
    return "\n".join(dong) + "\n"


def main() -> int:
    dich = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else FILE_MAC_DINH
    ket_qua = thu_thap()
    dich.write_text(tao_markdown(ket_qua), encoding="utf-8")
    for key, ten, _ in NHOM:
        print(f"{ten}: {sum(len(api) for api in ket_qua[key].values())} API")
    print(f"Đã ghi {dich}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
