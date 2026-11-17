"""Xóa loại câu hỏi / câu hỏi trắc nghiệm cùng dữ liệu liên quan: câu hỏi, đáp án và các phiên khảo sát đã làm.

Phiên khảo sát có câu trả lời cho câu hỏi bị xóa thì bị xóa trọn (mọi câu trả lời của phiên) vì phiên thiếu một phần
câu hỏi không còn cho kết quả đúng. Xóa theo thứ tự con trước cha, không dựa vào ON DELETE CASCADE của CSDL.
Các hàm `xoa_*` chưa commit.
"""

from sqlalchemy import delete, distinct, false, func, or_, select
from sqlalchemy.orm import Session

from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat


def _ssid_lien_quan(cau_hoi_ids: list[int], loai_ids: list[int] | None = None):
    """Câu lệnh chọn ssid các phiên có câu trả lời thuộc các câu hỏi / loại câu hỏi sắp xóa."""
    dieu_kien = []
    if cau_hoi_ids:
        dieu_kien.append(TnChiTietTraLoi.cau_hoi_id.in_(cau_hoi_ids))
    if loai_ids:
        dieu_kien.append(TnChiTietTraLoi.loai_cau_hoi_id.in_(loai_ids))
    return select(distinct(TnChiTietTraLoi.ssid)).where(or_(*dieu_kien) if dieu_kien else false())


def _dem(db: Session, cau_hoi_ids: list[int], loai_ids: list[int] | None = None) -> dict[str, int]:
    so_dap_an = (
        db.scalar(select(func.count()).select_from(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id.in_(cau_hoi_ids)))
        if cau_hoi_ids
        else 0
    )
    so_phien = db.scalar(select(func.count()).select_from(_ssid_lien_quan(cau_hoi_ids, loai_ids).subquery()))
    return {"so_cau_hoi": len(cau_hoi_ids), "so_dap_an": so_dap_an or 0, "so_phien": so_phien or 0}


def _xoa(db: Session, cau_hoi_ids: list[int], loai_ids: list[int] | None = None) -> None:
    ssids = list(db.scalars(_ssid_lien_quan(cau_hoi_ids, loai_ids)))
    if ssids:
        db.execute(delete(TnChiTietTraLoi).where(TnChiTietTraLoi.ssid.in_(ssids)))
        db.execute(delete(TnPhienKhaoSat).where(TnPhienKhaoSat.ssid.in_(ssids)))
    if cau_hoi_ids:
        db.execute(delete(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id.in_(cau_hoi_ids)))
        db.execute(delete(TnCauHoiTracNghiem).where(TnCauHoiTracNghiem.id.in_(cau_hoi_ids)))


def _loai_ton_tai(db: Session, ids: list[int]) -> list[int]:
    return list(db.scalars(select(DmLoaiCauHoi.id).where(DmLoaiCauHoi.id.in_(ids))))


def _cau_hoi_cua_loai(db: Session, loai_ids: list[int]) -> list[int]:
    return list(db.scalars(select(TnCauHoiTracNghiem.id).where(TnCauHoiTracNghiem.loai_cau_hoi_id.in_(loai_ids))))


def _cau_hoi_ton_tai(db: Session, ids: list[int]) -> list[int]:
    return list(db.scalars(select(TnCauHoiTracNghiem.id).where(TnCauHoiTracNghiem.id.in_(ids))))


def anh_huong_loai(db: Session, ids: list[int]) -> dict[str, int]:
    """Số bản ghi sẽ bị xóa theo các loại câu hỏi `ids` (id không tồn tại thì bỏ qua)."""
    ids = _loai_ton_tai(db, ids)
    if not ids:
        return {"so_loai": 0, "so_cau_hoi": 0, "so_dap_an": 0, "so_phien": 0}
    return {"so_loai": len(ids), **_dem(db, _cau_hoi_cua_loai(db, ids), ids)}


def xoa_loai(db: Session, ids: list[int]) -> int:
    """Xóa loại câu hỏi `ids` cùng câu hỏi, đáp án và phiên khảo sát liên quan. Trả số loại đã xóa."""
    ids = _loai_ton_tai(db, ids)
    if not ids:
        return 0
    _xoa(db, _cau_hoi_cua_loai(db, ids), ids)
    db.execute(delete(DmLoaiCauHoi).where(DmLoaiCauHoi.id.in_(ids)))
    return len(ids)


def anh_huong_cau_hoi(db: Session, ids: list[int]) -> dict[str, int]:
    """Số đáp án và phiên khảo sát sẽ bị xóa theo các câu hỏi `ids` (id không tồn tại thì bỏ qua)."""
    return _dem(db, _cau_hoi_ton_tai(db, ids))


def xoa_cau_hoi(db: Session, ids: list[int]) -> int:
    """Xóa câu hỏi `ids` cùng đáp án và phiên khảo sát liên quan. Trả số câu hỏi đã xóa."""
    ids = _cau_hoi_ton_tai(db, ids)
    if ids:
        _xoa(db, ids)
    return len(ids)
