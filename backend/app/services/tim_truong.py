"""Tìm trường đào tạo một ngành cho tính năng tìm trường phù hợp.

Nguồn chính là dm_nganh_hoc_theo_truong (ngành theo trường, theo năm). Khi bật cờ
`tim_truong_ket_hop_phuong_thuc`, chỉ giữ các trường có ngành này trong đề án tuyển sinh
(chương trình đào tạo kèm phương thức tuyển sinh) của cùng năm.
"""

from datetime import datetime
from typing import Literal

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_nganh_hoc_theo_truong import DmNganhHocTheoTruong
from app.models.dm_truong import DmTruong
from app.schemas.dats_tuyen_sinh import TruongDaoTaoPage, TruongDaoTaoPublic
from app.services.truong_hien_thi import join_tinh_thanh, khu_vuc_hien_thi, loai_hien_thi

SapXep = Literal["ten_asc", "ten_desc", "chi_tieu_desc", "chuong_trinh_desc", "gan_toi"]


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _ma_truong_co_de_an(db: Session, ma_nganh: str, nam: int):
    """Mã các trường có ngành trong đề án tuyển sinh của năm, cùng điều kiện với /de-an-tuyen-sinh/truong-dao-tao."""
    nganh = db.scalar(select(DmNganhDaoTao).where(DmNganhDaoTao.ma_nganh == ma_nganh))
    dieu_kien_nganh = [
        DatsChuongTrinhDaoTao.id.in_(
            select(DatsTrinhDoNganh.de_an_chuong_trinh_id).where(DatsTrinhDoNganh.ma_nganh_chuan == ma_nganh)
        )
    ]
    if nganh is not None:
        dieu_kien_nganh += [
            DatsChuongTrinhDaoTao.nganh_dao_tao_id == nganh.id,
            DatsChuongTrinhDaoTao.ten_chuong_trinh == nganh.ten_nganh,
        ]
    return (
        select(DatsTuyenSinh.ma_truong)
        .join(DatsChuongTrinhDaoTao, DatsChuongTrinhDaoTao.de_an_id == DatsTuyenSinh.id)
        .where(DatsTuyenSinh.nam_tuyen_sinh == nam, or_(*dieu_kien_nganh))
        .distinct()
    )


def truong_theo_nganh(
    db: Session,
    *,
    ma_nganh: str,
    nam_tuyen_sinh: int | None = None,
    q: str | None = None,
    vung_mien: str | None = None,
    loai_co_so: str | None = None,
    ten_tinh_thanh: str | None = None,
    sap_xep: SapXep = "ten_asc",
    uu_tien_tinh: str | None = None,
    uu_tien_khu_vuc: str | None = None,
    page: int = 1,
    page_size: int = 12,
    ket_hop_phuong_thuc: bool | None = None,
) -> TruongDaoTaoPage:
    """Trường có ngành trong dm_nganh_hoc_theo_truong của năm, ghép thông tin từ dm_truong.

    `ket_hop_phuong_thuc` để None thì theo cấu hình hệ thống. `chi_tieu_desc` cần dữ liệu đề án,
    nguồn này chưa có chỉ tiêu nên sắp theo tên. `gan_toi` đưa trường cùng tỉnh, rồi cùng khu vực lên đầu.
    """
    if ket_hop_phuong_thuc is None:
        ket_hop_phuong_thuc = settings.tim_truong_ket_hop_phuong_thuc
    year = nam_tuyen_sinh if nam_tuyen_sinh is not None else datetime.now().year
    code = ma_nganh.strip().upper()
    khu_vuc = khu_vuc_hien_thi()
    loai = loai_hien_thi()
    filters = [
        DmNganhHocTheoTruong.ma_nganh == code,
        DmNganhHocTheoTruong.nam_hoc == year,
    ]
    if ket_hop_phuong_thuc:
        filters.append(DmTruong.ma_truong.in_(_ma_truong_co_de_an(db, code, year)))
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                DmTruong.ten_viet_tat.like(pattern, escape="\\"),
                DmTruong.ten_tieng_anh.like(pattern, escape="\\"),
            )
        )
    if vung_mien and vung_mien.strip():
        filters.append(khu_vuc == vung_mien.strip())
    if loai_co_so and loai_co_so.strip():
        filters.append(loai == loai_co_so.strip())
    if ten_tinh_thanh and ten_tinh_thanh.strip():
        filters.append(DmTruong.ten_tinh_thanh == ten_tinh_thanh.strip())

    joined = join_tinh_thanh(
        DmNganhHocTheoTruong.__table__.join(DmTruong, DmTruong.ma_truong == DmNganhHocTheoTruong.ma_truong)
    )
    school_columns = (
        DmTruong.ma_truong,
        DmTruong.ten_truong,
        DmTruong.ten_viet_tat,
        DmTruong.ten_tieng_anh,
        DmTruong.loai_hinh,
        DmTruong.ten_tinh_thanh,
        DmTruong.dia_chi_tru_so,
        DmTruong.website,
        DmTruong.website_tuyen_sinh,
        DmTruong.anh_dai_dien_url,
    )
    so_chuong_trinh = func.count(DmNganhHocTheoTruong.id)
    theo_ten = [DmTruong.ten_truong.asc(), DmTruong.ma_truong.asc()]
    if sap_xep == "ten_desc":
        thu_tu = [DmTruong.ten_truong.desc(), DmTruong.ma_truong.asc()]
    elif sap_xep == "chuong_trinh_desc":
        thu_tu = [so_chuong_trinh.desc(), *theo_ten]
    elif sap_xep == "gan_toi":
        nhanh = []
        if uu_tien_tinh and uu_tien_tinh.strip():
            nhanh.append((DmTruong.ten_tinh_thanh == uu_tien_tinh.strip(), 0))
        if uu_tien_khu_vuc and uu_tien_khu_vuc.strip():
            nhanh.append((func.max(khu_vuc) == uu_tien_khu_vuc.strip(), 1))
        thu_tu = [case(*nhanh, else_=2), *theo_ten] if nhanh else theo_ten
    else:
        thu_tu = theo_ten

    total = db.scalar(
        select(func.count(func.distinct(DmTruong.ma_truong))).select_from(joined).where(*filters)
    ) or 0
    rows = db.execute(
        select(*school_columns, func.max(loai), func.max(khu_vuc), so_chuong_trinh)
        .select_from(joined)
        .where(*filters)
        .group_by(*school_columns)
        .order_by(*thu_tu)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = [
        TruongDaoTaoPublic(
            ma_truong=row[0],
            ten_truong=row[1],
            ten_viet_tat=row[2],
            ten_tieng_anh=row[3],
            loai_hinh=row[4],
            ten_tinh_thanh=row[5],
            dia_chi_tru_so=row[6],
            website=row[7],
            website_tuyen_sinh=row[8],
            anh_dai_dien_url=row[9],
            loai_co_so=row[10],
            vung_mien=row[11],
            nam_tuyen_sinh=year,
            so_chuong_trinh=int(row[12] or 0),
        )
        for row in rows
    ]
    return TruongDaoTaoPage(items=items, total=total, page=page, page_size=page_size)
